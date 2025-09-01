import h5py as h5
import numpy as np

from typing import List

from qdrive.measurement.HDF5_collector.ds_cache import ds_cache

class H5_dependency_builder:
    '''
    build dependencies of different datasets in the HDF5 file according to the netCDF4 specification
    '''
    def __init__(self, ds_get_var : ds_cache, ds_dependencies : List[ds_cache]):
        self.ds_get_var = ds_get_var
        self.ds_dependencies = ds_dependencies

        self.dependency_names = []

        self.__build()

    def __build(self):
        self.dependency_names = []
        for dep in self.ds_dependencies:
            self.dependency_names.append(dep.name)

        dependencies_references = [] 
        for dep in self.ds_dependencies:
            dependencies_references.append(np.array([dep.dataset.ref], dtype=np.object_))

        if h5.h5a.exists(self.ds_get_var.dataset.id, 'DIMENSION_LIST'.encode('utf-8')):
            h5.h5a.delete(self.ds_get_var.dataset.id, name='DIMENSION_LIST'.encode('utf-8'))
        
        type_id = h5.h5t.vlen_create(h5.h5t.STD_REF_OBJ)
        space_id = h5.h5s.create_simple(
                        (len(dependencies_references),),
                        (len(dependencies_references),))
        
        attr = h5.h5a.create(self.ds_get_var.dataset.id, 
                             'DIMENSION_LIST'.encode('utf-8'),
                              type_id, space_id)
        
        # enforce array of array in numpy
        arr = np.array(dependencies_references + [''], dtype=object)[:-1]
        attr.write(arr)

    def rebuild(self):
        for dep_name, dep in zip(self.dependency_names, self.ds_dependencies):
            if dep_name != dep.name:
                self.__build()
                break

    def complete(self):
        for writer in [self.ds_get_var]+self.ds_dependencies:
            writer.complete()
            
def NETCDF4_reference_list_builder(file : 'h5.File', data_collections):
    reference_list = {}
    for dc in data_collections:
        set_vars = (dc.set_var_dynamic + dc.set_var_static)
        for i, set_var in enumerate(set_vars):
            reference_list.setdefault(set_var.name, [set_var.dataset, []])
            reference_list[set_var.name][1].append((dc.get_var.dataset.ref, i))
            
        
    for i in range(len(reference_list.items())):
        dataset, values = list(reference_list.values())[i]
        if h5.h5a.exists(dataset.id,'REFERENCE_LIST'.encode('utf-8')):
            h5.h5a.delete(dataset.id,name='REFERENCE_LIST'.encode('utf-8'))    
        
        type_id = h5.h5t.create(h5.h5t.COMPOUND, h5.h5t.STD_REF_OBJ.get_size() + h5.h5t.NATIVE_UINT32.get_size() )
        type_id.insert('dataset'.encode('utf-8'), 0, h5.h5t.STD_REF_OBJ)
        type_id.insert('dimension'.encode('utf-8'), h5.h5t.STD_REF_OBJ.get_size(), h5.h5t.NATIVE_UINT32)
        
        space_id = h5.h5s.create_simple( (len(values),),  (len(values),))
        
        attr = h5.h5a.create(dataset.id, 'REFERENCE_LIST'.encode('utf-8'), type_id, space_id)
        attr.write(np.array(values, dtype=[('dataset', 'O'), ('dimension', np.uint32)]))
        
        attr = h5.h5a.create(dataset.id, '_FillValue'.encode('utf-8'),
                                h5.h5t.NATIVE_DOUBLE, h5.h5s.create_simple( (1,), (1,)))
        attr.write(np.array(np.nan))
        
        attr = h5.h5a.create(dataset.id, '_Netcdf4Coordinates'.encode('utf-8'),
                              h5.h5t.NATIVE_INT32, h5.h5s.create_simple( (1,), (1,)))
        attr.write(np.array(i))
        
        attr = h5.h5a.create(dataset.id,'_Netcdf4Dimid'.encode('utf-8'),
                              h5.h5t.NATIVE_INT32, h5.h5s.create(h5.h5s.SCALAR))
        attr.write(np.array(i))
        
        create_str_attr(dataset, 'CLASS', 'DIMENSION_SCALE')
        create_str_attr(dataset, 'NAME', dataset.name[1:])

    setpoint_names = list(reference_list.keys())
    for i, dc in enumerate(data_collections):
        dataset = dc.get_var.dataset
        
        coordinates = []
        for v in (dc.set_var_dynamic + dc.set_var_static):
            coordinates.append(setpoint_names.index(v.dataset.name))
        
        attr = h5.h5a.create(dataset.id, '_FillValue'.encode('utf-8'),
                              h5.h5t.NATIVE_DOUBLE, h5.h5s.create_simple( (1,), (1,)))
        attr.write(np.array(np.nan))
        
        attr = h5.h5a.create(dataset.id, '_param_index'.encode('utf-8'),
                              h5.h5t.NATIVE_INT64, h5.h5s.create_simple((2,), (2,)))
        attr.write(np.array([0,i]))
        
        attr = h5.h5a.create(dataset.id, '_Netcdf4Coordinates'.encode('utf-8'),
                              h5.h5t.NATIVE_INT32,
                              h5.h5s.create_simple((len(coordinates),), (len(coordinates),)))
        attr.write(np.array(coordinates))
        
        attr = h5.h5a.create(dataset.id, '_Netcdf4Dimid'.encode('utf-8'),
                              h5.h5t.NATIVE_INT32, h5.h5s.create(h5.h5s.SCALAR))
        attr.write(np.array(0))
    
    # TODO update
    properties = 'hdf5=1.14.3'
    file.attrs['_NCProperties'] = np.array(properties.encode('ascii'), dtype=h5.string_dtype('ascii', len(properties)+1))


def create_str_attr(dataset, attr_name, string_value):
    if h5.h5a.exists(dataset.id, attr_name.encode('utf-8')):
            h5.h5a.delete(dataset.id,name = attr_name.encode('utf-8'))   

    type_id = h5.h5t.TypeID.copy(h5.h5t.C_S1)
    type_id.set_size(len(string_value)+1)
    type_id.set_strpad(h5.h5t.STR_NULLTERM)
    space = h5.h5s.create(h5.h5s.SCALAR)
    
    attr = h5.h5a.create(dataset.id, attr_name.encode('utf-8'), type_id, space)
    string = np.array(string_value.encode('ascii'), dtype=h5.string_dtype('ascii', len(string_value)+1))
    attr.write(string)
