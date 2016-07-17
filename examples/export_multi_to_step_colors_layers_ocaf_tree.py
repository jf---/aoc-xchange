#!/usr/bin/env python
# coding: utf-8

r"""Exporting multiple shapes to STEP with colors and layers"""

import logging
import os

from OCCDataExchange.step_ocaf import StepOcafImporter

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s :: %(levelname)6s :: %(module)20s :: %(lineno)3d :: %(message)s')

_dir = os.path.dirname(__file__)
step = StepOcafImporter(os.path.join(_dir, "..", "examples", "models_in", "step", "as1_pe_203.stp"))
the_shapes = step.shapes
the_colors = step.colors
the_layers = step.layers
the_layers_str = step.layers_str

print("Number of shapes : %i " % len(the_shapes))

from OCC.Display import SimpleGui
display, start_display, add_menu, add_function_to_menu = SimpleGui.init_display()

for i, shape in enumerate(the_shapes):
    display.DisplayShape(shape, color=the_colors[i])
    print(the_layers_str[i])

display.View_Iso()
display.FitAll()
start_display()
