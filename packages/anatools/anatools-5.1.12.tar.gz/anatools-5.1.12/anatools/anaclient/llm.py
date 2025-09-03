"""
Large Language Model Functions
"""

def get_llm_response(self, promptId, fields=None):
    """Retrieves the response to an LLM prompt.
    
    Parameters
    ----------
    promptId : str
        The ID of a prompt.
    fields : list[str], optional
        The fields to retrieve from the response.
    
    Returns
    -------
    dict
        Prompt response info
    """
    if self.check_logout(): return
    llm_response = self.ana_api.getLLMResponse(promptId=promptId, fields=fields)
    return llm_response


def create_llm_prompt(self, prompt, baseChannel, nodeType, nodeName):
    """ Creates an LLM prompt.
    
    Parameters
    ----------
    prompt : str
        The prompt to create

    baseChannel: str
        The base channel to use for examples

    nodeType: str
        The type of node to create

    nodeName: str
        The name of the node to create

    Returns
    -------
    str
        Prompt ID
    """
    if self.check_logout(): return
    prompt_id = self.ana_api.createLLMPrompt(prompt=prompt, baseChannel=baseChannel, nodeType=nodeType, nodeName=nodeName)
    return prompt_id


def delete_llm_prompt(self, promptId):
    """Deletes an LLM prompt.
    
    Parameters
    ----------
    promptId : str
        The ID of a prompt.
    
    Returns
    -------
    bool
        Success code
    """
    if self.check_logout(): return
    llm_response = self.ana_api.deleteLLMPrompt(promptId=promptId)
    return llm_response


def get_llm_base_channels(self):
    """Gets a list of the base channels

    Returns
    -------
    list[str]
        A list of the base channels
    """
    if self.check_logout(): return
    llm_response = self.ana_api.getLLMBaseChannels()
    return llm_response


def get_llm_channel_node_types(self):
    """Gets a dictionary of base channels. For each channel there is a list of valid node types.

    Returns
    -------
    dict
        A dictionary of base channels and their valid node types
    """
    if self.check_logout(): return
    llm_response = self.ana_api.getLLMChannelNodeTypes()
    return llm_response