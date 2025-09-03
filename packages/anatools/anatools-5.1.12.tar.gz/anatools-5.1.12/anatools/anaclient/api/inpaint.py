"""
Inpaint API calls.
"""

def getInpaints(self, volumeId, inpaintId=None, limit=100, cursor=None, fields=None):
    if fields is None: fields = self.getTypeFields("Inpaint")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getInpaints",
            "variables": {
                "volumeId": volumeId,
                "inpaintId": inpaintId,
                "cursor": cursor,
                "limit": limit
            },
            "query": f"""query 
                getInpaints($volumeId: String!, $inpaintId: String, $cursor: String, $limit: Int) {{
                    getInpaints(volumeId: $volumeId, inpaintId: $inpaintId, cursor: $cursor, limit: $limit) {{
                        {fields}
                }}
            }}"""})
    return self.errorhandler(response, "getInpaints")


def getInpaintLog(self, volumeId, inpaintId, fields=None):
    if fields is None: fields = self.getTypeFields("InpaintLog")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getInpaintLogs",
            "variables": {
                "volumeId": volumeId,
                "inpaintId": inpaintId
            },
            "query": f"""query 
                getInpaintLog($volumeId: String!, $inpaintId: String!) {{
                    getInpaintLog(volumeId: $volumeId, inpaintId: $inpaintId) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getInpaintLogs")


def createInpaint(self, volumeId, location, files=[], destination=None, dilation=5, inputType="MASK", outputType="SATRGB_BACKGROUND"):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createInpaint",
            "variables": {
                "volumeId": volumeId,
                "location": location,
                "files": files,
                "destination": destination,
                "dilation": dilation,
                "inputType": inputType,
                "outputType": outputType
            },
            "query": """mutation 
                createInpaint($volumeId: String!, $location: String!, $files: [String], $destination: String, $dilation: Int, $inputType: InpaintInputType, $outputType: InpaintOutputType) {
                    createInpaint(volumeId: $volumeId, location: $location, files: $files, destination: $destination, dilation: $dilation, inputType: $inputType, outputType: $outputType)
                }"""})
    return self.errorhandler(response, "createInpaint")


def deleteInpaint(self, volumeId, inpaintId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "deleteInpaint",
            "variables": {
                "volumeId": volumeId,
                "inpaintId": inpaintId
            },
            "query": """mutation 
                deleteInpaint($volumeId: String!, $inpaintId: String!) {
                    deleteInpaint(volumeId: $volumeId, inpaintId: $inpaintId)
                }"""})
    return self.errorhandler(response, "deleteInpaint")
