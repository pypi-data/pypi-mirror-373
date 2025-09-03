"""
API Keys calls.
"""

def getAPIKeyContext(self, apiKey):
    fields = self.getTypeFields("APIKey")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getAPIKeyContext",
            "variables": {
                "apiKey": apiKey
            },
            "query": f"""query getAPIKeyContext($apiKey: String!) {{
                            getAPIKeyContext(apiKey: $apiKey) {{
                                {fields}
                            }}
                        }}"""})
    return self.errorhandler(response, "getAPIKeyContext")

def getCurrentUserContext(self):
    """Fetches the current user's context using the Bearer token in session headers."""
    import time
    response = self.session.post(
        url=self.url,
        headers=self.headers, # Assumes Bearer token is already in self.headers
        json={
            "operationName": "GetCurrentUser",
            "variables": {},
            "query": """query GetCurrentUser {
                            getCurrentUser { # Or the actual query name and returned fields
                                userId
                                name # Added name as per definition
                                email
                                # Add other fields like defaultOrganizationId, defaultWorkspaceId if available
                            }
                        }"""})
    # The errorhandler should manage API errors, including token-related ones.
    data = self.errorhandler(response, "getCurrentUser")
    if data and 'userId' in data: # Basic validation
        # If the token itself has an expiry and it's returned by an introspection endpoint,
        # that would be ideal. For now, we don't have 'expiresAt' from this call.
        # The idtoken will be the bearer token itself, which anaclient.py will set.
        pass # Data is good
    return data


def getAPIKeys(self, apiKey=None, name=None):
    fields = self.getTypeFields("APIKey")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getAPIKeys",
            "variables": {
                "apiKey": apiKey,
                "name": name
            },
            "query": f"""query getAPIKeys ($apiKey: String, $name: String) {{
                            getAPIKeys(apiKey: $apiKey, name: $name) {{
                                {fields}
                            }}
                        }}"""})
    return self.errorhandler(response, "getAPIKeys")


def createAPIKey(self, name, scope="user", organizationId=None, workspaceId=None, expires=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createAPIKey",
            "variables": {
                "name": name,
                "scope": scope,
                "organizationId": organizationId,
                "workspaceId": workspaceId,
                "expiresAt": expires
            },
            "query": """mutation createAPIKey($name: String!, $scope: String, $organizationId: String, $workspaceId: String, $expiresAt: String) {
                            createAPIKey(name: $name, scope: $scope, organizationId: $organizationId, workspaceId: $workspaceId, expiresAt: $expiresAt)
                        }"""})
    return self.errorhandler(response, "createAPIKey")


def deleteAPIKey(self, name):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "deleteAPIKey",
            "variables": {
                "name": name
            },
            "query": """mutation deleteAPIKey($name: String!) {
                            deleteAPIKey(name: $name)
                        }"""})
    return self.errorhandler(response, "deleteAPIKey")
