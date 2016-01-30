#!/usr/bin/env python
# coding: utf-8

r"""IGES file reading tests"""

import logging

import pytest
from OCC import TopoDS
from OCCUtils import Topo

from OCCDataExchange.iges import IgesImporter
from OCCDataExchange.utils import path_from_file

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s :: %(levelname)6s :: %(module)20s :: %(lineno)3d :: %(message)s')


def test_iges_importer_wrong_path():
    r"""Wrong filename"""
    with pytest.raises(ValueError):
        IgesImporter("C:/stupid-filename.bad_extension")


def test_iges_importer_wrong_extension():
    r"""wrong file format (i.e. trying to read a step file with iges importer)"""
    with pytest.raises(ValueError):
        IgesImporter(path_from_file(__file__, "./models_in/aube_pleine.stp"))


def test_iges_importer_wrong_file_content():
    r"""wrong file content"""
    with pytest.raises(ValueError):
        IgesImporter(path_from_file(__file__, "./models_in/empty.igs"))


def test_iges_importer_happy_path():
    r"""happy path"""
    importer = IgesImporter(path_from_file(__file__, "./models_in/aube_pleine.iges"))
    assert isinstance(importer.compound, TopoDS.TopoDS_Compound)
    assert isinstance(importer.shapes, list)
    for shape in importer.shapes:
        assert isinstance(shape, TopoDS.TopoDS_Shape)


def test_iges_importer_happy_topology():
    r"""import iges file containing a box and test topology"""
    importer = IgesImporter(path_from_file(__file__, "./models_in/box.igs"))

    topo = Topo(importer.compound, return_iter=False)
    assert topo.number_of_faces() == 6
    assert topo.number_of_edges() == 24  # 12 edges * 2 possible orientations ?


def test_iges_importer_2_boxes():
    r"""Import an iges file containing 2 distinct boxes and test topology

    Notes
    -----
    This shows the current limitations of the IgesImporter as 2 boxes cannot be distinguished from one another

    """
    importer = IgesImporter(path_from_file(__file__, "./models_in/2_boxes.igs"))
    topo = Topo(importer.compound, return_iter=False)
    assert topo.number_of_faces() == 6 * 2
    assert topo.number_of_edges() == 24 * 2
