# -*- coding: utf-8 -*-
"""Video files.
"""

from math import ceil
from numpy import zeros, uint8
from pandas import DataFrame
from cv2 import (
    VideoCapture,
    CAP_PROP_FPS,
    CAP_PROP_FRAME_COUNT,
    CAP_PROP_FRAME_HEIGHT,
    CAP_PROP_FRAME_WIDTH,
    CAP_PROP_POS_MSEC,
)

from .utils import _expand_path


class VideoFrameInput:
    """An input object for extracting single frames from an input video."""

    def __init__(self, input_path):
        """Construct a new input from a video file.

        Args:
            input_path (str): Path to the video file. Can be any file readable
                by the OpenCV function VideoCapture.
            bsize (int): Number of frames to include in a batch. Defaults to
                256.
        """
        self.input_path = _expand_path(input_path)[0]
        self.meta = None
        self.fcount = -1
        self.finished = False
        self._video_cap = None
        self.reset()

        super().__init__()

    def reset(self):
        """Open connection to the video file."""
        self.fcount = -1
        self.finished = False

        self._video_cap = VideoCapture(self.input_path)
        self._ftotal = int(self._video_cap.get(CAP_PROP_FRAME_COUNT))
        self.meta = self._metadata()

    def next_frame(self):
        """Get the next frame."""
        if self.finished:
            return

        # get the next frame and return
        self.fcount = self.fcount + 1
        _, frame = self._video_cap.read()
        self.finished = self._ftotal == (self.fcount + 1)
        return frame

    def get_metadata(self):
        """Return metadata in a format to put into DVTOutput"""
        return {"meta": DataFrame(self.meta, index=[0])}

    def _metadata(self):
        """Fill metadata attribute using metadata from the video source."""
        path, bname, filename, file_extension = _expand_path(self.input_path)
        return {
            "type": "video",
            "fps": self._video_cap.get(CAP_PROP_FPS),
            "frames": int(self._video_cap.get(CAP_PROP_FRAME_COUNT)),
            "height": int(self._video_cap.get(CAP_PROP_FRAME_HEIGHT)),
            "width": int(self._video_cap.get(CAP_PROP_FRAME_WIDTH)),
            "input_path": path,
            "input_bname": bname,
            "input_filename": filename,
            "input_file_extension": file_extension,
        }


class VideoBatchInput:
    """An input object for extracting batches of images from an input video."""

    def __init__(self, input_path, bsize=256):
        """Construct a new input from a video file.

        Args:
            input_path (str): Path to the video file. Can be any file readable
                by the OpenCV function VideoCapture.
            bsize (int): Number of frames to include in a batch. Defaults to
                256.
        """
        self.input_path = _expand_path(input_path)[0]
        self.bsize = bsize
        self.meta = None
        self.fcount = 0
        self.finished = False
        self.start = 0
        self.end = 0
        self.max_batch = 0
        self._video_cap = None
        self._img = None
        self._continue_read = True
        self.reset()

        super().__init__()

    def reset(self):
        """Open connection to the video file."""
        # start settings to
        self.fcount = 0
        self.finished = False
        self.start = 0
        self.end = 0
        self._video_cap = VideoCapture(self.input_path)
        self.meta = self._metadata()
        self.max_batch = ceil(self.meta["frames"] / self.bsize)

        self._img = zeros(
            (self.bsize * 2, self.meta["height"], self.meta["width"], 3),
            dtype=uint8,
        )
        self._fill_bandwidth()  # fill the buffer with the first batch
        self._continue_read = True  # is there any more input left

    def next_batch(self):
        """Move forward one batch and return the current FrameBatch object.

        Returns:
            A FrameBatch object that contains the next set of frames.
        """

        if self.finished:
            return

        # shift window over by one bandwidth
        self._img[: self.bsize, :, :, :] = self._img[self.bsize :, :, :, :]

        # fill up the bandwidth; with zeros at and of video input
        if self._continue_read:
            self._fill_bandwidth()
        else:
            self.finished = True
            self._img[self.bsize :, :, :, :] = 0

        # update counters
        frame_start = self.fcount
        self.start = self.end
        self.end = self._video_cap.get(CAP_PROP_POS_MSEC)
        self.fcount = self.fcount + self.bsize

        # get frame names
        fnames = list(range(int(frame_start), int(frame_start + self.bsize)))

        # return batch of frames.
        return FrameBatch(
            img=self._img,
            start=self.start,
            end=self.end,
            finished=self.finished,
            fnames=fnames,
            bnum=(frame_start // self.bsize),
        )

    def get_metadata(self):
        """Return metadata in a format to put into a DVTOutput object."""
        return {"meta": DataFrame(self.meta, index=[0])}

    def _metadata(self):
        """Fill metadata attribute using metadata from the video source."""
        path, bname, filename, file_extension = _expand_path(self.input_path)
        return {
            "type": "video",
            "fps": self._video_cap.get(CAP_PROP_FPS),
            "frames": int(self._video_cap.get(CAP_PROP_FRAME_COUNT)),
            "height": int(self._video_cap.get(CAP_PROP_FRAME_HEIGHT)),
            "width": int(self._video_cap.get(CAP_PROP_FRAME_WIDTH)),
            "input_path": path,
            "input_bname": bname,
            "input_filename": filename,
            "input_file_extension": file_extension,
        }

    def _fill_bandwidth(self):
        """Read in the next set of frames from disk and store results.

        This should not be called directly, but only through the next_batch
        method. Otherwise the internal counters will become inconsistent.
        """
        for idx in range(self.bsize):
            self._continue_read, frame = self._video_cap.read()
            if self._continue_read:
                self._img[idx + self.bsize, :, :, :] = frame
            else:
                self._img[idx + self.bsize, :, :, :] = 0


class FrameBatch:
    """A collection of frames and associated metadata.

    The batch contains an array of size (bsize * 2, width, height, 3). At the
    start and end of the video file, the array is padded with zeros (an all
    black frame). The batch includes twice as many frames as given in the
    batch size, but an annotator should only return results from the first
    half of the data (the "batch"). The other data is included for annotators
    that need to look ahead of the current, such as the cut detectors.

    Attributes:
        img (np.array): A four-dimensional array containing pixels from the
            next 2*bsize of images.
        start (float): Time code at the start of the current batch.
        end (float): Time code at the end of the current batch.
        fnames (list): Names of frames in the batch.
        bnum (int): The batch number.
        bsize (int): Number of frames in a batch.
    """

    def __init__(self, **kwargs):
        self.img = kwargs.get("img")
        self.start = kwargs.get("start")
        self.end = kwargs.get("end")
        self.fnames = kwargs.get("fnames")
        self.bnum = kwargs.get("bnum")
        self.bsize = self.img.shape[0] // 2

    def get_frames(self):
        """Return the entire image dataset for the batch.

        Use this method if you need to look ahead at the following batch for
        an annotator to work. Images are given in RGB space.

        Returns:
            A four-dimensional array containing pixels from the current and
            next batches of data.
        """
        return self.img

    def get_batch(self):
        """Return image data for just the current batch.

        Use this method unless you have a specific need to look ahead at new
        values in the data. Images are given in RGB space.

        Returns:
            A four-dimensional array containing pixels from the current batch
            of images.
        """
        return self.img[: self.bsize, :, :, :]

    def get_frame_names(self):
        """Return frame names for the current batch of data.

        Returns:
            A list of names of length equal to the batch size.
        """
        return self.fnames
