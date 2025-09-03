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

class PaintEngine:
    
    def close(self) -> None:
        raise NotImplementedError()
    
    def start_new_layer(self, new_options : aspose.gis.painting.PaintLayerOptions) -> None:
        raise NotImplementedError()
    
    def update_state(self, state : aspose.gis.painting.PaintEngineState) -> None:
        raise NotImplementedError()
    
    def draw_ellipse(self, center : aspose.gis.common.Coordinate, rx : float, ry : float) -> None:
        raise NotImplementedError()
    
    def draw_shape(self, shape : aspose.gis.painting.PolylinesShape) -> None:
        raise NotImplementedError()
    
    def draw_characters(self, path : List[aspose.gis.painting.PlacedCharacter]) -> None:
        raise NotImplementedError()
    
    def draw_text(self, bottom_left : aspose.gis.common.Coordinate, text : str) -> None:
        raise NotImplementedError()
    
    def draw_image(self, stream : aspose.gis.common.AbstractPathInternal, width : float, height : float, opacity : float) -> None:
        raise NotImplementedError()
    
    def measure_text(self, text : str, font : Any) -> aspose.gis.common.Size:
        raise NotImplementedError()
    
    def measure_text_characters(self, text : str, font : Any) -> List[aspose.gis.common.Size]:
        raise NotImplementedError()
    
    def draw_rectangle(self, rectangle : aspose.gis.common.Rectangle) -> None:
        raise NotImplementedError()
    
    def draw_polyline(self, polyline : Iterable[aspose.gis.common.Coordinate]) -> None:
        raise NotImplementedError()
    
    @property
    def rounded_width(self) -> float:
        raise NotImplementedError()
    
    @property
    def rounded_height(self) -> float:
        raise NotImplementedError()
    

class PaintEngineOptions:
    
    def clone(self) -> aspose.gis.painting.PaintEngineOptions:
        raise NotImplementedError()
    
    @property
    def width(self) -> int:
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def resolution(self) -> int:
        raise NotImplementedError()
    
    @resolution.setter
    def resolution(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def background_color(self) -> aspose.pydrawing.Color:
        raise NotImplementedError()
    
    @background_color.setter
    def background_color(self, value : aspose.pydrawing.Color) -> None:
        raise NotImplementedError()
    

class PaintEngineState:
    
    @overload
    def rotate(self, degrees : float) -> None:
        raise NotImplementedError()
    
    @overload
    def rotate(self, cos : float, sin : float) -> None:
        raise NotImplementedError()
    
    def translate(self, x : float, y : float) -> None:
        raise NotImplementedError()
    
    def scale(self, x : float, y : float) -> None:
        raise NotImplementedError()
    
    @property
    def pen(self) -> aspose.gis.painting.PainterPen:
        raise NotImplementedError()
    
    @pen.setter
    def pen(self, value : aspose.gis.painting.PainterPen) -> None:
        raise NotImplementedError()
    
    @property
    def brush(self) -> aspose.gis.painting.PainterBrush:
        raise NotImplementedError()
    
    @brush.setter
    def brush(self, value : aspose.gis.painting.PainterBrush) -> None:
        raise NotImplementedError()
    
    @property
    def font(self) -> Any:
        raise NotImplementedError()
    
    @font.setter
    def font(self, value : Any) -> None:
        raise NotImplementedError()
    
    @property
    def transformation(self) -> aspose.gis.common.MatrixTransformation:
        raise NotImplementedError()
    
    @transformation.setter
    def transformation(self, value : aspose.gis.common.MatrixTransformation) -> None:
        raise NotImplementedError()
    
    @property
    def is_dirty(self) -> bool:
        raise NotImplementedError()
    
    @property
    def is_pen_dirty(self) -> bool:
        raise NotImplementedError()
    
    @property
    def is_brush_dirty(self) -> bool:
        raise NotImplementedError()
    
    @property
    def is_font_dirty(self) -> bool:
        raise NotImplementedError()
    
    @property
    def is_transfromation_dirty(self) -> bool:
        raise NotImplementedError()
    

class PaintEngines:
    
    @staticmethod
    def g_svg(path : aspose.gis.common.AbstractPathInternal, options : aspose.gis.painting.SvgGeometryOptions) -> aspose.gis.painting.PaintEngine:
        raise NotImplementedError()
    
    @staticmethod
    def svg(path : aspose.gis.common.AbstractPathInternal, options : aspose.gis.painting.SvgOptions) -> aspose.gis.painting.PaintEngine:
        raise NotImplementedError()
    
    @staticmethod
    def png(path : aspose.gis.common.AbstractPathInternal, options : aspose.gis.painting.PaintEngineOptions) -> aspose.gis.painting.PaintEngine:
        raise NotImplementedError()
    
    @staticmethod
    def bmp(path : aspose.gis.common.AbstractPathInternal, options : aspose.gis.painting.PaintEngineOptions) -> aspose.gis.painting.PaintEngine:
        raise NotImplementedError()
    
    @staticmethod
    def jpeg(path : aspose.gis.common.AbstractPathInternal, options : aspose.gis.painting.PaintEngineOptions) -> aspose.gis.painting.PaintEngine:
        raise NotImplementedError()
    

class PaintLayerOptions:
    
    def with_opacity(self, new_opacity : float) -> aspose.gis.painting.PaintLayerOptions:
        raise NotImplementedError()
    
    def with_scale(self, new_scale_x : float, new_scale_y : float) -> aspose.gis.painting.PaintLayerOptions:
        raise NotImplementedError()
    
    def allow_crisp_edges(self) -> aspose.gis.painting.PaintLayerOptions:
        raise NotImplementedError()
    
    def clone(self) -> aspose.gis.painting.PaintLayerOptions:
        raise NotImplementedError()
    
    def nearly_equal(self, other : aspose.gis.painting.PaintLayerOptions) -> bool:
        raise NotImplementedError()
    
    by_default : aspose.gis.painting.PaintLayerOptions
    @property
    def opacity(self) -> float:
        raise NotImplementedError()
    
    @property
    def scale_x(self) -> float:
        raise NotImplementedError()
    
    @property
    def scale_y(self) -> float:
        raise NotImplementedError()
    
    @property
    def crisp_edges(self) -> bool:
        raise NotImplementedError()
    

class Painter:
    
    @overload
    def start_new_layer(self, options : aspose.gis.painting.PaintLayerOptions) -> None:
        raise NotImplementedError()
    
    @overload
    def start_new_layer(self, opacity : float) -> None:
        raise NotImplementedError()
    
    @overload
    def translate(self, c : aspose.gis.common.Coordinate) -> None:
        raise NotImplementedError()
    
    @overload
    def translate(self, x : float, y : float) -> None:
        raise NotImplementedError()
    
    @overload
    def rotate(self, degrees : float) -> None:
        raise NotImplementedError()
    
    @overload
    def rotate(self, cos : float, sin : float) -> None:
        raise NotImplementedError()
    
    def scale(self, zoom_x : float, zoom_y : float) -> None:
        raise NotImplementedError()
    
    def draw_ellipse(self, center : aspose.gis.common.Coordinate, rx : float, ry : float) -> None:
        raise NotImplementedError()
    
    def draw_line(self, c0 : aspose.gis.common.Coordinate, c1 : aspose.gis.common.Coordinate) -> None:
        raise NotImplementedError()
    
    def draw_polyline(self, polyline : Iterable[aspose.gis.common.Coordinate]) -> None:
        raise NotImplementedError()
    
    def draw_rectangle(self, rectangle : aspose.gis.common.Rectangle) -> None:
        raise NotImplementedError()
    
    def draw_shape(self, shape : aspose.gis.painting.PolylinesShape) -> None:
        raise NotImplementedError()
    
    def draw_text(self, bottom_left : aspose.gis.common.Coordinate, text : str) -> None:
        raise NotImplementedError()
    
    def draw_characters(self, path : List[aspose.gis.painting.PlacedCharacter]) -> None:
        raise NotImplementedError()
    
    def draw_image(self, image_path : aspose.gis.common.AbstractPathInternal, width : float, height : float, opacity : float) -> None:
        raise NotImplementedError()
    
    def measure_text(self, text : str, font : Any) -> aspose.gis.common.Size:
        raise NotImplementedError()
    
    def measure_text_characters(self, text : str, font : Any) -> List[aspose.gis.common.Size]:
        raise NotImplementedError()
    
    @property
    def pen(self) -> aspose.gis.painting.PainterPen:
        raise NotImplementedError()
    
    @pen.setter
    def pen(self, value : aspose.gis.painting.PainterPen) -> None:
        raise NotImplementedError()
    
    @property
    def brush(self) -> aspose.gis.painting.PainterBrush:
        raise NotImplementedError()
    
    @brush.setter
    def brush(self, value : aspose.gis.painting.PainterBrush) -> None:
        raise NotImplementedError()
    
    @property
    def font(self) -> Any:
        raise NotImplementedError()
    
    @font.setter
    def font(self, value : Any) -> None:
        raise NotImplementedError()
    
    @property
    def tranformation(self) -> aspose.gis.common.MatrixTransformation:
        raise NotImplementedError()
    
    @tranformation.setter
    def tranformation(self, value : aspose.gis.common.MatrixTransformation) -> None:
        raise NotImplementedError()
    
    @property
    def rounded_width(self) -> float:
        raise NotImplementedError()
    
    @property
    def rounded_height(self) -> float:
        raise NotImplementedError()
    

class PainterBrush:
    
    def get_hash_code(self) -> int:
        raise NotImplementedError()
    
    def equals(self, other : aspose.gis.painting.PainterBrush) -> bool:
        raise NotImplementedError()
    

class PainterPen:
    
    def equals(self, other : aspose.gis.painting.PainterPen) -> bool:
        raise NotImplementedError()
    
    no_pen : aspose.gis.painting.PainterPen
    @property
    def color(self) -> aspose.pydrawing.Color:
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        raise NotImplementedError()
    
    @property
    def style(self) -> aspose.gis.painting.PenStyle:
        raise NotImplementedError()
    
    @property
    def line_join(self) -> aspose.gis.painting.PenLineJoin:
        raise NotImplementedError()
    
    @property
    def cap_style(self) -> aspose.gis.painting.PenCapStyle:
        raise NotImplementedError()
    
    @property
    def dash_pattern(self) -> Sequence[float]:
        raise NotImplementedError()
    
    @property
    def dash_offset(self) -> float:
        raise NotImplementedError()
    

class PainterPenOptions:
    
    @property
    def color(self) -> aspose.pydrawing.Color:
        raise NotImplementedError()
    
    @color.setter
    def color(self, value : aspose.pydrawing.Color) -> None:
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def style(self) -> aspose.gis.painting.PenStyle:
        raise NotImplementedError()
    
    @style.setter
    def style(self, value : aspose.gis.painting.PenStyle) -> None:
        raise NotImplementedError()
    
    @property
    def line_join(self) -> aspose.gis.painting.PenLineJoin:
        raise NotImplementedError()
    
    @line_join.setter
    def line_join(self, value : aspose.gis.painting.PenLineJoin) -> None:
        raise NotImplementedError()
    
    @property
    def cap_style(self) -> aspose.gis.painting.PenCapStyle:
        raise NotImplementedError()
    
    @cap_style.setter
    def cap_style(self, value : aspose.gis.painting.PenCapStyle) -> None:
        raise NotImplementedError()
    
    @property
    def dash_pattern(self) -> Iterable[float]:
        raise NotImplementedError()
    
    @dash_pattern.setter
    def dash_pattern(self, value : Iterable[float]) -> None:
        raise NotImplementedError()
    
    @property
    def dash_offset(self) -> Optional[float]:
        raise NotImplementedError()
    
    @dash_offset.setter
    def dash_offset(self, value : Optional[float]) -> None:
        raise NotImplementedError()
    

class PaintingExtensions:
    
    @staticmethod
    def customize_background_to_white(options : aspose.gis.painting.PaintEngineOptions) -> aspose.gis.painting.PaintEngineOptions:
        raise NotImplementedError()
    

class PlacedCharacter:
    
    @property
    def symbol(self) -> str:
        raise NotImplementedError()
    
    @symbol.setter
    def symbol(self, value : str) -> None:
        raise NotImplementedError()
    
    @property
    def bottom_left(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @bottom_left.setter
    def bottom_left(self, value : aspose.gis.common.Coordinate) -> None:
        raise NotImplementedError()
    
    @property
    def rotate(self) -> float:
        raise NotImplementedError()
    
    @rotate.setter
    def rotate(self, value : float) -> None:
        raise NotImplementedError()
    

class PolylinesShape:
    
    def add_rectangle(self, rectangle : aspose.gis.common.Rectangle) -> None:
        raise NotImplementedError()
    
    def add_polyline(self, coordinates : Iterable[aspose.gis.common.Coordinate]) -> None:
        raise NotImplementedError()
    
    @property
    def polylines(self) -> Sequence[Sequence[aspose.gis.common.Coordinate]]:
        raise NotImplementedError()
    

class SolidPainterBrush(PainterBrush):
    
    def get_hash_code(self) -> int:
        raise NotImplementedError()
    
    def equals(self, base_other : aspose.gis.painting.PainterBrush) -> bool:
        raise NotImplementedError()
    
    no_brush : aspose.gis.painting.SolidPainterBrush
    @property
    def color(self) -> aspose.pydrawing.Color:
        raise NotImplementedError()
    
    @property
    def style(self) -> aspose.gis.painting.BrushStyle:
        raise NotImplementedError()
    

class StrokeTemplates:
    
    @staticmethod
    def is_equal_pattern(multipliers : List[float], pattern : List[float]) -> bool:
        raise NotImplementedError()
    
    DOT_MULTIPLIERS : List[float]
    DASH_MULTIPLIERS : List[float]
    DASH_DOT_MULTIPLIERS : List[float]
    DASH_DOT_DOT_MULTIPLIERS : List[float]

class SvgGeometryOptions:
    
    @property
    def background_color(self) -> aspose.pydrawing.Color:
        raise NotImplementedError()
    
    @background_color.setter
    def background_color(self, value : aspose.pydrawing.Color) -> None:
        raise NotImplementedError()
    

class SvgOptions:
    
    @property
    def width(self) -> str:
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : str) -> None:
        raise NotImplementedError()
    
    @property
    def height(self) -> str:
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : str) -> None:
        raise NotImplementedError()
    
    @property
    def view_box(self) -> Optional[aspose.gis.common.Rectangle]:
        raise NotImplementedError()
    
    @view_box.setter
    def view_box(self, value : Optional[aspose.gis.common.Rectangle]) -> None:
        raise NotImplementedError()
    
    @property
    def background_color(self) -> aspose.pydrawing.Color:
        raise NotImplementedError()
    
    @background_color.setter
    def background_color(self, value : aspose.pydrawing.Color) -> None:
        raise NotImplementedError()
    
    @property
    def pixel_height(self) -> float:
        raise NotImplementedError()
    
    @pixel_height.setter
    def pixel_height(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def pixel_width(self) -> float:
        raise NotImplementedError()
    
    @pixel_width.setter
    def pixel_width(self, value : float) -> None:
        raise NotImplementedError()
    

class SvgTextureBrush(PainterBrush):
    
    def get_hash_code(self) -> int:
        raise NotImplementedError()
    
    def equals(self, base_other : aspose.gis.painting.PainterBrush) -> bool:
        raise NotImplementedError()
    
    @property
    def url_pattern_id(self) -> str:
        raise NotImplementedError()
    

class SystemDrawingAdapter:
    
    @staticmethod
    def convert_brush(brush : aspose.gis.painting.SolidPainterBrush) -> Any:
        raise NotImplementedError()
    
    @staticmethod
    def convert_pen(pen : aspose.gis.painting.PainterPen) -> Any:
        raise NotImplementedError()
    
    @staticmethod
    def convert_shape(shape : aspose.gis.painting.PolylinesShape) -> Any:
        raise NotImplementedError()
    
    @staticmethod
    def convert_transformation(transformation : aspose.gis.common.MatrixTransformation) -> Any:
        raise NotImplementedError()
    
    @staticmethod
    def convert_coordinate(coordinate : aspose.gis.common.Coordinate) -> Any:
        raise NotImplementedError()
    
    @staticmethod
    def get_cell_ascent(font : Any) -> float:
        raise NotImplementedError()
    
    @staticmethod
    def get_cell_descent(font : Any) -> float:
        raise NotImplementedError()
    
    @staticmethod
    def font_design_units_to_pixels(font : Any, value_in_design_units : int) -> float:
        raise NotImplementedError()
    
    @staticmethod
    def measure_text(graphics : Any, text : str, font : Any) -> aspose.gis.common.Size:
        raise NotImplementedError()
    
    string_format : Any

class SystemDrawingPaintEngine(PaintEngine):
    
    def close(self) -> None:
        raise NotImplementedError()
    
    def start_new_layer(self, new_options : aspose.gis.painting.PaintLayerOptions) -> None:
        raise NotImplementedError()
    
    def update_state(self, state : aspose.gis.painting.PaintEngineState) -> None:
        raise NotImplementedError()
    
    def draw_ellipse(self, center : aspose.gis.common.Coordinate, rx : float, ry : float) -> None:
        raise NotImplementedError()
    
    def draw_shape(self, shape : aspose.gis.painting.PolylinesShape) -> None:
        raise NotImplementedError()
    
    def draw_characters(self, text_path : List[aspose.gis.painting.PlacedCharacter]) -> None:
        raise NotImplementedError()
    
    def draw_text(self, bottom_left : aspose.gis.common.Coordinate, text : str) -> None:
        raise NotImplementedError()
    
    def draw_image(self, image_path : aspose.gis.common.AbstractPathInternal, width : float, height : float, opacity : float) -> None:
        raise NotImplementedError()
    
    def measure_text(self, text : str, text_font : Any) -> aspose.gis.common.Size:
        raise NotImplementedError()
    
    def measure_text_characters(self, text : str, text_font : Any) -> List[aspose.gis.common.Size]:
        raise NotImplementedError()
    
    def draw_rectangle(self, rectangle : aspose.gis.common.Rectangle) -> None:
        raise NotImplementedError()
    
    def draw_polyline(self, polyline : Iterable[aspose.gis.common.Coordinate]) -> None:
        raise NotImplementedError()
    
    @property
    def rounded_width(self) -> float:
        raise NotImplementedError()
    
    @property
    def rounded_height(self) -> float:
        raise NotImplementedError()
    

class SystemDrawingTextureBrush(PainterBrush):
    
    def get_hash_code(self) -> int:
        raise NotImplementedError()
    
    def equals(self, base_other : aspose.gis.painting.PainterBrush) -> bool:
        raise NotImplementedError()
    
    @property
    def brush(self) -> Any:
        raise NotImplementedError()
    

class BrushStyle:
    
    SOLID : BrushStyle
    NONE : BrushStyle
    HORIZONTAL_HATCH : BrushStyle
    VERTICAL_HATCH : BrushStyle
    CROSS_HATCH : BrushStyle
    FORWARD_DIAGONAL_HATCH : BrushStyle
    BACKWARD_DIAGONAL_HATCH : BrushStyle
    DIAGONAL_CROSS_HATCH : BrushStyle

class PenCapStyle:
    
    BUTT : PenCapStyle
    ROUND : PenCapStyle
    SQUARE : PenCapStyle

class PenLineJoin:
    
    MITER : PenLineJoin
    ROUND : PenLineJoin
    BEVEL : PenLineJoin

class PenStyle:
    
    SOLID : PenStyle
    NONE : PenStyle
    DASH : PenStyle
    DOT : PenStyle
    DASH_DOT : PenStyle
    DASH_DOT_DOT : PenStyle
    CUSTOM : PenStyle

