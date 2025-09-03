"""
UMAP Functions
"""
import os
import requests

def get_umaps(self, umapId=None, datasetId=None, workspaceId=None, cursor=None, limit=None, filters=None, fields=None):
    """Retrieves information about UMAP dataset comparison from the platform.
    
    Parameters
    ----------
    umapId : str
        UMAP Job ID. 
    datasetId : str
        Dataset Id to filter on.
    workspaceId : str
        Workspace ID where the datasets exists.
    cursor : str
        Cursor for pagination.
    limit : int
        Maximum number of umaps to return.
    filters: dict
        Filters that limit output to entries that match the filter 
    fields : list
        List of fields to return, leave empty to get all fields.
    
    Returns
    -------
    dict
        UMAP information.
    """
    self.check_logout()
    if workspaceId is None: workspaceId = self.workspace
    if limit is not None and limit <= 100: items = limit
    else: items = 100
    umaps = []
    while True:
        if limit and len(umaps) + items > limit: items = limit - len(umaps)
        ret = self.ana_api.getUMAPs(umapId=umapId, datasetId=datasetId, workspaceId=workspaceId, limit=items, cursor=cursor, filters=filters, fields=fields)
        umaps.extend(ret)
        if len(ret) < items or len(umaps) == limit: break
        cursor = ret[-1]["umapId"]
    return umaps
    

def create_umap(self, name, datasetIds, samples, description=None, seed=None, tags=None, workspaceId=None):
    """Creates a UMAP dataset comparison job on the platform.
    
    Parameters
    ----------
    datasetIds : [str]
        Dataset ID to retrieve information for. 
    samples : [int]
        Samples to take from each dataset.
    workspaceId : str
        Workspace ID where the datasets exists.
    
    Returns
    -------
    str
        The UMAP Job ID.
    """
    self.check_logout()
    if name is None: raise ValueError("The name parameter is required!")
    if datasetIds is None: raise ValueError("The datasetIds parameter is required!")
    if samples is None: raise ValueError("The samples parameter is required!")
    if len(datasetIds) != len(samples): raise ValueError("The length of datasetIds must match the length of samples.")
    for sample in samples:
        if sample < 5: raise ValueError("The minimum number of samples is 5!")
    if description is None: description = ''
    if seed is None: seed = 0
    if tags is None: tags = []
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.createUMAP(workspaceId=workspaceId, datasetIds=datasetIds, samples=samples, name=name, description=description, seed=seed, tags=tags)


def delete_umap(self, umapId, workspaceId=None):
    """Deletes/cancels a UMAP dataset comparison on the platform.
    
    Parameters
    ----------
    umapId : str
        UMAP Job ID. 
    workspaceId : str
        Workspace ID where the datasets exists.
    
    Returns
    -------
    bool
        Status.
    """
    self.check_logout()
    if umapId is None: raise ValueError("The umapId parameter is required!")
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.deleteUMAP(umapId=umapId, workspaceId=workspaceId)


def edit_umap(self, umapId, name=None, description=None, tags=None, workspaceId=None):
    """Edits a UMAP dataset comparison on the platform.
    
    Parameters
    ----------
    umapId : str
        UMAP Job ID. 
    name : str
        Name of the UMAP.
    description : str
        Description of the UMAP.
    workspaceId : str
        Workspace ID where the datasets exists.
    
    Returns
    -------
    bool
        Status.
    """
    self.check_logout()
    if umapId is None: raise ValueError("The umapId parameter is required!")
    if name is None: name = ""
    if description is None: description = ""
    if workspaceId is None: workspaceId = self.workspace
    if tags is not None and not isinstance(tags, list): raise ValueError("The tags parameter must be a list!")
    if tags is None: tags = []
    return self.ana_api.editUMAP(umapId=umapId, name=name, description=description, tags=tags, workspaceId=workspaceId)