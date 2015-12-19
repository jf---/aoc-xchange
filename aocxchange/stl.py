#!/usr/bin/python
# coding: utf-8

r"""STL module of aocxchange"""

from __future__ import print_function

import os
import warnings
import logging

import OCC.StlAPI
import OCC.TopoDS

import aocxchange.exceptions
import aocxchange.extensions
import aocxchange.utils

logger = logging.getLogger(__name__)


class StlImporter(object):
    r"""STL importer

    Parameters
    ----------
    filename : str

    """
    def __init__(self, filename):
        logger.info("StlImporter instantiated with filename : %s" % filename)

        # filename checks
        if not os.path.isfile(filename):
            msg = "StlImporter error: file %s not found." % filename
            logger.error(msg)
            raise aocxchange.exceptions.FileNotFoundException(msg)
        elif aocxchange.utils.extract_file_extension(filename).lower() not in \
                aocxchange.extensions.stl_extensions:
            msg = "Accepted extensions are %s" % str(aocxchange.extensions.stl_extensions)
            logger.error(msg)
            raise aocxchange.exceptions.IncompatibleFileFormatException(msg)
        else:
            logger.info("Filename passed existence and extension checks")
            self._filename = filename
        self._shape = None

        self.read_file()

    def read_file(self):
        r"""Read the STL file and stores the result in a TopoDS_Shape"""
        stl_reader = OCC.StlAPI.StlAPI_Reader()
        shape = OCC.TopoDS.TopoDS_Shape()
        stl_reader.Read(shape, self._filename)
        self._shape = shape

    @property
    def shape(self):
        r"""Shape"""
        if self._shape.IsNull():
            raise AssertionError("Error: the shape is NULL")
        else:
            return self._shape


class StlExporter(object):
    """ A TopoDS_Shape to STL exporter. Default mode is ASCII

    Parameters
    ----------
    filename : str
    ascii_mode : bool
        (default is False)
    """
    def __init__(self, filename=None, ascii_mode=False):

        if not os.path.isdir(os.path.dirname(filename)):
            msg = "Output directory does not exist"
            logger.error(msg)
            raise aocxchange.exceptions.DirectoryNotFoundException(msg)

        if aocxchange.utils.extract_file_extension(filename).lower() not in \
                aocxchange.extensions.stl_extensions:
            msg = "Accepted extensions are %s" % str(aocxchange.extensions.stl_extensions)
            logger.error(msg)
            raise aocxchange.exceptions.IncompatibleFileFormatException(msg)

        self._shape = None  # only one shape can be exported
        self._ascii_mode = ascii_mode

        if os.path.isfile(filename):
            msg = "Will be overwriting file: %s" % filename
            warnings.warn(msg)
            logger.warning(msg)
        self._filename = filename

    def set_shape(self, a_shape):
        """
        only a single shape can be exported...

        Parameters
        ----------
        a_shape

        """
        if not isinstance(a_shape, OCC.TopoDS.TopoDS_Shape) and not issubclass(a_shape.__class__,
                                                                               OCC.TopoDS.TopoDS_Shape):
            msg = "Expecting a TopoDS_Shape or subclass, got a %s" % a_shape.__class__
            logger.error(msg)
            raise ValueError(msg)

        if a_shape.IsNull():
            msg = "IgesExporter Error: the shape is NULL"
            logger.error(msg)
            raise ValueError(msg)
        else:
            self._shape = a_shape

    def write_file(self):
        r"""Write file"""
        stl_writer = OCC.StlAPI.StlAPI_Writer()
        stl_writer.Write(self._shape, self._filename, self._ascii_mode)
