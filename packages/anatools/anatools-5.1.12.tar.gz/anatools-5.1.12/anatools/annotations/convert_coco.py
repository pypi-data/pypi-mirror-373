import json
import os
import datetime
from PIL import Image


def create_cocodata():
    cocodata = dict()
    cocodata["info"] = {
        "description": "Rendered.AI Synthetic Dataset",
        "url": "https://rendered.ai/",
        "contributor": "info@rendered.ai",
        "version": "1.0",
        "year": str(datetime.datetime.now().year),
        "date_created": datetime.datetime.now().isoformat(),
    }
    cocodata["licenses"] = [{"id": 0, "url": "https://rendered.ai/", "name": "Rendered.AI License"}]
    cocodata["images"] = list()
    cocodata["categories"] = list()
    cocodata["annotations"] = list()
    return cocodata


def index_metadata_by_filename(metadir):
    """Pre-index all metadata files by their filename field for O(1) lookup"""
    metadata_index = {}

    for mf in os.listdir(metadir):
        if not mf.endswith(".json"):
            continue
        try:
            filepath = os.path.join(metadir, mf)
            with open(filepath, "r") as f:
                metadata = json.load(f)
                filename = metadata.get("filename")
                if filename:
                    metadata_index[filename] = metadata
        except (json.JSONDecodeError, IOError):
            continue

    return metadata_index


def get_image_dimensions(imgpath):
    """Cache image dimensions to avoid repeated file opens"""
    try:
        with Image.open(imgpath) as im:
            return im.size
    except:
        return None, None


def process_annotation_file(ann_file_path, metadata_index, imgdir, mapping=None):
    """Process a single annotation file and return the annotations and image data"""
    with open(ann_file_path, "r") as f:
        anns = json.load(f)

    image_filename = anns.get("filename")
    if not image_filename:
        return None, None, None

    metadata = metadata_index.get(image_filename)
    if metadata is None:
        return None, None, None

    annotations = []
    categories = {}

    for obj in metadata["objects"]:
        if mapping is None:
            for ann in anns["annotations"]:
                if ann["id"] == obj["id"]:
                    obj_type = obj["type"]
                    annotations.append(
                        {
                            "obj_id": ann["id"],
                            "obj_type": obj_type,
                            "segmentation": ann["segmentation"],
                            "bbox": ann["bbox"],
                            "area": ann["bbox"][2] * ann["bbox"][3],
                        }
                    )
                    break
        else:
            for prop in mapping["properties"]:
                if eval(prop):
                    for ann in anns["annotations"]:
                        if ann["id"] == obj["id"]:
                            class_num = mapping["properties"][prop]
                            categories[class_num] = mapping["classes"][class_num]
                            annotations.append(
                                {
                                    "obj_id": ann["id"],
                                    "category_id": class_num,
                                    "segmentation": ann["segmentation"],
                                    "bbox": ann["bbox"],
                                    "area": ann["bbox"][2] * ann["bbox"][3],
                                }
                            )
                            break

    # Prepare image data
    date = metadata.get("date", datetime.datetime.now().isoformat())
    imgdata = {"file_name": metadata["filename"], "date_captured": date, "license": 0}

    # Get image dimensions
    try:
        imgdata["width"] = metadata["sensor"]["resolution"][0]
        imgdata["height"] = metadata["sensor"]["resolution"][1]
    except:
        width, height = get_image_dimensions(os.path.join(imgdir, image_filename))
        if width and height:
            imgdata["width"] = width
            imgdata["height"] = height

    return annotations, imgdata, categories


def convert_coco(datadir, outdir, mapping=None):
    """Optimized COCO conversion with pre-indexing and optional parallel processing"""

    annsdir = os.path.join(datadir, "annotations")
    metadir = os.path.join(datadir, "metadata")
    imgdir = os.path.join(datadir, "images")

    # Pre-index metadata for O(1) lookup
    print("Indexing metadata files...")
    metadata_index = index_metadata_by_filename(metadir)
    print(f"Indexed {len(metadata_index)} metadata files")

    # Get sorted list of annotation files
    annsfiles = sorted([f for f in os.listdir(annsdir) if f.endswith(".json")])

    cocodata = create_cocodata()
    cats = {0: [None, "coco_background"]}
    all_annotations = []
    all_images = []

    imgid = 0
    annid = 0

    # Sequential processing
    for f in annsfiles:
        annotations, imgdata, categories = process_annotation_file(
            os.path.join(annsdir, f), metadata_index, imgdir, mapping
        )

        if annotations and imgdata:
            if mapping is None:
                for ann in annotations:
                    obj_type = ann["obj_type"]
                    if [None, obj_type] in cats.values():
                        class_num = [k for k, v in cats.items() if v == [None, obj_type]][0]
                    else:
                        class_num = len(cats.keys())
                        cats[class_num] = [None, obj_type]

                    annotation = {
                        "id": annid,
                        "image_id": imgid,
                        "category_id": class_num,
                        "segmentation": ann["segmentation"],
                        "area": ann["area"],
                        "bbox": ann["bbox"],
                        "iscrowd": 0,
                    }
                    all_annotations.append(annotation)
                    annid += 1
            else:
                cats.update(categories)
                for ann in annotations:
                    annotation = {
                        "id": annid,
                        "image_id": imgid,
                        "category_id": ann["category_id"],
                        "segmentation": ann["segmentation"],
                        "area": ann["area"],
                        "bbox": ann["bbox"],
                        "iscrowd": 0,
                    }
                    all_annotations.append(annotation)
                    annid += 1

            imgdata["id"] = imgid
            all_images.append(imgdata)
            imgid += 1

    # Build categories list
    sorted_cats = dict(sorted(cats.items()))
    for class_num, cat in sorted_cats.items():
        if class_num == 0:
            continue
        cocodata["categories"].append({"id": class_num, "name": cat[-1], "supercategory": cat[0]})

    # Add all data to cocodata
    cocodata["annotations"] = all_annotations
    cocodata["images"] = all_images

    # Write to file at once
    output_path = os.path.join(outdir, "coco.json")
    with open(output_path, "w") as f:
        json.dump(cocodata, f)

    print(f"Conversion complete: {len(all_images)} images, {len(all_annotations)} annotations")
    return cocodata
