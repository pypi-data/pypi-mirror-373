from qdrive.dataset.files.file_mgr_single import file_mgr_single
from qdrive.dataset.files.utility import is_scalar, is_iterable

import json, copy

class JSON_file(file_mgr_single):
    def __init__(self, file_info):
        super().__init__(file_info)
        
    @property
    def raw(self):
        if self.object_handle == None:
            with open(self.file_obj.current.path) as _json_file:
                self.object_handle = json.load(_json_file)
            self.local_handle =  self.object_handle
        return self.object_handle
    
    @property
    def json(self):
        return copy.deepcopy(self.raw)
    
    def __getitem__(self, key):
        self.__load()
        if is_iterable(self.local_handle):
            obj_slice = self.local_handle[key]
            return self.__create_from_self(obj_slice)
        else :
            raise ValueError(f"object of the type {type(self.raw)} cannot be accessed using this operator.")
    
    def __setitem__(self, key, value):
        self.__load()
        if is_iterable(self.local_handle):
            self.local_handle[key] = value
            self.__save()
        else :
            raise ValueError(f"object of the type {type(self.raw)} cannot be accessed using this operator.")
    
    def keys(self):
        self.__load()
        if isinstance(self.local_handle, dict):
            return self.local_handle.keys()
        raise ValueError("This operator is only supported for dict objects")

    def values(self):
        self.__load()
        if isinstance(self.local_handle, dict):
            return self.local_handle.values()
        raise ValueError("This operator is only supported for dict objects")
    
    def items(self):
        self.__load()
        if isinstance(self.local_handle, dict):
            return self.local_handle.items()
        raise ValueError("This operator is only supported for dict objects")
    
    def append(self, value):
        if isinstance(self.local_handle, list):
            self.local_handle.append(value)
            self.__save()
        else:
            raise ValueError(f"object of the type {type(self.raw)} can only append to the type list.")
    
    def __len__(self):
        self.__load()
        return len(self.local_handle)
    
    def __iter__(self):
        if isinstance(self.local_handle, (list, tuple)):
            return iter(self.local_handle)
        return None
    
    def update(self, object):
        new_desination = self._create_new_file_path(f'{self.name}.json')
        if is_scalar(object) or is_iterable(object):
            with open(new_desination, "w") as outfile:
                    json.dump(object, outfile)
        else:
            raise ValueError("Please provide a type compatible with the json file format.")
        self._update(new_desination)
    
    def __repr__(self):
        self.__load()
        return str(self.local_handle)

    def __load(self):
        return self.raw
    
    def __save(self):
        with open(self.file_obj.current.path, "w") as outfile:
            json.dump(self.object_handle, outfile)
        self._save() # save update in database

    def __create_from_self(self, local_handle):
        # TODO copy should be made here?
        new = JSON_file(self.file_obj)
        new.object_handle = self.object_handle
        new.local_handle = local_handle
        return new