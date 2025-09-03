import os
import requests

def download_file(url, fname, localDir):
    if localDir is None: localDir = os.getcwd()
    elif not os.path.exists(localDir): raise Exception(f"Could not find directory {localDir}.")
    with requests.get(url, stream=True) as downloadresponse:
        downloadresponse.raise_for_status()
        with open(os.path.join(localDir,fname), 'wb') as f:
            for chunk in downloadresponse.iter_content(chunk_size=8192): f.write(chunk)

    return os.path.join(localDir,fname)