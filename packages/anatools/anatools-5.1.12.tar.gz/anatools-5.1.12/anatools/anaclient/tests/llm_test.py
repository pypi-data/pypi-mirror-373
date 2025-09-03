import pytest

# TODO: support llm tests

# ### Fixtures ###
# @pytest.fixture(scope="session")
# def create_llm_prompt_fixture(client):
#     prompt = "Create a node that will place a 1x1x1 sphere in the center of the scene."
#     promptId = client.create_llm_prompt(prompt=prompt)
#     while client.get_llm_prompts(promptId=promptId)[0]['status'] not in ['success', 'failed', 'cancelled', 'timeout']: time.sleep(10)
#     return promptId


# ### Tests ###
# def test_create_llm_prompt(client, create_llm_prompt_fixture):
#     promptId = create_llm_prompt_fixture
#     assert isinstance(promptId, str)
#     response = client.get_llm_prompts(promptId=promptId)
#     assert isinstance(response, dict)
#     assert 'response' in response

# @pytest.mark.depends(['test_create_llm_prompt'])
# def delete_llm_prompt(client, create_llm_prompt_fixture):
#     promptId = create_llm_prompt_fixture
#     status = client.delete_llm_prompt(promptId=promptId)
#     assert status == True

# def get_llm_base_channels(client):
#     channels = client.get_llm_base_channels()
#     assert isinstance(channels, list)
#     assert len(channels) > 0

# def get_llm_channel_node_types(client):
#     nodeTypes = client.get_llm_channel_node_types()
#     assert isinstance(nodeTypes, list)
#     assert len(nodeTypes) > 0
    