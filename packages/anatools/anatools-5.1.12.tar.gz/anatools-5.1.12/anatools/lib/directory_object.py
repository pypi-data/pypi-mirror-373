# Copyright 2019-2022 DADoES, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the root directory in the "LICENSE" file or at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging
import os
import glob

logger = logging.getLogger(__name__)

class DirectoryObject:
    """ A directory stored on a volume """
    def __init__(self, directory):
        self.directory = directory

    def get_files(self, exclude_anameta = True, exclude_subdirs = True):
        """
        Get a list of the files in the directory. By default
        subdirectories and files ending in .anameta are excluded
        """
        path = os.path.join(self.directory, "*")
        files = glob.glob(path)
        path = os.path.join(self.directory, "*.anameta")
        anameta_files = glob.glob(path)
        if exclude_anameta:
            files = list(set(files) - set(anameta_files))
        if exclude_subdirs:
            for file in files[:]:
                if os.path.isdir(file):
                    files.remove(file)
        return files

    def toJSON(self):
        return {
            "class": self.__class__.__name__,
            "directory": self.directory
        }