#!/usr/bin/python
# coding: utf-8

r"""STL module of occaddons.dataexchange"""

from __future__ import print_function

import os
import warnings

import OCC.StlAPI
import OCC.TopoDS


class StlImporter(object):
    r"""STL importer

    Parameters
    ----------
    filename : str

    """
    def __init__(self, filename):
        self.set_filename(filename)
        self._shape = None

    def set_filename(self, filename):
        r"""Filename setter

        Parameters
        ----------
        filename

        """
        if not os.path.isfile(filename):
            print("StepImporter initialization Error: file %s not found." % filename)
            self._filename = None
        else:
            self._filename = filename

    def read_file(self):
        r"""Read the STL file and stores the result in a TopoDS_Shape"""
        stl_reader = OCC.StlAPI.StlAPI_Reader()
        shp = OCC.TopoDS.TopoDS_Shape()
        stl_reader.Read(shp, self._filename)
        self._shape = shp

    def get_shape(self):
        r"""Shape getter"""
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
        self._shape = None  # only one shape can be exported
        self._ascii_mode = ascii_mode
        self.set_filename(filename)

    def set_shape(self, a_shape):
        """
        only a single shape can be exported...

        Parameters
        ----------
        a_shape

        """
        # First check the shape
        if a_shape.IsNull():
            raise AssertionError("StlExporter Error: the shape is NULL")
        else:
            self._shape = a_shape

    def set_filename(self, filename):
        r"""Filename setter

        Parameters
        ----------
        filename : str
        """
        if os.path.isfile(filename):
            warnings.warn('will be overwriting file: %s' % filename)
        self._filename = filename

    def write_file(self):
        r"""Write file"""
        stl_writer = OCC.StlAPI.StlAPI_Writer()
        stl_writer.Write(self._shape, self._filename, self._ascii_mode)
