"""
Workspace Functions
"""

def set_workspace(self, workspaceId):
    """Set the workspace to the one you wish to work in.

    Parameters
    ----------
    workspaceId : str
        Workspace ID for the workspace you wish to work in.
    """
    from anatools.lib.print import print_color 
    self.check_logout()
    if workspaceId is None: raise Exception('WorkspaceId must be specified.')
    workspaces = self.get_workspaces(workspaceId=workspaceId)
    if len(workspaces) == 0: raise Exception(f'Workspace with workspaceId {workspaceId} not found!')
    self.workspace = workspaces[0]['workspaceId']
    self.organization = workspaces[0]['organizationId']
    if self.interactive: print_color(f'The current organization is: {self.organization}\nThe current workspace is: {self.workspace}', '91e600')
    return True


def get_workspaces(self, organizationId=None, workspaceId=None, cursor=None, limit=None, filters=None, fields=None):
    """Shows list of workspaces with id, name, and owner data.
    
    Parameters
    ----------
    organizationId : str
        Organization ID to filter on. Optional
    workspaceId : str
        Workspace ID to filter on. Optional
    cursor : str
        Cursor for pagination.
    limit : int
        Maximum number of workspaces to return.
    filters: dict
        Filters that limit output to entries that match the filter 
    fields : list
        List of fields to return, leave empty to get all fields.

    Returns
    -------
    list[dict]
        Workspace data for all workspaces for a user.
    """  
    if self.check_logout(): return
    if limit is not None and limit <= 100: items = limit
    else: items = 100
    workspaces = []
    while True:
        if limit and len(workspaces) + items > limit: items = limit - len(workspaces)
        ret = self.ana_api.getWorkspaces(organizationId=organizationId, workspaceId=workspaceId, limit=items, cursor=cursor, filters=filters, fields=fields)
        workspaces.extend(ret)
        if len(ret) < items or len(workspaces) == limit: break
        cursor = ret[-1]["workspaceId"]
    return workspaces


def create_workspace(self, name, description='', channelIds=[], volumeIds=[], code=None, tags=None, objective='', organizationId=None):
    """Create a new workspace with specific channels.
    
    Parameters
    ----------
    name : str    
        Workspace name.
    description : str
        Workspace description.
    channelIds : list[str]
        List of channel ids to add to workspace.
    volumeIds: list[str]
        List of volume ids that the workspace will have access to.
    code: str
        Content code that used for creating a workspace
    tags: list[str]
        List of tags to add to workspace.
    objective: str
        A goal to give the workspace.
    organizationId : str
        Organization ID. Defaults to current if not specified.  
    
    Returns
    -------
    str
        Workspace ID if creation was successful. Otherwise returns message.
    """    
    if self.check_logout(): return
    if name is None: raise ValueError("Name must be provided")
    if description is None: description = ''
    if code is None: code = ''
    if tags is None: tags = []
    if organizationId is None: organizationId = self.organization
    return self.ana_api.createWorkspace(organizationId=organizationId, name=name, description=description, channelIds=channelIds, volumeIds=volumeIds, code=code, tags=tags, objective=objective)


def delete_workspace(self, workspaceId=None):
    """Delete an existing workspace. 
    
    Parameters
    ----------
    workspaceId : str    
        Workspace ID for workspace to get deleted. Deletes current workspace if not specified. 
    
    Returns
    -------
    str
        Success or failure message if workspace was sucessfully removed.
    """
    if self.check_logout(): return
    if workspaceId is None: workspaceId = self.workspace 
    if self.interactive:
        response = input('This will destroy all data within the worksapce, inlcuding graphs, datasets and models.\nAre you certain you want to delete this workspace? (y/n)  ')
        if response.lower() != 'y': return True
    return self.ana_api.deleteWorkspace(workspaceId=workspaceId)


def edit_workspace(self, name=None, description=None, channelIds=None, volumeIds=None, ganIds=None, mapIds=None, tags=None, objective=None, workspaceId=None):
    """Edit workspace information. 
    
    Parameters
    ----------
    name : str    
        New name to replace old one.
    description : str
        New description to replace old one.
    channelIds: list[str]
        Names of channels that the workspace will have access to.
    volumeIds: list[str]
        List of volume ids that the workspace will have access to.
    ganIds: list[str]
        List of GAN ids that the workspace will have access to.
    mapIds: list[str]
        List of map ids that the workspace will have access to.
    tags: list[str]
        List of tags to add or remove.
    objective: str
        A goal to give the workspace.
    workspaceId : str    
        Workspace ID for workspace to update.
    
    Returns
    -------
    bool
        Success or failure message if workspace was sucessfully updated.
    """  
    if self.check_logout(): return
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.editWorkspace(workspaceId=workspaceId, name=name, description=description, channelIds=channelIds, volumeIds=volumeIds, ganIds=ganIds, mapIds=mapIds, tags=tags, objective=objective)


def mount_workspaces(self, workspaces):
    """Retrieves credentials for mounting workspaces.
    
    Parameters
    ----------
    workspaces : [str]
       Workspaces to retrieve mount credentials for.

    Returns
    -------
    dict
        Credential information.
    """
    self.check_logout()
    if not len(workspaces): raise Exception('The workspaces parameter must be a list of workspaceIds!')
    return self.ana_api.mountWorkspaces(workspaces=workspaces)