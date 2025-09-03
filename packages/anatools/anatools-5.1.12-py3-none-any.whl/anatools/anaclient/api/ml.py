"""
ML API calls.
"""

def getMLArchitectures(self, fields=None):
    if fields is None: fields = self.getTypeFields("MLArchitecture")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getMLArchitectures",
            "variables": {},
            "query": f"""query 
                getMLArchitectures {{
                    getMLArchitectures {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getMLArchitectures")


def getMLModels(self, workspaceId, datasetId=None, modelId=None, cursor=None, limit=100, filters={}, fields=None):
    if fields is None: fields = self.getTypeFields("MLModel")
    fields = "\n".join(fields)
    if filters is None: filters = {}
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getMLModels",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId,
                "modelId": modelId,
                "cursor": cursor,
                "limit": limit,
                "filters": filters
            },
            "query": f"""query 
                getMLModels ($workspaceId: String!, $datasetId: String, $modelId: String, $cursor: String, $limit: Int, $filters: MLModelFilter) {{
                    getMLModels (workspaceId: $workspaceId, datasetId: $datasetId, modelId: $modelId, cursor: $cursor, limit: $limit, filters: $filters) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getMLModels")


def createMLModel(self, workspaceId, datasetId, architectureId, name, description=None, parameters=None, tags=[]):
    response = self.session.post(
        url = self.url, 
        headers = self.headers,
        json = {
            "operationName": "createMLModel",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId,
                "architectureId": architectureId,
                "name": name,
                "description": description,
                "parameters": parameters,
                "tags": tags
            },
            "query": """mutation 
                createMLModel ($workspaceId: String!, $datasetId: String!, $architectureId: String!, $name: String, $description: String, $parameters: String, $tags: [String]) {
                    createMLModel (workspaceId: $workspaceId, datasetId: $datasetId, architectureId: $architectureId, name: $name, description: $description, parameters: $parameters, tags: $tags)
                }"""})
    return self.errorhandler(response, "createMLModel")


def deleteMLModel(self, workspaceId, modelId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "deleteMLModel",
            "variables": {
                "workspaceId": workspaceId,
                "modelId": modelId,
            },
            "query": """mutation 
                deleteMLModel ($workspaceId: String!, $modelId: String!) {
                    deleteMLModel (workspaceId: $workspaceId, modelId: $modelId)
                }"""})
    return self.errorhandler(response, "deleteMLModel")


def editMLModel(self, workspaceId, modelId, name=None, description=None, tags=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "editMLModel",
            "variables": {
                "workspaceId": workspaceId,
                "modelId": modelId,
                "name": name,
                "description": description,
                "tags": tags
            },
            "query": """mutation 
                editMLModel ($workspaceId: String!, $modelId: String!, $name: String, $description: String, $tags: [String]) {
                    editMLModel (workspaceId: $workspaceId, modelId: $modelId, name: $name, description: $description, tags: $tags)
                }"""})
    return self.errorhandler(response, "editMLModel")


def downloadMLModel(self, workspaceId, modelId, checkpoint=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "downloadMLModel",
            "variables": {
                "workspaceId": workspaceId,
                "modelId": modelId,
                "checkpoint": checkpoint
            },
            "query": """mutation 
                downloadMLModel ($workspaceId: String!, $modelId: String!, $checkpoint: String) {
                    downloadMLModel (workspaceId: $workspaceId, modelId: $modelId, checkpoint: $checkpoint)
                }"""})
    return self.errorhandler(response, "downloadMLModel")


def uploadMLModel(self, workspaceId, architectureId, name, size, description=None, tags=[]):
    fields = self.getTypeFields("UploadMLModelResponse")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "uploadMLModel",
            "variables": {
                "workspaceId": workspaceId,
                "architectureId": architectureId,
                "name": name,
                "size": size,
                "description": description,
                "tags": tags
            },
            "query": f"""mutation 
                uploadMLModel ($workspaceId: String!, $architectureId: String!, $name: String!, $size: Float!, $description: String, $tags: [String]) {{
                    uploadMLModel (workspaceId: $workspaceId, architectureId: $architectureId, name: $name, size: $size, description: $description, tags: $tags) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "uploadMLModel")


def uploadMLModelFinalizer(self, workspaceId, key, uploadId, parts):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "uploadMLModelFinalizer",
            "variables": {
                "workspaceId": workspaceId,
                "key": key,
                "uploadId": uploadId,
                "parts": parts
            },
            "query": """mutation 
                uploadMLModelFinalizer ($workspaceId: String!, $key: String!, $uploadId: String, $parts: [MultipartInput!]) {
                    uploadMLModelFinalizer (workspaceId: $workspaceId, key: $key, uploadId: $uploadId, parts: $parts)
                }"""})
    return self.errorhandler(response, "uploadMLModelFinalizer")


def getMLInferences(self, workspaceId, inferenceId=None, datasetId=None, modelId=None, cursor=None, limit=100, filters={}, fields=None):
    if fields is None: fields = self.getTypeFields("MLInference")
    fields = "\n".join(fields)
    if filters is None: filters = {}
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getMLInferences",
            "variables": {
                "workspaceId": workspaceId,
                "inferenceId": inferenceId,
                "datasetId": datasetId,
                "modelId": modelId,
                "cursor": cursor,
                "limit": limit,
                "filters": filters
            },
            "query": f"""query 
                getMLInferences ($workspaceId: String!, $inferenceId: String, $datasetId: String, $modelId: String, $cursor: String, $limit: Int, $filters: MLInferenceFilter) {{
                    getMLInferences (workspaceId: $workspaceId, inferenceId: $inferenceId, datasetId: $datasetId, modelId: $modelId, cursor: $cursor, limit: $limit, filters: $filters) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getMLInferences")


def getMLInferenceMetrics(self, workspaceId, inferenceId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getMLInferenceMetrics",
            "variables": {
                "workspaceId": workspaceId,
                "inferenceId": inferenceId
            },
            "query": """query 
                getMLInferenceMetrics ($workspaceId: String!, $inferenceId: String!) {
                    getMLInferenceMetrics (workspaceId: $workspaceId, inferenceId: $inferenceId)
                }"""})
    return self.errorhandler(response, "getMLInferenceMetrics")


def createMLInference(self, workspaceId, datasetId, modelId, mapId=None, tags=[]):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createMLInference",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId,
                "modelId": modelId,
                "mapId": mapId,
                "tags": tags
            },
            "query": """mutation 
                createMLInference ($workspaceId: String!, $datasetId: String!, $modelId: String!, $mapId: String, $tags: [String]) {
                    createMLInference (workspaceId: $workspaceId, datasetId: $datasetId, modelId: $modelId, mapId: $mapId, tags: $tags)
                }"""})
    return self.errorhandler(response, "createMLInference")


def deleteMLInference(self, workspaceId, inferenceId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "deleteMLInference",
            "variables": {
                "workspaceId": workspaceId,
                "inferenceId": inferenceId
            },
            "query": """mutation 
                deleteMLInference ($workspaceId: String!, $inferenceId: String!) {
                    deleteMLInference (workspaceId: $workspaceId, inferenceId: $inferenceId)
                }"""})
    return self.errorhandler(response, "deleteMLInference")


def editMLInference(self, workspaceId, inferenceId, tags=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "editMLInference",
            "variables": {
                "workspaceId": workspaceId,
                "inferenceId": inferenceId,
                "tags": tags
            },
            "query": """mutation 
                editMLInference ($workspaceId: String!, $inferenceId: String!, $tags: [String]) {
                    editMLInference (workspaceId: $workspaceId, inferenceId: $inferenceId, tags: $tags)
                }"""})
    return self.errorhandler(response, "editMLInference")


def downloadMLInference(self, workspaceId, inferenceId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "downloadMLInference",
            "variables": {
                "workspaceId": workspaceId,
                "inferenceId": inferenceId
            },
            "query": """mutation 
                downloadMLInference ($workspaceId: String!, $inferenceId: String!) {
                    downloadMLInference (workspaceId: $workspaceId, inferenceId: $inferenceId)
                }"""})
    return self.errorhandler(response, "downloadMLInference")
