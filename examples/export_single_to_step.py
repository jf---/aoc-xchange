#!/usr/bin/python
# coding: utf-8

r"""Exporting a single shape to STL"""

import OCC.BRepPrimAPI

import aocxchange.step

# First create a simple shape to export
box_shape = OCC.BRepPrimAPI.BRepPrimAPI_MakeBox(50, 50, 50).Shape()

# Export to STEP
step_exporter = aocxchange.step.StepExporter("./models_output/result_export_single.stp")
step_exporter.add_shape(box_shape)
step_exporter.write_file()
