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

class MapBlockTypes:
    
    RAW_BIN : int
    HEADER : int
    SPATIAL_INDEX : int
    OBJECTS : int
    COORDINATES : int
    GARBAGE : int
    TOOL : int

class MapCoordinatesSection:
    
    @property
    def coordinates_count(self) -> int:
        raise NotImplementedError()
    
    @property
    def holes_count(self) -> int:
        raise NotImplementedError()
    

class MapHeader:
    
    @property
    def map_file_version(self) -> int:
        raise NotImplementedError()
    
    @map_file_version.setter
    def map_file_version(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def block_size(self) -> int:
        raise NotImplementedError()
    
    @block_size.setter
    def block_size(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def first_block_size(self) -> int:
        raise NotImplementedError()
    
    @property
    def coordinate_system_to_distance_units(self) -> float:
        raise NotImplementedError()
    
    @coordinate_system_to_distance_units.setter
    def coordinate_system_to_distance_units(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def bounding_box(self) -> aspose.gis.common.BoundingBox:
        raise NotImplementedError()
    
    @property
    def first_index_block_position(self) -> int:
        raise NotImplementedError()
    
    @first_index_block_position.setter
    def first_index_block_position(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def first_garbage_block_position(self) -> int:
        raise NotImplementedError()
    
    @first_garbage_block_position.setter
    def first_garbage_block_position(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def first_tool_block_position(self) -> int:
        raise NotImplementedError()
    
    @first_tool_block_position.setter
    def first_tool_block_position(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def points_count(self) -> int:
        raise NotImplementedError()
    
    @points_count.setter
    def points_count(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def lines_count(self) -> int:
        raise NotImplementedError()
    
    @lines_count.setter
    def lines_count(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def regions_count(self) -> int:
        raise NotImplementedError()
    
    @regions_count.setter
    def regions_count(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def texts_count(self) -> int:
        raise NotImplementedError()
    
    @texts_count.setter
    def texts_count(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def maximal_coordinates_buffer_size(self) -> int:
        raise NotImplementedError()
    
    @maximal_coordinates_buffer_size.setter
    def maximal_coordinates_buffer_size(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def distance_units_code(self) -> int:
        raise NotImplementedError()
    
    @distance_units_code.setter
    def distance_units_code(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def maximal_spatial_index_depth(self) -> int:
        raise NotImplementedError()
    
    @maximal_spatial_index_depth.setter
    def maximal_spatial_index_depth(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def coordinate_precision(self) -> int:
        raise NotImplementedError()
    
    @coordinate_precision.setter
    def coordinate_precision(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def reflect_x_axis_coordinate(self) -> int:
        raise NotImplementedError()
    
    @reflect_x_axis_coordinate.setter
    def reflect_x_axis_coordinate(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def objects_length_array_id(self) -> int:
        raise NotImplementedError()
    
    @objects_length_array_id.setter
    def objects_length_array_id(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def pens_count(self) -> int:
        raise NotImplementedError()
    
    @pens_count.setter
    def pens_count(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def brushes_count(self) -> int:
        raise NotImplementedError()
    
    @brushes_count.setter
    def brushes_count(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def symbols_count(self) -> int:
        raise NotImplementedError()
    
    @symbols_count.setter
    def symbols_count(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def fonts_count(self) -> int:
        raise NotImplementedError()
    
    @fonts_count.setter
    def fonts_count(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def tool_blocks_count(self) -> int:
        raise NotImplementedError()
    
    @tool_blocks_count.setter
    def tool_blocks_count(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def coordinate_system(self) -> aspose.gis.common.formats.mapinfo.CoordinateSystem:
        raise NotImplementedError()
    
    @property
    def transform(self) -> aspose.gis.common.formats.mapinfo.tabformat.map.MapTransform:
        raise NotImplementedError()
    
    @transform.setter
    def transform(self, value : aspose.gis.common.formats.mapinfo.tabformat.map.MapTransform) -> None:
        raise NotImplementedError()
    

class MapHeaderConst:
    
    MAP_VERSION : int
    TAB_VERSION : int
    FILE_MAGIC_NUMBER : int
    HEADER_OBJECT_SIZES : List[int]

class MapObjectsHeader:
    
    @property
    def identifier(self) -> int:
        raise NotImplementedError()
    
    @identifier.setter
    def identifier(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def used_bytes_count(self) -> int:
        raise NotImplementedError()
    
    @used_bytes_count.setter
    def used_bytes_count(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def center_x(self) -> int:
        raise NotImplementedError()
    
    @center_x.setter
    def center_x(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def center_y(self) -> int:
        raise NotImplementedError()
    
    @center_y.setter
    def center_y(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def last_coordinate_block(self) -> int:
        raise NotImplementedError()
    
    @last_coordinate_block.setter
    def last_coordinate_block(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def first_coordinate_block(self) -> int:
        raise NotImplementedError()
    
    @first_coordinate_block.setter
    def first_coordinate_block(self, value : int) -> None:
        raise NotImplementedError()
    

class MapReader(aspose.gis.common.formats.mapinfo.IGraphcialObjectsFile):
    
    @property
    def coordinate_system(self) -> aspose.gis.common.formats.mapinfo.CoordinateSystem:
        raise NotImplementedError()
    
    @property
    def common_graphical_objects_type(self) -> Optional[aspose.gis.common.formats.mapinfo.graphicalobjects.GraphicalObjectType]:
        raise NotImplementedError()
    

class MapTransform:
    
    def apply(self, ix : int, iy : int) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    def to_int_coordinate(self, coordinate : aspose.gis.common.Coordinate, n_x : List[int], n_y : List[int]) -> None:
        raise NotImplementedError()
    
    @property
    def coordinates_origin_quadrant(self) -> aspose.gis.common.Quadrant:
        raise NotImplementedError()
    
    @property
    def coordinates_origin_quadrant_byte(self) -> int:
        raise NotImplementedError()
    
    @property
    def x_displacement(self) -> float:
        raise NotImplementedError()
    
    @property
    def y_displacement(self) -> float:
        raise NotImplementedError()
    
    @property
    def x_scale(self) -> float:
        raise NotImplementedError()
    
    @property
    def y_scale(self) -> float:
        raise NotImplementedError()
    

class MapObjectTypeCodes:
    
    NONE : MapObjectTypeCodes
    POINT : MapObjectTypeCodes
    LINE : MapObjectTypeCodes
    POLYLINE : MapObjectTypeCodes
    ARC : MapObjectTypeCodes
    REGION : MapObjectTypeCodes
    TEXT : MapObjectTypeCodes
    RECTANGLE : MapObjectTypeCodes
    ROUNDED_RECTANGLE : MapObjectTypeCodes
    ELLIPSE : MapObjectTypeCodes
    MULTI_POLYLINE : MapObjectTypeCodes
    FONT_POINT : MapObjectTypeCodes
    CUSTOM_POINT : MapObjectTypeCodes
    V450_REGION : MapObjectTypeCodes
    V450_MULTI_POLYLINE : MapObjectTypeCodes
    MULTI_POINT : MapObjectTypeCodes
    COLLECTION : MapObjectTypeCodes
    UNKNOWN1 : MapObjectTypeCodes
    V800_REGION : MapObjectTypeCodes
    V800_MULTI_POLYLINE : MapObjectTypeCodes
    V800_MULTI_POINT : MapObjectTypeCodes
    V800_COLLECTION : MapObjectTypeCodes

