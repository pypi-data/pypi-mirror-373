import pytest


### Fixtures ###
@pytest.fixture(scope="session")
def create_workspace_fixture(client):
    workspaceId = client.create_workspace(name=f"anatools-workspace-{client.timestamp}", organizationId=client.organization)
    return workspaceId


### Tests ###
def test_set_workspace(client):
    workspaceId = client.workspace
    status = client.set_workspace(workspaceId=workspaceId)
    assert status == True
    assert client.workspace == workspaceId

def test_get_workspaces(client, create_workspace_fixture):
    workspaces = client.get_workspaces()
    assert isinstance(workspaces, list)
    assert len(workspaces) > 0
    assert create_workspace_fixture in [w['workspaceId'] for w in workspaces]

@pytest.mark.dependency(depends=["test_edit_workspace"])
def test_delete_workspace(client, create_workspace_fixture):
    workspaceId = create_workspace_fixture
    status = client.delete_workspace(workspaceId=workspaceId)
    assert status == True

def test_edit_workspace(client, create_workspace_fixture):
    workspaceId = create_workspace_fixture
    status = client.edit_workspace(workspaceId=workspaceId, name=f"anatools-workspace-edit-{client.timestamp}", channelIds=[client.channel])
    assert status == True