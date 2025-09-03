from typing import List, Optional, Dict, Iterable, Any, overload
import io
import collections.abc
from collections.abc import Sequence
from datetime import datetime
from aspose.pyreflection import Type
import aspose.pycore
import aspose.pydrawing
from uuid import UUID
import aspose.gis
import aspose.gis.common
import aspose.gis.common.formats
import aspose.gis.common.formats.dbase
import aspose.gis.common.formats.gdbtable
import aspose.gis.common.formats.mapinfo
import aspose.gis.common.formats.mapinfo.graphicalobjects
import aspose.gis.common.formats.mapinfo.interchangeformat
import aspose.gis.common.formats.mapinfo.styling
import aspose.gis.common.formats.mapinfo.tabformat
import aspose.gis.common.formats.mapinfo.tabformat.map
import aspose.gis.common.formats.wkb
import aspose.gis.common.formats.wkt
import aspose.gis.common.formats.xml
import aspose.gis.common.io
import aspose.gis.epsg
import aspose.gis.formats
import aspose.gis.formats.bmpw
import aspose.gis.formats.csv
import aspose.gis.formats.database
import aspose.gis.formats.database.dataediting
import aspose.gis.formats.database.fromdefinition
import aspose.gis.formats.esriascii
import aspose.gis.formats.esrijson
import aspose.gis.formats.filegdb
import aspose.gis.formats.gdal
import aspose.gis.formats.geojson
import aspose.gis.formats.geojsonseq
import aspose.gis.formats.geopackage
import aspose.gis.formats.geotiff
import aspose.gis.formats.gml
import aspose.gis.formats.gpx
import aspose.gis.formats.infile
import aspose.gis.formats.inmemory
import aspose.gis.formats.jpegw
import aspose.gis.formats.kml
import aspose.gis.formats.kml.specificfields
import aspose.gis.formats.kml.styles
import aspose.gis.formats.mapinfointerchange
import aspose.gis.formats.mapinfotab
import aspose.gis.formats.osmxml
import aspose.gis.formats.pngw
import aspose.gis.formats.postgis
import aspose.gis.formats.shapefile
import aspose.gis.formats.sqlserver
import aspose.gis.formats.tiffw
import aspose.gis.formats.topojson
import aspose.gis.formats.worldfile
import aspose.gis.formats.xyztile
import aspose.gis.geometries
import aspose.gis.geotools
import aspose.gis.geotools.extensions
import aspose.gis.geotools.layersmap
import aspose.gis.geotools.mapbuilder
import aspose.gis.geotools.wayanalyzer
import aspose.gis.imagemetadata
import aspose.gis.indexing
import aspose.gis.indexing.bplustree
import aspose.gis.indexing.qixtree
import aspose.gis.indexing.rtree
import aspose.gis.labeling
import aspose.gis.labeling.line
import aspose.gis.painting
import aspose.gis.projections
import aspose.gis.raster
import aspose.gis.raster.web
import aspose.gis.relationship
import aspose.gis.relationship.joins
import aspose.gis.rendering
import aspose.gis.rendering.colorizers
import aspose.gis.rendering.formats
import aspose.gis.rendering.formats.bmp
import aspose.gis.rendering.formats.jpeg
import aspose.gis.rendering.formats.png
import aspose.gis.rendering.formats.svg
import aspose.gis.rendering.labelings
import aspose.gis.rendering.sld
import aspose.gis.rendering.symbolizers
import aspose.gis.spatialreferencing
import aspose.gis.topology
import aspose.gis.topology.algorithms
import aspose.gis.topology.buffer
import aspose.gis.topology.graph

class Map:
    '''Map is a collection of layers that can be rendered on top of each other via :py:class:`aspose.gis.rendering.Renderer`.'''
    
    @overload
    def add(self, layer : aspose.gis.VectorLayer, keep_open : bool) -> None:
        '''Creates a :py:class:`aspose.gis.rendering.VectorMapLayer` with default symbolizer and adds it to the map. Layers are rendered in addition order.
        
        :param layer: A vector layer to represent by :py:class:`aspose.gis.rendering.VectorMapLayer`.
        :param keep_open: to leave the vector layer open after the :py:class:`aspose.gis.rendering.Map` object is disposed;
        to dispose the layer.'''
        raise NotImplementedError()
    
    @overload
    def add(self, layer : aspose.gis.VectorLayer, symbolizer : aspose.gis.rendering.symbolizers.VectorSymbolizer, keep_open : bool) -> None:
        '''Creates and adds a :py:class:`aspose.gis.rendering.VectorMapLayer` to the map. Layers are rendered in addition order.
        
        :param layer: A vector layer to represent by :py:class:`aspose.gis.rendering.VectorMapLayer`.
        :param symbolizer: A symbolizer to use for rendering. If , default symbolizer is used.
        :param keep_open: to leave the vector layer open after the :py:class:`aspose.gis.rendering.Map` object is disposed;
        to dispose the layer.'''
        raise NotImplementedError()
    
    @overload
    def add(self, layer : aspose.gis.VectorLayer, symbolizer : aspose.gis.rendering.symbolizers.VectorSymbolizer, labeling : aspose.gis.rendering.labelings.Labeling, keep_open : bool) -> None:
        '''Creates and adds a :py:class:`aspose.gis.rendering.VectorMapLayer` to the map. Layers are rendered in addition order.
        
        :param layer: A vector layer to represent by :py:class:`aspose.gis.rendering.VectorMapLayer`.
        :param symbolizer: A symbolizer to use for rendering. If , default symbolizer is used.
        :param labeling: Labeling to use to label features in layer. If , default :py:class:`aspose.gis.rendering.labelings.NullLabeling` will be used.
        :param keep_open: to leave the layer open after the :py:class:`aspose.gis.rendering.Map` object is disposed; otherwise, .'''
        raise NotImplementedError()
    
    @overload
    def add(self, layer : aspose.gis.VectorLayer, symbolizer : aspose.gis.rendering.symbolizers.VectorSymbolizer, labeling : aspose.gis.rendering.labelings.Labeling, default_reference_system : aspose.gis.spatialreferencing.SpatialReferenceSystem, keep_open : bool) -> None:
        '''Creates and adds a :py:class:`aspose.gis.rendering.VectorMapLayer` to the map. Layers are rendered in addition order.
        
        :param layer: A vector layer to represent by :py:class:`aspose.gis.rendering.VectorMapLayer`.
        :param symbolizer: A symbolizer to use for rendering. If , default symbolizer is used.
        :param labeling: Labeling to use to label features in layer. If , default :py:class:`aspose.gis.rendering.labelings.NullLabeling` will be used.
        :param default_reference_system: Specifies a value for a source spatial reference (layer\sequence) if that is missing. Default **null** will be used.
        :param keep_open: to leave the layer open after the :py:class:`aspose.gis.rendering.Map` object is disposed; otherwise, .'''
        raise NotImplementedError()
    
    @overload
    def add(self, features_sequence : aspose.gis.FeaturesSequence) -> None:
        '''Creates and adds a :py:class:`aspose.gis.rendering.VectorMapLayer` to the map. Layers are rendered in addition order.
        
        :param features_sequence: A features sequence to represent by :py:class:`aspose.gis.rendering.VectorMapLayer`.'''
        raise NotImplementedError()
    
    @overload
    def add(self, features_sequence : aspose.gis.FeaturesSequence, symbolizer : aspose.gis.rendering.symbolizers.VectorSymbolizer) -> None:
        '''Creates and adds a :py:class:`aspose.gis.rendering.VectorMapLayer` to the map. Layers are rendered in addition order.
        
        :param features_sequence: A features sequence to represent by :py:class:`aspose.gis.rendering.VectorMapLayer`.
        :param symbolizer: A symbolizer to use for rendering. If , default symbolizer is used.'''
        raise NotImplementedError()
    
    @overload
    def add(self, features_sequence : aspose.gis.FeaturesSequence, symbolizer : aspose.gis.rendering.symbolizers.VectorSymbolizer, labeling : aspose.gis.rendering.labelings.Labeling) -> None:
        '''Creates and adds a :py:class:`aspose.gis.rendering.VectorMapLayer` to the map. Layers are rendered in addition order.
        
        :param features_sequence: A features sequence to represent by :py:class:`aspose.gis.rendering.VectorMapLayer`.
        :param symbolizer: A symbolizer to use for rendering.
        :param labeling: Labeling to use to label features in layer. If , :py:class:`aspose.gis.rendering.labelings.NullLabeling` will be used.'''
        raise NotImplementedError()
    
    @overload
    def add(self, map_layer : aspose.gis.rendering.MapLayer) -> None:
        '''Adds a layer to the map. Layers are rendered in addition order.
        
        :param map_layer: The layer to be added.'''
        raise NotImplementedError()
    
    @overload
    def add(self, layer : aspose.gis.raster.RasterLayer, colorizer : aspose.gis.rendering.colorizers.RasterColorizer, keep_open : bool) -> None:
        '''Creates a :py:class:`aspose.gis.rendering.RasterMapLayer` with default colorizer and adds it to the map.
        
        :param layer: A vector layer to represent by :py:class:`aspose.gis.raster.RasterLayer`.
        :param colorizer: A colorizer to use for rendering. If , default colorizer is used.
        :param keep_open: to leave the raster layer open after the :py:class:`aspose.gis.rendering.Map` object is disposed;
        to dispose the layer.'''
        raise NotImplementedError()
    
    @overload
    def render(self, output_path : str, renderer : aspose.gis.rendering.Renderer) -> None:
        '''Renders map into a file.
        
        :param output_path: Path to the output file.
        :param renderer: Renderer to use.'''
        raise NotImplementedError()
    
    @overload
    def render(self, output_path : aspose.gis.AbstractPath, renderer : aspose.gis.rendering.Renderer) -> None:
        '''Renders map into a file.
        
        :param output_path: Path to the output file.
        :param renderer: Renderer to use.'''
        raise NotImplementedError()
    
    @property
    def extent(self) -> aspose.gis.Extent:
        '''Specifies bounds of map to render.
        If set to , extent is calculated during rendering to include all geometries in all layers.'''
        raise NotImplementedError()
    
    @extent.setter
    def extent(self, value : aspose.gis.Extent) -> None:
        '''Specifies bounds of map to render.
        If set to , extent is calculated during rendering to include all geometries in all layers.'''
        raise NotImplementedError()
    
    @property
    def padding(self) -> aspose.gis.rendering.Measurement:
        '''Specifies padding to add to the extent.'''
        raise NotImplementedError()
    
    @padding.setter
    def padding(self, value : aspose.gis.rendering.Measurement) -> None:
        '''Specifies padding to add to the extent.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> aspose.gis.rendering.Measurement:
        '''Visual width of the map.'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : aspose.gis.rendering.Measurement) -> None:
        '''Visual width of the map.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> aspose.gis.rendering.Measurement:
        '''Visual height of the map.'''
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : aspose.gis.rendering.Measurement) -> None:
        '''Visual height of the map.'''
        raise NotImplementedError()
    
    @property
    def resolution(self) -> float:
        '''Resolution to be used to render this map and to convert between :py:class:`aspose.gis.rendering.Measurement`. Defaults to 96.'''
        raise NotImplementedError()
    
    @resolution.setter
    def resolution(self, value : float) -> None:
        '''Resolution to be used to render this map and to convert between :py:class:`aspose.gis.rendering.Measurement`. Defaults to 96.'''
        raise NotImplementedError()
    
    @property
    def background_color(self) -> aspose.pydrawing.Color:
        '''Background color of the map. Defaults to :py:attr:`aspose.pydrawing.Color.Transparent`.'''
        raise NotImplementedError()
    
    @background_color.setter
    def background_color(self, value : aspose.pydrawing.Color) -> None:
        '''Background color of the map. Defaults to :py:attr:`aspose.pydrawing.Color.Transparent`.'''
        raise NotImplementedError()
    
    @property
    def spatial_reference_system(self) -> aspose.gis.spatialreferencing.SpatialReferenceSystem:
        ''':py:attr:`aspose.gis.rendering.Map.spatial_reference_system` of the map.'''
        raise NotImplementedError()
    
    @spatial_reference_system.setter
    def spatial_reference_system(self, value : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> None:
        ''':py:attr:`aspose.gis.rendering.Map.spatial_reference_system` of the map.'''
        raise NotImplementedError()
    

class MapLayer:
    '''A ``MapLayer``is a base class for layers inside the :py:class:`aspose.gis.rendering.Map`.'''
    
    @property
    def opacity(self) -> float:
        '''Opacity of the layer.'''
        raise NotImplementedError()
    
    @opacity.setter
    def opacity(self, value : float) -> None:
        '''Opacity of the layer.'''
        raise NotImplementedError()
    

class Measurement:
    '''A number that indicates a render measurement.'''
    
    @staticmethod
    def pixels(value : float) -> aspose.gis.rendering.Measurement:
        '''Returns a new instance of ``Measurement`` that represents length in pixels.
        
        :param value: Number of pixels.
        :returns: New instance of ``Measurement`` class.'''
        raise NotImplementedError()
    
    @staticmethod
    def points(value : float) -> aspose.gis.rendering.Measurement:
        '''Returns a new instance of ``Measurement`` that represents length in points.
        
        :param value: Number of points.
        :returns: New instance of ``Measurement`` class.'''
        raise NotImplementedError()
    
    @staticmethod
    def millimeters(value : float) -> aspose.gis.rendering.Measurement:
        '''Returns a new instance of ``Measurement`` that represents length in millimeters.
        
        :param value: Number of millimeters.
        :returns: New instance of ``Measurement`` class.'''
        raise NotImplementedError()
    
    @staticmethod
    def inches(value : float) -> aspose.gis.rendering.Measurement:
        '''Returns a new instance of ``Measurement`` that represents length in inches.
        
        :param value: Number of inches.
        :returns: New instance of ``Measurement`` class.'''
        raise NotImplementedError()
    
    @staticmethod
    def map_units(value : float) -> aspose.gis.rendering.Measurement:
        '''Returns a new instance of ``Measurement`` that represents length in maps Spatial Reference units.
        
        :param value: Number of units.
        :returns: New instance of ``Measurement`` class.'''
        raise NotImplementedError()
    
    @staticmethod
    def meters_on_earth(value : float) -> aspose.gis.rendering.Measurement:
        '''Returns a new instance of ``Measurement`` that represents length in meters on the Earth.
        
        :param value: Number of meters.
        :returns: New instance of ``Measurement`` class.'''
        raise NotImplementedError()
    
    zero : aspose.gis.rendering.Measurement
    '''A measurement of zero length.'''
    @property
    def value(self) -> float:
        '''A number that indicates the length of the measurement.'''
        raise NotImplementedError()
    
    @property
    def unit(self) -> aspose.gis.rendering.Unit:
        '''A unit of measurement.'''
        raise NotImplementedError()
    

class RasterMapLayer(MapLayer):
    '''A layer inside :py:class:`aspose.gis.rendering.Map` that represents a raster layer data.'''
    
    @property
    def opacity(self) -> float:
        '''Opacity of the layer.'''
        raise NotImplementedError()
    
    @opacity.setter
    def opacity(self, value : float) -> None:
        '''Opacity of the layer.'''
        raise NotImplementedError()
    
    @property
    def colorizer(self) -> aspose.gis.rendering.colorizers.RasterColorizer:
        '''Colorizer to use to render cells of the raster.'''
        raise NotImplementedError()
    
    @colorizer.setter
    def colorizer(self, value : aspose.gis.rendering.colorizers.RasterColorizer) -> None:
        '''Colorizer to use to render cells of the raster.'''
        raise NotImplementedError()
    
    @property
    def resampling(self) -> aspose.gis.rendering.RasterMapResampling:
        '''Specifies warp options of the layer on a map.'''
        raise NotImplementedError()
    
    @resampling.setter
    def resampling(self, value : aspose.gis.rendering.RasterMapResampling) -> None:
        '''Specifies warp options of the layer on a map.'''
        raise NotImplementedError()
    

class RasterMapResampling:
    '''This class describes how to resample a raster layer when rendering a map.'''
    
    @property
    def width(self) -> int:
        '''Specifies raster width on a map in pixels and columns.
        If the value is set to 0, the width is automatically computed. The default value is "0".'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : int) -> None:
        '''Specifies raster width on a map in pixels and columns.
        If the value is set to 0, the width is automatically computed. The default value is "0".'''
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        '''Specifies raster height on a map in pixels and columns.
        If the value is set to 0, the height is automatically computed. The default value is "0".'''
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : int) -> None:
        '''Specifies raster height on a map in pixels and columns.
        If the value is set to 0, the height is automatically computed. The default value is "0".'''
        raise NotImplementedError()
    

class Renderer:
    '''A base class for renderers.'''
    
    @overload
    def render(self, map : aspose.gis.rendering.Map, output_path : str) -> None:
        '''Renders map.
        
        :param map: Map to render.
        :param output_path: Path to the output file.'''
        raise NotImplementedError()
    
    @overload
    def render(self, map : aspose.gis.rendering.Map, output_path : aspose.gis.AbstractPath) -> None:
        '''Renders map.
        
        :param map: Map to render.
        :param output_path: Path to the output file.'''
        raise NotImplementedError()
    

class Renderers:
    '''Renderers for all supported formats.'''
    
    svg : aspose.gis.rendering.formats.svg.SvgRenderer
    '''A renderer that renders into the SVG format.'''
    png : aspose.gis.rendering.formats.png.PngRenderer
    '''A renderer that renders into the PNG format.'''
    jpeg : aspose.gis.rendering.formats.jpeg.JpegRenderer
    '''A renderer that renders into the JPEG format.'''
    bmp : aspose.gis.rendering.formats.bmp.BmpRenderer
    '''A renderer that renders into the BMP format.'''

class VectorMapLayer(MapLayer):
    '''A layer inside :py:class:`aspose.gis.rendering.Map` that represents a vector layer data.'''
    
    @overload
    def import_sld(self, path : str, options : aspose.gis.rendering.sld.SldImportOptions) -> None:
        '''Imports style from Styled Layer Descriptor file located at the specified path.
        
        :param path: Path to the Styled Layer Descriptor file.
        :param options: Import options.'''
        raise NotImplementedError()
    
    @overload
    def import_sld(self, path : aspose.gis.AbstractPath, options : aspose.gis.rendering.sld.SldImportOptions) -> None:
        '''Imports style from Styled Layer Descriptor file located at the specified path.
        
        :param path: Path to the Styled Layer Descriptor file.
        :param options: Import options.'''
        raise NotImplementedError()
    
    def import_sld_from_string(self, sld : str, options : aspose.gis.rendering.sld.SldImportOptions) -> None:
        '''Imports style from the specified Styled Layer Descriptor string.
        
        :param sld: Styled Layer Descriptor.
        :param options: Import options.'''
        raise NotImplementedError()
    
    @property
    def opacity(self) -> float:
        '''Opacity of the layer.'''
        raise NotImplementedError()
    
    @opacity.setter
    def opacity(self, value : float) -> None:
        '''Opacity of the layer.'''
        raise NotImplementedError()
    
    @property
    def features_sequence(self) -> aspose.gis.FeaturesSequence:
        '''The features sequence represented by this ``VectorMapLayer``.'''
        raise NotImplementedError()
    
    @property
    def symbolizer(self) -> aspose.gis.rendering.symbolizers.VectorSymbolizer:
        '''Symbolizer to use to render features of the layer.'''
        raise NotImplementedError()
    
    @symbolizer.setter
    def symbolizer(self, value : aspose.gis.rendering.symbolizers.VectorSymbolizer) -> None:
        '''Symbolizer to use to render features of the layer.'''
        raise NotImplementedError()
    
    @property
    def labeling(self) -> aspose.gis.rendering.labelings.Labeling:
        '''Specifies warp options of the map layer.'''
        raise NotImplementedError()
    
    @labeling.setter
    def labeling(self, value : aspose.gis.rendering.labelings.Labeling) -> None:
        '''Specifies warp options of the map layer.'''
        raise NotImplementedError()
    

class CapStyle:
    '''Specifies how lines are rendered at their ends.'''
    
    BUTT : CapStyle
    '''Sharp square edge.'''
    ROUND : CapStyle
    '''Rounded edge.'''
    SQUARE : CapStyle
    '''Slightly elongated square edge.'''

class FillStyle:
    '''Specifies a filling pattern.'''
    
    SOLID : FillStyle
    '''Solid fill.'''
    NONE : FillStyle
    '''Do not fill.'''
    HORIZONTAL_HATCH : FillStyle
    '''A pattern of horizontal lines.'''
    VERTICAL_HATCH : FillStyle
    '''A pattern of vertical lines.'''
    CROSS_HATCH : FillStyle
    '''A pattern of horizontal and vertical lines that cross.'''
    FORWARD_DIAGONAL_HATCH : FillStyle
    '''A pattern of lines on a diagonal from upper left to lower right.'''
    BACKWARD_DIAGONAL_HATCH : FillStyle
    '''A pattern of lines on a diagonal from upper right to lower left.'''
    DIAGONAL_CROSS_HATCH : FillStyle
    '''A pattern of crisscross diagonal lines.'''

class LineJoin:
    '''Determines how lines are rendered at intersections of line segments.'''
    
    MITER : LineJoin
    '''Sharp corner.'''
    ROUND : LineJoin
    '''Rounded corner.'''
    BEVEL : LineJoin
    '''Diagonal corner.'''

class StrokeStyle:
    '''Specifies a stroke style.'''
    
    SOLID : StrokeStyle
    '''Specifies a plain line.'''
    NONE : StrokeStyle
    '''Specifies, that no line should be drawn.'''
    DASH : StrokeStyle
    '''Specifies a dash line.'''
    DOT : StrokeStyle
    '''Specifies a dotted line.'''
    DASH_DOT : StrokeStyle
    '''Specifies alternate dots and dashes .'''
    DASH_DOT_DOT : StrokeStyle
    '''Specifies a dash-dot-dot line.'''
    CUSTOM : StrokeStyle
    '''Custom dash pattern line.'''

class Unit:
    '''A unit of measurement.'''
    
    PIXELS : Unit
    '''Specifies pixels.'''
    POINTS : Unit
    '''Specifies points. There are 72 points in inch.'''
    MILLIMETERS : Unit
    '''Specifies millimeters.'''
    INCHES : Unit
    '''Specifies inches. One inch is 25.4 millimeters.'''
    MAP_UNITS : Unit
    '''Specifies Spatial Reference specific map units.'''
    METERS_ON_EARTH : Unit
    '''Specifies a length in actual meters on the Earth regardless what is the :py:attr:`aspose.gis.rendering.Map.spatial_reference_system`.'''

