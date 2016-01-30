#!/usr/bin/env python
# coding: utf-8

r"""STL module of OCCDataExchange"""

from __future__ import print_function

import logging

from OCC import StlAPI
from OCC import TopoDS

from OCCDataExchange.checks import check_importer_filename, check_exporter_filename, check_overwrite, check_shape
from OCCDataExchange.extensions import stl_extensions

logger = logging.getLogger(__name__)


class StlImporter(object):
    r"""STL importer

    Parameters
    ----------
    filename : str

    """

    def __init__(self, filename):
        logger.info("StlImporter instantiated with filename : %s" % filename)

        check_importer_filename(filename, stl_extensions)
        self._filename = filename
        self._shape = None

        logger.info("Reading file ....")
        self.read_file()

    def read_file(self):
        r"""Read the STL file and stores the result in a TopoDS_Shape"""
        stl_reader = StlAPI.StlAPI_Reader()
        shape = TopoDS.TopoDS_Shape()
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
        logger.info("StlExporter instantiated with filename : %s" % filename)
        logger.info("StlExporter ascii : %s" % str(ascii_mode))

        check_exporter_filename(filename, stl_extensions)
        check_overwrite(filename)

        self._shape = None  # only one shape can be exported
        self._ascii_mode = ascii_mode
        self._filename = filename

    def set_shape(self, a_shape):
        """
        only a single shape can be exported...

        Parameters
        ----------
        a_shape

        """
        check_shape(a_shape)  # raises an exception if the shape is not valid
        self._shape = a_shape

    def write_file(self):
        r"""Write file"""
        stl_writer = StlAPI.StlAPI_Writer()
        stl_writer.Write(self._shape, self._filename, self._ascii_mode)
        logger.info("Wrote STL file")
