import time
import os
import pytest
from .graphs_test import upload_graph_fixture, get_default_graph_fixture

### Fixtures ###
@pytest.fixture(name="create_dataset_fixture", scope="session")
def create_dataset_fixture(client, upload_graph_fixture):
    graphId = upload_graph_fixture
    datasetId = client.create_dataset(name=f"anatools-dataset-create", graphId=graphId, description="anatools test dataset", runs=100, priority=1, seed=1, tags=["test"], workspaceId=client.workspace)
    while client.get_datasets(datasetId=datasetId)[0]['status'] not in ['success', 'failed', 'cancelled', 'timeout']: time.sleep(10)
    return datasetId

@pytest.fixture(name="download_dataset_fixture", scope="session")
def download_dataset_fixture(client, create_dataset_fixture):
    datasetId = create_dataset_fixture
    datasetfile = client.download_dataset(datasetId=datasetId, workspaceId=client.workspace)
    return datasetfile

@pytest.fixture(name="get_dataset_files_fixture", scope="session")
def get_dataset_files_fixture(client, create_dataset_fixture):
    datasetId = create_dataset_fixture
    files = client.get_dataset_files(datasetId=datasetId, workspaceId=client.workspace)
    return files

@pytest.fixture(name="upload_dataset_fixture", scope="session")
def upload_dataset_fixture(client, download_dataset_fixture):
    datasetfile = download_dataset_fixture
    datasetId = client.upload_dataset(name=f"anatools-dataset-upload", file=datasetfile, workspaceId=client.workspace)
    return datasetId
                
@pytest.fixture(name="create_mixed_dataset_fixture", scope="session")
def create_mixed_dataset_fixture(client, create_dataset_fixture, upload_dataset_fixture):
    datasetId1 = create_dataset_fixture
    datasetId2 = upload_dataset_fixture
    mixedDatasetId = client.create_mixed_dataset(name=f"anatools-dataset-mixed", parameters={datasetId1: {"samples": 100}, datasetId2: {"samples": 100}}, description="anatools test mixed dataset", seed=1, tags=["test"], workspaceId=client.workspace)
    return mixedDatasetId

@pytest.fixture(name="get_dataset_run_fixture", scope="session")
def get_dataset_run_fixture(client, create_dataset_fixture):
    datasetId = create_dataset_fixture
    runs = client.get_dataset_runs(datasetId=datasetId, workspaceId=client.workspace)
    return runs[-1]['runId']


### Tests ###
@pytest.mark.smoke
def test_get_datasets(client):
    datasets = client.get_datasets(workspaceId=client.workspace)
    assert isinstance(datasets, list)

@pytest.mark.smoke
def test_create_dataset(client, create_dataset_fixture):
    datasetId = create_dataset_fixture
    assert isinstance(datasetId, str)
    datasets = client.get_datasets(datasetId=datasetId)
    assert len(datasets) == 1
    assert datasets[0]['status'] == 'success'

def test_download_dataset(download_dataset_fixture):
    datasetfile = download_dataset_fixture
    assert os.path.isfile(datasetfile)

def test_edit_dataset(client, create_dataset_fixture):
    datasetId = create_dataset_fixture
    status = client.edit_dataset(datasetId=datasetId, name="anatools-dataset-edit", workspaceId=client.workspace)
    assert status == True

@pytest.mark.smoke
@pytest.mark.dependency(depends=["test_get_datasets"])
@pytest.mark.dependency(depends=["test_edit_dataset"], optional=True)
def test_delete_dataset(client, create_dataset_fixture):
    datasetId = create_dataset_fixture
    status = client.delete_dataset(datasetId=datasetId, workspaceId=client.workspace)
    assert status == True

def test_cancel_dataset(client, upload_graph_fixture):
    graphId = upload_graph_fixture
    datasetId = client.create_dataset(name="anatools-dataset-cancel", graphId=graphId, description="anatools test cancel dataset", runs=1, priority=1, seed=1, tags=["test"], workspaceId=client.workspace)
    assert isinstance(datasetId, str)
    while client.get_datasets(datasetId=datasetId)[0]['status'] not in ['running', 'starting']: time.sleep(10)
    status = client.cancel_dataset(datasetId=datasetId, workspaceId=client.workspace)
    assert status == True
    while client.get_datasets(datasetId=datasetId)[0]['status'] not in ['cancelled']: time.sleep(10)
    assert client.get_datasets(datasetId=datasetId)[0]['status'] == 'cancelled'

def test_upload_dataset(upload_dataset_fixture):
    datasetId = upload_dataset_fixture
    assert isinstance(datasetId, str)

def test_create_mixed_dataset(create_mixed_dataset_fixture):
    datasetId = create_mixed_dataset_fixture
    assert isinstance(datasetId, str)

def test_get_dataset_files(get_dataset_files_fixture):
    files = get_dataset_files_fixture
    assert isinstance(files, list)
    assert len(files) > 0

def test_get_dataset_runs(get_dataset_run_fixture):
    runId = get_dataset_run_fixture
    assert isinstance(runId, str)

def test_get_dataset_log(client, create_dataset_fixture, get_dataset_run_fixture):
    datasetId = create_dataset_fixture
    runId = get_dataset_run_fixture
    log = client.get_dataset_log(datasetId=datasetId, runId=runId, workspaceId=client.workspace)
    assert isinstance(log, dict)
