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

class MidReader(aspose.gis.common.formats.mapinfo.IDataRowsFile):
    

class MifReader(aspose.gis.common.formats.mapinfo.IGraphcialObjectsFile):
    
    @property
    def version(self) -> int:
        raise NotImplementedError()
    
    @property
    def charset_encoding(self) -> str:
        raise NotImplementedError()
    
    @property
    def delimiter(self) -> str:
        raise NotImplementedError()
    
    @property
    def coordinate_system(self) -> aspose.gis.common.formats.mapinfo.CoordinateSystem:
        raise NotImplementedError()
    
    @property
    def columns(self) -> Sequence[aspose.gis.common.formats.mapinfo.Column]:
        raise NotImplementedError()
    
    @property
    def common_graphical_objects_type(self) -> Optional[aspose.gis.common.formats.mapinfo.graphicalobjects.GraphicalObjectType]:
        raise NotImplementedError()
    

class MifToken:
    
    @staticmethod
    def number(text : str) -> aspose.gis.common.formats.mapinfo.interchangeformat.MifToken:
        raise NotImplementedError()
    
    @staticmethod
    def string(text : str) -> aspose.gis.common.formats.mapinfo.interchangeformat.MifToken:
        raise NotImplementedError()
    
    @staticmethod
    def keyword(text : str) -> aspose.gis.common.formats.mapinfo.interchangeformat.MifToken:
        raise NotImplementedError()
    
    def is_keyword(self, keyword : str) -> bool:
        raise NotImplementedError()
    
    def equals(self, other : aspose.gis.common.formats.mapinfo.interchangeformat.MifToken) -> bool:
        raise NotImplementedError()
    
    eof : aspose.gis.common.formats.mapinfo.interchangeformat.MifToken
    open : aspose.gis.common.formats.mapinfo.interchangeformat.MifToken
    close : aspose.gis.common.formats.mapinfo.interchangeformat.MifToken
    comma : aspose.gis.common.formats.mapinfo.interchangeformat.MifToken
    newline : aspose.gis.common.formats.mapinfo.interchangeformat.MifToken
    @property
    def token_type(self) -> aspose.gis.common.formats.mapinfo.interchangeformat.MifTokenType:
        raise NotImplementedError()
    
    @property
    def text(self) -> str:
        raise NotImplementedError()
    

class MifTokenizer:
    
    @overload
    def read_token(self) -> aspose.gis.common.formats.mapinfo.interchangeformat.MifToken:
        raise NotImplementedError()
    
    @overload
    def read_token(self, expected_type : aspose.gis.common.formats.mapinfo.interchangeformat.MifTokenType, description : str) -> aspose.gis.common.formats.mapinfo.interchangeformat.MifToken:
        raise NotImplementedError()
    
    def seek(self, new_position : int, new_line_number : int) -> None:
        raise NotImplementedError()
    
    def read_double(self, description : str) -> float:
        raise NotImplementedError()
    
    def read_int(self, description : str) -> int:
        raise NotImplementedError()
    
    def read_char(self, description : str) -> str:
        raise NotImplementedError()
    
    def read_string(self, description : str) -> str:
        raise NotImplementedError()
    
    def read_keyword(self, description : str) -> str:
        raise NotImplementedError()
    
    def skip_to_new_line(self) -> None:
        raise NotImplementedError()
    
    def peek_token(self) -> aspose.gis.common.formats.mapinfo.interchangeformat.MifToken:
        raise NotImplementedError()
    
    @property
    def line_number(self) -> int:
        raise NotImplementedError()
    
    @property
    def position(self) -> int:
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        raise NotImplementedError()
    
    @encoding.setter
    def encoding(self, value : str) -> None:
        raise NotImplementedError()
    

class MifTokenType:
    
    NEWLINE : MifTokenType
    OPEN : MifTokenType
    CLOSE : MifTokenType
    COMMA : MifTokenType
    KEYWORD : MifTokenType
    STRING : MifTokenType
    NUMBER : MifTokenType
    EOF : MifTokenType

