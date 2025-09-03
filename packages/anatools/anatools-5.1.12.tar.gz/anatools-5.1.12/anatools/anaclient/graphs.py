"""
Graphs Functions
"""

def get_graphs(self, graphId=None, workspaceId=None, staged=False, cursor=None, limit=None, filters=None, fields=None):
    """Queries the workspace graphs based off provided parameters. If the workspaceId isn't specified, the current workspace will get used.
    
    Parameters
    ----------
    graphid : str
        GraphID to filter on. Optional.
    workspaceId : str    
        Workspace ID to filter on. If none is provided, the default workspace will get used.
    staged : bool
        If true, returns only graphs that are staged.
    cursor : str
        Cursor for pagination.
    limit : int
        Maximum number of graphs to return.
    filters: dict
        Filters that limit output to entries that match the filter 
    fields : list
        List of fields to return, leave empty to get all fields.
    
    Returns
    -------
    list[dict]
        A list of graphs based off provided query parameters if any parameters match.
    """
    self.check_logout()
    if workspaceId is None: workspaceId = self.workspace
    if limit is not None and limit <= 100: items = limit
    else: items = 100
    graphs = []
    while True:
        if limit and len(graphs) + items > limit: items = limit - len(graphs)
        ret = self.ana_api.getGraphs(workspaceId=workspaceId, graphId=graphId, staged=staged, limit=items, cursor=cursor, filters=filters, fields=fields)
        graphs.extend(ret)
        if len(ret) < items or len(graphs) == limit: break
        cursor = ret[-1]["graphId"]
    return graphs


def upload_graph(self, graph, channelId, name, description=None, staged=True, workspaceId=None):
    """Uploads a new graph based off provided parameters.
    
    Parameters
    ----------
    graph: str
        The graph as filepath, or python dictionary.
    channelId: str
        Id of channel to generate the graph with.
    name : str
        Name for the graph that will get generated.
    description: str
        Description of graph. Optional.
    staged: bool
        If true, the graph will get staged (read-only).
    workspaceId : str    
        Workspace ID create the graph in. If none is provided, the default workspace will get used. 
    
    Returns
    -------
    str
        The graphId if it was uploaded sucessfully.
    """
    import json
    import os
    import yaml

    self.check_logout()
    if graph is None: raise ValueError('The graph parameter is required!')
    if channelId is None: raise ValueError('The channelId parameter is required!')
    if name is None: raise ValueError('The name parameter is required!')
    if workspaceId is None: workspaceId = self.workspace
    if type(graph) is dict: graph = json.dumps(graph)
    else: 
        if not os.path.exists(graph): raise ValueError('The provided filepath for the graph parameter does not exist!')
        if graph.endswith('.json'): graph = open(graph, 'r').read()
        elif graph.endswith('.yaml') or graph.endswith('.yml'): graph = json.dumps(yaml.safe_load(open(graph, 'r').read()))
        else: raise ValueError('The graph parameter must be a dictionary or filepath of .json or .yaml file!')
    return self.ana_api.uploadGraph(workspaceId=workspaceId, channelId=channelId, graph=graph, name=name, description=description, staged=staged)


def edit_graph(self, graphId, name=None, description=None, graph=None, tags=None, workspaceId=None):
    """Update graph description and name. 
    
    Parameters
    ----------
    graphId : str
        Graph id to update.
    name: str
        New name to update.
    description: str
        New description to update.
    graph: str
        New graph to update.
    tags: list[str]
        New tags to update.
    workspaceId : str    
        Workspace ID of the graph's workspace. If none is provided, the current workspace will get used. 
    
    Returns
    -------
    bool
        If True, the graph was successfully edited.
    """
    self.check_logout()
    if graphId is None: raise ValueError('The graphId parameter is required!')
    if name is None and description is None and graph is None and tags is None: return True
    if workspaceId is None: workspaceId = self.workspace
    graphinfo = self.ana_api.getGraphs(workspaceId=workspaceId, graphId=graphId)[0]
    if graphinfo['staged'] and graph: raise ValueError('The graph is staged and cannot be edited!')
    return self.ana_api.editGraph(workspaceId=workspaceId, graphId=graphId, name=name, description=description, tags=tags)


def delete_graph(self, graphId, workspaceId=None):
    """Delete a graph in a workspace.
    
    Parameters
    ----------
    graphId : str
        Graph id to delete.
    workspaceId : str    
        Workspace ID of the graph's workspace. If none is provided, the current workspace will get used. 
    
    Returns
    -------
    str
        A success or error message based on graph's delete.
    """
    self.check_logout()
    if graphId is None: raise ValueError('The graphId parameter is required!')
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.deleteGraph(workspaceId=workspaceId, graphId=graphId)
    

def download_graph(self, graphId, filepath=None, workspaceId=None):
    """Downloads a graph and save it to a file. If filepath is provided, the graph will get saved to that location.
    
    Parameters
    ----------
    graphId : str
        Graph ID of the graph to download.
    filepath : str
        Filepath to save the graph to. Optional.
    workspaceId : str    
        Workspace ID of the graph's workspace. If none is provided, the default workspace will get used. 
    
    Returns
    -------
    str
        The filepath of the downloaded graph.
    """
    import json
    import yaml

    self.check_logout()
    if graphId is None: raise ValueError('The graphId parameter is required!')
    if workspaceId is None: workspaceId = self.workspace
    graph = self.ana_api.getGraphs(workspaceId=workspaceId, graphId=graphId)[0]
    if filepath is None: filepath = f"{graph['name']}.yaml"
    graphstr = self.ana_api.downloadGraph(workspaceId=workspaceId, graphId=graphId)
    if filepath.endswith('.json'):
        with open(filepath, 'w+') as jsonfile:
            json.dump(json.loads(graphstr), jsonfile)
    elif filepath.endswith('.yaml') or filepath.endswith('.yml'):
        with open(filepath, 'w+') as yamlfile:
            yaml.safe_dump(json.loads(graphstr), yamlfile)
    else: raise ValueError('The filepath parameter must be a .json or .yaml file!')
    return filepath


def get_default_graph(self, channelId, filepath=None):
    """Downlaosd the default graph for a channel.
    
    Parameters
    ----------
    channelId:
        Id of channel to get the default graph for.
    filepath : str
        Filepath to save the graph to. Optional.

    Returns
    -------
    str
        The filepath of the downloaded graph.
    """
    import json
    import yaml
    
    self.check_logout()
    if channelId is None: raise ValueError('The channelId parameter is required!')
    graphstr = self.ana_api.getDefaultGraph(channelId=channelId)
    if filepath is None: filepath = "default.yaml"
    if filepath.endswith('.json'):
        with open(filepath, 'w+') as jsonfile:
            json.dump(json.loads(graphstr), jsonfile)
    elif filepath.endswith('.yaml') or filepath.endswith('.yml'):
        with open(filepath, 'w+') as yamlfile:
            yaml.safe_dump(json.loads(graphstr), yamlfile)
    else: raise ValueError('The filepath parameter must be a .json or .yaml file!')
    return filepath
    

def set_default_graph(self, graphId, workspaceId=None):
    """Sets the default graph for a channel. User must be in the organization that owns the channel.
    
    Parameters
    ----------
    graphId: str
        The ID of the graph that you want to be the default for the channel
    workspaceId : str
        The ID of the Workspace that the graph is in.

    Returns
    -------
    bool
        If True, the graph was successfully set as the default graph for the channel.
    """
    if self.check_logout(): return    
    if graphId is None: raise ValueError('The graphId parameter is required!')
    if workspaceId is None: workspaceId = self.workspace
    graph = self.ana_api.getGraphs(workspaceId=workspaceId, graphId=graphId)[0]
    return self.ana_api.setDefaultGraph(channelId=graph['channelId'], workspaceId=workspaceId, graphId=graphId)
    