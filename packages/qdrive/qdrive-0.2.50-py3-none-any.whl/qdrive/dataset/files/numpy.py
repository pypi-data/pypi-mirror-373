import numpy, os
from qdrive.dataset.files.file_mgr_single import file_mgr_single

class numpy_file(file_mgr_single):
    @property           
    def raw(self):
        if self.object_handle == None:
            self.object_handle = numpy.load(self.file_obj.current.path)
            if len(self.object_handle.files) == 1 and is_npz_array(self.object_handle):
                self.object_handle = self.object_handle[self.object_handle.files[0]]
            elif is_npz_array(self.object_handle):
                out = []
                for file in self.object_handle.files:
                    out.append(self.object_handle[file])
                self.object_handle = out
            else :
                out = {}
                for file in self.object_handle.files:
                    out[file] = self.object_handle[file]
                self.object_handle = out
        return self.object_handle
    
    def __getitem__(self, item):
        if isinstance(self.raw, (dict, list)):
            return self.raw[item]
        elif item==0:
            return self.raw
        else:
            raise ValueError("The numpy object can be accessed by calling myds[my_file].raw .")
    
    def update(self, object):
        path = self._create_new_file_path(f'{self.name}.npz')
        
        if isinstance(object, numpy.ndarray):
            numpy.savez_compressed(path, object)
        elif is_numpy_array(object):
            numpy.savez_compressed(path, *object)
        elif is_numpy_dict(object):
            numpy.savez_compressed(path, **object)
        else:
            raise ValueError("Unexpected arguments ..")
        self._update(path)
        
def is_npz_array(object):
    i = 0
    for file in object.files:
        if file != f"arr_{i}":
            return False
        i+=1
    return True

def is_numpy_array(object):
    if not isinstance(object, list):
        return False
    for i in object:
        if not isinstance(i, numpy.ndarray):
            return False
    return True

def is_numpy_dict(object):
    if not isinstance(object, dict):
        return False
    for i in object.values():
        if not isinstance(i, numpy.ndarray):
            return False
    if len(object) == 0:
        return False
    return True