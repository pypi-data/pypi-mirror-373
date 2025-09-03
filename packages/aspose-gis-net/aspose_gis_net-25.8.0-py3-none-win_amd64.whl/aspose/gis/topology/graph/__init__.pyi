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

class Edge(aspose.gis.topology.Chain):
    
    @staticmethod
    def compute_is_clockwise(coordinates : Sequence[aspose.gis.common.Coordinate]) -> bool:
        raise NotImplementedError()
    
    def segment_at(self, index : int) -> aspose.gis.topology.ChainSegment:
        raise NotImplementedError()
    
    def locate(self, coordinate : aspose.gis.common.Coordinate) -> aspose.gis.topology.Location:
        raise NotImplementedError()
    
    def take_coordinates_dangerous(self) -> List[aspose.gis.common.Coordinate]:
        raise NotImplementedError()
    
    def inner_location(self, index : int) -> aspose.gis.topology.Location:
        raise NotImplementedError()
    
    def outer_location(self, index : int) -> aspose.gis.topology.Location:
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
    
    @property
    def label(self) -> aspose.gis.labeling.Label:
        raise NotImplementedError()
    

class EdgeEnd:
    
    @property
    def origin(self) -> aspose.gis.topology.graph.EdgeEndStar:
        raise NotImplementedError()
    
    @origin.setter
    def origin(self, value : aspose.gis.topology.graph.EdgeEndStar) -> None:
        raise NotImplementedError()
    
    @property
    def destination(self) -> aspose.gis.topology.graph.EdgeEndStar:
        raise NotImplementedError()
    
    @property
    def opposite(self) -> aspose.gis.topology.graph.EdgeEnd:
        raise NotImplementedError()
    
    @property
    def edge(self) -> aspose.gis.topology.graph.Edge:
        raise NotImplementedError()
    
    @property
    def start_coordinate(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @property
    def end_coordinate(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @property
    def is_forward(self) -> bool:
        raise NotImplementedError()
    
    @property
    def label(self) -> aspose.gis.labeling.Label:
        raise NotImplementedError()
    

class EdgeEndStar:
    
    def get_index_of(self, edge_end : aspose.gis.topology.graph.EdgeEnd) -> int:
        raise NotImplementedError()
    
    def enumerate_clockwise(self) -> Iterable[aspose.gis.topology.graph.EdgeEnd]:
        raise NotImplementedError()
    
    def enumerate_counter_clockwise(self) -> Iterable[aspose.gis.topology.graph.EdgeEnd]:
        raise NotImplementedError()
    
    def enumerate_clockwise_from(self, start_edge_end : aspose.gis.topology.graph.EdgeEnd) -> Iterable[aspose.gis.topology.graph.EdgeEnd]:
        raise NotImplementedError()
    
    def enumerate_counter_clockwise_from(self, start_edge_end : aspose.gis.topology.graph.EdgeEnd) -> Iterable[aspose.gis.topology.graph.EdgeEnd]:
        raise NotImplementedError()
    
    @property
    def node(self) -> aspose.gis.topology.graph.Node:
        raise NotImplementedError()
    
    @property
    def coordinate(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @property
    def count(self) -> int:
        raise NotImplementedError()
    
    def __getitem__(self, key : int) -> aspose.gis.topology.graph.EdgeEnd:
        raise NotImplementedError()
    

class Label:
    
    def left_location(self, geometry_index : int) -> aspose.gis.topology.Location:
        raise NotImplementedError()
    
    def on_location(self, geometry_index : int) -> aspose.gis.topology.Location:
        raise NotImplementedError()
    
    def right_location(self, geometry_index : int) -> aspose.gis.topology.Location:
        raise NotImplementedError()
    
    def is_area(self, geometry_index : int) -> bool:
        raise NotImplementedError()
    

class Node:
    
    def location(self, geometry_index : int) -> aspose.gis.topology.Location:
        raise NotImplementedError()
    
    @property
    def coordinate(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @property
    def edge_end_star(self) -> aspose.gis.topology.graph.EdgeEndStar:
        raise NotImplementedError()
    
    @property
    def is_isolated(self) -> bool:
        raise NotImplementedError()
    
    @property
    def label(self) -> aspose.gis.labeling.Label:
        raise NotImplementedError()
    

class NodeMap:
    
    @overload
    def get_node_at(self, x : float, y : float) -> aspose.gis.topology.graph.Node:
        raise NotImplementedError()
    
    @overload
    def get_node_at(self, coordinate : aspose.gis.common.Coordinate) -> aspose.gis.topology.graph.Node:
        raise NotImplementedError()
    
    @property
    def coordinates(self) -> Iterable[aspose.gis.common.Coordinate]:
        raise NotImplementedError()
    

class PlanarGraph:
    
    @overload
    @staticmethod
    def build(geometry : aspose.gis.topology.TopologyGeometry) -> aspose.gis.topology.graph.PlanarGraph:
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def build(geometry0 : aspose.gis.topology.TopologyGeometry, geometry1 : aspose.gis.topology.TopologyGeometry) -> aspose.gis.topology.graph.PlanarGraph:
        raise NotImplementedError()
    
    @overload
    def is_area_labels_consistent(self) -> bool:
        raise NotImplementedError()
    
    @overload
    def is_area_labels_consistent(self, inconsistent_star : List[aspose.gis.topology.graph.EdgeEndStar], geometry_index : List[int]) -> bool:
        raise NotImplementedError()
    
    def get_intersection_matrix(self) -> aspose.gis.topology.IntersectionMatrix:
        raise NotImplementedError()
    
    def has_splitted_edges(self) -> bool:
        raise NotImplementedError()
    
    def throw_is_not_consistent(self, left_name : str, right_name : str) -> None:
        raise NotImplementedError()
    
    def select_overlay(self, code : aspose.gis.topology.graph.OverlayCode) -> aspose.gis.topology.graph.PlanarGraph:
        raise NotImplementedError()
    
    def select_intersection(self) -> aspose.gis.topology.graph.PlanarGraph:
        raise NotImplementedError()
    
    def select_union(self) -> aspose.gis.topology.graph.PlanarGraph:
        raise NotImplementedError()
    
    def select_difference(self) -> aspose.gis.topology.graph.PlanarGraph:
        raise NotImplementedError()
    
    def select_sym_difference(self) -> aspose.gis.topology.graph.PlanarGraph:
        raise NotImplementedError()
    
    def build_geometry(self, join_lines : bool) -> aspose.gis.topology.TopologyGeometry:
        raise NotImplementedError()
    
    def relate(self, intersection_pattern_matrix : str) -> bool:
        raise NotImplementedError()
    
    def complete_labeling(self) -> None:
        raise NotImplementedError()
    
    @property
    def edges(self) -> List[aspose.gis.topology.graph.Edge]:
        raise NotImplementedError()
    
    @property
    def edge_ends(self) -> Sequence[aspose.gis.topology.graph.EdgeEnd]:
        raise NotImplementedError()
    
    @property
    def nodes(self) -> aspose.gis.topology.graph.NodeMap:
        raise NotImplementedError()
    
    @property
    def intersector_events_count(self) -> int:
        raise NotImplementedError()
    

class OverlayCode:
    
    INTERSECTION : OverlayCode
    UNION : OverlayCode
    DIFFERENCE : OverlayCode
    SYM_DIFFERENCE : OverlayCode

