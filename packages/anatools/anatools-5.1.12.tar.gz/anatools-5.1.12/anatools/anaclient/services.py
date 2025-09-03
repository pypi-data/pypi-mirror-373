"""
Services Functions
"""

def get_service_types(self, fields=None):
    """Get the service types supported by the platform.
    
    Parameters
    ----------
    fields : list
        List of fields to return, leave empty to get all fields.
   
    Returns
    -------
    list[dict]
        service types
    """
    import json
    self.check_logout()
    response = self.ana_api.getServiceTypes(fields=fields)
    return response


def get_services(self, organizationId=None, workspaceId=None, serviceId=None, cursor=None, limit=None, filters=None, fields=None):
    """Fetches all services available to an organization or workspace.
    
    Parameters
    ----------
    organizationId : str
        Filter services list on what's available to the organization.
    workspaceId : str    
        Filter services list on what's available to the workspace.
    serviceId: str
        Filter services list on the specific serviceId.
    cursor : str
        Cursor for pagination.
    limit : int
        Maximum of services to return.
    filters: dict
        Filters that limit output to entries that match the filter
    fields : list
        List of fields to return, leave empty to get all fields.
    
    Returns
    -------
    list[dict]
        List of services associated with workspace, organization or serviceId.
    """
    self.check_logout()
    if limit is not None and limit <= 100: items = limit
    else: items = 100
    services = []
    while True:
        if limit and len(services) + items > limit: items = limit - len(services)
        ret = self.ana_api.getServices(organizationId=organizationId, workspaceId=workspaceId, serviceId=serviceId, limit=items, cursor=cursor, filters=filters, fields=fields)
        services.extend(ret)
        if len(ret) < items or len(services) == limit: break
        cursor = ret[-1]["serviceId"]
    return services


def create_service(self, name, description=None, organizationId=None, serviceTypeId=None, volumes=[], instance=None, tags=[], serverId=None):
    """Create a new service for your organization.
    
    Parameters
    ----------
    name : str
        Service name.
    description : str
        Description of the service
    organizationId : str
        Organization ID. Defaults to current if not specified.
    serviceType : str
        The service type that the service adheres to.
    volumes : list[str]
        List of the data volume names to associate with this service.
    instance: str
        AWS Instance type the service will run on.
    tags : list[str]
        List of tags to associate with this service.
    serverId: str
        The ID of the server the service is drafted on, if applicable.
   
    Returns
    -------
    str
        ServiceId of the new service.
    """
    if self.check_logout(): return
    if organizationId is None: organizationId = self.organization
    if serviceTypeId is None: serviceTypeId = 'custom'
    result = self.ana_api.createService(organizationId=organizationId, name=name, description=description, volumes=volumes, instance=instance, serviceTypeId=serviceTypeId, tags=tags, editorId=serverId)
    return result


def edit_service(self, serviceId, name=None, description=None, volumes=None, instance=None, tags=None):
    """Edit a service for your organization.
    
    Parameters
    ----------
    serviceId : str
        Service ID of the service to edit.
    name : name
        The new name to give the service.
    description : str
        Description of the service.
    volumes : list[str]
        Data volumes for the service.
    instance: str
        AWS Instance type to run the service on.
    tags : list[str]
        
    
    Returns
    -------
    bool
        If true, the service was successfully edited.
    """
    self.check_logout()
    if serviceId is None: raise Exception('serviceId must be specified.')
    result = self.ana_api.editService(serviceId=serviceId, name=name, description=description, volumes=volumes, instance=instance, tags=tags)
    return result


def delete_service(self, serviceId):
    """Delete a service from your organization.
    
    Parameters
    ----------
    serviceId : str
        Id of service to delete.
    
    Returns
    -------
    str
        Status
    """
    self.check_logout()
    if serviceId is None: raise Exception('ServiceId must be specified.')
    result = self.ana_api.deleteService(serviceId=serviceId)
    return result


def build_service(self, servicefile):
    """Build the Docker image of a service.
    
    Parameters
    ----------
    servicefile : str
        The service file for the service to build.

    Returns
    -------
    bool
        A boolean that indicates if the service Docker image was successfully built.
    """
    import os
    import docker
    import json
    import time
    import shutil
    import subprocess
    import tempfile
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
        pass

    # check for service Dockerfile
    print('Building Service Image...', end='', flush=True)    
    if not os.path.isfile(servicefile): raise Exception(f'No service file {servicefile} found.')
    servicedir, servicefile = os.path.split(servicefile)
    imgtime = int(time.time())
    image = f"anadeploy-service-{imgtime}"
    if servicedir == "": servicedir = "./"   
    if not os.path.isdir(os.path.join(servicedir, '.devcontainer')): raise Exception(f'No .devcontainer directory found in service directory.')
    if not os.path.isfile(os.path.join(servicedir, '.devcontainer/Dockerfile')): raise Exception(f'No Dockerfile found in .devcontainer/ directory, build requires Dockerfile.')

    # call the docker build command
    try:
        start = time.time()
        streamer = dockerclient.build(
            path=servicedir, 
            dockerfile=os.path.join(servicedir, '.devcontainer/Dockerfile'), 
            tag=image, 
            rm=True, 
            decode=True, 
            platform='linux/amd64', 
            nocache=False,
            pull=False)
        logfilepath = os.path.join(tempfile.gettempdir(), 'dockerbuild.log')
        logfile = open(logfilepath, 'w')
        while True:
            try:
                output = streamer.__next__()
                if self.verbose == 'debug':
                    if 'stream' in output: print(output['stream'].strip('\n'), flush=True)
                    if 'error' in output: print_color(f'{output["error"]}', 'ff0000')
                if 'stream' in output: logfile.write(output['stream'])
                if 'error' in output: logfile.write(output["error"])
                print(f'\rBuilding Service Image...  [{time.time()-start:.3f}s]', end='', flush=True)
            except StopIteration:
                time.sleep(1)
                try:
                    dockerclient = docker.from_env()
                    dockerclient.images.get(image)
                    logfile.close()
                    break
                except Exception as e: raise Exception(e)
    except Exception as e:
        logfile.close()
        raise Exception(f'Error encountered while building Docker image. Please check logfile {logfilepath}.')
    if self.verbose != 'debug' and os.path.exists(logfilepath): os.remove(logfilepath)
    print(f"\rBuilding Service Image...done.  [{time.time()-start:.3f}s]", flush=True)
    return image


def deploy_service(self, serviceId=None, servicefile=None):
    """Deploy the Docker image of a service.
    
    Parameters
    ----------
    serviceId : str
        ServiceId that you are pushing the image to.
    servicefile: str
        Name of the service file to look for. 
    
    Returns
    -------
    str
        deploymentId for current service deployment
    """
    import os
    import docker
    import time
    import base64

    self.check_logout()
    if serviceId is None and image is None: raise Exception('The serviceId or local image must be specified.')
    try: dockerclient = docker.from_env()
    except: raise Exception('Error connecting to Docker.')
    image = self.build_service(servicefile)
    try: serviceimage = dockerclient.images.get(image)
    except docker.errors.ImageNotFound: raise Exception(f'Could not find Docker image with name "{image}".')
    except: raise Exception('Error connecting to Docker.')

    dockerinfo = self.ana_api.deployService(serviceId)
    deploymentId = dockerinfo['deploymentId']
    reponame = dockerinfo['ecrEndpoint']
    encodedpass = dockerinfo['ecrPassword']
    if encodedpass:
        encodedbytes = encodedpass.encode('ascii')
        decodedbytes = base64.b64decode(encodedbytes)
        decodedpass = decodedbytes.decode('ascii').split(':')[-1]
    else: raise Exception('Failed to retrieve credentials from Rendered.ai platform.')

    # tag and push image
    serviceimage.tag(reponame)
    largest = 0
    start = time.time()
    servicedir, servicefile = os.path.split(servicefile)
    if servicedir == "": servicedir = "./"  
    logfile = open(os.path.join(servicedir, 'dockerpush.log'), 'w')
    for line in dockerclient.images.push(reponame, auth_config={'username':'AWS', 'password':decodedpass}, stream=True, decode=True):
        logfile.write(str(line) + '\n')
        if 'status' in line and 'progressDetail' in line:
            if 'current' in line['progressDetail'] and 'total' in line['progressDetail']:
                progressDetail = line['progressDetail']
                if progressDetail['total'] >= largest:
                    largest = progressDetail['total']
                    print(f"\rPushing Service Image...  [{time.time()-start:.3f}s, {min(100,round((progressDetail['current']/progressDetail['total']) * 100))}%]", end='', flush=True)
        if 'error' in line: 
            if 'HTTP 403' in line['error']: raise Exception('You do not have permission to push to this repository.')
            else: raise Exception(line['error'])
    logfile.close()
    if self.verbose != 'debug': os.remove(os.path.join(servicedir, 'dockerpush.log'))
    print(f"\rPushing Service Image...done.  [{time.time()-start:.3f}s]     ", flush=True)
    
    # cleanup docker and update services
    dockerclient.images.remove(reponame)
    dockerclient.images.remove(image)
    dockerclient.close()
    return deploymentId


def get_service_deployment(self, deploymentId, stream=False):
    """Retrieves status for a service deployment.
    
    Parameters
    ----------
    deploymentId: str
        The deploymentId to retrieve status for
    stream: bool
        Flag to monitor deployment status until complete.

    Returns
    -------
    list[dict]
        Deployment status. 
    """
    import time
    self.check_logout()
    if deploymentId is None: raise Exception('DeploymentId must be specified.')
    if stream:
        data = self.ana_api.getServiceDeployment(deploymentId=deploymentId)
        print(f"\r\tStep {data['status']['step']} - {data['status']['message']}", end='', flush=True)
        while (data['status']['state'] not in ['Service Deployment Complete','Service Deployment Failed']):
            time.sleep(10)
            print(f"\r\tStep {data['status']['step']} - {data['status']['message']}", end='', flush=True)
            if self.check_logout(): return
            data = self.ana_api.getServiceDeployment(deploymentId=deploymentId)
        print(f"\r\tStep {data['status']['step']} - {data['status']['message']}", flush=True)
        return data
    else: return self.ana_api.getServiceDeployment(deploymentId=deploymentId)

    

def get_service_jobs(self, workspaceId=None, jobId=None, cursor=None, limit=None, filters=None, fields=None):
    """Fetches all service jobs that have run in a workspace.
    
    Parameters
    ----------
    workspaceId : str    
        The workspace to fetch the service jobs from. If not specified, the current workspace is used.
    jobId: str
        Filter service jobs list on the specific jobId.
    cursor : str
        Cursor for pagination.
    limit : int
        Maximum of service jobs to return.
    filters: dict
        Filters that limit output to entries that match the filter
    fields : list
        List of fields to return, leave empty to get all fields.
    
    Returns
    -------
    list[dict]
        List of service jobs associated with workspace.
    """
    self.check_logout()
    if workspaceId is None: workspaceId = self.workspace
    if limit is not None and limit <= 100: items = limit
    else: items = 100
    jobs = []
    while True:
        if limit and len(jobs) + items > limit: items = limit - len(jobs)
        ret = self.ana_api.getServiceJobs(workspaceId=workspaceId, jobId=jobId, limit=items, cursor=cursor, filters=filters, fields=fields)
        jobs.extend(ret)
        if len(ret) < items or len(jobs) == limit: break
        cursor = ret[-1]["serviceJobId"]
    return jobs


def create_service_job(self, serviceId, name, description=None, payload=None, workspaceId=None):
    """Create a service job for a service.
    
    Parameters
    ----------
    workspaceId : str
        Workspace ID of the workspace to create the job for. If not specified, the current workspace is used.
    serviceId : str
        Service ID of the service to create the job for.
    name : str
        Name of the job.
    description : str
        Description of the job.
    payload : dict
        Payload for the job.
    
    Returns
    -------
    str
        JobId of the created job.
    """
    self.check_logout()
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.createServiceJob(workspaceId=workspaceId, serviceId=serviceId, name=name, description=description, payload=payload)


def delete_service_job(self, jobId, workspaceId=None):
    """Delete a service job for a service.
    
    Parameters
    ----------
    workspaceId : str
        Workspace ID of the workspace to delete the job from. If not specified, the current workspace is used.
    jobId : str
        JobId of the job to delete.
    
    Returns
    -------
    bool
        If true, the job was successfully deleted.
    """
    self.check_logout()
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.deleteServiceJob(workspaceId=workspaceId, jobId=jobId)


def add_workspace_services(self, serviceIds, workspaceId=None):
    """Add a service to a workspace.
    
    Parameters
    ----------
    workspaceId : str
        Workspace ID of the workspace to add the service to. If not specified, the current workspace is used.
    serviceIds : str
        Service IDs of the services to add to the workspace.
    
    Returns
    -------
    bool
        If true, the services were successfully added to the workspace."""
    self.check_logout()
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.addWorkspaceServices(workspaceId=workspaceId, serviceIds=serviceIds)


def remove_workspace_services(self, serviceIds, workspaceId=None):
    """Remove a service from a workspace.
    
    Parameters
    ----------
    workspaceId : str
        Workspace ID of the workspace to remove the service from. If not specified, the current workspace is used.
    serviceIds : str
        Service IDs of the services to remove from the workspace.
    
    Returns
    -------
    bool
        If true, the services were successfully removed from the workspace."""
    self.check_logout()
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.removeWorkspaceServices(workspaceId=workspaceId, serviceIds=serviceIds)


def get_workspace_service_credentials(self, workspaceId=None):
    """Get the credentials for a workspace service.

    Parameters
    ----------
    workspaceId : str
        Workspace ID of the workspace to get the service credentials for. If not specified, the current workspace is used.
    
    Returns
    -------
    dict
        Dictionary of credentials for the workspace service."""
    self.check_logout()
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.getWorkspaceServiceCredentials(workspaceId=workspaceId)
    
    
def get_instance_types(self):
    """Get the available instance types for a service.
    
    Returns
    -------
    list
        List of instance types."""
    self.check_logout()
    return self.ana_api.getInstanceTypes()