import pytest
from .datasets_test import create_dataset_fixture

### Fixtures ###
@pytest.fixture(scope="session")
def create_analytics_fixture(client, create_dataset_fixture):
    datasetId = create_dataset_fixture
    analyticsId = client.create_analytics(datasetId=datasetId, type='Properties', workspaceId=client.workspace)
    while client.get_analytics(analyticsId=analyticsId, workspaceId=client.workspace)[0]['status'] not in ['success', 'failed', 'cancelled', 'timeout']: time.sleep(10)
    return analyticsId


### Tests ###
@pytest.mark.smoke
def test_get_analytics_types(client):
    analytics_types = client.get_analytics_types()
    assert isinstance(analytics_types, list)
    assert len(analytics_types) > 0

@pytest.mark.dependency(depends=["test_create_analytics"])
def test_get_analytics(client):
    analytics = client.get_analytics(workspaceId=client.workspace)
    assert isinstance(analytics, list)
    assert len(analytics) > 0

def test_create_analytics(client, create_analytics_fixture):
    analyticsId = create_analytics_fixture
    analytics = client.get_analytics(analyticsId=analyticsId, workspaceId=client.workspace)
    assert len(analytics) == 1
    assert analytics[0]['status'] == 'success'

def test_download_analytics(client, create_analytics_fixture):
    analyticsId = create_analytics_fixture
    analytics = client.download_analytics(analyticsId=analyticsId, workspaceId=client.workspace)
    assert isinstance(analytics, dict)

@pytest.mark.dependency(depends=["test_get_analytics","test_download_analytics"])
def test_delete_analytics(client, create_analytics_fixture):
    analyticsId = create_analytics_fixture
    status = client.delete_analytics(analyticsId=analyticsId, workspaceId=client.workspace)
    assert status == True
