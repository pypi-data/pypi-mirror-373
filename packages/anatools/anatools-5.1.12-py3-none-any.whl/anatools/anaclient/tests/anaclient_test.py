import anatools
import pytest
import os


def test_client():
    assert os.environ.get("RENDEREDAI_API_KEY") is not None    
    client = anatools.client(interactive=False)
    assert client is not None
    assert client.organization is not None
    assert client.workspace is not None

def test_client_invalid_env():
    with pytest.raises(Exception) as excinfo:
        anatools.client(environment='invalid', interactive=False)
    assert 'Invalid environment argument.' in str(excinfo.value)

def test_client_invalid_apikey():
    with pytest.raises(Exception) as excinfo:
        anatools.client(APIKey='invalid', interactive=False)
    assert 'There was an issue retrieving the API Key context.' in str(excinfo.value)
