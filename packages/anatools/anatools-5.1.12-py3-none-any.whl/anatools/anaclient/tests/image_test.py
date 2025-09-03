import os
from .datasets_test import get_dataset_files_fixture

### Tests ###
def test_get_image_annotation(client, get_dataset_files_fixture):
    files = get_dataset_files_fixture
    images = [file for file in files if 'images' in file['path']]
    annotation = client.get_image_annotation(datasetId=files[0]['datasetId'], filename=images[0], workspaceId=client.workspace)
    assert isinstance(annotation, dict)
    assert 'filename' in annotation

def test_get_image_mask(client, get_dataset_files_fixture):
    files = get_dataset_files_fixture
    images = [file for file in files if 'images' in file['path']]
    mask = client.get_image_mask(datasetId=files[0]['datasetId'], filename=images[0], workspaceId=client.workspace)
    assert isinstance(mask, str)
    assert os.path.isfile(mask)
    os.remove(mask)

def test_get_image_metadata(client, get_dataset_files_fixture):
    files = get_dataset_files_fixture
    images = [file for file in files if 'images' in file['path']]
    metadata = client.get_image_metadata(datasetId=files[0]['datasetId'], filename=images[0], workspaceId=client.workspace)
    assert isinstance(metadata, dict)
    assert 'filename' in metadata
