"""
Image API calls.
"""

def getImageAnnotation(self, workspaceId, datasetId, filename, fields=None):
    if fields is None: fields = self.getTypeFields("RunData")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getImageAnnotation",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId,
                "filename": filename
            },
            "query": f"""query 
                getImageAnnotation($workspaceId: String!, $datasetId: String! $filename: String!) {{
                    getImageAnnotation(workspaceId: $workspaceId, datasetId: $datasetId, filename: $filename) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getImageAnnotation")


def getImageMask(self, workspaceId, datasetId, filename, fields=None):
    if fields is None: fields = self.getTypeFields("RunData")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getImageMask",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId,
                "filename": filename
            },
            "query": f"""query 
                getImageMask($workspaceId: String!, $datasetId: String! $filename: String!) {{
                    getImageMask(workspaceId: $workspaceId, datasetId: $datasetId, filename: $filename) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getImageMask")


def getImageMetadata(self, workspaceId, datasetId, filename, fields=None):
    if fields is None: fields = self.getTypeFields("RunData")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getImageMetadata",
            "variables": {
                "workspaceId": workspaceId,
                "datasetId": datasetId,
                "filename": filename
            },
            "query": f"""query 
                getImageMetadata($workspaceId: String!, $datasetId: String! $filename: String!) {{
                    getImageMetadata(workspaceId: $workspaceId, datasetId: $datasetId, filename: $filename) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getImageMetadata")
