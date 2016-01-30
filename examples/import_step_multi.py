#!/usr/bin/env python
# coding: utf-8

r"""Importing multiple shapes from STEP"""

from __future__ import print_function

import logging

from OCC.Display import SimpleGui
from OCCUtils import Topo

from OCCDataExchange.step import StepImporter
from OCCDataExchange import path_from_file

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s :: %(levelname)6s :: %(module)20s :: %(lineno)3d :: %(message)s')
display, start_display, add_menu, add_function_to_menu = SimpleGui.init_display()

# filename = OCCDataExchange.path_from_file(__file__, "./models_in/step/dm1-id-214.stp")
# filename = OCCDataExchange.path_from_file(__file__, "./models_in/step/APB_GC.stp")  # big file 50 Mb !
# filename = OCCDataExchange.path_from_file(__file__, "./models_in/step/66m.stp")
filename = path_from_file(__file__, "./models_in/step/ASA.STEP")
# filename = OCCDataExchange.path_from_file(__file__, "./models_in/step/Groupama_VO70.stp")
step_importer = StepImporter(filename)

the_shapes = step_importer.shapes
print("Nb shapes : %i" % len(the_shapes))  # 4
# print("number_of_shapes(): %i" % step_importer.number_of_shapes)  # 0 ??

# display.DisplayColoredShape(the_shapes[0], Quantity.Quantity_Color(Quantity.Quantity_NOC_GRAY3))
for s in Topo(the_shapes[0]).solids():
    display.DisplayShape(s)

display.FitAll()
display.View_Iso()
start_display()
