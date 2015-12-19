#!/usr/bin/python
# coding: utf-8

r"""IGES module of aocxchange"""

from __future__ import print_function

import os
import os.path
import logging
import warnings

import OCC.BRep
import OCC.IFSelect
import OCC.IGESControl
import OCC.TopoDS
import OCC.TopAbs

import aocxchange.exceptions
import aocxchange.utils
import aocxchange.extensions

import aocutils.types
import aocutils.brep.shell_make
import aocutils.brep.solid_make
import aocutils.topology

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
        self._shapes = list()
        self.nb_shapes = 0

        # filename checks
        if not os.path.isfile(filename):
            msg = "IgesImporter error: file %s not found." % filename
            logger.error(msg)
            raise aocxchange.exceptions.FileNotFoundException(msg)
        elif aocxchange.utils.extract_file_extension(filename).lower() not in \
                aocxchange.extensions.iges_extensions:
            msg = "Accepted extensions are %s" % str(aocxchange.extensions.iges_extensions)
            logger.error(msg)
            raise aocxchange.exceptions.IncompatibleFileFormatException(msg)
        else:
            logger.info("Filename passed existence and extension checks")
            self._filename = filename
        logger.info("Reading file ....")

        self.read_file()

    def read_file(self):
        """
        Read the IGES file and stores the result in a list of OCC.TopoDS.TopoDS_Shape

        """
        igescontrol_reader = OCC.IGESControl.IGESControl_Reader()
        status = igescontrol_reader.ReadFile(self._filename)
        igescontrol_reader.PrintCheckLoad(False, OCC.IFSelect.IFSelect_ItemsByEntity)
        nb_roots = igescontrol_reader.NbRootsForTransfer()
        logger.info("Nb roots for transfer : %i" % nb_roots)

        if status == OCC.IFSelect.IFSelect_RetDone and nb_roots != 0:

            igescontrol_reader.PrintCheckTransfer(False, OCC.IFSelect.IFSelect_ItemsByEntity)
            ok = igescontrol_reader.TransferRoots()
            logger.info("TransferRoots status : %i" % ok)
            self.nb_shapes = igescontrol_reader.NbShapes()

            for n in range(1, nb_roots + 1):

                logger.info("Root index %i" % n)

                # for i in range(1, self.nb_shapes + 1):
                a_shape = igescontrol_reader.Shape(n)
                if a_shape.IsNull():
                    msg = "At least one shape in IGES cannot be transferred"
                    logger.warning(msg)
                else:
                    self._shapes.append(a_shape)
                    logger.info("Appending a %s to list of shapes" %
                                aocutils.types.topo_types_dict[a_shape.ShapeType()])
        else:
            msg = "Status is not OCC.IFSelect.IFSelect_RetDone or No root for transfer"
            logger.error(msg)
            raise aocxchange.exceptions.IgesFileReadException(msg)

    @property
    def compound(self):
        """ Create and returns a compound from the _shapes list

        Returns
        -------
        OCC.TopoDS.TopoDS_Compound

        Notes
        -----
        Importing an iges box results in:
        0 solid
        0 shell
        6 faces
        24 edges

        """
        # Create a compound
        compound = OCC.TopoDS.TopoDS_Compound()
        brep_builder = OCC.BRep.BRep_Builder()
        brep_builder.MakeCompound(compound)
        # Populate the compound
        for shape in self._shapes:
            brep_builder.Add(compound, shape)
        return compound

    @property
    def faces(self):
        r"""Return only the shapes that are faces"""
        # return [shape for shape in self._shapes if shape.ShapeType() == OCC.TopAbs.TopAbs_FACE]
        return aocutils.topology.Topo(self.compound, return_iter=False).faces()

    @property
    def solid(self):
        r"""Tries to create a solid from the loaded iges geometry

        Returns
        -------
        OCC.TopoDS.TopoDS_Solid

        Notes
        -----
        This is meaningless for faces that are not connected

        See Also
        --------
        examples/import_iges_multi.py to visualize the current impossibility to distinguish the 2 boxes

        """
        return aocutils.brep.solid_make.solid(self.shell)

    @property
    def shell(self):
        r"""Tries to create a shell from the loaded iges geometry

        Returns
        -------
        OCC.TopoDS.TopoDS_Shell

        Notes
        -----
        This is meaningless for faces that are not connected

        See Also
        --------
        examples/import_iges_multi.py to visualize the current impossibility to distinguish the 2 boxes

        """
        if len(self.faces) == 0:
            msg = "Cannot build a shell from 0 face"
            logger.error(msg)
            raise aocxchange.exceptions.BRepBuildingException(msg)
        builder = OCC.TopoDS.TopoDS_Builder()
        shell = OCC.TopoDS.TopoDS_Shell()
        builder.MakeShell(shell)
        for face in self.faces:
            builder.Add(shell, face)
        return shell

    @property
    def shapes(self):
        r"""Shapes getter

        Returns
        -------
        list[OCC.TopoDS.TopoDS_Shape]

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
        # Format should be "5.1" or "5.3"

        if format not in ["5.1", "5.3"]:
            msg = "Unsupported IGES format"
            logger.error(msg)
            raise aocxchange.exceptions.IgesUnknownFormatException(msg)

        if not os.path.isdir(os.path.dirname(filename)):
            msg = "Output directory does not exist"
            logger.error(msg)
            raise aocxchange.exceptions.DirectoryNotFoundException(msg)

        if aocxchange.utils.extract_file_extension(filename).lower() not in \
                aocxchange.extensions.iges_extensions:
            msg = "Accepted extensions are %s" % str(aocxchange.extensions.iges_extensions)
            logger.error(msg)
            raise aocxchange.exceptions.IncompatibleFileFormatException(msg)

        self._shapes = list()

        if os.path.isfile(filename):
            msg = "Will be overwriting file: %s" % filename
            warnings.warn(msg)
            logger.warning(msg)
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
        r"""Write file

        Returns
        -------
        bool

        """
        OCC.IGESControl.IGESControl_Controller().Init()
        iges_writer = OCC.IGESControl.IGESControl_Writer("write.iges.unit", self._brepmode)
        for shape in self._shapes:
            iges_writer.AddShape(shape)
        iges_writer.ComputeModel()
        if iges_writer.Write(self._filename):
            return True
        else:
            return False


