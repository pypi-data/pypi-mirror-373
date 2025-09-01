'''
Test file access for getting and creating files:

Test:
- create a dataset + add a hdf5 file:
    * add a hdf5 file using an xarray
        ** hdf5_file.nc
        --> access as ds['hdf5_file']  and ds['hdf5_file.nc'] should work. -- check that in case without suffix a deprecation warning is raised.
        ** hdf5_file.hdf5
        --> access as ds['hdf5_file']  and ds['hdf5_file.hdf5'] should work. -- check that in case without suffix a deprecation warning is raised.
        ** hdf5_file.h5
        --> access as ds['hdf5_file']  and ds['hdf5_file.h5'] should work. -- check that in case without suffix a deprecation warning is raised.
- create a dataset + add a hdf5 file
    * add a file:
        ** hdf5_file.json
        ** hdf5_file.hdf5
    * should be able to access both files with the extension. When trying to access without the extension, it should raise an exception.
- create files without extension:
    * when adding a file without extension, it should raise an exception.
        - e.g. test --> test json, xarray, numpy array, Path.
    * when adding a file with an extension, it should work.
- test file update:
    * create file 'test_file.hdf5'
    * assign a different xarray to the dataset
    * check that there are two versions of the file
'''

import xarray
import numpy as np
import warnings
import pytest
import tempfile
from pathlib import Path
from qdrive.dataset.dataset import dataset


def test_dataset_file_access_1():
    """Test creating and accessing HDF5 files with different extensions"""
    base_name = "hdf5_file"
    file_names = [f"{base_name}.nc", f"{base_name}.hdf5", f"{base_name}.h5"]
    for file_name in file_names:
        ds = dataset.create(name=f"test_dataset_file_access_1_{file_name}")
        xr_ds = xarray.Dataset(coords={"x": [1, 2, 3]}, data_vars={"y": [4, 5, 6]})
        ds[file_name] = xr_ds
        
        # Test access with full filename
        xr_ds_reloaded = ds[file_name].xarray
        assert xr_ds.equals(xr_ds_reloaded)
        
        # Test access without extension (should show deprecation warning)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            xr_ds_reloaded_2 = ds[base_name].xarray
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "deprecated" in str(w[0].message)
        
        assert xr_ds.equals(xr_ds_reloaded_2)
        
        # reload the dataset -- check if all still works!
        ds_reloaded = dataset(str(ds.uuid))  # Convert to string to avoid type issues
        xr_ds_reloaded_3 = ds_reloaded[file_name].xarray
        assert xr_ds.equals(xr_ds_reloaded_3)
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            xr_ds_reloaded_4 = ds_reloaded[base_name].xarray
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
        
        assert xr_ds.equals(xr_ds_reloaded_4)


def test_dataset_file_access_2():
    """Test creating and accessing files with different extensions (json and hdf5)"""
    ds = dataset.create(name="test_dataset_file_access_2")
    
    # Add JSON file
    json_data = {"param_name": "some_param", "value": 42}
    ds["data_file.json"] = json_data
    
    # Add HDF5 file
    xr_ds = xarray.Dataset(coords={"x": [1, 2, 3]}, data_vars={"y": [4, 5, 6]})
    ds["data_file.hdf5"] = xr_ds
    
    # Should be able to access both files with extension
    reloaded_json = ds["data_file.json"].json
    assert reloaded_json == json_data
    
    reloaded_xr = ds["data_file.hdf5"].xarray
    assert xr_ds.equals(reloaded_xr)
    
    # When trying to access without extension, it should raise an exception
    # since both files have the same base name "data_file"
    with pytest.raises(KeyError):
        ds["data_file"]


def test_dataset_file_without_extension():
    """Test that creating files without extension raises an exception"""
    ds = dataset.create(name="test_dataset_file_without_extension")
    
    # Test with JSON data
    json_data = {"param_name": "some_param"}
    with pytest.raises(ValueError, match="Please provide a filename with a suffix"):
        ds["test_file"] = json_data
    
    # Test with xarray
    xr_ds = xarray.Dataset(coords={"x": [1, 2, 3]}, data_vars={"y": [4, 5, 6]})
    with pytest.raises(ValueError, match="Please provide a filename with a suffix"):
        ds["test_file"] = xr_ds
    
    # Test with numpy array
    np_array = np.array([1, 2, 3, 4, 5])
    with pytest.raises(ValueError, match="Please provide a filename with a suffix"):
        ds["test_file"] = np_array
    
    # Test that adding with extension works
    ds["test_file.json"] = json_data
    ds["test_file.hdf5"] = xr_ds
    ds["test_file.npz"] = np_array
    
    # Verify they were created correctly
    assert ds["test_file.json"].json == json_data
    assert xr_ds.equals(ds["test_file.hdf5"].xarray)
    assert np.array_equal(ds["test_file.npz"].raw, np_array)


def test_dataset_file_update():
    """Test file update functionality - creating multiple versions"""
    ds = dataset.create(name="test_dataset_file_update")
    
    # Create initial file
    xr_ds_1 = xarray.Dataset(coords={"x": [1, 2, 3]}, data_vars={"y": [4, 5, 6]})
    ds["test_file.hdf5"] = xr_ds_1
    
    # Verify initial state
    assert len(ds["test_file.hdf5"].versions) == 1
    assert ds["test_file.hdf5"].current_version() is not None
    
    # Update with different xarray
    xr_ds_2 = xarray.Dataset(coords={"x": [1, 2, 3, 4]}, data_vars={"y": [7, 8, 9, 10]})
    ds["test_file.hdf5"] = xr_ds_2
    
    # Check that there are now two versions
    assert len(ds["test_file.hdf5"].versions) == 2
    
    # Test accessing different versions
    version_0_data = ds["test_file.hdf5"].version(0).xarray
    version_1_data = ds["test_file.hdf5"].version(1).xarray
    
    # Version 0 should be the original data
    assert xr_ds_1.equals(version_0_data)
    # Version 1 should be the updated data
    assert xr_ds_2.equals(version_1_data)
    
    # Current version should be the latest (version 1)
    current_data = ds["test_file.hdf5"].xarray
    assert xr_ds_2.equals(current_data)

def test_dataset_file_access_edge_cases():
    """Test edge cases and error conditions"""
    ds = dataset.create(name="test_dataset_file_access_edge_cases")
    
    # Test invalid file extension for xarray
    xr_ds = xarray.Dataset(coords={"x": [1, 2, 3]}, data_vars={"y": [4, 5, 6]})
    with pytest.raises(ValueError, match="is not supported for hdf5 files"):
        ds["test_file.txt"] = xr_ds
    
    # Test multiple dots in filename
    with pytest.raises(ValueError, match="There can only by one extension per file name"):
        ds["test.file.hdf5"] = xr_ds
    
    # Test accessing non-existent file
    with pytest.raises(KeyError):
        ds["non_existent_file.hdf5"]


def test_dataset_html_creation():
    """Test creating an html file using a temporary directory to avoid residual files"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        ds = dataset.create(name="test_dataset_html_creation")

        html_data = "<html><body><h1>Hello, World!</h1></body></html>"

        # Create the HTML file inside a pytest-provided temporary directory
        file_path = Path(tmp_dir) / "test_file.html"
        file_path.write_text(html_data)

        # Add the file to the dataset via its Path object
        ds["test_file.html"] = file_path

        stored_path = ds["test_file.html"].path
        
        if isinstance(stored_path, str):
            stored_path = Path(stored_path)
        if not isinstance(stored_path, Path):
            raise ValueError("wrong type of path")
        
        assert stored_path.exists()
        assert stored_path.read_text() == html_data

