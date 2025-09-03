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

class Chain:
    
    @staticmethod
    def compute_is_clockwise(coordinates : Sequence[aspose.gis.common.Coordinate]) -> bool:
        raise NotImplementedError()
    
    def segment_at(self, index : int) -> aspose.gis.topology.ChainSegment:
        raise NotImplementedError()
    
    def locate(self, coordinate : aspose.gis.common.Coordinate) -> aspose.gis.topology.Location:
        raise NotImplementedError()
    
    def take_coordinates_dangerous(self) -> List[aspose.gis.common.Coordinate]:
        raise NotImplementedError()
    
    @property
    def start_coordinate(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @property
    def end_coordinate(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @property
    def segments_count(self) -> int:
        raise NotImplementedError()
    
    @property
    def is_closed(self) -> bool:
        raise NotImplementedError()
    
    @property
    def is_clockwise(self) -> bool:
        raise NotImplementedError()
    

class ChainSegment:
    
    def contains(self, coordinate : aspose.gis.common.Coordinate) -> bool:
        raise NotImplementedError()
    
    def is_subsequent_to(self, other : aspose.gis.topology.ChainSegment) -> bool:
        raise NotImplementedError()
    
    def equals(self, other : aspose.gis.topology.ChainSegment) -> bool:
        raise NotImplementedError()
    
    @property
    def c1(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @property
    def c2(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @property
    def chain(self) -> aspose.gis.topology.Chain:
        raise NotImplementedError()
    
    @property
    def is_upward(self) -> bool:
        raise NotImplementedError()
    
    @property
    def index(self) -> int:
        raise NotImplementedError()
    

class ContainmentTree:
    
    def get_tree_node_of(self, chain : aspose.gis.topology.Chain) -> aspose.gis.topology.ContainmentTreeNode:
        raise NotImplementedError()
    
    @property
    def is_valid(self) -> bool:
        raise NotImplementedError()
    
    @property
    def top_level_nodes(self) -> Sequence[aspose.gis.topology.ContainmentTreeNode]:
        raise NotImplementedError()
    
    @property
    def nodes(self) -> Iterable[aspose.gis.topology.ContainmentTreeNode]:
        raise NotImplementedError()
    

class ContainmentTreeNode:
    
    @property
    def chain(self) -> aspose.gis.topology.Chain:
        raise NotImplementedError()
    
    @property
    def children(self) -> Sequence[aspose.gis.topology.ContainmentTreeNode]:
        raise NotImplementedError()
    
    @property
    def depth(self) -> int:
        raise NotImplementedError()
    

class CoordinateExtensions:
    
    @staticmethod
    def is_on_segment(c : aspose.gis.common.Coordinate, p1 : aspose.gis.common.Coordinate, p2 : aspose.gis.common.Coordinate) -> bool:
        raise NotImplementedError()
    
    @staticmethod
    def is_inside_bounding_box(c : aspose.gis.common.Coordinate, p1 : aspose.gis.common.Coordinate, p2 : aspose.gis.common.Coordinate) -> bool:
        raise NotImplementedError()
    
    @staticmethod
    def distance_to(c : aspose.gis.common.Coordinate, l1 : aspose.gis.common.Coordinate, l2 : aspose.gis.common.Coordinate) -> float:
        raise NotImplementedError()
    
    @staticmethod
    def get_orientation(c : aspose.gis.common.Coordinate, p1 : aspose.gis.common.Coordinate, p2 : aspose.gis.common.Coordinate) -> aspose.gis.topology.Orientation:
        raise NotImplementedError()
    

class Intersection:
    
    @property
    def intersection_type(self) -> aspose.gis.topology.IntersectionType:
        raise NotImplementedError()
    
    @property
    def has_segment2(self) -> bool:
        raise NotImplementedError()
    
    @property
    def segment1(self) -> aspose.gis.topology.ChainSegment:
        raise NotImplementedError()
    
    @property
    def segment2(self) -> aspose.gis.topology.ChainSegment:
        raise NotImplementedError()
    
    @property
    def chain1(self) -> aspose.gis.topology.Chain:
        raise NotImplementedError()
    
    @property
    def chain2(self) -> aspose.gis.topology.Chain:
        raise NotImplementedError()
    
    @property
    def coordinate(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @property
    def end_coordinate(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    

class IntersectionMatrix:
    
    @staticmethod
    def is_valid_pattern(intersection_pattern_matrix : str, error_message : List[String]) -> bool:
        raise NotImplementedError()
    
    def matches(self, other : aspose.gis.topology.IntersectionMatrix) -> bool:
        raise NotImplementedError()
    
    def increase_can_change_matches(self, other : aspose.gis.topology.IntersectionMatrix) -> bool:
        raise NotImplementedError()
    
    def get(self, location1 : aspose.gis.topology.Location, location2 : aspose.gis.topology.Location) -> aspose.gis.topology.IntersectionMatrixDimension:
        raise NotImplementedError()
    
    def set(self, location1 : aspose.gis.topology.Location, location2 : aspose.gis.topology.Location, dimension : aspose.gis.topology.IntersectionMatrixDimension) -> None:
        raise NotImplementedError()
    
    def set_at_least(self, location1 : aspose.gis.topology.Location, location2 : aspose.gis.topology.Location, dimension : aspose.gis.topology.IntersectionMatrixDimension) -> bool:
        raise NotImplementedError()
    

class TopologyException:
    

class TopologyGeometry:
    
    def is_exterior_ring(self, chain : aspose.gis.topology.Chain) -> bool:
        raise NotImplementedError()
    
    def add_line_string(self, line : aspose.gis.topology.Chain) -> None:
        raise NotImplementedError()
    
    def add_polygon_exterior_ring(self, ring : aspose.gis.topology.Chain) -> None:
        raise NotImplementedError()
    
    def add_polygon_interior_ring(self, ring : aspose.gis.topology.Chain) -> None:
        raise NotImplementedError()
    
    def add_point(self, c : aspose.gis.common.Coordinate) -> None:
        raise NotImplementedError()
    
    def has_valid_rings_nesting(self) -> bool:
        raise NotImplementedError()
    
    def get_intersections(self) -> Iterable[aspose.gis.topology.Intersection]:
        raise NotImplementedError()
    
    def buffer(self, distance : float, buffer_options : aspose.gis.topology.buffer.BufferOptions) -> aspose.gis.topology.TopologyGeometry:
        raise NotImplementedError()
    
    @property
    def exterior_rings(self) -> Sequence[aspose.gis.topology.Chain]:
        raise NotImplementedError()
    
    @property
    def interior_rings(self) -> Sequence[aspose.gis.topology.Chain]:
        raise NotImplementedError()
    
    @property
    def lines(self) -> Sequence[aspose.gis.topology.Chain]:
        raise NotImplementedError()
    
    @property
    def points(self) -> Sequence[aspose.gis.common.Coordinate]:
        raise NotImplementedError()
    

class IntersectionMatrixDimension:
    
    NO_DIMENSION : IntersectionMatrixDimension
    POINT_DIMENSION : IntersectionMatrixDimension
    LINE_DIMENSION : IntersectionMatrixDimension
    AREA_DIMENSION : IntersectionMatrixDimension
    ANY_DIMENSION : IntersectionMatrixDimension
    IRRELEVANT : IntersectionMatrixDimension

class IntersectionType:
    
    SEGMENT_WITH_SEGMENT : IntersectionType
    SEGMENT_WITH_SEGMENT_OVERLAPPING : IntersectionType
    SEGMENT_WITH_POINT : IntersectionType

class Location:
    
    UNDEFINED : Location
    EXTERIOR : Location
    BOUNDARY : Location
    INTERIOR : Location

class Orientation:
    
    COLLINEAR : Orientation
    CLOCKWISE : Orientation
    COUNTER_CLOCKWISE : Orientation

