#!/usr/bin/env python3

from os import listdir, mkdir
from os.path import isfile, isdir, join, splitext, exists

import numpy as np
import pandas as pd

from dvt import (
    VideoFrameInput,
    VideoBatchInput,
    AverageAnnotator,
    InstanceAnnotator,
    LVISAnnotator,
    KeypointsAnnotator,
    PanopticAnnotator,
    FaceAnnotator,
    FaceDetectMtcnn,
    FaceEmbedVgg2,
    EmbedAnnotator,
    EmbedImageKerasResNet50,
    DiffAnnotator,
    CutAggregator,
    SizeAnnotator,
    DVTOutput,
    imread
)


# Create the output directories and collect file paths to process
img_dirs = listdir(join("inter", "imgs"))
img_paths = []
for dname in img_dirs:
    if not isdir(join("inter", "nn", dname)):
        mkdir(join("inter", "nn", dname))
    img_paths += [(dname, x) for x in listdir(join("inter", "imgs", dname))]

# Create annotators
annotation_embd = EmbedAnnotator(embedding=EmbedImageKerasResNet50())
annotation_face = FaceAnnotator(
    detector=FaceDetectMtcnn(), embedding=FaceEmbedVgg2()
)
annotation_inst = InstanceAnnotator()
annotation_kpnt = KeypointsAnnotator()
annotation_lvis = LVISAnnotator()
annotation_pano = PanopticAnnotator()
annotation_size = SizeAnnotator()

for input_path in img_paths:
    try:
        this_id = splitext(input_path[1])[0]
        embd_out = join("inter", "nn", input_path[0], this_id + "_embd.csv")
        face_out = join("inter", "nn", input_path[0], this_id + "_face.csv")
        inst_out = join("inter", "nn", input_path[0], this_id + "_inst.csv")
        kpnt_out = join("inter", "nn", input_path[0], this_id + "_kpnt.csv")
        lvis_out = join("inter", "nn", input_path[0], this_id + "_lvic.csv")
        pano_out = join("inter", "nn", input_path[0], this_id + "_pano.csv")
        size_out = join("inter", "nn", input_path[0], this_id + "_size.csv")

        if True:
            #if not exists(embd_out):
            # Load the image
            img = imread(join("inter", "imgs", input_path[0], input_path[1]))

            # Create the output object
            output = DVTOutput()
            output.set_meta("collection", input_path[0])
            output.set_meta("filename", this_id)

            # Run the annotations (this is slow)
            output.add_annotation(annotation_embd.annotate(img))
            output.add_annotation(annotation_face.annotate(img))
            output.add_annotation(annotation_inst.annotate(img))
            output.add_annotation(annotation_kpnt.annotate(img))
            output.add_annotation(annotation_lvis.annotate(img))
            output.add_annotation(annotation_pano.annotate(img))
            output.add_annotation(annotation_size.annotate(img))

            # Save the dataframes as individual files
            df = output.get_dataframes()
            df_embed = df["embed"]
            np.savetxt(embd_out, df_embed.embed.values[0], delimiter=',')
            df_embed.to_csv(embd_out, index=False)
            df["face"].to_csv(face_out, index=False)
            df["instance"].to_csv(inst_out, index=False)
            df["keypoint"].to_csv(kpnt_out, index=False)
            df["lvis"].to_csv(lvis_out, index=False)
            df["panoptic"].to_csv(pano_out, index=False)
            df["size"].to_csv(size_out, index=False)

            print("Done with {0:s}".format(embd_out))

    except:
        print("Error with {0:s}/{1:s}".format(input_path[0], input_path[1]))
