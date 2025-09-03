"""
LLM API calls.
"""

def getLLMResponse(self, promptId, fields=None):
    if fields is None: fields = self.getTypeFields("LLMResponse")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getLLMResponse",
            "variables": {
                "promptId": promptId
            },
            "query": f"""query 
                getLLMResponse($promptId: String!) {{
                    getLLMResponse(promptId: $promptId) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getLLMResponse")


def createLLMPrompt(self, prompt, baseChannel, nodeType, nodeName):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createLLMPrompt",
            "variables": {
                "prompt": prompt,
                "baseChannel": baseChannel,
                "nodeType": nodeType,
                "nodeName": nodeName
            },
            "query": """mutation 
                createLLMPrompt($prompt: String!, $baseChannel: String!, $nodeType: String!, $nodeName: String!) {
                    createLLMPrompt(prompt: $prompt, baseChannel: $baseChannel, nodeType: $nodeType, nodeName: $nodeName)
                }"""})
    return self.errorhandler(response, "createLLMPrompt")


def deleteLLMPrompt(self, promptId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createLLMPrompt",
            "variables": {
                "promptId": promptId
            },
            "query": """mutation 
                deleteLLMPrompt($promptId: String!) {
                    deleteLLMPrompt(promptId: $promptId)
                }"""})
    return self.errorhandler(response, "deleteLLMPrompt")


def getLLMBaseChannels(self):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getLLMBaseChannels",
            "variables": {},
            "query": """query 
                getLLMBaseChannels {
                    getLLMBaseChannels
                }"""})
    return self.errorhandler(response, "getLLMBaseChannels")


def getLLMChannelNodeTypes(self):
    fields = self.getTypeFields("LLMChannelNodeTypes")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getLLMChannelNodeTypes",
            "variables": {},
            "query": f"""query 
                getLLMChannelNodeTypes {{
                    getLLMChannelNodeTypes {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getLLMChannelNodeTypes")
