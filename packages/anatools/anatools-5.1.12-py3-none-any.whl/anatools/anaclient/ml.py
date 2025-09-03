"""
Machine Learning Functions
"""

def get_ml_architectures(self, fields=None):
    """Retrieves the machine learning model architectures available on the platform.
    
    Parameters
    ----------
    fields : list[str], optional
        The fields to retrieve from the response.
    
    Returns
    -------
    dict
        Machine learning model architectures
    """
    self.check_logout()
    return self.ana_api.getMLArchitectures(fields=fields)


def get_ml_models(self, workspaceId=None, datasetId=None, modelId=None, cursor=None, limit=100, filters=None, fields=None):
    """Retrieves the machine learning model architectures available on the platform.
    
    Parameters
    ----------
    workspaceId : str
        Workspace ID
    datasetId : str
        Dataset ID
    modelId : str
        Model ID
    cursor : str, optional
        Cursor for pagination
    limit : int, optional
        Maximum number of ml models to return
    filters: dict
        Filters that limit output to entries that match the filter 
    fields : list[str], optional
        The fields to retrieve from the response.

    Returns
    -------
    dict
        Machine learning model architectures
    """
    self.check_logout()
    if workspaceId is None: workspaceId = self.workspace
    if limit is not None and limit <= 100: items = limit
    else: items = 100
    models = []
    while True:
        if limit and len(models) + items > limit: items = limit - len(models)
        ret = self.ana_api.getMLModels(workspaceId=workspaceId, datasetId=datasetId, modelId=modelId, limit=items, cursor=cursor, filters=filters, fields=fields)
        models.extend(ret)
        if len(ret) < items or len(models) == limit: break
        cursor = ret[-1]["modelId"]
    return models


def create_ml_model(self, datasetId, architectureId, name, parameters, description=None, tags=None, workspaceId=None):
    """Creates a new machine learning model.
    
    Parameters
    ----------
    architectureId : str
        Architecture ID
    datasetId : str
        Dataset ID
    name : str
        Model name
    description : str
        Model description
    paramters : str
        JSON string of model parameters
    workspaceId : str
        Workspace ID

    Returns
    -------
    str
        Machine learning model ID
    """
    self.check_logout()
    if workspaceId is None: workspaceId = self.workspace
    if datasetId is None: raise ValueError("The datasetId parameter is required!")
    if architectureId is None: raise ValueError("The architectureId parameter is required!")
    if name is None: raise ValueError("The name parameter is required!")
    if parameters is None: raise ValueError("The parameters parameter is required!")
    if description is None: description = ''
    if tags is None: tags = []
    return self.ana_api.createMLModel(workspaceId=workspaceId, datasetId=datasetId, architectureId=architectureId, name=name, description=description, parameters=parameters, tags=tags)


def delete_ml_model(self, modelId, workspaceId=None):
    """Deletes or cancels a machine learning training job.
    
    Parameters
    ----------
    modelId : str
        Model ID
    workspaceId : str
        Workspace ID

    Returns
    -------
    bool
        Returns True if successful
    """
    self.check_logout()
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.deleteMLModel(workspaceId=workspaceId, modelId=modelId)


def edit_ml_model(self, modelId, name=None, description=None, tags=None, workspaceId=None):
    """Edit the name or description of a machine learning model.
    
    Parameters
    ----------
    modelId : str
        Model ID
    name : str
        Model name
    description : str
        Model description
    tags : list[str]
        Model tags
    workspaceId : str
        Workspace ID

    Returns
    -------
    bool
        Returns True if successful
    """
    self.check_logout()
    if workspaceId is None: workspaceId = self.workspace
    if name is None and description is None and tags is None: return True
    return self.ana_api.editMLModel(workspaceId=workspaceId, modelId=modelId, name=name, description=description, tags=tags)


def download_ml_model(self, modelId, checkpoint=None, localDir=None, workspaceId=None):
    """Download the machine learning model.
    
    Parameters
    ----------
    modelId : str
        Model ID
    checkpoint : str
        Checkpoint to download. If not specified, the final model will be downloaded
    localDir : str
        Local directory to save the model
    workspaceId : str
        Workspace ID

    Returns
    -------
    str
        Returns the filename of the downloaded model
    """
    import os
    from anatools.lib.download import download_file

    self.check_logout()
    if modelId is None: raise Exception('modelId must be specified.')
    if localDir is None: localDir = os.getcwd()
    if workspaceId is None: workspaceId = self.workspace
    url = self.ana_api.downloadMLModel(workspaceId=workspaceId, modelId=modelId, checkpoint=checkpoint)
    fname = url.split('?')[0].split('/')[-1]
    return download_file(url=url, fname=fname, localDir=localDir) 


def upload_ml_model(self, name, modelfile, architectureId, description=None, tags=None, workspaceId=None):
    """Upload a machine learning model.
    
    Parameters
    ----------
    name : str
        Model name
    modelfile : str
        The filepath of the compressed file containing the model, classes and spec.
    architectureId : str
        Architecture ID
    description : str
        Model description
    tags : list[str]
        Model tags
    workspaceId : str
        Workspace ID

    Returns
    -------
    bool
        Success / failure
    """
    import os
    from anatools.anaclient.helpers import multipart_upload_file

    self.check_logout()
    if name is None: raise ValueError("The name parameter is required!")
    if modelfile is None: raise ValueError("The filename parameter is required!")
    if architectureId is None: raise ValueError("The architectureId parameter is required!")
    if description is None: description = ''
    if tags is None: tags = []
    if workspaceId is None: workspaceId = self.workspace
    filesize = os.path.getsize(modelfile)
    fileinfo = self.ana_api.uploadMLModel(workspaceId=workspaceId, architectureId=architectureId, name=name, size=filesize, description=description, tags=tags)
    modelId = fileinfo['modelId']
    parts = multipart_upload_file(modelfile, fileinfo["partSize"], fileinfo["urls"], f"Uploading ml model {modelfile}")
    self.check_logout()
    finalize_success = self.ana_api.uploadMLModelFinalizer(workspaceId=workspaceId, uploadId=fileinfo['uploadId'], key=fileinfo['key'], parts=parts)
    if not finalize_success: raise Exception(f"Failed to upload dataset {modelfile}.")
    if self.interactive: print(f"\x1b[1K\rUpload completed successfully!", flush=True)
    return modelId


def get_ml_inferences(self, workspaceId=None, inferenceId=None, datasetId=None, modelId=None, cursor=None, limit=None, filters=None, fields=None):
    """Get the inferences of a machine learning model.
    
    Parameters
    ----------
    inferenceId : str
        Inference ID
    datasetId : str
        Dataset ID
    modelId : str
        Model ID
    workspaceId : str
        Workspace ID
    cursor : str
        Cursor for pagination
    limit : int
        Maximum number of inferences to return
    filters: dict
        Filters that limit output to entries that match the filter 
    fields : list
        List of fields to return, leave empty to get all fields.

    Returns
    -------
    dict
        Inference data
    """
    self.check_logout()
    if workspaceId is None: workspaceId = self.workspace
    if limit is not None and limit <= 100: items = limit
    else: items = 100
    inferences = []
    while True:
        if limit and len(inferences) + items > limit: items = limit - len(inferences)
        ret = self.ana_api.getMLInferences(workspaceId=workspaceId, inferenceId=inferenceId, datasetId=datasetId, modelId=modelId, limit=limit, cursor=cursor, filters=filters, fields=fields)
        inferences.extend(ret)
        if len(ret) < items or len(inferences) == limit: break
        cursor = ret[-1]["inferenceId"]
    return inferences


def get_ml_inference_metrics(self, inferenceId, workspaceId=None):
    """Get the metrics from an inference job.
    
    Parameters
    ----------
    inferenceId : str
        Inference ID
    workspaceId : str
        Workspace ID
    
    Returns
    -------
    dict
        Metric data
    """
    self.check_logout()
    if inferenceId is None: raise ValueError("The inferenceId parameter is required!")
    if workspaceId is None: workspaceId = self.workspace
    metrics = self.ana_api.getMLInferenceMetrics(workspaceId=workspaceId, inferenceId=inferenceId)
    return json.loads(metrics)


def create_ml_inference(self, datasetId, modelId, mapId=None, tags=None, workspaceId=None):
    """Create a new machine learning inference job.
    
    Parameters
    ----------
    datasetId : str
        Dataset ID
    modelId : str
        Model ID
    mapId : str
        Map ID
    workspaceId : str
        Workspace ID
    
    Returns
    -------
    str
        Inference ID
    """
    self.check_logout()
    if datasetId is None: raise ValueError("The datasetId parameter is required!")
    if modelId is None: raise ValueError("The modelId parameter is required!")
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.createMLInference(workspaceId=workspaceId, datasetId=datasetId, modelId=modelId, mapId=mapId, tags=tags)


def delete_ml_inference(self, inferenceId, workspaceId=None):
    """Deletes or cancels a machine learning inference job.
    
    Parameters
    ----------
    inferenceId : str
        Inference ID
    workspaceId : str
        Workspace ID
    
    Returns
    -------
    bool
        Returns True if successful
    """
    self.check_logout()
    if inferenceId is None: raise ValueError("The inferenceId parameter is required!")
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.deleteMLInference(workspaceId, inferenceId)


def edit_ml_inference(self, inferenceId, tags=None, workspaceId=None):
    """Edit the tags of a machine learning inference job.
    
    Parameters
    ----------
    inferenceId : str
        Inference ID
    tags : list[str]
        Tags to add or remove
    workspaceId : str
        Workspace ID
    
    Returns
    -------
    bool
        Returns True if successful
    """
    self.check_logout()
    if inferenceId is None: raise ValueError("The inferenceId parameter is required!")
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.editMLInference(workspaceId, inferenceId, tags)


def download_ml_inference(self, inferenceId, localDir=None, workspaceId=None):
    """Download the inference detections.
    
    Parameters
    ----------
    inferencId : str
        Inference ID
    localDir : str
        Local directory to save the model
    workspaceId : str
        Workspace ID
    
    Returns
    -------
    str
        Returns the filename of the downloaded model
    """
    import os
    from anatools.lib.download import download_file

    self.check_logout()
    if inferenceId is None: raise Exception('The inferenceId parameter is required!')
    if localDir is None: localDir = os.getcwd()
    if workspaceId is None: workspaceId = self.workspace
    url = self.ana_api.downloadMLInference(workspaceId=workspaceId, inferenceId=inferenceId)
    fname = url.split('?')[0].split('/')[-1]
    return download_file(url=url, fname=fname, localDir=localDir) 