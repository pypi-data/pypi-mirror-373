from typing import List, Any
from pathlib import Path

import time, h5py, uuid, dataclasses, os

from qcodes.parameters import Parameter, MultiParameter, ParameterWithSetpoints, ArrayParameter

from etiket_client.python_api.dataset_model.files import FileType, generate_version_id, FileStatusLocal
from etiket_client.settings.folders import create_file_dir

from qdrive.measurement.data_collector_var import set_var_static, set_var_dynamic, get_var
from qdrive.measurement.HDF5_collector.ds_cache import ds_cache
from qdrive.measurement.HDF5_collector.h5_writer_container import h5_writer_container
from qdrive.measurement.HDF5_collector.h5_dependency_builder import H5_dependency_builder, NETCDF4_reference_list_builder

# TODO fix naming clashes
@dataclasses.dataclass
class data_collection:
    parameter : Any
    get_var : ds_cache
    set_var_static : List[ds_cache]
    set_var_dynamic : List[ds_cache]
    dependency_builder : H5_dependency_builder
    param_idx : int

    def add_data(self, data):
        if self.parameter in data.keys():
            for data_saver_dynamic in self.set_var_dynamic:
                data_saver_dynamic.add_result(data[data_saver_dynamic.var_info.parameter])

            if issubclass(self.parameter.__class__, MultiParameter) : 
                self.get_var.add_result(data[self.parameter][self.param_idx])
            else:
                self.get_var.add_result(data[self.parameter])

    def save(self):
        self.dependency_builder.rebuild() #only writes when needed.
        for preprocessor in [self.get_var] + self.set_var_static + self.set_var_dynamic:
            preprocessor.write()

    def complete(self):
        for preprocessor in [self.get_var] + self.set_var_static + self.set_var_dynamic:
            preprocessor.complete()

class data_collector:
    def __init__(self, dataset, dtype = FileType.HDF5_NETCDF):
        self.dataset = dataset
        self.measurement_name = None
        h5_file = self.__create_hdf5_file(dtype)
        self.HDF5_writers = h5_writer_container(h5_file)
        self.ds_collections : List[data_collection] = []
        self.last_write = time.time()
        self.write_every = 0.1 #100ms
        
        self.first_write_happened = False
    
    def __create_hdf5_file(self, dtype, name = "measurement") -> 'h5py.File':
        self.measurement_name = name
        if name in self.dataset.files.keys():
            raise ValueError("Already a measurement present in this dataset. Please start a new one.")
        
        filename = f'{name}.hdf5'
        fpath = create_file_dir(self.dataset.scope.uuid, self.dataset.uuid, uuid.uuid4(), generate_version_id())
        Path(fpath+filename).touch()
        
        self.dataset._files._add_new_file(filename, file_path=fpath+filename,
                                file_type=dtype, generator="qdrive", file_status = FileStatusLocal.writing)
        self.lock_file = os.path.dirname(self.dataset[filename].path) + "/.lock"
        os.close(os.open(self.lock_file, os.O_CREAT | os.O_EXCL | os.O_RDWR))
        hdf5_file = h5py.File(self.dataset[filename].path, 'w', locking=False, libver='v112')
        return hdf5_file
    
    def __add__(self, other : 'List[data_collection] | data_collection'):
        if self.first_write_happened:
            raise ValueError("Cannot add to a data collector after the first write has happened.")
        if isinstance(other, list):
            self.ds_collections += other
        else:
            self.ds_collections.append(other)
        return self

    def _enable_swmr(self):
        if self.first_write_happened is False:
            # this was a quick fix, putting this here, in swmr mode, no new attributes can be created
            # this is supposed to be fixed with VDF SWMR mode (aka SWMR 2.0), but the implementation is not yet in the H5 library (lack of money :/).
            NETCDF4_reference_list_builder(self.HDF5_writers.h5_file ,self.ds_collections)
            self.HDF5_writers.h5_file.swmr_mode = True
            self.first_write_happened = True
            os.remove(self.lock_file)
            
    @property
    def size(self):
        return len(self.ds_collections)

    def set_attr(self, name : str, value):
        if self.first_write_happened:
            raise ValueError("Cannot set attributes after the first write has happened.")
        self.HDF5_writers.h5_file.attrs[name] = value
    
    def add_data(self, data):
        self._enable_swmr()
        
        for collection in self.ds_collections:
            if collection.parameter in data.keys():
                collection.add_data(data)
        
        if self.last_write + self.write_every < time.time():
            self.__save()
            self.last_write = time.time()

    def __save(self): #this happens automatically when data is added.
        for collection in self.ds_collections:
            collection.save()
        self.HDF5_writers.h5_file.flush()

    def complete(self):
        self.__save()
        
        # NETCDF4_REFERENCE_LIST_buider(self.HDF5_writers.h5_file ,self.ds_collections)
        for collection in self.ds_collections:
            collection.complete()            
        
        self.HDF5_writers.h5_file.close()

        self.dataset[self.measurement_name].file_obj.current._mark_complete()



def get_var_to_get_mgr(get_vars : 'get_var | List[get_var]', collector : data_collector) -> List[data_collection]:
    if not isinstance(get_vars, list):
        get_vars = [get_vars]
    
    ds_collections = []
    
    for i, get_variable in enumerate(get_vars):
        get_var_cache = ds_cache(collector.HDF5_writers, get_variable, get_variable.ndim, 0)
        set_var_static_cache = []
        
        for stat_var in get_variable.set_vars_static:
            data_pre = ds_cache(collector.HDF5_writers, stat_var, 1, 0)
            set_var_static_cache.append(data_pre)
            
        set_var_dynamic_cache = []
        for j, set_vars_dynamic in enumerate(get_variable.set_vars_dynamic):
            data_pre = ds_cache(collector.HDF5_writers, set_vars_dynamic,
                                get_variable.ndim, get_variable.ndim-j-1)
            set_var_dynamic_cache.append(data_pre)

        if len(set_var_dynamic_cache) > 1:
            for j in range(len(set_var_dynamic_cache)-1):
                for dyn_cache in set_var_dynamic_cache[j+1:]:
                    set_var_dynamic_cache[j].add_child(dyn_cache)
                set_var_dynamic_cache[j].add_child(get_var_cache)
        
        # ensure that the dataset contains the right linkage.
        dep_builder = H5_dependency_builder(get_var_cache, set_var_dynamic_cache + set_var_static_cache)
        
        ds_collections.append(
                data_collection(
                    get_variable.parameter, get_var_cache, set_var_static_cache,
                    set_var_dynamic_cache, dep_builder, i))
        
    return ds_collections

# TODO intergrate in data_collector.
# TODO check qcodes multiparameter with multiple setpoint allowed formats.
def from_QCoDeS_parameter(parameter, dependencies, writer_collection : data_collector) -> List[data_collection]:
    set_vars_dyn = []
    for dependency in dependencies:
        set_vars_dyn.append(set_var_dynamic.from_parameter(dependency))

    if issubclass(parameter.__class__, MultiParameter):
        data_collectors = []

        get_vars = []
        for i in range(len(parameter.names)):
            set_vars_stat = []
        
            for j in range(len(parameter.setpoints[i])):
                set_vars_stat.append(set_var_static(f"{parameter.name}_{parameter.names[i]}_{parameter.setpoint_names[i][j]}",
                                        parameter.setpoint_labels[i][j],
                                        parameter.setpoint_units[i][j],
                                        parameter.setpoints[i][j]))

            get_vars.append(get_var(f"{parameter.name}_{parameter.names[i]}",
                                parameter.labels[i],
                                parameter.units[i],
                                parameter,
                                set_vars_dyn,
                                set_vars_stat) )
            
        data_collectors += get_var_to_get_mgr(get_vars, writer_collection)

        return data_collectors

    elif issubclass(parameter.__class__, ParameterWithSetpoints):
        set_vars_stat = []
        for i in range(len(parameter.setpoints)):
            set_vars_stat.append(
                set_var_static(parameter.setpoints[i].name,
                                        parameter.setpoints[i].label,
                                        parameter.setpoints[i].unit,
                                        parameter.setpoints[i]()))
        return get_var_to_get_mgr(
                    get_var(parameter.name, parameter.label,
                            parameter.unit, parameter, set_vars_dyn,
                            set_vars_stat),
                    writer_collection)
        
    elif issubclass(parameter.__class__, ArrayParameter):
        set_vars_stat = []
        
        for i in range(len(parameter.setpoints)):
            set_vars_stat.append(set_var_static(parameter.setpoint_names[i],
                                    parameter.setpoint_labels[i],
                                    parameter.setpoint_units[i],
                                    parameter.setpoints[i]))
        return get_var_to_get_mgr(
                    get_var(parameter.name, parameter.label,
                        parameter.unit, parameter, set_vars_dyn,
                        set_vars_stat),
                    writer_collection )
                
    elif issubclass(parameter.__class__, Parameter):
        return get_var_to_get_mgr(
                    get_var(parameter.name, parameter.label, 
                            parameter.unit, parameter, set_vars_dyn), 
                    writer_collection)
    
    else:
        raise ValueError("Only QCoDeS parameters are currently supported.")
