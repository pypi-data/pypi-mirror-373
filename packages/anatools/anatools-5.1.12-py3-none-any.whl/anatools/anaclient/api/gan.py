"""
GAN API calls.
"""

def getGANModels(self, organizationId, workspaceId, modelId, limit=100, cursor=None, filters={}, fields=None):
    if fields is None: fields = self.getTypeFields("GANModel")
    fields = "\n".join(fields)
    if filters is None: filters = {}
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getGANModels",
            "variables": {
                "organizationId": organizationId,
                "workspaceId": workspaceId,
                "modelId": modelId,
                "limit": limit,
                "cursor": cursor,
                "filters": filters
            },
            "query": f"""query 
                getGANModels($organizationId: String, $workspaceId: String, $modelId: String, $limit: Int, $cursor: String, $filters: GANModelFilter) {{
                    getGANModels(organizationId: $organizationId, workspaceId: $workspaceId, modelId: $modelId, limit: $limit, cursor: $cursor, filters: $filters){{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getGANModels")


def getGANDatasets(self, datasetId, workspaceId, gandatasetId, limit=100, cursor=None, fields=None):
    if fields is None: fields = self.getTypeFields("GANDataset")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getGANDatasets",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId,
                "gandatasetId": gandatasetId,
                "limit": limit,
                "cursor": cursor
            },
            "query": f"""query 
                getGANDatasets($workspaceId: String!, $datasetId: String, $gandatasetId: String, $limit: Int, $cursor: String) {{
                    getGANDatasets(workspaceId: $workspaceId, datasetId: $datasetId, gandatasetId: $gandatasetId, limit: $limit, cursor: $cursor) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getGANDatasets")


def createGANDataset(self, workspaceId, datasetId, modelId, name, description='', tags=[]):
    if tags is None: tags = []
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createGANDataset",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId,
                "modelId": modelId,
                "name": name,
                "description": description,
                "tags": tags
            },
            "query": """mutation 
                createGANDataset($workspaceId: String!, $datasetId: String!, $modelId: String!, $name: String, $description: String, $tags: [String]) {
                    createGANDataset(workspaceId: $workspaceId, datasetId: $datasetId, modelId: $modelId, name: $name, description: $description, tags: $tags)
                }"""})
    return self.errorhandler(response, "createGANDataset")


def deleteGANDataset(self, datasetId, workspaceId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "deleteGANDataset",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId
            },
            "query": """mutation 
                deleteGANDataset($workspaceId: String!, $datasetId: String!) {
                    deleteGANDataset(workspaceId: $workspaceId, datasetId: $datasetId)
                }"""})
    return self.errorhandler(response, "deleteGANDataset")


def uploadGANModel(self, organizationId, name, size, description, flags='', tags=[]):
    fields = self.getTypeFields("UploadGANResponse")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "uploadGANModel",
            "variables": {
                "organizationId": organizationId,
                "name": name,
                "size": size,
                "description": description,
                "flags": flags,
                "tags": tags
            },
            "query": f"""mutation 
                uploadGANModel($organizationId: String!, $name: String!, $size: Float!, $description: String!, $flags: String, $tags: [String]) {{
                    uploadGANModel(organizationId: $organizationId, name: $name, size: $size, description: $description, flags: $flags, tags: $tags) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "uploadGANModel")


def uploadGANModelFinalizer(self, organizationId, uploadId, key, parts):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "uploadGANModelFinalizer",
            "variables": {
                "organizationId": organizationId,
                "uploadId": uploadId,
                "key": key,
                "parts": parts,
            },
            "query": """mutation 
                uploadGANModelFinalizer($organizationId: String!, $uploadId: String!, $key: String!, $parts: [MultipartInput!]) {
                    uploadGANModelFinalizer(organizationId: $organizationId, uploadId: $uploadId, key: $key, parts: $parts)
                }"""})
    return self.errorhandler(response, "uploadGANModelFinalizer")


def deleteGANModel(self, modelId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "deleteGANModel",
            "variables": {
                "modelId": modelId,
            },
            "query": """mutation 
                deleteGAN($modelId: String!) {
                    deleteGAN(modelId: $modelId)
                }"""})
    return self.errorhandler(response, "deleteGANModel")


def editGANModel(self, modelId, name=None, description=None, flags=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "editGAN",
            "variables": {
                "modelId": modelId,
                "name": name,
                "description": description,
                "flags": flags
            },
            "query": """mutation 
                editGAN($modelId: String!, $name: String, $description: String, $flags: String) {
                    editGAN(modelId: $modelId, name: $name, description: $description, flags: $flags)
                }"""})
    return self.errorhandler(response, "editGAN")


def downloadGANModel(self, modelId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "downloadGAN",
            "variables": {
                "modelId": modelId
            },
            "query": """mutation 
                downloadGAN($modelId: String!) {
                    downloadGAN(modelId: $modelId) 
                }"""})
    return self.errorhandler(response, "downloadGAN")
