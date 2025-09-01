'''
check tag functionality:

- test 1: create a dataset, us the tag keyword to add initial tags --> reload ds --> check that the tags are added
- test 2: create a dataset, after the dataset has been created, add tags --> reload ds --> check that the tags are added
- test 3: create a dataset, after the dataset has been created, add tags, then append a tag to the tag list --> reload ds --> check that all tags are added
- test 4: create a dataset, after the dataset has been created, add tags, then delete a tag a the tag list --> reload ds --> check that all tags are added
- test 5: create a dataset, after the dataset has been created, add tags by assigning a list to tags, assign other list to tags --> reload ds --> check that all tags are added
'''
from qdrive.dataset.dataset import dataset


def test_dataset_tags_1():
    """Test 1: create a dataset with initial tags and verify they persist after reload"""
    ds = dataset.create(name="test_dataset_tags_1", tags=["tag1", "tag2"])
    assert ds.tags == ["tag1", "tag2"]
    ds_uuid = ds.uuid
    ds_reloaded = dataset(ds_uuid)
    assert ds_reloaded.tags == ["tag1", "tag2"]


def test_dataset_tags_2():
    """Test 2: create a dataset, add tags after creation, and verify they persist"""
    ds = dataset.create(name="test_dataset_tags_2")
    ds.tags = ["tag1", "tag2"]
    assert ds.tags == ["tag1", "tag2"]
    ds_uuid = ds.uuid
    ds_reloaded = dataset(ds_uuid)
    assert ds_reloaded.tags == ["tag1", "tag2"]


def test_dataset_tags_3():
    """Test 3: create a dataset, add tags, then append additional tags and verify all persist"""
    ds = dataset.create(name="test_dataset_tags_3")
    ds.tags = ["tag1", "tag2"]
    assert ds.tags == ["tag1", "tag2"]
    
    # Append a new tag to the existing list
    ds.tags.append("tag3")
    assert ds.tags == ["tag1", "tag2", "tag3"]
    
    ds_uuid = ds.uuid
    ds_reloaded = dataset(ds_uuid)
    assert ds_reloaded.tags == ["tag1", "tag2", "tag3"]


def test_dataset_tags_4():
    """Test 4: create a dataset, add tags, remove a tag, and verify changes persist"""
    ds = dataset.create(name="test_dataset_tags_4")
    ds.tags = ["tag1", "tag2", "tag3"]
    assert ds.tags == ["tag1", "tag2", "tag3"]
    
    # Remove a tag from the list
    ds.tags.remove("tag2")
    assert ds.tags == ["tag1", "tag3"]
    
    ds_uuid = ds.uuid
    ds_reloaded = dataset(ds_uuid)
    assert ds_reloaded.tags == ["tag1", "tag3"]


def test_dataset_tags_5():
    """Test 5: create a dataset, assign different tag lists, and verify the latest assignment persists"""
    ds = dataset.create(name="test_dataset_tags_5")
    
    # First assignment
    ds.tags = ["tag1", "tag2"]
    assert ds.tags == ["tag1", "tag2"]
    
    # Second assignment (overwrite previous tags)
    ds.tags = ["tag3", "tag4", "tag5"]
    assert ds.tags == ["tag3", "tag4", "tag5"]
    
    ds_uuid = ds.uuid
    ds_reloaded = dataset(ds_uuid)
    assert ds_reloaded.tags == ["tag3", "tag4", "tag5"]