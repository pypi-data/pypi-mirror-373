import pytest


### Fixtures ###
@pytest.fixture(scope="session")
def create_preview_fixture(client, create_graph_fixture):
    graphId = create_graph_fixture
    previewId = client.create_preview(graphId=graphId, workspaceId=client.workspace)
    while client.get_preview(previewId=previewId, workspaceId=client.workspace)[0]['status'] not in ['success', 'failed', 'cancelled', 'timeout']: time.sleep(10)
    return previewId


### Tests ###
def test_create_preview(client, create_preview_fixture):
    previewId = create_preview_fixture
    assert isinstance(previewId, str)
    preview = client.get_preview(previewId=previewId, workspaceId=client.workspace)
    assert isinstance(preview, dict)
    assert preview['status'] == 'success'
    