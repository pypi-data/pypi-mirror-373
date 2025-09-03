"""
Annotations API calls.
"""

def getAnnotationFormats(self):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getAnnotationFormats",
            "variables": {},
            "query": """query 
                getAnnotationFormats{
                    getAnnotationFormats
                }"""})
    return self.errorhandler(response, "getAnnotationFormats")


def getAnnotations(self, workspaceId, datasetId, annotationId, cursor=None, limit=100, filters={}, fields=None):
    if fields is None: fields = self.getTypeFields("Annotation")
    fields = "\n".join(fields)
    if filters is None: filters = {}
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getAnnotations",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId,
                "annotationId": annotationId,
                "cursor": cursor,
                "limit": limit,
                "filters": filters
            },
            "query": f"""query 
                getAnnotations($workspaceId: String!, $datasetId: String $annotationId: String, $limit: Int, $cursor: String, $filters: AnnotationFilter) {{
                    getAnnotations(workspaceId: $workspaceId, datasetId: $datasetId, annotationId: $annotationId, limit: $limit, cursor: $cursor, filters: $filters){{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getAnnotations")


def getAnnotationMaps(self, organizationId, workspaceId, mapId, cursor=None, limit=100, filters={}, fields=None):
    if fields is None: fields = self.getTypeFields("AnnotationMap")
    fields = "\n".join(fields)
    if filters is None: filters = {}
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getAnnotationMaps",
            "variables": {
                "organizationId": organizationId,
                "workspaceId": workspaceId,
                "mapId": mapId,
                "cursor": cursor,
                "limit": limit,
                "filters": filters
            },
            "query": f"""query 
                getAnnotationMaps($organizationId: String, $workspaceId: String, $mapId: String, $limit: Int, $cursor: String, $filters: AnnotationMapFilter) {{
                    getAnnotationMaps(organizationId: $organizationId, workspaceId: $workspaceId, mapId: $mapId, limit: $limit, cursor: $cursor, filters: $filters) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getAnnotationMaps")


def downloadAnnotationMap(self, mapId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "downloadMap",
            "variables": {
                "mapId": mapId
            },
            "query": """mutation 
                downloadMap($mapId: String!) {
                    downloadMap(mapId: $mapId) 
                }"""})
    return self.errorhandler(response, "downloadMap")


def createAnnotation(self, workspaceId, datasetId, format, mapId=None, tags=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createAnnotation",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId,
                "format": format,
                "mapId": mapId,
                "tags": tags
            },
            "query": """mutation 
                createAnnotation($workspaceId: String!, $datasetId: String!, $format: String!, $mapId: String, $tags: [String]) {
                    createAnnotation(workspaceId: $workspaceId, datasetId: $datasetId, format: $format, mapId: $mapId, tags: $tags)
                }"""})
    return self.errorhandler(response, "createAnnotation")


def downloadAnnotation(self, workspaceId, annotationId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "downloadAnnotation",
            "variables": {
                "workspaceId": workspaceId,
                "annotationId": annotationId
            },
            "query": """mutation 
                downloadAnnotation($workspaceId: String!, $annotationId: String!) {
                    downloadAnnotation(workspaceId: $workspaceId, annotationId: $annotationId)
                }"""})
    return self.errorhandler(response, "downloadAnnotation")


def deleteAnnotation(self, workspaceId, annotationId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "deleteAnnotation",
            "variables": {
                "workspaceId": workspaceId,
                "annotationId": annotationId
            },
            "query": """mutation 
                deleteAnnotation($workspaceId: String!, $annotationId: String!) {
                    deleteAnnotation(workspaceId: $workspaceId, annotationId: $annotationId)
                }"""})
    return self.errorhandler(response, "deleteAnnotation")


def editAnnotation(self, workspaceId, annotationId, tags=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "editAnnotation",
            "variables": {
                "workspaceId": workspaceId,
                "annotationId": annotationId,
                "tags": tags
            },
            "query": """mutation 
                editAnnotation($workspaceId: String!, $annotationId: String!, $tags: [String]) {
                    editAnnotation(workspaceId: $workspaceId, annotationId: $annotationId, tags: $tags)
                }"""})
    return self.errorhandler(response, "editAnnotation")


def createAnnotationMap(self, organizationId, name, description=None, tags=None):
    if fields is None: fields = self.getTypeFields("MapData")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createMap",
            "variables": {
                "organizationId": organizationId,
                "name": name,
                "description": description,
                "tags": tags
            },
            "query": f"""mutation 
                createMap($organizationId: String!, $name: String!, $description: String, $tags: [String]) {{
                    createMap(organizationId: $organizationId, name: $name, description: $description, tags: $tags){{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "createMap")


def editAnnotationMap(self, mapId, name=None, description=None, tags=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "editMap",
            "variables": {
                "mapId": mapId,
                "name": name,
                "description": description,
                "tags": tags
            },
            "query": """mutation 
                editMap($mapId: String!, $name: String, $description: String, $tags: [String]) {
                    editMap(mapId: $mapId, name: $name, description: $description, tags: $tags)
                }"""})
    return self.errorhandler(response, "editMap")


def deleteAnnotationMap(self, mapId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "deleteManageMap",
            "variables": {
                "mapId": mapId,
            },
            "query": """mutation 
                deleteMap($mapId: String!) {
                    deleteMap(mapId: $mapId)
                }"""})
    return self.errorhandler(response, "deleteMap")