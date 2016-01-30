#!/usr/bin/env python
# coding: utf-8

r"""Importing STL"""

import logging

from OCCUtils import Topo

from OCCDataExchange.stl import StlImporter
from OCCDataExchange import path_from_file

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s :: %(levelname)6s :: %(module)20s :: %(lineno)3d :: %(message)s')

# open/parse STL file and get the resulting TopoDS_Shape instance
# filename = OCCDataExchange.path_from_file(__file__, "./models_in/sample.stl")
# filename = OCCDataExchange.path_from_file(__file__, "./models_in/USS_Albacore.STL")
filename = path_from_file(__file__, "./models_in/stl/USS_Albacore.STL")
my_stl_importer = StlImporter(filename)
the_shape = my_stl_importer.shape

# Then display the shape
display, start_display, add_menu, add_function_to_menu = SimpleGui.init_display()
# display.DisplayShape(the_shape, color='BLUE', update=True)

# 1 shell to display

for sh in Topo(the_shape).shells():
    display.DisplayShape(sh)

# faces
# OCCUtils.display.topology.faces(display, the_shape, show_numbers=False)  # super slow !!
display.FitAll()
display.View_Iso()
start_display()
