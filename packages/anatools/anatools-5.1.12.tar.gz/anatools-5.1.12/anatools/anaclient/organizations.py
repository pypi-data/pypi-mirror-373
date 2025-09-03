"""
Organization Functions
"""


def set_organization(self, organizationId, workspaceId=None):
    """Set the organization (and optionally a workspace) to the one you wish to work in.

    Parameters
    ----------
    organizationId : str
        Organization ID for the organization you wish to work in.
    workspaceId : str, optional
        Workspace ID for the workspace you wish to work in. Uses default workspace if this is not set.
    """
    from anatools.lib.print import print_color

    self.check_logout()
    if organizationId is None: raise Exception('OrganizationId must be specified.')
    organization = self.get_organizations(organizationId=organizationId)[0]
    self.organization = organization['organizationId']
    workspaces = self.get_workspaces(organizationId=self.organization)
    if len(workspaces) == 0: 
        if self.interactive: raise Exception("No workspaces available, please contact support@rendered.ai."); 
    if workspaceId:
        if workspaceId not in [w['workspaceId'] for w in workspaces]:
            raise Exception(f"Workspace {workspaceId} not found in organization {organizationId}.")
        self.workspace = workspaceId
    self.workspace = workspaces[0]['workspaceId']
    if self.interactive: print_color(f'The current organization is: {self.organization}\nThe current workspace is: {self.workspace}', '91e600')
    return True


def get_organizations(self, organizationId=None, cursor=None, limit=None, fields=None):
    """Shows the organizations the user belongs to and the user's role in that organization.
    
    Parameters
    ----------
    organizationId : str
        Organization ID to filter.
    cursor : str
        Cursor for pagination.
    limit : int
        Maximum number of organizations to return.
    fields : list
        List of fields to return, leave empty to get all fields.
    
    Returns
    -------
    list[dict]
        Information about the organizations you belong to. 
    """  
    self.check_logout()
    if limit is not None and limit <= 100: items = limit
    else: items = 100
    organizations = []
    while True:
        if limit and len(organizations) + items > limit: items = limit - len(organizations)
        ret = self.ana_api.getOrganizations(organizationId, limit=items, cursor=cursor, fields=fields)
        organizations.extend(ret)
        if len(ret) < items or len(organizations) == limit: break
        cursor = ret[-1]["organizationId"]
    return organizations


def edit_organization(self, name, organizationId=None):
    """Update the organization name. Uses current organization if no organizationId provided.
    
    Parameters
    ----------
    name : str
        Name to update organization to.
    organizationId : str
        Organization Id to update.
    
    Returns
    -------
    bool
        True if organization was edited successfully, False otherwise.
    """  
    self.check_logout()
    if name is None: raise ValueError("The name parameter is required!")
    if organizationId is None: organizationId = self.organization
    return self.ana_api.editOrganization(organizationId=organizationId, name=name)


def get_organization_members(self, organizationId=None, cursor=None, limit=None, fields=None):
    """Get users of an organization.
    
    Parameters
    ----------
    organizationId : str
        Organization ID. Defaults to current if not specified.
    cursor : str
        Cursor for pagination.
    limit : int
        Maximum number of members to return.
    fields : list
        List of fields to return, leave empty to get all fields.
    
    Returns
    -------
    list[dict]
        Information about users of an organization.
    """
    self.check_logout()
    if organizationId is None: organizationId = self.organization
    if limit is not None and limit <= 100: items = limit
    else: items = 100
    members = []
    while True:
        if limit and len(members) + items > limit: items = limit - len(members)
        ret = self.ana_api.getMembers(organizationId=organizationId, limit=items, cursor=cursor, fields=fields)
        members.extend(ret)
        if len(ret) < items or len(members) == limit: break
        cursor = ret[-1]["userId"]
    return members


def get_organization_invites(self, organizationId=None, cursor=None, limit=None, fields=None):
    """Get invitations of an organization.
    
    Parameters
    ----------
    organizationId : str
        Organization ID. Defaults to current if not specified.
    cursor : str
        Cursor for pagination.
    limit : int
        Maximum number of invitations to return.
    fields : list
        List of fields to return, leave empty to get all fields.
    
    Returns
    -------
    list[dict]
        Information about invitations of an organization.
    """
    self.check_logout()
    if organizationId is None: organizationId = self.organization
    if limit is not None and limit <= 100: items = limit
    else: items = 100
    invites = []
    while True:
        if limit and len(invites) + items > limit: items = limit - len(invites)
        ret = self.ana_api.getInvitations(organizationId=organizationId, limit=items, cursor=cursor, fields=fields)
        invites.extend(ret)
        if len(ret) < items or len(invites) == limit: break
        cursor = ret[-1]["email"]
    return invites


def add_organization_member(self, email, role, organizationId=None):
    """Add a user to an existing organization.
    
    Parameters
    ----------
    email: str
        Email of user to add.
    role : str
        Role for user. 
    organizationId : str
        Organization ID to add members too. Uses current if not specified.
    
    Returns
    -------
    str
        Response status if user got added to workspace succesfully. 
    """
    self.check_logout()
    if email is None: raise ValueError("The email parameter is required!")
    if role is None: raise ValueError("The role parameter is required!")
    if organizationId is None: organizationId = self.organization
    return self.ana_api.addMember(email=email, role=role, organizationId=organizationId)


def remove_organization_member(self, email, organizationId=None):
    """Remove a member from an existing organization.
    
    Parameters
    ----------
    email : str
        Member email to remove.
    organizationId: str
        Organization ID to remove member from. Removes from current organization if not specified.
    
    Returns
    -------
    str
        Response status if member got removed from organization succesfully. 
    """
    self.check_logout()
    if email is None: raise ValueError("The email parameter is required!")
    if organizationId is None: organizationId = self.organization
    return self.ana_api.removeMember(email=email, organizationId=organizationId)


def remove_organization_invitation(self, email, organizationId=None):
    """Remove a invitation from an existing organization.
    
    Parameters
    ----------
    email : str
        Invitation email to remove.
    organizationId: str
        Organization ID to remove member from. Removes from current organization if not specified.
    
    Returns
    -------
    str
        Response status if member got removed from organization succesfully. 
    """
    self.check_logout()
    if email is None: raise ValueError("The email parameter is required!")
    if organizationId is None: organizationId = self.organization
    return self.ana_api.removeMember(email=email, organizationId=organizationId)


def edit_organization_member(self, email, role, organizationId=None):
    """Edit a member's role. 
    
    Parameters
    ----------
    email : str
        Member email to edit.
    role: str
        Role to assign. 
    organizationId: str
        Organization ID to remove member from. Edits member in current organization if not specified.
    
    Returns
    -------
    str
        Response if member got edited succesfully. 
    """
    self.check_logout()
    if email is None: raise ValueError("The email parameter is required!")
    if role is None: raise ValueError("The role parameter is required!")
    if organizationId is None: organizationId = self.organization
    return self.ana_api.editMember(email=email, role=role, organizationId=organizationId)
