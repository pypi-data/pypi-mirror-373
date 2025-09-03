import json
import math
import os
import datetime
import hashlib
import mimetypes
from PIL import Image

def create_cocodata():
    cocodata = dict()
    cocodata['info'] = {    
        "description":  "Rendered.AI Synthetic Dataset",
        "url":          "https://rendered.ai/",
        "contributor":  "info@rendered.ai",
        "version":      "1.0",
        "year":         str(datetime.datetime.now().year),
        "date_created": datetime.datetime.now().isoformat()}
    cocodata['licenses'] = [{
        "id":   0,
        "url":  "https://rendered.ai/",     # "url": "https://creativecommons.org/licenses/by-nc-nd/4.0/",
        "name": "Rendered.AI License"}]     # "name": "Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License"}]
    cocodata['images'] = list()
    cocodata['categories'] = list()
    return cocodata


def create_bounding_box_geojson(min_x, min_y, max_x, max_y):
    """
    Create a GeoJSON object representing the bounding box with the given coordinates.
    
    :param min_x: Minimum x value (longitude)
    :param min_y: Minimum y value (latitude)
    :param max_x: Maximum x value (longitude)
    :param max_y: Maximum y value (latitude)
    :return: GeoJSON object as a dictionary
    """
    # Define the coordinates of the bounding box in GeoJSON format
    coordinates = [
        [
            [min_x, min_y],  # Bottom-left corner
            [min_x, max_y],  # Top-left corner
            [max_x, max_y],  # Top-right corner
            [max_x, min_y],  # Bottom-right corner
            [min_x, min_y]   # Close the polygon by returning to the bottom-left corner
        ]
    ]

    # Create the GeoJSON object
    geojson = {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": coordinates
        },
    }

    return geojson


def generate_file_checksum(file_path, algorithm='sha256'):
    """
    Generate a checksum hash for a given file.

    Parameters:
    - file_path (str): The path to the file.
    - algorithm (str): The hashing algorithm to use (e.g., 'md5', 'sha1', 'sha256').

    Returns:
    - str: The hexadecimal checksum hash of the file.
    """
    # Create a hash object with the specified algorithm
    hash_obj = hashlib.new(algorithm)
    
    # Open the file in binary mode and read in chunks
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_obj.update(chunk)
    
    # Return a string providing the algorithm and the hash of the image
    return f'{algorithm}:{hash_obj.hexdigest()}'


def get_image_bands(image_path):
    # Open the image file
    with Image.open(image_path) as img:
       
        # Get the individual bands in the image (e.g., 'R', 'G', 'B')
        bands = list(img.getbands())  # Convert tuple to a list

        return bands


def get_rotated_bbox_coordinates(center_x, center_y, width, height, angle_degrees):
    """
    Calculates the pixel-space coordinates of a rotated bounding box.

    Parameters:
    - center_x, center_y: The center of the bounding box in pixel space
    - width, height: The width and height of the bounding box
    - angle_degrees: The rotation angle of the bounding box in degrees

    Returns:
    - A list of coordinates starting from the topmost point and proceeding anti-clockwise.
    """
    
    # Convert angle from degrees to radians
    angle_radians = math.radians(angle_degrees)

    # Half dimensions
    half_width = width / 2.0
    half_height = height / 2.0

    # Calculate the coordinates of the four corners relative to the center
    corners = [
        (-half_width, -half_height),  # Top-left
        (half_width, -half_height),   # Top-right
        (half_width, half_height),    # Bottom-right
        (-half_width, half_height)    # Bottom-left
    ]

    # Rotate the corners relative to the center
    rotated_corners = []
    for x, y in corners:
        rotated_x = center_x + (x * math.cos(angle_radians) + y * math.sin(angle_radians))
        rotated_y = center_y + (-x * math.sin(angle_radians) + y * math.cos(angle_radians))
        rotated_corners.append((rotated_x, rotated_y))

    # Sort by angle to get counter-clockwise order
    rotated_corners.sort(key=lambda point: math.atan2(point[1] - center_y, point[0] - center_x))

    # Find the topmost point to start from
    topmost_point = max(rotated_corners, key=lambda point: point[1])

    # Reorder points to start with the topmost
    topmost_index = rotated_corners.index(topmost_point)
    rotated_corners = rotated_corners[topmost_index:] + rotated_corners[:topmost_index]

    # Flatten the list of tuples
    return [coord for point in rotated_corners for coord in point]


class geo_image:
    def __init__(self, image_width, image_height, top_left_lat, top_left_lon, bottom_right_lat, bottom_right_lon):
        """
         Parameters:
        - image_width: The width of the image in pixels.
        - image_height: The height of the image in pixels.
        - top_left_lat: The latitude of the top-left corner of the image.
        - top_left_lon: The longitude of the top-left corner of the image.
        - bottom_right_lat: The latitude of the bottom-right corner of the image.
        - bottom_right_lon: The longitude of the bottom-right corner of the image.
        """
 
        self.image_width = image_width
        self.image_height = image_height
        self.top_left_lat = top_left_lat
        self.top_left_lon = top_left_lon
        self.bottom_right_lat = bottom_right_lat
        self.bottom_right_lon = bottom_right_lon

    def pixel_to_geo(self, pixel_coords):
        """
        Converts a flattened list of pixel coordinates to geographic coordinates (latitude, longitude).

        Parameters:
        - pixel_coords: A flattened list of pixel coordinates [x1, y1, x2, y2, ...].

        Returns:
        - A flattened list of geographic coordinates [lat1, lon1, lat2, lon2, ...].
        """

        # Calculate the width and height of the geographic area covered by the image
        lat_range = abs(self.top_left_lat - self.bottom_right_lat)
        lon_range = abs(self.bottom_right_lon - self.top_left_lon)

        # Initialize the list for geographic coordinates
        geographic_coords = []

        # Iterate over the pixel coordinates in pairs (x, y)
        for i in range(0, len(pixel_coords), 2):
            pixel_x = pixel_coords[i]
            pixel_y = pixel_coords[i + 1]

            # Calculate the geographic coordinates of the pixel
            lat = self.top_left_lat - (pixel_y / self.image_height) * lat_range
            lon = self.top_left_lon + (pixel_x / self.image_width) * lon_range

            # Append the result to the list
            geographic_coords.append(lon)
            geographic_coords.append(lat)

        return geographic_coords


def get_highest_classification(classifications):
    # Define the order of classification levels
    level_rank = {'UNCLASSIFIED': 0, 'CONFIDENTIAL': 1, 'SECRET': 2, 'TOP SECRET': 3}
    
    # Find the highest classification level in the provided list
    highest_level = None
    highest_rank = -1
    
    for classification in classifications:
        rank = level_rank.get(classification, -1)
        if rank > highest_rank:
            highest_rank = rank
            highest_level = classification
    
    return highest_level


def convert_geococo(datadir, outdir, mapping = None):

    annsdir = os.path.join(datadir, "annotations")
    metadir = os.path.join(datadir, "metadata")
    imgdir = os.path.join(datadir, "images")
    annsfiles = os.listdir(annsdir)
    
    cocodata = create_cocodata()
    cats = {0:[None, 'coco_background']}
    imgid = 0
    annid = 0

    with open(os.path.join(outdir,'geococo.json'), 'w+') as of:
        of.write('{"annotations": [')
        first = True

        img_height_list = []
        img_width_list = []
        img_count = 0
        img_memory_size = 0
        classification_list = []
        # for each interpretation, gather annotations and map categories
        for f in sorted(annsfiles):
            if not f.endswith('.json'): continue
            with open(os.path.join(annsdir,f), 'r') as af: anns = json.load(af)
            with open(os.path.join(metadir,f.replace('ana','metadata')), 'r') as mf: metadata = json.load(mf)

            # check for required fields for rotated bounding box calculation
            calc_rotated_bbox = False
            rb_meta_fields = ['meters_per_pixel', 'azimuth']
            if 'sensor' in metadata:
                img_width =  metadata['sensor']['resolution'][0]
                img_height =  metadata['sensor']['resolution'][1]
                if 'frame' in metadata['sensor']: metadata['frame'] = metadata['sensor']['frame']
                if all(metadata['sensor'].get(field) is not None for field in rb_meta_fields):
                    calc_rotated_bbox = True
            else:
                im = Image.open(os.path.join(imgdir, anns['filename']))
                img_width, img_height = im.size
            
            # check for required metadata fields for geolocation
            calc_geo = False
            geo_fields = ['lat', 'lon', 'bottom', 'right']
            lat, lon, bottom, right = [0, 0, 0, 0]
            if 'environment' in metadata:
                if all(metadata['environment'].get(field) is not None for field in geo_fields):
                    lat, lon, bottom, right = [metadata['environment'][field] for field in geo_fields]
                    img_geo = geo_image(img_width, img_height, *[metadata['environment'][field] for field in geo_fields])
                    calc_geo = True

            # for each object in the metadata file, check if any of the properties are true
            for obj in metadata['objects']:
                if mapping is None:
                    for ann in anns['annotations']:
                        if ann['id'] == obj['id']: 
                            if [None, obj['type']] in cats.values(): class_num = [k for k,v in cats.items() if v == [None, obj['type']]][0]
                            else : class_num = len(cats.keys())
                            cats[class_num] = [None, obj['type']]
                            annotation = {}
                            annotation['id'] = annid
                            annotation['image_id'] = imgid
                            annotation['category_id'] = class_num
                            annotation['segmentation'] = ann['segmentation']
                            annotation['area'] = ann['bbox'][2] * ann['bbox'][3]
                            annotation['bbox'] = ann['bbox']
                            annotation['iscrowd'] = 0
                            annotation['keypoints'] = []
                            annotation['num_keypoints'] = 0
                            annotation['bbox_rotated'] = []
                            annotation['object_center'] = [ann['centroid'][1], ann['centroid'][0]]
                            annotation['bbox_geo'] = []
                            annotation['bbox_rotated_geo'] = []
                            annotation['object_center_geo'] = []
                            annotation['keypoints_geo'] = []
                            annotation['classification'] = 'Undefined'
                            if 'keypoints' in ann:
                                annotation['keypoints'] = ann['keypoints']
                                annotation['num_keypoints'] = len(ann['keypoints'])
                                if calc_geo:
                                    annotation['keypoints_geo'] = img_geo.pixel_to_geo(ann['keypoints'])
                            if calc_rotated_bbox:
                                obj_width = ann['size'][0] / metadata['sensor']['meters_per_pixel']
                                obj_length = ann['size'][1] / metadata['sensor']['meters_per_pixel']
                                rotation = (math.degrees(ann['rotation'][2]) - metadata['sensor']['azimuth']) % 360
                                annotation['bbox_rotated'] = [ann['centroid'][1], ann['centroid'][0], obj_width, obj_length, rotation]
                                if calc_geo:
                                    bbox_rotated_coords = get_rotated_bbox_coordinates(*annotation['bbox_rotated'])
                                    annotation['bbox_rotated_geo'] = img_geo.pixel_to_geo(bbox_rotated_coords)
                            if calc_geo:
                                annotation['bbox_geo'] = img_geo.pixel_to_geo(annotation['bbox'])
                                annotation['object_center_geo'] = img_geo.pixel_to_geo(annotation['object_center'])
                            if 'classification' in ann:
                                annotation['classification'] = ann['classification']
                                if ann['classification'] not in classification_list:
                                    classification_list.append(ann['classification'])
                            annid += 1
                            if not first: of.write(', ')
                            json.dump(annotation, of)
                            first = False
                            break
                else:
                    for prop in mapping['properties']:
                        if eval(prop):
                            for ann in anns['annotations']:
                                if ann['id'] == obj['id']: 
                                    class_num = mapping['properties'][prop]
                                    cats[class_num] = mapping['classes'][class_num]
                                    annotation = {}
                                    annotation['id'] = annid
                                    annotation['image_id'] = imgid
                                    annotation['category_id'] = class_num
                                    annotation['segmentation'] = ann['segmentation']
                                    annotation['area'] = ann['bbox'][2] * ann['bbox'][3]
                                    annotation['bbox'] = ann['bbox']
                                    annotation['iscrowd'] = 0
                                    annotation['keypoints'] = []
                                    annotation['num_keypoints'] = 0
                                    annotation['bbox_rotated'] = []
                                    annotation['object_center'] = [ann['centroid'][1], ann['centroid'][0]]
                                    annotation['bbox_geo'] = []
                                    annotation['bbox_rotated_geo'] = []
                                    annotation['object_center_geo'] = []
                                    annotation['keypoints_geo'] = []
                                    annotation['classification'] = 'Undefined'
                                    if 'keypoints' in ann:
                                        annotation['keypoints'] = ann['keypoints']
                                        annotation['num_keypoints'] = len(ann['keypoints'])
                                        if calc_geo:
                                            annotation['keypoints_geo'] = img_geo.pixel_to_geo(ann['keypoints'])
                                    if calc_rotated_bbox:
                                        obj_width = ann['size'][0] / metadata['sensor']['meters_per_pixel']
                                        obj_length = ann['size'][1] / metadata['sensor']['meters_per_pixel']
                                        rotation = (math.degrees(ann['rotation'][2]) - metadata['sensor']['azimuth']) % 360
                                        annotation['bbox_rotated'] = [ann['centroid'][1], ann['centroid'][0], obj_width, obj_length, rotation]
                                        if calc_geo:
                                            bbox_rotated_coords = get_rotated_bbox_coordinates(*annotation['bbox_rotated'])
                                            annotation['bbox_rotated_geo'] = img_geo.pixel_to_geo(bbox_rotated_coords)
                                    if calc_geo:
                                        annotation['bbox_geo'] = img_geo.pixel_to_geo(annotation['bbox'])
                                        annotation['object_center_geo'] = img_geo.pixel_to_geo(annotation['object_center'])
                                    if 'classification' in ann:
                                        annotation['classification'] = ann['classification']
                                        if ann['classification'] not in classification_list:
                                            classification_list.append(ann['classification'])
                                    annid += 1
                                    if not first: of.write(', ')
                                    json.dump(annotation, of)
                                    first = False
                                    break
            img_path = os.path.join(imgdir, anns['filename'])
            bands = get_image_bands(img_path)
            
            # add geococo file data
            file_data = {
                'checksum':         generate_file_checksum(img_path),
                'mimetype':         mimetypes.guess_type(img_path)[0],
                'pixel_bounds':     create_bounding_box_geojson(0, 0, img_width, img_height),
                'geo_bounds':       create_bounding_box_geojson(lon, bottom, lat, right),
                'band_names':       bands,
                'memory_size':      os.path.getsize(img_path)
            }
            img_memory_size += file_data['memory_size']

            # add chipping and acquisition data
            chipping_data = {}
            acquisition_data = {}
            chipping_pairs = {'parent_name': 'name', 'parent_checksum':'checksum', 'parent_mimetype':'mimetype'}
            acquisition_env_pairs = {'image_type': 'image_type', 'acquisition_time_earliest': 'datetime', 'acquisition_time_latest': 'datetime', 
                                'sun_altitude': 'sun_angle', 'sun_azimuth': 'sun_azimuth', 'rendering_tool': 'renderer', 'cloud_cover': 'cloud_cover',
                                'platform': 'platform', 'classification': 'classification'}
            acquisition_sensor_pairs = {'look_angle': 'look_angle', 'azimuthal_angle': 'azimuth'}
            if 'environment' in metadata:
                for key, value in chipping_pairs.items():
                    if value in metadata['environment']:
                        chipping_data[key] = metadata['environment'][value]
                for key, value in acquisition_env_pairs.items():
                    if value in metadata['environment']:
                        acquisition_data[key] = metadata['environment'][value]
            if 'sensor' in metadata:
                for key, value in acquisition_sensor_pairs.items():
                    if value in metadata['sensor']:
                        acquisition_data[key] = metadata['sensor'][value]
                if 'meters_per_pixel' in metadata['sensor']:
                    acquisition_data['gsd'] = [metadata['sensor']['meters_per_pixel'], metadata['sensor']['meters_per_pixel']]
            acquisition_data['is_synthetic'] = True
            if 'classification' in acquisition_data:
                if acquisition_data['classification'] not in classification_list:
                    classification_list.append(acquisition_data['classification'])

            date = datetime.datetime.now().isoformat()
            if 'date' in metadata: date = metadata['date']
            imgdata = {
                'id':               imgid, 
                'file_name':        metadata['filename'], 
                'date_captured':    date, 
                'license':          0, 
                'width':            img_width,
                'height':           img_height,
                'file_data':        file_data,
                'chipping_data':    chipping_data,
                'acquisition_data': acquisition_data}

            if imgdata['width'] not in img_width_list:
                img_width_list.append(imgdata['width'])
            if imgdata['height'] not in img_height_list:
                img_height_list.append(imgdata['height'])

            cocodata['images'].append(imgdata)
            imgid += 1
            img_count += 1
        sorted_cats = dict(sorted(cats.items()))
        for class_num, cat in sorted_cats.items():
            if class_num == 0: continue
            cocodata['categories'].append({
                'id':               class_num, 
                'name':             cat[-1],
                'supercategory':    cat[0]
            })

        # add geococo info fields
        if len(img_width_list) == 1:
            cocodata['info']['image_width'] = img_width_list[0]
        if len(img_height_list) == 1:
            cocodata['info']['image_height'] = img_height_list[0]
        cocodata['info']['image_count'] = img_count
        cocodata['info']['memory_size'] = img_memory_size
        
        if len(classification_list) == 1:
            cocodata['info']['classification'] = classification_list[0]
        elif len(classification_list) > 1:
            cocodata['info']['classification'] = get_highest_classification(classification_list)

        of.write('], ')
        of.write(f'"info": {json.dumps(cocodata["info"])}, ')
        of.write(f'"licenses": {json.dumps(cocodata["licenses"])}, ')
        of.write(f'"images": {json.dumps(cocodata["images"])}, ')
        of.write(f'"categories": {json.dumps(cocodata["categories"])}')
        of.write('}')