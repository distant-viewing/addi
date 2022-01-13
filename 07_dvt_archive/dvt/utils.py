# -*- coding: utf-8 -*-
"""Utility functions used across the toolkit.

Public methods may be useful in producing new annotators, aggregators, and
pipeline methods.
"""

from json import loads, dump
from os.path import abspath, expanduser, isdir, basename, splitext
from os import makedirs


def _check_out_dir(output_dir, should_exist=False):
    if output_dir is not None:
        output_dir = abspath(expanduser(output_dir))
        if should_exist:
            assert isdir(output_dir)
        elif not isdir(output_dir):
            makedirs(output_dir)

    return output_dir


def _expand_path(path):
    path = abspath(expanduser(path))
    bname = basename(path)
    filename, file_extension = splitext(bname)
    return path, bname, filename, file_extension


def _data_to_json(dframe, path=None, exclude_set=None, exclude_key=None):
    if exclude_set is None:
        exclude_set = set()

    if exclude_key is None:
        exclude_key = set()

    output = {}
    for key, value in dframe.items():
        if value.shape[0] != 0 and key not in exclude_set:
            drop_these = set(exclude_key).intersection(set(value.columns))
            output[key] = loads(
                value.drop(drop_these).to_json(orient="records")
            )

    if not path:  # pragma: no cover
        return output

    with open(path, "w+") as fin:
        dump(output, fin)

    return None
