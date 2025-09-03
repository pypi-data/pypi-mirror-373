"""
Datasets API calls.
"""

def getDatasets(self, workspaceId, datasetId=None, cursor=None, limit=100, filters={}, fields=None):
    if fields is None: fields = self.getTypeFields("Dataset")
    fields = "\n".join(fields)
    if filters is None: filters = {}
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getDatasets",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId,
                "limit": limit,
                "cursor": cursor,
                "filters": filters
            },
            "query": f"""query 
                getDatasets($workspaceId: String!, $datasetId: String, $cursor: String, $limit: Int, $filters: DatasetFilter) {{
                    getDatasets(workspaceId: $workspaceId, datasetId: $datasetId, cursor: $cursor, limit: $limit, filters: $filters) {{
                       {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getDatasets")


def getDatasetJobs(self, organizationId, workspaceId, datasetId=None, cursor=None, limit=100, filters={}, fields=None):
    if fields is None: fields = self.getTypeFields("DatasetJob")
    fields = "\n".join(fields)
    if filters is None: filters = {}
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getDatasetJobs",
            "variables": {
                "organizationId": organizationId,
                "workspaceId": workspaceId,
                "datasetId": datasetId,
                "limit": limit,
                "cursor": cursor,
                "filters": filters
            },
            "query": f"""query 
                getDatasetJobs($organizationId: String, $workspaceId: String, $datasetId: String, $cursor: String, $limit: Int, $filters: DatasetJobFilter) {{
                    getDatasetJobs(organizationId: $organizationId, workspaceId: $workspaceId, datasetId: $datasetId, cursor: $cursor, limit: $limit, filters: $filters) {{
                       {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getDatasetJobs")


def createDataset(self, workspaceId, graphId, name, description=None, runs=1, seed=0, priority=1, tags=[]):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createDataset",
            "variables": {
                "workspaceId": workspaceId,
                "graphId": graphId,
                "name": name,
                "description": description,
                "runs": runs,
                "seed": seed,
                "priority": priority,
                "tags": tags
            },
            "query": """mutation 
                createDataset($workspaceId: String!, $graphId: String!, $name: String!, $description: String, $runs: Int!, $seed: Int!, $priority: Int!, $tags: [String]) {
                    createDataset(workspaceId: $workspaceId, graphId: $graphId, name: $name, description: $description, runs: $runs, seed: $seed, priority: $priority, tags: $tags)
                }"""})
    return self.errorhandler(response, "createDataset")


def deleteDataset(self, workspaceId, datasetId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "deleteDataset",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId
            },
            "query": """mutation 
                deleteDataset($workspaceId: String!, $datasetId: String!) {
                    deleteDataset(workspaceId: $workspaceId, datasetId: $datasetId)
                }"""})
    return self.errorhandler(response, "deleteDataset")


def editDataset(self, workspaceId, datasetId, name=None, description=None, pause=None, priority=None, tags=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "editDataset",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId,
                "name": name,
                "description": description,
                "pause": pause,
                "priority": priority,
                "tags": tags
            },
            "query": """mutation 
                editDataset($workspaceId: String!, $datasetId: String!, $name: String, $description: String, $pause: Boolean, $priority: Int, $tags: [String]) {
                    editDataset(workspaceId: $workspaceId, datasetId: $datasetId, name: $name, description: $description, pause: $pause, priority: $priority, tags: $tags)
                }"""})
    return self.errorhandler(response, "editDataset")


def downloadDataset(self, workspaceId, datasetId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "downloadDataset",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId
            },
            "query": """mutation 
                downloadDataset($workspaceId: String!, $datasetId: String!) {
                    downloadDataset(workspaceId: $workspaceId, datasetId: $datasetId)
                }"""})
    return self.errorhandler(response, "downloadDataset")


def cancelDataset(self, workspaceId, datasetId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "cancelDataset",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId
            },
            "query": """mutation 
                cancelDataset($workspaceId: String!, $datasetId: String!) {
                    cancelDataset(workspaceId: $workspaceId, datasetId: $datasetId)
                }"""})
    return self.errorhandler(response, "cancelDataset")


def datasetUpload(self, workspaceId, filename, filesize, description, tags=[]):
    if "UploadDatasetResponse" not in self.fields: fields = self.getTypeFields("UploadDatasetResponse")
    else: fields = self.fields["UploadDatasetResponse"]
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "uploadDatasetV2",
            "variables": {
                "workspaceId": workspaceId,
                "name": filename,
                "size": filesize,
                "description": description,
                "tags": tags
            },
            "query": f"""mutation 
                uploadDatasetV2($workspaceId: String!, $name: String!, $size: Float!, $description: String!, $tags: [String]) {{
                    uploadDatasetV2(workspaceId: $workspaceId, name: $name, size: $size, description: $description, tags: $tags){{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "uploadDatasetV2")

def datasetUploadFinalizer(self, workspaceId, uploadId, key, parts):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "uploadDatasetV2Finalizer",
            "variables": {
                "workspaceId": workspaceId,
                "uploadId": uploadId,
                "key": key,
                "parts": parts,
            },
            "query": """mutation 
                uploadDatasetV2Finalizer($workspaceId: String!, $uploadId: String!, $key: String!, $parts: [MultipartInput!]) {
                    uploadDatasetV2Finalizer(workspaceId: $workspaceId, uploadId: $uploadId, key: $key, parts: $parts)
                }"""})
    return self.errorhandler(response, "uploadDatasetV2Finalizer")


def getDatasetRuns(self, workspaceId, datasetId, state=None, fields=None):
    if fields is None: fields = self.getTypeFields("DatasetRun")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getDatasetRuns",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId,
                "state": state,
            },
            "query": f"""query 
                getDatasetRuns($workspaceId: String!, $datasetId: String!, $state: String) {{
                    getDatasetRuns(workspaceId: $workspaceId, datasetId: $datasetId, state: $state) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getDatasetRuns")


def getDatasetLog(self, workspaceId, datasetId, runId, fields=None):
    if fields is None: fields = self.getTypeFields("DatasetLog")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getDatasetLog",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId,
                "runId": runId
            },
            "query": f"""query 
                getDatasetLog($workspaceId: String!, $datasetId: String!, $runId: String!) {{
                    getDatasetLog(workspaceId: $workspaceId, datasetId: $datasetId, runId: $runId) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getDatasetLog")


def getDatasetFiles(self, workspaceId, datasetId, path, limit=100, cursor=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getDatasetFiles",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId,
                "path": path,
                "limit": limit,
                "cursor": cursor
            },
            "query": """query 
                getDatasetFiles($workspaceId: String!, $datasetId: String!, $path: String, $limit: Int, $cursor: String) {
                    getDatasetFiles(workspaceId: $workspaceId, datasetId: $datasetId, path: $path, limit: $limit, cursor: $cursor)
                }"""})
    return self.errorhandler(response, "getDatasetFiles")


def createMixedDataset(self, workspaceId, name, parameters, description='', seed=0, tags=[]):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createMixedDataset",
            "variables": {
                "workspaceId": workspaceId,
                "name": name,
                "parameters": parameters,
                "description": description,
                "seed": seed,
                "tags": tags
            },
            "query": """mutation 
                createMixedDataset($workspaceId: String!, $name: String!, $parameters: String!, $description: String, $seed: Int, $tags: [String]) {
                    createMixedDataset(workspaceId: $workspaceId, name: $name, parameters: $parameters, description: $description, seed: $seed, tags: $tags)
                }"""})
    return self.errorhandler(response, "createMixedDataset")