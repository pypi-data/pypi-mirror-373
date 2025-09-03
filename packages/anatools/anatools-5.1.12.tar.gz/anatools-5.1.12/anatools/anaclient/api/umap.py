"""
GAN API calls.
"""

def getUMAPs(self, umapId, datasetId, workspaceId, limit=100, cursor=None, filters={}, fields=None):
    if fields is None: fields = self.getTypeFields("UMAP")
    fields = "\n".join(fields)
    if filters is None: filters = {}
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getUMAPs",
            "variables": {
                "workspaceId": workspaceId,
                "umapId": umapId,
                "datasetId": datasetId,
                "limit": limit,
                "cursor": cursor,
                "filters": filters
            },
            "query": f"""query 
                getUMAPs($workspaceId: String!, $datasetId: String, $umapId: String, $limit: Int, $cursor: String, $filters: UMAPFilter) {{
                    getUMAPs(workspaceId: $workspaceId, datasetId: $datasetId, umapId: $umapId, limit: $limit, cursor: $cursor, filters: $filters) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getUMAPs")


def createUMAP(self, workspaceId, name, datasetIds, samples, description=None, seed=None, tags=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createUMAP",
            "variables": {
                "workspaceId": workspaceId,
                "name": name,
                "datasetIds": datasetIds,
                "samples": samples,
                "description": description,
                "seed": seed,
                "tags": tags
            },
            "query": """mutation 
                createUMAP($workspaceId: String!, $name: String, $datasetIds: [String]!, $samples: [Int]!, $description: String, $seed: Int, $tags: [String]) {
                    createUMAP(workspaceId: $workspaceId, name: $name, datasetIds: $datasetIds, samples: $samples, description: $description, seed: $seed, tags: $tags)
                }"""})
    return self.errorhandler(response, "createUMAP")


def deleteUMAP(self, umapId, workspaceId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "deleteUMAP",
            "variables": {
                "workspaceId": workspaceId,
                "umapId": umapId,
            },
            "query": """mutation 
                deleteUMAP($workspaceId: String!, $umapId: String!) {
                    deleteUMAP(workspaceId: $workspaceId, umapId: $umapId)
                }"""})
    return self.errorhandler(response, "deleteUMAP")


def editUMAP(self, workspaceId, umapId, name=None, description=None, tags=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "editUMAP",
            "variables": {
                "workspaceId": workspaceId,
                "umapId": umapId,
                "name": name,
                "description": description,
                "tags": tags
            },
            "query": """mutation 
                editUMAP($workspaceId: String!, $umapId: String!, $name: String, $description: String, $tags: [String]) {
                    editUMAP(workspaceId: $workspaceId, umapId: $umapId, name: $name, description: $description, tags: $tags)
                }"""})
    return self.errorhandler(response, "editUMAP")