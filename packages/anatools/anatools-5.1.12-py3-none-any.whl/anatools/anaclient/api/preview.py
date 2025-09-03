"""
Previews API calls.
"""

def getPreview(self, workspaceId, previewId, fields=None):
    if fields is None: fields = self.getTypeFields("Preview")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getPreview",
            "variables": {
                "workspaceId": workspaceId,
                "previewId": previewId
            },
            "query": f"""query 
                getPreview($workspaceId: String!, $previewId: String!) {{
                    getPreview(workspaceId: $workspaceId, previewId: $previewId) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getPreview")


def createPreview(self, workspaceId, graphId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createPreview",
            "variables": {
                "workspaceId": workspaceId,
                "graphId": graphId
            },
            "query": """mutation 
                createPreview($workspaceId: String!, $graphId: String!) {
                    createPreview(workspaceId: $workspaceId, graphId: $graphId)
                }"""})
    return self.errorhandler(response, "createPreview")

