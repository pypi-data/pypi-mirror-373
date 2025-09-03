import os
import pytest

### Fixtures ###
@pytest.fixture(scope="session")
def create_volume_fixture(client):
    volumeId = client.create_volume(name=f"anatools-volume-{client.timestamp}", organizationId=client.organization)
    client.edit_workspace(workspaceId=client.workspace, volumeIds=[volumeId])
    return volumeId

@pytest.fixture(scope="session")
def upload_volume_data_fixture(client, create_volume_fixture):
    volumeId = create_volume_fixture
    file = "test.txt"
    with open(file, "w") as f: f.write("test")
    client.upload_volume_data(volumeId=volumeId, files=[file])
    return file


### Tests ###
def test_get_volumes(client):
    volumes = client.get_volumes()
    assert isinstance(volumes, list)

def test_create_volume(client, create_volume_fixture):
    volumes = client.get_volumes(workspaceId=client.workspace)
    assert isinstance(volumes, list)
    assert len(volumes) == 1
    assert volumes[0]['volumeId'] == create_volume_fixture

@pytest.mark.dependency(depends=["test_delete_volume_data", "test_delete_inpaint"])
def test_delete_volume(client, create_volume_fixture):
    volumeId = create_volume_fixture
    status = client.delete_volume(volumeId=volumeId)
    assert status == True

def test_edit_volume(client, create_volume_fixture):
    volumeId = create_volume_fixture
    status = client.edit_volume(volumeId=volumeId, name=f"anatools-volume-edited-{client.timestamp}")
    assert status == True

def test_upload_volume_data(client, create_volume_fixture, upload_volume_data_fixture):
    volumeId = create_volume_fixture
    file = upload_volume_data_fixture
    volumedata = client.get_volume_data(volumeId=volumeId, files=[file])
    assert isinstance(volumedata, list)
    assert len(volumedata) == 1
    assert volumedata[0]['filename'] == file

def test_download_volume_data(client, create_volume_fixture, upload_volume_data_fixture):
    volumeId = create_volume_fixture
    file = upload_volume_data_fixture
    filepath = client.download_volume_data(volumeId=volumeId, files=[file])
    assert os.path.exists(filepath)  

@pytest.mark.dependency(depends=["test_upload_volume_data","test_download_volume_data"])
def test_delete_volume_data(client, create_volume_fixture, upload_volume_data_fixture):
    volumeId = create_volume_fixture
    file = upload_volume_data_fixture
    status = client.delete_volume_data(volumeId=volumeId, files=[file])
    assert status == True

def test_mount_volumes(client, create_volume_fixture):
    volumeId = create_volume_fixture
    credentials = client.mount_volumes(volumes=[volumeId])
    assert isinstance(credentials, dict)
