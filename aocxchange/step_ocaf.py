#!/usr/bin/python
# coding: utf-8

r"""step_ocaf module of occaddons.dataexchange"""

from __future__ import print_function

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

logger = logging.getLogger(__name__)


class StepOcafImport(object):
    r"""Imports STEP file that support layers & colors"""
    def __init__(self, filename):
        self.filename = filename

        # The shape at index i in the following list corresponds
        # to the color and layer at index i in their respective lists
        self._shapes = list()
        self._colors = list()
        self._layers = list()

    @property
    def shapes(self):
        r"""Shapes"""
        return self._shapes

    @property
    def colors(self):
        r"""Colors"""
        return self._colors

    @property
    def layers(self):
        r"""Layers"""
        return self._layers

    @property
    def layers_str(self):
        r"""Returns a readable list of layers in the same order as self._shapes

        If self.shapes = [shape_1, shape_2], layers_str will return ['red', 'green'] when shape_1 is on the "red" layer
        and shape_2 is on the 'green' layer.

        See Also
        --------
        examples/export_multi_to_step_colors_layers_ocaf.py

        """
        layer_string_list = list()
        for i, layer in enumerate(self._layers):
            string = ""
            for j in range(1, layer.GetObject().Length() + 1):
                extended_string = layer.GetObject().Value(j)

                for k in range(1, extended_string.Length() + 1):
                    ascii_code = extended_string.Value(k)
                    string += (chr(ascii_code))

            layer_string_list.append(string)
        return layer_string_list

    def read_file(self):
        r"""Read file"""
        logger.info("Reading STEP file")
        h_doc = OCC.TDocStd.Handle_TDocStd_Document()

        # Create the application
        app = OCC.XCAFApp._XCAFApp.XCAFApp_Application_GetApplication().GetObject()
        app.NewDocument(OCC.TCollection.TCollection_ExtendedString("MDTV-CAF"), h_doc)

        # Get root assembly
        doc = h_doc.GetObject()
        h_shape_tool = OCC.XCAFDoc.XCAFDoc_DocumentTool().ShapeTool(doc.Main())
        color_tool = OCC.XCAFDoc.XCAFDoc_DocumentTool().ColorTool(doc.Main())
        layer_tool = OCC.XCAFDoc.XCAFDoc_DocumentTool().LayerTool(doc.Main())
        l_materials = OCC.XCAFDoc.XCAFDoc_DocumentTool().MaterialTool(doc.Main())

        step_reader = OCC.STEPCAFControl.STEPCAFControl_Reader()
        step_reader.SetColorMode(True)
        step_reader.SetLayerMode(True)
        step_reader.SetNameMode(True)
        step_reader.SetMatMode(True)

        status = step_reader.ReadFile(str(self.filename))

        if status == OCC.IFSelect.IFSelect_RetDone:
            logger.info("Transfer doc to STEPCAFControl_Reader")
            step_reader.Transfer(doc.GetHandle())

        labels = OCC.TDF.TDF_LabelSequence()
        color_labels = OCC.TDF.TDF_LabelSequence()
        # TopoDS_Shape a_shape;
        shape_tool = h_shape_tool.GetObject()
        h_shape_tool.GetObject().GetFreeShapes(labels)

        logger.info('Number of shapes at root :%i' % labels.Length())

        # for i in range(labels.Length()):
        #     a_shape = h_shape_tool.GetObject().GetShape(labels.Value(i+1))
        #     logger.debug("%i - type : %s" % (i, a_shape.ShapeType()))
        #     sub_shapes_labels = OCC.TDF.TDF_LabelSequence()
        #     print("Is Assembly?", shape_tool.IsAssembly(labels.Value(i + 1)))
        #     # sub_shapes = shape_tool.getsubshapes(labels.Value(i+1), sub_shapes_labels)
        #
        #     sub_shapes = shape_tool.FindSubShape(labels.Value(i + 1), a_shape, labels.Value(i + 1))
        #     print('Number of subshapes in the assembly : %i' % sub_shapes_labels.Length())
        #
        # color_tool.GetObject().GetColors(color_labels)
        # logger.info('Number of colors : %i' % color_labels.Length())

        for i in range(labels.Length()):
            # print i
            label = labels.Value(i + 1)
            logger.debug("Label : %s" % label)
            a_shape = h_shape_tool.GetObject().GetShape(labels.Value(i+1))

            # string_seq = OCC.TColStd.TColStd_HSequenceOfExtendedString()
            # string_seq is an OCC.TColStd.TColStd_HSequenceOfExtendedString
            string_seq = layer_tool.GetObject().GetLayers(a_shape)
            color = OCC.Quantity.Quantity_Color()
            c = color_tool.GetObject().GetColor(a_shape, OCC.XCAFDoc.XCAFDoc_ColorSurf, color)

            logger.info("The shape type is : %i" % a_shape.ShapeType())
            if a_shape.ShapeType() == OCC.TopAbs.TopAbs_COMPOUND:
                logger.info("The shape type is OCC.TopAbs.TopAbs_COMPOUND")
                topo = aocutils.topology.Topo(a_shape)
                logger.info("Nb of compounds : %i" % topo.number_of_compounds())
                logger.info("Nb of solids : %i" % topo.number_of_solids())
                logger.info("Nb of shells : %i" % topo.number_of_shells())
                for solid in topo.solids():
                    logger.info("Adding solid to the shapes list")
                    self._shapes.append(solid)
            elif a_shape.ShapeType() == OCC.TopAbs.TopAbs_SOLID:
                logger.info("The shape type is OCC.TopAbs.TopAbs_SOLID")
                self._shapes.append(a_shape)
                self._colors.append(color)
                self._layers.append(string_seq)

        return True


class StepOcafExport(object):
    r"""STEP export that support layers & colors"""
    def __init__(self, filename, layer_name='layer-00'):
        self.filename = filename
        self.h_doc = h_doc = OCC.TDocStd.Handle_TDocStd_Document()
        print("Empty Doc?", h_doc.IsNull())

        # Create the application
        app = OCC.XCAFApp._XCAFApp.XCAFApp_Application_GetApplication().GetObject()
        app.NewDocument(OCC.TCollection.TCollection_ExtendedString("MDTV-CAF"), h_doc)

        # Get root assembly
        doc = h_doc.GetObject()
        h_shape_tool = OCC.XCAFDoc.XCAFDoc_DocumentTool().ShapeTool(doc.Main())
        l_colors = OCC.XCAFDoc.XCAFDoc_DocumentTool().ColorTool(doc.Main())
        l_layers = OCC.XCAFDoc.XCAFDoc_DocumentTool().LayerTool(doc.Main())
        labels = OCC.TDF.TDF_LabelSequence()
        color_labels = OCC.TDF.TDF_LabelSequence()
        # TopoDS_Shape aShape;

        self.shape_tool = h_shape_tool.GetObject()
        self.top_label = self.shape_tool.NewShape()
        self.colors = l_colors.GetObject()
        self.layers = l_layers.GetObject()

        self.current_color = OCC.Quantity.Quantity_Color(OCC.Quantity.Quantity_NOC_RED)
        self.current_layer = self.layers.AddLayer(OCC.TCollection.TCollection_ExtendedString(layer_name))
        self.layer_names = {}

    def set_color(self, r=1, g=1, b=1, color=None):
        r"""Set color

        Parameters
        ----------
        r
        g
        b
        color

        """
        if color is not None:
            self.current_color = color
        else:
            clr = OCC.Quantity.Quantity_Color(r, g, b, 0)
            self.current_color = clr

    def set_layer(self, layer_name):
        r"""set the current layer name

        if the layer has already been set before, that TDF_Label will be used

        Parameters
        ----------
        layer_name: str
            name of the layer

        """
        if layer_name in self.layer_names:
            self.current_layer = self.layer_names[layer_name]
        else:
            self.current_layer = self.layers.AddLayer(OCC.TCollection.TCollection_ExtendedString(layer_name))
            self.layer_names[layer_name] = self.current_layer

    def add_shape(self, shape, color=None, layer=None):
        r"""add a shape to export

        a layer and color can be specified.

        note that the set colors / layers will be used for further objects
        added too!

        Parameters
        ----------
        shape : TopoDS_Shape
            the TopoDS_Shape to export
        color :
            can be a tuple: (r,g,b) or a Quantity_Color instance
        layer : str
            layer name

        """
        assert issubclass(shape.__class__, OCC.TopoDS.TopoDS_Shape) or isinstance(shape, OCC.TopoDS.TopoDS_Shape),\
            'not a TopoDS_Shape or subclass'
        shp_label = self.shape_tool.AddShape(shape)

        if color is None:
            self.colors.SetColor(shp_label, self.current_color, OCC.XCAFDoc.XCAFDoc_ColorGen)
        else:
            if isinstance(color, OCC.Quantity.Quantity_Color):
                self.current_color = color
            else:
                assert len(color) == 3, 'expected a tuple with three values < 1.'
                r, g, b = color
                self.set_color(r, g, b)
            self.colors.SetColor(shp_label, self.current_color, OCC.XCAFDoc.XCAFDoc_ColorGen)

        if layer is None:
            self.layers.SetLayer(shp_label, self.current_layer)
        else:
            self.set_layer(layer)
            self.layers.SetLayer(shp_label, self.current_layer)

    def write_file(self):
        r"""Write file"""
        work_session = OCC.XSControl.XSControl_WorkSession()
        writer = OCC.STEPCAFControl.STEPCAFControl_Writer(work_session.GetHandle(), False)
        writer.Transfer(self.h_doc, OCC.STEPControl.STEPControl_AsIs)
        logger.info('Writing STEP file')
        status = writer.Write(self.filename)
        logger.info('Status:', status)
