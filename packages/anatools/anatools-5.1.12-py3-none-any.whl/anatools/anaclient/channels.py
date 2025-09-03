"""
Channels Functions
"""

def get_channels(self, organizationId=None, workspaceId=None, channelId=None, cursor=None, limit=None, filters=None, fields=None):
    """Fetches all 
    
    Parameters
    ----------
    organizationId : str
        Filter channel list on what's available to the organization.
    workspaceId : str    
        Filter channel list on what's available to the workspace.
    channelId: str
        Filter channel list on the specific channelId.
    cursor : str
        Cursor for pagination.
    limit : int
        Maximum of channels to return.
    filters: dict
        Filters that limit output to entries that match the filter
    fields : list
        List of fields to return, leave empty to get all fields.
    
    Returns
    -------
    list[dict]
        List of channels associated with user, workspace, organization or channelId.
    """
    self.check_logout()
    if organizationId is None and workspaceId is None: workspaceId = self.workspace
    if limit is not None and limit <= 100: items = limit
    else: items = 100
    channels = []
    while True:
        if limit and len(channels) + items > limit: items = limit - len(channels)
        ret = self.ana_api.getChannels(organizationId=organizationId, workspaceId=workspaceId, channelId=channelId, limit=items, cursor=cursor, filters=filters, fields=fields)
        channels.extend(ret)
        if len(ret) < items or len(channels) == limit: break
        cursor = ret[-1]["channelId"]
    return channels
                

def get_channel_nodes(self, channelId, fields=None):
    """Get the nodes for a channel.
    
    Parameters
    ----------
    channelId : str
        Channel Id to filter.
    fields : list
        List of fields to return, leave empty to get all fields.
   
    Returns
    -------
    list[dict]
        channel node schema data
    """
    import json
    self.check_logout()
    response = self.ana_api.getChannelSchema(channelId=channelId)
    data = json.loads(response)
    if fields: data = data = [{k: v for k, v in item.items() if k in fields} for item in data]
    return data


def create_channel(self, name, description=None, organizationId=None, volumes=[], instance=None, timeout=120, interfaceVersion=1):
    """Create a channel for your organization.
    
    Parameters
    ----------
    name : str
        Channel name.
    description : str
        Description of the channel
    organizationId : str
        Organization ID. Defaults to current if not specified.
    volumes : list[str]
        List of the data volume names to associate with this channel.
    instance: str
        AWS Instance type.
    timeout: int
        Maximum runtime of a channel run.
    interface: int
        The ana interface version number.
   
    Returns
    -------
    list[dict]
        channel data
    """
    if self.check_logout(): return
    if organizationId is None: organizationId = self.organization
    result = self.ana_api.createChannel(organizationId=organizationId, name=name, description=description, volumes=volumes, instance=instance, timeout=timeout, interfaceVersion=interfaceVersion)
    return result


def edit_channel(self, channelId, name=None, description=None, volumes=None, instance=None, timeout=None, status=None, interfaceVersion=None, preview=None):
    """Edit a channel for your organization.
    
    Parameters
    ----------
    channelId : str
        ChannelId ID of the channel to edit.
    name : name
        The new name to give the channel.
    description : str
        Description of the channel
    volumes : list[str]
        Data volumes for the channel.
    instance: str
        Instance type to run the channel on.
    timeout: int
        Maximum runtime for the channel run.
    status: str
        The status of the channel.
    interface: int
        The ana interface version number.
    preview: bool
        Enable or disable the preview for the channel.
    
    Returns
    -------
    bool
        If true, the channel was successfully edited.
    """
    self.check_logout()
    if channelId is None: raise Exception('ChannelId must be specified.')
    result = self.ana_api.editChannel(channelId=channelId, name=name, description=description, volumes=volumes, instance=instance, timeout=timeout, status=status, interfaceVersion=interfaceVersion, preview=preview)
    return result


def delete_channel(self, channelId):
    """Delete a channel of your organization.
    
    Parameters
    ----------
    channelId : str
        Id of channel to delete.
    
    Returns
    -------
    str
        Status
    """
    self.check_logout()
    if channelId is None: raise Exception('ChannelId must be specified.')
    result = self.ana_api.deleteChannel(channelId=channelId)
    return result


def build_channel(self, channelfile, ignore=['data/', 'output/'], verify=False):
    """Build the Docker image of a channel.
    
    Parameters
    ----------
    channelfile : str
        The channel file for the channel to build.
    ignore : list, optional
        List of files or directories to ignore during the build.
    verify : bool, optional
        If True, verifies the image by running the anautils command.

    Returns
    -------
    bool
        A boolean that indicates if the channel Docker image was successfully built.
    """
    import os
    import docker
    import json
    import shutil
    import time
    import subprocess
    from anatools.lib.print import print_color

    # make sure we can connect to docker
    try: dockerclient = docker.APIClient(base_url='unix://var/run/docker.sock')
    except: raise Exception('Cannot connect to Docker host.')

    # check System and Docker space usage
    try:
        disk_usage = shutil.disk_usage('/')
        gb_free = disk_usage.free / (1024**3)  # Convert bytes to GB
        if self.verbose == 'debug': print(f"Disk space left: {gb_free:.3f}GB")
        if gb_free < 20: print_color(f'\nWarning: Low disk space detected! Only {gb_free:.1f}GB available.', 'ffff00')
        docker_space_cmd = "docker system df --format json"
        result = subprocess.run(docker_space_cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            docker_stats = json.loads(result.stdout)
            total_docker_size = sum(item.get('Size', 0) for item in docker_stats if 'Size' in item)
            docker_gb = total_docker_size / (1024**3)  # Convert bytes to GB
            if self.verbose == 'debug': print(f"Docker space used: {docker_gb:.3f}GB")
            if docker_gb > 20:
                print_color(f'\nWarning: Docker is using {docker_gb:.1f}GB of disk space!', 'ffff00')
                print_color('Consider running "docker system prune -a" to free up space.', 'ffff00')
                print_color('This will remove:', 'ffff00')
                print_color('  - All stopped containers', 'ffff00')
                print_color('  - All networks not used by at least one container', 'ffff00')
                print_color('  - All dangling images', 'ffff00')
                print_color('  - All dangling build cache', 'ffff00')
    except Exception as e:
        print(e)
        pass

    # build dockerfile
    print('Building Channel Image...', end='', flush=True)    
    if not os.path.isfile(channelfile): raise Exception(f'No channel file {channelfile} found.')
    channeldir, channelfile = os.path.split(channelfile)
    if channeldir == "": channeldir = "./"   
    if not os.path.isdir(os.path.join(channeldir, '.devcontainer')): raise Exception(f'No .devcontainer directory found in channel directory.')
    if not os.path.isfile(os.path.join(channeldir, '.devcontainer/Dockerfile')): raise Exception(f'Issue detected with .devcontainer directory, build requires Dockerfile.')

    # check if dockerfile already exists, if so rename it
    if os.path.isfile(os.path.join(channeldir, 'Dockerfile')):
        os.rename(os.path.join(channeldir, 'Dockerfile'), os.path.join(channeldir, 'Dockerfile.old'))

    # create new Dockerfile
    with open(os.path.join(channeldir, 'Dockerfile'), 'w+') as buildfile:
        with open(os.path.join(channeldir,'.devcontainer/Dockerfile')) as dockerfile: buildfile.write(dockerfile.read())
        deploycommands = """\n
# Commands used for deployment
WORKDIR /ana
COPY . .
RUN sudo chown -R $(whoami):$(whoami) /ana
RUN sudo /home/$USERNAME/miniconda3/bin/pip install -r /ana/requirements.txt || \\
    sudo /home/$USERNAME/.conda/bin/pip install -r /ana/requirements.txt
RUN sudo /home/$USERNAME/miniconda3/envs/anatools/bin/pip install -r /ana/requirements.txt || \\
    sudo /home/$USERNAME/.conda/envs/anatools/bin/pip install -r /ana/requirements.txt 
"""
        buildfile.write(deploycommands)

    # build the dockerignore for docker context, ignore specified files and directories
    if os.path.isfile(os.path.join(channeldir, '.dockerignore')):
        os.rename(os.path.join(channeldir, '.dockerignore'), os.path.join(channeldir, '.dockerignore.old'))
    with open(os.path.join(channeldir, '.dockerignore'), 'w+') as ignorefile:
        for i in ignore: ignorefile.write(f'{i}\n')

    # call the docker build command
    status = False
    try:
        start = time.time()
        streamer = dockerclient.build(path=channeldir, tag=channelfile.split('.')[0], decode=True)
        logfile = open(os.path.join(channeldir, 'dockerbuild.log'), 'w')
        while True:
            try:
                output = streamer.__next__()
                if self.verbose == 'debug':
                    if 'stream' in output: print(output['stream'].strip('\n'), flush=True)
                    if 'error' in output: print_color(f'{output["error"]}', 'ff0000')
                if 'stream' in output: logfile.write(output['stream'])
                if 'error' in output: logfile.write(output["error"])
                print(f'\rBuilding Channel Image...  [{time.time()-start:.3f}s]', end='', flush=True)
            except StopIteration as e:
                time.sleep(5)
                print(f"\rBuilding Channel Image...done.  [{time.time()-start:.3f}s]", flush=True)
                try:
                    dockerclient = docker.from_env()
                    dockerclient.images.get(channelfile.split('.')[0])
                    status = True
                    logfile.close()
                    break
                except Exception as e:
                    raise Exception()
    except Exception as e:
        raise Exception(f'Error encountered while building Docker image. Please check logfile dockerbuild.log.')

    # if verify, check that image is valid by running anautils command
    if verify:
        try:
            print(f'Verifying Channel Image...', end='', flush=True)
            start = time.time()

            # Run anautils command in the Docker container to verify schema
            container_name = f"verify_{channelfile.split('.')[0]}_{int(time.time())}"
            cmd = [
                "docker", "run", "--name", container_name, 
                channelfile.split('.')[0], 
                "anautils", "--mode=schema", "--output=/tmp"
            ]
            
            result = subprocess.run(cmd,  capture_output=True, text=True, check=False)
            subprocess.run(["docker", "rm", container_name], capture_output=True)
            if result.returncode != 0:
                print_color(f"\n\n{result.stderr}\n", "ff0000")
                raise Exception(f'Error encountered while verifying Docker image with the anautils command.')
            
            print(f"\rVerifying Channel Image...done. [{time.time()-start:.3f}s]")
            status = True
                
        except Exception as e:
            raise Exception(f'Error encountered while verifying Docker image. Please check that you can generate the schema using the anautils command.')

    # cleanup
    if self.verbose != 'debug': os.remove(os.path.join(channeldir, 'dockerbuild.log'))
    os.remove(os.path.join(channeldir, '.dockerignore'))
    os.remove(os.path.join(channeldir, 'Dockerfile'))
    if os.path.isfile(os.path.join(channeldir, '.dockerignore.old')):
        os.rename(os.path.join(channeldir, '.dockerignore.old'), os.path.join(channeldir, '.dockerignore'))
    if os.path.isfile(os.path.join(channeldir, 'Dockerfile.old')):
        os.rename(os.path.join(channeldir, 'Dockerfile.old'), os.path.join(channeldir, 'Dockerfile'))
    
    return status


def deploy_channel(self, channelId=None, channelfile=None, image=None):
    """Deploy the Docker image of a channel.
    
    Parameters
    ----------
    channelId : str
        ChannelId that you are pushing the image to. If the channelId isn't specified, it will use the image name to lookup the channelId.
    channelfile: str
        Name of the channel file to look for. 
    image: str
        The Docker image name. This should match the channel name when running ana. If image is not specified, it will use the channel name for the channelId.
    
    Returns
    -------
    str
        deploymentId for current round of deployment or an error message if something went wrong
    """
    import os
    import docker
    import time
    import base64

    self.check_logout()
    if channelId is None and image is None: raise Exception('The channelId or local image must be specified.')
    try: dockerclient = docker.from_env()
    except: raise Exception('Cannot connect to Docker host.')

    # build channel image if not specified
    if channelfile and not image:
        if self.build_channel(channelfile, verify=True): image = os.path.split(channelfile)[1].split('.')[0]
        else: return False
    else: raise Exception('The channelfile or a docker image must be specified!')
    try: channelimage = dockerclient.images.get(image)
    except docker.errors.ImageNotFound: raise Exception(f'Could not find Docker image with name "{image}".')
    except: raise Exception('Error connecting to Docker.')

    # get repository info
    print(f"Pushing Channel Image...", end='', flush=True)
    dockerinfo = self.ana_api.deployChannel(channelId, image)
    deploymentId = dockerinfo['deploymentId']
    reponame = dockerinfo['ecrEndpoint']
    encodedpass = dockerinfo['ecrPassword']
    if encodedpass:
        encodedbytes = encodedpass.encode('ascii')
        decodedbytes = base64.b64decode(encodedbytes)
        decodedpass = decodedbytes.decode('ascii').split(':')[-1]
    else: raise Exception('Failed to retrieve credentials from Rendered.ai platform.')

    # tag and push image
    channelimage.tag(reponame)
    largest = 0
    start = time.time()
    channeldir, channelfile = os.path.split(channelfile)
    if channeldir == "": channeldir = "./"  
    logfile = open(os.path.join(channeldir, 'dockerpush.log'), 'w')
    for line in dockerclient.images.push(reponame, auth_config={'username':'AWS', 'password':decodedpass}, stream=True, decode=True):
        if 'status' in line and 'progressDetail' in line:
            if 'current' in line['progressDetail'] and 'total' in line['progressDetail']:
                progressDetail = line['progressDetail']
                if progressDetail['total'] >= largest:
                    largest = progressDetail['total']
                    print(f"\rPushing Channel Image...  [{time.time()-start:.3f}s, {min(100,round((progressDetail['current']/progressDetail['total']) * 100))}%]", end='', flush=True)
        logfile.write(str(line) + '\n')
    logfile.close()
    if self.verbose != 'debug': os.remove(os.path.join(channeldir, 'dockerpush.log'))
    print(f"\rPushing Channel Image...done.  [{time.time()-start:.3f}s]     ", flush=True)
    
    # cleanup docker and update channels
    dockerclient.images.remove(reponame)
    dockerclient.images.remove(image)
    dockerclient.close()
    return deploymentId


def get_deployment_status(self, deploymentId, stream=False):
    """Retrieves status for a channel's deployment.
    
    Parameters
    ----------
    deploymentId: str
        The deploymentId to retrieve status for
    stream: bool
        Flag to print information to the terminal so the user can avoid constant polling to retrieve status.

    Returns
    -------
    list[dict]
        Deployment status. 
    """
    import time
    self.check_logout()
    if deploymentId is None: raise Exception('DeploymentId must be specified.')
    if stream:
        data = self.ana_api.getChannelDeployment(deploymentId=deploymentId)
        print(f"\r\tStep {data['status']['step']} - {data['status']['message']}", end='', flush=True)
        while (data['status']['state'] not in ['Channel Deployment Complete','Channel Deployment Failed']):
            time.sleep(10)
            print(f"\r\tStep {data['status']['step']} - {data['status']['message']}", end='', flush=True)
            if self.check_logout(): return
            data = self.ana_api.getChannelDeployment(deploymentId=deploymentId)
        print(f"\r\tStep {data['status']['step']} - {data['status']['message']}", flush=True)
        return data
    else: return self.ana_api.getChannelDeployment(deploymentId=deploymentId)

    
def get_channel_documentation(self, channelId):
    """Returns channel documentation as markdown text.
    
    Parameters
    ----------
    channelID: str
        The channelId of the channel

    Returns
    -------
    str
        The markdown file for channel documentation.
    """
    return self.ana_api.getChannelDocumentation(channelId=channelId)
    

def upload_channel_documentation(self, channelId, mdfile):
    """Uploads a markdown file for channel documentation.
    
    Parameters
    ----------
    channelID: str
        The channelId of the channel
    mdfile: str
        The filepath of the markdown file used for channel documentation.

    Returns
    -------
    bool
        Success/Failure of channel documenation upload.
    """
    import os
    import requests

    if not os.path.isfile(mdfile): raise ValueError(f'Could not find file {mdfile}')
    if os.path.splitext(mdfile)[1] != '.md': raise ValueError('The channel documentation file must be in markdown format with .md extension.') 
    fileinfo = self.ana_api.uploadChannelDocumentation(channelId=channelId, keys=[os.path.basename(mdfile)])[0]
    with open(mdfile, 'rb') as filebytes:
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
        response = requests.post(fileinfo['url'], data=data, files=files)
        if response.status_code != 204: 
            print(response.status_code)
            raise Exception('Failed to upload channel documentation file.')
    return True


def get_node_documentation(self, channelId, node, fields=None):
    """Retrieves the markdown documentation for a node.
    
    Parameters
    ----------
    channelId: str
        The channelId of the channel
    node: str
        The node to retrieve documentation for.
    fields: list[str]
        List of fields to retrieve for the node documentation.

    Returns
    -------
    str
        The markdown documentation for the node.
    """
    data = self.ana_api.getNodeDocumentation(channelId=channelId, node=node, fields=fields)
    if data: return data
    else: return False
    

def profile_channel(self, graphId=None, channelId=None, instances=None, workspaceId=None):
    """Profile a channel using a graph on the Rendered.ai Platform.
    
    Parameters
    ----------
    name: str
        Name for dataset. 
    graphId : str
        ID of the staged graph to create dataset from.
    description : str 
        Description for new dataset.
    runs : int
        Number of times a channel will run within a single job. This is also how many different images will get created within the dataset. 
    priority : int
        Job priority.
    seed : int
        Seed number.
    workspaceId : str
        Workspace ID of the staged graph's workspace. If none is provided, the current workspace will get used. 
    
    Returns
    -------
    str
        Success or failure message about dataset creation.
    """
    import datetime
    import json
    import time

    if self.check_logout(): return
    if channelId is None and graphId is None: raise ValueError('Either the channelId or graphId parameters must be specified!')
    if instances is None: instances = []
    if type(instances) != list: raise ValueError('The instances parameter must be a list of valid AWS instances types!')
    if workspaceId is None: workspaceId = self.workspace
    
    timestamp = datetime.datetime.now().isoformat()
    starttime = time.time()
    created_graph = False
    if graphId:
        try:
            graphs = self.ana_api.getGraphs(graphId=graphId)
            if len(graphs) == 0: raise ValueError(f'Could not find graph with ID "{graphId}"')
            graphId = graphs[0]['graphId']
            channel = self.ana_api.getChannels(channelId=graphs[0]['channelId'])
        except Exception as e: raise e
    else:
        try:
            channels = self.ana_api.getChannels(channelId=channelId)
            if len(channels) == 0: raise ValueError(f'Could not find channel with ID "{channelId}"')
            channel = channels[0]
            graph = self.ana_api.getDefaultGraph(channelId=channelId)
            graphId = self.ana_api.createGraph(name=f'default-{timestamp}', channelId=channel['channelId'], description=f"Staged graph for profiling channel {channel['name']} (channelId={channel['channelId']}).", staged=True, graph=graph, workspaceId=workspaceId)
            created_graph = True
        except Exception as e: raise e

    # create dataset jobs
    if self.interactive: print(f"Profiling channel {channel['name']}...", end='\r', flush=True)
    if not instances: instances = ['g4dn.xlarge', 'g5.xlarge', 'g6.xlarge', 'g6e.xlarge'] # self.ana_api.getDefaultInstanceTypes()
    jobs = {}
    for instance in instances:
        datasetId = self.ana_api.createDataset(workspaceId=workspaceId, graphId=graphId, name=f"profile-{timestamp}", description=f"Profile of channel {channel['name']} (channelId={channel['channelId']}) on instance type {instance}", runs=1, seed=0, priority=1, instanceType=instance)
        jobs[instance] = {'datasetId': datasetId}

    # wait for dataset jobs to complete
    complete = []
    while True:
        for instance in jobs.keys():
            if jobs[instance]['datasetId'] in complete: continue
            jobdata = self.ana_api.getDatasets(datasetId=jobs[instance]['datasetId'], workspaceId=workspaceId)[0]
            if jobdata['status'] in ['success', 'failed', 'timeout']:
                complete.append(jobs[instance]['datasetId'])
                jobs[instance]['status'] = jobdata['status']
        time.sleep(10)
        if self.interactive: print(f"Profiling channel {channel['name']}...\t[{len(complete)}/{len(jobs)} {int(time.time()-starttime)}]s", end='\r', flush=True)
        if len(jobs.keys()) == len(complete): break
    
    # get dataset metrics
    for instance in jobs.keys():
        runs = self.ana_api.getDatasetRuns(datasetId=jobs[instance]['datasetId'], workspaceId=workspaceId)
        jobs[instance]['metrics'] = self.ana_api.getDatasetMetrics(datasetId=jobs[instance]['datasetId'], runId=runs[0]['runId'], workspaceId=workspaceId)
        # jobs[instance]['stats'] = self.ana_api.getInstanceStats(instance=instance)
    if self.interactive: print(f"Profiling channel {channel['name']}...done! [{int(time.time()-starttime)}s]\033[K", flush=True)

    return jobs