import h5py, json, numpy, xarray, os, shutil, warnings, uuid, pathlib, h5netcdf.legacyapi as netcdf4, contextlib

from typing import Union

from qdrive.dataset.files.utility import is_scalar, is_iterable

from qdrive.dataset.files.HDF5 import HDF5_file, xarray_dataset_attr_formatter_to_json, xarray_dataArray_attr_formatter_json
from qdrive.dataset.files.json import JSON_file
from qdrive.dataset.files.numpy import numpy_file, is_numpy_array, is_numpy_dict
from qdrive.dataset.files.file import file_file

from etiket_client.settings.folders import create_file_dir
from etiket_client.python_api.dataset_model.files import file_manager as file_manager_etiket,\
    file_object, FileType, generate_version_id, FileStatusLocal

# TODO add method to load csv files and save them as HDF5

class file_manager():
    def __init__(self, dataset, file_mgr_core : file_manager_etiket):
        self.ds = dataset
        self.file_obj = {}
        self.name_router = {} # add hoc added ...
        self.file_mgr_core = file_mgr_core
        
        for file in file_mgr_core.values():
            self.__load_file(file)
        
    def __getitem__(self, filename) -> Union[HDF5_file, JSON_file, numpy_file, file_file]:
        # phasing out the ability to access the file without the extension.
        if filename not in self.file_obj and filename in self.name_router:
            # check if there are no two files starting with the same name in the file_obj
            filenames = list(self.file_obj.keys())
            filename_without_extension = filename.rsplit('.', 1)[0] if '.' in filename else filename
            filenames_starting_with_name = [f for f in filenames if f == filename_without_extension]
            if len(filenames_starting_with_name) > 1:
                raise KeyError(f"There are multiple files starting with the same name: {filenames_starting_with_name}. Please use the filename with the extension.")
            # add deprecation warning
            message = f"Accessing the file without the extension is deprecated. Please use the filename {self.name_router[filename]} instead."
            warnings.warn(message, DeprecationWarning)
            return self.file_obj[self.name_router[filename]]
        return self.file_obj[filename]
        
    def __setitem__(self, filename, value):
        self.ds._create_local()

        try:
            obj =self[filename]
            filename = obj.filename
        except KeyError:
            pass
        
        if filename not in self.keys():
            if "." in filename:
                parts = filename.split(".")
                if len(parts) > 2:
                    raise ValueError(f"There can only by one extension per file name. Please use only one dot in the file name.")
                name = parts[0]
                file_extension = parts[1]
            else:
                raise ValueError(f"The filename {filename} is not valid. Please provide a filename with a suffix.")
            
            fpath = create_file_dir(self.ds.scope.uuid, self.ds.uuid, uuid.uuid4(), generate_version_id())

            file_type = FileType.UNKNOWN
            generator = "unknown"
            if isinstance(value, numpy.ndarray) or is_numpy_dict(value) or is_numpy_array(value):
                if file_extension is None:
                    fname = f'{name}.npz'
                else:
                    if file_extension != "npz":
                        raise ValueError(f"The file extension {file_extension} is not supported for numpy arrays. Please use .npz.")
                    fname = f'{name}.{file_extension}'
                destination = fpath + fname
                if isinstance(value, numpy.ndarray):
                    numpy.savez_compressed(destination, value)
                elif is_numpy_array(value):
                    numpy.savez_compressed(destination, *value)
                elif is_numpy_dict(value):
                    numpy.savez_compressed(destination, **value)
                file_type = FileType.NDARRAY
                generator = f"numpy.{numpy.__version__}"
            elif isinstance(value, pathlib.Path):
                if not value.exists():
                    raise ValueError(f"Path {value} does not exist.")
                fname =  os.path.basename(value)
                destination = fpath + fname
                
                if value.suffix in {".hdf5", ".h5", ".nc"}:
                    file_type = FileType.HDF5
                    with contextlib.suppress(Exception):
                        with netcdf4.Dataset(value):
                            file_type = FileType.HDF5_NETCDF
                if value.suffix == ".json":
                    with contextlib.suppress(Exception):
                        json.load(value.open())
                        file_type = FileType.JSON
                if file_extension is not None and f".{file_extension}" != value.suffix:
                    raise ValueError(f"The file extension {file_extension} is not supported for the file {value}. Please use {value.suffix}.")
                
                shutil.copyfile(value, destination)
            elif isinstance(value, str):
                if file_extension is not None and file_extension != "txt":
                    raise ValueError(f"The file extension {file_extension} is not supported for txt files. Please use .txt.")
                fname = f'{name}.txt'
                destination = fpath + fname
                with open(destination, "w") as outfile:
                    outfile.write(value)
            elif is_scalar(value) or is_iterable(value):
                if file_extension is not None and file_extension != "json":
                    raise ValueError(f"The file extension {file_extension} is not supported for json files. Please use .json.")
                fname = f'{name}.json'
                destination = fpath + fname
                with open(destination, "w") as outfile:
                    json.dump(value, outfile)
                file_type = FileType.JSON
                generator = f"json.{json.__version__}"
            elif isinstance(value, h5py.File):
                if file_extension is not None and file_extension != "hdf5":
                    raise ValueError(f"The file extension {file_extension} is not supported for hdf5 files. Please use .hdf5.")
                fname = f'{name}.hdf5'
                destination = fpath + fname
                
                ori_filename = (value.file.filename)
                value.file.close()
                shutil.copyfile(ori_filename, destination)
                file_type = FileType.HDF5
                generator = f"h5py.{h5py.__version__}"
            elif isinstance(value, (xarray.Dataset, xarray.DataArray)):
                if file_extension is not None and (file_extension != "nc" and file_extension != "hdf5" and file_extension != "h5"):
                    raise ValueError(f"The file extension {file_extension} is not supported for hdf5 files. Please use .hdf5.")
                fname = f'{name}.{file_extension}'
                destination = fpath + fname
                if isinstance(value, xarray.Dataset):
                    value = xarray_dataset_attr_formatter_to_json(value)
                elif isinstance(value, xarray.DataArray):
                    value = xarray_dataArray_attr_formatter_json(value)
                comp = {"zlib": True, "complevel": 3}
                encoding = {var: comp for var in list(value.data_vars)+list(value.coords)}
                value.to_netcdf(destination, engine='h5netcdf', invalid_netcdf=True, encoding=encoding)
                file_type = FileType.HDF5_NETCDF
                generator = f"xarray.{xarray.__version__}"
            else: 
                raise ValueError(f"Assignment of the type {type(value)} is not supported.")
            
            self._add_new_file(filename, destination, file_type, generator)
        else:
            self.file_obj[filename].update(value)
    
    def __load_file(self, file : file_object):
        if file.current.type is FileType.HDF5_NETCDF or file.current.type is FileType.HDF5_CACHE:
            file_modifier = HDF5_file(file)
        elif file.current.type is FileType.HDF5:
            file_modifier = HDF5_file(file)
        elif file.current.type is FileType.JSON:
            file_modifier = JSON_file(file)
        elif file.current.type is FileType.NDARRAY:
            file_modifier = numpy_file(file)
        elif file.current.type is FileType.TEXT:
            file_modifier = file_file(file)
        elif file.current.type is FileType.UNKNOWN:
            file_modifier = file_file(file)
        else:
            raise ValueError("Unrecognized file type. Contact support.")
        
        if file_modifier.name not in self.file_obj:
            self.file_obj[file.filename] = file_modifier
        else:
            self.file_obj[file.filename] += file_modifier
        self.name_router[file.name] = file.filename
        
    def _add_new_file(self, filename, file_path, file_type, generator, file_status = FileStatusLocal.complete ):
        name = filename.rsplit('.', 1)[0] if '.' in filename else filename
        file = self.file_mgr_core.add_new_file(name, filename, file_path, file_type, file_status, generator)
        self.__load_file(file)
        if len(self.file_mgr_core) > 50:
            message = f"Many files are present in the dataset ({len(self.file_mgr_core)}). Is this necessary?"
            warnings.warn(message)

    def __len__(self):
        return len(self.file_obj)
    
    def __iter__(self):
        return iter(self.file_obj.values())
    
    def keys(self):
        return list(self.file_obj.keys())
