import qdrive, uuid, os

from typing import Optional

from etiket_client.remote.endpoints.dataset import dataset_create, dataset_read_by_alt_uid
from etiket_client.remote.endpoints.file import file_create, file_generate_presigned_upload_link_single, file_read, FileSelect
from etiket_client.remote.endpoints.models.dataset import DatasetCreate, DatasetRead
from etiket_client.remote.endpoints.models.file import FileCreate, FileStatusRem, FileType, FileRead
from etiket_client.sync.uploader.file_uploader import upload_new_file_single
from etiket_client.local.exceptions import DatasetNotFoundException

from etiket_client.sync.base.checksums.hdf5 import md5_netcdf4
from etiket_client.sync.base.checksums.any import md5

def check_file_remote_ds(remote_ds: DatasetRead, file_name: str, file_version: str) -> Optional[FileRead]:
    for file in remote_ds.files:
        if file.name == file_name:
            if file.version_id == file_version:
                return file
    return None

def copy_dataset(dataset_src_uuid, scope_src_uuid, scope_dst_uuid):
    '''
    Copy a dataset from one scope to another. Do note that the copied dataset will get a new UUID!
    
    Args:
        dataset_src_uuid: The UUID of the dataset to copy.
        scope_dst_uuid: The UUID of the scope to copy the dataset to.
    '''    
    print("----------------------------------------------------------------")
    print("Copying dataset with UUID", dataset_src_uuid, " in scope, ", scope_src_uuid, " to ", scope_dst_uuid, "\n")
    ds = qdrive.dataset(dataset_src_uuid, scope_src_uuid)
    try :
        if ds.alt_uid is not None:
            dataset_read_by_alt_uid(str(ds.alt_uid), scope_dst_uuid)
        else:
            dataset_read_by_alt_uid(str(ds.uuid), scope_dst_uuid)
    except DatasetNotFoundException:
        dc = DatasetCreate(uuid = uuid.uuid4(), alt_uid= ds.alt_uid if ds.alt_uid is not None else str(ds.uuid),
                collected=ds.collected,  name = ds.name, creator = ds.creator,
                description= ds.description, keywords = ds.keywords,
                ranking= ds.ranking, scope_uuid = scope_dst_uuid, 
                attributes = ds.attributes)
        dataset_create(dc)
    
    # read the dataset from the remote server
    if ds.alt_uid is not None:
        new_ds = dataset_read_by_alt_uid(ds.alt_uid, scope_dst_uuid)       
    else:
        new_ds = dataset_read_by_alt_uid(ds.uuid, scope_dst_uuid)       
    
    # copy the files from the remote server to the local server
    for file in ds:
        file_obj = file.file_obj      
        for version in file.version_ids:
            file_obj.set_version_id(version)
            file_version = file_obj.current
            file_path = file.path
            size_bytes = os.path.getsize(file_path)
            file_read_server = check_file_remote_ds(new_ds, file_version.name, file_version.version_id)
            
            file_uuid = uuid.uuid4()
            if file_read_server is None:
                print(f"CREATING FILE {file_version.name} ({file_version.filename})- {file_version.version_id} ON REMOTE SERVER")
                fc = FileCreate(name=file_version.name, filename = file_version.filename,
                    uuid=file_uuid, creator=file_version.creator, collected=file_version.collected,
                    size=size_bytes, type=file_version.type, file_generator="", version_id=file_version.version_id,
                    ranking=file_version.ranking, immutable=True, ds_uuid=new_ds.uuid)
                file_create(fc)
                file_select = FileSelect(uuid=file_uuid, version_id=file_version.version_id)
                file_read_server = file_read(file_select)[0]
                print("CREATED")
            else:
                print(f"FILE {file_version.name} - {file_version.version_id} ALREADY EXISTS ON REMOTE SERVER")
            
            if file_read_server.status != FileStatusRem.secured:
                print(f"STARTING UPLOAD with size {size_bytes / (1024 * 1024):.4f} MB")
                # upload the file to the remote server
                md5_checksum = md5(file_path)
                if file_version.type == FileType.HDF5_NETCDF:
                    md5_checksum_netcdf4 = md5_netcdf4(file_path)
                else:
                    md5_checksum_netcdf4 = None
                upload_info = file_generate_presigned_upload_link_single(file_read_server.uuid, file_read_server.version_id)
                upload_new_file_single(file_path, upload_info, md5_checksum, md5_checksum_netcdf4)
                print("UPLOADED")
            else:
                print("File IS ALREADY UPLOADED")
    print("\n")