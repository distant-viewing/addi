# -*- coding: utf-8 -*-
"""Aggregators.
"""

from pandas import DataFrame


class CutAggregator:
    """Uses difference between successive frames to detect cuts.

    This aggregator uses information from the difference annotator to detect
    the cuts.

    Attributes:
        min_len (int): minimum allowed length of a cut.
        ignore_vals (dict): Dictionary of cutoffs that cause a frame to be
            ignored for the purpose of detecting cuts. Keys indicate the
            variables in the differences output and values show the minimum
            value allowed for a frame to be considered for a cut. Typically
            used to ignore frames that are too dark (i.e., during fades). Set
            to None (default) if no ignored values are needed.
        cut_vals (dict): Dictionary of cutoffs that cause a frame to be
            considered a cut. Keys indicate the variables in the differences
            output and values are the cutoffs. Setting to None (default) will
            return no cuts.
        name (str): A description of the aggregator. Used as a key in the
            output data.
    """

    def __init__(self, **kwargs):

        self.ignore_vals = kwargs.get("ignore_vals", {})
        self.cut_vals = kwargs.get("cut_vals", None)
        self.min_len = kwargs.get("min_len", 1)

    def aggregate(self, diff):
        """Aggregate difference annotator.

        Args:
            diff (DataFrame): output of the difference annotator

        Returns:
            A dictionary frame giving the detected cuts.
        """

        # grab the data, initialize counters, and create output `cuts`
        ignore_this_frame = True
        current_cut_start = 0
        cuts = {"frame_start": [], "frame_end": []}

        # cycle through frames and collection shots; assumes that the data is
        # ordered by frame
        mlen = len(diff["frame"])
        for ind in range(mlen):
            this_frame = diff["frame"][ind]

            # check to see if we should ignore the next frame; by default we
            # ignore the phantom frame at the end of the video at time T+1.
            ignore_next_frame = False
            if (ind + 1) >= mlen:
                ignore_next_frame = True
            else:
                for key, coff in self.ignore_vals.items():
                    if diff[key][ind + 1] < coff:  # pragma: no cover
                        ignore_next_frame = True
                        break

            # check if there should be a cut; note: this is defined such that
            # the this_frame is the *last* frame in the current cut, not the
            # first in the next cut
            long_flag = (this_frame - current_cut_start + 1) >= self.min_len
            if long_flag and not ignore_next_frame:
                cut_detect = True
                for key, coff in self.cut_vals.items():
                    if diff[key][ind] < coff:
                        cut_detect = False
                        break
            else:
                cut_detect = False

            if ignore_next_frame and not ignore_this_frame:
                cut_detect = True

            # if `cut_detect` at this point, then we want to finish the active
            # cut with the current frame
            if cut_detect:
                cuts["frame_start"].append(current_cut_start)
                cuts["frame_end"].append(this_frame)

            if cut_detect or ignore_next_frame:
                current_cut_start = this_frame + 1

            # push forward the ignore flag
            ignore_this_frame = ignore_next_frame

        return DataFrame(cuts)
