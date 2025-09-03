"""
Rules API calls.
"""
def getPlatformRules(self):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getPlatformRules",
            "variables": {},
            "query": """query 
                getPlatformRules {
                    getPlatformRules
                }"""})
    return self.errorhandler(response, "getPlatformRules")


def getOrganizationRules(self, organizationId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers,
        json = {
            "operationName": "getOrganizationRules",
            "variables": {
                "organizationId": organizationId
            },
            "query": """query 
                getOrganizationRules($organizationId: String) {
                    getOrganizationRules(organizationId: $organizationId)
                }"""})
    return self.errorhandler(response, "getOrganizationRules")


def getWorkspaceRules(self, workspaceId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getWorkspaceRules",
            "variables": {
                "workspaceId": workspaceId
            },
            "query": """query 
                getWorkspaceRules($workspaceId: String) {
                    getWorkspaceRules(workspaceId: $workspaceId)
                }"""})      
    return self.errorhandler(response, "getWorkspaceRules")


def getServiceRules(self, serviceId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getServiceRules",
            "variables": {
                "serviceId": serviceId  
            },
            "query": """query 
                getServiceRules($serviceId: String) {
                    getServiceRules(serviceId: $serviceId)
                }"""})
    return self.errorhandler(response, "getServiceRules")


def getUserRules(self):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getUserRules",
            "variables": {},
            "query": """query 
                getUserRules {
                    getUserRules
                }"""})
    return self.errorhandler(response, "getUserRules")


def editOrganizationRules(self, organizationId, rules):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "editOrganizationRules",
            "variables": {
                "organizationId": organizationId,
                "rules": rules
            },
            "query": """mutation 
                editOrganizationRules($organizationId: String!, $rules: String!) {
                    editOrganizationRules(organizationId: $organizationId, rules: $rules)
                }"""})
    return self.errorhandler(response, "editOrganizationRules")


def editWorkspaceRules(self, workspaceId, rules):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "editWorkspaceRules",
            "variables": {
                "workspaceId": workspaceId,
                "rules": rules
            },
            "query": """mutation 
                editWorkspaceRules($workspaceId: String!, $rules: String!) {
                    editWorkspaceRules(workspaceId: $workspaceId, rules: $rules)
                }"""})
    return self.errorhandler(response, "editWorkspaceRules")


def editServiceRules(self, serviceId, rules):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "editServiceRules",
            "variables": {
                "serviceId": serviceId,
                "rules": rules
            },
            "query": """mutation 
                editServiceRules($serviceId: String!, $rules: String!) {
                    editServiceRules(serviceId: $serviceId, rules: $rules)
                }"""})
    return self.errorhandler(response, "editServiceRules")


def editUserRules(self, userId, rules):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "editUserRules",
            "variables": {
                "userId": userId,
                "rules": rules
            },
            "query": """mutation 
                editUserRules($userId: String!, $rules: String!) {
                    editUserRules(userId: $userId, rules: $rules)
                }"""})
    return self.errorhandler(response, "editUserRules")
    