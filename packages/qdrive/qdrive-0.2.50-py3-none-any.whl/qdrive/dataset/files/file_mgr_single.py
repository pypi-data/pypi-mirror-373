from etiket_client.python_api.dataset_model.files import file_object, generate_version_id
from etiket_client.settings.folders import create_file_dir

import abc, shutil, os, warnings, typing


# TODO should we have a rename or delete function?
class file_mgr_single(abc.ABC):
    def __init__(self, file_obj: file_object):
        self.file_obj = file_obj
        self._n_writes = 0
        self.object_handle = None

    @property
    def name(self):
        return self.file_obj.current.name

    @property
    def filename(self):
        return self.file_obj.current.filename
    
    @property
    def type(self):
        return self.file_obj.current.type
    
    @property
    def local(self):
        return self.file_obj.current.local
    
    @property
    def path(self):
        return self.file_obj.current.path

    def __call__(self):
        return self.raw()

    @property
    @abc.abstractmethod
    def raw(self):
        pass
    
    @property
    def versions(self) -> 'typing.List[int]':
        return [i for i in range(len(self.file_obj.versions))]
    
    @property
    def version_info(self) -> file_object:
        return self.file_obj
    
    def version(self, version_number : int) -> 'typing.Type[typing.Self]':
        self.file_obj.set_version_number(version_number)
        self.object_handle = None
        return self
    
    @property
    def version_ids(self) -> 'typing.List[int]':
        return self.file_obj.versions

    def version_id(self, version_id : 'int'):
        self.file_obj.set_version_id(version_id)
        self.object_handle = None
        return self
    
    def current_version(self) -> 'int':
        return self.file_obj.current.version_id
    
    def export(self, path, file_name):
        '''
        Export the file to the targetted location.
        '''
        if not os.path.exists(path):
            os.makedirs(path)
        if not path.endswith("/"):
            path += "/"
        
        shutil.copyfile(self.file_obj.current.path, path+file_name)
        print(f'Exported {self.name} to the following location\n\t {path+file_name}')
    
    @abc.abstractmethod
    def update(self, item):
        '''
        Updates the current file. A new version of the file will be created.
        '''
        pass
    
    def _create_new_file_path(self, file_name):
        version_id = generate_version_id()
        path = create_file_dir(self.file_obj.dataset.scope.uuid, self.file_obj.dataset.uuid, self.file_obj.current.uuid, version_id)
        return path + file_name
    
    def _update(self, full_path):
        self.file_obj.update_version_of_current_file(full_path)
        self.object_handle = None
        
        # TODO add docs that document when new versions are made.
        if len(self.versions) >50 :
            message = f"detecting many of versions ({len(self.versions)}) of the same file ({self.name}). Is this really needed?"
            warnings.warn(message)
    
    def _save(self):
        self.file_obj.save_current_file()

        self._n_writes += 1
        if self._n_writes >50 :
            message = f"detecting many modifications ({self._n_writes}) to the same file ({self.name}). Is this really needed?"
            warnings.warn(message)

    def __repr__(self):
        return str(self.raw)