# -*- coding: utf-8 -*-
"""Annotators for extracting high-level metadata about the images in the input.
"""

from os.path import join

from cv2 import imwrite, resize, cvtColor, COLOR_BGR2HSV

from .abstract import ImageAnnotator
from .utils import _check_out_dir


class SizeAnnotator(ImageAnnotator):
    """Annotator for grabbing metadata about the images in the batch.

    Attributes:
        name (str): A description of the aggregator. Used as a key in the
            output data.
    """

    def annotate_image(self, img):
        """Annotate the batch of frames with the image annotator.

        Args:
            img (Array)

        Returns:
            A dictionary containing the height and width of the input image.
        """
        output = {"size": {"height": [img.shape[0]], "width": [img.shape[1]]}}
        return output


class AverageAnnotator(ImageAnnotator):
    """Annotator for grabbing"""

    def annotate_image(self, img):
        """Annotate the batch of frames with the image annotator.

        Args:
            img (Array)

        Returns:
            A dictionary containing the average value and saturation of the
            image.
        """
        img_hsv = cvtColor(img, COLOR_BGR2HSV)
        output = {
            "average": {
                "saturation": [img_hsv[:, :, 1].mean()],
                "val": [img_hsv[:, :, 2].mean()],
            }
        }
        return output


class ImwriteAnnotator(ImageAnnotator):
    """Annotator for saving still images from an input.

    The annotate method of this annotator does not return any data. It is
    useful only for its side effects.
    """

    def __init__(self, **kwargs):
        self.output_dir = _check_out_dir(kwargs["output_dir"])
        self.size = kwargs.get("size", None)

        super().__init__(**kwargs)

    def annotate_image(self, img, **kwargs):
        """Annotate the images."""
        opath = join(self.output_dir, kwargs.get("fname", "figure.png"))

        if self.size is not None:
            scale = img.shape[1] / self.size
            new_size = (int(img.shape[2] // scale), int(self.size))
            img_resize = resize(img, new_size)
            imwrite(filename=opath, img=img_resize)
        else:
            imwrite(filename=opath, img=img)
