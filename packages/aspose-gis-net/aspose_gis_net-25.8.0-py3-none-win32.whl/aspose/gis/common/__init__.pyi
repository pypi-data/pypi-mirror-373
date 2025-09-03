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

class AbstractPathInternal:
    
    def is_file(self) -> bool:
        raise NotImplementedError()
    
    def delete(self) -> None:
        raise NotImplementedError()
    
    def open(self, access : System.IO.FileAccess) -> io.RawIOBase:
        raise NotImplementedError()
    
    def list_directory(self) -> Iterable[aspose.gis.common.AbstractPathInternal]:
        raise NotImplementedError()
    
    def combine(self, path : str) -> aspose.gis.common.AbstractPathInternal:
        raise NotImplementedError()
    
    def with_extension(self, new_extension : str) -> aspose.gis.common.AbstractPathInternal:
        raise NotImplementedError()
    
    def with_location(self, path : str) -> aspose.gis.common.AbstractPathInternal:
        raise NotImplementedError()
    
    @property
    def location(self) -> str:
        raise NotImplementedError()
    
    @property
    def separator(self) -> str:
        raise NotImplementedError()
    

class AbstractPathInternalExtensions:
    
    @staticmethod
    def create_or_open(path : aspose.gis.common.AbstractPathInternal, created : List[Boolean]) -> io.RawIOBase:
        raise NotImplementedError()
    

class BezierCurve:
    
    def linearize(self, coordinates : List[aspose.gis.common.Coordinate], step_size_in_degree : float) -> None:
        raise NotImplementedError()
    
    def coordinate_at(self, t : float) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @property
    def c0(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @property
    def c1(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @property
    def c2(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @property
    def c3(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    

class BinaryConverter:
    
    @overload
    def get_bytes(self, value : bool) -> List[int]:
        raise NotImplementedError()
    
    @overload
    def get_bytes(self, value : int) -> List[int]:
        raise NotImplementedError()
    
    @overload
    def get_bytes(self, value : int) -> List[int]:
        raise NotImplementedError()
    
    @overload
    def get_bytes(self, value : int) -> List[int]:
        raise NotImplementedError()
    
    @overload
    def get_bytes(self, value : str) -> List[int]:
        raise NotImplementedError()
    
    @overload
    def get_bytes(self, value : int) -> List[int]:
        raise NotImplementedError()
    
    @overload
    def get_bytes(self, value : int) -> List[int]:
        raise NotImplementedError()
    
    @overload
    def get_bytes(self, value : int) -> List[int]:
        raise NotImplementedError()
    
    @overload
    def get_bytes(self, value : float) -> List[int]:
        raise NotImplementedError()
    
    @overload
    def get_bytes(self, value : float) -> List[int]:
        raise NotImplementedError()
    
    def to_s_byte(self, value : int) -> sbyte:
        raise NotImplementedError()
    
    def to_boolean(self, value : List[int], start_index : int) -> bool:
        raise NotImplementedError()
    
    def to_int16(self, value : List[int], start_index : int) -> int:
        raise NotImplementedError()
    
    def to_int32(self, value : List[int], start_index : int) -> int:
        raise NotImplementedError()
    
    def to_int64(self, value : List[int], start_index : int) -> int:
        raise NotImplementedError()
    
    def to_char(self, value : List[int], start_index : int) -> str:
        raise NotImplementedError()
    
    def to_double(self, value : List[int], start_index : int) -> float:
        raise NotImplementedError()
    
    def to_single(self, value : List[int], start_index : int) -> float:
        raise NotImplementedError()
    
    def to_u_int16(self, value : List[int], start_index : int) -> int:
        raise NotImplementedError()
    
    def to_u_int32(self, value : List[int], start_index : int) -> int:
        raise NotImplementedError()
    
    def to_u_int64(self, value : List[int], start_index : int) -> int:
        raise NotImplementedError()
    
    little_endian : aspose.gis.common.BinaryConverter
    big_endian : aspose.gis.common.BinaryConverter

class BoundingBox:
    
    def clone(self) -> aspose.gis.common.BoundingBox:
        raise NotImplementedError()
    
    def grow(self, other : aspose.gis.common.BoundingBox, has_z : bool, has_m : bool) -> None:
        raise NotImplementedError()
    
    def grow_x(self, x : float) -> None:
        raise NotImplementedError()
    
    def grow_y(self, y : float) -> None:
        raise NotImplementedError()
    
    def grow_z(self, z : float) -> None:
        raise NotImplementedError()
    
    def grow_m(self, m : float) -> None:
        raise NotImplementedError()
    
    def has_values(self) -> bool:
        raise NotImplementedError()
    
    def clear(self) -> None:
        raise NotImplementedError()
    
    @property
    def x_min(self) -> float:
        raise NotImplementedError()
    
    @x_min.setter
    def x_min(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def x_max(self) -> float:
        raise NotImplementedError()
    
    @x_max.setter
    def x_max(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def y_min(self) -> float:
        raise NotImplementedError()
    
    @y_min.setter
    def y_min(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def y_max(self) -> float:
        raise NotImplementedError()
    
    @y_max.setter
    def y_max(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def z_min(self) -> float:
        raise NotImplementedError()
    
    @z_min.setter
    def z_min(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def z_max(self) -> float:
        raise NotImplementedError()
    
    @z_max.setter
    def z_max(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def m_min(self) -> float:
        raise NotImplementedError()
    
    @m_min.setter
    def m_min(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def m_max(self) -> float:
        raise NotImplementedError()
    
    @m_max.setter
    def m_max(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def bounding_rectangle(self) -> aspose.gis.common.BoundingRectangle:
        raise NotImplementedError()
    
    @property
    def x_center(self) -> float:
        raise NotImplementedError()
    
    @property
    def y_center(self) -> float:
        raise NotImplementedError()
    
    @property
    def z_center(self) -> float:
        raise NotImplementedError()
    
    @property
    def m_center(self) -> float:
        raise NotImplementedError()
    
    @property
    def xy_center(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @property
    def has_z(self) -> bool:
        raise NotImplementedError()
    
    @property
    def has_m(self) -> bool:
        raise NotImplementedError()
    
    @property
    def x_length(self) -> float:
        raise NotImplementedError()
    
    @property
    def y_length(self) -> float:
        raise NotImplementedError()
    
    @property
    def z_length(self) -> float:
        raise NotImplementedError()
    
    @property
    def m_length(self) -> float:
        raise NotImplementedError()
    

class BoundingRectangle:
    
    @overload
    def contains(self, other : aspose.gis.common.BoundingRectangle) -> bool:
        raise NotImplementedError()
    
    @overload
    def contains(self, x : float, y : float) -> bool:
        raise NotImplementedError()
    
    @overload
    def contains(self, c : aspose.gis.common.Coordinate) -> bool:
        raise NotImplementedError()
    
    @overload
    def grow(self, other : aspose.gis.common.BoundingRectangle) -> None:
        raise NotImplementedError()
    
    @overload
    def grow(self, x : float, y : float) -> None:
        raise NotImplementedError()
    
    @overload
    def grow(self, c : aspose.gis.common.Coordinate) -> None:
        raise NotImplementedError()
    
    @overload
    def distance(self, other : aspose.gis.common.BoundingRectangle) -> float:
        raise NotImplementedError()
    
    @overload
    def distance(self, x : float, y : float) -> float:
        raise NotImplementedError()
    
    @overload
    def distance(self, coordinate : aspose.gis.common.Coordinate) -> float:
        raise NotImplementedError()
    
    @overload
    def squared_distance(self, other : aspose.gis.common.BoundingRectangle) -> float:
        raise NotImplementedError()
    
    @overload
    def squared_distance(self, x : float, y : float) -> float:
        raise NotImplementedError()
    
    @overload
    def squared_distance(self, c : aspose.gis.common.Coordinate) -> float:
        raise NotImplementedError()
    
    def intersects(self, other : aspose.gis.common.BoundingRectangle) -> bool:
        raise NotImplementedError()
    
    def contains_x(self, x : float) -> bool:
        raise NotImplementedError()
    
    def contains_y(self, y : float) -> bool:
        raise NotImplementedError()
    
    def intersection(self, other : aspose.gis.common.BoundingRectangle) -> aspose.gis.common.BoundingRectangle:
        raise NotImplementedError()
    
    def grow_x(self, x : float) -> None:
        raise NotImplementedError()
    
    def grow_y(self, y : float) -> None:
        raise NotImplementedError()
    
    def clone(self) -> aspose.gis.common.BoundingRectangle:
        raise NotImplementedError()
    
    def equals(self, other : aspose.gis.common.BoundingRectangle) -> bool:
        raise NotImplementedError()
    
    @property
    def has_values(self) -> bool:
        raise NotImplementedError()
    
    @property
    def x_min(self) -> float:
        raise NotImplementedError()
    
    @x_min.setter
    def x_min(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def y_min(self) -> float:
        raise NotImplementedError()
    
    @y_min.setter
    def y_min(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def x_max(self) -> float:
        raise NotImplementedError()
    
    @x_max.setter
    def x_max(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def y_max(self) -> float:
        raise NotImplementedError()
    
    @y_max.setter
    def y_max(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        raise NotImplementedError()
    
    @property
    def center(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @property
    def area(self) -> float:
        raise NotImplementedError()
    
    @property
    def min_coordinate(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @property
    def max_coordinate(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    

class CharsetResolver:
    
    @staticmethod
    def get_encoding(charset_name : str) -> str:
        raise NotImplementedError()
    

class CircularArc:
    
    @overload
    @staticmethod
    def from_center(center : aspose.gis.common.Coordinate, start : aspose.gis.common.Coordinate, end : aspose.gis.common.Coordinate, clockwise : bool) -> aspose.gis.common.CircularArc:
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def from_center(center : aspose.gis.common.Coordinate, radius : float, start_angle_rad : float, end_angle_rad : float, clockwise : bool) -> aspose.gis.common.CircularArc:
        raise NotImplementedError()
    
    @overload
    def linearize(self, result : List[aspose.gis.common.Coordinate], tolerance : float, add_endpoints : bool) -> None:
        raise NotImplementedError()
    
    @overload
    def linearize(self, result : List[aspose.gis.common.Coordinate], tolerance : float, add_endpoints : bool, index_of_mid : List[int]) -> None:
        raise NotImplementedError()
    
    def get_coordinate(self, angle : float) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    def get_normalized_angles(self, start_angle : List[Double], mid_angle : List[Double], end_angle : List[Double]) -> None:
        raise NotImplementedError()
    
    def grow_bounding_rectangle(self, brect : aspose.gis.common.BoundingRectangle) -> None:
        raise NotImplementedError()
    
    def equal(self, other : aspose.gis.common.CircularArc) -> bool:
        raise NotImplementedError()
    
    def equals(self, other : aspose.gis.common.CircularArc) -> bool:
        raise NotImplementedError()
    
    @property
    def start(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @property
    def mid(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @property
    def end(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @property
    def is_circle(self) -> bool:
        raise NotImplementedError()
    
    @property
    def is_line(self) -> bool:
        raise NotImplementedError()
    
    @property
    def is_point(self) -> bool:
        raise NotImplementedError()
    
    @property
    def radius(self) -> float:
        raise NotImplementedError()
    
    @property
    def circle_center(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @property
    def length(self) -> float:
        raise NotImplementedError()
    
    @property
    def is_clockwise(self) -> bool:
        raise NotImplementedError()
    
    @property
    def is_minor(self) -> bool:
        raise NotImplementedError()
    

class Coordinate:
    
    def equals(self, other : aspose.gis.common.Coordinate) -> bool:
        raise NotImplementedError()
    
    def compare_to(self, other : aspose.gis.common.Coordinate) -> int:
        raise NotImplementedError()
    
    def distance_to(self, other : aspose.gis.common.Coordinate) -> float:
        raise NotImplementedError()
    
    def nearly_equal(self, other : aspose.gis.common.Coordinate) -> bool:
        raise NotImplementedError()
    
    min_value : aspose.gis.common.Coordinate
    max_value : aspose.gis.common.Coordinate
    @property
    def x(self) -> float:
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        raise NotImplementedError()
    

class Ellipse:
    
    def get_angle(self, coordinate : aspose.gis.common.Coordinate) -> float:
        raise NotImplementedError()
    
    def get_coordinate(self, parametric_angle : float) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    def get_arc(self, start : aspose.gis.common.Coordinate, end : aspose.gis.common.Coordinate, clockwise : bool) -> aspose.gis.common.EllipticArc:
        raise NotImplementedError()
    
    def linearize(self, coordinates : List[aspose.gis.common.Coordinate], step_size_in_degrees : float) -> None:
        raise NotImplementedError()
    
    @property
    def center(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @property
    def x_radius(self) -> float:
        raise NotImplementedError()
    
    @property
    def y_radius(self) -> float:
        raise NotImplementedError()
    
    @property
    def rotation(self) -> float:
        raise NotImplementedError()
    

class EllipticArc:
    
    def linearize(self, coordinates : List[aspose.gis.common.Coordinate], step_size_in_degree : float) -> None:
        raise NotImplementedError()
    
    @property
    def ellipse(self) -> aspose.gis.common.Ellipse:
        raise NotImplementedError()
    
    @property
    def start_coordinate(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @property
    def end_coordinate(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @property
    def clockwise(self) -> bool:
        raise NotImplementedError()
    

class Ensure:
    
    @overload
    @staticmethod
    def in_range(arg : int, min : int, max_exclusive : int, parameter_name : str) -> None:
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def in_range(arg : int, min : int, max_exclusive : int, parameter_name : str) -> None:
        raise NotImplementedError()
    
    @staticmethod
    def not_special_double(arg : float, parameter_name : str) -> None:
        raise NotImplementedError()
    
    @staticmethod
    def multiples_to(arg : int, multiplier : int, parameter_name : str) -> None:
        raise NotImplementedError()
    

class GlobOptions:
    
    @property
    def wild_card(self) -> str:
        raise NotImplementedError()
    
    @wild_card.setter
    def wild_card(self, value : str) -> None:
        raise NotImplementedError()
    
    @property
    def single_char(self) -> str:
        raise NotImplementedError()
    
    @single_char.setter
    def single_char(self, value : str) -> None:
        raise NotImplementedError()
    
    @property
    def escape_char(self) -> str:
        raise NotImplementedError()
    
    @escape_char.setter
    def escape_char(self, value : str) -> None:
        raise NotImplementedError()
    
    @property
    def match_case(self) -> bool:
        raise NotImplementedError()
    
    @match_case.setter
    def match_case(self, value : bool) -> None:
        raise NotImplementedError()
    

class IdSequence:
    
    def get_next(self) -> str:
        raise NotImplementedError()
    

class LocalFilePath(AbstractPathInternal):
    
    def is_file(self) -> bool:
        raise NotImplementedError()
    
    def delete(self) -> None:
        raise NotImplementedError()
    
    def open(self, access : System.IO.FileAccess) -> io.RawIOBase:
        raise NotImplementedError()
    
    def list_directory(self) -> Iterable[aspose.gis.common.AbstractPathInternal]:
        raise NotImplementedError()
    
    def combine(self, filename : str) -> aspose.gis.common.AbstractPathInternal:
        raise NotImplementedError()
    
    def with_extension(self, new_extension : str) -> aspose.gis.common.AbstractPathInternal:
        raise NotImplementedError()
    
    def with_location(self, new_location : str) -> aspose.gis.common.AbstractPathInternal:
        raise NotImplementedError()
    
    @property
    def location(self) -> str:
        raise NotImplementedError()
    
    @property
    def separator(self) -> str:
        raise NotImplementedError()
    

class MatrixTransformation:
    
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
    
    @overload
    def transform(self, coordinate : aspose.gis.common.Coordinate) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @overload
    def transform(self, x : float, y : float) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    def scale(self, zoom_x : float, zoom_y : float) -> None:
        raise NotImplementedError()
    
    def clone(self) -> aspose.gis.common.MatrixTransformation:
        raise NotImplementedError()
    
    def lock_from_editing(self) -> None:
        raise NotImplementedError()
    
    def equals(self, other : aspose.gis.common.MatrixTransformation) -> bool:
        raise NotImplementedError()
    
    @property
    def is_editable(self) -> bool:
        raise NotImplementedError()
    
    @property
    def m11(self) -> float:
        raise NotImplementedError()
    
    @m11.setter
    def m11(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def m12(self) -> float:
        raise NotImplementedError()
    
    @m12.setter
    def m12(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def m21(self) -> float:
        raise NotImplementedError()
    
    @m21.setter
    def m21(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def m22(self) -> float:
        raise NotImplementedError()
    
    @m22.setter
    def m22(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def dx(self) -> float:
        raise NotImplementedError()
    
    @dx.setter
    def dx(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def dy(self) -> float:
        raise NotImplementedError()
    
    @dy.setter
    def dy(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def rotation(self) -> float:
        raise NotImplementedError()
    
    @property
    def is_null(self) -> bool:
        raise NotImplementedError()
    

class NumberOperations:
    
    @overload
    @staticmethod
    def degrees_to_radians(degrees : float) -> float:
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def degrees_to_radians(degrees : int) -> float:
        raise NotImplementedError()
    
    @staticmethod
    def nearly_equal(a : float, b : float, epsilon : float) -> bool:
        raise NotImplementedError()
    
    @staticmethod
    def nearly_equal_or_less(a : float, b : float, epsilon : float) -> bool:
        raise NotImplementedError()
    
    @staticmethod
    def nearly_equal_or_more(a : float, b : float, epsilon : float) -> bool:
        raise NotImplementedError()
    
    @staticmethod
    def strictly_more(a : float, b : float, epsilon : float) -> bool:
        raise NotImplementedError()
    
    @staticmethod
    def strictly_less(a : float, b : float, epsilon : float) -> bool:
        raise NotImplementedError()
    
    @staticmethod
    def clamp(value : float, min : float, max : float) -> float:
        raise NotImplementedError()
    
    @staticmethod
    def wrap_longitude(longitude_in_radians : float, tolerance : float) -> float:
        raise NotImplementedError()
    
    @staticmethod
    def radians_to_degrees(radians : float) -> float:
        raise NotImplementedError()
    
    EPSILON : float

class Rectangle:
    
    def equals(self, other : aspose.gis.common.Rectangle) -> bool:
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        raise NotImplementedError()
    
    @property
    def area(self) -> float:
        raise NotImplementedError()
    
    @property
    def size(self) -> aspose.gis.common.Size:
        raise NotImplementedError()
    
    @property
    def top_left(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @property
    def bottom_left(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @property
    def bottom_right(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @property
    def top_right(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @property
    def center(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    

class SingleStreamPath(AbstractPathInternal):
    
    def is_file(self) -> bool:
        raise NotImplementedError()
    
    def delete(self) -> None:
        raise NotImplementedError()
    
    def open(self, access : System.IO.FileAccess) -> io.RawIOBase:
        raise NotImplementedError()
    
    def list_directory(self) -> Iterable[aspose.gis.common.AbstractPathInternal]:
        raise NotImplementedError()
    
    def combine(self, path : str) -> aspose.gis.common.AbstractPathInternal:
        raise NotImplementedError()
    
    def with_extension(self, new_extension : str) -> aspose.gis.common.AbstractPathInternal:
        raise NotImplementedError()
    
    def with_location(self, path : str) -> aspose.gis.common.AbstractPathInternal:
        raise NotImplementedError()
    
    @property
    def location(self) -> str:
        raise NotImplementedError()
    
    @property
    def separator(self) -> str:
        raise NotImplementedError()
    

class Size:
    
    def to_coordinate(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    def equals(self, other : aspose.gis.common.Size) -> bool:
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        raise NotImplementedError()
    

class StringOperations:
    
    @staticmethod
    def is_ascii(text : str) -> bool:
        raise NotImplementedError()
    
    @staticmethod
    def matches(text : str, pattern : str, options : aspose.gis.common.GlobOptions) -> bool:
        raise NotImplementedError()
    

class Quadrant:
    
    NORTH_EAST : Quadrant
    NORTH_WEST : Quadrant
    SOUTH_WEST : Quadrant
    SOUTH_EAST : Quadrant

