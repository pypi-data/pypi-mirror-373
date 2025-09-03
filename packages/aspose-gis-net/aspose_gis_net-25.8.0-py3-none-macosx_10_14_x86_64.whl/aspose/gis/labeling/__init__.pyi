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

class ILabelStyle:
    
    def measure_text(self, text : str) -> aspose.gis.common.Size:
        raise NotImplementedError()
    
    def measure_text_characters(self, text : str) -> List[aspose.gis.common.Size]:
        raise NotImplementedError()
    

class Label:
    
    @property
    def text(self) -> str:
        raise NotImplementedError()
    
    @property
    def style(self) -> aspose.gis.labeling.ILabelStyle:
        raise NotImplementedError()
    
    @property
    def possible_positions(self) -> Sequence[aspose.gis.labeling.LabelPosition]:
        raise NotImplementedError()
    
    @property
    def priority(self) -> int:
        raise NotImplementedError()
    

class LabelPosition:
    
    @property
    def bounding_rectangle(self) -> aspose.gis.common.BoundingRectangle:
        raise NotImplementedError()
    
    @property
    def cost(self) -> float:
        raise NotImplementedError()
    

class LabelPositionIntersector:
    
    @staticmethod
    def intersects(position1 : aspose.gis.labeling.LabelPosition, position2 : aspose.gis.labeling.LabelPosition) -> bool:
        raise NotImplementedError()
    

class LabelsIndex:
    
    def add_label(self, label : aspose.gis.labeling.PlacedLabel) -> None:
        raise NotImplementedError()
    
    def has_intersections(self, position : aspose.gis.labeling.LabelPosition) -> bool:
        raise NotImplementedError()
    
    @property
    def count(self) -> int:
        raise NotImplementedError()
    
    @property
    def labels(self) -> Iterable[aspose.gis.labeling.PlacedLabel]:
        raise NotImplementedError()
    

class LabelsPlacer:
    
    @overload
    def add_label_to_place(self, label : aspose.gis.labeling.Label) -> None:
        raise NotImplementedError()
    
    @overload
    def add_label_to_place(self, text : str, style : aspose.gis.labeling.ILabelStyle, positions : List[aspose.gis.labeling.LabelPosition]) -> None:
        raise NotImplementedError()
    
    def place_labels(self) -> Iterable[aspose.gis.labeling.PlacedLabel]:
        raise NotImplementedError()
    

class PlacedLabel:
    
    @property
    def label(self) -> aspose.gis.labeling.Label:
        raise NotImplementedError()
    
    @property
    def position(self) -> aspose.gis.labeling.LabelPosition:
        raise NotImplementedError()
    

class SimpleLabelPosition(LabelPosition):
    
    @property
    def bounding_rectangle(self) -> aspose.gis.common.BoundingRectangle:
        raise NotImplementedError()
    
    @property
    def cost(self) -> float:
        raise NotImplementedError()
    
    @property
    def bottom_left(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @property
    def rotation(self) -> float:
        raise NotImplementedError()
    
    @property
    def bounding_tetragon(self) -> aspose.gis.labeling.Tetragon:
        raise NotImplementedError()
    

class Tetragon:
    
    def translate(self, delta : aspose.gis.common.Coordinate) -> aspose.gis.labeling.Tetragon:
        raise NotImplementedError()
    
    def intersects(self, tetragon : aspose.gis.labeling.Tetragon) -> bool:
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
    
    @property
    def angle(self) -> float:
        raise NotImplementedError()
    
    @property
    def bounding_rectangle(self) -> aspose.gis.common.BoundingRectangle:
        raise NotImplementedError()
    

