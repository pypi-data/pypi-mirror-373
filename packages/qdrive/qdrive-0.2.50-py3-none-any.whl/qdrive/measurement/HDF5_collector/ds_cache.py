from typing import List, TYPE_CHECKING

from qdrive.measurement.data_collector_var import get_var, set_var_dynamic, set_var_static
from qdrive.measurement.HDF5_collector.h5_cache import BRANCH_DETECTED_EXCEPTION

if TYPE_CHECKING:
    from qdrive.measurement.HDF5_collector.h5_writer_container import h5_writer_container

import numpy as np

class IRREGULAR_DATASET_EXCEPTION(Exception):
    pass

# TODO :: find a better name for this class
# TODO :: check if flat cache really needed?
class ds_cache:
    '''
    Represents the cache of a single variable of a dataset (e.g. a setpoint or getter).
    Multiple ds_caches can be linked to a single h5_writer, i.e. to avoid storing the same setpoints twice.
    When a divergence between different setpoints occurs, new h5_writers are automatically constructed (i.e. BRANCH_DETECTED_EXCEPTION)
    -- this only happens when SWMR is not enabled.
    '''
    def __init__(self, data_collection : 'h5_writer_container',
                 var_info : 'get_var | set_var_dynamic | set_var_static', ndim, nth_dim):
        self.ndim = ndim
        self.nth_dim = nth_dim
        self.var_info = var_info
        self.data_collection = data_collection
        self.writer = data_collection.create_writer(var_info, ndim)

        self.flat_cache = None
        if ndim > 1 and not isinstance(var_info, get_var):
            self.flat_cache = np.full((100,), np.nan)
        
        self.__last_result = None

        self.__flat_cursor = 0
        self.__relative_cursor = 0

        self.__children : List[ds_cache] = []

    @property
    def name(self):
        return self.writer.name

    @property
    def dataset(self):
        return self.writer.dataset
    
    def write(self):
        self.writer.write()

    def complete(self):
        self.writer.complete()
    
    def add_child(self, child : 'ds_cache'):
        self.__children.append(child)

    def add_result(self, result):
        if isinstance(result, (list, tuple)) :
            result = np.asarray(result)

        if self.flat_cache is not None:
            self.__increase_cache()
            self.flat_cache[self.__flat_cursor] = result
            self.__flat_cursor += 1
        
        if self.nth_dim != 0 and self.__last_result == result:
            return
        else:
            self.__last_result = result
            if self.__relative_cursor != 0 and self.nth_dim != 0:
                self.__reset_child_idx()

        try:
            self.writer.add_result(self.__relative_cursor, result)
            self.__relative_cursor += 1
        except BRANCH_DETECTED_EXCEPTION:
            if self.__flat_cursor-1 != self.__relative_cursor:
                raise IRREGULAR_DATASET_EXCEPTION
            
            # check if a suitable dataset branch is available
            other_writer = self.writer.derived_writer
            while (other_writer is not None):
                if other_writer.cache.check_result(self.__relative_cursor, result):
                    self.writer = other_writer
                    self.__relative_cursor += 1
                    return
                other_writer = other_writer.derived_writer

            self.writer = self.data_collection.duplicate_setpoint(self.writer, self.__relative_cursor)
            self.writer.add_result(self.__relative_cursor, result)
            self.__relative_cursor += 1
        # TODO CLEAN
        except Exception as err:
            print(f"Unexpected {err}, {type(err)}")
            print('Data will be stored.')
            raise err

    def __reset_child_idx(self):
        for child in self.__children:
            child.__relative_cursor = 0
            child.__last_result = None
            if child.writer.data.ndim > 1:
                child.writer.reset_index(self.nth_dim)

    def __increase_cache(self):
        if self.flat_cache is None:
            raise Exception("Flat cache not initialized")
        
        if self.__flat_cursor +1 >= self.flat_cache.size:
            size = self.flat_cache.size
            self.flat_cache.resize([size*2])
            self.flat_cache[size:] = np.nan