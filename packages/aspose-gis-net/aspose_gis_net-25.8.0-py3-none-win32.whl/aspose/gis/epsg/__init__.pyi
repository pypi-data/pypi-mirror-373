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

class CompoundCrsEntry:
    
    @staticmethod
    def create(name : str, horizontal_crs_code : int, vertical_crs_code : int) -> aspose.gis.epsg.CompoundCrsEntry:
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        raise NotImplementedError()
    
    @property
    def horizontal_crs_code(self) -> int:
        raise NotImplementedError()
    
    @property
    def vertical_crs_code(self) -> int:
        raise NotImplementedError()
    

class EllipsoidEntry:
    
    @staticmethod
    def create(name : str, semi_major_axis : float, inverse_flattening : float) -> aspose.gis.epsg.EllipsoidEntry:
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        raise NotImplementedError()
    
    @property
    def semi_major_axis(self) -> float:
        raise NotImplementedError()
    
    @property
    def inverse_flattening(self) -> float:
        raise NotImplementedError()
    

class EpsgDatabase:
    

class GeocentricCrsEntry:
    
    @staticmethod
    def create(name : str, unit_code : int, datum_code : int) -> aspose.gis.epsg.GeocentricCrsEntry:
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        raise NotImplementedError()
    
    @property
    def unit_code(self) -> int:
        raise NotImplementedError()
    
    @property
    def datum_code(self) -> int:
        raise NotImplementedError()
    

class GeographicCrsEntry:
    
    @staticmethod
    def create(name : str, to_wgs_84_entry_index : int, datum_code : int, unit_code : int, three_dimensional : bool, deprecated : bool) -> aspose.gis.epsg.GeographicCrsEntry:
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        raise NotImplementedError()
    
    @property
    def to_wgs_84_entry_index(self) -> int:
        raise NotImplementedError()
    
    @property
    def datum_code(self) -> int:
        raise NotImplementedError()
    
    @property
    def unit_code(self) -> int:
        raise NotImplementedError()
    
    @property
    def three_dimensional(self) -> bool:
        raise NotImplementedError()
    
    @property
    def deprecated(self) -> bool:
        raise NotImplementedError()
    

class GeographicDatumEntry:
    
    @staticmethod
    def create(name : str, ellipsoid_code : int, prime_meridian_code : int) -> aspose.gis.epsg.GeographicDatumEntry:
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        raise NotImplementedError()
    
    @property
    def ellipsoid_code(self) -> int:
        raise NotImplementedError()
    
    @property
    def prime_meridian_code(self) -> int:
        raise NotImplementedError()
    

class PrimeMeridianEntry:
    
    @staticmethod
    def create(name : str, longitude_in_degrees : float) -> aspose.gis.epsg.PrimeMeridianEntry:
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        raise NotImplementedError()
    
    @property
    def longitude_in_degrees(self) -> float:
        raise NotImplementedError()
    

class ProjectedCrsEntry:
    
    @staticmethod
    def create(name : str, geog_crs_code : int, unit_code : int, projection_method_code : int, projection_parameters_value_code : int, axises_orientation : str) -> aspose.gis.epsg.ProjectedCrsEntry:
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        raise NotImplementedError()
    
    @property
    def geographic_crs_code(self) -> int:
        raise NotImplementedError()
    
    @property
    def unit_code(self) -> int:
        raise NotImplementedError()
    
    @property
    def projection_method_code(self) -> int:
        raise NotImplementedError()
    
    @property
    def projection_parameters_value_code(self) -> int:
        raise NotImplementedError()
    
    @property
    def axises_orientation(self) -> str:
        raise NotImplementedError()
    

class ProjectionMethodEntry:
    
    @staticmethod
    def create(name : str) -> aspose.gis.epsg.ProjectionMethodEntry:
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        raise NotImplementedError()
    

class ProjectionParameterValueEntry:
    
    @staticmethod
    def create(parameter_code : int, value : float) -> aspose.gis.epsg.ProjectionParameterValueEntry:
        raise NotImplementedError()
    
    @property
    def parameter_code(self) -> int:
        raise NotImplementedError()
    
    @property
    def value(self) -> float:
        raise NotImplementedError()
    

class ToWgs84Entry:
    
    @staticmethod
    def create(dx : float, dy : float, dz : float, rx : float, ry : float, rz : float, scale : float) -> aspose.gis.epsg.ToWgs84Entry:
        raise NotImplementedError()
    
    @property
    def dx(self) -> float:
        raise NotImplementedError()
    
    @property
    def dy(self) -> float:
        raise NotImplementedError()
    
    @property
    def dz(self) -> float:
        raise NotImplementedError()
    
    @property
    def rx(self) -> float:
        raise NotImplementedError()
    
    @property
    def ry(self) -> float:
        raise NotImplementedError()
    
    @property
    def rz(self) -> float:
        raise NotImplementedError()
    
    @property
    def scale(self) -> float:
        raise NotImplementedError()
    

class UnitEntry:
    
    @staticmethod
    def create(name : str, factor : float) -> aspose.gis.epsg.UnitEntry:
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        raise NotImplementedError()
    
    @property
    def factor(self) -> float:
        raise NotImplementedError()
    

class VerticalCrsEntry:
    
    @staticmethod
    def create(name : str, unit_code : int, datum_code : int, up : bool) -> aspose.gis.epsg.VerticalCrsEntry:
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        raise NotImplementedError()
    
    @property
    def unit_code(self) -> int:
        raise NotImplementedError()
    
    @property
    def datum_code(self) -> int:
        raise NotImplementedError()
    
    @property
    def up(self) -> bool:
        raise NotImplementedError()
    

class VerticalDatumEntry:
    
    @staticmethod
    def create(name : str) -> aspose.gis.epsg.VerticalDatumEntry:
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        raise NotImplementedError()
    

