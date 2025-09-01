import numpy as np

class BRANCH_DETECTED_EXCEPTION(Exception):
    pass

# TODO this caching should remove itselves once parts are writen to the hdf5 file.
class h5_dynamic_cache:
    def __init__(self, ndim, result_shape = [], cache=None, cursor=None, maxsize = 0):
        '''
        dynamic cache that can grow dynamically in time,

        Args:
            ndim (int) : number of dimensions of the cache (not including the dimension of the result)
            result_shape (list) : shape of the result
            cache (np.ndarray) : can be provided if the cache needs to be loaded with values
            cursor (list) : indicating at what indices the next write will occur
            maxsize (int) : maximum size of the lowest dimension (used to measure correct shape of the ds)
        '''
        self.ndim = ndim
        self.result_shape = result_shape

        if ndim == 0:
            shape = list(self.result_shape)
            if shape == []:
                shape = [1]
        else:
            shape = [1]*(ndim-1) + [100] + list(self.result_shape)

        if cache is None:
            self.cache = np.full(shape, np.nan)
        else:
            self.cache = np.array(cache)
            
        if cursor is None:
            self.cursor = [0]*ndim
            if ndim == 0:
                self.cursor = [0]
        else:
            self.cursor = list(cursor)

        self.__shape = [1]*ndim
        self.__maxsize = maxsize

    @property
    def size(self):
        return np.prod(self.shape)

    @property
    def shape(self):
        if self.ndim == 0:
            return self.result_shape
        self.__shape[-1] = self.__maxsize
        return self.__shape + self.result_shape

    @staticmethod
    def from_cache(cache, index):
        '''
        create a dynamic cache from an existing cache (only meant for setpoints)

        Args:
            cache (dynamic_cache) : other cache
            index (int) : the index at which new writes should start
        '''
        if len(cache.result_shape) > 0:
            raise NotImplementedError("reset cache only supported for 0D results.")
        if cache.ndim != 1:
            raise NotImplementedError("reset cache only supported for 1D arrays.")
        
        data = np.copy(cache.cache)
        data[index:] = np.nan

        return h5_dynamic_cache(ndim = 1, result_shape = [], 
                                cache=data, cursor=[index],
                                maxsize=index)

    def check_result(self, index, result):
        if self.cache[index] == result:
            return True
        return False
        
    def add_result(self, index, result):
        if self.ndim == 0:
            self.cache[:] = result
            self.cursor[0] += 1
        else:
            if index == self.cursor[self.ndim-1]:
                if self.cursor[self.ndim-1] >= self.cache.shape[self.ndim-1]:
                    self.__extend_shape(self.ndim-1)
                
                self.cache[tuple(self.cursor)] = result
                self.cursor[self.ndim-1] += 1

                if self.cursor[self.ndim-1] > self.__maxsize:
                    self.__maxsize = self.cursor[self.ndim-1]
            elif index < self.cursor[self.ndim-1]:
                if self.cache[index] != result:
                    raise BRANCH_DETECTED_EXCEPTION
            else:
                raise Exception("Index at which to write results is running ahead, this should not be contact support.")

    def __extend_shape(self, dim):
        old_shape = list(self.cache.shape)
        new_shape = list(self.cache.shape)
        new_shape[dim] *= 2

        new_cache = np.full(new_shape, np.nan)
        new_cache[tuple([slice(0, i) for i in old_shape])] = self.cache
        self.cache = new_cache

    def increase_index(self, dim):
        # TODO this a little ugly, get rid of it by changing design.
        dim_idx = self.ndim-1-dim
        self.cursor[dim_idx] += 1
        
        for i in range(dim_idx + 1, self.ndim):
            self.cursor[i] = 0

        if self.cursor[dim_idx] >= self.cache.shape[dim_idx]:
            self.__extend_shape(dim_idx)
        
        if self.cursor[dim_idx] >= self.__shape[dim_idx]:
            self.__shape[dim_idx] = self.cursor[dim_idx] + 1
        
class H5_static_cache:
    def __init__(self, ndim, data):
        self.ndim = ndim
        self.result_shape = ((),)

        self.cache = data
        self.cursor = list(data.shape)
        self.n_writes = 1

    @property 
    def shape(self):
        return self.cache.shape
    
    @property
    def size(self):
        return np.prod(self.shape)

    def add_result(self, index, result):
        raise NotImplementedError

    def increase_index(self, dim):
        raise NotImplementedError
    
    @staticmethod
    def from_cache(cache, n_writes):
        raise NotImplementedError