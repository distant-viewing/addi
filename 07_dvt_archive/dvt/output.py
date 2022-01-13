# -*- coding: utf-8 -*-
"""Video files.
"""

from pandas import concat

from .utils import _data_to_json


class DVTOutput:
    """An object for storing the output of annotations and aggregations."""

    def __init__(self):
        """Construct a new output object."""
        self._data = {}
        self._meta = {}

    def add_annotation(self, annotation):
        """Open connection to the video file."""
        assert isinstance(annotation, dict)

        for key, value in annotation.items():
            if not key in self._data:
                self._data[key] = []

            self._data[key].append(_add_meta(value, self._meta))

    def set_meta(self, key, value):
        """Set a metadata variable."""
        self._meta[key] = value

    def reset_meta(self):
        """Reset the metadata."""
        self._meta = {}

    def get_dataframes(self):
        """Return data frames as a dictionary."""
        output = {}
        for key, value in self._data.items():
            output[key] = concat(value, ignore_index=True)

        return output

    def get_json(self, path=None, exclude_set=None, exclude_key=None):
        """Return or save json object."""
        return _data_to_json(
            self.get_dataframes(), path, exclude_set, exclude_key
        )


def _add_meta(annotation, meta):
    for key, value in meta.items():
        annotation.insert(0, key, value)

    return annotation
