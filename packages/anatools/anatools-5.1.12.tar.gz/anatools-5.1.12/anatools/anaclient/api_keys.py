"""
API Keys Functions
"""


def get_api_keys(self):
    """Queries the api keys associated with user's account. This call will return data only when logged in with email/password.
    
    Parameters
    ----------
    
    Returns
    -------
    [dict]
        Names of API keys associated with user's account.
    """
    if self.check_logout(): return
    return self.ana_api.getAPIKeys()


def create_api_key(self, name, scope='user', organizationId=None, workspaceId=None, expires=None):
    """Creates a new API Key for the User; the key will only be visible once, so make sure to save it.
        To use the API Key on login, ensure it is set as an environment variable called RENDEREDAI_API_KEY or with the APIKey parameter when initializing the anatools client.
        This call can only be used when logged in with email/password.
    
    Parameters
    ----------
    name: str
        Name of the API Key. 
    scope: str
        Scope of the API Key, this can be set to 'user', 'organization', or 'workspace' to limit the scope of access for the API Key. 
    organizationId: str
        Organization ID to set the API Key access to a particular organization's data.
    workspaceId: str
        Workspace ID to set the API Key access to a particular workspace's data.
    expires : str
        Expiration date to set for the API Key. If no expiration is provided, the key will not expire. 
        
    Returns
    -------
    str
        API Key
    """
    if self.check_logout(): return
    if self.user is None: raise Exception("Please sign in with username/password to create an API Key.")
    if name is None: raise Exception("Name must be set for an API Key, each API Key name must be unique.")
    if scope not in ['user', 'organization', 'workspace']: raise Exception("Scope must be set to 'user', 'organization', or 'workspace'.")
    if organizationId and organizationId not in [org['organizationId'] for org in self.get_organizations()]: raise Exception("Organization ID not found.")
    if workspaceId and workspaceId not in [workspace['workspaceId'] for workspace in self.get_workspaces()]: raise Exception("Workspace ID not found.")
    return self.ana_api.createAPIKey(name=name, scope=scope, organizationId=organizationId, workspaceId=workspaceId, expires=expires)


def delete_api_key(self, name):
    """Deletes the API key from user account. This call can only be used when logged in with email/password.
    
    Parameters
    ----------
    name: str
        Name of the API Key to delete.
        
    Returns
    -------
    bool
        Success or failure message about API key deletion
    """
    if self.check_logout(): return
    if name is None: return
    return self.ana_api.deleteAPIKey(name=name)
