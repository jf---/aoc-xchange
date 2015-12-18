#!/usr/bin/python
# coding: utf-8

r"""Importing multiple shapes from STEP"""

from __future__ import print_function

import OCC.Display.SimpleGui

import aocxchange.step


display, start_display, add_menu, add_function_to_menu = OCC.Display.SimpleGui.init_display('wx')

step_importer = aocxchange.step.StepImporter("./models_input/dm1-id-214.stp")
step_importer.read_file()

the_shapes = step_importer.shapes
print("Nb shapes): %i" % len(the_shapes))  # 4
# print("number_of_shapes(): %i" % step_importer.number_of_shapes)  # 0 ??


display.DisplayColoredShape(the_shapes, "RED")
display.FitAll()
display.View_Iso()
start_display()
