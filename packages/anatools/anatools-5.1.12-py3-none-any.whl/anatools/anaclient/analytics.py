"""
Analytics Functions
"""

def get_analytics_types(self):
    """Retrieve the analytics types available on the Rendered.ai Platform.
    
    Returns
    -------
    list[str]
        The analytics types available on the Platform.
    """
    self.check_logout()
    return self.ana_api.getAnalyticsTypes()


def get_analytics(self, analyticsId=None, datasetId=None, workspaceId=None, cursor=None, limit=None, filters=None, fields=None):
    """Retrieve information about analytics jobs.
    
    Parameters
    ----------
    analyticsId : str
        Analytics Job ID.
    datasetId : str
        Dataset ID of the analytics job.
    workspaceId: str
        Workspace ID where the analytics exist. If none is provided, the current workspace will get used.
    cursor : str
        Cursor for pagination.
    limit : int
        Maximum number of analytics to return.
    filters: dict
        Filters that limit output to entries that match the filter 
    fields : list[str]
        List of fields to return, leave empty to get all fields.
    
    Returns
    -------
    list[dict]
        Analytics job information.
    """
    self.check_logout()
    if workspaceId is None: workspaceId = self.workspace
    if limit is not None and limit <= 100: items = limit
    else: items = 100
    analytics = []
    while True:
        if limit and len(analytics) + items > limit: items = limit - len(analytics)
        ret = self.ana_api.getAnalytics(workspaceId=workspaceId, datasetId=datasetId, analyticsId=analyticsId, limit=items, cursor=cursor, filters=filters, fields=fields)
        analytics.extend(ret)
        if len(ret) < items or len(analytics) == limit: break
        cursor = ret[-1]["analyticsId"]
    return analytics


def download_analytics(self, analyticsId, workspaceId=None):
    """Retrieve information about a specific analytics job. 
    If an analytics job is of type `Object Metrics` or `Mean Brightness`, then images will get downloaded to current working directory. 
    
    Parameters
    ----------
    analyticsId : str
        Analytics Job ID.
    workspaceId: str
        Workspace ID where the analytics exist. If none is provided, the current workspace will get used. 
    
    Returns
    -------
    list[dict]
        Analytics job information.
    """
    import os, json, requests
    self.check_logout()
    if analyticsId is None: raise ValueError("The analyticsId parameter is required!")
    if workspaceId is None: workspaceId = self.workspace
    result = self.ana_api.getAnalytics(workspaceId=workspaceId, analyticsId=analyticsId)
    if len(result) == 0: raise ValueError("Could not find analytics job with analyticsId: {analyticsId}")
    result = result[0]
    if result['type'] not in ['Object Metrics', 'Mean Brightness']: raise ValueError("Analytics job must be of type 'Object Metrics' or 'Mean Brightness' to download images.")
    analytics_result = json.dumps(result)
    presigned_urls = [str for str in analytics_result.split("\\\"") if str.startswith("https")]
    for i in range(len(presigned_urls)):
        filename = presigned_urls[i].split("/")[-1].split("?")[0]
        if self.interactive: print(f"\r[{i+1} / {len(presigned_urls)}]  Downloading {filename}...", end="", flush=True)
        with requests.get(presigned_urls[i], allow_redirects=True) as response:
            with open(filename, "wb") as outfile: outfile.write(response.content)
        analytics_result = analytics_result.replace(presigned_urls[i], os.path.join(os.getcwd(), filename), 1)
    if self.interactive: print("\r", end="")
    return json.loads(analytics_result)


def create_analytics(self, datasetId, type, workspaceId=None, tags=None):
    """Generate analytics for a dataset.
    
    Parameters
    ----------
    datasetId : str
        The datasetId of the dataset to generate analytics for.
    type : str
        The type of analytics to generate for the dataset.
    workspaceId : str
        Workspace ID of the dataset to generate the analytics for. If none is provided, the current workspace will get used. 
    tags : list[str]
        Tags for the analytics job.
    
    Returns
    -------
    str
        The analyticsId for the analytics job.
    """
    self.check_logout()
    if workspaceId is None: workspaceId = self.workspace
    if type not in self.get_analytics_types(): raise ValueError(f"The type parameter '{type}' is invalid, must be one of {self.get_analytics_types()}.")
    return self.ana_api.createAnalytics(workspaceId=workspaceId, datasetId=datasetId, type=type, tags=tags)


def delete_analytics(self, analyticsId, workspaceId=None):
    """Deletes analytics for a dataset.
    
    Parameters
    ----------
    analyticsId : str
        Analytics ID for the analytics to delete. 
    workspaceId: str
        Workspace ID where the analytics exist. If none is provided, the current workspace will get used. 
    
    Returns
    -------
    bool
        If true, successfully deleted the analytics.
    """
    self.check_logout()
    if analyticsId is None: raise ValueError("The analyticsId parameter is required!")
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.deleteAnalytics(workspaceId=workspaceId, analyticsId=analyticsId)


def edit_analytics(self, analyticsId, tags=None, workspaceId=None):
    """Edits analytics for a dataset.
    
    Parameters
    ----------
    analyticsId : str
        Analytics ID for the analytics to edit. 
    tags : list[str]
        Tags for the analytics job.
    workspaceId: str
        Workspace ID where the analytics exist. If none is provided, the current workspace will get used. 
    
    Returns
    -------
    bool
        If true, successfully edited the analytics.
    """
    self.check_logout()
    if analyticsId is None: raise ValueError("The analyticsId parameter is required!")
    if not isinstance(tags, list): raise ValueError("The tags parameter must be a list!")
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.editAnalytics(workspaceId=workspaceId, analyticsId=analyticsId, tags=tags)
    