# -*- coding: utf-8 -*-
"""Distant Viewing Toolkit for the Analysis of Visual Culture

The Distant TV Toolkit is a Python package designed to facilitate the
computational analysis of visual culture. It contains low-level architecture
for applying state-of-the-art computer vision algorithms to still and moving
images. The higher-level functionality of the toolkit allows users to quickly
extract semantic metadata from digitized collections. Extracted information
can be visualized for search and discovery or aggregated and analyzed to find
patterns across a corpus.
"""

from cv2 import imread, imwrite, imshow

from .abstract import ImageAnnotator, BatchAnnotator
from .annotate import SizeAnnotator, ImwriteAnnotator, AverageAnnotator
from .aggregate import CutAggregator
from .batch import DiffAnnotator
from .detectron import (
    InstanceAnnotator,
    LVISAnnotator,
    CityscapesAnnotator,
    KeypointsAnnotator,
    PanopticAnnotator,
)
from .keras import (
    FaceAnnotator,
    FaceDetectMtcnn,
    FaceEmbedVgg2,
    EmbedAnnotator,
    EmbedImageKeras,
    EmbedImageKerasResNet50,
)
from .output import DVTOutput
from .video import VideoFrameInput, VideoBatchInput, FrameBatch

__version__ = "0.4.0"
