#!/usr/bin/env python
# coding: utf-8

r"""Importing BREP"""

import logging

from OCC.Display import SimpleGui
from OCCUtils import Topo

from OCCDataExchange.brep import BrepImporter
from OCCDataExchange import path_from_file

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s :: %(levelname)6s :: %(module)20s :: %(lineno)3d :: %(message)s')

# open/parse BREP file and get the resulting TopoDS_Shape instance
filename = path_from_file(__file__, "./models_in/brep/carter.brep")
my_brep_importer = BrepImporter(filename)
the_shape = my_brep_importer.shape

# Then display the shape
display, start_display, add_menu, add_function_to_menu = SimpleGui.init_display()
# display.DisplayShape(the_shape, color='BLUE', update=True)

# 1 solid to display

for s in Topo(the_shape):
    display.DisplayShape(s)

# faces
# OCCUtils.display.topology.faces(display, the_shape, show_numbers=False)  # super slow !!
display.FitAll()
display.View_Iso()
start_display()
