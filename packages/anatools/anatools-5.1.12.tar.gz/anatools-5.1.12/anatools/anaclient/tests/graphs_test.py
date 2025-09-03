import pytest
import yaml

### Fixtures ###
@pytest.fixture(name="get_default_graph_fixture", scope="session")
def get_default_graph_fixture(client):
    graphfile = client.get_default_graph(channelId=client.channel, filepath="default.yaml")
    with open(graphfile, 'r') as yamlfile:
        graph = yaml.safe_load(yamlfile)
    return graph

@pytest.fixture(name="upload_graph_fixture", scope="session")
def upload_graph_fixture(client, get_default_graph_fixture):
    graph = get_default_graph_fixture
    graphId = client.upload_graph(name="anatools-graph", graph=graph, channelId=client.channel, workspaceId=client.workspace)
    return graphId


### Tests ###
@pytest.mark.smoke
def test_get_graphs(client):
    graphs = client.get_graphs(workspaceId=client.workspace)
    assert isinstance(graphs, list)

@pytest.mark.smoke
def test_get_default_graph(get_default_graph_fixture):
    graph = get_default_graph_fixture
    assert isinstance(graph, dict)
    assert 'nodes' in graph.keys()

@pytest.mark.smoke
def test_upload_graph(upload_graph_fixture):
    graphId = upload_graph_fixture
    assert isinstance(graphId, str)

def test_edit_graph(client, upload_graph_fixture):
    graphId = upload_graph_fixture
    status = client.edit_graph(graphId=graphId, name="anatools-graph-edit", description="anatools test graph edit")
    assert status == True

@pytest.mark.dependency(depends=["test_edit_graph", "test_download_graph"])
def test_delete_graph(client, upload_graph_fixture):
    graphId = upload_graph_fixture
    status = client.delete_graph(graphId=graphId, workspaceId=client.workspace)
    assert status == True

def test_download_graph(client, upload_graph_fixture):
    graphId = upload_graph_fixture
    graph = client.download_graph(graphId=graphId, workspaceId=client.workspace)
    assert isinstance(graph, dict)
    assert 'nodes' in graph.keys()

# def test_set_default_graph(client, create_channel_fixture, upload_graph_fixture):
#     channelId = create_channel_fixture
#     graphId = upload_graph_fixture
#     status = client.set_default_graph(channelId=channelId, graphId=graphId)
#     assert status == True