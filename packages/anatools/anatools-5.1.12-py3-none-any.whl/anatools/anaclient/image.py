"""
Image Functions
"""

def get_image_annotation(self, datasetId, filename, workspaceId=None, fields=None):
    """Retrieves the annotation for an image.
    
    Parameters
    ----------
    workspaceId: str
        Workspace ID containing the image. If not specified then the current workspace is used.
    datasetId: str
        Dataset ID containing the image
    filename
        Name of the image file the annotation is for
    
    Returns
    -------
    dict
        Annotation information for the specified image.
    """
    self.check_logout()
    if datasetId is None: raise ValueError("The datasetId parameter is required!")
    if filename is None: raise ValueError("The filename parameter is required!")
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.getImageAnnotation(workspaceId, datasetId, filename, fields=fields)


def get_image_mask(self, datasetId, filename, workspaceId=None, fields=None):
    """Retrieves the mask for an image.
    
    Parameters
    ----------
    workspaceId: str
        Workspace ID containing the image. If not specified then the default
        workspace is used.
    datasetId: str
        Dataset ID containing the image
    filename
        Name of the image file the mask is for
    
    Returns
    -------
    dict
        Mask information for the specified image.
    """
    self.check_logout()
    if datasetId is None: raise ValueError("The datasetId parameter is required!")
    if filename is None: raise ValueError("The filename parameter is required!")
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.getImageMask(workspaceId, datasetId, filename, fields=fields)


def get_image_metadata(self, datasetId, filename, workspaceId=None, fields=None):
    """Retrieves the metadata for an image.
    
    Parameters
    ----------
    workspaceId: str
        Workspace ID containing the image. If not specified then the default
        workspace is used.
    datasetId: str
        Dataset ID containing the image
    filename
        Name of the image file the metadata is for
    
    Returns
    -------
    dict
        Metadata information for the specified image.
    """
    self.check_logout()
    if datasetId is None: raise ValueError("The datasetId parameter is required!")
    if filename is None: raise ValueError("The filename parameter is required!")
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.getImageMetadata(workspaceId, datasetId, filename, fields=fields)
