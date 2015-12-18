#!/usr/bin/python
# coding: utf-8

r"""Exporting multiple shapes to IGES"""

import OCC.BRepPrimAPI

import aocxchange.iges


# First create a simple shape to export
box_shape = OCC.BRepPrimAPI.BRepPrimAPI_MakeBox(50, 50, 50).Shape()
sphere_shape = OCC.BRepPrimAPI.BRepPrimAPI_MakeSphere(20).Shape()

# Export to STEP
my_iges_exporter = aocxchange.iges.IgesExporter("./models_output/result_export_multi.iges", format="5.3")
my_iges_exporter.add_shape(box_shape)
my_iges_exporter.add_shape(sphere_shape)
my_iges_exporter.write_file()
