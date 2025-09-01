import shutil, os
from qdrive.dataset.files.file_mgr_single import file_mgr_single

class file_file(file_mgr_single):
    @property           
    def raw(self):
        raise ValueError("Cannot load a file of unknown type. It is possible to load the file yourself using the path variable of the file object (e.g. ds[\"my_file\"].path)")
    
    @property
    def path(self):
        return self.file_obj.current.path
    
    def update(self, file_path):
        if not os.path.isfile(file_path):
            raise ValueError("File does not exist")
        path = self._create_new_file_path(os.path.split(file_path)[1])
        shutil.copyfile(file_path, path)
        self._update(path)
        
    def __repr__(self):
        if self.path.endswith(".py") or self.path.endswith(".txt"):
            with open(self.path) as file:
                data = file.read()
            return data
        return f"File at {self.path}"