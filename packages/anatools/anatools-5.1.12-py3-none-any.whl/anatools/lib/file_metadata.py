# Copyright 2019-2023 DADoES, Inc.
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
import yaml
import os
import logging

logger = logging.getLogger(__name__)

def file_metadata(filename):
    """
    Get the metadata associated with a file. Return it as a dictionary.
    If there is no metadata file then return an empty dictionary.
    """
    metadata_filename = filename + ".anameta"
    if os.path.isfile(metadata_filename):
        try:
            with open(metadata_filename, "r") as f:
                metadata = yaml.safe_load(f)
        except:
            logger.error(f"Error reading metadata file '{metadata_filename}'")
            raise
    else:
        # if there is no .anameta file then return None
        metadata = None
    return metadata