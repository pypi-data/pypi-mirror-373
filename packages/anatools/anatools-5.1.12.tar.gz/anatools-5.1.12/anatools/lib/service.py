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
import yaml
import glob
import logging
import os
import sys
import importlib
from pathlib import Path
import anatools
import anatools.lib.context as ctx

logger = logging.getLogger(__name__)


def find_servicefile():
    service = None
    servicefiles = []
    # search local directory
    localfiles = [file for file in os.listdir('.') if file.endswith('.yml') or file.endswith('.yaml') ]
    for file in localfiles: servicefiles.append(file)
    for servicefile in servicefiles:
        with open(servicefile, 'r') as f:
            cfg = yaml.safe_load(f)
            # if it adds packages then assume it's a service file
            if "service" in cfg:
                service = servicefile
                print(f'Using servicefile found at {service}.\nIf this is the wrong service, specify a servicefile using the --service argument.')
                break
    return service


class Service:
    
    def __init__(self, servicefile):
        """ Create a service class from a service file """
        self.servicefile = servicefile
        self.description = None
        self.volumes = []
        self.schemas = {}
        self.remotes = []
        with open(servicefile, 'r') as f:
            cfg = yaml.safe_load(f)
            if "service" in cfg:
                self.name = cfg["service"].get("name", os.path.dirname(servicefile))
                self.description = cfg["service"].get("description", None)
                self.volumes = cfg["service"].get("volumes", [])
                self.schemas = cfg["service"].get("tools", {})
            if "remotes" in cfg:
                self.remotes = cfg["remotes"]
                
