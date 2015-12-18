#!/usr/bin/python
# coding: utf-8

r"""Exporting a shape to STL"""

from __future__ import print_function

import OCC.BRepPrimAPI

import aocxchange.stl

# First create a simple shape to export
my_box_shape = OCC.BRepPrimAPI.BRepPrimAPI_MakeBox(50, 50, 50).Shape()

# Export to STL. If ASCIIMode is set to False, then binary format is used.
my_stl_exporter = aocxchange.stl.StlExporter("./models_output/result_export.stl", ascii_mode=True)
my_stl_exporter.set_shape(my_box_shape)
my_stl_exporter.write_file()
