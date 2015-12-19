#!/usr/bin/python
# coding: utf-8

r"""utils module of aocxchange"""

from __future__ import print_function

import os


def path_from_file(file_origin, relative_path):
    r"""Builds an absolute path from a file using a relative path

    Parameters
    ----------
    file_origin : str
    relative_path : str
    """
    dir_of_file_origin = os.path.dirname(os.path.realpath(file_origin))
    return os.path.abspath(os.path.join(dir_of_file_origin, relative_path))


def extract_file_extension(filename):
    r"""Extract the extension from the file name

    Parameters
    ----------
    filename : str
        Path to the file

    """
    return (filename.split("/")[-1]).split(".")[-1]
