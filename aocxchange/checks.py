#!/usr/bin/python
# coding: utf-8

r"""Common checks to all exporters and importers
"""

import os.path
import logging
import warnings

import OCC.TopoDS

import aocxchange.exceptions
import aocxchange.utils

logger = logging.getLogger(__name__)


def check_importer_filename(filename, allowed_extensions):
    r"""Check the filename is ok for importing

    Parameters
    ----------
    filename : str
        Full path to the file
    allowed_extensions : list[str]
        List of allowed extensions

    """
    # Check the file exists
    if not os.path.isfile(filename):
        msg = "Importer error : file %s not found." % filename
        logger.error(msg)
        raise aocxchange.exceptions.FileNotFoundException(msg)

    _check_extension(filename, allowed_extensions)
    logger.info("Filename passed checks")
    return True


def check_exporter_filename(filename, allowed_extensions):
    r"""Check the filename is ok for exporting

    Parameters
    ----------
    filename : str
        Full path to the file
    allowed_extensions : list[str]
        List of allowed extensions

    """
    # Check the output directory exists
    if not os.path.isdir(os.path.dirname(filename)):
        msg = "Exporter error : Output directory does not exist"
        logger.error(msg)
        raise aocxchange.exceptions.DirectoryNotFoundException(msg)

    _check_extension(filename, allowed_extensions)
    logger.info("Filename passed checks")
    return True


def check_overwrite(filename):
    r"""

    Parameters
    ----------
    filename : str
        Full path to the file

    Returns
    -------
    bool

    """
    if os.path.isfile(filename):
        msg = "Will be overwriting file: %s" % filename
        warnings.warn(msg)
        logger.warning(msg)
        return True
    else:
        return False


def _check_extension(filename, allowed_extensions):
    if aocxchange.utils.extract_file_extension(filename).lower() not in allowed_extensions:
        msg = "Accepted extensions are %s" % str(allowed_extensions)
        logger.error(msg)
        raise aocxchange.exceptions.IncompatibleFileFormatException(msg)


def check_shape(a_shape):
    r"""Check the shape before adding it to an exporter

    Parameters
    ----------
    a_shape : OCC.TopoDS.TopoDS_Shape or subclass

    Returns
    -------
    bool
        True if all tests passed, raises an exception otherwise
    """
    if not isinstance(a_shape, OCC.TopoDS.TopoDS_Shape) and not issubclass(a_shape.__class__, OCC.TopoDS.TopoDS_Shape):
        msg = "Expecting a TopoDS_Shape or subclass, got a %s" % a_shape.__class__
        logger.error(msg)
        raise ValueError(msg)

    if a_shape.IsNull():
        msg = "IgesExporter Error: the shape is NULL"
        logger.error(msg)
        raise ValueError(msg)

    return True
