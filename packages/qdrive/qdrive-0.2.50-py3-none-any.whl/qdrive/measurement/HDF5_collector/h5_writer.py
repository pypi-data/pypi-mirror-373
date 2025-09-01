import h5py as h5
import numpy as np

from qdrive.measurement.HDF5_collector.h5_cache import H5_static_cache, h5_dynamic_cache


class h5_writer:
    def __init__(self, cache : 'h5_dynamic_cache | H5_static_cache', dataset : 'h5.Dataset', var_info, ds_collection):
        self.cache = cache
        self.dataset = dataset
        self.var_info = var_info
        self.writer_collection = ds_collection

        self.cursor = [0 for i in range(self.cache.ndim)]
        self.reference_count = 1

        self.derived_writer = None

    @property
    def name(self):
        return self.dataset.name

    @name.setter
    def name(self, name):
        self.writer_collection.h5_file[name] =  self.dataset
        self.dataset = self.writer_collection.h5_file[name]

    @property
    def size(self):
        return self.cache.size

    @property
    def shape(self):
        return self.cache.shape
    
    @property
    def ndim(self):
        return self.cache.ndim
    
    @property
    def data(self):
        return self.cache.cache

    def add_result(self, index, result):
        self.cache.add_result(index, result)

    def reset_index(self, dimension):
        self.cache.increase_index(dimension)

    def write(self):
        if self.cursor == self.cache.cursor:
            return

        if self.dataset.shape != self.data.shape:
            self.dataset.resize(self.data.shape)
        
        if self.ndim != 0: 
            # this can be done better, but right now not a performance limitation
            slices = []
            for i in range(len(self.dataset.shape)):
                if self.cursor[i] == self.cache.cursor[i]:
                    slices.append(slice(self.cursor[i], self.cursor[i]+1))
                else:
                    if i == self.cache.ndim-1:
                        slices.append(slice(self.cursor[i], self.cache.cursor[i]))
                    else:
                        slices.append(slice(self.cursor[i], self.cache.cursor[i]+1))
                    break
            self.dataset.write_direct(self.data, np.s_[tuple(slices)], np.s_[tuple(slices)])
        else: 
            self.dataset.write_direct(self.data)
        
        self.cursor = list(self.cache.cursor)
        self.dataset.attrs.modify('__cursor', np.array(self.cursor, dtype=np.int32))
        self.dataset.attrs.modify('__shape', np.array(self.shape, dtype=np.int32))
        
    def complete(self):
        self.dataset.resize(self.shape)
        self.dataset.attrs['completed'] = True
        
    def remove_reference(self):
        self.reference_count -=1
        if self.reference_count == 0:
            del self.writer_collection.h5_file[self.dataset.name]
