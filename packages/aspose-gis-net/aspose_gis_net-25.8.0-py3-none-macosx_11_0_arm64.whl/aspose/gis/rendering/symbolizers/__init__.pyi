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

class GeometryGenerator(VectorSymbolizer):
    '''Decorate a symbolizer to modify feature\'s geometry before rendering.'''
    
    null : aspose.gis.rendering.symbolizers.NullVectorSymbolizer
    '''The :py:class:`aspose.gis.rendering.symbolizers.NullVectorSymbolizer` draws nothing and effectively skips rendering of a geometry it is applied to.'''
    @property
    def symbolizer(self) -> aspose.gis.rendering.symbolizers.VectorSymbolizer:
        '''Specifies a symbolizer to apply to the modified geometry.
        Default is .'''
        raise NotImplementedError()
    
    @symbolizer.setter
    def symbolizer(self, value : aspose.gis.rendering.symbolizers.VectorSymbolizer) -> None:
        '''Specifies a symbolizer to apply to the modified geometry.
        Default is .'''
        raise NotImplementedError()
    

class LayeredSymbolizer(VectorSymbolizer):
    '''A symbolizer that renders several other symbolizers.'''
    
    def add(self, symbolizer : aspose.gis.rendering.symbolizers.VectorSymbolizer) -> None:
        '''Adds the specified symbolizer.
        
        :param symbolizer: The symbolizer to add.'''
        raise NotImplementedError()
    
    null : aspose.gis.rendering.symbolizers.NullVectorSymbolizer
    '''The :py:class:`aspose.gis.rendering.symbolizers.NullVectorSymbolizer` draws nothing and effectively skips rendering of a geometry it is applied to.'''
    @property
    def rendering_order(self) -> aspose.gis.rendering.symbolizers.RenderingOrder:
        '''Determines the rendering order.
        
        *
        
        *'''
        raise NotImplementedError()
    
    @rendering_order.setter
    def rendering_order(self, value : aspose.gis.rendering.symbolizers.RenderingOrder) -> None:
        '''Determines the rendering order.
        
        *
        
        *'''
        raise NotImplementedError()
    

class MarkerCluster(VectorSymbolizer):
    '''Marker cluster symbolizer.'''
    
    null : aspose.gis.rendering.symbolizers.NullVectorSymbolizer
    '''The :py:class:`aspose.gis.rendering.symbolizers.NullVectorSymbolizer` draws nothing and effectively skips rendering of a geometry it is applied to.'''
    @property
    def marker(self) -> aspose.gis.rendering.symbolizers.VectorSymbolizer:
        '''Specifies the marker symbolizer in the cluster center.'''
        raise NotImplementedError()
    
    @marker.setter
    def marker(self, value : aspose.gis.rendering.symbolizers.VectorSymbolizer) -> None:
        '''Specifies the marker symbolizer in the cluster center.'''
        raise NotImplementedError()
    
    @property
    def nested_marker(self) -> aspose.gis.rendering.symbolizers.VectorSymbolizer:
        '''Specifies the marker symbolizer for nested cluster points. The default is :py:attr:`aspose.gis.rendering.symbolizers.VectorSymbolizer.null`.'''
        raise NotImplementedError()
    
    @nested_marker.setter
    def nested_marker(self, value : aspose.gis.rendering.symbolizers.VectorSymbolizer) -> None:
        '''Specifies the marker symbolizer for nested cluster points. The default is :py:attr:`aspose.gis.rendering.symbolizers.VectorSymbolizer.null`.'''
        raise NotImplementedError()
    

class MarkerLine(VectorSymbolizer):
    '''Marker line symbolizer.'''
    
    null : aspose.gis.rendering.symbolizers.NullVectorSymbolizer
    '''The :py:class:`aspose.gis.rendering.symbolizers.NullVectorSymbolizer` draws nothing and effectively skips rendering of a geometry it is applied to.'''
    @property
    def marker(self) -> aspose.gis.rendering.symbolizers.VectorSymbolizer:
        '''Specifies the marker symbolizer along the line.'''
        raise NotImplementedError()
    
    @marker.setter
    def marker(self, value : aspose.gis.rendering.symbolizers.VectorSymbolizer) -> None:
        '''Specifies the marker symbolizer along the line.'''
        raise NotImplementedError()
    
    @property
    def interval(self) -> aspose.gis.rendering.Measurement:
        '''Specifies the interval between markers along the line.'''
        raise NotImplementedError()
    
    @interval.setter
    def interval(self, value : aspose.gis.rendering.Measurement) -> None:
        '''Specifies the interval between markers along the line.'''
        raise NotImplementedError()
    
    @property
    def offset_along_line(self) -> aspose.gis.rendering.Measurement:
        '''Specifies the offset along the line for the first marker.'''
        raise NotImplementedError()
    
    @offset_along_line.setter
    def offset_along_line(self, value : aspose.gis.rendering.Measurement) -> None:
        '''Specifies the offset along the line for the first marker.'''
        raise NotImplementedError()
    
    @property
    def offset(self) -> aspose.gis.rendering.Measurement:
        '''Specifies offset from the original line.
        For positive distance the offset will be at the left side of the input line (relative to the line direction).
        For a negative distance it will be at the right side.'''
        raise NotImplementedError()
    
    @offset.setter
    def offset(self, value : aspose.gis.rendering.Measurement) -> None:
        '''Specifies offset from the original line.
        For positive distance the offset will be at the left side of the input line (relative to the line direction).
        For a negative distance it will be at the right side.'''
        raise NotImplementedError()
    
    @property
    def rotate_markers(self) -> bool:
        '''Specifies whether markers should be rotated along the line.'''
        raise NotImplementedError()
    
    @rotate_markers.setter
    def rotate_markers(self, value : bool) -> None:
        '''Specifies whether markers should be rotated along the line.'''
        raise NotImplementedError()
    

class MarkerPatternFill(VectorSymbolizer):
    '''Marker pattern fill symbolizer.'''
    
    null : aspose.gis.rendering.symbolizers.NullVectorSymbolizer
    '''The :py:class:`aspose.gis.rendering.symbolizers.NullVectorSymbolizer` draws nothing and effectively skips rendering of a geometry it is applied to.'''
    @property
    def marker(self) -> aspose.gis.rendering.symbolizers.VectorSymbolizer:
        '''Specifies the marker symbolizer for filling.'''
        raise NotImplementedError()
    
    @marker.setter
    def marker(self, value : aspose.gis.rendering.symbolizers.VectorSymbolizer) -> None:
        '''Specifies the marker symbolizer for filling.'''
        raise NotImplementedError()
    
    @property
    def horizontal_interval(self) -> aspose.gis.rendering.Measurement:
        '''Specifies the horizontal interval between markers.'''
        raise NotImplementedError()
    
    @horizontal_interval.setter
    def horizontal_interval(self, value : aspose.gis.rendering.Measurement) -> None:
        '''Specifies the horizontal interval between markers.'''
        raise NotImplementedError()
    
    @property
    def vertical_interval(self) -> aspose.gis.rendering.Measurement:
        '''Specifies the vertical interval between markers.'''
        raise NotImplementedError()
    
    @vertical_interval.setter
    def vertical_interval(self, value : aspose.gis.rendering.Measurement) -> None:
        '''Specifies the vertical interval between markers.'''
        raise NotImplementedError()
    
    @property
    def horizontal_displacement(self) -> aspose.gis.rendering.Measurement:
        '''Specifies the horizontal offset for markers in even horizontal line.'''
        raise NotImplementedError()
    
    @horizontal_displacement.setter
    def horizontal_displacement(self, value : aspose.gis.rendering.Measurement) -> None:
        '''Specifies the horizontal offset for markers in even horizontal line.'''
        raise NotImplementedError()
    
    @property
    def vertical_displacement(self) -> aspose.gis.rendering.Measurement:
        '''Specifies the vertical offset for markers in even vertical line.'''
        raise NotImplementedError()
    
    @vertical_displacement.setter
    def vertical_displacement(self, value : aspose.gis.rendering.Measurement) -> None:
        '''Specifies the vertical offset for markers in even vertical line.'''
        raise NotImplementedError()
    

class MixedGeometrySymbolizer(VectorSymbolizer):
    '''Applies correct symbolizer to a feature geometry according to its geometry type.'''
    
    null : aspose.gis.rendering.symbolizers.NullVectorSymbolizer
    '''The :py:class:`aspose.gis.rendering.symbolizers.NullVectorSymbolizer` draws nothing and effectively skips rendering of a geometry it is applied to.'''
    @property
    def point_symbolizer(self) -> aspose.gis.rendering.symbolizers.VectorSymbolizer:
        '''Specifies a symbolizer to use for point geometries in the layer.'''
        raise NotImplementedError()
    
    @point_symbolizer.setter
    def point_symbolizer(self, value : aspose.gis.rendering.symbolizers.VectorSymbolizer) -> None:
        '''Specifies a symbolizer to use for point geometries in the layer.'''
        raise NotImplementedError()
    
    @property
    def line_symbolizer(self) -> aspose.gis.rendering.symbolizers.VectorSymbolizer:
        '''Specifies a symbolizer to use for line geometries in the layer.'''
        raise NotImplementedError()
    
    @line_symbolizer.setter
    def line_symbolizer(self, value : aspose.gis.rendering.symbolizers.VectorSymbolizer) -> None:
        '''Specifies a symbolizer to use for line geometries in the layer.'''
        raise NotImplementedError()
    
    @property
    def polygon_symbolizer(self) -> aspose.gis.rendering.symbolizers.VectorSymbolizer:
        '''Specifies a symbolizer to use for polygon geometries in the layer.'''
        raise NotImplementedError()
    
    @polygon_symbolizer.setter
    def polygon_symbolizer(self, value : aspose.gis.rendering.symbolizers.VectorSymbolizer) -> None:
        '''Specifies a symbolizer to use for polygon geometries in the layer.'''
        raise NotImplementedError()
    

class NullVectorSymbolizer(VectorSymbolizer):
    '''The ``NullSymbolizer`` draws nothing and effectively skips rendering of a geometry it is applied to.'''
    
    null : aspose.gis.rendering.symbolizers.NullVectorSymbolizer
    '''The :py:class:`aspose.gis.rendering.symbolizers.NullVectorSymbolizer` draws nothing and effectively skips rendering of a geometry it is applied to.'''
    instance : aspose.gis.rendering.symbolizers.NullVectorSymbolizer
    '''Gets an instance of ``NullSymbolizer``.'''

class RasterImageMarker(VectorSymbolizer):
    '''This symbolizer renders a provided raster image.'''
    
    def clone(self) -> aspose.gis.rendering.symbolizers.RasterImageMarker:
        '''Clones this instance.
        
        :returns: A clone of this instance.'''
        raise NotImplementedError()
    
    null : aspose.gis.rendering.symbolizers.NullVectorSymbolizer
    '''The :py:class:`aspose.gis.rendering.symbolizers.NullVectorSymbolizer` draws nothing and effectively skips rendering of a geometry it is applied to.'''
    @property
    def width(self) -> aspose.gis.rendering.Measurement:
        '''Specifies the width of the marker.'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : aspose.gis.rendering.Measurement) -> None:
        '''Specifies the width of the marker.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> aspose.gis.rendering.Measurement:
        '''Specifies the height of the marker.'''
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : aspose.gis.rendering.Measurement) -> None:
        '''Specifies the height of the marker.'''
        raise NotImplementedError()
    
    @property
    def opacity(self) -> float:
        '''Opacity of the layer. Default value is 1.0.'''
        raise NotImplementedError()
    
    @opacity.setter
    def opacity(self, value : float) -> None:
        '''Opacity of the layer. Default value is 1.0.'''
        raise NotImplementedError()
    
    @property
    def horizontal_anchor_point(self) -> aspose.gis.rendering.symbolizers.HorizontalAnchor:
        '''specifies which side of a marker shape will be aligned horizontally with the point location.'''
        raise NotImplementedError()
    
    @horizontal_anchor_point.setter
    def horizontal_anchor_point(self, value : aspose.gis.rendering.symbolizers.HorizontalAnchor) -> None:
        '''specifies which side of a marker shape will be aligned horizontally with the point location.'''
        raise NotImplementedError()
    
    @property
    def vertical_anchor_point(self) -> aspose.gis.rendering.symbolizers.VerticalAnchor:
        '''Specifies which side of a marker shape will be aligned vertically with the point location.'''
        raise NotImplementedError()
    
    @vertical_anchor_point.setter
    def vertical_anchor_point(self, value : aspose.gis.rendering.symbolizers.VerticalAnchor) -> None:
        '''Specifies which side of a marker shape will be aligned vertically with the point location.'''
        raise NotImplementedError()
    
    @property
    def horizontal_offset(self) -> aspose.gis.rendering.Measurement:
        '''Specifies horizontal offset from a point location to the shape anchor point.'''
        raise NotImplementedError()
    
    @horizontal_offset.setter
    def horizontal_offset(self, value : aspose.gis.rendering.Measurement) -> None:
        '''Specifies horizontal offset from a point location to the shape anchor point.'''
        raise NotImplementedError()
    
    @property
    def vertical_offset(self) -> aspose.gis.rendering.Measurement:
        '''Specifies vertical offset from a point location to the shape anchor point.'''
        raise NotImplementedError()
    
    @vertical_offset.setter
    def vertical_offset(self, value : aspose.gis.rendering.Measurement) -> None:
        '''Specifies vertical offset from a point location to the shape anchor point.'''
        raise NotImplementedError()
    
    @property
    def rotation(self) -> float:
        '''Specifies the rotation of the symbol about its center point, in decimal degrees.
        Positive values indicate rotation in the clockwise direction, negative values indicate counter-clockwise rotation.'''
        raise NotImplementedError()
    
    @rotation.setter
    def rotation(self, value : float) -> None:
        '''Specifies the rotation of the symbol about its center point, in decimal degrees.
        Positive values indicate rotation in the clockwise direction, negative values indicate counter-clockwise rotation.'''
        raise NotImplementedError()
    

class Rule:
    '''A user-defined rule for :py:class:`aspose.gis.rendering.symbolizers.RuleBasedSymbolizer`.'''
    
    @staticmethod
    def create_else_rule(symbolizer : aspose.gis.rendering.symbolizers.VectorSymbolizer) -> aspose.gis.rendering.symbolizers.Rule:
        '''Creates new rule that applies a symbolizer to feature whenever it doesn\'t match any filter rule.
        
        :param symbolizer: Symbolizer to apply.
        :returns: New Rule object.'''
        raise NotImplementedError()
    
    @property
    def is_else_rule(self) -> bool:
        '''Gets a value indicating whether this rule is "else-rule".'''
        raise NotImplementedError()
    
    @property
    def is_filter_rule(self) -> bool:
        '''Gets a value indicating whether this rule is "filter-rule".'''
        raise NotImplementedError()
    
    @property
    def symbolizer(self) -> aspose.gis.rendering.symbolizers.VectorSymbolizer:
        '''Symbolizer to apply to the feature.'''
        raise NotImplementedError()
    

class RuleBasedSymbolizer(VectorSymbolizer):
    '''Applies a symbolizer to feature geometries according to user-defined rules.'''
    
    def add_else_rule(self, symbolizer : aspose.gis.rendering.symbolizers.VectorSymbolizer) -> None:
        '''Adds a symbolizer that will be applied to features that don\'t match any filtering rule.
        
        :param symbolizer: A symbolizer.'''
        raise NotImplementedError()
    
    def add(self, rule : aspose.gis.rendering.symbolizers.Rule) -> None:
        '''Adds a rule.
        
        :param rule: Rule to add.'''
        raise NotImplementedError()
    
    null : aspose.gis.rendering.symbolizers.NullVectorSymbolizer
    '''The :py:class:`aspose.gis.rendering.symbolizers.NullVectorSymbolizer` draws nothing and effectively skips rendering of a geometry it is applied to.'''

class SimpleFill(VectorSymbolizer):
    '''Simple polygon symbolizer.'''
    
    def clone(self) -> aspose.gis.rendering.symbolizers.SimpleFill:
        '''Clones this instance.
        
        :returns: A clone of this instance.'''
        raise NotImplementedError()
    
    null : aspose.gis.rendering.symbolizers.NullVectorSymbolizer
    '''The :py:class:`aspose.gis.rendering.symbolizers.NullVectorSymbolizer` draws nothing and effectively skips rendering of a geometry it is applied to.'''
    @property
    def fill_color(self) -> aspose.pydrawing.Color:
        '''Specifies the color and transparency for filling.'''
        raise NotImplementedError()
    
    @fill_color.setter
    def fill_color(self, value : aspose.pydrawing.Color) -> None:
        '''Specifies the color and transparency for filling.'''
        raise NotImplementedError()
    
    @property
    def stroke_color(self) -> aspose.pydrawing.Color:
        '''Specifies the color and transparency given to the line.'''
        raise NotImplementedError()
    
    @stroke_color.setter
    def stroke_color(self, value : aspose.pydrawing.Color) -> None:
        '''Specifies the color and transparency given to the line.'''
        raise NotImplementedError()
    
    @property
    def stroke_width(self) -> aspose.gis.rendering.Measurement:
        '''Specifies the width of the line.'''
        raise NotImplementedError()
    
    @stroke_width.setter
    def stroke_width(self, value : aspose.gis.rendering.Measurement) -> None:
        '''Specifies the width of the line.'''
        raise NotImplementedError()
    
    @property
    def stroke_line_join(self) -> aspose.gis.rendering.LineJoin:
        '''Determines how lines are rendered at intersection of line segments.'''
        raise NotImplementedError()
    
    @stroke_line_join.setter
    def stroke_line_join(self, value : aspose.gis.rendering.LineJoin) -> None:
        '''Determines how lines are rendered at intersection of line segments.'''
        raise NotImplementedError()
    
    @property
    def stroke_style(self) -> aspose.gis.rendering.StrokeStyle:
        '''Specifies how the symbol lines should be drawn.'''
        raise NotImplementedError()
    
    @stroke_style.setter
    def stroke_style(self, value : aspose.gis.rendering.StrokeStyle) -> None:
        '''Specifies how the symbol lines should be drawn.'''
        raise NotImplementedError()
    
    @property
    def stroke_dash_pattern(self) -> Iterable[aspose.gis.rendering.Measurement]:
        '''Specifies an array of distances that specifies the lengths of alternating dashes and spaces
        in dashed lines.'''
        raise NotImplementedError()
    
    @stroke_dash_pattern.setter
    def stroke_dash_pattern(self, value : Iterable[aspose.gis.rendering.Measurement]) -> None:
        '''Specifies an array of distances that specifies the lengths of alternating dashes and spaces
        in dashed lines.'''
        raise NotImplementedError()
    
    @property
    def stroke_dash_offset(self) -> aspose.gis.rendering.Measurement:
        '''Specifies the distance from the start of a line to the beginning of a dash pattern.'''
        raise NotImplementedError()
    
    @stroke_dash_offset.setter
    def stroke_dash_offset(self, value : aspose.gis.rendering.Measurement) -> None:
        '''Specifies the distance from the start of a line to the beginning of a dash pattern.'''
        raise NotImplementedError()
    
    @property
    def fill_style(self) -> aspose.gis.rendering.FillStyle:
        '''Specifies the fill style.'''
        raise NotImplementedError()
    
    @fill_style.setter
    def fill_style(self, value : aspose.gis.rendering.FillStyle) -> None:
        '''Specifies the fill style.'''
        raise NotImplementedError()
    
    @property
    def horizontal_offset(self) -> aspose.gis.rendering.Measurement:
        '''Specifies horizontal offset from a point location to the rendered shape.'''
        raise NotImplementedError()
    
    @horizontal_offset.setter
    def horizontal_offset(self, value : aspose.gis.rendering.Measurement) -> None:
        '''Specifies horizontal offset from a point location to the rendered shape.'''
        raise NotImplementedError()
    
    @property
    def vertical_offset(self) -> aspose.gis.rendering.Measurement:
        '''Specifies vertical offset from a polygon location to the rendered shape.'''
        raise NotImplementedError()
    
    @vertical_offset.setter
    def vertical_offset(self, value : aspose.gis.rendering.Measurement) -> None:
        '''Specifies vertical offset from a polygon location to the rendered shape.'''
        raise NotImplementedError()
    

class SimpleLine(VectorSymbolizer):
    '''Simple line symbolizer.'''
    
    def clone(self) -> aspose.gis.rendering.symbolizers.SimpleLine:
        '''Clones this instance.
        
        :returns: A clone of this instance.'''
        raise NotImplementedError()
    
    null : aspose.gis.rendering.symbolizers.NullVectorSymbolizer
    '''The :py:class:`aspose.gis.rendering.symbolizers.NullVectorSymbolizer` draws nothing and effectively skips rendering of a geometry it is applied to.'''
    @property
    def color(self) -> aspose.pydrawing.Color:
        '''Specifies the color and transparency given to the line.'''
        raise NotImplementedError()
    
    @color.setter
    def color(self, value : aspose.pydrawing.Color) -> None:
        '''Specifies the color and transparency given to the line.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> aspose.gis.rendering.Measurement:
        '''Specifies the width of the line.'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : aspose.gis.rendering.Measurement) -> None:
        '''Specifies the width of the line.'''
        raise NotImplementedError()
    
    @property
    def line_join(self) -> aspose.gis.rendering.LineJoin:
        '''Determines how lines are rendered at intersection of line segments.'''
        raise NotImplementedError()
    
    @line_join.setter
    def line_join(self, value : aspose.gis.rendering.LineJoin) -> None:
        '''Determines how lines are rendered at intersection of line segments.'''
        raise NotImplementedError()
    
    @property
    def style(self) -> aspose.gis.rendering.StrokeStyle:
        '''Specifies how the symbol lines should be drawn.'''
        raise NotImplementedError()
    
    @style.setter
    def style(self, value : aspose.gis.rendering.StrokeStyle) -> None:
        '''Specifies how the symbol lines should be drawn.'''
        raise NotImplementedError()
    
    @property
    def dash_pattern(self) -> Iterable[aspose.gis.rendering.Measurement]:
        '''Specifies an array of distances that specifies the lengths of alternating dashes and spaces
        in dashed lines.'''
        raise NotImplementedError()
    
    @dash_pattern.setter
    def dash_pattern(self, value : Iterable[aspose.gis.rendering.Measurement]) -> None:
        '''Specifies an array of distances that specifies the lengths of alternating dashes and spaces
        in dashed lines.'''
        raise NotImplementedError()
    
    @property
    def dash_offset(self) -> aspose.gis.rendering.Measurement:
        '''Specifies the distance from the start of a line to the beginning of a dash pattern.'''
        raise NotImplementedError()
    
    @dash_offset.setter
    def dash_offset(self, value : aspose.gis.rendering.Measurement) -> None:
        '''Specifies the distance from the start of a line to the beginning of a dash pattern.'''
        raise NotImplementedError()
    
    @property
    def cap_style(self) -> aspose.gis.rendering.CapStyle:
        '''Specifies how lines are rendered at their ends.'''
        raise NotImplementedError()
    
    @cap_style.setter
    def cap_style(self, value : aspose.gis.rendering.CapStyle) -> None:
        '''Specifies how lines are rendered at their ends.'''
        raise NotImplementedError()
    
    @property
    def offset(self) -> aspose.gis.rendering.Measurement:
        '''Specifies offset from the original line.
        For positive distance the offset will be at the left side of the input line (relative to the line direction).
        For a negative distance it will be at the right side.'''
        raise NotImplementedError()
    
    @offset.setter
    def offset(self, value : aspose.gis.rendering.Measurement) -> None:
        '''Specifies offset from the original line.
        For positive distance the offset will be at the left side of the input line (relative to the line direction).
        For a negative distance it will be at the right side.'''
        raise NotImplementedError()
    

class SimpleMarker(VectorSymbolizer):
    '''Simple point symbolizer.'''
    
    def clone(self) -> aspose.gis.rendering.symbolizers.SimpleMarker:
        '''Clones this instance.
        
        :returns: A clone of this instance.'''
        raise NotImplementedError()
    
    null : aspose.gis.rendering.symbolizers.NullVectorSymbolizer
    '''The :py:class:`aspose.gis.rendering.symbolizers.NullVectorSymbolizer` draws nothing and effectively skips rendering of a geometry it is applied to.'''
    @property
    def fill_color(self) -> aspose.pydrawing.Color:
        '''Specifies the color and transparency for filling.'''
        raise NotImplementedError()
    
    @fill_color.setter
    def fill_color(self, value : aspose.pydrawing.Color) -> None:
        '''Specifies the color and transparency for filling.'''
        raise NotImplementedError()
    
    @property
    def size(self) -> aspose.gis.rendering.Measurement:
        '''Specifies the size of the marker.'''
        raise NotImplementedError()
    
    @size.setter
    def size(self, value : aspose.gis.rendering.Measurement) -> None:
        '''Specifies the size of the marker.'''
        raise NotImplementedError()
    
    @property
    def stroke_color(self) -> aspose.pydrawing.Color:
        '''Specifies the color and transparency given to the line.'''
        raise NotImplementedError()
    
    @stroke_color.setter
    def stroke_color(self, value : aspose.pydrawing.Color) -> None:
        '''Specifies the color and transparency given to the line.'''
        raise NotImplementedError()
    
    @property
    def stroke_width(self) -> aspose.gis.rendering.Measurement:
        '''Specifies the width of the line.'''
        raise NotImplementedError()
    
    @stroke_width.setter
    def stroke_width(self, value : aspose.gis.rendering.Measurement) -> None:
        '''Specifies the width of the line.'''
        raise NotImplementedError()
    
    @property
    def stroke_line_join(self) -> aspose.gis.rendering.LineJoin:
        '''Determines how lines are rendered at intersection of line segments.'''
        raise NotImplementedError()
    
    @stroke_line_join.setter
    def stroke_line_join(self, value : aspose.gis.rendering.LineJoin) -> None:
        '''Determines how lines are rendered at intersection of line segments.'''
        raise NotImplementedError()
    
    @property
    def stroke_style(self) -> aspose.gis.rendering.StrokeStyle:
        '''Specifies how the symbol lines should be drawn.'''
        raise NotImplementedError()
    
    @stroke_style.setter
    def stroke_style(self, value : aspose.gis.rendering.StrokeStyle) -> None:
        '''Specifies how the symbol lines should be drawn.'''
        raise NotImplementedError()
    
    @property
    def stroke_dash_pattern(self) -> Iterable[aspose.gis.rendering.Measurement]:
        '''Specifies an array of distances that specifies the lengths of alternating dashes and spaces
        in dashed lines.'''
        raise NotImplementedError()
    
    @stroke_dash_pattern.setter
    def stroke_dash_pattern(self, value : Iterable[aspose.gis.rendering.Measurement]) -> None:
        '''Specifies an array of distances that specifies the lengths of alternating dashes and spaces
        in dashed lines.'''
        raise NotImplementedError()
    
    @property
    def stroke_dash_offset(self) -> aspose.gis.rendering.Measurement:
        '''Specifies the distance from the start of a line to the beginning of a dash pattern.'''
        raise NotImplementedError()
    
    @stroke_dash_offset.setter
    def stroke_dash_offset(self, value : aspose.gis.rendering.Measurement) -> None:
        '''Specifies the distance from the start of a line to the beginning of a dash pattern.'''
        raise NotImplementedError()
    
    @property
    def shape_type(self) -> aspose.gis.rendering.symbolizers.MarkerShapeType:
        '''Specifies the shape of the marker.'''
        raise NotImplementedError()
    
    @shape_type.setter
    def shape_type(self, value : aspose.gis.rendering.symbolizers.MarkerShapeType) -> None:
        '''Specifies the shape of the marker.'''
        raise NotImplementedError()
    
    @property
    def horizontal_anchor_point(self) -> aspose.gis.rendering.symbolizers.HorizontalAnchor:
        '''Specifies which side of a marker shape will be aligned horizontally with the point location.'''
        raise NotImplementedError()
    
    @horizontal_anchor_point.setter
    def horizontal_anchor_point(self, value : aspose.gis.rendering.symbolizers.HorizontalAnchor) -> None:
        '''Specifies which side of a marker shape will be aligned horizontally with the point location.'''
        raise NotImplementedError()
    
    @property
    def vertical_anchor_point(self) -> aspose.gis.rendering.symbolizers.VerticalAnchor:
        '''Specifies which side of a marker shape will be aligned vertically with the point location.'''
        raise NotImplementedError()
    
    @vertical_anchor_point.setter
    def vertical_anchor_point(self, value : aspose.gis.rendering.symbolizers.VerticalAnchor) -> None:
        '''Specifies which side of a marker shape will be aligned vertically with the point location.'''
        raise NotImplementedError()
    
    @property
    def horizontal_offset(self) -> aspose.gis.rendering.Measurement:
        '''Specifies horizontal offset from a point location to the shape anchor point.'''
        raise NotImplementedError()
    
    @horizontal_offset.setter
    def horizontal_offset(self, value : aspose.gis.rendering.Measurement) -> None:
        '''Specifies horizontal offset from a point location to the shape anchor point.'''
        raise NotImplementedError()
    
    @property
    def vertical_offset(self) -> aspose.gis.rendering.Measurement:
        '''Specifies vertical offset from a point location to the shape anchor point.'''
        raise NotImplementedError()
    
    @vertical_offset.setter
    def vertical_offset(self, value : aspose.gis.rendering.Measurement) -> None:
        '''Specifies vertical offset from a point location to the shape anchor point.'''
        raise NotImplementedError()
    
    @property
    def rotation(self) -> float:
        '''Specifies the rotation of the symbol about its center point, in decimal degrees.
        Positive values indicate rotation in the clockwise direction, negative values indicate counter-clockwise rotation.'''
        raise NotImplementedError()
    
    @rotation.setter
    def rotation(self, value : float) -> None:
        '''Specifies the rotation of the symbol about its center point, in decimal degrees.
        Positive values indicate rotation in the clockwise direction, negative values indicate counter-clockwise rotation.'''
        raise NotImplementedError()
    

class VectorSymbolizer:
    '''The abstract root class for the symbolizers that render vector features.'''
    
    null : aspose.gis.rendering.symbolizers.NullVectorSymbolizer
    '''The :py:class:`aspose.gis.rendering.symbolizers.NullVectorSymbolizer` draws nothing and effectively skips rendering of a geometry it is applied to.'''

class HorizontalAnchor:
    '''Specifies side to be aligned horizontally.'''
    
    CENTER : HorizontalAnchor
    '''Specifies that centers will be aligned.'''
    LEFT : HorizontalAnchor
    '''Specifies that left sides will be aligned.'''
    RIGHT : HorizontalAnchor
    '''Specifies that right sides will be aligned.'''

class MarkerShapeType:
    '''A shape type of the marker.'''
    
    CIRCLE : MarkerShapeType
    '''Circle shape.'''
    TRIANGLE : MarkerShapeType
    '''Triangle shape.'''
    SQUARE : MarkerShapeType
    '''Square shape.'''
    STAR : MarkerShapeType
    '''Star shape.'''
    CROSS : MarkerShapeType
    '''Cross shape.'''
    X : MarkerShapeType
    '''\'X\' letter shape.'''

class RenderingOrder:
    '''Determines the rendering order.'''
    
    BY_FEATURES : RenderingOrder
    '''Render feature with all symbolizers, then proceed to the next feature.'''
    BY_LAYERS : RenderingOrder
    '''Render all features with a symbolizer, then proceed with drawing features to the next symbolizer.'''

class VerticalAnchor:
    '''Specifies side to be aligned vertically.'''
    
    CENTER : VerticalAnchor
    '''Specifies that centers will be aligned.'''
    TOP : VerticalAnchor
    '''Specifies that top sides will be aligned.'''
    BOTTOM : VerticalAnchor
    '''Specifies that bottom sides will be aligned'''

