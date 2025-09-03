"""
Graphs API calls.
"""

def getGraphs(self, workspaceId, graphId=None, name=None, email=None, staged=True, limit=100, cursor=None, filters={}, fields=None):
    if fields is None: fields = self.getTypeFields("Graph")
    fields = "\n".join(fields)
    if filters is None: filters = {}
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getGraphs",
            "variables": {
                "workspaceId": workspaceId,
                "graphId": graphId,
                "staged": staged,
                "limit": limit,
                "cursor": cursor,
                "filters": filters
            },
            "query": f"""query 
                getGraphs($workspaceId: String!, $graphId: String, $staged: Boolean, $limit: Int, $cursor: String, $filters: GraphFilter) {{
                    getGraphs(workspaceId: $workspaceId, graphId: $graphId, staged: $staged, limit: $limit, cursor: $cursor, filters: $filters) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getGraphs")


def uploadGraph(self, workspaceId, channelId, graph, name, description='', staged=False, tags=[]):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createGraph",
            "variables": {
                "workspaceId": workspaceId,
                "channelId": channelId,
                "graph": graph,
                "name": name,
                "description": description,
                "staged": staged,
                "tags": tags
            },
            "query": """mutation 
                createGraph($workspaceId: String!, $channelId: String!, $graph: String!, $name: String!, $description: String, $staged: Boolean, $tags: [String]) {
                    createGraph(workspaceId: $workspaceId, channelId: $channelId, graph: $graph, name: $name, description: $description, staged: $staged, tags: $tags)
                }"""})
    return self.errorhandler(response, "createGraph")


def deleteGraph(self, workspaceId, graphId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "deleteGraph",
            "variables": {
                "workspaceId": workspaceId,
                "graphId": graphId
            },
            "query": """mutation 
                deleteGraph($workspaceId: String!, $graphId: String!) {
                    deleteGraph(workspaceId: $workspaceId, graphId: $graphId)
                }"""})
    return self.errorhandler(response, "deleteGraph")


def editGraph(self, workspaceId, graphId, name=None, description=None, graph=None, tags=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "editGraph",
            "variables": {
                "workspaceId": workspaceId,
                "graphId": graphId,
                "name": name,
                "description": description,
                "graph": graph,
                "tags": tags
            },
            "query": """mutation 
                editGraph($workspaceId: String!, $graphId: String!, $name: String, $description: String, $graph: String, $tags: [String]) {
                    editGraph(workspaceId: $workspaceId, graphId: $graphId, name: $name, description: $description, graph: $graph, tags: $tags)
                }"""})
    return self.errorhandler(response, "editGraph")


def downloadGraph(self, workspaceId, graphId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "downloadGraph",
            "variables": {
                "workspaceId": workspaceId,
                "graphId": graphId
            },
            "query": """mutation 
                downloadGraph($workspaceId: String!, $graphId: String!) {
                    downloadGraph(workspaceId: $workspaceId, graphId: $graphId)
                }"""})
    return self.errorhandler(response, "downloadGraph")


def getDefaultGraph(self, channelId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getDefaultGraph",
            "variables": {
                "channelId": channelId,
            },
            "query": """query 
                getDefaultGraph($channelId: String!) {
                    getDefaultGraph(channelId: $channelId)
                }"""})
    return self.errorhandler(response, "getDefaultGraph")


def setDefaultGraph(self, channelId, workspaceId, graphId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers,
        json = {
            "operationName": "setChannelGraph",
            "variables": {
                "channelId": channelId,
                "workspaceId": workspaceId,
                "graphId": graphId,
            },
            "query": """mutation 
                setChannelGraph($channelId: String!, $workspaceId: String!, $graphId: String) {
                    setChannelGraph(channelId: $channelId, workspaceId: $workspaceId, graphId: $graphId)
                }"""})
    return self.errorhandler(response, "setChannelGraph")
    