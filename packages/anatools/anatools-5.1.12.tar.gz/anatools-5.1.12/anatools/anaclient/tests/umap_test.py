import pytest
import time
from .datasets_test import create_dataset_fixture, upload_dataset_fixture


### Fixtures ###
@pytest.fixture(scope="session")
def create_umap_fixture(client, create_dataset_fixture, upload_dataset_fixture):
    datasetId1 = create_dataset_fixture
    datasetId2 = upload_dataset_fixture
    umapId = client.create_umap(name="anatools-umap", datasetIds=[datasetId1, datasetId2], samples=[10, 10], workspaceId=client.workspace)
    while client.get_umaps(umapId=umapId, workspaceId=client.workspace)[0]['status'] not in ['success', 'failed', 'cancelled', 'timeout']: time.sleep(10)
    return umapId


### Tests ###
def get_umaps(client):
    umaps = client.get_umaps(workspaceId=client.workspace)
    assert isinstance(umaps, list)

def test_create_umap(client, create_umap_fixture):
    umapId = create_umap_fixture
    assert isinstance(umapId, str)
    umaps = client.get_umaps(umapId=umapId, workspaceId=client.workspace)
    assert isinstance(umaps, list)
    assert len(umaps) == 1
    assert umaps[0]['status'] == 'success'
    
def test_edit_umap(client, create_umap_fixture):
    umapId = create_umap_fixture
    status = client.edit_umap(umapId=umapId, name="anatools-umap-edit", workspaceId=client.workspace)
    assert status == True
    umaps = client.get_umaps(umapId=umapId, workspaceId=client.workspace)
    assert isinstance(umaps, list)
    assert len(umaps) == 1
    assert umaps[0]['name'] == "anatools-umap-edit"

@pytest.mark.dependency(depends=["test_create_umap", "test_edit_umap"])
def test_delete_umap(client, create_umap_fixture):
    umapId = create_umap_fixture
    status = client.delete_umap(umapId=umapId, workspaceId=client.workspace)
    assert status == True
