#!/usr/bin/env python
# coding: utf-8

r"""STL file writing tests"""

import pytest
import os.path
import glob
import logging

from OCC import BRepPrimAPI
from OCC import gp
from OCC import TopoDS
from OCCUtils import Topo
from OCCUtils.types_lut import ShapeToTopology

from OCCDataExchange.stl import StlExporter, StlImporter
from OCCDataExchange.utils import path_from_file

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s :: %(levelname)6s :: %(module)20s :: %(lineno)3d :: %(message)s')

shape_to_topology = ShapeToTopology()


@pytest.yield_fixture(autouse=True)
def cleandir():
    r"""Clean the tests output directory

    autouse=True insure this fixture wraps every test function
    yield represents the function call
    """
    yield  # represents the test function call
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models_out")
    files = glob.glob(output_dir + "\*")
    print("Cleaning output directory ...")
    for f in files:
        os.remove(f)
    print("Output directory clean")


@pytest.fixture()
def box_shape():
    r"""Box shape for testing"""
    return BRepPrimAPI.BRepPrimAPI_MakeBox(10, 20, 30).Shape()


def test_stl_exporter_wrong_filename(box_shape):
    r"""Trying to write to a non-existent directory"""
    filename = path_from_file(__file__, "./nonexistent/box.stl")
    with pytest.raises(AssertionError):
        StlExporter(filename)


def test_stl_exporter_wrong_extension(box_shape):
    r"""Trying to write a step file with the IgesExporter"""
    filename = path_from_file(__file__, "./models_out/box.step")
    with pytest.raises(AssertionError):
        StlExporter(filename)


def test_stl_exporter_adding_not_a_shape(box_shape):
    r"""Adding something to the exporter that is not a TopoDS_Shape or a subclass"""
    filename = path_from_file(__file__, "./models_out/box.stl")
    exporter = StlExporter(filename)
    with pytest.raises(ValueError):
        exporter.set_shape(gp.gp_Pnt(1, 1, 1))


def test_stl_exporter_happy_path(box_shape):
    r"""Happy path"""
    filename = path_from_file(__file__, "./models_out/box.sTl")
    exporter = StlExporter(filename)
    exporter.set_shape(box_shape)
    exporter.write_file()
    assert os.path.isfile(filename)
    # tests.utils.clean_output_dir()


def test_stl_exporter_happy_path_shape_subclass(box_shape):
    r"""Happy path with a subclass of TopoDS_Shape"""
    filename = path_from_file(__file__, "./models_out/box.stl")
    exporter = StlExporter(filename)
    solid = shape_to_topology(box_shape)
    assert isinstance(solid, TopoDS.TopoDS_Solid)
    exporter.set_shape(solid)
    exporter.write_file()
    assert os.path.isfile(filename)


def test_stl_exporter_overwrite(box_shape):
    r"""Happy path with a subclass of TopoDS_Shape"""
    filename = path_from_file(__file__, "./models_out/box.stl")
    exporter = StlExporter(filename)
    solid = shape_to_topology(box_shape)
    assert isinstance(solid, TopoDS.TopoDS_Solid)
    exporter.set_shape(solid)
    exporter.write_file()
    assert os.path.isfile(filename)

    # read the written box.stl
    importer = StlImporter(filename)
    topo = Topo(importer.shape)
    assert topo.number_of_shells() == 1

    # set a sphere and write again with same exporter
    sphere = BRepPrimAPI.BRepPrimAPI_MakeSphere(10)
    exporter.set_shape(sphere.Shape())
    exporter.write_file()  # this creates a file with a sphere only, this is STL specific

    # check that the file contains the sphere only
    importer = StlImporter(filename)
    topo = Topo(importer.shape)
    assert topo.number_of_shells() == 1

    # create a new exporter and overwrite with a box only
    filename = path_from_file(__file__, "./models_out/box.stl")
    exporter = StlExporter(filename)
    solid = shape_to_topology(box_shape)
    exporter.set_shape(solid)
    exporter.write_file()
    assert os.path.isfile(filename)

    # check the file only contains a box
    importer = StlImporter(filename)
    topo = Topo(importer.shape)
    assert topo.number_of_shells() == 1
