import os
import pytest
from .datasets_test import create_dataset_fixture

### Fixtures ###
@pytest.fixture(scope="session")
def create_gan_dataset_fixture(client, upload_gan_model_fixture, create_dataset_fixture):
    modelId = upload_gan_model_fixture
    datasetId = create_dataset_fixture
    datasetId = client.create_gan_dataset(name=f"anatools-gan-dataset", modelId=modelId, datasetId=datasetId, workspaceId=client.workspace)
    while client.get_gan_datasets(datasetId=datasetId)[0]['status'] not in ['success', 'failed', 'cancelled', 'timeout']: time.sleep(10)
    return datasetId

@pytest.fixture(scope="session")
def upload_gan_model_fixture(client):
    modelfile = "model.pth"
    modelId = client.upload_gan_model(name=f"anatool-gan-upload-{client.timestamp}", description="anatools test upload gan model", modelfile=modelfile, flags=[])
    status = client.edit_workspace(modelIds=[modelId])
    assert isinstance(modelId, str)
    assert status == True
    return modelId


### Tests ###
def test_get_gan_models(client):
    models = client.get_gan_models()
    assert isinstance(models, list)

def test_get_gan_datasets(client):
    datasets = self.get_gan_datasets(workspaceId=client.workspace)
    assert isinstance(datasets, list)

def test_create_gan_dataset(client, create_gan_dataset_fixture):
    datasetId = create_gan_dataset_fixture
    assert isinstance(datasetId, str)
    datasets = client.get_gan_datasets(datasetId=datasetId, workspaceId=client.workspace)
    assert isinstance(datasets, list)
    assert len(datasets) == 1
    assert datasets[0]['status'] == 'success'

@pytest.mark.dependency(depends=["test_create_gan_dataset"])
def test_delete_gan_dataset(client, create_gan_dataset_fixture):
    datasetId = create_gan_dataset_fixture
    status = client.delete_gan_dataset(datasetId=datasetId, workspaceId=client.workspace)
    assert status == True

def test_upload_gan_model(client, upload_gan_model_fixture):
    modelId = upload_gan_model_fixture
    assert isinstance(modelId, str)
    models = client.get_gan_models(modelId=modelId)
    assert isinstance(models, list)
    assert len(models) == 1
    assert isinstance(models[0], dict)

@pytest.mark.dependency(depends=["test_edit_gan_model","test_download_gan_model"])
def delete_gan_model(client, create_gan_model_fixture):
    modelId = create_gan_model_fixture
    status = client.delete_gan_model(modelId=modelId)
    assert status == True

def test_edit_gan_model(client, create_gan_model_fixture):
    modelId = create_gan_model_fixture
    status = client.edit_gan_model(modelId=modelId, name=f"anatools-gan-edit-{client.timestamp}")
    assert status == True

def test_download_gan_model(client, create_gan_model_fixture):
    modelId = create_gan_model_fixture
    modelfile = client.download_gan_model(modelId=modelId)
    assert os.path.isfile(modelfile)
    os.remove(modelfile)
    