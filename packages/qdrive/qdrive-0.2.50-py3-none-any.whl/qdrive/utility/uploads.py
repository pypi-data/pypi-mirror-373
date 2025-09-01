import pathlib, uuid, os, xarray, datetime, yaml, tempfile, contextlib

from typing import List, Optional
from dataclasses import dataclass

from qdrive import dataset
from qdrive.scopes import get_default_scope, get_scope
from etiket_client.sync.backends.filebase.manifest import Manifest, sync_item
from etiket_client.sync.base.manifest_v2 import QH_DATASET_INFO_FILE, QH_MANIFEST_FILE

from etiket_client.settings.user_settings import user_settings

from etiket_client.remote.endpoints.dataset import dataset_create, dataset_read, dataset_update
from etiket_client.remote.endpoints.file import file_create, file_generate_presigned_upload_link_single, file_read, FileSelect
from etiket_client.remote.endpoints.models.dataset import DatasetCreate, DatasetRead, DatasetUpdate
from etiket_client.remote.endpoints.models.file import FileCreate, FileStatusRem, FileType, FileRead
from etiket_client.sync.uploader.file_uploader import upload_new_file_single
from etiket_client.local.exceptions import DatasetNotFoundException
from etiket_client.local.dao.dataset import dao_dataset
from etiket_client.local.models.dataset import DatasetCreate as DatasetCreateLocal
from etiket_client.local.dao.file import dao_file, FileSelect as FileSelectLocal
from etiket_client.local.models.file import FileCreate as FileCreateLocal, FileStatusLocal
from etiket_client.local.database import get_db_session_context
from etiket_client.sync.base.checksums.hdf5 import md5_netcdf4
from etiket_client.sync.base.checksums.any import md5

@dataclass
class FileUploadInfo:
    file_path : pathlib.Path
    name : str
    convert_zarr_to_hdf5 : bool = False
    
    def __post_init__(self):
        self._version_id = self.computed_version_id()
    
    @contextlib.contextmanager
    def load(self):
        if self.convert_zarr_to_hdf5:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = pathlib.Path(temp_dir) / (str(self.name)[:-5] + ".hdf5")
                xarray.open_zarr(self.file_path).to_netcdf(temp_path, engine='h5netcdf', invalid_netcdf=True)
                zarr_path = self.file_path
                zarr_name = zarr_path.name
                self.file_path = temp_path
                self.name = self.name[:-5] + ".hdf5"
                yield self
                # restore
                self.file_path = zarr_path
                self.name = zarr_name
        else:
            yield self
        
    @property
    def version_id(self):
        return self._version_id
    
    def computed_version_id(self):
        if self.convert_zarr_to_hdf5:
            max_mtime = 0.0
            for r, _, fs in os.walk(self.file_path):
                for fn in fs:
                    p = pathlib.Path(r) / fn
                    try:
                        m = p.stat().st_mtime
                        if m > max_mtime:
                            max_mtime = m
                    except FileNotFoundError:
                        continue
            return int(max_mtime * 1000)
        else:
            return int(self.file_path.stat().st_mtime * 1000)
    
    @property
    def created(self):
        def get_ctime(path : pathlib.Path) -> float:
            stat = path.stat()
            if hasattr(stat, "st_birthtime"):
                return stat.st_birthtime
            else:
                return stat.st_ctime
        
        if self.file_path.is_dir():
            min_time = get_ctime(self.file_path)
            for root, _, files in os.walk(self.file_path):
                for fn in files:
                    f_ctime = get_ctime(pathlib.Path(root) / fn)
                    if f_ctime < min_time:
                        min_time = f_ctime
            return datetime.datetime.fromtimestamp(min_time)
        else:
            return datetime.datetime.fromtimestamp(get_ctime(self.file_path))
    
def check_scope_match(scope_uuid : uuid.UUID, folder_path : pathlib.Path) -> bool:
    manifest_path = folder_path / QH_MANIFEST_FILE
    
    if not manifest_path.exists():
        return True
    
    with open(manifest_path, 'r', encoding="utf-8") as f:
        manifest_raw = yaml.safe_load(f)
        # if the scope uuid is the same as the updated scope uuid, update the manifest
        if 'scope_uuid' in manifest_raw:
            return scope_uuid == uuid.UUID(manifest_raw['scope_uuid'])
        else:
            return False
        
def update_scope_uuid(scope_uuid : uuid.UUID, folder_path : pathlib.Path):
    manifest_path = folder_path / QH_MANIFEST_FILE
    with open(manifest_path, 'r', encoding="utf-8") as f:
        manifest_raw = yaml.safe_load(f)
        manifest_raw['scope_uuid'] = str(scope_uuid)
    

def check_file_remote_ds(remote_ds: DatasetRead, file_name: str, file_version: int) -> Optional[FileRead]:
    for file in remote_ds.files:
        if file.name == file_name:
            if file.version_id == file_version:
                return file
    return None

def determine_file_type(file_path: pathlib.Path) -> FileType:
    if file_path.suffix in ['.h5', '.nc', '.hdf5']:
        try:
            with xarray.open_dataset(file_path, engine='h5netcdf'):
                pass
            return FileType.HDF5_NETCDF
        except Exception:
            return FileType.HDF5
    elif file_path.suffix in ['.json']:
        return FileType.JSON
    elif file_path.suffix in ['.npy']:
        return FileType.NDARRAY
    elif file_path.suffix in ['.txt']:
        return FileType.TEXT
    else:
        return FileType.UNKNOWN

def __server_upload(manifest : Manifest, name : str, description : Optional[str],
                    tags : list[str], attributes : dict[str, str], alt_uid : Optional[str],
                    collected : datetime.datetime,
                    files : List[FileUploadInfo]):
    dataset_uuid = uuid.UUID(manifest.manifest.get('dataset_uuid'))
    scope_uuid = uuid.UUID(manifest.manifest.get('scope_uuid'))
    # dataset_sync_path retained via manifest; individual files carry absolute paths
    
    print("----------------------------------------------------------------")
    print("Uploading dataset with UUID", dataset_uuid, " in scope, ", scope_uuid, "\n")
    try :
        ds = dataset_read(dataset_uuid, scope_uuid)
        print("DATASET FOUND")
        # overwrite the dataset info with the new info
        du = DatasetUpdate(alt_uid= alt_uid,name = name,
                            description= description, keywords = list(set(tags + ds.keywords)),
                            attributes = {**(ds.attributes or {}), **attributes})
        dataset_update(ds.uuid, du)
    except DatasetNotFoundException:
        print("CREATING DATASET")
        dc = DatasetCreate(uuid = dataset_uuid, alt_uid= alt_uid,
                collected=collected,  name = name,
                creator = user_settings.user_sub,
                description= description, keywords = tags,
                ranking= 0, scope_uuid = scope_uuid, 
                attributes = attributes)
        dataset_create(dc)
    
    ds_remote = dataset_read(dataset_uuid, scope_uuid)
    
    # copy the files from the remote server to the local server
    for file in files:
        with file.load() as f_loaded:
            file_read_server = check_file_remote_ds(ds_remote, f_loaded.name, f_loaded.version_id)

            file_uuid = uuid.uuid4()
            if file_read_server is None:
                print(f"CREATING FILE {f_loaded.name} - {f_loaded.version_id} ON REMOTE SERVER")
                filename = pathlib.Path(f_loaded.name).name
                fc = FileCreate(name=f_loaded.name, filename = filename, uuid=file_uuid,
                                creator=user_settings.user_sub, collected=f_loaded.created,
                                size=f_loaded.file_path.stat().st_size, type=determine_file_type(f_loaded.file_path),
                                file_generator="", version_id=f_loaded.version_id,
                                ranking=0, immutable=True, ds_uuid=ds_remote.uuid,)
                file_create(fc)
                file_select = FileSelect(uuid=file_uuid, version_id=f_loaded.version_id)
                file_read_server = file_read(file_select)[0]
                print("CREATED")
            else:
                print(f"FILE {f_loaded.name} - {f_loaded.version_id} ALREADY EXISTS ON REMOTE SERVER")
            
            if file_read_server.status != FileStatusRem.secured:
                print(f"STARTING UPLOAD with size {f_loaded.file_path.stat().st_size / (1024 * 1024):.4f} MB")
                # upload the file to the remote server
                md5_checksum = md5(f_loaded.file_path)
                if file_read_server.type == FileType.HDF5_NETCDF:
                    md5_checksum_netcdf4 = md5_netcdf4(f_loaded.file_path)
                else:
                    md5_checksum_netcdf4 = None
                upload_info = file_generate_presigned_upload_link_single(file_read_server.uuid, file_read_server.version_id)
                upload_new_file_single(f_loaded.file_path, upload_info, md5_checksum, md5_checksum_netcdf4)
                print("UPLOADED")
            else:
                print("File IS ALREADY UPLOADED")    

def __local_upload(manifest : Manifest, name : str, description : Optional[str],
                    tags : list[str], attributes : dict[str, str], alt_uid : Optional[str],
                    collected : datetime.datetime, files : List[FileUploadInfo]):
    dataset_uuid = uuid.UUID(manifest.manifest.get('dataset_uuid'))
    scope_uuid = uuid.UUID(manifest.manifest.get('scope_uuid'))
    # dataset_sync_path retained via manifest; individual files carry absolute paths
    
    with get_db_session_context() as session:
        try:
            ds = dataset(dataset_uuid, scope_uuid)
            ds.name = name
            if attributes:
                current_attrs = dict(ds.attributes) if ds.attributes else {}
                merged_attrs = dict(current_attrs)
                merged_attrs.update(attributes)
                if merged_attrs != current_attrs:
                    ds.attributes = merged_attrs
            if ds.tags != list(set(tags + ds.tags)):
                ds.tags = list(set(tags + ds.tags))
            if ds.description != description:
                ds.description = description            
            if ds.alt_uid != alt_uid:
                ds.alt_uid = alt_uid
            print("DATASET FOUND")
        except DatasetNotFoundException:
            print("CREATING DATASET")
            dc = DatasetCreateLocal(uuid = dataset_uuid, alt_uid= alt_uid, collected=collected,  name = name,
                                creator = user_settings.user_sub, description= description, keywords = tags,
                                ranking= 0, scope_uuid = scope_uuid,  attributes = attributes)
            dao_dataset.create(dc, session)
            print("CREATED")
        
        ds = dataset(dataset_uuid, scope_uuid)
        
        for file in files:
            with file.load() as f_loaded:
                file_path = f_loaded.file_path
                version_id = f_loaded.version_id
                name = f_loaded.name
                fname = pathlib.Path(name).name # filename without path
                                
                files_local = dao_file.get_file_by_name(ds.uuid, name, session)
                
                local_version_exists = False
                local_uuid = None
                for file_local in files_local:
                    local_uuid = file_local.uuid
                    if file_local.version_id == version_id:
                        local_version_exists = True
                
                if not local_version_exists:
                    print(f"ADDING FILE {name} - {version_id} TO LOCAL DB")
                    fc = FileCreateLocal(name=name, filename = fname, uuid=local_uuid if local_uuid else uuid.uuid4(),
                                        creator=user_settings.user_sub, collected=f_loaded.created,
                                        size=f_loaded.file_path.stat().st_size, type=determine_file_type(f_loaded.file_path),
                                        file_generator="", version_id=f_loaded.version_id,
                                        ranking=0, synchronized=False, ds_uuid=ds.uuid, status=FileStatusLocal.complete,
                                        local_path=file_path.as_posix())
                    dao_file.create(fc, session)
                else:
                    print(f"FILE {name} - {version_id} ALREADY EXISTS in local db")

def upload_folder(folder_path : str | pathlib.Path, 
                    scope : Optional[str | uuid.UUID] = None,
                    dataset_name : Optional[str] = None,
                    dataset_description : Optional[str] = None,
                    dataset_tags : Optional[list[str]] = None,
                    dataset_attributes : Optional[dict[str, str]] = None,
                    dataset_alt_uid : Optional[str] = None,
                    dataset_collected : Optional[datetime.datetime] = None,
                    direct_upload = False,
                    convert_zarr_to_hdf5 : bool = False,
                    allow_scope_override : bool = False) -> dataset:
    '''
    Upload a folder to a dataset, and adds all the files in the folder to the dataset.
    
    Args:
        folder_path (str | pathlib.Path): The path to the folder to upload.
        scope (str | uuid.UUID): The scope to upload the dataset to. If None, the default scope will be used.
        dataset_name (str): The name of the dataset.
        dataset_description (str): The description of the dataset.
        dataset_tags (list[str]): The tags of the dataset.
        dataset_attributes (dict[str, str]): The attributes of the dataset.
        dataset_alt_uid (str): The alternative unique identifier of the dataset.
        dataset_collected (datetime.datetime): The time the dataset is collected, by default this will be the min creation time of all files.
        direct_upload (bool): If True, the folder will be uploaded directly to the server (no local copy), otherwise a local dataset will be made first and uploaded by the sync agent.
        convert_zarr_to_hdf5 (bool): If True, the Zarr directories will be converted to HDF5 using xarray (otherwise, they will be skipped).
        allow_scope_override (bool): by default, the dataset can only be uploaded to one scope. If True, the scope will be overridden if it does not match the scope to which the folder has already been uploaded.
    Returns:
        dataset (Dataset): The dataset that was uploaded.
    '''
    folder_path = pathlib.Path(folder_path)
    
    if not pathlib.Path(folder_path).exists():
        raise FileNotFoundError(f"Folder {folder_path} does not exist.")
    
    # check if the folder is a directory.
    if not folder_path.is_dir():
        raise NotADirectoryError(f"Folder {folder_path} is not a directory.")
    
    scope_raw = get_scope(scope) if scope is not None else get_default_scope()

    # normalize optional collection arguments to avoid mutable default values
    dataset_tags = dataset_tags or []
    dataset_attributes = dataset_attributes or {}

    syncidentifier = sync_item(datasetUUID=uuid.uuid4(), scopeUUID=scope_raw.uuid,
                                dataIdentifier=str(folder_path), creator=user_settings.user_sub)
    
    if not check_scope_match(scope_raw.uuid, folder_path):
        if allow_scope_override is True:
            update_scope_uuid(scope_raw.uuid, folder_path)
        else:
            raise ValueError(f"Scope {scope_raw.name} does not match scope to which the folder has already been uploaded. Please set allow_scope_override=True if this is intended.")
    
    manifest = Manifest(dataset_path=folder_path, syncIdentifier=syncidentifier)
    manifest.write()

    ds_files: List[FileUploadInfo] = []
    
    for root, dirs, files in os.walk(folder_path):
        zdirs = [d for d in dirs if d.endswith('.zarr')]
        for zd in zdirs:
            zarr_path = (pathlib.Path(root) / zd).resolve()
            relative_path = zarr_path.relative_to(folder_path.resolve())
            ds_files.append(FileUploadInfo(file_path=zarr_path,
                                name=relative_path.as_posix(),
                                convert_zarr_to_hdf5=convert_zarr_to_hdf5))
        
        dirs[:] = [d for d in dirs if not d.endswith('.zarr')]
        for file in files:
            # skip the manifest file.
            if file == QH_MANIFEST_FILE or file == QH_DATASET_INFO_FILE:
                continue
            
            abs_path = (pathlib.Path(root) / file).resolve()
            relative_path = abs_path.relative_to(folder_path.resolve())
            ds_files.append(FileUploadInfo(file_path=abs_path, name=relative_path.as_posix()))
    
    if dataset_name is None:
        dataset_name = folder_path.name
    
    if dataset_collected is None:
        if ds_files:
            dataset_collected = min(file.created for file in ds_files)
        else:
            # creation time of the folder
            dataset_collected = datetime.datetime.fromtimestamp(folder_path.stat().st_ctime)
    
    if direct_upload:
        __server_upload(manifest, dataset_name, dataset_description, dataset_tags, dataset_attributes, dataset_alt_uid, dataset_collected, ds_files)
    else:
        __local_upload(manifest, dataset_name, dataset_description, dataset_tags, dataset_attributes, dataset_alt_uid, dataset_collected, ds_files)

    return dataset(uuid.UUID(manifest.manifest.get('dataset_uuid')), uuid.UUID(manifest.manifest.get('scope_uuid')))