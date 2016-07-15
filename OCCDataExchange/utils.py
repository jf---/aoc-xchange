#!/usr/bin/env python
# coding: utf-8

r"""utils module of OCCDataExchange"""

from __future__ import print_function

import logging
import os

logger = logging.getLogger(__name__)


def path_from_file(file_origin, relative_path):
    r"""Builds an absolute path from a file using a relative path

    Parameters
    ----------
    file_origin : str
        Full / absolute path to he file from which the path is to be built
    relative_path : str
        The relative path from file_origin

    Returns
    -------
    str
        Absolute file path

    """
    # Check the file exists
    if not os.path.isfile(file_origin):
        msg = "File %s not found." % file_origin
        logger.error(msg)
        raise AssertionError(msg)
    dir_of_file_origin = os.path.dirname(os.path.realpath(file_origin))
    return os.path.abspath(os.path.join(dir_of_file_origin, relative_path))


def extract_file_extension(filename):
    r"""Extract the extension from the file name

    Parameters
    ----------
    filename : str
        Path to the file

    """
    if "." not in filename.split("/")[-1]:
        return ""
    else:
        return (filename.split("/")[-1]).split(".")[-1]


def shape_to_file(shape, pth, filename, format='iges'):
    """write a Shape to a .iges .brep .stl or .step file"""

    from OCCDataExchange.brep import BrepExporter
    from OCCDataExchange.iges import IgesExporter
    from OCCDataExchange.step import StepExporter
    from OCCDataExchange.stl import StlExporter

    _pth = os.path.join(pth, filename)
    assert not os.path.isdir(_pth), 'wrong path, filename'
    _file = str("%s.%s" % (_pth, format))

    _formats = ['iges', 'igs', 'step', 'stp', 'brep', 'stl']
    assert format in _formats, '%s is not a readable format, should be one of %s ' % (format, _formats)

    if format in ['iges', 'igs']:
        writer = IgesExporter(_file)
        writer.add_shape(shape)
        writer.write_file()
        return _file

    elif format in ['step', 'stp']:
        writer = StepExporter(_file)
        writer.add_shape(shape)
        writer.write_file()
        return _file

    elif format == 'brep':
        writer = BrepExporter(_file)
        writer.set_shape(shape)
        writer.write_file()
        return _file

    elif format == 'stl':
        writer = StlExporter(_file)
        writer.set_shape(shape)
        writer.write_file()
        return _file

    else:
        raise ValueError('format should be one of [iges,igs], [step,stp], brep, stl\ngot %s' % (format))


def file_to_shape(pth):
    '''get a Shape from an .iges or .step file'''

    from OCCDataExchange.brep import BrepImporter
    from OCCDataExchange.iges import IgesImporter
    from OCCDataExchange.step import StepImporter
    from OCCDataExchange.stl import StlImporter

    assert os.path.isfile(pth), '%s is not a valid file' % (pth)
    ext = os.path.splitext(pth)[1].lower()
    assert ext in ['.iges', '.igs', '.stp', '.step', '.brep', '.stl'], '%s is not an readable format' % (ext)

    if ext in ['.iges', '.igs']:
        reader = IgesImporter(pth)
        return reader.compound

    elif ext in ['.step', '.stp']:
        reader = StepImporter(pth)
        return reader.compound

    elif ext == '.brep':
        reader = BrepImporter(pth)
        return reader.compound

    elif ext == '.stl':
        reader = StlImporter(pth)
        return reader.shape
