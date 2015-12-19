#!/usr/bin/python
# coding: utf-8

r"""Importing STL"""

import logging

import OCC.Display.SimpleGui

import aocxchange.stl
import aocxchange.utils

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s :: %(levelname)6s :: %(module)20s :: %(lineno)3d :: %(message)s')

# open/parse STL file and get the resulting TopoDS_Shape instance
# filename = aocxchange.utils.path_from_file(__file__, "./models_in/sample.stl")
filename = aocxchange.utils.path_from_file(__file__, "./models_in/USS_Albacore.STL")
filename = aocxchange.utils.path_from_file(__file__, "./models_in/USS_Albacore.STL")
my_stl_importer = aocxchange.stl.StlImporter(filename)
the_shape = my_stl_importer.shape

# Then display the shape
display, start_display, add_menu, add_function_to_menu = OCC.Display.SimpleGui.init_display('wx')
display.DisplayShape(the_shape, color='BLUE', update=True)
display.FitAll()
display.View_Iso()
start_display()
