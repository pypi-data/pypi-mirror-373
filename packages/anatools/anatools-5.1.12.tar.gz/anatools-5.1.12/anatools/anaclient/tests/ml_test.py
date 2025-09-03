import os
import pytest
import time
from .datasets_test import create_dataset_fixture

# # TODO: support ml tests

# ### Fixtures ###
# @pytest.fixture(scope="session")
# def get_ml_architectures_fixture(client):
#     architectures = client.get_ml_architectures()
#     return architectures

# @pytest.fixture(scope="session")
# def create_ml_model_fixture(client, get_ml_architectures_fixture, create_dataset_fixture):
#     architectureId = get_ml_architectures_fixture[0]['architectureId']
#     datasetId = create_dataset_fixture
#     parameters = {}
#     modelId = client.create_ml_model(datasetId=datasetId, architectureId=architectureId, name='anatools-ml-model', parameters=parameters, workspaceId=client.workspace)
#     while client.get_ml_models(modelId=modelId, workspaceId=client.workspace)[0]['status'] not in ['success', 'failed', 'cancelled', 'timeout']: time.sleep(10)
#     return modelId

# @pytest.fixture(scope="session")
# def download_ml_model_fixture(client, create_ml_model_fixture):
#     modelId = create_ml_model_fixture
#     modelFile = client.download_ml_model(modelId=modelId, workspaceId=client.workspace)
#     return modelFile

# @pytest.fixture(scope="session")
# def create_ml_inference_fixture(client, create_ml_model_fixture, create_dataset_fixture):
#     modelId = create_ml_model_fixture
#     datasetId = create_dataset_fixture
#     inferenceId = client.create_ml_inference(modelId=modelId, datasetId=datasetId, workspaceId=client.workspace)
#     while client.get_ml_inferences(inferenceId=inferenceId, workspaceId=client.workspace)[0]['status'] not in ['success', 'failed', 'cancelled', 'timeout']: time.sleep(10)
#     return inferenceId

# ### Tests ###
# def test_get_ml_architectures(get_ml_architectures_fixture):
#     architectures = get_ml_architectures_fixture
#     assert isinstance(architectures, list)

# def test_get_ml_models(client):
#     models = client.get_ml_models(workspaceId=client.workspace)
#     assert isinstance(models, list)

# def test_create_ml_model(client, create_ml_model_fixture):
#     modelId = create_ml_model_fixture
#     assert isinstance(modelId, str)
#     models = client.get_ml_models(modelId=modelId, workspaceId=client.workspace)
#     assert len(models) == 1
#     assert models[0]['status'] == 'success'

# @pytest.mark.depends(['test_create_ml_model', 'test_edit_ml_model', 'test_download_ml_model', 'test_delete_ml_inference'])
# def test_delete_ml_model(client, create_ml_model_fixture):
#     modelId = create_ml_model_fixture
#     status = client.delete_ml_model(modelId=modelId, workspaceId=client.workspace)
#     assert status == True

# def test_edit_ml_model(client, create_ml_model_fixture):
#     modelId = create_ml_model_fixture
#     status = client.edit_ml_model(modelId=modelId, name='anatools-ml-model-edit', workspaceId=client.workspace)
#     assert status == True

# def test_download_ml_model(download_ml_model_fixture):
#     modelFile = download_ml_model_fixture
#     assert os.path.isfile(modelFile)

# def test_upload_ml_model(client, download_ml_model_fixture):
#     modelFile = download_ml_model_fixture
#     modelId = client.upload_ml_model(name=f"anatools-ml-model-upload", description="anatools test upload ml model", modelFile=modelFile, workspaceId=client.workspace)
#     assert isinstance(modelId, str)
#     while client.get_ml_models(modelId=modelId, workspaceId=client.workspace)[0]['status'] not in ['success', 'failed', 'cancelled', 'timeout']: time.sleep(10)
#     models = client.get_ml_models(modelId=modelId, workspaceId=client.workspace)
#     assert len(models) == 1
#     assert models[0]['status'] == 'success'

# def test_get_ml_inferences(client):
#     inferences = client.get_ml_inferences(workspaceId=client.workspace)
#     assert isinstance(inferences, list)

# def test_get_ml_inference_metrics(client, test_create_ml_inference):
#     inferenceId = test_create_ml_inference
#     metrics = client.get_ml_inference_metrics(inferenceId=inferenceId, workspaceId=client.workspace)
#     assert isinstance(metrics, list)

# def test_create_ml_inference(client, create_ml_inference_fixture):
#     inferenceId = create_ml_inference_fixture
#     assert isinstance(inferenceId, str)
#     inferences = client.get_ml_inferences(inferenceId=inferenceId, workspaceId=client.workspace)
#     assert len(inferences) == 1
#     assert inferences[0]['status'] == 'success'    

# @pytest.mark.dependency(depends=["test_create_ml_inference", "test_download_ml_inference"])
# def test_delete_ml_inference(client, create_ml_inference_fixture):
#     inferenceId = create_ml_inference_fixture
#     status = client.delete_ml_inference(inferenceId=inferenceId, workspaceId=client.workspace)
#     assert status == True

# def test_download_ml_inference(client, create_ml_inference_fixture):
#     inferenceId = create_ml_inference_fixture
#     inferenceFile = client.download_ml_inference(inferenceId=inferenceId, workspaceId=client.workspace)
#     assert os.path.isfile(inferenceFile)
#     os.remove(inferenceFile)
    