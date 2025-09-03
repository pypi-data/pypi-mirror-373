import pytest


def test_get_api_keys(client):
    keys = client.get_api_keys()
    assert isinstance(keys, list)


# # TODO: support api key tests
# def test_get_api_key_data(client, test_create_api_key):
#     name, scope = test_create_api_key
#     data = client.get_api_key_data(name=name)
#     assert isinstance(data, dict)
#     assert data['name'] == name
#     assert data['scope'] == scope


# @pytest.fixture(scope="session")
# def test_create_api_key(client):
#     name = "anatools-api-key"
#     scope = "user"
#     key = client.create_api_key(name="anatools-api-key", scope="user")
#     assert isinstance(key, str) 
#     return name, scope


# @pytest.mark.dependency(depends=["test_get_api_key_data"])
# def test_delete_api_key(client, test_create_api_key):
#     name, scope = test_create_api_key
#     status = client.delete_api_key(name=name)
#     assert status == True
