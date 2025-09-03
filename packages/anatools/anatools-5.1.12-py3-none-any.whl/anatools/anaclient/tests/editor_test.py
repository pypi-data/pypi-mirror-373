import os
import pytest
import time

# TODO: support remote development and SSH key tests

# ### Fixtures ###
# @pytest.fixture(scope="session")
# def create_remote_development_fixture(client):
#     editorId = client.create_remote_development(channelId=client.channel)
#     while client.get_remote_development(editorId=editorId)['status'] not in ['running', 'failed', 'cancelled', 'timeout']: time.sleep(10)
#     return editorId

# @pytest.fixture(scope="session")
# def register_ssh_key_fixture(filename=None):
#     filename = "test-ssh-key.pub"
#     with open(filename, "w") as f: f.write("test")
#     client.register_ssh_key(filename=filename)
#     os.remove(filename)
#     return filename


# ### Tests ###
# def test_list_remote_development(client):
#     editors = client.list_remote_development()
#     assert isinstance(editors, list)

# def test_create_remote_development(client, create_remote_development_fixture):
#     editorId = create_remote_development_fixture
#     assert client.get_remote_development(editorId=editorId)['status'] == ['running']

# @pytest.mark.dependency(depends=["stop_remote_development"])
# def test_delete_remote_development(client, create_remote_development_fixture):
#     editorId = create_remote_development_fixture
#     status = client.delete_remote_development(editorId=editorId)
#     assert status == True

# def test_stop_remote_development(client, create_remote_development_fixture):
#     editorId = create_remote_development_fixture
#     status = client.stop_remote_development(editorId=editorId)
#     assert status == True

# def test_start_remote_development(client, create_remote_development_fixture):
#     editorId = create_remote_development_fixture
#     status = client.start_remote_development(editorId=editorId)
#     assert status == True

# def test_prepare_ssh_remote_development(client, create_remote_development_fixture):
#     editorId = create_remote_development_fixture
#     status = client.prepare_ssh_remote_development(editorId=editorId)
#     assert status == True   
   
# def test_get_ssh_keys(client, register_ssh_key_fixture):
#     sshkeys = client.get_ssh_keys()
#     assert isinstance(sshkeys, list)
#     assert len(sshkeys) > 0

# @pytest.mark.dependency(depends=["test_get_ssh_keys"])
# def test_deregister_ssh_key(client, register_ssh_key_fixture):
#     sshkey = register_ssh_key_fixture
#     status = client.deregister_ssh_key(sshkey=sshkey)
#     assert status == True
   