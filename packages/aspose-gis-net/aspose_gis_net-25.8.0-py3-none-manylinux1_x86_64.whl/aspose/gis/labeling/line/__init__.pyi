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

class CompoundLabelPosition(aspose.gis.labeling.LabelPosition):
    
    @property
    def bounding_rectangle(self) -> aspose.gis.common.BoundingRectangle:
        raise NotImplementedError()
    
    @property
    def cost(self) -> float:
        raise NotImplementedError()
    
    @property
    def parts(self) -> Sequence[aspose.gis.labeling.line.SymbolTetragon]:
        raise NotImplementedError()
    

class CurvedLinePlacer(IAlongLinePlacer):
    
    def accumulate_candidates(self, candidates : List[aspose.gis.labeling.LabelPosition], line : Sequence[aspose.gis.common.Coordinate]) -> None:
        raise NotImplementedError()
    

class IAlongLinePlacer:
    
    def accumulate_candidates(self, candidates : List[aspose.gis.labeling.LabelPosition], line : Sequence[aspose.gis.common.Coordinate]) -> None:
        raise NotImplementedError()
    

class LineGeometryUtils:
    
    @staticmethod
    def normalized_angle(angle : float) -> float:
        raise NotImplementedError()
    
    @staticmethod
    def angle(end : aspose.gis.common.Coordinate, start : aspose.gis.common.Coordinate) -> float:
        raise NotImplementedError()
    
    @staticmethod
    def angle_anti(end : aspose.gis.common.Coordinate, start : aspose.gis.common.Coordinate) -> float:
        raise NotImplementedError()
    
    @staticmethod
    def find_line_circle_intersection(charter_start : aspose.gis.common.Coordinate, diameter : float, segment_start : aspose.gis.common.Coordinate, segment_end : aspose.gis.common.Coordinate) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    

class LinePlacerContext:
    
    @property
    def candidates_limit(self) -> float:
        raise NotImplementedError()
    
    @candidates_limit.setter
    def candidates_limit(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def label_width(self) -> float:
        raise NotImplementedError()
    
    @label_width.setter
    def label_width(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def label_height(self) -> float:
        raise NotImplementedError()
    
    @label_height.setter
    def label_height(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def max_angle_inside(self) -> float:
        raise NotImplementedError()
    
    @max_angle_inside.setter
    def max_angle_inside(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def max_angle_outside(self) -> float:
        raise NotImplementedError()
    
    @max_angle_outside.setter
    def max_angle_outside(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def line_offset(self) -> float:
        raise NotImplementedError()
    
    @line_offset.setter
    def line_offset(self, value : float) -> None:
        raise NotImplementedError()
    

class MeasuredLine:
    
    def get_point_by_distance(self, distance_along_line : float) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    def get_segment_index(self, distance_along_line : float) -> int:
        raise NotImplementedError()
    
    @property
    def line(self) -> Sequence[aspose.gis.common.Coordinate]:
        raise NotImplementedError()
    
    @property
    def segment_lengths(self) -> Sequence[float]:
        raise NotImplementedError()
    
    @property
    def distance_to_segment(self) -> Sequence[float]:
        raise NotImplementedError()
    
    @property
    def middle_of_line(self) -> float:
        raise NotImplementedError()
    
    @property
    def is_closed(self) -> bool:
        raise NotImplementedError()
    
    @property
    def total_line_length(self) -> float:
        raise NotImplementedError()
    

class MeasuredLineSegment:
    
    @property
    def angle(self) -> float:
        raise NotImplementedError()
    
    @property
    def along_line_start(self) -> float:
        raise NotImplementedError()
    
    @property
    def along_line_end(self) -> float:
        raise NotImplementedError()
    
    @property
    def along_line_center(self) -> float:
        raise NotImplementedError()
    
    @property
    def length(self) -> float:
        raise NotImplementedError()
    

class ParallelLinePlacer(IAlongLinePlacer):
    
    def accumulate_candidates(self, candidates : List[aspose.gis.labeling.LabelPosition], line : Sequence[aspose.gis.common.Coordinate]) -> None:
        raise NotImplementedError()
    

class StraightenSegments:
    
    @property
    def segments(self) -> Sequence[aspose.gis.labeling.line.MeasuredLineSegment]:
        raise NotImplementedError()
    
    @property
    def longest_length(self) -> float:
        raise NotImplementedError()
    

class SymbolTetragon:
    
    def translate(self, delta : aspose.gis.common.Coordinate) -> None:
        raise NotImplementedError()
    
    @property
    def angle(self) -> float:
        raise NotImplementedError()
    
    @property
    def symbol_index(self) -> int:
        raise NotImplementedError()
    
    @property
    def tetragon(self) -> aspose.gis.labeling.Tetragon:
        raise NotImplementedError()
    

