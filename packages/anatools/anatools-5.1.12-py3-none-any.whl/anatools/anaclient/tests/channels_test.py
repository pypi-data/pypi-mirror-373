import pytest


@pytest.mark.smoke
def test_get_channels(client):
    channels = client.get_channels(workspaceId=client.workspace)
    assert isinstance(channels, list)
    assert len(channels) > 0

@pytest.mark.smoke
def test_get_channel_nodes(client):
    nodes = client.get_channel_nodes(channelId=client.channel)
    assert isinstance(nodes, list)
    assert len(nodes) > 0


# # TODO: support channel tests (cleanup/prevent archive)
# @pytest.fixture(scope="session")
# def test_create_channel(client):
#     channelId = client.create_channel(name=f"anatools-channel-create-{client.timestamp}", organizationId=client.organization)
#     assert isinstance(channelId, str)
#     return channelId


# @pytest.mark.dependency(depends=["test_create_channel"])
# def test_edit_channel(client, test_create_channel):
#     channelId = test_create_channel
#     status = client.edit_channel(channelId=channelId, name=f"anatools-channel-edit-{client.timestamp}")
#     assert status == True


# @pytest.mark.dependency(depends=["test_edit_channel", "test_get_deployment_status"])
# def test_delete_channel(client, test_create_channel):
#     channelId = test_create_channel
#     status = client.delete_channel(channelId=channelId)
#     assert status == True


# @pytest.fixture(scope="session")
# def test_deploy_channel(client, test_create_channel):
#     channelId = test_create_channel
#     deploymentId = client.deploy_channel(channelId=channelId)
#     assert isinstance(deploymentId, str)
#     return deploymentId


# def test_get_deployment_status(client, test_deploy_channel):
#     deploymentId = test_deploy_channel
#     status = client.get_deployment_status(deploymentId=deploymentId)
#     assert isinstance(status, dict)


@pytest.mark.smoke
def get_channel_documentation(client):
    docs =  client.ana_api.getChannelDocumentation(channelId=client.channel)
    assert isinstance(docs, str)
    

# def upload_channel_documentation(client, test_create_channel):
#     with open("README.md", "w") as f: f.write("# README")
#     channelId = test_create_channel
#     status = client.upload_channel_documentation(channelId=channelId, mdfile="README.md")
#     assert status == True


@pytest.mark.smoke
def get_node_documentation(client):
    docs = client.get_node_documentation(channelId=client.channel, node='Render')
    assert isinstance(docs, dict)
