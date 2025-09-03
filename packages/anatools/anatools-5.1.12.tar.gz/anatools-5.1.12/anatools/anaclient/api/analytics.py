"""
Analytics API calls.
"""

def getAnalytics(self, workspaceId, analyticsId=None, datasetId=None, cursor=None,  limit=100, filters={}, fields=None):
    if fields is None: fields = self.getTypeFields("Analytics")
    fields = "\n".join(fields)
    if filters is None: filters = {}
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getAnalytics",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId,
                "analyticsId": analyticsId,
                "cursor": cursor,
                "limit": limit,
                "filters": filters
            },
            "query": f"""query 
                getAnalytics($workspaceId: String!, $datasetId: String, $analyticsId: String, $cursor: String, $limit: Int, $filters: AnalyticsFilter) {{
                    getAnalytics(workspaceId: $workspaceId, datasetId: $datasetId, analyticsId: $analyticsId, cursor: $cursor, limit: $limit, filters: $filters){{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getAnalytics")


def getAnalyticsTypes(self):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getAnalyticsTypes",
            "variables": {},
            "query": """query 
                getAnalyticsTypes{
                    getAnalyticsTypes
                }"""})
    return self.errorhandler(response, "getAnalyticsTypes")


def createAnalytics(self, workspaceId, datasetId, type, tags=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createAnalytics",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId,
                "type": type,
                "tags": tags

            },
            "query": """mutation 
                createAnalytics($workspaceId: String!, $datasetId: String!, $type: String!, $tags: [String]) {
                    createAnalytics(workspaceId: $workspaceId, datasetId: $datasetId, type: $type, tags: $tags)
                }"""})
    return self.errorhandler(response, "createAnalytics")


def deleteAnalytics(self, workspaceId, analyticsId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "deleteAnalytics",
            "variables": {
                "workspaceId": workspaceId,
                "analyticsId": analyticsId
            },
            "query": """mutation 
                deleteAnalytics($workspaceId: String!, $analyticsId: String!) {
                    deleteAnalytics(workspaceId: $workspaceId, analyticsId: $analyticsId)
                }"""})
    return self.errorhandler(response, "deleteAnalytics")


def editAnalytics(self, workspaceId, analyticsId, tags=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "editAnalytics",
            "variables": {
                "workspaceId": workspaceId,
                "analyticsId": analyticsId,
                "tags": tags
            },
            "query": """mutation 
                editAnalytics($workspaceId: String!, $analyticsId: String!, $tags: [String]) {
                    editAnalytics(workspaceId: $workspaceId, analyticsId: $analyticsId, tags: $tags)
                }"""})
    return self.errorhandler(response, "editAnalytics")
    