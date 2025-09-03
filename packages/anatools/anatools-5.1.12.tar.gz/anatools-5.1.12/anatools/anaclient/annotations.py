"""
Annotations Functions
"""


def get_annotation_formats(self):
    """Retrieves the annotation formats supported by the Rendered.ai Platform.
    
    Returns
    -------
    list[str]
        The annotation formats supported.
    """
    if self.check_logout(): return
    return self.ana_api.getAnnotationFormats()


def get_annotation_maps(self, organizationId=None, workspaceId=None, mapId=None, cursor=None, limit=None, filters=None, fields=None):
    """Retrieves annotation map information. If neither organizationId or workspaceId are specified, it will use the current workspace.
    
    Parameters
    ----------
    organizationId : str
        Organization ID to retrieve maps for.
    workspaceId: str
        Workspace ID to retrieve maps for.
    mapId: str
        Annotation map ID to retrieve.
    cursor: str
        Cursor for pagination.
    limit: int
        Maximum number of maps to return.
    filters: dict
        Filters that limit output to entries that match the filter
    fields: list[str]
        List of fields to return, leave empty to get all fields.
    
    Returns
    -------
    list[dict]
        The requested annotation maps.
    """
    self.check_logout()
    if organizationId is None and workspaceId is None: workspaceId = self.workspace
    if limit is not None and limit <= 100: items = limit
    else: items = 100
    maps = []
    while True:
        if limit and len(maps) + items > limit: items = limit - len(maps)
        ret = self.ana_api.getAnnotationMaps(organizationId=organizationId, workspaceId=workspaceId, mapId=mapId, limit=items, cursor=cursor, filters=filters, fields=fields)
        maps.extend(ret)
        if len(ret) < items or len(maps) == limit: break
        cursor = ret[-1]["mapId"]
    return maps


def get_annotations(self, datasetId=None, annotationId=None, workspaceId=None, cursor=None, limit=None, filters=None, fields=None):
    """Retrieve information about existing annotations generated for a dataset.
    
    Parameters
    ----------
    datasetId : str
        Dataset ID to generate annotations for.
    annotationId : str
        Annotation ID for a specific annotations job.
    workspaceId: str
        Workspace ID where the annotations exist. If none is provided, the current workspace will get used.
    cursor: str
        Cursor for pagination.
    limit: int
        Maximum number of annotations to return.
    filters: dict
        Filters that limit output to entries that match the filter.
    fields: list[str]
        List of fields to return, leave empty to get all fields.
    
    Returns
    -------
    list[dict]
        Annotation information.
    """
    self.check_logout()
    if workspaceId is None: workspaceId = self.workspace
    if limit is not None and limit <= 100: items = limit
    else: items = 100
    annotations = []
    while True:
        if limit and len(annotations) + items > limit: items = limit - len(annotations)
        ret = self.ana_api.getAnnotations(workspaceId=workspaceId, datasetId=datasetId, annotationId=annotationId, limit=items, cursor=cursor, filters=filters, fields=fields)
        annotations.extend(ret)
        if len(ret) < items or len(annotations) == limit: break
        cursor = ret[-1]["annotationId"]
    return annotations
    

def create_annotation(self, datasetId, format, mapId=None, tags=None, workspaceId=None):
    """Generates annotations for an existing dataset. 
    
    Parameters
    ----------
    datasetId : str
        Dataset ID to generate annotation for.
    format : str
        Annotation format to use.
    mapId: str
        The ID of the map file used for annotations.
    tags: list[str]
        Tags to apply to the annotation.
    workspaceId: str
        Workspace ID of the dataset to generate annotation for. If none is provided, the current workspace will get used. 
    
    Returns
    -------
    str
        The annotationsId for the annotation job.
    """
    self.check_logout()
    if workspaceId is None: workspaceId = self.workspace
    if datasetId is None: raise ValueError("The datasetId parameter is required!")
    if format is None: raise ValueError("The format parameter is required!")
    if tags is None: tags = []
    return self.ana_api.createAnnotation(workspaceId=workspaceId, datasetId=datasetId, format=format, mapId=mapId, tags=tags)
    

def download_annotation(self, annotationId, workspaceId=None):
    """Downloads annotations archive.
    
    Parameters
    ----------
    datasetId : str
        Dataset ID to download image annotation for.
    annotationId : str
        Id of previously generated image annotation. 
    workspaceId: str
        Workspace ID of the dataset to generate annotation for. If none is provided, the current workspace will get used. 
    
    Returns
    -------
    str
        The name of the archive file that got downloaded.
    """
    import requests

    self.check_logout()
    if workspaceId is None: workspaceId = self.workspace
    if annotationId is None: raise ValueError("The annotationId parameter is required!")
    url = self.ana_api.downloadAnnotation(workspaceId=workspaceId, annotationId=annotationId)
    fname = url.split('?')[0].split('/')[-1]
    with requests.get(url, stream=True) as downloadresponse:
        with open(fname, 'wb') as outfile:
            downloadresponse.raise_for_status()
            outfile.write(downloadresponse.content)
            with open(fname, 'wb') as f:
                for chunk in downloadresponse.iter_content(chunk_size=8192):
                    f.write(chunk)
    return fname


def delete_annotation(self, annotationId, workspaceId=None):
    """Delete a dataset annotation.
    
    Parameters
    ----------
    annotationId : str
        AnnoationId of the annotation job.
    workspaceId: str
        Workspace ID of the dataset to generate annotation for. If none is provided, the current workspace will get used. 
    
    Returns
    -------
    bool
        If true, successfully deleted the annotation.
    """
    self.check_logout()
    if workspaceId is None: workspaceId = self.workspace
    if annotationId is None: raise ValueError("The annotationId parameter is required!")
    return self.ana_api.deleteAnnotation(workspaceId=workspaceId, annotationId=annotationId)


def edit_annotation(self, annotationId, tags=None, workspaceId=None):
    """Edits annotations for a dataset.
    
    Parameters
    ----------
    annotationId : str
        Annotation ID for the annotation to edit. 
    tags : list[str]
        Tags for the annotation job.
    workspaceId: str
        Workspace ID where the annotation exist. If none is provided, the current workspace will get used. 
    
    Returns
    -------
    bool
        If true, successfully edited the annotation.
    """
    self.check_logout()
    if annotationId is None: raise ValueError("The annotationId parameter is required!")
    if not isinstance(tags, list): raise ValueError("The tags parameter must be a list!")
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.editAnnotation(workspaceId=workspaceId, annotationId=annotationId, tags=tags)


def create_annotation_map(self, name, description, mapfile, organizationId=None):
    """Uploades an annotation map to the microservice. The map will be owned by the specified organization.
    If not organizationId is given the model will be owned by that of the analcient.
    
    Parameters
    ----------
    name : str
        A name for map.
    description : str
        Details about the map.
    mapfile : str
        The map file - relative to the local directry.
    organizationId : str
        Id of organization that owns the map, that of the anaclient if not given.
    
    Returns
    -------
    mapId : str
        The unique identifier for this map.
    """
    import os
    import requests

    self.check_logout()
    if organizationId is None: organizationId = self.organization
    if name is None: raise ValueError("The name parameter is required!")
    if description is None: raise ValueError("The description parameter is required!")
    if mapfile is None: raise ValueError("The mapfile parameter is required!")
    if not os.path.exists(mapfile): raise Exception("File not found in " + os.getcwd())
    fileinfo = self.ana_api.createAnnotationMap(organizationId=organizationId, name=name, description=description)
    with open(mapfile, 'rb') as filebytes:
        files = {'file': filebytes}
        data = {
            "key":                  fileinfo['fields']['key'],
            "bucket":               fileinfo['fields']['bucket'],
            "X-Amz-Algorithm":      fileinfo['fields']['algorithm'],
            "X-Amz-Credential":     fileinfo['fields']['credential'],
            "X-Amz-Date":           fileinfo['fields']['date'],
            "X-Amz-Security-Token": fileinfo['fields']['token'],
            "Policy":               fileinfo['fields']['policy'],
            "X-Amz-Signature":      fileinfo['fields']['signature'],
        }
        requests.post(fileinfo['url'], data=data, files=files)
        if self.interactive: print('Map file uploaded to the Rendered.ai Platform.', flush=True)
    return fileinfo['mapId']


def edit_annotation_map(self, mapId, name=None, description=None, tags=None):
    """Edits the name, description or tags of a map file.
    
    Parameters
    ----------
    mapId: str
        The mapId that will be updated.
    name : str
        The new name of the annotation map. Note: this name needs to be unique per organization.
    description : str
        Description of the annotation map.
    tags : list[str]
        Tags to apply to the map.
    
    Returns
    -------
    bool
        Returns True if the map was edited.
    """
    self.check_logout()
    if mapId is None: raise Exception('The mapId parameter is required!')
    if name is None and description is None and tags is None: return True
    return self.ana_api.editAnnotationMap(mapId=mapId, name=name, description=description, tags=tags)


def delete_annotation_map(self, mapId):
    """Deletes the annotation map.
    
    Parameters
    ----------
    mapId : str
        The ID of a specific Map to delete.
    
    Returns
    -------
    bool
        Returns True if the map was deleted.
    """
    self.check_logout()
    if mapId is None: raise Exception('The mapId parameter is required!')
    return self.ana_api.deleteAnnotationMap(mapId=mapId)


def download_annotation_map(self, mapId, localDir=None):
    """Download the annotation map file from your organization.
    
    Parameters
    ----------
    mapId : str
       MapId to download.
    localDir : str
        Path for where to download the annotation map. If none is provided, current working directory will be used.
    
    Returns
    -------
    str
        The name of the map file that got downloaded.
    """
    from anatools.lib.download import download_file
    import os

    self.check_logout()
    if mapId is None: raise Exception('The mapId parameter is required!')
    if localDir is None: localDir = os.getcwd()
    url = self.ana_api.downloadAnnotationMap(mapId=mapId)
    fname = url.split('?')[0].split('/')[-1]
    return download_file(url=url, fname=fname, localDir=localDir) 
    