"""
Dataset Functions
"""

def get_datasets(self, datasetId=None, workspaceId=None, filters=None, cursor=None, limit=None, fields=None):
    """Queries the workspace datasets based off provided parameters.
    
    Parameters
    ----------
    datasetId : str
        Dataset ID to filter.
    workspaceId : str
        Workspace ID of the dataset's workspace. If none is provided, the current workspace will get used. 
    filters: dict
        Filters items that match the filter
    cursor : str
        Cursor for pagination.
    limit : int
        Maximum of datasets to return.
    fields : list
        List of fields to return, leave empty to get all fields.
    
    Returns
    -------
    list[dict]
        Information about the dataset based off the query parameters. 
    """
    self.check_logout()
    if workspaceId is None: workspaceId = self.workspace
    if limit is not None and limit <= 100: items = limit
    else: items = 100
    datasets = []
    while True:
        if limit and len(datasets) + items > limit: items = limit - len(datasets)
        ret = self.ana_api.getDatasets(workspaceId=workspaceId, datasetId=datasetId, limit=items, cursor=cursor, filters=filters, fields=fields)
        datasets.extend(ret)
        if len(ret) < items or len(datasets) == limit: break
        cursor = ret[-1]["datasetId"]
    return datasets


def get_dataset_jobs(self, organizationId=None, workspaceId=None, datasetId=None, cursor=None, limit=None, filters=None, fields=None):
    """Queries the organization or workspace for active dataset jobs based off provided parameters. 
    If neither organizationId or workspaceId is provided, the current workspace will get used.
    
    Parameters
    ----------
    organizationId : str
        Queries an organization for active dataset jobs.
    workspaceId : str
        Queries a workspace for active dataset jobs.
    datasetId : str
        Dataset ID to filter.
    cursor : str
        Cursor for pagination.
    limit : int
        Maximum number of dataset jobs to return.
    filters : dict
        Filters items that match the filter
    fields : list
        List of fields to return, leave empty to get all fields.

    Returns
    -------
    str
        Information about the active dataset jobs. 
    """
    self.check_logout()
    if organizationId is None and workspaceId is None: workspaceId = self.workspace
    if limit is not None and limit <= 100: items = limit
    else: items = 100
    jobs = []
    while True:
        if limit and len(jobs) + items > limit: items = limit - len(jobs)
        ret = self.ana_api.getDatasetJobs(organizationId=organizationId, workspaceId=workspaceId, datasetId=datasetId, limit=items, cursor=cursor, filters=filters, fields=fields)
        jobs.extend(ret)
        if len(ret) < items or len(jobs) == limit: break
        cursor = ret[-1]["datasetId"]
    return jobs


def create_dataset(self, name, graphId, description='', runs=1, priority=1, seed=1, tags=[], workspaceId=None):
    """Create a new synthetic dataset using a graph in the workspace. This will start a new dataset job in the workspace.
    
    Parameters
    ----------
    name: str
        Name for dataset. 
    graphId : str
        ID of the graph to create dataset from.
    description : str 
        Description for new dataset.
    runs : int
        Number of times a channel will run within a single job. This is also how many different images will get created within the dataset. 
    priority : int
        Job priority.
    seed : int
        Seed number.
    tags : list[str]
        Tags for new dataset.
    workspaceId : str
        Workspace ID of the staged graph's workspace. If none is provided, the current workspace will get used. 
    
    Returns
    -------
    str
        Success or failure message about dataset creation.
    """
    self.check_logout()
    if name is None: raise ValueError("The name parameter is required!")
    if graphId is None: raise ValueError("The graphId parameter is required!")
    if description is None: description = ''
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.createDataset(workspaceId=workspaceId, graphId=graphId, name=name, description=description, runs=runs, seed=seed, priority=priority, tags=tags)


def edit_dataset(self, datasetId, description=None, name=None, pause=None, priority=None, tags=None, workspaceId=None):
    """Update dataset properties.
    
    Parameters
    ----------
    datasetId : str
        Dataset ID to edit the name, description or tags for.
    name: str
        New name for dataset.
    description : str 
        New description.
    tags : list
        New tags for dataset.
    pause : bool
        Pauses the dataset job if it is running.
    priority : int
        New priority for dataset job (1-3).
    workspaceId : str
        Workspace ID of the dataset to get updated. If none is provided, the current workspace will get used. 
    
    Returns
    -------
    bool
        Returns True if the dataset was updated successfully.
    """
    self.check_logout()
    if datasetId is None: raise ValueError("The datasetId parameter is required!")
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.editDataset(workspaceId=workspaceId, datasetId=datasetId, name=name, description=description, pause=pause, priority=priority, tags=tags)
    

def delete_dataset(self, datasetId, workspaceId=None):
    """Delete an existing dataset.
    
    Parameters
    ----------
    datasetId : str
        Dataset ID of dataset to delete.
    workspaceId : str
        Workspace ID that the dataset is in. If none is provided, the current workspace will get used. 
    
    Returns
    -------
    bool
        Returns True if the dataset was deleted successfully.
    """
    self.check_logout()
    if datasetId is None: raise ValueError("The datasetId parameter is required!")
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.deleteDataset(workspaceId=workspaceId, datasetId=datasetId)
    

def download_dataset(self, datasetId, workspaceId=None, localDir=None):
    """Download a dataset.
    
    Parameters
    ----------
    datasetId : str
        Dataset ID of dataset to download.
    workspaceId : str
        Workspace ID that the dataset is in. If none is provided, the default workspace will get used. 
    localDir : str
        Path for where to download the dataset. If none is provided, current working directory will be used.
        
    Returns
    -------
    str
        Returns the path the dataset was downloaded to.
    """
    from anatools.lib.download import download_file

    self.check_logout()
    if datasetId is None: raise ValueError("The datasetId parameter is required!")
    if workspaceId is None: workspaceId = self.workspace    
    url = self.ana_api.downloadDataset(workspaceId=workspaceId, datasetId=datasetId)        
    fname = self.ana_api.getDatasets(workspaceId=workspaceId, datasetId=datasetId)[0]['name'] + '.zip'
    return download_file(url=url, fname=fname, localDir=localDir) 


def cancel_dataset(self, datasetId, workspaceId=None):
    """Stop a running job.
    
    Parameters
    ----------
    datasetId : str
        Dataset ID of the running job to stop.
    workspaceId: str
        Workspace ID of the running job. If none is provided, the default workspace will get used. 
    
    Returns
    -------
    bool
        Returns True if the job was cancelled successfully.
    """
    self.check_logout()
    if datasetId is None: raise ValueError("The datasetId parameter is required!")
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.cancelDataset(workspaceId=workspaceId, datasetId=datasetId)


def upload_dataset(self, filename, description=None, tags=None, workspaceId=None):
    """Uploads a compressed file to the datasets library in the workspace.
    
    Parameters
    ----------
    filename: str
        Path to the dataset folder or file for uploading. Must be zip or tar file types.
    workspaceId : str
        WorkspaceId to upload dataset to. Defaults to current.
    description : str
        Description for new dataset.
    
    Returns
    -------
    str
        The unique identifier for this dataset.
    """
    import os
    from anatools.anaclient.helpers import multipart_upload_file

    self.check_logout()
    if filename is None: raise ValueError("Filename must be defined.")
    if description is None: description = ''
    if workspaceId is None: workspaceId = self.workspace
    if os.path.splitext(filename)[1] not in ['.zip', '.tar', '.gz']: raise Exception('Dataset upload is only supported for zip, tar, and tar.gz files.')
    if not os.path.exists(filename): raise Exception(f'Could not find file: {filename}')
    filesize = os.path.getsize(filename)
    fileinfo = self.ana_api.datasetUpload(workspaceId=workspaceId, filename=filename, filesize=filesize, description=description, tags=tags)
    datasetId = fileinfo['datasetId']
    parts = multipart_upload_file(filename, fileinfo["partSize"], fileinfo["urls"], f"Uploading dataset {filename}")
    finalize_success = self.ana_api.datasetUploadFinalizer(workspaceId, fileinfo['uploadId'], fileinfo['key'], parts)
    if not finalize_success: raise Exception(f"Failed to upload dataset {filename}.")
    if self.interactive: print(f"\x1b[1K\rUpload completed successfully!", flush=True)
    return datasetId


def get_dataset_runs(self, datasetId, state=None, workspaceId=None, fields=None):
    """Shows all dataset run information to the user. Can filter by state.
    
    Parameters
    ----------
    datasetId: str
        The dataset to retrieve logs for.
    state: str
        Filter run list by status.
    workspaceId : str
        The workspace the dataset is in.
    fields : list
        List of fields to return, leave empty to get all fields.
    
    Returns
    -------
    list[dict]
        List of run associated with datasetId.
    """
    self.check_logout()
    if datasetId is None: raise ValueError("The datasetId parameter is required!")
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.getDatasetRuns(workspaceId=workspaceId, datasetId=datasetId, state=state, fields=fields)
                

def get_dataset_log(self, datasetId, runId, saveLogFile=False, workspaceId=None, fields=None):
    """Shows dataset log information to the user.
    
    Parameters
    ----------
    datasetId: str
        The dataset the run belongs to.
    runId: str
        The run to retrieve the log for.
    saveLogFile: bool
        If True, saves log file to current working directory.
    workspaceId: str
        The workspace the run belongs to.
    fields : list
        List of fields to return, leave empty to get all fields.
    
    Returns
    -------
    list[dict]
        Get log information by runId
    """
    import json 

    self.check_logout()
    if datasetId is None: raise ValueError("The datasetId parameter is required!")
    if runId is None: raise ValueError("The runId parameter is required!")
    if workspaceId is None: workspaceId = self.workspace
    log = self.ana_api.getDatasetLog(workspaceId=workspaceId, datasetId=datasetId, runId=runId, fields=fields)
    if saveLogFile and 'log' in log:
        with open (f"{datasetId}-{log['run']}.log",'w+') as logfile:
            for line in json.loads(log['log']): logfile.write(f"{line['message']}\n")
        if self.interactive: print(f"Saved log to {datasetId}-{log['run']}.log")
    else: return log


def get_dataset_files(self, datasetId, path=None, workspaceId=None, cursor=None, limit=100):
    """Gets a list of files that are contained in the specified dataset 
    
    Parameters
    ----------
    datasetId : str
        Dataset ID to filter.
    path : str 
        Directory path in the dataset, e.g. "images"   
    workspaceId : str
        Workspace ID of the dataset's workspace. If none is provided, the current workspace will get used.
    cursor : str
        Cursor for pagination.
    limit : int
        Maximum number of files to retrieve.
    
    Returns
    -------
    [str]
        List of file names. 
    """
    if self.check_logout(): return
    if datasetId is None: raise ValueError("The datasetId parameter is required!")
    if workspaceId is None: workspaceId = self.workspace
    if limit is not None and limit <= 100: items = limit
    else: items = 100
    files = []
    while True:
        if limit and len(files) + items > limit: items = limit - len(files)
        ret = self.ana_api.getDatasetFiles(workspaceId=workspaceId, datasetId=datasetId, path=path, limit=items, cursor=cursor)
        files.extend(ret)
        if len(ret) < items or len(files) == limit: break
        cursor = ret[-1]
    return files
                

def create_mixed_dataset(self, name, parameters, description='', seed=None, tags=None, workspaceId=None):
    """Creates a new datasts using the samples provided in the parameters dict. The dict must be defined by:
        {
            "datasetId1": {"samples": <int>, "classes": [<class1>, class2>, ...]},
            "datasetId2": {"samples": <int>},
            ...
        }
    
    Parameters
    ----------
    name: str
        The name of the new mixed dataset
    parameters: dict
        A dictionary of datasetId keys with values of {"samples": <int>, "classes": [<class1>, class2], ...}
    description: str
        Description for new dataset.
    seed: int
        The seed for the mixed dataset, used to set the random seed.
    tags: list[str]
        A list of tags to apply to the new dataset.
    workspaceId: str
        The workspace the dataset is in.
    
    Returns
    -------
    str
        The dataset ID of the new mixed dataset.
    """
    import json 

    if self.check_logout(): return
    if workspaceId is None: workspaceId = self.workspace
    if name is None: raise ValueError("The name parameter is required!")
    if parameters is None or type(parameters) is not dict: raise ValueError("The parameters parameter must be a dictionary, see docs.")
    for datasetId in parameters.keys():
        if 'samples' not in parameters[datasetId]: raise ValueError(f"Missing 'samples' key for datasetId {datasetId} in parameters parameter!")
    return self.ana_api.createMixedDataset(workspaceId=workspaceId, name=name, parameters=json.dumps(parameters), description=description, seed=seed, tags=tags)