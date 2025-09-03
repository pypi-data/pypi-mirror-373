"""
Staged Graphs Functions
"""

def get_preview(self, previewId, workspaceId=None, fields=None):
    """Queries the preview job run in the workspace. 
    
    Parameters
    ----------
    previewId : str
        The unique identifier for the preview job.
    workspaceId : str    
        Workspace the preview job was run in. If none is provided, the default workspace will get used.
    fields : list
        List of fields to return, leave empty to get all fields.
    
    Returns
    -------
    dict
        Job run information.
    """
    if self.check_logout(): return
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.getPreview(workspaceId=workspaceId, previewId=previewId, fields=fields)



def create_preview(self, graphId, workspaceId=None):
    """Creates a preview job.
    
    Parameters
    ----------
    graphId: str
        The unique identifier for the graph.
    workspaceId : str    
        Workspace ID create the preview in. If none is provided, the default workspace will get used. 
    
    Returns
    -------
    str
        The unique identifier for the preview job.
    """
    if self.check_logout(): return
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.createPreview(workspaceId=workspaceId, graphId=graphId)
    