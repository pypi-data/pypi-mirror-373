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

class Column:
    
    @staticmethod
    def get_type(type_name : str) -> aspose.gis.common.formats.mapinfo.ColumnType:
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        raise NotImplementedError()
    
    @name.setter
    def name(self, value : str) -> None:
        raise NotImplementedError()
    
    @property
    def column_type(self) -> aspose.gis.common.formats.mapinfo.ColumnType:
        raise NotImplementedError()
    
    @column_type.setter
    def column_type(self, value : aspose.gis.common.formats.mapinfo.ColumnType) -> None:
        raise NotImplementedError()
    
    @property
    def width(self) -> int:
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def precision(self) -> int:
        raise NotImplementedError()
    
    @precision.setter
    def precision(self, value : int) -> None:
        raise NotImplementedError()
    

class CoordinateSystem:
    
    @property
    def projection_id(self) -> int:
        raise NotImplementedError()
    
    @projection_id.setter
    def projection_id(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def projection_parameters(self) -> List[float]:
        raise NotImplementedError()
    
    @property
    def unit_id(self) -> aspose.gis.common.formats.mapinfo.UnitId:
        raise NotImplementedError()
    
    @unit_id.setter
    def unit_id(self, value : aspose.gis.common.formats.mapinfo.UnitId) -> None:
        raise NotImplementedError()
    
    @property
    def datum(self) -> aspose.gis.common.formats.mapinfo.Datum:
        raise NotImplementedError()
    

class Datum:
    
    @property
    def id(self) -> int:
        raise NotImplementedError()
    
    @id.setter
    def id(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def has_datum_parameters(self) -> bool:
        raise NotImplementedError()
    
    @has_datum_parameters.setter
    def has_datum_parameters(self, value : bool) -> None:
        raise NotImplementedError()
    
    @property
    def ellipsoid_id(self) -> int:
        raise NotImplementedError()
    
    @ellipsoid_id.setter
    def ellipsoid_id(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def shift_x(self) -> float:
        raise NotImplementedError()
    
    @shift_x.setter
    def shift_x(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def shift_y(self) -> float:
        raise NotImplementedError()
    
    @shift_y.setter
    def shift_y(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def shift_z(self) -> float:
        raise NotImplementedError()
    
    @shift_z.setter
    def shift_z(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def rotation_x(self) -> float:
        raise NotImplementedError()
    
    @rotation_x.setter
    def rotation_x(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def rotation_y(self) -> float:
        raise NotImplementedError()
    
    @rotation_y.setter
    def rotation_y(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def rotation_z(self) -> float:
        raise NotImplementedError()
    
    @rotation_z.setter
    def rotation_z(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def scale(self) -> float:
        raise NotImplementedError()
    
    @scale.setter
    def scale(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def prime_meridian(self) -> float:
        raise NotImplementedError()
    
    @prime_meridian.setter
    def prime_meridian(self, value : float) -> None:
        raise NotImplementedError()
    

class IDataRow:
    
    def is_null(self, field_index : int) -> bool:
        raise NotImplementedError()
    
    def read_character(self, field_index : int) -> str:
        raise NotImplementedError()
    
    def read_integer(self, field_index : int) -> int:
        raise NotImplementedError()
    
    def read_small_integer(self, field_index : int) -> int:
        raise NotImplementedError()
    
    def read_large_integer(self, field_index : int) -> int:
        raise NotImplementedError()
    
    def read_decimal(self, field_index : int) -> float:
        raise NotImplementedError()
    
    def read_float(self, field_index : int) -> float:
        raise NotImplementedError()
    
    def read_date_time(self, field_index : int) -> datetime:
        raise NotImplementedError()
    
    def read_date(self, field_index : int) -> datetime:
        raise NotImplementedError()
    
    def read_time(self, field_index : int) -> datetime:
        raise NotImplementedError()
    
    def read_logical(self, field_index : int) -> bool:
        raise NotImplementedError()
    
    @property
    def row_number(self) -> int:
        raise NotImplementedError()
    
    @property
    def fields_count(self) -> int:
        raise NotImplementedError()
    

class IDataRowsFile:
    

class IGraphcialObjectsFile:
    
    @property
    def common_graphical_objects_type(self) -> Optional[aspose.gis.common.formats.mapinfo.graphicalobjects.GraphicalObjectType]:
        raise NotImplementedError()
    

class MapInfoException:
    

class MapInfoSizes:
    
    HEADER_SIZE : int
    OBJECTS_HEADER : int
    COORDINATE_HEADER : int
    UNCOMPRESSED_COORDINATE : int
    COMPRESSED_COORDINATE : int
    SEGMENT_HEADER : int
    SEGMENT_HEADER450 : int

class ColumnType:
    
    CHAR : ColumnType
    INTEGER : ColumnType
    SMALL_INTEGER : ColumnType
    LARGE_INTEGER : ColumnType
    DECIMAL : ColumnType
    FLOAT : ColumnType
    DATE : ColumnType
    TIME : ColumnType
    DATE_TIME : ColumnType
    LOGICAL : ColumnType

class UnitId:
    
    UNKNOWN : UnitId
    MILE : UnitId
    KILOMETER : UnitId
    INCH : UnitId
    INTERNATIONAL_FOOT : UnitId
    YARD : UnitId
    MILLIMETER : UnitId
    CENTIMETER : UnitId
    METER : UnitId
    US_SURVEY_FOOT : UnitId
    NAUTICAL_MILE : UnitId
    EMPTY : UnitId
    LINK : UnitId
    CHAIN : UnitId
    ROD : UnitId
    DEGREE : UnitId

