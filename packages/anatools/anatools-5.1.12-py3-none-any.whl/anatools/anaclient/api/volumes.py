"""
Volumes API calls.
"""

def getVolumes(self, organizationId=None, workspaceId=None, volumeId=None, cursor=None, limit=100, filters={}, fields=None):
    if fields is None: fields = self.getTypeFields("Volume")
    fields = "\n".join(fields)
    if filters is None: filters = {}
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getVolumes",
            "variables": {
                "organizationId": organizationId,
                "workspaceId": workspaceId,
                "volumeId": volumeId,
                "limit": limit,
                "cursor": cursor,
                "filters": filters
            },
            "query": f"""query 
                getVolumes($organizationId: String, $workspaceId: String, $volumeId: String, $limit: Int, $cursor: String, $filters: VolumeFilter) {{
                    getVolumes(organizationId: $organizationId, workspaceId: $workspaceId, volumeId: $volumeId, limit: $limit, cursor: $cursor, filters: $filters) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getVolumes")


def getVolumeData(self, volumeId, keys=[], dir=None, recursive=False, cursor=None, limit=100, filters=None):
    fields = self.getTypeFields("VolumeData")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getVolumeData",
            "variables": {
                "volumeId": volumeId,
                "keys": keys,
                "dir": dir,
                "recursive": recursive,
                "limit": limit,
                "cursor": cursor,
                "filters": filters
            },
            "query": f"""query 
                getVolumeData($volumeId: String!, $keys: [String], $dir: String, $recursive: Boolean, $limit: Int, $cursor: String, $filters: VolumeDataFilter) {{
                    getVolumeData(volumeId: $volumeId, keys: $keys, dir: $dir, recursive: $recursive, limit: $limit, cursor: $cursor, filters: $filters) {{
                       keys {{{fields}}}
                    }}
                }}"""})
    return self.errorhandler(response, "getVolumeData")


def createVolume(self, organizationId, name, description='', permission='write', tags=[]):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createVolume",
            "variables": {
                "organizationId": organizationId,
                "name": name,
                "description": description,
                "permission": permission,
                "tags": tags
            },
            "query": """mutation 
                createVolume($organizationId: String!, $name: String!, $description: String, $permission: String, $tags: [String]) {
                    createVolume(organizationId: $organizationId, name: $name, description: $description, permission: $permission, tags: $tags)
                }"""})
    return self.errorhandler(response, "createVolume")


def deleteVolume(self, volumeId, organizationId=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "deleteVolume",
            "variables": {
                "volumeId": volumeId,
                "organizationId": organizationId
            },
            "query": """mutation 
                deleteVolume($volumeId: String!, $organizationId: String!) {
                    deleteVolume(volumeId: $volumeId, organizationId: $organizationId)
                }"""})
    return self.errorhandler(response, "deleteVolume")


def editVolume(self, volumeId, name=None, description=None, permission=None, tags=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "editVolume",
            "variables": {
                "volumeId": volumeId,
                "name": name,
                "description": description,
                "permission": permission,
                "tags": tags
            },
            "query": """mutation 
                editVolume($volumeId: String!, $name: String, $description: String, $permission: String, $tags: [String]) {
                    editVolume(volumeId: $volumeId, name: $name, description: $description, permission: $permission, tags: $tags)
                }"""})
    return self.errorhandler(response, "editVolume")


def editVolumeData(self, volumeId, source, key):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "editVolumeData",
            "variables": {
                "volumeId": volumeId,
                "source": source,
                "key": key,
            },
            "query": """mutation 
                editVolumeData($volumeId: String!, $source: String!, $key: String!) {
                    editVolumeData(volumeId: $volumeId, source: $source, key: $key)
                }"""})
    return self.errorhandler(response, "editVolumeData")


def uploadVolumeData(self, volumeId, key, size):
    fields = self.getTypeFields("UploadVolumeDataResponse")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "uploadVolumeData",
            "variables": {
                "volumeId": volumeId,
                "key": key,
                "size": size,
            },
            "query": f"""mutation 
                uploadVolumeData($volumeId: String!, $key: String!, $size: Float!) {{
                    uploadVolumeData(volumeId: $volumeId, key: $key, size: $size) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "uploadVolumeData")


def uploadVolumeDataFinalizer(self, volumeId, uploadId, key, parts):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "uploadVolumeDataFinalizer",
            "variables": {
                "volumeId": volumeId,
                "uploadId": uploadId,
                "key": key,
                "parts": parts,
            },
            "query": """mutation 
                uploadVolumeDataFinalizer($volumeId: String!, $uploadId: String!, $key: String!, $parts: [MultipartInput!]) {
                    uploadVolumeDataFinalizer(volumeId: $volumeId, uploadId: $uploadId, key: $key, parts: $parts)
                }"""})
    return self.errorhandler(response, "uploadVolumeDataFinalizer")


def deleteVolumeData(self, volumeId, keys=[]):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "deleteVolumeData",
            "variables": {
                "volumeId": volumeId,
                "keys": keys
            },
            "query": """mutation 
                deleteVolumeData($volumeId: String!, $keys: [String]!) {
                    deleteVolumeData(volumeId: $volumeId, keys: $keys)
                }"""})
    return self.errorhandler(response, "deleteVolumeData")


def mountVolumes(self, volumes):
    fields = self.getTypeFields("VolumeCredentials")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "mountVolumes",
            "variables": {
                "volumes": volumes
            },
            "query": f"""mutation 
                mountVolumes($volumes: [String]!) {{
                    mountVolumes(volumes: $volumes) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "mountVolumes")


def addWorkspaceVolumes(self, workspaceId, volumeIds):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "addWorkspaceVolumes",
            "variables": {
                "workspaceId": workspaceId,
                "volumeIds": volumeIds
            },
            "query": """mutation 
                addWorkspaceVolumes($workspaceId: String!, $volumeIds: [String]!) {
                    addWorkspaceVolumes(workspaceId: $workspaceId, volumeIds: $volumeIds)
                }"""})
    return self.errorhandler(response, "addWorkspaceVolumes")


def removeWorkspaceVolumes(self, workspaceId, volumeIds):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "removeWorkspaceVolumes",
            "variables": {
                "workspaceId": workspaceId,
                "volumeIds": volumeIds
            },
            "query": """mutation 
                removeWorkspaceVolumes($workspaceId: String!, $volumeIds: [String]!) {
                    removeWorkspaceVolumes(workspaceId: $workspaceId, volumeIds: $volumeIds)
                }"""})
    return self.errorhandler(response, "removeWorkspaceVolumes")