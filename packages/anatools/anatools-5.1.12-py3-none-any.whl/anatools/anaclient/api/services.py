"""
Services API calls.
"""

def getServiceTypes(self, fields=None):
    if fields is None: fields = self.getTypeFields("ServiceType")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getServiceTypes",
            "variables": {},
            "query": F"""query 
                getServiceTypes {{
                    getServiceTypes {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getServiceTypes")


def getServices(self, organizationId=None, workspaceId=None, serviceId=None, limit=100, cursor=None, filters={}, fields=None):
    if fields is None: fields = self.getTypeFields("Service")
    fields = "\n".join(fields)
    if filters is None: filters = {}
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getServices",
            "variables": {
                "organizationId": organizationId,
                "workspaceId": workspaceId,
                "serviceId": serviceId,
                "limit": limit,
                "cursor": cursor,
                "filters": filters
            },
            "query": F"""query 
                getServices($organizationId: String, $workspaceId: String, $serviceId: String, $limit: Int, $cursor: String, $filters: ServicesFilter) {{
                    getServices(organizationId: $organizationId, workspaceId: $workspaceId, serviceId: $serviceId, limit: $limit, cursor: $cursor, filters: $filters) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getServices")


def createService(self, organizationId, serviceTypeId, name, description=None, volumes=None, instance=None, tags=None, editorId=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createService",
            "variables": {
                "organizationId": organizationId,
                "serviceTypeId": serviceTypeId,
                "name": name,
                "description": description,
                "volumes": volumes,
                "instance": instance,
                "tags": tags,
                "editorId": editorId
            },
            "query": """mutation 
                createService($organizationId: String!, $serviceTypeId: String!, $name: String!, $description: String, $volumes: [String], $instance: String, $tags: [String], $editorId: String) {
                    createService(organizationId: $organizationId, serviceTypeId: $serviceTypeId, name: $name, description: $description, volumes: $volumes, instance: $instance, tags: $tags, editorId: $editorId)
                }"""})
    return self.errorhandler(response, "createService")


def deleteService(self, serviceId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "deleteService",
            "variables": {
                "serviceId": serviceId,
            },
            "query": """mutation 
                deleteService($serviceId: String!) {
                    deleteService(serviceId: $serviceId)
                }"""})
    return self.errorhandler(response, "deleteService")


def editService(self, serviceId, name=None, description=None, volumes=None, instance=None, tags=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "editService",
            "variables": {
                "serviceId": serviceId,
                "name": name,
                "description": description,
                "volumes": volumes,
                "instance": instance,
                "tags": tags
            },
            "query": """mutation 
                editService($serviceId: String!, $name: String, $description: String, $volumes: [String], $instance: String, $tags: [String]) {
                    editService(serviceId: $serviceId, name: $name, description: $description, volumes: $volumes, instance: $instance, tags: $tags)
                }"""})
    return self.errorhandler(response, "editService")


def deployService(self, serviceId):
    fields = self.getTypeFields("ECRDeployment")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "deployService",
            "variables": {
                "serviceId": serviceId
            },
            "query": f"""mutation 
                deployService($serviceId: String!) {{
                    deployService(serviceId: $serviceId) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "deployService")


def getServiceDeployment(self, deploymentId):
    fields = self.getTypeFields("ServiceDeployment")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getServiceDeployment",
            "variables": {
                "deploymentId": deploymentId
            },
            "query": f"""query 
                getServiceDeployment($deploymentId: String!) {{
                    getServiceDeployment(deploymentId: $deploymentId) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getServiceDeployment")

    
def addWorkspaceServices(self, workspaceId, serviceIds):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "addWorkspaceServices",
            "variables": {
                "workspaceId": workspaceId,
                "serviceIds": serviceIds
            },
            "query": """mutation 
                addWorkspaceServices($workspaceId: String!, $serviceIds: [String]!) {
                    addWorkspaceServices(workspaceId: $workspaceId, serviceIds: $serviceIds)
                }"""})
    return self.errorhandler(response, "addWorkspaceServices")


def removeWorkspaceServices(self, workspaceId, serviceIds):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "removeWorkspaceServices",
            "variables": {
                "workspaceId": workspaceId,
                "serviceIds": serviceIds
            },
            "query": """mutation 
                removeWorkspaceServices($workspaceId: String!, $serviceIds: [String]!) {
                    removeWorkspaceServices(workspaceId: $workspaceId, serviceIds: $serviceIds)
                }"""})
    return self.errorhandler(response, "removeWorkspaceServices")


def getServiceJobs(self, workspaceId, serviceId, limit=100, cursor=None, filters={}, fields=None):
    if fields is None: fields = self.getTypeFields("ServiceJob")
    fields = "\n".join(fields)
    if filters is None: filters = {}
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getServiceJobs",
            "variables": {
                "workspaceId": workspaceId,
                "serviceId": serviceId,
                "limit": limit,
                "cursor": cursor,
                "filters": filters
            },
            "query": F"""query 
                getServiceJobs($workspaceId: String!, $serviceId: String, $limit: Int, $cursor: String, $filters: ServiceJobsFilter) {{
                    getServiceJobs(workspaceId: $workspaceId, serviceId: $serviceId, limit: $limit, cursor: $cursor, filters: $filters) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getServiceJobs")


def createServiceJob(self, workspaceId, serviceId, name, description, payload):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createServiceJob",
            "variables": {
                "workspaceId": workspaceId,
                "serviceId": serviceId,
                "name": name,
                "description": description,
                "payload": payload
            },
            "query": """mutation 
                createServiceJob($workspaceId: String!, $serviceId: String!, $name: String!, $description: String, $payload: String!) {
                    createServiceJob(workspaceId: $workspaceId, serviceId: $serviceId, name: $name, description: $description, payload: $payload)
                }"""})
    return self.errorhandler(response, "createServiceJob")


def deleteServiceJob(self, jobId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "deleteServiceJob",
            "variables": {
                "jobId": jobId
            },
            "query": """mutation 
                deleteServiceJob($jobId: String!) {
                    deleteServiceJob(jobId: $jobId)
                }"""})
    return self.errorhandler(response, "deleteServiceJob")


def getWorkspaceServiceCredentials(self, workspaceId):
    fields = self.getTypeFields("ServiceCredentials")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getWorkspaceServiceCredentials",
            "variables": {
                "workspaceId": workspaceId
            },
            "query": f"""query 
                getWorkspaceServiceCredentials($workspaceId: String!) {{
                    getWorkspaceServiceCredentials(workspaceId: $workspaceId) {{
                        {fields}
                    }}
                }}"""
        })
    return self.errorhandler(response, "getWorkspaceServiceCredentials")
    

def getInstanceTypes(self):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getInstanceTypes",
            "variables": {},
            "query": """query
                getInstanceTypes {
                    getInstanceTypes
                }"""
        })
    return self.errorhandler(response, "getInstanceTypes")