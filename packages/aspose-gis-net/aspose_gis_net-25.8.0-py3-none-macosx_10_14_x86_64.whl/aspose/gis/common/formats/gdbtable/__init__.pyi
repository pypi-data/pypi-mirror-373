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

class GdbBezierSegment(GdbCurveSegment):
    
    @property
    def start_point_index(self) -> int:
        raise NotImplementedError()
    
    @start_point_index.setter
    def start_point_index(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def segment_type(self) -> aspose.gis.common.formats.gdbtable.GdbCurveSegmentType:
        raise NotImplementedError()
    
    @property
    def c1(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @c1.setter
    def c1(self, value : aspose.gis.common.Coordinate) -> None:
        raise NotImplementedError()
    
    @property
    def c2(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @c2.setter
    def c2(self, value : aspose.gis.common.Coordinate) -> None:
        raise NotImplementedError()
    

class GdbBinaryReaderExtensions:
    

class GdbBinaryWriterExtensions:
    

class GdbCircularArcSegment(GdbCurveSegment):
    
    @property
    def start_point_index(self) -> int:
        raise NotImplementedError()
    
    @start_point_index.setter
    def start_point_index(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def segment_type(self) -> aspose.gis.common.formats.gdbtable.GdbCurveSegmentType:
        raise NotImplementedError()
    
    @property
    def coordinate(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @coordinate.setter
    def coordinate(self, value : aspose.gis.common.Coordinate) -> None:
        raise NotImplementedError()
    
    @property
    def coordinate_is_interior(self) -> bool:
        raise NotImplementedError()
    
    @coordinate_is_interior.setter
    def coordinate_is_interior(self, value : bool) -> None:
        raise NotImplementedError()
    
    @property
    def is_empty(self) -> bool:
        raise NotImplementedError()
    
    @is_empty.setter
    def is_empty(self, value : bool) -> None:
        raise NotImplementedError()
    
    @property
    def is_line(self) -> bool:
        raise NotImplementedError()
    
    @is_line.setter
    def is_line(self, value : bool) -> None:
        raise NotImplementedError()
    
    @property
    def is_point(self) -> bool:
        raise NotImplementedError()
    
    @is_point.setter
    def is_point(self, value : bool) -> None:
        raise NotImplementedError()
    
    @property
    def is_minor(self) -> bool:
        raise NotImplementedError()
    
    @is_minor.setter
    def is_minor(self, value : bool) -> None:
        raise NotImplementedError()
    
    @property
    def is_counter_clockwise(self) -> bool:
        raise NotImplementedError()
    
    @is_counter_clockwise.setter
    def is_counter_clockwise(self, value : bool) -> None:
        raise NotImplementedError()
    

class GdbCurveSegment:
    
    @property
    def start_point_index(self) -> int:
        raise NotImplementedError()
    
    @start_point_index.setter
    def start_point_index(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def segment_type(self) -> aspose.gis.common.formats.gdbtable.GdbCurveSegmentType:
        raise NotImplementedError()
    

class GdbEllipticArcSegment(GdbCurveSegment):
    
    @property
    def start_point_index(self) -> int:
        raise NotImplementedError()
    
    @start_point_index.setter
    def start_point_index(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def segment_type(self) -> aspose.gis.common.formats.gdbtable.GdbCurveSegmentType:
        raise NotImplementedError()
    
    @property
    def center(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @center.setter
    def center(self, value : aspose.gis.common.Coordinate) -> None:
        raise NotImplementedError()
    
    @property
    def angle(self) -> float:
        raise NotImplementedError()
    
    @angle.setter
    def angle(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def angle_delta(self) -> float:
        raise NotImplementedError()
    
    @angle_delta.setter
    def angle_delta(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def rotation(self) -> float:
        raise NotImplementedError()
    
    @rotation.setter
    def rotation(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def semi_major_radius(self) -> float:
        raise NotImplementedError()
    
    @semi_major_radius.setter
    def semi_major_radius(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def minor_major_ratio(self) -> float:
        raise NotImplementedError()
    
    @minor_major_ratio.setter
    def minor_major_ratio(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def is_empty(self) -> bool:
        raise NotImplementedError()
    
    @is_empty.setter
    def is_empty(self, value : bool) -> None:
        raise NotImplementedError()
    
    @property
    def is_point(self) -> bool:
        raise NotImplementedError()
    
    @is_point.setter
    def is_point(self, value : bool) -> None:
        raise NotImplementedError()
    
    @property
    def is_line(self) -> bool:
        raise NotImplementedError()
    
    @is_line.setter
    def is_line(self, value : bool) -> None:
        raise NotImplementedError()
    
    @property
    def is_circular(self) -> bool:
        raise NotImplementedError()
    
    @is_circular.setter
    def is_circular(self, value : bool) -> None:
        raise NotImplementedError()
    
    @property
    def center_to(self) -> bool:
        raise NotImplementedError()
    
    @center_to.setter
    def center_to(self, value : bool) -> None:
        raise NotImplementedError()
    
    @property
    def center_from(self) -> bool:
        raise NotImplementedError()
    
    @center_from.setter
    def center_from(self, value : bool) -> None:
        raise NotImplementedError()
    
    @property
    def is_counter_clockwise(self) -> bool:
        raise NotImplementedError()
    
    @is_counter_clockwise.setter
    def is_counter_clockwise(self, value : bool) -> None:
        raise NotImplementedError()
    
    @property
    def is_minor(self) -> bool:
        raise NotImplementedError()
    
    @is_minor.setter
    def is_minor(self, value : bool) -> None:
        raise NotImplementedError()
    
    @property
    def is_complete(self) -> bool:
        raise NotImplementedError()
    
    @is_complete.setter
    def is_complete(self, value : bool) -> None:
        raise NotImplementedError()
    

class GdbFieldDescription:
    
    @property
    def name(self) -> str:
        raise NotImplementedError()
    
    @name.setter
    def name(self, value : str) -> None:
        raise NotImplementedError()
    
    @property
    def alias(self) -> str:
        raise NotImplementedError()
    
    @alias.setter
    def alias(self, value : str) -> None:
        raise NotImplementedError()
    
    @property
    def field_type(self) -> aspose.gis.common.formats.gdbtable.GdbFieldType:
        raise NotImplementedError()
    
    @property
    def is_nullable(self) -> bool:
        raise NotImplementedError()
    
    @is_nullable.setter
    def is_nullable(self, value : bool) -> None:
        raise NotImplementedError()
    
    @property
    def default_value(self) -> Any:
        raise NotImplementedError()
    
    @default_value.setter
    def default_value(self, value : Any) -> None:
        raise NotImplementedError()
    
    @property
    def width(self) -> int:
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : int) -> None:
        raise NotImplementedError()
    

class GdbMultiPartShape(GdbShape):
    
    @property
    def has_z(self) -> bool:
        raise NotImplementedError()
    
    @property
    def has_m(self) -> bool:
        raise NotImplementedError()
    
    @property
    def bounding_box(self) -> aspose.gis.common.BoundingBox:
        raise NotImplementedError()
    
    @bounding_box.setter
    def bounding_box(self, value : aspose.gis.common.BoundingBox) -> None:
        raise NotImplementedError()
    
    @property
    def parts_sizes(self) -> List[int]:
        raise NotImplementedError()
    
    @parts_sizes.setter
    def parts_sizes(self, value : List[int]) -> None:
        raise NotImplementedError()
    
    @property
    def xy(self) -> List[aspose.gis.common.Coordinate]:
        raise NotImplementedError()
    
    @xy.setter
    def xy(self, value : List[aspose.gis.common.Coordinate]) -> None:
        raise NotImplementedError()
    
    @property
    def z(self) -> List[float]:
        raise NotImplementedError()
    
    @z.setter
    def z(self, value : List[float]) -> None:
        raise NotImplementedError()
    
    @property
    def m(self) -> List[float]:
        raise NotImplementedError()
    
    @m.setter
    def m(self, value : List[float]) -> None:
        raise NotImplementedError()
    
    @property
    def curves(self) -> List[aspose.gis.common.formats.gdbtable.GdbCurveSegment]:
        raise NotImplementedError()
    
    @curves.setter
    def curves(self, value : List[aspose.gis.common.formats.gdbtable.GdbCurveSegment]) -> None:
        raise NotImplementedError()
    
    @property
    def has_curves(self) -> bool:
        raise NotImplementedError()
    

class GdbMultiPointShape(GdbShape):
    
    @property
    def has_z(self) -> bool:
        raise NotImplementedError()
    
    @property
    def has_m(self) -> bool:
        raise NotImplementedError()
    
    @property
    def bounding_box(self) -> aspose.gis.common.BoundingBox:
        raise NotImplementedError()
    
    @bounding_box.setter
    def bounding_box(self, value : aspose.gis.common.BoundingBox) -> None:
        raise NotImplementedError()
    
    @property
    def xy(self) -> List[aspose.gis.common.Coordinate]:
        raise NotImplementedError()
    
    @xy.setter
    def xy(self, value : List[aspose.gis.common.Coordinate]) -> None:
        raise NotImplementedError()
    
    @property
    def z(self) -> List[float]:
        raise NotImplementedError()
    
    @z.setter
    def z(self, value : List[float]) -> None:
        raise NotImplementedError()
    
    @property
    def m(self) -> List[float]:
        raise NotImplementedError()
    
    @m.setter
    def m(self, value : List[float]) -> None:
        raise NotImplementedError()
    

class GdbPointShape(GdbShape):
    
    @property
    def has_z(self) -> bool:
        raise NotImplementedError()
    
    @property
    def has_m(self) -> bool:
        raise NotImplementedError()
    
    @property
    def bounding_box(self) -> aspose.gis.common.BoundingBox:
        raise NotImplementedError()
    
    @bounding_box.setter
    def bounding_box(self, value : aspose.gis.common.BoundingBox) -> None:
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        raise NotImplementedError()
    
    @x.setter
    def x(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        raise NotImplementedError()
    
    @y.setter
    def y(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def z(self) -> Optional[float]:
        raise NotImplementedError()
    
    @z.setter
    def z(self, value : Optional[float]) -> None:
        raise NotImplementedError()
    
    @property
    def m(self) -> Optional[float]:
        raise NotImplementedError()
    
    @m.setter
    def m(self, value : Optional[float]) -> None:
        raise NotImplementedError()
    

class GdbShape:
    
    @property
    def has_z(self) -> bool:
        raise NotImplementedError()
    
    @property
    def has_m(self) -> bool:
        raise NotImplementedError()
    
    @property
    def bounding_box(self) -> aspose.gis.common.BoundingBox:
        raise NotImplementedError()
    
    @bounding_box.setter
    def bounding_box(self, value : aspose.gis.common.BoundingBox) -> None:
        raise NotImplementedError()
    

class GdbShapeFieldDescription(GdbFieldDescription):
    
    @property
    def name(self) -> str:
        raise NotImplementedError()
    
    @name.setter
    def name(self, value : str) -> None:
        raise NotImplementedError()
    
    @property
    def alias(self) -> str:
        raise NotImplementedError()
    
    @alias.setter
    def alias(self, value : str) -> None:
        raise NotImplementedError()
    
    @property
    def field_type(self) -> aspose.gis.common.formats.gdbtable.GdbFieldType:
        raise NotImplementedError()
    
    @property
    def is_nullable(self) -> bool:
        raise NotImplementedError()
    
    @is_nullable.setter
    def is_nullable(self, value : bool) -> None:
        raise NotImplementedError()
    
    @property
    def default_value(self) -> Any:
        raise NotImplementedError()
    
    @default_value.setter
    def default_value(self, value : Any) -> None:
        raise NotImplementedError()
    
    @property
    def width(self) -> int:
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : int) -> None:
        raise NotImplementedError()
    
    unknown_srs_string : str
    @property
    def has_z(self) -> bool:
        raise NotImplementedError()
    
    @has_z.setter
    def has_z(self, value : bool) -> None:
        raise NotImplementedError()
    
    @property
    def has_m(self) -> bool:
        raise NotImplementedError()
    
    @has_m.setter
    def has_m(self, value : bool) -> None:
        raise NotImplementedError()
    
    @property
    def srs_wkt(self) -> str:
        raise NotImplementedError()
    
    @srs_wkt.setter
    def srs_wkt(self, value : str) -> None:
        raise NotImplementedError()
    
    @property
    def x_origin(self) -> float:
        raise NotImplementedError()
    
    @x_origin.setter
    def x_origin(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def y_origin(self) -> float:
        raise NotImplementedError()
    
    @y_origin.setter
    def y_origin(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def xy_scale(self) -> float:
        raise NotImplementedError()
    
    @xy_scale.setter
    def xy_scale(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def m_origin(self) -> float:
        raise NotImplementedError()
    
    @m_origin.setter
    def m_origin(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def m_scale(self) -> float:
        raise NotImplementedError()
    
    @m_scale.setter
    def m_scale(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def z_origin(self) -> float:
        raise NotImplementedError()
    
    @z_origin.setter
    def z_origin(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def z_scale(self) -> float:
        raise NotImplementedError()
    
    @z_scale.setter
    def z_scale(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def xy_tolerance(self) -> float:
        raise NotImplementedError()
    
    @xy_tolerance.setter
    def xy_tolerance(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def m_tolerance(self) -> float:
        raise NotImplementedError()
    
    @m_tolerance.setter
    def m_tolerance(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def z_tolerance(self) -> float:
        raise NotImplementedError()
    
    @z_tolerance.setter
    def z_tolerance(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def bounding_box(self) -> aspose.gis.common.BoundingBox:
        raise NotImplementedError()
    

class GdbTableException:
    

class GdbTableFile:
    
    @overload
    @staticmethod
    def open(path : str) -> aspose.gis.common.formats.gdbtable.GdbTableFile:
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def open(path : aspose.gis.common.AbstractPathInternal) -> aspose.gis.common.formats.gdbtable.GdbTableFile:
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def create(path : str) -> aspose.gis.common.formats.gdbtable.GdbTableFile:
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def create(path : aspose.gis.common.AbstractPathInternal) -> aspose.gis.common.formats.gdbtable.GdbTableFile:
        raise NotImplementedError()
    
    @staticmethod
    def is_valid_field_name(name : str, error : List[String]) -> bool:
        raise NotImplementedError()
    
    def add_field(self, field : aspose.gis.common.formats.gdbtable.GdbFieldDescription) -> None:
        raise NotImplementedError()
    
    def has_field(self, name : str) -> bool:
        raise NotImplementedError()
    
    def is_valid_and_unqiue_field_name(self, name : str, error : List[String]) -> bool:
        raise NotImplementedError()
    
    def read_row(self, row_id : int) -> aspose.gis.common.formats.gdbtable.GdbTableRowReader:
        raise NotImplementedError()
    
    def read_row_at(self, row_index : int) -> aspose.gis.common.formats.gdbtable.GdbTableRowReader:
        raise NotImplementedError()
    
    def delete_row(self, row_id : int) -> None:
        raise NotImplementedError()
    
    def delete_row_at(self, row_index : int) -> None:
        raise NotImplementedError()
    
    def create_row(self) -> aspose.gis.common.formats.gdbtable.GdbTableRowWriter:
        raise NotImplementedError()
    
    def add_row(self, row : aspose.gis.common.formats.gdbtable.GdbTableRowWriter) -> int:
        raise NotImplementedError()
    
    def update_row(self, row : aspose.gis.common.formats.gdbtable.GdbTableRowWriter, row_index : int) -> None:
        raise NotImplementedError()
    
    @property
    def is_dirty(self) -> bool:
        raise NotImplementedError()
    
    @property
    def gdb_table_version(self) -> aspose.gis.common.formats.gdbtable.GdbTableVersion:
        raise NotImplementedError()
    
    @property
    def count(self) -> int:
        raise NotImplementedError()
    
    @property
    def shape_type(self) -> aspose.gis.common.formats.gdbtable.GdbTableShapeType:
        raise NotImplementedError()
    
    @shape_type.setter
    def shape_type(self, value : aspose.gis.common.formats.gdbtable.GdbTableShapeType) -> None:
        raise NotImplementedError()
    
    @property
    def fields(self) -> Sequence[aspose.gis.common.formats.gdbtable.GdbFieldDescription]:
        raise NotImplementedError()
    
    @property
    def shape_field(self) -> aspose.gis.common.formats.gdbtable.GdbShapeFieldDescription:
        raise NotImplementedError()
    
    @property
    def object_id_field(self) -> aspose.gis.common.formats.gdbtable.GdbFieldDescription:
        raise NotImplementedError()
    
    @property
    def next_row_id(self) -> int:
        raise NotImplementedError()
    

class GdbTableIndexFile:
    
    @overload
    @staticmethod
    def open(path : str) -> aspose.gis.common.formats.gdbtable.GdbTableIndexFile:
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def open(path : aspose.gis.common.AbstractPathInternal) -> aspose.gis.common.formats.gdbtable.GdbTableIndexFile:
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def create(path : str) -> aspose.gis.common.formats.gdbtable.GdbTableIndexFile:
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def create(path : aspose.gis.common.AbstractPathInternal) -> aspose.gis.common.formats.gdbtable.GdbTableIndexFile:
        raise NotImplementedError()
    
    def is_block_present(self, block_number : int) -> bool:
        raise NotImplementedError()
    
    def add(self, offset : int) -> int:
        raise NotImplementedError()
    
    def delete(self, row_id : int) -> None:
        raise NotImplementedError()
    
    def get_offset(self, row_id : int) -> int:
        raise NotImplementedError()
    
    @property
    def number_of_offsets_in_block(self) -> int:
        raise NotImplementedError()
    
    @property
    def last_row_id(self) -> int:
        raise NotImplementedError()
    
    @property
    def next_row_id(self) -> int:
        raise NotImplementedError()
    
    @property
    def blocks_count(self) -> int:
        raise NotImplementedError()
    

class GdbTableRowReader:
    
    def skip_field(self) -> None:
        raise NotImplementedError()
    
    def read_int16(self) -> int:
        raise NotImplementedError()
    
    def read_int32(self) -> int:
        raise NotImplementedError()
    
    def read_float32(self) -> float:
        raise NotImplementedError()
    
    def read_float64(self) -> float:
        raise NotImplementedError()
    
    def read_raster(self) -> int:
        raise NotImplementedError()
    
    def read_string(self) -> str:
        raise NotImplementedError()
    
    def read_xml(self) -> str:
        raise NotImplementedError()
    
    def read_guid(self) -> UUID:
        raise NotImplementedError()
    
    def read_global_id(self) -> UUID:
        raise NotImplementedError()
    
    def read_date_time(self) -> datetime:
        raise NotImplementedError()
    
    def read_binary(self) -> List[int]:
        raise NotImplementedError()
    
    def read_shape(self) -> aspose.gis.common.formats.gdbtable.GdbShape:
        raise NotImplementedError()
    
    @property
    def table(self) -> aspose.gis.common.formats.gdbtable.GdbTableFile:
        raise NotImplementedError()
    
    @property
    def row_id(self) -> int:
        raise NotImplementedError()
    
    @property
    def field_description(self) -> aspose.gis.common.formats.gdbtable.GdbFieldDescription:
        raise NotImplementedError()
    
    @property
    def has_field(self) -> bool:
        raise NotImplementedError()
    
    @property
    def is_field_null(self) -> bool:
        raise NotImplementedError()
    

class GdbTableRowWriter:
    
    def write_null(self) -> None:
        raise NotImplementedError()
    
    def write_int16(self, value : int) -> None:
        raise NotImplementedError()
    
    def write_int32(self, value : int) -> None:
        raise NotImplementedError()
    
    def write_float32(self, value : float) -> None:
        raise NotImplementedError()
    
    def write_float64(self, value : float) -> None:
        raise NotImplementedError()
    
    def write_string(self, value : str) -> None:
        raise NotImplementedError()
    
    def write_date_time(self, date_time : datetime) -> None:
        raise NotImplementedError()
    
    def write_shape(self, shape : aspose.gis.common.formats.gdbtable.GdbShape) -> None:
        raise NotImplementedError()
    
    def write_xml(self, xml : str) -> None:
        raise NotImplementedError()
    
    def write_binary(self, bytes : List[int]) -> None:
        raise NotImplementedError()
    
    def write_global_id(self, guid : UUID) -> None:
        raise NotImplementedError()
    
    def write_guid(self, guid : UUID) -> None:
        raise NotImplementedError()
    
    @property
    def has_field(self) -> bool:
        raise NotImplementedError()
    
    @property
    def field_description(self) -> aspose.gis.common.formats.gdbtable.GdbFieldDescription:
        raise NotImplementedError()
    

class GdbCurveSegmentType:
    
    CIRCULAR_ARC : GdbCurveSegmentType
    LINE : GdbCurveSegmentType
    SPIRAL : GdbCurveSegmentType
    BEZIER : GdbCurveSegmentType
    ELLIPTIC_ARC : GdbCurveSegmentType

class GdbFieldType:
    
    INT16 : GdbFieldType
    INT32 : GdbFieldType
    FLOAT32 : GdbFieldType
    FLOAT64 : GdbFieldType
    STRING : GdbFieldType
    DATE_TIME : GdbFieldType
    OBJECT_ID : GdbFieldType
    SHAPE : GdbFieldType
    BINARY : GdbFieldType
    RASTER : GdbFieldType
    GUID : GdbFieldType
    GLOBAL_ID : GdbFieldType
    XML : GdbFieldType

class GdbTableShapeType:
    
    NONE : GdbTableShapeType
    POINT : GdbTableShapeType
    MULTI_POINT : GdbTableShapeType
    POLYLINE : GdbTableShapeType
    POLYGON : GdbTableShapeType
    MULTI_PATCH : GdbTableShapeType

class GdbTableVersion:
    
    VERSION9 : GdbTableVersion
    VERSION10 : GdbTableVersion

