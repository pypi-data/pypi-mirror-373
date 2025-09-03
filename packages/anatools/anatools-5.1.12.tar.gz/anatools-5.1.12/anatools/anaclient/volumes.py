"""
Volumes Functions
"""
import os
import traceback
from anatools.anaclient.helpers import generate_etag, multipart_upload_file

def get_volumes(self, volumeId=None, organizationId=None, workspaceId=None, cursor=None, limit=None, filters=None, fields=None):
    """Retrieves all volumes the user has access to.
    
    Parameters
    ----------
    volumeId : str
        The ID of a specific Volume.
    organizationId : str
        The ID of the organization that the volume belongs to.
    workspaceId : str
        The ID of the workspace that the volume belongs to.
    cursor : str
        Cursor for pagination.
    limit : int
        Maximum number of volumes to return.
    filters: dict
        Filters that limit output to entries that match the filter 
    fields : list
        List of fields to return, leave empty to get all fields.
    
    Returns
    -------
    list[dict]
        Volume Info
    """
    self.check_logout()
    if organizationId is None and workspaceId is None: organizationId = self.organization
    if limit is not None and limit <= 100: items = limit
    else: items = 100
    volumes = []
    while True:
        if limit and len(volumes) + items > limit: items = limit - len(volumes)
        ret = self.ana_api.getVolumes(organizationId=organizationId, workspaceId=workspaceId, volumeId=volumeId, limit=items, cursor=cursor, filters=filters, fields=fields)
        volumes.extend(ret)
        if len(ret) < items or len(volumes) == limit: break
        cursor = ret[-1]["volumeId"]
    return volumes


def create_volume(self, name, description=None, organizationId=None, permission=None, tags=None):
    """Creates a new volume with the specified name in the organization. By default the permission on the volume is set to `write`.
    
    Parameters
    ----------
    name : str
        The name of the new volume. Note: this name needs to be unique per organization.
    description : str
        Description of the volume
    organizationId : str
        The ID of the organization that the volume will belong to.
    permission : str
        Permission to set for the volume. Choose from: read, write, or view.
    tags : list
        Tags to set for the volume.
    
    Returns
    -------
    str
        volumeId
    """
    self.check_logout()
    if name is None: raise Exception("The name parameter is required!")
    if description is None: description = ''
    if organizationId is None: organizationId = self.organization
    return self.ana_api.createVolume(organizationId=organizationId, name=name, description=description, permission=permission, tags=tags)

    
def delete_volume(self, volumeId):
    """Removes the volume from the organization. Note that this will delete any remote data in the volume 
    and channels that rely on this volume will need to be updated.
    
    Parameters
    ----------
    volumeId : str
        The ID of a specific Volume to delete.
    
    Returns
    -------
    str
        Status
    """
    self.check_logout()
    if volumeId is None: raise Exception('The volumeId parameter is required!')
    return self.ana_api.deleteVolume(volumeId=volumeId)


def edit_volume(self, volumeId, name=None, description=None, permission=None, tags=None):
    """Edits the volume in your current organization.
    
    Parameters
    ----------
    volumeId: str
        The volumeId that will be updated.
    name : str
        The new name of the new volume. Note: this name needs to be unique per organization.
    description : str
        Description of the volume
    permission : str
        Permission to set for the volume. Choose from: read, write, or view.
    tags : list
        Tags to set for the volume.
    
    Returns
    -------
    str
        Status True or False
    """
    if self.check_logout(): return
    if volumeId is None: raise Exception('VolumeId must be specified.')
    if name is None and description is None: raise Exception("Either name or description must be specified.")
    if tags and not isinstance(tags, list): raise Exception("Tags must be a list of strings.")
    return self.ana_api.editVolume(volumeId=volumeId, name=name, description=description, permission=permission, tags=tags)


def get_volume_data(self, volumeId, files=None, dir=None, recursive=False, cursor=None, limit=None):
    """Retrieves information about data from a volume.
    
    Parameters
    ----------
    volumeId : str
       VolumeId to get data for.
    files : str
        The specific files or directories to retrieve information about from the volume, if you wish to retrieve all then leave the list empty.
    dir : str
        Specific volume directory to retrieve information about. Optional. 
    recursive : bool
        Whether to recursively retrieve information about the volume. Optional.
    cursor : str
        Cursor for pagination. Optional.
    limit : int
        Maximum number of volumes to return. Optional.
    
    Returns
    -------
    str
       Status
    """
    self.check_logout()
    if volumeId is None: raise Exception('The volumeId parameter is required!')
    if limit is not None and limit <= 100: items = limit
    if files is None: files = []
    if dir is None: dir = ''
    if cursor is None: cursor = 0
    else: items = 100
    volumedata = []
    while True:
        if limit and len(volumedata) + items > limit: items = limit - len(volumedata)
        ret = self.ana_api.getVolumeData(volumeId=volumeId, keys=files, dir=dir, recursive=recursive, cursor=str(cursor), limit=limit)
        volumedata.extend(ret)
        if len(ret) < items or len(volumedata) == limit: break
        cursor += items
    return volumedata


def edit_volume_data(self, volumeId, source, key):
    """Edit data in a volume.
    
    Parameters
    ----------
    volumeId : str
       VolumeId to edit data of.
    source : str
        The source of the data to edit.
    key : str
        The key of the data to edit.
    
    Returns
    -------
    str
       Status
    """
    self.check_logout()
    if volumeId is None: raise Exception('The volumeId parameter is required!')
    if source is None: raise Exception('The source parameter is required!')
    if key is None: raise Exception('The key parameter is required!')
    return self.ana_api.editVolumeData(volumeId=volumeId, source=source, key=key)


def download_volume_data(self, volumeId, files=[], localDir=None, recursive=True, sync=False):
    """Download data from a volume.
    
    Parameters
    ----------
    volumeId : str
       VolumeId to download data of.
    files : str
        The specific files or directories to retrieve from the volume, if you wish to retrieve all then leave the list empty.
    localDir : str
        The location of the local directory to download the files to. If not specified, this will download the files to the current directory.
    recursive: bool
        Recursively download files from the volume.
    sync: bool
        Syncs data between the local directory and the remote location. Only creates folders in the destination if they contain one or more files.
    Returns
    -------
    str
       Status
    """
    import hashlib
    import os
    import requests
    import traceback

    self.check_logout()
    if volumeId is None: raise Exception('The volumeId parameter is required!')
    if localDir is None: localDir = os.getcwd()
    if not os.path.exists(localDir): os.makedirs(localDir, exist_ok=True)

    response = []
    for file in files or [""]:
        condition = True
        offset = 0
        limit = 100

        key_param = [] if file.endswith("/") or file == "" else [file]
        dir_param = file if file.endswith("/") else ""

        while condition:
            result = self.ana_api.getVolumeData(
                volumeId=volumeId, 
                keys=key_param,
                dir=dir_param,
                limit=limit, 
                recursive=recursive, 
                cursor=str(offset)
            )
            for fileinfo in result['keys']:
                if fileinfo['size']:
                    response.append({
                        'key': os.path.join(dir_param, fileinfo['key']),
                        'size': fileinfo['size'],
                        'lastUpdated': fileinfo['updatedAt'],
                        'hash': fileinfo['hash'],
                        'url': fileinfo['url'],
                    })
            if len(result['keys']) < limit: condition = False
            else: offset += limit

    source_hashes = list(map(lambda x: x['key'] + x['hash'], response))
    destination_files = []
    destination_hashes = []

    if sync == True:    
        for root, dirs, files in os.walk(localDir):
            for file in files:
                filepath = os.path.join(root, file).replace(localDir, '')
                destination_files.append(filepath)
                file_hash = hashlib.md5()
                with open(os.path.join(root, file),'rb') as f: 
                    while True:
                        chunk = f.read(128 * file_hash.block_size)
                        if not chunk:
                            break
                        file_hash.update(chunk)
                destination_hashes.append(filepath + file_hash.hexdigest())

    for index, hash in enumerate(source_hashes):
        if (sync == True and (hash in destination_hashes)):
            if self.interactive: 
                print(f"\x1b[1K\rsync: {response[index]['key']}'s hash exists in {localDir}", flush=True)
        elif sync == False or (hash not in destination_hashes):
            try:
                downloadresponse = requests.get(url=response[index]['url'])
                filename = os.path.join(localDir, response[index]['key'])
                if not os.path.exists(os.path.dirname(filename)):
                    os.makedirs(os.path.dirname(filename))
                with open(filename, 'wb') as outfile:
                    outfile.write(downloadresponse.content)
                if self.interactive: 
                    print(f"\x1b[1K\rdownload: {response[index]['key']} to {filename}", flush=True)
            except:
                traceback.print_exc()
                print(f"\x1b[1K\rdownload: failed to download {response[index]['key']}", flush=True)
    return


def upload_volume_data(self, volumeId, files=None, localDir=None, destinationDir=None, sync=False):
    """Upload data to a volume.
    
    Parameters
    ----------
    volumeId : str
       VolumeId to upload data to.
    files : list[str]
        The specific files or directories to push to the volume from the localDir. If you wish to push all data in the root directory, then leave the list empty.
    localDir : str
        The location of the local directory to upload the files from. If not specified, this will try to upload the files from the current directory.
    destinationDir : str
        The target directory in the volume where files will be uploaded. If not specified, files will be uploaded to the root of the volume.
    sync: bool
        Recursively uploads new and updated files from the source to the destination. Only creates folders in the destination if they contain one or more files.
    
    Returns
    -------
    str
       Status
    """
    self.check_logout()
    if volumeId is None: raise Exception('The volumeId parameter is required!')
    if files is None: files = []
    if localDir is None: localDir = os.getcwd()
    if not localDir.endswith('/'): localDir+='/'
    if not os.path.exists(localDir): raise Exception(f"Could not find directory {localDir}.")
    if destinationDir is not None:
        destinationDir = destinationDir.strip('/')
        if destinationDir: destinationDir += '/'

    source_files = []
    source_hashes = []
    faileduploads = []
        
    if len(files):
        for file in files:
            filepath = os.path.join(localDir, file)
            if os.path.isdir(filepath):
                for root, dirs, files in os.walk(filepath):
                    for file in files:
                        filepath = os.path.join(root, file).replace(localDir, '')
                        source_files.append(filepath)
                        if sync == True:
                            file_hash = generate_etag(os.path.join(root,file))
                            source_hashes.append(filepath + file_hash)
            elif os.path.isfile(filepath):
                source_files.append(file)
                if sync == True:
                    file_hash = generate_etag(filepath)
                    source_hashes.append(file + file_hash)
            else: print(f"Could not find {filepath}.")
    else:
        for root, dirs, files in os.walk(localDir):
            for file in files:
                filepath = os.path.join(root, file).replace(localDir, '')
                source_files.append(filepath)
                if sync == True:
                    file_hash = generate_etag(os.path.join(root,file))
                    source_hashes.append(filepath + file_hash)

    if sync == True:
        response = []
        condition = True
        offset = 0

        while condition:
            result = self.ana_api.getVolumeData(volumeId=volumeId, keys=[], dir=destinationDir or "", limit=100, offset=offset)
            for fileinfo in result['keys']:
                response.append({
                    'key':          fileinfo['key'],
                    'size':         fileinfo['size'],
                    'lastUpdated':  fileinfo['updatedAt'],
                    'hash':         fileinfo['hash'],
                    'url':          fileinfo['url'],
                })
            
            if (result['pageInfo']['totalItems'] > offset + 100):
                offset += 100
            else:
                condition = False

        destination_hashes = list(map((lambda x: x['key'] + x['hash']), [file for file in response if file['size'] != 0]))
        delete_files = []
        for index, object in enumerate(response):
            if object['key'] not in source_files:
                destination_file = (destinationDir or '') + object['key']
                delete_files.append(destination_file)  

        if (len(delete_files)):
            print(f"The following files will be deleted:", end='\n', flush=True)
            for file in delete_files:
                print(f"   {file}", end='\n', flush=True)
            answer = input("Delete these files [Y/n]: ")
            if answer.lower() == "y":
                self.refresh_token()
                self.ana_api.deleteVolumeData(volumeId=volumeId, keys=delete_files)

    for index, file in enumerate(source_files):
        destination_key = (destinationDir or '') + file
        print(f"\x1b[1K\rUploading {file} to the volume [{index+1} / {len(source_files)}]", end='\n' if self.verbose else '', flush=True)
        if (sync == True and (source_hashes[index] in destination_hashes)):
            print(f"\x1b[1K\rsync: {file}'s hash exists", end='\n' if self.verbose else '', flush=True)
        elif sync == False or (source_hashes[index] not in destination_hashes):
            try:
                self.refresh_token()
                filepath = os.path.join(localDir, file)
                filesize = os.path.getsize(filepath)
                fileinfo = self.ana_api.uploadVolumeData(volumeId=volumeId, key=destination_key, size=filesize)
                # print(f"\x1b[1K\rupload: {file} to the volume. [{index+1} / {len(source_files)}]", end='\n' if self.verbose else '', flush=True)
                parts = multipart_upload_file(filepath, int(fileinfo["partSize"]), fileinfo["urls"], f"Uploading {file} to the volume [{index+1} / {len(source_files)}]")
                self.refresh_token()
                finalize_success = self.ana_api.uploadVolumeDataFinalizer(volumeId, fileinfo['uploadId'], fileinfo['key'], parts)
                if not finalize_success:
                    faileduploads.append(file)
            except:
                traceback.print_exc()
                faileduploads.append(file)
                print(f"\x1b[1K\rupload: {file} failed", end='\n' if self.verbose else '', flush=True)
    print("\x1b[1K\rUploading files completed.", flush=True)
    if len(faileduploads): print('The following files failed to upload:', faileduploads, flush=True)
    return
            

def delete_volume_data(self, volumeId, files=None):
    """Delete data from a volume.
    
    Parameters
    ----------
    volumeId : str
       VolumeId to delete files from.
    files : str
        The specific files to delete from the volume. If left empty, no files are deleted.
    
    Returns
    -------
    str
       Status
    """
    self.check_logout()
    if volumeId is None: raise Exception('The volumeId parameter is required!')
    if files is None: files = []
    return self.ana_api.deleteVolumeData(volumeId=volumeId, keys=files)


def mount_volumes(self, volumes):
    """Retrieves credentials for mounting volumes.
    
    Parameters
    ----------
    volumes : [str]
       Volumes to retrieve mount credentials for.

    Returns
    -------
    dict
        Credential information.
    """
    self.check_logout()
    if not len(volumes): raise Exception('The volumes parameter must be a list of volumeIds!')
    return self.ana_api.mountVolumes(volumes=volumes)


def add_workspace_volumes(self, volumeIds, workspaceId=None):
    """Add volumes to a workspace.
    
    Parameters
    ----------
    workspaceId : str
        Workspace ID of the workspace to add the volumes to. If not specified, the current workspace is used.
    volumeIds : str
        Volume IDs of the volumes to add to the workspace.
    
    Returns
    -------
    bool
        If true, the volumes were successfully added to the workspace."""
    self.check_logout()
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.addWorkspaceVolumes(workspaceId=workspaceId, volumeIds=volumeIds)


def remove_workspace_volumes(self, volumeIds, workspaceId=None):
    """Remove volumes from a workspace.
    
    Parameters
    ----------
    workspaceId : str
        Workspace ID of the workspace to remove the volumes from. If not specified, the current workspace is used.
    volumeIds : str
        Volume IDs of the volumes to remove from the workspace.
    
    Returns
    -------
    bool
        If true, the volumes were successfully removed from the workspace."""
    self.check_logout()
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.removeWorkspaceVolumes(workspaceId=workspaceId, volumeIds=volumeIds)


def search_volume(self, volumeId, directory=None, recursive=True, keywords=None, fileformats=None, filetypes=None, tags=None, cursor=None, limit=None):
    """Searches a volume for files that match the specified filters.
    
    Parameters
    ----------
    volumeId : str
        Volume ID of the volume to search.
    directory: str
        Limit search to a specific directory.
    recursive: bool
        Search all subdirectories if true, only specified directory if not.
    keywords : [str]
        The keyword to search for, can be in filename or path.
    fileformats: [str]
        The file format to search for (ie. png, jpeg, blend)
    filetypes: [str]
        The file type to search for (ie. 3D, Image, Video, Text)
    tags:
        The tags to search for.

    Returns
    -------
    [data]
        Returns a list of volume data files found that match the criteria."""
    self.check_logout()
    if volumeId is None: raise Exception('The volumeId parameter must be specified.')
    if directory and not isinstance(directory, str): raise Exception('The directory parameter must be a string.')
    if recursive and not isinstance(recursive, bool): raise Exception('The recursive parameter must be a boolean.')
    if keywords and not isinstance(keywords, list): raise Exception('The keywords parameter must be a list.')
    if fileformats and not isinstance(fileformats, list): raise Exception('The fileformats parameter must be a list.')
    if filetypes and not isinstance(filetypes, list): raise Exception('The filetypes parameter must be a list.')
    if tags and not isinstance(tags, list): raise Exception('The tags parameter must be a list.')
    
    filters = {'texts':[], 'fileFormats': [], 'fileTypes':[]}
    if keywords: filters['texts'] = keywords
    if tags: filters['texts'] = filters['texts'].extend(tags)
    if fileformats: [filters['fileFormats'].append({'eq': fileformat}) for fileformat in fileformats]
    if filetypes: [filters['fileTypes'].append({'eq': filetype}) for filetype in filetypes]
    if limit is not None and limit <= 100: items = limit
    else: items = 100
    volumedata = []
    while True:
        if limit and len(volumedata) + items > limit: items = limit - len(volumedata)
        ret = self.ana_api.getVolumeData(volumeId=volumeId, dir=directory, recursive=recursive, cursor=cursor, limit=limit, filters=filters)
        volumedata.extend(ret['keys'])
        if len(ret['keys']) < items or len(volumedata) == limit: break
        cursor = ret['keys'][-1]["key"]
    return volumedata