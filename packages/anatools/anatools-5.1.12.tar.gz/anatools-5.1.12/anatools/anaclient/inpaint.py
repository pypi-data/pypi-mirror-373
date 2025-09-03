"""
Inpaint Functions
"""

def get_inpaints(self, volumeId, inpaintId=None, limit=None, cursor=None, fields=None):
    """Fetches the inpaint jobs in the volume.
    
    Parameters
    ----------
    volumeId : str
        The volumeId to query for inpaint jobs.
    inpaintId : str
        The inpaintId of an inpaint job.
    limit : int
        Maximum number of inpaint jobs to return.
    cursor : str
        Cursor for pagination.
    fields : list
        List of fields to return, leave empty to get all fields.

    Returns
    -------
    dict
        Inpaint jobs info
    """
    self.check_logout()
    if limit is not None and limit <= 100: items = limit
    else: items = 100
    inpaints = []
    while True:
        if limit and len(inpaints) + items > limit: items = limit - len(inpaints)
        ret = self.ana_api.getInpaints(volumeId, inpaintId, limit=items, cursor=cursor, fields=fields)
        inpaints.extend(ret)
        if len(ret) < items or len(inpaints) == limit: break
        cursor = ret[-1]["inpaintId"]
    return inpaints


def get_inpaint_log(self, volumeId, inpaintId, fields=None):
    """ Fetches the logs for the inpaint job.
    
    Parameters
    ----------
    volumeId : str
        Volume ID
    inpaintId : str
        Inpaint ID
    fields : list
        List of fields to return, leave empty to get all fields.

    Returns
    -------
    str
        logs
    """
    if self.check_logout(): return
    return self.ana_api.getInpaintLog(volumeId=volumeId, inpaintId=inpaintId, fields=fields)


def create_inpaint(self, volumeId, location, files=[], destination=None, dilation=5, inputType="MASK", outputType="PNG"):
    """Creates an inpaint job.
    
    Parameters
    ----------
    volumeId : str
        Volume ID
    location : str
        Directory location of the input files
    files : list
        List of files to inpaint, leave empty to inpaint all files in directory
    destination : str
        Destination of the inpaint
    dilation : int
        Dilation used for the inpaint service
    inputType : str
        Type of input file, options are 'MASK', 'GEOJSON', 'COCO', 'KITTI', 'PASCAL', 'YOLO'
    outputType : str
        Type of output file, options are 'SATRGB_BACKGROUND', 'PNG', 'JPG'

    Returns
    -------
    str
        Inpaint ID
    """
    inputTypes = ["MASK", "GEOJSON", "COCO", "KITTI", "PASCAL", "YOLO"]
    outputTypes = ["SATRGB_BACKGROUND", "PNG", "JPG"]
    if self.check_logout(): return
    if inputType not in inputTypes: raise ValueError(f"inputType must be one of {inputTypes}")
    if outputType not in outputTypes: raise ValueError(f"outputType must be one of {outputTypes}")
    return self.ana_api.createInpaint(volumeId=volumeId, location=location, files=files, destination=destination, dilation=dilation, inputType=inputType, outputType=outputType)


def delete_inpaint(self, volumeId, inpaintId):
    """Deletes or cancels an inpaint job.
    
    Parameters
    ----------
    volumeId : str
        Volume ID
    inpaintId : str
        Inpaint ID
    
    Returns
    -------
    bool
        Success / Failure
    """
    if self.check_logout(): return
    return self.ana_api.deleteInpaint(volumeId, inpaintId)
