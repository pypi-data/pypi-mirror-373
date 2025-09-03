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
import os
import sys
import logging
from anatools.lib.generator import ObjectGenerator
from anatools.lib.file_object import FileObject
from anatools.lib.directory_object import DirectoryObject

logger = logging.getLogger(__name__)

def blender_load(self, **kwargs):
    """
    Load a blender file. Doesn't require a collection name.
    """
    import bpy
    from anatools.lib.search_utils import find_root
    if self.loaded:
        # only load the object once
        return

    blender_file = kwargs.pop("blender_file")

    # load the collection containing the object
    with bpy.data.libraries.load(filepath="//" + blender_file, link=False) as (df, dt):
        dt.collections = df.collections
    
    if len(dt.collections) > 0:
        # the object was in a collection
        self.root = find_root(dt.collections[0])
        self.collection = self.root.users_collection[0]
    else:
        # there was no collection found. load the first object found.
        with bpy.data.libraries.load(filepath="//" + blender_file, link=False) as (df, dt):
            dt.objects = df.objects
        name = dt.objects[0].name
        self.collection = bpy.data.collections.new(name)
        bpy.data.collections[name].objects.link(dt.objects[0])
        self.root = dt.objects[0]
    
    # link the collection to the scene
    bpy.context.scene.collection.children.link(self.collection)

    # deprecated parameter
    self.loaded = True

    # get the filename and rename the object and collection for metadata consistency
    name = os.path.splitext(os.path.basename(blender_file))[0]
    self.root.name = name
    self.root.users_collection[0].name = name
    self.object_type = self.root.name

    # save object config if it was provided
    if "config" in kwargs:
        self.config = kwargs.pop("config")


def filename_to_generator(filename, object_class):
    # create an object generator that uses filename as its source
    
    _, ext = os.path.splitext(filename)
    if ext == ".blend":
        # copy the class so we can replace the load method for blender objects
        new_generator_class = type('DynamicObject', object_class.__bases__, dict(object_class.__dict__))
        new_generator_class.load = blender_load
        wrapped_generator = ObjectGenerator(
            new_generator_class,
            None,
            blender_file=filename)
    elif ext == ".gltf":
        # Use existing load method for gltf objects
        wrapped_generator = ObjectGenerator(
            object_class,
            None,
            file_path=filename)
    else:
        logger.error(f"File type of '{ext}' not supported")
        sys.exit(1)
    return wrapped_generator

def file_to_objgen(generators, object_class):
    """
    Process a mixed list of generators, FileObjects, and DirectoryObjects
    For any FileObject in the list, wrap it in an ObjectGenerator. The object type returned by the
    generator will be 'object_class'. The loader method will be replaced with one appropriate
    to the file type specified in the FileObject (currently only Blender is supported).
    For any DirectoryObject in the list, loop through all files in the directory (excluding
    subdirectories and files ending in .anameta) and make them object generators as above.
    """

    # return generators
    wrapped_generators = []
    for generator in generators:
        if isinstance(generator, FileObject):
            wrapped_generators.append(filename_to_generator(generator.filename, object_class))
        elif isinstance(generator, DirectoryObject):
            files = generator.get_files()
            for filename in files:
                wrapped_generators.append(filename_to_generator(filename, object_class))
        else:
            wrapped_generators.append(generator)

    return wrapped_generators