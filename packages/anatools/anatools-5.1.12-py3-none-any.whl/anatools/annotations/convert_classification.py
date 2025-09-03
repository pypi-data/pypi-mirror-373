import json
import os

def convert_classification(datadir, outdir, mapping=None):

    annsdir = os.path.join(datadir, "annotations")
    metadir = os.path.join(datadir, "metadata")
    imgdir = os.path.join(datadir, "images")
    classification = {}

    for img in os.listdir(imgdir):
        imgbase, imgext = os.path.splitext(img)
        metadata = json.load(open(os.path.join(metadir, imgbase + "-metadata.json")))
        anns = json.load(open(os.path.join(annsdir, imgbase + "-ana.json")))
        for obj in metadata['objects']:
            if mapping is None:
                for ann in anns['annotations']:
                    if ann['id'] == obj['id']:
                        class_name = obj['type']
                        if class_name not in classification: classification[class_name] = []
                        if img not in classification[class_name]: classification[class_name].append(img)
            else:
                for prop in mapping['properties']:
                    if eval(prop):
                        for ann in anns['annotations']:
                            if ann['id'] == obj['id']: 
                                class_num = mapping['properties'][prop]
                                class_name = mapping['classes'][class_num][-1]
                                if class_name not in classification: classification[class_name] = []
                                if img not in classification[class_name]: classification[class_name].append(img)

    with open(os.path.join(outdir,'classification.json'), 'w+') as cf:
        json.dump(classification, cf)

