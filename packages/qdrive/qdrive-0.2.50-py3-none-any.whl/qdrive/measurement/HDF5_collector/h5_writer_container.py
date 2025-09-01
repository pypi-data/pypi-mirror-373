from qdrive.measurement.data_collector_var import set_var_static, set_var_dynamic, get_var
from qdrive.measurement.HDF5_collector.h5_cache import h5_dynamic_cache, H5_static_cache
from qdrive.measurement.HDF5_collector.h5_writer import h5_writer
from qdrive.measurement.HDF5_collector.h5_dependency_builder import create_str_attr

import h5py as h5
import numpy as np

# TODO test if everything works well for big chunks, e.g. digitizer data
class h5_writer_container(dict):
    '''
    Contains a dict that holds all the datasets that are open in the current HDF5 file
    '''
    def __init__(self, h5_file):
        self.h5_file = h5_file

    def create_writer(self, var_info : 'get_var | set_var_dynamic | set_var_static', ndim : int) -> h5_writer:
        if isinstance(var_info, get_var):
            if var_info.name in self.keys():
                raise ValueError(f'The same parameter {var_info.name} is submitted twice?\nThis is not allowed.')
            dataset_cache = h5_dynamic_cache(ndim, var_info.result_shape)
        elif isinstance(var_info, set_var_dynamic):
            if var_info.name in self.keys():
                return self[var_info.name]
            dataset_cache = h5_dynamic_cache(1)
        elif isinstance(var_info, set_var_static):
            # TODO ensure that is can't be a problem.
            if var_info.name in self.keys():
                raise ValueError(f'This is a problem')
            dataset_cache = H5_static_cache(1, var_info.data)
        else:
            raise ValueError

        HDF5_dataset = create_ds(self.h5_file, var_info, dataset_cache)
        writer = h5_writer(dataset_cache, HDF5_dataset, var_info, self)
        self[var_info.name] = writer

        return writer

    def duplicate_setpoint(self, old_writer, current_idx):
        # resolve  naming
        name = list(self.keys())[list(self.values()).index(old_writer)]
        old_writer.remove_reference()

        name_split = name.rsplit('_', 1)
        # TODO :: check if this is robust
        if len(name_split) == 2 and name_split[-1].isdigit():
            new_name = self.__find_new_name(name_split[0])
            self[new_name] = duplicate_writer(self, self.h5_file, old_writer, current_idx, new_name)
            return self[new_name]
        else:
            old_new_name = f"{name}_0"
            new_new_name = f"{name}_1"

            self[old_new_name] = self[name]
            self[old_new_name].name = old_new_name
            del self[name]

            self[new_new_name] = duplicate_writer(self, self.h5_file, old_writer, current_idx, new_new_name)
            return self[new_new_name]

    def __find_new_name(self, base):
        i = 1
        while (f"{base}_{i-1}" in self.keys()):
            i+=1
        return f"{base}_{i}"

# TODO check various compression algorithms vs performance
# spin qubit data sets (https://pypi.org/project/hdf5plugin/)
def create_ds(h5_file : 'h5.File', var_info : 'get_var | set_var_dynamic | set_var_static', cache : 'h5_dynamic_cache | H5_static_cache', name=None) -> 'h5.Dataset':
    shape = cache.cache.shape
    max_shape =  [None for i in range(len(shape))]

    result_shape = []
    if isinstance(var_info, get_var):
        result_shape = var_info.result_shape
        
    # create chunks : target 10-1000 KB
    chunk_size = [1 for i in range(len(shape))]
    chunk_size[-1] = 1000
    
    if isinstance(var_info, get_var):
        size_result_shape = 1
        for i in result_shape:
            size_result_shape *= i
        
        # Recommended size between 10KB-1MB
        if size_result_shape*64 < 64e3:
            chunk_size[var_info.ndim-1] = int(1e3/size_result_shape)
            chunk_size[var_info.ndim:] = result_shape 
        elif size_result_shape*64 < 1e6:
            chunk_size[var_info.ndim:] = result_shape 
        else:  # expected large dataset, so we also take big chunks.
            chunk_size[var_info.ndim:] = calc_chunk_size_large_ds(result_shape)
    elif isinstance(var_info, set_var_static):
            chunk_size = calc_chunk_size_large_ds(cache.cache.shape)
    
    if name is None:
        name = var_info.name
    
    ds =  h5_file.create_dataset(name, shape, maxshape = tuple(max_shape),
                                chunks=tuple(chunk_size), dtype='f8',
                                compression="gzip",compression_opts=3, fillvalue=np.nan)

    ds.attrs['long_name'] = var_info.label
    ds.attrs['units'] = var_info.unit

    ds.attrs['completed'] = False
    if isinstance(var_info, get_var):
        if var_info.ndim == 0:
            ds.attrs.create('__cursor', [0], dtype=np.int32, shape=(1,))
        else:
            ds.attrs.create('__cursor', [0]*var_info.ndim, dtype=np.int32, shape=(var_info.ndim,))
        ds.attrs.create('__shape', [0]*(var_info.ndim + len(var_info.result_shape)), dtype=np.int32, shape=(var_info.ndim + len(var_info.result_shape),))
    else:
        ds.attrs.create('__cursor', [0], dtype=np.int32, shape=(1,))
        ds.attrs.create('__shape', [0], dtype=np.int32, shape=(1,))
    return ds


def duplicate_writer(writer_coll, h5_file, old_writer, index, name):
    dataset_cache = h5_dynamic_cache.from_cache(old_writer.cache, index)
    HDF5_dataset = create_ds(h5_file, old_writer.var_info, dataset_cache, name)
    return h5_writer(dataset_cache, HDF5_dataset, old_writer.var_info, writer_coll)

def calc_chunk_size_large_ds(shape):
    max_chunk_size = 4096
    chunk_of_result = []

    combined_chunk_size = 1
    for dim_shape in reversed(shape):           
        if combined_chunk_size > max_chunk_size:
            chunk_of_result.append(1)
            continue

        if dim_shape * combined_chunk_size < max_chunk_size:
            chunk_of_result.append(dim_shape)
            combined_chunk_size *= dim_shape
        else:
            size = max(1, int(max_chunk_size / combined_chunk_size))
            chunk_of_result.append(size)
            combined_chunk_size *= size

    return list(reversed(chunk_of_result))