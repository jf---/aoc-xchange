#!/usr/bin/env python
# coding: utf-8

r"""IGES module of OCCDataExchange"""

from __future__ import print_function

import logging

from OCC import BRep
from OCC import IFSelect
from OCC import IGESControl
from OCC import TopoDS
from OCCUtils.types_lut import topo_lut

from OCCDataExchange.checks import check_importer_filename, check_exporter_filename, check_overwrite, check_shape
from OCCDataExchange.extensions import iges_extensions

logger = logging.getLogger(__name__)


class IgesImporter(object):
    r"""IGES importer

    Parameters
    ----------
    filename : str
        Absolute filepath

    """

    def __init__(self, filename=None):
        logger.info("IgesImporter instantiated with filename : %s" % filename)

        check_importer_filename(filename, iges_extensions)

        self._shapes = list()
        self.nb_shapes = 0
        self._filename = filename

        logger.info("Reading file ....")
        self.read_file()

    def read_file(self):
        """
        Read the IGES file and stores the result in a list of TopoDS.TopoDS_Shape

        """
        igescontrol_reader = IGESControl.IGESControl_Reader()
        status = igescontrol_reader.ReadFile(self._filename)
        igescontrol_reader.PrintCheckLoad(False, IFSelect.IFSelect_ItemsByEntity)
        nb_roots = igescontrol_reader.NbRootsForTransfer()
        logger.info("Nb roots for transfer : %i" % nb_roots)

        if status == IFSelect.IFSelect_RetDone and nb_roots != 0:

            igescontrol_reader.PrintCheckTransfer(False, IFSelect.IFSelect_ItemsByEntity)
            ok = igescontrol_reader.TransferRoots()
            logger.info("TransferRoots status : %i" % ok)
            self.nb_shapes = igescontrol_reader.NbShapes()

            for n in range(1, nb_roots + 1):

                logger.debug("Root index %i" % n)

                # for i in range(1, self.nb_shapes + 1):
                a_shape = igescontrol_reader.Shape(n)
                if a_shape.IsNull():
                    msg = "At least one shape in IGES cannot be transferred"
                    logger.warning(msg)
                else:
                    self._shapes.append(a_shape)
                    logger.debug("Appending a %s to list of shapes" %
                                 topo_lut[a_shape.ShapeType()])
        else:
            msg = "Status is not IFSelect.IFSelect_RetDone or No root for transfer"
            logger.error(msg)
            raise ValueError(msg)

    @property
    def compound(self):
        """ Create and returns a compound from the _shapes list

        Returns
        -------
        TopoDS.TopoDS_Compound

        Notes
        -----
        Importing an iges box results in:
        0 solid
        0 shell
        6 faces
        24 edges

        """
        # Create a compound
        compound = TopoDS.TopoDS_Compound()
        brep_builder = BRep.BRep_Builder()
        brep_builder.MakeCompound(compound)
        # Populate the compound
        for shape in self._shapes:
            brep_builder.Add(compound, shape)
        return compound

    @property
    def shapes(self):
        r"""Shapes getter

        Returns
        -------
        list[TopoDS.TopoDS_Shape]

        """
        return self._shapes


class IgesExporter(object):
    r"""IGES exporter

    Parameters
    ----------
    filename : str
    format : ["5.1", "5.3"]

    """

    def __init__(self, filename, format="5.1"):
        logger.info("IgesExporter instantiated with filename : %s" % filename)
        logger.info("IgesExporter format : %s" % format)

        if format not in ["5.1", "5.3"]:
            msg = "Unsupported IGES format"
            logger.error(msg)
            raise ValueError(msg)

        check_exporter_filename(filename, iges_extensions)
        check_overwrite(filename)

        self._shapes = list()
        self._filename = filename

        if format == "5.3":
            self._brepmode = True
        else:
            self._brepmode = False

    def add_shape(self, a_shape):
        r"""Add shape

        Parameters
        ----------
        a_shape : TopoDS_Shape or subclass

        """
        check_shape(a_shape)  # raises an exception if the shape is not valid
        self._shapes.append(a_shape)

    def write_file(self):
        r"""Write file

        Returns
        -------
        bool

        """
        IGESControl.IGESControl_Controller().Init()
        iges_writer = IGESControl.IGESControl_Writer("write.iges.unit", self._brepmode)
        for shape in self._shapes:
            iges_writer.AddShape(shape)
        iges_writer.ComputeModel()

        write_status = iges_writer.Write(self._filename)

        if write_status == IFSelect.IFSelect_RetDone:
            logger.info("IGES file write successful.")
        else:
            msg = "An error occurred while writing the IGES file"
            logger.error(msg)
            raise ValueError(msg)
