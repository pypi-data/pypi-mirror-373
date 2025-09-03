"""
Channels API calls.
"""

def getChannels(self, organizationId=None, workspaceId=None, channelId=None, limit=100, cursor=None, filters={}, fields=None):
    if fields is None: fields = self.getTypeFields("Channel")
    fields = "\n".join(fields)
    if filters is None: filters = {}
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getChannels",
            "variables": {
                "organizationId": organizationId,
                "workspaceId": workspaceId,
                "channelId": channelId,
                "limit": limit,
                "cursor": cursor,
                "filters": filters
            },
            "query": F"""query 
                getChannels($organizationId: String, $workspaceId: String, $channelId: String, $limit: Int, $cursor: String, $filters: ChannelFilter) {{
                    getChannels(organizationId: $organizationId, workspaceId: $workspaceId, channelId: $channelId, limit: $limit, cursor: $cursor, filters: $filters) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getChannels")


def getChannelDeployment(self, deploymentId):
    fields = self.getTypeFields("ChannelDeployment")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getChannelDeployment",
            "variables": {
                "deploymentId": deploymentId
            },
            "query": f"""query 
                getChannelDeployment($deploymentId: String!) {{
                    getChannelDeployment(deploymentId: $deploymentId) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getChannelDeployment")


def getChannelSchema(self, channelId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers,
        json = {
            "operationName": "getChannelSchema",
            "variables": {
                "channelId": channelId
            },
            "query": """query getChannelSchema($channelId: String) {
                getChannelSchema(channelId: $channelId)
            }"""})
    return self.errorhandler(response, "getChannelSchema")


def createChannel(self, organizationId, name, description=None, volumes=None, instance=None, timeout=None, interfaceVersion=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createChannel",
            "variables": {
                "organizationId": organizationId,
                "name": name,
                "description": description,
                "volumes": volumes,
                "instance": instance,
                "timeout": timeout,
                "interfaceVersion": interfaceVersion
            },
            "query": """mutation 
                createChannel($organizationId: String!, $name: String!, $description: String, $volumes: [String], $instance: String, $timeout: Int, $interfaceVersion: Int) {
                    createChannel(organizationId: $organizationId, name: $name, description: $description, volumes: $volumes, instance: $instance, timeout: $timeout, interfaceVersion: $interfaceVersion)
                }"""})
    return self.errorhandler(response, "createChannel")


def deleteChannel(self, channelId, organizationId=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "deleteChannel",
            "variables": {
                "channelId": channelId,
                "organizationId": organizationId
            },
            "query": """mutation 
                deleteChannel($channelId: String!, $organizationId: String!) {
                    deleteChannel(channelId: $channelId, organizationId: $organizationId)
                }"""})
    return self.errorhandler(response, "deleteChannel")


def editChannel(self, channelId, name=None, description=None, volumes=None, instance=None, timeout=None, status=None, interfaceVersion=None, preview=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "editChannel",
            "variables": {
                "channelId": channelId,
                "name": name,
                "description": description,
                "volumes": volumes,
                "instance": instance,
                "timeout": timeout,
                "status":status,
                "interfaceVersion": interfaceVersion,
                "preview": preview
            },
            "query": """mutation 
                editChannel($channelId: String!, $name: String, $description: String, $volumes: [String], $instance: String, $timeout: Int, $status: String, $interfaceVersion: Int, $preview: Boolean) {
                    editChannel(channelId: $channelId, name: $name, description: $description, volumes: $volumes, instance: $instance, timeout: $timeout, status: $status, interfaceVersion: $interfaceVersion, preview: $preview)
                }"""})
    return self.errorhandler(response, "editChannel")


def deployChannel(self, channelId, alias=None):
    fields = self.getTypeFields("ECRDeployment")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "deployChannel",
            "variables": {
                "channelId": channelId,
                "alias": alias
            },
            "query": f"""mutation 
                deployChannel($channelId: String!, $alias: String) {{
                    deployChannel(channelId: $channelId, alias: $alias) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "deployChannel")

    
def getChannelDocumentation(self, channelId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers,
        json = {
            "operationName": "getChannelDocumentation",
            "variables": {
                "channelId": channelId
            },
            "query": """query getChannelDocumentation($channelId: String!) {
                getChannelDocumentation(channelId: $channelId)
            }"""})
    return self.errorhandler(response, "getChannelDocumentation")


def uploadChannelDocumentation(self, channelId, keys=[]):
    fields = self.getTypeFields("ChannelDocumentationUpload")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers,
        json = {
            "operationName": "uploadChannelDocumentation",
            "variables": {
                "channelId": channelId,
                "keys": keys,
            },
            "query": f"""mutation uploadChannelDocumentation($channelId: String!, $keys: [String]!) {{
                uploadChannelDocumentation(channelId: $channelId, keys: $keys) {{
                    {fields}
                }}
            }}"""})
    return self.errorhandler(response, "uploadChannelDocumentation")


def getNodeDocumentation(self, channelId, node, fields=None):
    if fields is None: fields = self.getTypeFields("NodeDocumentation")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers,
        json = {
            "operationName": "getNodeDocumentation",
            "variables": {
                "channelId": channelId,
                "nodeClass": node
            },
            "query": f"""query getNodeDocumentation($channelId: String!, $nodeClass: String!) {{
                getNodeDocumentation(channelId: $channelId, nodeClass: $nodeClass) {{
                    {fields}
                }}
            }}"""})
    return self.errorhandler(response, "getNodeDocumentation")