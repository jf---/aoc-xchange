#!/usr/bin/python
# coding: utf-8

r"""Importing multiple shapes from IGES"""

from __future__ import print_function

import OCC.Display.SimpleGui

import aocxchange.iges
import aocxchange.utils


display, start_display, add_menu, add_function_to_menu = OCC.Display.SimpleGui.init_display('wx')

# my_iges_importer = occaddons.dataexchange.iges.IgesImporter("../../data/IGES/splines.igs")
filename = aocxchange.utils.path_from_file(__file__, "./models_in/2_boxes.igs")
iges_importer = aocxchange.iges.IgesImporter(filename)

iges_importer.read_file()
the_shapes = iges_importer.shapes

print(iges_importer.nb_shapes)  # 13
print(len(iges_importer.shapes))  # 169

show = "solid"
if show == "compound":
    display.DisplayShape(iges_importer.compound)
elif show == "shell":
    display.DisplayShape(iges_importer.shell)
elif show == "solid":
    display.DisplayShape(iges_importer.solid)
else:
    for face in iges_importer.faces:
        display.DisplayShape(face)

display.FitAll()
display.View_Iso()
start_display()
