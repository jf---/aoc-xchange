#!/usr/bin/python
# coding: utf-8

r"""Importing multiple shapes from STEP"""

from __future__ import print_function

import logging

import OCC.Display.SimpleGui

import aocxchange.step
import aocxchange.utils

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s :: %(levelname)6s :: %(module)20s :: %(lineno)3d :: %(message)s')

display, start_display, add_menu, add_function_to_menu = OCC.Display.SimpleGui.init_display('wx')

filename = aocxchange.utils.path_from_file(__file__, "./models_in/dm1-id-214.stp")
step_importer = aocxchange.step.StepImporter(filename)

the_shapes = step_importer.shapes
print("Nb shapes): %i" % len(the_shapes))  # 4
# print("number_of_shapes(): %i" % step_importer.number_of_shapes)  # 0 ??


display.DisplayColoredShape(the_shapes, "RED")
display.FitAll()
display.View_Iso()
start_display()
