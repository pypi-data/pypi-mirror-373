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

class WktCompositeValue(WktValue):
    
    @overload
    def equals(self, obj : Any) -> bool:
        raise NotImplementedError()
    
    @overload
    def equals(self, composite : aspose.gis.common.formats.wkt.WktCompositeValue) -> bool:
        raise NotImplementedError()
    
    @overload
    def equals(self, other : aspose.gis.common.formats.wkt.WktValue) -> bool:
        raise NotImplementedError()
    
    @overload
    def get_composite_value(self, regular_name : str, other_name : str) -> aspose.gis.common.formats.wkt.WktCompositeValue:
        raise NotImplementedError()
    
    @overload
    def get_composite_value(self, other_names : List[str]) -> aspose.gis.common.formats.wkt.WktCompositeValue:
        raise NotImplementedError()
    
    @overload
    def get_composite_value(self, index : int) -> aspose.gis.common.formats.wkt.WktCompositeValue:
        raise NotImplementedError()
    
    @overload
    def get_composite_value(self, index : int, expected_name : str) -> aspose.gis.common.formats.wkt.WktCompositeValue:
        raise NotImplementedError()
    
    @overload
    def try_get_composite_value(self, value_name : str, value : List[aspose.gis.common.formats.wkt.WktCompositeValue]) -> bool:
        raise NotImplementedError()
    
    @overload
    def try_get_composite_value(self, index : int, output : List[aspose.gis.common.formats.wkt.WktCompositeValue]) -> bool:
        raise NotImplementedError()
    
    @overload
    def try_get_composite_value(self, index : int, expected_name : str, output : List[aspose.gis.common.formats.wkt.WktCompositeValue]) -> bool:
        raise NotImplementedError()
    
    @staticmethod
    def create(wkt : str) -> aspose.gis.common.formats.wkt.WktCompositeValue:
        raise NotImplementedError()
    
    def get_hash_code(self) -> int:
        raise NotImplementedError()
    
    def to_string(self) -> str:
        raise NotImplementedError()
    
    def get_string(self, index : int) -> str:
        raise NotImplementedError()
    
    def get_double(self, index : int) -> float:
        raise NotImplementedError()
    
    def get_integer(self, index : int) -> int:
        raise NotImplementedError()
    
    def get_or_default_integer(self, index : int, default_value : int) -> int:
        raise NotImplementedError()
    
    def get_keyword(self, index : int) -> str:
        raise NotImplementedError()
    
    def try_get_double(self, index : int, output : List[Double]) -> bool:
        raise NotImplementedError()
    
    def get_composite_value_index(self, value_name : str) -> int:
        raise NotImplementedError()
    
    @property
    def parent(self) -> aspose.gis.common.formats.wkt.WktCompositeValue:
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        raise NotImplementedError()
    
    @property
    def count(self) -> int:
        raise NotImplementedError()
    
    def __getitem__(self, key : int) -> aspose.gis.common.formats.wkt.WktValue:
        raise NotImplementedError()
    

class WktDateTime(WktValue):
    
    @overload
    def equals(self, obj : Any) -> bool:
        raise NotImplementedError()
    
    @overload
    def equals(self, other : aspose.gis.common.formats.wkt.WktValue) -> bool:
        raise NotImplementedError()
    
    @staticmethod
    def create(wkt : str) -> aspose.gis.common.formats.wkt.WktCompositeValue:
        raise NotImplementedError()
    
    def get_hash_code(self) -> int:
        raise NotImplementedError()
    
    def to_string(self) -> str:
        raise NotImplementedError()
    
    @property
    def parent(self) -> aspose.gis.common.formats.wkt.WktCompositeValue:
        raise NotImplementedError()
    
    @property
    def value(self) -> str:
        raise NotImplementedError()
    

class WktKeyword(WktValue):
    
    @overload
    def equals(self, obj : Any) -> bool:
        raise NotImplementedError()
    
    @overload
    def equals(self, other : aspose.gis.common.formats.wkt.WktValue) -> bool:
        raise NotImplementedError()
    
    @staticmethod
    def create(wkt : str) -> aspose.gis.common.formats.wkt.WktCompositeValue:
        raise NotImplementedError()
    
    def get_hash_code(self) -> int:
        raise NotImplementedError()
    
    def to_string(self) -> str:
        raise NotImplementedError()
    
    @property
    def parent(self) -> aspose.gis.common.formats.wkt.WktCompositeValue:
        raise NotImplementedError()
    
    @property
    def value(self) -> str:
        raise NotImplementedError()
    

class WktNumber(WktValue):
    
    @overload
    def equals(self, obj : Any) -> bool:
        raise NotImplementedError()
    
    @overload
    def equals(self, other : aspose.gis.common.formats.wkt.WktValue) -> bool:
        raise NotImplementedError()
    
    @staticmethod
    def create(wkt : str) -> aspose.gis.common.formats.wkt.WktCompositeValue:
        raise NotImplementedError()
    
    def get_hash_code(self) -> int:
        raise NotImplementedError()
    
    def to_string(self) -> str:
        raise NotImplementedError()
    
    @property
    def parent(self) -> aspose.gis.common.formats.wkt.WktCompositeValue:
        raise NotImplementedError()
    
    @property
    def value(self) -> float:
        raise NotImplementedError()
    

class WktString(WktValue):
    
    @overload
    def equals(self, obj : Any) -> bool:
        raise NotImplementedError()
    
    @overload
    def equals(self, other : aspose.gis.common.formats.wkt.WktValue) -> bool:
        raise NotImplementedError()
    
    @staticmethod
    def create(wkt : str) -> aspose.gis.common.formats.wkt.WktCompositeValue:
        raise NotImplementedError()
    
    def get_hash_code(self) -> int:
        raise NotImplementedError()
    
    def to_string(self) -> str:
        raise NotImplementedError()
    
    @property
    def parent(self) -> aspose.gis.common.formats.wkt.WktCompositeValue:
        raise NotImplementedError()
    
    @property
    def value(self) -> str:
        raise NotImplementedError()
    

class WktToken:
    
    def is_keyword_with_text(self, text : str) -> bool:
        raise NotImplementedError()
    
    def equals(self, other : aspose.gis.common.formats.wkt.WktToken) -> bool:
        raise NotImplementedError()
    
    @property
    def type(self) -> aspose.gis.common.formats.wkt.WktTokenType:
        raise NotImplementedError()
    
    @property
    def text(self) -> str:
        raise NotImplementedError()
    
    @property
    def position(self) -> int:
        raise NotImplementedError()
    

class WktTokenizer:
    
    def extract_next_token(self) -> None:
        raise NotImplementedError()
    
    @property
    def current_token(self) -> aspose.gis.common.formats.wkt.WktToken:
        raise NotImplementedError()
    

class WktValue:
    
    @overload
    def equals(self, other : aspose.gis.common.formats.wkt.WktValue) -> bool:
        raise NotImplementedError()
    
    @overload
    def equals(self, o : Any) -> bool:
        raise NotImplementedError()
    
    @staticmethod
    def create(wkt : str) -> aspose.gis.common.formats.wkt.WktCompositeValue:
        raise NotImplementedError()
    
    def get_hash_code(self) -> int:
        raise NotImplementedError()
    
    def to_string(self) -> str:
        raise NotImplementedError()
    
    @property
    def parent(self) -> aspose.gis.common.formats.wkt.WktCompositeValue:
        raise NotImplementedError()
    

class WktWriter:
    
    @overload
    def write_number(self, number : float) -> None:
        raise NotImplementedError()
    
    @overload
    def write_number(self, number : int) -> None:
        raise NotImplementedError()
    
    def write_composite_start(self, composite_value_name : str) -> None:
        raise NotImplementedError()
    
    def write_composite_end(self) -> None:
        raise NotImplementedError()
    
    def write_keyword(self, keyword : str) -> None:
        raise NotImplementedError()
    
    def write_string(self, string : str) -> None:
        raise NotImplementedError()
    
    @property
    def options(self) -> aspose.gis.common.formats.wkt.WktWriterOptions:
        raise NotImplementedError()
    

class WktWriterOptions:
    
    @property
    def use_square_brackets(self) -> bool:
        raise NotImplementedError()
    
    @use_square_brackets.setter
    def use_square_brackets(self, value : bool) -> None:
        raise NotImplementedError()
    
    @property
    def force_uppercase_keywords(self) -> bool:
        raise NotImplementedError()
    
    @force_uppercase_keywords.setter
    def force_uppercase_keywords(self, value : bool) -> None:
        raise NotImplementedError()
    
    @property
    def dispose_writer(self) -> bool:
        raise NotImplementedError()
    
    @dispose_writer.setter
    def dispose_writer(self, value : bool) -> None:
        raise NotImplementedError()
    

class WktTokenType:
    
    INVALID : WktTokenType
    KEYWORD : WktTokenType
    NUMBER : WktTokenType
    STRING : WktTokenType
    DATE_TIME : WktTokenType
    COMMA : WktTokenType
    OPEN : WktTokenType
    CLOSE : WktTokenType
    SEMI_COLON : WktTokenType
    EQUALS : WktTokenType
    EOF : WktTokenType

