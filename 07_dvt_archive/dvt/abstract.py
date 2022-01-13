# -*- coding: utf-8 -*-
"""Abstract classes for running the Distant Viewing Toolkit.
"""

from abc import ABC, abstractmethod

from pandas import DataFrame
from numpy import ndarray


class ImageAnnotator(ABC):  # pragma: no cover
    """Base class for annotating a single frame.

    Subclasses of this abstract class take subsets of frames, composed as
    FrameBatch objects, and return annotated data. Several common annotations
    are implemented in the toolkit. Users can create their own annotations
    by implementing the __init__ and annotate_image methods.
    """

    def annotate(self, img, **kwargs):
        """Annotate an image."""
        return _process_output_values(self.annotate_image(img, **kwargs))

    @abstractmethod
    def annotate_image(self, img):
        """Annotate an image."""
        return


class BatchAnnotator(ABC):  # pragma: no cover
    """Base class for annotating a batch of images."""

    def annotate(self, batch, **kwargs):
        """Annotate a batch of images."""
        return _process_output_values(self.annotate_batch(batch, **kwargs))

    @abstractmethod
    def annotate_batch(self, batch):
        """Annotate a batch of images."""
        return


def _process_output_values(output_vals):
    """Take input and create pandas data frame."""
    if output_vals is None:
        return

    assert isinstance(output_vals, dict)

    output = {}
    for key, value in output_vals.items():
        if isinstance(value, DataFrame):
            output[key] = value
        else:
            assert isinstance(value, dict)

            # convert numpy array into a list of arrays for pandas
            for skey in value.keys():
                if isinstance(value[skey], ndarray) and len(value[skey].shape) > 1:
                    value[skey] = [x for x in value[skey]]

            try:
                dframe = DataFrame(value)
            except ValueError as _:
                dframe = DataFrame(value, index=[0])

            output[key] = dframe

    return output
