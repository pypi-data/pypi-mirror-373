import os
import pytest
import time
from .datasets_test import create_dataset_fixture

### Fixtures ###
@pytest.fixture(scope="session")
def create_annotation_fixture(client, create_dataset_fixture):
    datasetId = create_dataset_fixture
    annotationId = client.create_annotation(datasetId=datasetId, format='COCO', workspaceId=client.workspace)
    while client.get_annotations(annotationId=annotationId, workspaceId=client.workspace)[0]['status'] not in ['success', 'failed', 'cancelled', 'timeout']: time.sleep(10)
    return annotationId

@pytest.fixture(scope="session")
def create_annotation_map_fixture(client):
    mapfile = "mapfile.json"
    mapdata = """
classes:
  1: [none, Crane Truck]
  2: [none, Tank]

properties: 
  obj['type'] == 'Crane_Truck_1': 1
  obj['type'] == 'M2A3_Bradley': 2
"""
    with open(mapfile, "w") as f: f.write(mapdata)   
    mapId = client.create_annotation_map(name=f"anatools-map-{client.timestamp}", description="test", mapfile=mapfile, organizationId=client.organization)
    client.edit_workspace(workspaceId=client.workspace, mapIds=[mapId])
    os.remove(mapfile)
    return mapId


### Tests ###
@pytest.mark.smoke
def test_get_annotation_formats(client):
    annotation_formats = client.get_annotation_formats()
    assert isinstance(annotation_formats, list)
    assert len(annotation_formats) > 0

@pytest.mark.smoke
def test_get_annotation_maps(client):
    annotation_maps = client.get_annotation_maps(workspaceId=client.workspace)
    assert isinstance(annotation_maps, list)

@pytest.mark.dependency(depends=["test_create_annotation"])
def test_get_annotations(client):
    annotations = client.get_annotations(workspaceId=client.workspace)
    assert isinstance(annotations, list)
    assert len(annotations) > 0

@pytest.fixture(scope="session")
def test_create_annotation(client, create_annotation_fixture):
    annotationId = create_annotation_fixture
    assert isinstance(annotationId, str)
    annotation = client.get_annotations(annotationId=annotationId, workspaceId=client.workspace)
    assert len(annotation) == 1
    assert annotation[0]['status'] == 'success'

def test_download_annotation(client, create_annotation_fixture):
    annotationId = create_annotation_fixture
    annotation_file = client.download_annotation(annotationId=annotationId, workspaceId=client.workspace)
    assert isinstance(annotation_file, str)
    assert os.path.isfile(annotation_file)
    os.remove(annotation_file)

@pytest.mark.dependency(depends=["test_get_annotations","test_download_annotation"])
def test_delete_annotation(client, create_annotation_fixture):
    annotationId = create_annotation_fixture
    status = client.delete_annotation(annotationId=annotationId, workspaceId=client.workspace)
    assert status == True

def test_create_annotation_map(client, create_annotation_map_fixture):
    mapId = create_annotation_map_fixture
    assert isinstance(mapId, str)
    maps = client.get_annotation_maps(mapId=mapId, workspaceId=client.workspace)
    assert len(maps) == 1
    assert isinstance(maps[0], dict)

def test_edit_annotation_map(client, create_annotation_map_fixture):
    mapId = create_annotation_map_fixture
    status = client.edit_annotation_map(mapId=mapId, name=f"anatools-map-edit-{client.timestamp}", description="test edit")
    assert status == True

def test_download_annotation_map(client, create_annotation_map_fixture):
    mapId = create_annotation_map_fixture
    mapfile = client.download_annotation_map(mapId=mapId, workspaceId=client.workspace)
    assert os.path.isfile(mapfile)
    os.remove(mapfile)

@pytest.mark.dependency(depends=["test_delete_annotation"])
def test_delete_annotation_map(client, create_annotation_map_fixture):
    mapId = create_annotation_map_fixture
    status = client.delete_annotation_map(mapId=mapId, workspaceId=client.workspace)
    assert status == True