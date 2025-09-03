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

class BufferLineSimplifier:
    
    @staticmethod
    def simplify_inside(ring : aspose.gis.topology.Chain, tolerance : float) -> aspose.gis.topology.Chain:
        raise NotImplementedError()
    
    @staticmethod
    def simplify_outside(ring : aspose.gis.topology.Chain, tolerance : float) -> aspose.gis.topology.Chain:
        raise NotImplementedError()
    
    @staticmethod
    def simplify_left(line : aspose.gis.topology.Chain, tolerance : float) -> aspose.gis.topology.Chain:
        raise NotImplementedError()
    
    @staticmethod
    def simplify_right(line : aspose.gis.topology.Chain, tolerance : float) -> aspose.gis.topology.Chain:
        raise NotImplementedError()
    

class BufferOptions:
    
    @staticmethod
    def all_round(quadrant_segments : int) -> aspose.gis.topology.buffer.BufferOptions:
        raise NotImplementedError()
    
    @property
    def join_style(self) -> aspose.gis.topology.buffer.BufferJoinStyle:
        raise NotImplementedError()
    
    @join_style.setter
    def join_style(self, value : aspose.gis.topology.buffer.BufferJoinStyle) -> None:
        raise NotImplementedError()
    
    @property
    def end_cap_style(self) -> aspose.gis.topology.buffer.BufferEndCapStyle:
        raise NotImplementedError()
    
    @end_cap_style.setter
    def end_cap_style(self, value : aspose.gis.topology.buffer.BufferEndCapStyle) -> None:
        raise NotImplementedError()
    
    @property
    def quadrant_segments(self) -> int:
        raise NotImplementedError()
    
    @quadrant_segments.setter
    def quadrant_segments(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def miter_limit(self) -> float:
        raise NotImplementedError()
    
    @miter_limit.setter
    def miter_limit(self, value : float) -> None:
        raise NotImplementedError()
    

class CurveBuilder:
    
    @overload
    def add_coordinate(self, x : float, y : float) -> None:
        raise NotImplementedError()
    
    @overload
    def add_coordinate(self, c : aspose.gis.common.Coordinate) -> None:
        raise NotImplementedError()
    
    @staticmethod
    def build_circle(center : aspose.gis.common.Coordinate, radius : float, quadrant_segments : int) -> Sequence[aspose.gis.common.Coordinate]:
        raise NotImplementedError()
    
    def arc_to(self, end_coordinate : aspose.gis.common.Coordinate, center : aspose.gis.common.Coordinate, clockwise : bool) -> None:
        raise NotImplementedError()
    
    @property
    def curve(self) -> List[aspose.gis.common.Coordinate]:
        raise NotImplementedError()
    

class OffsetCurveBuilder:
    
    @overload
    @staticmethod
    def build_one_side_for_line(line : aspose.gis.topology.Chain, distance : float, quadrant_segments : int) -> Sequence[aspose.gis.common.Coordinate]:
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def build_one_side_for_line(line : aspose.gis.topology.Chain, distance : float, options : aspose.gis.topology.buffer.BufferOptions) -> Sequence[aspose.gis.common.Coordinate]:
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def build_for_line(line : aspose.gis.topology.Chain, distance : float, quadrant_segments : int) -> Sequence[aspose.gis.common.Coordinate]:
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def build_for_line(line : aspose.gis.topology.Chain, distance : float, options : aspose.gis.topology.buffer.BufferOptions) -> Sequence[aspose.gis.common.Coordinate]:
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def build_for_ring(ring : aspose.gis.topology.Chain, distance : float, quadrant_segments : int) -> Sequence[aspose.gis.common.Coordinate]:
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def build_for_ring(ring : aspose.gis.topology.Chain, distance : float, options : aspose.gis.topology.buffer.BufferOptions) -> Sequence[aspose.gis.common.Coordinate]:
        raise NotImplementedError()
    

class BufferEndCapStyle:
    
    ROUND : BufferEndCapStyle
    FLAT : BufferEndCapStyle

class BufferJoinStyle:
    
    ROUND : BufferJoinStyle
    MITER : BufferJoinStyle

