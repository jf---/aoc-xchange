#!/usr/bin/env python
# coding: utf-8

r"""DAT file reading tests"""

import logging

from OCCDataExchange.dat import DatImporter
from OCCDataExchange.utils import path_from_file

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s :: %(levelname)6s :: %(module)20s :: %(lineno)3d :: %(message)s')


def test_read_dat_file():
    r"""Test reading a foil section definition dat file"""
    importer = DatImporter(path_from_file(__file__, "./models_in/naca0006.dat"),
                                               skip_first_line=True)
    pts = importer.points
    assert len(pts) == 35
