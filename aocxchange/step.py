#!/usr/bin/python
# coding: utf-8

r"""step module of aocxchange"""

from __future__ import print_function

import os
import os.path
import logging

import OCC.BRep
import OCC.IFSelect
import OCC.Interface
import OCC.Quantity
import OCC.STEPCAFControl
import OCC.STEPControl
import OCC.TCollection
import OCC.TColStd
import OCC.TDF
import OCC.TDocStd
import OCC.TopAbs
import OCC.TopoDS
import OCC.XCAFApp
import OCC.XCAFDoc
import OCC.XSControl

import aocutils.topology
import aocutils.types

import aocxchange.exceptions
import aocxchange.utils
import aocxchange.extensions

logger = logging.getLogger(__name__)


class StepImporter(object):
    r"""STEP file importer

    Parameters
    ----------
    filename : str

    """
    def __init__(self, filename=None):
        self._shapes = list()
        self._number_of_shapes = 0

        # filename checks
        if not os.path.isfile(filename):
            msg = "StepImporter initialization Error: file %s not found." % filename
            logger.error(msg)
            raise aocxchange.exceptions.FileNotFoundException(msg)
        elif aocxchange.utils.extract_file_extension(filename).lower() not in \
                aocxchange.extensions.step_extensions:
            msg = "Accepted extensions are %s" % str(aocxchange.extensions.step_extensions)
            logger.error(msg)
            raise aocxchange.exceptions.IncompatibleFileFormatException(msg)
        else:
            logger.info("Filename passed existence and extension checks")
            self._filename = filename

        self.read_file()

    # CONFUSING !! Comes from an assignment in ReadFile but looks like the len of shapes
    # @property
    # def number_of_shapes(self):
    #     """ Number of shapes from the importer
    #
    #     Returns
    #     -------
    #     int
    #
    #     """
    #     return self._number_of_shapes

    def read_file(self):
        """
        Read the STEP file and stores the result in a _shapes list
        """
        stepcontrol_reader = OCC.STEPControl.STEPControl_Reader()
        status = stepcontrol_reader.ReadFile(self._filename)

        if status == OCC.IFSelect.IFSelect_RetDone:
            stepcontrol_reader.PrintCheckLoad(False, OCC.IFSelect.IFSelect_ItemsByEntity)
            nb_roots = stepcontrol_reader.NbRootsForTransfer()
            logger.info("%i root(s)" % nb_roots)
            if nb_roots == 0:
                msg = "No root for transfer"
                logger.error(msg)
                raise aocxchange.exceptions.StepFileReadException(msg)

            stepcontrol_reader.PrintCheckTransfer(False, OCC.IFSelect.IFSelect_ItemsByEntity)

            self._number_of_shapes = stepcontrol_reader.NbShapes()

            for n in range(1, nb_roots + 1):
                logger.info("Root index %i" % n)
                ok = stepcontrol_reader.TransferRoot(n)
                logger.info("TransferRoots status : %i" % ok)

                # for i in range(1, self.nb_shapes + 1):
                a_shape = stepcontrol_reader.Shape(n)
                if a_shape.IsNull():
                    msg = "At least one shape in IGES cannot be transferred"
                    logger.warning(msg)
                else:
                    self._shapes.append(a_shape)
                    logger.info("Appending a %s to list of shapes" %
                                aocutils.types.topo_types_dict[a_shape.ShapeType()])
            return True
        else:
            msg = "Status is not OCC.IFSelect.IFSelect_RetDone"
            logger.error(msg)
            raise aocxchange.exceptions.StepFileReadException(msg)

    @property
    def compound(self):
        """ Create and returns a compound from the _shapes list"""
        # Create a compound
        compound = OCC.TopoDS.TopoDS_Compound()
        brep_builder = OCC.BRep.BRep_Builder()
        brep_builder.MakeCompound(compound)
        # Populate the compound
        for shape in self._shapes:
            brep_builder.Add(compound, shape)
        return compound

    @property
    def shapes(self):
        r"""Shapes

        Returns
        -------
        list[OCC.TopoDS.TopoDS_Shape]

        """
        return self._shapes


class StepExporter(object):
    r"""STEP file exporter

    Parameters
    ----------
    filename : str
        the file to save to eg. myshape.step
    verbose : bool
        verbosity of the STEP exporter
    schema : ["AP203", "AP214CD"]
        which STEP schema to use, either AP214CD or AP203
    tolerance : float

    """
    def __init__(self, filename, verbose=False, schema="AP214CD", tolerance=1e-4):

        if schema not in ["AP203", "AP214CD"]:
            msg = "Unsupported STEP schema"
            logger.error(msg)
            raise aocxchange.exceptions.StepUnknownSchemaException(msg)

        if not os.path.isdir(os.path.dirname(filename)):
            msg = "Output directory does not exist"
            logger.error(msg)
            raise aocxchange.exceptions.DirectoryNotFoundException(msg)

        if aocxchange.utils.extract_file_extension(filename).lower() not in \
                aocxchange.extensions.step_extensions:
            msg = "Accepted extensions are %s" % str(aocxchange.extensions.step_extensions)
            logger.error(msg)
            raise aocxchange.exceptions.IncompatibleFileFormatException(msg)

        self._shapes = list()
        self.verbose = verbose
        self._filename = filename
        self._stepcontrol_writer = OCC.STEPControl.STEPControl_Writer()
        self._stepcontrol_writer.SetTolerance(tolerance)

        OCC.Interface.Interface_Static_SetCVal("write.step.schema", schema)

    def add_shape(self, a_shape):
        r"""Add a shape to export

        Parameters
        ----------
        a_shape : TopoDS_Shape or subclass

        """
        if not isinstance(a_shape, OCC.TopoDS.TopoDS_Shape) and not issubclass(a_shape.__class__,
                                                                               OCC.TopoDS.TopoDS_Shape):
            msg = "Expecting a TopoDS_Shape or subclass, got a %s" % a_shape.__class__
            logger.error(msg)
            raise ValueError(msg)

        if a_shape.IsNull():
            msg = "IgesExporter Error: the shape is NULL"
            logger.error(msg)
            raise ValueError(msg)
        else:
            self._shapes.append(a_shape)

    def write_file(self):
        r"""Write STEP file"""
        for shp in self._shapes:
            transfer_status = self._stepcontrol_writer.Transfer(shp, OCC.STEPControl.STEPControl_AsIs)
            if transfer_status != OCC.IFSelect.IFSelect_RetDone:
                msg = "An error occurred while transferring a shape to the STEP writer"
                logger.error(msg)
                raise aocxchange.exceptions.StepShapeTransferException(msg)

        write_status = self._stepcontrol_writer.Write(self._filename)

        if self.verbose:
            self._stepcontrol_writer.PrintStatsTransfer()

        if write_status == OCC.IFSelect.IFSelect_RetDone:
            logger.info("STEP file write successful.")
        else:
            msg = "An error occurred while writing the STEP file"
            logger.error(msg)
            raise aocxchange.exceptions.StepFileWriteException(msg)
