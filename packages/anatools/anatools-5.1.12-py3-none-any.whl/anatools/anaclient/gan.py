"""
GAN Functions
"""


def get_gan_models(self, organizationId=None, workspaceId=None, modelId=None, cursor=None, limit=None, filters=None, fields=None):
    """Retrieve information about GAN models
    
    Parameters
    ----------
    organizationId : str
        Organization ID that owns the models
    workspaceId : str
        Workspace ID that contains the models
    cursor : str
        Cursor for pagination.
    limit : int
        Maximum number of models to return.
    modelId : str
        Model ID to retrieve information for. 
    filters: dict
        Filters that limit output to entries that match the filter
    fields : list
        List of fields to return, leave empty to get all fields.
    
    Returns
    -------
    list[dict]
        GAN Model information.
    """
    self.check_logout()
    if organizationId is None and workspaceId is None: workspaceId = self.workspace
    if limit is not None and limit <= 100: items = limit
    else: items = 100
    gamodels = []
    while True:
        if limit and len(gamodels) + items > limit: items = limit - len(gamodels)
        ret = self.ana_api.getGANModels(organizationId=organizationId, workspaceId=workspaceId, modelId=modelId, limit=items, cursor=cursor, filters=filters, fields=fields)
        gamodels.extend(ret)
        if len(ret) < items or len(gamodels) == limit: break
        cursor = ret[-1]["modelId"]
    return gamodels
    

def get_gan_datasets(self, datasetId=None, gandatasetId=None, workspaceId=None, cursor=None, limit=None, fields=None):
    """Retrieve information about GAN-generated dataset jobs.
    
    Parameters
    ----------
    datasetId : str
        Dataset ID to retrieve information for. 
    gandatasetId : str
        Gan dataset ID to retrieve.
    workspaceId : str
        Workspace ID where the dataset exists.
    cursor : str
        Cursor for pagination.
    limit : int
        Maximum number of datasets to return.
    fields : list
        List of fields to return, leave empty to get all fields.

    Returns
    -------
    list[dict]
        Information about the GAN Datasets in the workspace.
    """
    self.check_logout()
    if workspaceId is None: workspaceId = self.workspace
    if limit is not None and limit <= 100: items = limit
    else: items = 100
    gandatasets = []
    while True:
        if limit and len(gandatasets) + items > limit: items = limit - len(gandatasets)
        ret = self.ana_api.getGANDatasets(workspaceId=workspaceId, datasetId=datasetId, gandatasetId=gandatasetId, limit=items, cursor=cursor, fields=fields)
        gandatasets.extend(ret)
        if len(ret) < items or len(gandatasets) == limit: break
        cursor = ret[-1]["datasetId"]
    return gandatasets


def create_gan_dataset(self, datasetId, modelId, name, description, tags, workspaceId=None):
    """Create a new GAN dataset based off an existing dataset. This will start a new job.
    
    Parameters
    ----------
    modelId : str
        Model ID to use for the GAN.
    datasetId : str
        Dataset ID to input into the GAN. 
    name : str
        Name for the GAN dataset.
    description : str
        Description for the GAN dataset.
    tags : list
        Tags for the GAN dataset.
    workspaceId : str
        Workspace ID where the dataset exists.
    
    Returns
    -------
    str
        The datsetId for the GAN Dataset job.
    """
    self.check_logout()
    if datasetId is None: raise ValueError("The datasetId parameter is required!")
    if modelId is None: raise ValueError("The modelId parameter is required!")
    if name is None: raise ValueError("The name parameter is required!")
    if description is None: description = ''
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.createGANDataset(workspaceId=workspaceId, datasetId=datasetId, modelId=modelId, name=name, description=description, tags=tags)


def delete_gan_dataset(self, datasetId, workspaceId=None):
    """Deletes a GAN dataset job.
    
    Parameters
    ----------
    datasetId : str
        Dataset ID for the GAN dataset. 
    workspaceId : str
        Workspace ID where the dataset exists.
    
    Returns
    -------
    bool
        Returns True if the GAN dataset was successfully deleted.
    """
    self.check_logout()
    if datasetId is None: raise ValueError("The datasetId parameter is required!")
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.deleteGANDataset(workspaceId=workspaceId, datasetId=datasetId)


def upload_gan_model(self, name, description, modelfile, flags=None, tags=None, organizationId=None):
    """Uploades a GAN model to the microservice. The model will be owned by the specified organization.
    If organizationId is not given the model will be owned by that of the analcient.
    
    Parameters
    ----------
    name : str
        A name for model.
    description : str
        Details about the model.
    modelfile : str
        The file of the model - relative to the local directry.
    flags : str
        Parameters for use when running the model.
    tags : list[str]
        Tags for the model.
    organizationId : str
        Id of organization that owns the model, that of the anaclient if not given.
    
    Returns
    -------
    str
        The modelId for the uploaded model.
    """
    import os
    from anatools.anaclient.helpers import multipart_upload_file

    self.check_logout()
    if modelfile is None: raise ValueError("The filename parameter is required!")
    if description is None: description = ''
    if organizationId is None: organizationId = self.organization
    if not os.path.exists(modelfile): raise Exception(f'Could not find file: {modelfile}')
    filesize = os.path.getsize(modelfile)
    fileinfo = self.ana_api.uploadGANModel(organizationId=organizationId, name=name, size=filesize, description=description, flags=flags, tags=tags)
    modelId = fileinfo['modelId']
    parts = multipart_upload_file(modelfile, fileinfo["partSize"], fileinfo["urls"], f"Uploading gan model {modelfile}")
    finalize_success = self.ana_api.uploadGANModelFinalizer(organizationId, fileinfo['uploadId'], fileinfo['key'], parts)
    if not finalize_success: raise Exception(f"Failed to upload dataset {modelfile}.")
    if self.interactive: print(f"\x1b[1K\rUpload completed successfully!", flush=True)
    return modelId


def delete_gan_model(self, modelId):
    """Delete the GAN model and remove access to it from all shared organizations.
    This can only be done by a user in the organization that owns the model.
    
    Parameters
    ----------
    modelId : str
        The ID of a specific GAN model.
    
    Returns
    -------
    bool
        If True, the model was successfully deleted.
    """
    self.check_logout()
    if modelId is None: raise Exception('The modelId parameter is required!')
    return self.ana_api.deleteGANModel(modelId=modelId)


def edit_gan_model(self, modelId, name=None, description=None, flags=None, tags=None):
    """Edits the name, description, and flags of a gan model.
    
    Parameters
    ----------
    modelId: str
        The modelId that will be updated.
    name : str
        The new name of the gan model. Note: this name needs to be unique per organization.
    description : str
        Description of the gan model
    flags : str
        Flags for the model
    tags : list[str]
        Tags for the model
    
    Returns
    -------
    bool
        If True, the model was successfully edited.
    """
    self.check_logout()
    if modelId is None: raise Exception('The modelId parameter is required!')
    if name is None and description is None and flags is None: return True
    return self.ana_api.editGANModel(modelId=modelId, name=name, description=description, flags=flag, tags=tags)


def download_gan_model(self, modelId, localDir=None):
    """Download the gan model file from your organization.
    
    Parameters
    ----------
    modelId : str
       ModelId to download.
    localDir : str
        Path for where to download the gan model. If none is provided, current working directory will be used.
    
    Returns
    -------
    str
        The filepath of the downloaded GAN model.
    """
    import os
    from anatools.lib.download import download_file
    
    self.check_logout()
    if modelId is None: raise Exception('The modelId parameter is required!')
    if localDir is None: localDir = os.getcwd()
    url = self.ana_api.downloadGANModel(modelId=modelId)
    fname = url.split('?')[0].split('/')[-1]
    return download_file(url=url, fname=fname, localDir=localDir) 