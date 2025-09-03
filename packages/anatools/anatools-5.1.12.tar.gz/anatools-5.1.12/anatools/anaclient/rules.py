"""
Rules Functions
"""

def get_platform_rules(self):
    """Get the rules for an organization.
    Returns
    -------
    str
        String of rules for the platform."""
    self.check_logout()
    return self.ana_api.getPlatformRules()


def get_organization_rules(self, organizationId=None):
    """Get the rules for an organization.
    
    Parameters
    ----------
    organizationId : str
        Organization ID of the organization to get the rules for. If not specified, the current organization is used.
    
    Returns
    -------
    str
        String of rules for the organization."""
    self.check_logout()
    if organizationId is None: organizationId = self.organization
    return self.ana_api.getOrganizationRules(organizationId=organizationId)


def get_workspace_rules(self, workspaceId=None):
    """Get the rules for a workspace.
    
    Parameters
    ----------
    workspaceId : str
        Workspace ID of the workspace to get the rules for. If not specified, the current workspace is used.
    
    Returns
    -------
    str
        String of rules for the workspace."""
    self.check_logout()
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.getWorkspaceRules(workspaceId=workspaceId)


def get_service_rules(self, serviceId=None):
    """Get the rules for a service.
    
    Parameters
    ----------
    serviceId : str
        Service ID of the service to get the rules for. If not specified, the current service is used.
    
    Returns
    -------
    str
        String of rules for the service."""
    self.check_logout()
    if serviceId is None: serviceId = self.service
    return self.ana_api.getServiceRules(serviceId=serviceId)


def get_user_rules(self):
    """Get the rules for the current user."""
    self.check_logout()
    return self.ana_api.getUserRules()
    

def edit_organization_rules(self, rules, organizationId=None):
    """Edit the rules for an organization.
    
    Parameters
    ----------
    organizationId : str
        Organization ID of the organization to edit the rules for. If not specified, the current organization is used.
    rules : str
        String of rules to edit for the organization."""
    self.check_logout()
    if organizationId is None: organizationId = self.organization
    if type(rules) is not str: raise Exception('Rules parameter must be a string.')
    return self.ana_api.editOrganizationRules(organizationId=organizationId, rules=rules)
    

def edit_workspace_rules(self, rules, workspaceId=None):
    """Edit the rules for a workspace.
    
    Parameters
    ----------
    workspaceId : str
        Workspace ID of the workspace to edit the rules for. If not specified, the current workspace is used.
    rules : str
        String of rules to edit for the workspace."""
    self.check_logout()
    if workspaceId is None: workspaceId = self.workspace
    if type(rules) is not str: raise Exception('Rules parameter must be a string.')
    return self.ana_api.editWorkspaceRules(workspaceId=workspaceId, rules=rules)


def edit_service_rules(self, rules, serviceId):
    """Edit the rules for a service.
    
    Parameters
    ----------
    serviceId : str
        Service ID of the service to edit the rules for. If not specified, the current service is used.
    rules : str
        String of rules to edit for the service."""
    self.check_logout()
    if type(rules) is not str: raise Exception('Rules parameter must be a string.')
    return self.ana_api.editServiceRules(serviceId=serviceId, rules=rules)
    

def edit_user_rules(self, rules):
    """Edit the rules for the current user.
    
    Parameters
    ----------
    rules : str
        String of rules to edit for the user."""
    self.check_logout()
    if type(rules) is not str: raise Exception('Rules parameter must be a string.')
    return self.ana_api.editUserRules(rules=rules)