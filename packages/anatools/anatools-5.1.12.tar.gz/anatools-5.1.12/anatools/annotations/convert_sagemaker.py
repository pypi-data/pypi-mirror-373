import os
import json
from PIL import Image, ImageDraw

exts = Image.registered_extensions()
supported_extensions = {ex for ex, f in exts.items() if f in Image.OPEN}

def convert_sagemaker_od(datadir, outdir, mapping = None):
    """ Generate annotations for AWS Sagemaker. Annotation jpegs will be placed in <datadir>/<outputdir>.
    Parameters
    ----------
    datadir : str
        Location of Rendered.ai dataset output.
    outputdir : str
        Name of directory where the results should be written.
    mapfile: str
        The map file used for annotations (YAML only).
    
    Returns
    -------
    """

    annsdir = os.path.join(datadir, "annotations")
    metadir = os.path.join(datadir, "metadata")

    # Get the image shape
    try:
        sample_image_filename = [image for image in os.listdir(datadir + '/images') if os.path.splitext(image)[1].lower() in supported_extensions]
        sample_image = Image.open(datadir + '/images/' + sample_image_filename[0])
        imgshape = [sample_image.size[0], sample_image.size[1], len(sample_image.getbands())]
    except: raise Exception('Could not find a supported image in the dataset images directory.')

    sodcats = list()
    for annsfilename in os.listdir(annsdir):
        with open(os.path.join(annsdir, annsfilename), 'r') as af:
            anns = json.load(af)
        with open(os.path.join(metadir, annsfilename.replace('ana', 'metadata')), 'r') as mf:
            metadata = json.load(mf)

        soddata = dict()
        soddata['file'] = anns['filename']
        soddata['image_size'] = [{'width':imgshape[0],'height':imgshape[1],'depth':imgshape[2]}]
        soddata['annotations'] = list()
        for obj in metadata['objects']:
            if mapping is None:
                for ann in anns['annotations']:
                    if ann['id'] == obj['id']:
                        cat_name = obj['type']  
                        if cat_name not in sodcats: sodcats.append(cat_name)     
                        soddata['annotations'].append({
                            'class_id': sodcats.index(cat_name),
                            'left':     ann['bbox'][0],
                            'top':      ann['bbox'][1],
                            'width':    ann['bbox'][2],
                            'height':   ann['bbox'][3]
                        })
                        break

            else:
                for prop in mapping['properties']:
                    if eval(prop):
                        for ann in anns['annotations']:
                            if ann['id'] == obj['id']:
                                objann = ann
                                break
                        else:  # All the objects from the scene are recorded in metadata; only those in the image are annotated
                            continue

                        rai_cat_id = mapping['properties'][prop]
                        cat = mapping['classes'][rai_cat_id]
                        cat_name = cat[-1]
                        if cat_name not in sodcats: sodcats.append(cat_name)              
                        soddata['annotations'].append({
                            'class_id': sodcats.index(cat_name),
                            'left':     objann['bbox'][0],
                            'top':      objann['bbox'][1],
                            'width':    objann['bbox'][2],
                            'height':   objann['bbox'][3]
                        })
                        break

        soddata['categories'] = list()
        for cId, cName in enumerate(sodcats):
            soddata['categories'].append({'class_id':cId, 'name':cName})
    
        outfile = os.path.join(outdir, '{}.json'.format(anns['filename'].split('.')[0]))
        with open(outfile, 'w') as f:
            json.dump(soddata, f)


def convert_sagemaker_ss(datadir, outdir, mapping=None):
    """ Generate masks for AWS Sagemaker Semantic Segmentation. Mask pngs will be placed in <datadir>/<outputdir>.
    Parameters
    ----------
    datadir : str
        Location of Rendered.ai dataset output.
    outputdir : str
        Name of directory where the results should be written.
    mapfile: str
        The map file used for annotations (YAML only).
    
    Returns
    -------
    """

    annsdir = os.path.join(datadir, "annotations")
    metadir = os.path.join(datadir, "metadata")

    # Get the image shape
    try:
        sample_image_filename = [image for image in os.listdir(datadir + '/images') if os.path.splitext(image)[1].lower() in supported_extensions]
        sample_image = Image.open(datadir + '/images/' + sample_image_filename[0])
        imgshape = [sample_image.size[0], sample_image.size[1], len(sample_image.getbands())]
    except: raise Exception('Could not find a supported image in the dataset images directory.')

    sodcats = ['background']
    for annsfilename in os.listdir(annsdir):
        with open(os.path.join(annsdir, annsfilename), 'r') as af:
            anns = json.load(af)
        with open(os.path.join(metadir, annsfilename.replace('ana', 'metadata')), 'r') as mf:
            metadata = json.load(mf)
        maskimg = Image.new("L", (imgshape[0], imgshape[1]))
        draw = ImageDraw.Draw(maskimg)

        for obj in metadata['objects']:
            if mapping is None:
                for ann in anns['annotations']:
                    if ann['id'] == obj['id']:
                        cat_name = obj['type']  
                        if cat_name not in sodcats: sodcats.append(cat_name)    
                        rai_cat_id = sodcats.index(cat_name)
                        draw.polygon(ann['segmentation'][0], fill=rai_cat_id, outline=rai_cat_id)
                        break
            else:
                for prop in mapping['properties']:
                    if eval(prop):
                        for ann in anns['annotations']:
                            if ann['id'] == obj['id']:
                                objann = ann
                                break
                        rai_cat_id = mapping['properties'][prop]
                        draw.polygon(objann['segmentation'][0], fill=rai_cat_id, outline=rai_cat_id)
                        break

        maskimg.save(os.path.join(outdir, f'{anns["filename"].split(".")[0]}.png'))

    with open(os.path.join(outdir, 'classes.txt'), 'w') as tf:
        for i in range(len(sodcats)):
            if i == 0: continue
            tf.write(f'{i} {sodcats[i]}\n')