# -*- coding: utf-8 -*-
"""Annotators for extracting high-level metadata about the images in the input.
"""

from numpy import abs as npabs, mean, percentile, prod, zeros
from cv2 import cvtColor, calcHist, resize, COLOR_BGR2HSV

from .abstract import BatchAnnotator


class DiffAnnotator(BatchAnnotator):
    """Annotator for detecting differences between frames."""

    def __init__(self, **kwargs):

        self.quantiles = kwargs.get("quantiles", [])
        self.size = kwargs.get("size", 32)
        self.bins = kwargs.get("bins", 16)

    def annotate_batch(self, batch):
        """Annotate the batch of frames with the difference annotator.

        Args:
            batch (FrameBatch): A batch of images to annotate.

        Returns:
            A list of dictionaries containing the video name, frame, average
            value, and any requested quantile and histogram differences.
        """

        output = {"frame": batch.get_frame_names()}
        output["avg_value"] = _average_value_batch(batch)

        for quant in self.quantiles:
            key = "q{0:d}".format(quant)
            output[key] = _l1_quantile(batch, quantile=quant, size=self.size)

            key = "h{0:d}".format(quant)
            output[key] = _hist_diffs(batch, quantile=quant, bins=self.bins)

        return {"diff": output}


def _l1_quantile(batch, quantile=50, size=32):
    """Compute differences between subsequent frames in a batch."""
    bsize = batch.bsize
    msize = bsize + 1
    assert msize <= batch.get_frames().shape[0]

    simg = zeros((msize, size, size, 3))
    for iran in range(msize):
        fsmall = resize(batch.get_frames()[iran, :, :, :], (size, size))
        fsmall_hsv = cvtColor(fsmall, COLOR_BGR2HSV)
        simg[iran, :, :, :] = fsmall_hsv

    norm = simg[slice(0, bsize), :, :, :] - simg[slice(1, bsize + 1), :, :, :]

    return percentile(npabs(norm), q=quantile, axis=(1, 2, 3))


def _hist_diffs(batch, quantile=50, bins=16):
    """Compute differences between HSV histograms across a batch."""
    bsize = batch.bsize
    msize = bsize + 1
    assert msize <= batch.get_frames().shape[0]

    hist_vals = _hsv_hist(batch, msize, bins=bins)
    norm = hist_vals[slice(0, bsize), :] - hist_vals[slice(1, bsize + 1), :]
    norm = norm / prod(batch.get_frames().shape[1:4]) * 100

    return percentile(npabs(norm), q=quantile, axis=(1))


def _hsv_hist(batch, msize, bins=16):
    """Compute histogram counts from a batch of images."""
    hist_vals = zeros((msize, bins * 3))
    for iran in range(msize):
        hsv = cvtColor(batch.get_frames()[iran, :, :, :], COLOR_BGR2HSV)
        for i in range(3):
            hist = calcHist([hsv], [i], None, [bins], [0, 256]).flatten()
            hist_vals[iran, slice(i * bins, (i + 1) * bins)] = hist

    return hist_vals


def _average_value_batch(batch):
    """Compute the average value across a batch of images."""
    img = batch.get_batch()
    return mean(img, axis=(1, 2, 3))
