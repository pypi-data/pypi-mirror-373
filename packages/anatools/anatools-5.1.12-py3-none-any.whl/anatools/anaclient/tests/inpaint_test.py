import pytest
from .volumes_test import create_volume_fixture

# TODO: support inpaint tests

# ### Fixtures ###
# @pytest.fixture(scope="session")
# def create_inpaint_fixture(client, create_volume_fixture):
#     volumeId = create_volume_fixture
#     client.upload_volume_data(volumeId=volumeId, files=["assets/inpaint.png", "assets/coco.json"])
#     inpaintId = client.create_inpaint(volumeId=volumeId, location="./", files=["inpaint.png"], inputType="COCO", outputType="PNG")
#     while client.get_inpaints(inpaintId=inpaintId)[0]['status'] not in ['success', 'failed', 'cancelled', 'timeout']: time.sleep(10)
#     return inpaintId


# ### Tests ###
# def test_get_inpaints(client, create_inpaint_fixture):
#     volumeId = create_inpaint_fixture
#     inpaints = client.get_inpaints(volumeId=volumeId)
#     assert isinstance(inpaints, list)

# def test_get_inpaint_logs(client, create_inpaint_fixture):
#     inpaintId = create_inpaint_fixture
#     logs = client.get_inpaint_logs(inpaintId=inpaintId)
#     assert isinstance(logs, dict)

# @pytest.mark.dependency(depends=["test_get_inpaint_logs"])
# def test_delete_inpaint(client, create_inpaint_fixture):
#     inpaintId = create_inpaint_fixture
#     status = client.delete_inpaint(inpaintId=inpaintId)
#     assert status == True
    
