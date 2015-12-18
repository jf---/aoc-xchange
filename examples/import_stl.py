#!/usr/bin/python
# coding: utf-8

r"""Importing STL"""

import OCC.Display.SimpleGui
import aocxchange.stl

# open/parse STL file and get the resulting TopoDS_Shape instance
my_stl_importer = aocxchange.stl.StlImporter("./models_input/sample.stl")
my_stl_importer.read_file()
the_shape = my_stl_importer.get_shape()

# Then display the shape
display, start_display, add_menu, add_function_to_menu = OCC.Display.SimpleGui.init_display('wx')
display.DisplayShape(the_shape, color='RED')
display.FitAll()
display.View_Iso()
start_display()
