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

class BinaryDataReader:
    
    @staticmethod
    def little_endian(input : io.RawIOBase, leave_open : bool) -> aspose.gis.common.io.BinaryDataReader:
        raise NotImplementedError()
    
    @staticmethod
    def big_endian(input : io.RawIOBase, leave_open : bool) -> aspose.gis.common.io.BinaryDataReader:
        raise NotImplementedError()
    
    @staticmethod
    def create(byte_order : aspose.gis.common.io.ByteOrder, input : io.RawIOBase, leave_open : bool) -> aspose.gis.common.io.BinaryDataReader:
        raise NotImplementedError()
    
    def read_byte(self) -> int:
        raise NotImplementedError()
    
    def read_s_byte(self) -> sbyte:
        raise NotImplementedError()
    
    def read_int16(self) -> int:
        raise NotImplementedError()
    
    def read_int32(self) -> int:
        raise NotImplementedError()
    
    def read_int64(self) -> int:
        raise NotImplementedError()
    
    def read_u_int16(self) -> int:
        raise NotImplementedError()
    
    def read_u_int32(self) -> int:
        raise NotImplementedError()
    
    def read_u_int64(self) -> int:
        raise NotImplementedError()
    
    def read_single(self) -> float:
        raise NotImplementedError()
    
    def read_double(self) -> float:
        raise NotImplementedError()
    
    @property
    def is_little_endian(self) -> bool:
        raise NotImplementedError()
    
    @property
    def base_stream(self) -> io.RawIOBase:
        raise NotImplementedError()
    

class BinaryDataWriter:
    
    @overload
    def write(self, value : sbyte) -> None:
        raise NotImplementedError()
    
    @overload
    def write(self, value : bool) -> None:
        raise NotImplementedError()
    
    @overload
    def write(self, value : int) -> None:
        raise NotImplementedError()
    
    @overload
    def write(self, value : int) -> None:
        raise NotImplementedError()
    
    @overload
    def write(self, value : int) -> None:
        raise NotImplementedError()
    
    @overload
    def write(self, value : float) -> None:
        raise NotImplementedError()
    
    @overload
    def write(self, value : float) -> None:
        raise NotImplementedError()
    
    @overload
    def write(self, value : int) -> None:
        raise NotImplementedError()
    
    @overload
    def write(self, value : int) -> None:
        raise NotImplementedError()
    
    @overload
    def write(self, value : int) -> None:
        raise NotImplementedError()
    
    @overload
    def write(self, value : int) -> None:
        raise NotImplementedError()
    
    @staticmethod
    def little_endian(output : io.RawIOBase, leave_open : bool) -> aspose.gis.common.io.BinaryDataWriter:
        raise NotImplementedError()
    
    @staticmethod
    def big_endian(output : io.RawIOBase, leave_open : bool) -> aspose.gis.common.io.BinaryDataWriter:
        raise NotImplementedError()
    
    @property
    def base_stream(self) -> io.RawIOBase:
        raise NotImplementedError()
    
    @property
    def is_little_endian(self) -> bool:
        raise NotImplementedError()
    

class BomStream:
    
    @property
    def bom_offset(self) -> int:
        raise NotImplementedError()
    

class BufferingReadStream:
    

class EventableStream:
    

class IndexableStreamReader:
    
    def set_split_settings(self, words : List[aspose.gis.common.formats.xml.XmlName]) -> None:
        raise NotImplementedError()
    
    def set_symbol_to_replace_illegal(self, symbol_to_replace_illegal : str) -> None:
        raise NotImplementedError()
    
    @property
    def offsets_pos(self) -> Sequence[int]:
        raise NotImplementedError()
    

class OutputBuffer:
    
    @overload
    def set_value_at(self, offset : int, value : float, is_big_endian : bool) -> None:
        raise NotImplementedError()
    
    @overload
    def set_value_at(self, offset : int, value : int, is_big_endian : bool) -> None:
        raise NotImplementedError()
    
    @overload
    def set_value_at(self, offset : int, bytes : List[int]) -> None:
        raise NotImplementedError()
    
    def reset_and_grow(self) -> None:
        raise NotImplementedError()
    
    def reset_and_fix_size(self, size_limit : int) -> None:
        raise NotImplementedError()
    
    def write_to_stream(self, stream : io.RawIOBase) -> None:
        raise NotImplementedError()
    
    @property
    def size(self) -> int:
        raise NotImplementedError()
    

class TextIndex:
    
    def read_line(self) -> str:
        raise NotImplementedError()
    
    @property
    def position(self) -> int:
        raise NotImplementedError()
    
    @position.setter
    def position(self, value : int) -> None:
        raise NotImplementedError()
    
    @property
    def end_of_stream(self) -> bool:
        raise NotImplementedError()
    

class XmlReplacedStreamReader:
    
    def set_symbol_to_replace_illegal(self, symbol_to_replace_illegal : str) -> None:
        raise NotImplementedError()
    

class ByteOrder:
    
    LITTLE_ENDIAN : ByteOrder
    BIG_ENDIAN : ByteOrder

