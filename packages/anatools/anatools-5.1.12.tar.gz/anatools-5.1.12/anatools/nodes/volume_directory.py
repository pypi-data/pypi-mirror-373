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
from anatools.lib.node import Node
import anatools.lib.context as ctx
from anatools.lib.directory_object import DirectoryObject

logger = logging.getLogger(__name__)

class VolumeDirectory(Node):
    """ Create a directory object from a directory path """

    def exec(self):
        """Execute node"""

        directory_desc = self.inputs["Directory"][0]
        volume_id, rel_path = directory_desc.split(":/")
        directory = os.path.join(ctx.data, 'volumes', volume_id, rel_path)
        directory_object = DirectoryObject(directory)

        return {"Directory": directory_object}
