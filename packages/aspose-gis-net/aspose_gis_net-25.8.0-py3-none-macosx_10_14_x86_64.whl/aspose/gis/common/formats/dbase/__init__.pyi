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

class DBase:
    
    @overload
    @staticmethod
    def open(path : str, encoding : str) -> aspose.gis.common.formats.dbase.DBase:
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def open(path : aspose.gis.common.AbstractPathInternal, encoding : str) -> aspose.gis.common.formats.dbase.DBase:
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def create(path : str, options : aspose.gis.common.formats.dbase.DBaseOptions) -> aspose.gis.common.formats.dbase.DBase:
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def create(path : aspose.gis.common.AbstractPathInternal, options : aspose.gis.common.formats.dbase.DBaseOptions) -> aspose.gis.common.formats.dbase.DBase:
        raise NotImplementedError()
    
    @staticmethod
    def edit(path : aspose.gis.common.AbstractPathInternal, options : aspose.gis.common.formats.dbase.DBaseOptions, encoding : str) -> aspose.gis.common.formats.dbase.DBase:
        raise NotImplementedError()
    
    def add_field(self, name : str, type : str, width : int, precision : int) -> None:
        raise NotImplementedError()
    
    def read_raw(self, record_index : int, field_index : int) -> List[int]:
        raise NotImplementedError()
    
    def read_character(self, record_index : int, field_index : int) -> str:
        raise NotImplementedError()
    
    def read_integer(self, record_index : int, field_index : int, is_ignore_wrong_data : bool) -> int:
        raise NotImplementedError()
    
    def read_integer64(self, record_index : int, field_index : int, is_ignore_wrong_data : bool) -> int:
        raise NotImplementedError()
    
    def read_number(self, record_index : int, field_index : int, is_ignore_wrong_data : bool) -> float:
        raise NotImplementedError()
    
    def read_date(self, record_index : int, field_index : int, is_ignore_wrong_data : bool) -> datetime:
        raise NotImplementedError()
    
    def read_logical(self, record_index : int, field_index : int, is_ignore_wrong_data : bool) -> bool:
        raise NotImplementedError()
    
    def read_binary_integer(self, record_index : int, field_index : int) -> int:
        raise NotImplementedError()
    
    def is_null(self, record_index : int, field_index : int) -> bool:
        raise NotImplementedError()
    
    def write_character(self, record_index : int, field_index : int, value : str) -> None:
        raise NotImplementedError()
    
    def write_integer(self, record_index : int, field_index : int, value : int) -> None:
        raise NotImplementedError()
    
    def write_integer64(self, record_index : int, field_index : int, value : int) -> None:
        raise NotImplementedError()
    
    def write_number(self, record_index : int, field_index : int, value : float) -> None:
        raise NotImplementedError()
    
    def write_date(self, record_index : int, field_index : int, value : datetime) -> None:
        raise NotImplementedError()
    
    def write_logical(self, record_index : int, field_index : int, value : bool) -> None:
        raise NotImplementedError()
    
    def write_binary_integer(self, record_index : int, field_index : int, value : int) -> None:
        raise NotImplementedError()
    
    def write_binary_integer64(self, record_index : int, field_index : int, value : int) -> None:
        raise NotImplementedError()
    
    def write_binary_float(self, record_index : int, field_index : int, value : float) -> None:
        raise NotImplementedError()
    
    def write_raw_bytes(self, record_index : int, field_index : int, bytes : List[int]) -> None:
        raise NotImplementedError()
    
    def write_null(self, record_index : int, field_index : int) -> None:
        raise NotImplementedError()
    
    def add_record(self) -> int:
        raise NotImplementedError()
    
    def delete_record(self, record_index : int) -> None:
        raise NotImplementedError()
    
    def is_record_deleted(self, record_index : int) -> bool:
        raise NotImplementedError()
    
    def read_field_value(self, record_index : int, field_index : int) -> str:
        raise NotImplementedError()
    
    @property
    def fields(self) -> List[aspose.gis.common.formats.dbase.DBaseField]:
        raise NotImplementedError()
    
    @property
    def encoding(self) -> str:
        raise NotImplementedError()
    
    @property
    def records_count(self) -> int:
        raise NotImplementedError()
    

class DBaseException:
    

class DBaseField:
    
    @property
    def name(self) -> str:
        raise NotImplementedError()
    
    @property
    def type(self) -> str:
        raise NotImplementedError()
    
    @property
    def length(self) -> int:
        raise NotImplementedError()
    
    @property
    def decimals(self) -> int:
        raise NotImplementedError()
    
    @property
    def offset(self) -> int:
        raise NotImplementedError()
    

class DBaseOptions:
    
    @property
    def write_code_page_file(self) -> bool:
        raise NotImplementedError()
    
    @write_code_page_file.setter
    def write_code_page_file(self, value : bool) -> None:
        raise NotImplementedError()
    
    @property
    def is_trim_long_data(self) -> bool:
        raise NotImplementedError()
    
    @is_trim_long_data.setter
    def is_trim_long_data(self, value : bool) -> None:
        raise NotImplementedError()
    

