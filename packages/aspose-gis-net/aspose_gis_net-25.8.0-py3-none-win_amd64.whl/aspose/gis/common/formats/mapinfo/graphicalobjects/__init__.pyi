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

class Arc(GraphicalObject):
    
    @overload
    def equals(self, other : aspose.gis.common.formats.mapinfo.graphicalobjects.Arc) -> bool:
        raise NotImplementedError()
    
    @overload
    def equals(self, obj : Any) -> bool:
        raise NotImplementedError()
    
    def get_hash_code(self) -> int:
        raise NotImplementedError()
    
    @property
    def graphical_object_type(self) -> aspose.gis.common.formats.mapinfo.graphicalobjects.GraphicalObjectType:
        raise NotImplementedError()
    
    @property
    def ellipse_coordinate1(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @ellipse_coordinate1.setter
    def ellipse_coordinate1(self, value : aspose.gis.common.Coordinate) -> None:
        raise NotImplementedError()
    
    @property
    def ellipse_coordinate2(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @ellipse_coordinate2.setter
    def ellipse_coordinate2(self, value : aspose.gis.common.Coordinate) -> None:
        raise NotImplementedError()
    
    @property
    def start_angle(self) -> float:
        raise NotImplementedError()
    
    @start_angle.setter
    def start_angle(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def end_angle(self) -> float:
        raise NotImplementedError()
    
    @end_angle.setter
    def end_angle(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def pen(self) -> Optional[aspose.gis.common.formats.mapinfo.styling.Pen]:
        raise NotImplementedError()
    
    @pen.setter
    def pen(self, value : Optional[aspose.gis.common.formats.mapinfo.styling.Pen]) -> None:
        raise NotImplementedError()
    

class Ellipse(GraphicalObject):
    
    @overload
    def equals(self, other : aspose.gis.common.Ellipse) -> bool:
        raise NotImplementedError()
    
    @overload
    def equals(self, obj : Any) -> bool:
        raise NotImplementedError()
    
    def get_hash_code(self) -> int:
        raise NotImplementedError()
    
    @property
    def graphical_object_type(self) -> aspose.gis.common.formats.mapinfo.graphicalobjects.GraphicalObjectType:
        raise NotImplementedError()
    
    @property
    def coordinate1(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @coordinate1.setter
    def coordinate1(self, value : aspose.gis.common.Coordinate) -> None:
        raise NotImplementedError()
    
    @property
    def coordinate2(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @coordinate2.setter
    def coordinate2(self, value : aspose.gis.common.Coordinate) -> None:
        raise NotImplementedError()
    
    @property
    def pen(self) -> Optional[aspose.gis.common.formats.mapinfo.styling.Pen]:
        raise NotImplementedError()
    
    @pen.setter
    def pen(self, value : Optional[aspose.gis.common.formats.mapinfo.styling.Pen]) -> None:
        raise NotImplementedError()
    
    @property
    def brush(self) -> Optional[aspose.gis.common.formats.mapinfo.styling.Brush]:
        raise NotImplementedError()
    
    @brush.setter
    def brush(self, value : Optional[aspose.gis.common.formats.mapinfo.styling.Brush]) -> None:
        raise NotImplementedError()
    

class GraphicalCollection(GraphicalObject):
    
    @overload
    def equals(self, other : aspose.gis.common.formats.mapinfo.graphicalobjects.GraphicalCollection) -> bool:
        raise NotImplementedError()
    
    @overload
    def equals(self, obj : Any) -> bool:
        raise NotImplementedError()
    
    def get_hash_code(self) -> int:
        raise NotImplementedError()
    
    @property
    def graphical_object_type(self) -> aspose.gis.common.formats.mapinfo.graphicalobjects.GraphicalObjectType:
        raise NotImplementedError()
    
    @property
    def elements(self) -> List[aspose.gis.common.formats.mapinfo.graphicalobjects.GraphicalObject]:
        raise NotImplementedError()
    
    @elements.setter
    def elements(self, value : List[aspose.gis.common.formats.mapinfo.graphicalobjects.GraphicalObject]) -> None:
        raise NotImplementedError()
    

class GraphicalObject:
    
    def equals(self, other : Any) -> bool:
        raise NotImplementedError()
    
    def get_hash_code(self) -> int:
        raise NotImplementedError()
    
    @property
    def graphical_object_type(self) -> aspose.gis.common.formats.mapinfo.graphicalobjects.GraphicalObjectType:
        raise NotImplementedError()
    

class Line(GraphicalObject):
    
    @overload
    def equals(self, other : aspose.gis.common.formats.mapinfo.graphicalobjects.Line) -> bool:
        raise NotImplementedError()
    
    @overload
    def equals(self, obj : Any) -> bool:
        raise NotImplementedError()
    
    def get_hash_code(self) -> int:
        raise NotImplementedError()
    
    @property
    def graphical_object_type(self) -> aspose.gis.common.formats.mapinfo.graphicalobjects.GraphicalObjectType:
        raise NotImplementedError()
    
    @property
    def start(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @start.setter
    def start(self, value : aspose.gis.common.Coordinate) -> None:
        raise NotImplementedError()
    
    @property
    def end(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @end.setter
    def end(self, value : aspose.gis.common.Coordinate) -> None:
        raise NotImplementedError()
    
    @property
    def pen(self) -> Optional[aspose.gis.common.formats.mapinfo.styling.Pen]:
        raise NotImplementedError()
    
    @pen.setter
    def pen(self, value : Optional[aspose.gis.common.formats.mapinfo.styling.Pen]) -> None:
        raise NotImplementedError()
    

class MultiPoint(GraphicalObject):
    
    @overload
    def equals(self, other : aspose.gis.common.formats.mapinfo.graphicalobjects.MultiPoint) -> bool:
        raise NotImplementedError()
    
    @overload
    def equals(self, obj : Any) -> bool:
        raise NotImplementedError()
    
    def get_hash_code(self) -> int:
        raise NotImplementedError()
    
    @property
    def graphical_object_type(self) -> aspose.gis.common.formats.mapinfo.graphicalobjects.GraphicalObjectType:
        raise NotImplementedError()
    
    @property
    def coordinates(self) -> List[aspose.gis.common.Coordinate]:
        raise NotImplementedError()
    
    @coordinates.setter
    def coordinates(self, value : List[aspose.gis.common.Coordinate]) -> None:
        raise NotImplementedError()
    
    @property
    def symbol(self) -> Optional[aspose.gis.common.formats.mapinfo.styling.Symbol]:
        raise NotImplementedError()
    
    @symbol.setter
    def symbol(self, value : Optional[aspose.gis.common.formats.mapinfo.styling.Symbol]) -> None:
        raise NotImplementedError()
    

class None(GraphicalObject):
    
    @overload
    def equals(self, other : aspose.gis.common.formats.mapinfo.graphicalobjects.None) -> bool:
        raise NotImplementedError()
    
    @overload
    def equals(self, obj : Any) -> bool:
        raise NotImplementedError()
    
    def get_hash_code(self) -> int:
        raise NotImplementedError()
    
    @property
    def graphical_object_type(self) -> aspose.gis.common.formats.mapinfo.graphicalobjects.GraphicalObjectType:
        raise NotImplementedError()
    
    instance : aspose.gis.common.formats.mapinfo.graphicalobjects.None

class Point(GraphicalObject):
    
    @overload
    def equals(self, other : aspose.gis.common.formats.mapinfo.graphicalobjects.Point) -> bool:
        raise NotImplementedError()
    
    @overload
    def equals(self, obj : Any) -> bool:
        raise NotImplementedError()
    
    def get_hash_code(self) -> int:
        raise NotImplementedError()
    
    @property
    def graphical_object_type(self) -> aspose.gis.common.formats.mapinfo.graphicalobjects.GraphicalObjectType:
        raise NotImplementedError()
    
    @property
    def coordinate(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @coordinate.setter
    def coordinate(self, value : aspose.gis.common.Coordinate) -> None:
        raise NotImplementedError()
    
    @property
    def symbol(self) -> Optional[aspose.gis.common.formats.mapinfo.styling.Symbol]:
        raise NotImplementedError()
    
    @symbol.setter
    def symbol(self, value : Optional[aspose.gis.common.formats.mapinfo.styling.Symbol]) -> None:
        raise NotImplementedError()
    
    @property
    def symbol_id(self) -> int:
        raise NotImplementedError()
    
    @symbol_id.setter
    def symbol_id(self, value : int) -> None:
        raise NotImplementedError()
    

class Polygon:
    
    def equals(self, other : aspose.gis.common.formats.mapinfo.graphicalobjects.Polygon) -> bool:
        raise NotImplementedError()
    
    @property
    def exterior_ring(self) -> List[aspose.gis.common.Coordinate]:
        raise NotImplementedError()
    
    @exterior_ring.setter
    def exterior_ring(self, value : List[aspose.gis.common.Coordinate]) -> None:
        raise NotImplementedError()
    
    @property
    def interior_rings(self) -> Sequence[List[aspose.gis.common.Coordinate]]:
        raise NotImplementedError()
    
    @interior_rings.setter
    def interior_rings(self, value : Sequence[List[aspose.gis.common.Coordinate]]) -> None:
        raise NotImplementedError()
    

class Polyline(GraphicalObject):
    
    @overload
    def equals(self, other : aspose.gis.common.formats.mapinfo.graphicalobjects.Polyline) -> bool:
        raise NotImplementedError()
    
    @overload
    def equals(self, obj : Any) -> bool:
        raise NotImplementedError()
    
    def get_hash_code(self) -> int:
        raise NotImplementedError()
    
    @property
    def graphical_object_type(self) -> aspose.gis.common.formats.mapinfo.graphicalobjects.GraphicalObjectType:
        raise NotImplementedError()
    
    @property
    def lines(self) -> List[List[aspose.gis.common.Coordinate]]:
        raise NotImplementedError()
    
    @lines.setter
    def lines(self, value : List[List[aspose.gis.common.Coordinate]]) -> None:
        raise NotImplementedError()
    
    @property
    def pen(self) -> Optional[aspose.gis.common.formats.mapinfo.styling.Pen]:
        raise NotImplementedError()
    
    @pen.setter
    def pen(self, value : Optional[aspose.gis.common.formats.mapinfo.styling.Pen]) -> None:
        raise NotImplementedError()
    
    @property
    def smooth(self) -> bool:
        raise NotImplementedError()
    
    @smooth.setter
    def smooth(self, value : bool) -> None:
        raise NotImplementedError()
    

class Rectangle(GraphicalObject):
    
    @overload
    def equals(self, other : aspose.gis.common.Rectangle) -> bool:
        raise NotImplementedError()
    
    @overload
    def equals(self, obj : Any) -> bool:
        raise NotImplementedError()
    
    def get_hash_code(self) -> int:
        raise NotImplementedError()
    
    @property
    def graphical_object_type(self) -> aspose.gis.common.formats.mapinfo.graphicalobjects.GraphicalObjectType:
        raise NotImplementedError()
    
    @property
    def coordinate1(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @coordinate1.setter
    def coordinate1(self, value : aspose.gis.common.Coordinate) -> None:
        raise NotImplementedError()
    
    @property
    def coordinate2(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @coordinate2.setter
    def coordinate2(self, value : aspose.gis.common.Coordinate) -> None:
        raise NotImplementedError()
    
    @property
    def pen(self) -> Optional[aspose.gis.common.formats.mapinfo.styling.Pen]:
        raise NotImplementedError()
    
    @pen.setter
    def pen(self, value : Optional[aspose.gis.common.formats.mapinfo.styling.Pen]) -> None:
        raise NotImplementedError()
    
    @property
    def brush(self) -> Optional[aspose.gis.common.formats.mapinfo.styling.Brush]:
        raise NotImplementedError()
    
    @brush.setter
    def brush(self, value : Optional[aspose.gis.common.formats.mapinfo.styling.Brush]) -> None:
        raise NotImplementedError()
    

class Region(GraphicalObject):
    
    @overload
    def equals(self, other : aspose.gis.common.formats.mapinfo.graphicalobjects.Region) -> bool:
        raise NotImplementedError()
    
    @overload
    def equals(self, obj : Any) -> bool:
        raise NotImplementedError()
    
    def get_hash_code(self) -> int:
        raise NotImplementedError()
    
    @property
    def graphical_object_type(self) -> aspose.gis.common.formats.mapinfo.graphicalobjects.GraphicalObjectType:
        raise NotImplementedError()
    
    @property
    def polygons(self) -> List[aspose.gis.common.formats.mapinfo.graphicalobjects.Polygon]:
        raise NotImplementedError()
    
    @polygons.setter
    def polygons(self, value : List[aspose.gis.common.formats.mapinfo.graphicalobjects.Polygon]) -> None:
        raise NotImplementedError()
    
    @property
    def pen(self) -> Optional[aspose.gis.common.formats.mapinfo.styling.Pen]:
        raise NotImplementedError()
    
    @pen.setter
    def pen(self, value : Optional[aspose.gis.common.formats.mapinfo.styling.Pen]) -> None:
        raise NotImplementedError()
    
    @property
    def brush(self) -> Optional[aspose.gis.common.formats.mapinfo.styling.Brush]:
        raise NotImplementedError()
    
    @brush.setter
    def brush(self, value : Optional[aspose.gis.common.formats.mapinfo.styling.Brush]) -> None:
        raise NotImplementedError()
    
    @property
    def center(self) -> Optional[aspose.gis.common.Coordinate]:
        raise NotImplementedError()
    
    @center.setter
    def center(self, value : Optional[aspose.gis.common.Coordinate]) -> None:
        raise NotImplementedError()
    

class RoundedRectangle(GraphicalObject):
    
    @overload
    def equals(self, other : aspose.gis.common.formats.mapinfo.graphicalobjects.RoundedRectangle) -> bool:
        raise NotImplementedError()
    
    @overload
    def equals(self, obj : Any) -> bool:
        raise NotImplementedError()
    
    def get_hash_code(self) -> int:
        raise NotImplementedError()
    
    @property
    def graphical_object_type(self) -> aspose.gis.common.formats.mapinfo.graphicalobjects.GraphicalObjectType:
        raise NotImplementedError()
    
    @property
    def coordinate1(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @coordinate1.setter
    def coordinate1(self, value : aspose.gis.common.Coordinate) -> None:
        raise NotImplementedError()
    
    @property
    def coordinate2(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @coordinate2.setter
    def coordinate2(self, value : aspose.gis.common.Coordinate) -> None:
        raise NotImplementedError()
    
    @property
    def x_radius(self) -> float:
        raise NotImplementedError()
    
    @x_radius.setter
    def x_radius(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def y_radius(self) -> float:
        raise NotImplementedError()
    
    @y_radius.setter
    def y_radius(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def pen(self) -> Optional[aspose.gis.common.formats.mapinfo.styling.Pen]:
        raise NotImplementedError()
    
    @pen.setter
    def pen(self, value : Optional[aspose.gis.common.formats.mapinfo.styling.Pen]) -> None:
        raise NotImplementedError()
    
    @property
    def brush(self) -> Optional[aspose.gis.common.formats.mapinfo.styling.Brush]:
        raise NotImplementedError()
    
    @brush.setter
    def brush(self, value : Optional[aspose.gis.common.formats.mapinfo.styling.Brush]) -> None:
        raise NotImplementedError()
    

class Text(GraphicalObject):
    
    @overload
    def equals(self, other : aspose.gis.common.formats.mapinfo.graphicalobjects.Text) -> bool:
        raise NotImplementedError()
    
    @overload
    def equals(self, obj : Any) -> bool:
        raise NotImplementedError()
    
    def get_hash_code(self) -> int:
        raise NotImplementedError()
    
    @property
    def graphical_object_type(self) -> aspose.gis.common.formats.mapinfo.graphicalobjects.GraphicalObjectType:
        raise NotImplementedError()
    
    @property
    def text_string(self) -> str:
        raise NotImplementedError()
    
    @text_string.setter
    def text_string(self, value : str) -> None:
        raise NotImplementedError()
    
    @property
    def coordinate1(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @coordinate1.setter
    def coordinate1(self, value : aspose.gis.common.Coordinate) -> None:
        raise NotImplementedError()
    
    @property
    def coordinate2(self) -> aspose.gis.common.Coordinate:
        raise NotImplementedError()
    
    @coordinate2.setter
    def coordinate2(self, value : aspose.gis.common.Coordinate) -> None:
        raise NotImplementedError()
    

class GraphicalObjectType:
    
    NONE : GraphicalObjectType
    POINT : GraphicalObjectType
    MULTI_POINT : GraphicalObjectType
    LINE : GraphicalObjectType
    POLYLINE : GraphicalObjectType
    REGION : GraphicalObjectType
    RECTANGLE : GraphicalObjectType
    ROUNDED_RECTANGLE : GraphicalObjectType
    TEXT : GraphicalObjectType
    ELLIPSE : GraphicalObjectType
    ARC : GraphicalObjectType
    GRAPHICAL_COLLECTION : GraphicalObjectType

