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

class Axis:
    '''An axis describes one dimension of SRS.'''
    
    @property
    def name(self) -> str:
        '''Name of this axis.'''
        raise NotImplementedError()
    
    @property
    def direction(self) -> aspose.gis.spatialreferencing.AxisDirection:
        '''Direction of this axis.'''
        raise NotImplementedError()
    
    @property
    def is_east_west_axis(self) -> bool:
        '''Detects if direction of axis is East or West.'''
        raise NotImplementedError()
    
    @property
    def is_north_south_axis(self) -> bool:
        '''Detects if direction of axis is North or South.'''
        raise NotImplementedError()
    
    @property
    def is_up_down_axis(self) -> bool:
        '''Detects if direction of axis is Up or Down.'''
        raise NotImplementedError()
    
    @property
    def is_other_axis(self) -> bool:
        '''Detects if this axis direction is Other.'''
        raise NotImplementedError()
    

class BursaWolfParameters:
    '''Class that contains parameters of Bursa-Wolf formula to transform to another datum.'''
    
    def equals(self, other : aspose.gis.spatialreferencing.BursaWolfParameters) -> bool:
        '''Indicates whether the current object is equal to another object of the same type.
        
        :param other: An object to compare with this object.
        :returns: true if the current object is equal to the ``other`` parameter; otherwise, false.'''
        raise NotImplementedError()
    
    null : aspose.gis.spatialreferencing.BursaWolfParameters
    '''Special value, indicating that parameters are unknown.'''
    @property
    def dx(self) -> float:
        '''Dx in meters.'''
        raise NotImplementedError()
    
    @property
    def dy(self) -> float:
        '''Dy in meters.'''
        raise NotImplementedError()
    
    @property
    def dz(self) -> float:
        '''Dz in meters.'''
        raise NotImplementedError()
    
    @property
    def rx(self) -> float:
        '''Rx in seconds.'''
        raise NotImplementedError()
    
    @property
    def ry(self) -> float:
        '''Ry in seconds.'''
        raise NotImplementedError()
    
    @property
    def rz(self) -> float:
        '''Rz in seconds.'''
        raise NotImplementedError()
    
    @property
    def scale(self) -> float:
        '''Scale in parts per million.'''
        raise NotImplementedError()
    
    @property
    def is_null(self) -> bool:
        '''Determine whether this instance is :py:attr:`aspose.gis.spatialreferencing.BursaWolfParameters.null`.'''
        raise NotImplementedError()
    

class CompoundSpatialReferenceSystem(SpatialReferenceSystem):
    '''Compound SRS unites two underlying SRS, none of which can be compound.'''
    
    @overload
    def is_equivalent(self, other : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> bool:
        '''Detects whether this SRS is equivalent to other SRS. :py:func:`aspose.gis.spatialreferencing.SpatialReferenceSystem.is_equivalent`.
        
        :param other: Other SRS.
        :returns: bool value, indicating whether this SRS is equivalent to other SRS.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def is_equivalent(srs1 : aspose.gis.spatialreferencing.SpatialReferenceSystem, srs2 : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> bool:
        '''Determines if two SRS are equivalent.
        Same coordinates of equivalent SRS match same place on Earth.
        Some parameters of equivalent SRS can be different, for example :py:attr:`aspose.gis.spatialreferencing.IdentifiableObject.name`.
        
        :param srs1: First SRS.
        :param srs2: Second SRS.
        :returns: bool value, indicating whether two SRS are equivalent.'''
        raise NotImplementedError()
    
    @staticmethod
    def try_create_from_wkt(wkt : str, value : List[aspose.gis.spatialreferencing.SpatialReferenceSystem]) -> bool:
        '''Creates a new ``SpatialReferenceSystem`` based on WKT (Well-Known Text) string.
        
        :param wkt: WKT string.
        :param value: When this methods returns , contains an SRS created from WKT; otherwise,
        contains .
        :returns: if SRS was successfully created;  otherwise.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_from_wkt(wkt : str) -> aspose.gis.spatialreferencing.SpatialReferenceSystem:
        '''Creates a new ``SpatialReferenceSystem`` based on WKT (Well-Known Text) string.
        
        :param wkt: WKT string.
        :returns: New ``SpatialReferenceSystem``.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_from_epsg(epsg : int) -> aspose.gis.spatialreferencing.SpatialReferenceSystem:
        '''Create a spatial reference system based the specified EPSG code.
        
        :param epsg: EPSG code of the spatial reference system.
        :returns: A new spatial reference system with the specified EPSG code.'''
        raise NotImplementedError()
    
    @staticmethod
    def try_create_from_epsg(epsg : int, value : List[aspose.gis.spatialreferencing.SpatialReferenceSystem]) -> bool:
        '''Create a spatial reference system based the specified EPSG code.
        
        :param epsg: EPSG code of the spatial reference system.
        :param value: When this methods returns , contains a SRS with the specified EPSG code; otherwise,
        contains .
        :returns: if specified EPSG code is known and SRS was created;  otherwise.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_geographic(parameters : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystemParameters, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem:
        '''Create geographic SRS from custom parameters.
        
        :param parameters: Parameters to create from.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Geographic SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_geocentric(parameters : aspose.gis.spatialreferencing.GeocentricSpatialReferenceSystemParameters, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.GeocentricSpatialReferenceSystem:
        '''Create geocentric SRS from custom parameters.
        
        :param parameters: Parameters to create from.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Geocentric SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_projected(parameters : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystemParameters, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem:
        '''Create projected SRS from custom parameters.
        
        :param parameters: Parameters to create from.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Projected SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_vertical(name : str, vertical_datum : aspose.gis.spatialreferencing.VerticalDatum, vertical_unit : aspose.gis.rendering.Unit, vertical_axis : aspose.gis.spatialreferencing.Axis, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.VerticalSpatialReferenceSystem:
        '''Create vertical SRS.
        
        :param name: Name of SRS. If .
        :param vertical_datum: Datum to be used in SRS.
        :param vertical_unit: Unit to be used in SRS. If , :py:attr:`aspose.gis.spatialreferencing.Unit.meter` will be used.
        :param vertical_axis: Axis with "up" or "down" direction, to be used in SRS. If , axis with up direction will be used.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Vertical SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_compound(name : str, head : aspose.gis.spatialreferencing.SpatialReferenceSystem, tail : aspose.gis.spatialreferencing.SpatialReferenceSystem, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.CompoundSpatialReferenceSystem:
        '''Create compound SRS.
        
        :param name: Name of new SRS.
        :param head: Head SRS of new SRS.
        :param tail: Tail SRS of new SRS.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Compound SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_local(name : str, datum : aspose.gis.spatialreferencing.LocalDatum, unit : aspose.gis.rendering.Unit, axises : List[aspose.gis.spatialreferencing.Axis], identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.LocalSpatialReferenceSystem:
        raise NotImplementedError()
    
    def validate(self, error_message : List[String]) -> bool:
        '''Determine if this SRS is valid. See :py:func:`aspose.gis.spatialreferencing.SpatialReferenceSystem.validate` for validity description.
        
        :param error_message: Description of invalidity (if result is )
        :returns: If this SRS is valid - , otherwise - .'''
        raise NotImplementedError()
    
    def get_axis(self, dimension : int) -> aspose.gis.spatialreferencing.Axis:
        '''Get :py:class:`aspose.gis.spatialreferencing.Axis` that describes dimension.
        
        :param dimension: Number of dimension.
        :returns: Axis that describes dimension.'''
        raise NotImplementedError()
    
    def get_unit(self, dimension : int) -> aspose.gis.rendering.Unit:
        '''Get :py:class:`aspose.gis.spatialreferencing.Unit` of dimension.
        
        :param dimension: Number of dimension.
        :returns: Unit of dimension.'''
        raise NotImplementedError()
    
    def export_to_wkt(self) -> str:
        '''Returns representation of this SRS as WKT string.
        The result WKT string will match OGC 01-009 specification, usually named "WKT1".
        
        :returns: WKT representation of this SRS.'''
        raise NotImplementedError()
    
    def try_create_transformation_to(self, target_srs : aspose.gis.spatialreferencing.SpatialReferenceSystem, value : List[aspose.gis.spatialreferencing.SpatialReferenceSystemTransformation]) -> bool:
        '''Creates transformation from this ``SpatialReferenceSystem`` to another ``SpatialReferenceSystem``.
        
        :param target_srs: Another ``SpatialReferenceSystem``.
        :param value: When this methods returns , contains a transformation; otherwise, contains .
        :returns: Transformation from this ``SpatialReferenceSystem`` to another ``SpatialReferenceSystem``.
        :returns: if transformation was created successfully;  otherwise.'''
        raise NotImplementedError()
    
    def create_transformation_to(self, target_srs : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> aspose.gis.spatialreferencing.SpatialReferenceSystemTransformation:
        '''Creates transformation from this ``SpatialReferenceSystem`` to another ``SpatialReferenceSystem``.
        
        :param target_srs: Another ``SpatialReferenceSystem``.
        :returns: Transformation from this ``SpatialReferenceSystem`` to another ``SpatialReferenceSystem``.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Name of this object.'''
        raise NotImplementedError()
    
    @property
    def epsg_code(self) -> int:
        '''If this objects identifier is EPSG identifier - return its code. Otherwise - return -1.'''
        raise NotImplementedError()
    
    @property
    def identifier(self) -> aspose.gis.spatialreferencing.Identifier:
        '''Identifier of this identifiable object.'''
        raise NotImplementedError()
    
    wgs84 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''WGS 84 (EPSG:4326) spatial reference system.'''
    web_mercator : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem
    '''Web Mercator (EPSG:3857) spatial reference system.'''
    wgs72 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''WGS 72 (EPSG:4322) spatial reference system.'''
    nad83 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''NAD 83 (EPSG:4269) spatial reference system.'''
    etrs89 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''ETRS 89 (EPSG:4258) spatial reference system.'''
    etrs_89_lambert_conformal_conic : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem
    '''ETRS 89 / Lambert Conformal Conic (EPSG:3034) spatial reference system.'''
    etrs_89_lambert_azimuthal_equal_area : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem
    '''ETRS 89 / ETRS Lambert Azimuthal Equal Area (EPSG:3035) spatial reference system.'''
    osgb36 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''OSGB 36 (EPSG:4277) spatial reference system.'''
    osgb_36_british_national_grid : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem
    '''OSGB 36 / British National Grid (EPSG:27700) spatial reference system.'''
    @property
    def is_valid(self) -> bool:
        '''Same as :py:func:`aspose.gis.spatialreferencing.SpatialReferenceSystem.validate`, but don\'t return error message.'''
        raise NotImplementedError()
    
    @property
    def type(self) -> aspose.gis.spatialreferencing.SpatialReferenceSystemType:
        '''Type of this Compound SRS. Can be :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystemType.GEOGRAPHIC` if
        this Compound SRS is combination of geographic and vertical SRS, or :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystemType.PROJECTED` if
        this Compound SRS is combination of projected and vertical SRS.'''
        raise NotImplementedError()
    
    @property
    def is_compound(self) -> bool:
        '''Returns .'''
        raise NotImplementedError()
    
    @property
    def is_single(self) -> bool:
        '''Returns whether this SRS is single (not a union of two SRS).'''
        raise NotImplementedError()
    
    @property
    def as_geographic(self) -> aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem:
        '''Return geographic representation of this SRS. If this compound SRS indeed represents a geographic SRS, the result will
        be three dimensional geographic SRS (with longitude, latitude, height dimensions). Otherwise an exception will be thrown.'''
        raise NotImplementedError()
    
    @property
    def as_projected(self) -> aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem:
        '''Return projected representation of this SRS. If this compound SRS indeed represents a projected SRS, the result will
        be three dimensional projected SRS (with X, Y, height dimensions). Otherwise an exception will be thrown.'''
        raise NotImplementedError()
    
    @property
    def as_geocentric(self) -> aspose.gis.spatialreferencing.GeocentricSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.GeocentricSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.type` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def as_vertical(self) -> aspose.gis.spatialreferencing.VerticalSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.VerticalSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.type` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def as_local(self) -> aspose.gis.spatialreferencing.LocalSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.LocalSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.type` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def as_compound(self) -> aspose.gis.spatialreferencing.CompoundSpatialReferenceSystem:
        '''Return this.'''
        raise NotImplementedError()
    
    @property
    def dimensions_count(self) -> int:
        '''Number of dimensions. For compound SRS this is sum of number of dimensions of underlying SRS.'''
        raise NotImplementedError()
    
    @property
    def has_prime_meridian(self) -> bool:
        '''Compound SRS has prime meridian if any of underlying SRS have prime meridian.'''
        raise NotImplementedError()
    
    @property
    def prime_meridian(self) -> aspose.gis.spatialreferencing.PrimeMeridian:
        '''Return prime meridian of this SRS.
        If both :py:attr:`aspose.gis.spatialreferencing.CompoundSpatialReferenceSystem.head` and :py:attr:`aspose.gis.spatialreferencing.CompoundSpatialReferenceSystem.tail` have prime meridian - return prime meridian of head.'''
        raise NotImplementedError()
    
    @property
    def has_geographic_datum(self) -> bool:
        '''Compound SRS have geographic datum if any of underlying SRS have geographic datum.'''
        raise NotImplementedError()
    
    @property
    def geographic_datum(self) -> aspose.gis.spatialreferencing.GeographicDatum:
        '''Return geographic datum of this SRS.
        If both :py:attr:`aspose.gis.spatialreferencing.CompoundSpatialReferenceSystem.head` and :py:attr:`aspose.gis.spatialreferencing.CompoundSpatialReferenceSystem.tail` have geographic datum - return geographic datum of head.'''
        raise NotImplementedError()
    
    @property
    def head(self) -> aspose.gis.spatialreferencing.SpatialReferenceSystem:
        '''First underlying SRS.'''
        raise NotImplementedError()
    
    @property
    def tail(self) -> aspose.gis.spatialreferencing.SpatialReferenceSystem:
        '''Second underlying SRS.'''
        raise NotImplementedError()
    

class Ellipsoid(IdentifiableObject):
    '''Ellipsoid represents an ellipsoid, which approximates earth.'''
    
    @overload
    @staticmethod
    def is_equivalent(ellipsoid1 : aspose.gis.spatialreferencing.Ellipsoid, ellipsoid2 : aspose.gis.spatialreferencing.Ellipsoid) -> bool:
        '''Determines if two ellipsoids are equivalent.
        If ellipsoid A is equivalent to ellipsoid B, then they have same semi major axis and inverse flattening.
        
        :param ellipsoid1: First ellipsoid.
        :param ellipsoid2: Second ellipsoid.
        :returns: bool value, indicating whether two ellipsoids are equivalent.'''
        raise NotImplementedError()
    
    @overload
    def is_equivalent(self, other : aspose.gis.spatialreferencing.Ellipsoid) -> bool:
        '''Determines if two ellipsoids are equivalent.
        If ellipsoid A is equivalent to ellipsoid B, then they have same semi major axis and inverse flattening.
        
        :param other: Other ellipsoid.
        :returns: bool value, indicating whether two ellipsoids are equivalent.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Name of this object.'''
        raise NotImplementedError()
    
    @property
    def epsg_code(self) -> int:
        '''If this objects identifier is EPSG identifier - return its code. Otherwise - return -1.'''
        raise NotImplementedError()
    
    @property
    def identifier(self) -> aspose.gis.spatialreferencing.Identifier:
        '''Identifier of this identifiable object.'''
        raise NotImplementedError()
    
    wgs84 : aspose.gis.spatialreferencing.Ellipsoid
    '''WGS 84 Ellipsoid.'''
    wgs72 : aspose.gis.spatialreferencing.Ellipsoid
    '''WGS 72 Ellipsoid.'''
    grs80 : aspose.gis.spatialreferencing.Ellipsoid
    '''GRS 1980 Ellipsoid.'''
    airy : aspose.gis.spatialreferencing.Ellipsoid
    '''Airy ellipsoid.'''
    @property
    def is_valid(self) -> bool:
        '''Detects whether ellipsoid is valid: its semi major axis is more then 0 and inverse flattening is positive or equal to 0.'''
        raise NotImplementedError()
    
    @property
    def is_sphere(self) -> bool:
        '''Detects whether this ellipsoid is a sphere.'''
        raise NotImplementedError()
    
    @property
    def semi_major_axis(self) -> float:
        '''Semi major axis of ellipsoid.'''
        raise NotImplementedError()
    
    @property
    def inverse_flattening(self) -> float:
        '''Inverse flattening of ellipsoid. 0 if this is a sphere.'''
        raise NotImplementedError()
    
    @property
    def semi_minor_axis(self) -> float:
        '''Semi minor axis of ellipsoid. Equals to semi major axis if this is a sphere.'''
        raise NotImplementedError()
    

class GeocentricSpatialReferenceSystem(SpatialReferenceSystem):
    '''Geocentric SRS is 3 dimensional cartesian SRS with origin at earth center.'''
    
    @overload
    @staticmethod
    def is_equivalent(srs1 : aspose.gis.spatialreferencing.SpatialReferenceSystem, srs2 : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> bool:
        '''Determines if two SRS are equivalent.
        Same coordinates of equivalent SRS match same place on Earth.
        Some parameters of equivalent SRS can be different, for example :py:attr:`aspose.gis.spatialreferencing.IdentifiableObject.name`.
        
        :param srs1: First SRS.
        :param srs2: Second SRS.
        :returns: bool value, indicating whether two SRS are equivalent.'''
        raise NotImplementedError()
    
    @overload
    def is_equivalent(self, other : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> bool:
        '''Detects whether this SRS is equivalent to other SRS. :py:func:`aspose.gis.spatialreferencing.SpatialReferenceSystem.is_equivalent`.
        
        :param other: Other SRS.
        :returns: bool value, indicating whether this SRS is equivalent to other SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def try_create_from_wkt(wkt : str, value : List[aspose.gis.spatialreferencing.SpatialReferenceSystem]) -> bool:
        '''Creates a new ``SpatialReferenceSystem`` based on WKT (Well-Known Text) string.
        
        :param wkt: WKT string.
        :param value: When this methods returns , contains an SRS created from WKT; otherwise,
        contains .
        :returns: if SRS was successfully created;  otherwise.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_from_wkt(wkt : str) -> aspose.gis.spatialreferencing.SpatialReferenceSystem:
        '''Creates a new ``SpatialReferenceSystem`` based on WKT (Well-Known Text) string.
        
        :param wkt: WKT string.
        :returns: New ``SpatialReferenceSystem``.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_from_epsg(epsg : int) -> aspose.gis.spatialreferencing.SpatialReferenceSystem:
        '''Create a spatial reference system based the specified EPSG code.
        
        :param epsg: EPSG code of the spatial reference system.
        :returns: A new spatial reference system with the specified EPSG code.'''
        raise NotImplementedError()
    
    @staticmethod
    def try_create_from_epsg(epsg : int, value : List[aspose.gis.spatialreferencing.SpatialReferenceSystem]) -> bool:
        '''Create a spatial reference system based the specified EPSG code.
        
        :param epsg: EPSG code of the spatial reference system.
        :param value: When this methods returns , contains a SRS with the specified EPSG code; otherwise,
        contains .
        :returns: if specified EPSG code is known and SRS was created;  otherwise.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_geographic(parameters : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystemParameters, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem:
        '''Create geographic SRS from custom parameters.
        
        :param parameters: Parameters to create from.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Geographic SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_geocentric(parameters : aspose.gis.spatialreferencing.GeocentricSpatialReferenceSystemParameters, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.GeocentricSpatialReferenceSystem:
        '''Create geocentric SRS from custom parameters.
        
        :param parameters: Parameters to create from.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Geocentric SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_projected(parameters : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystemParameters, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem:
        '''Create projected SRS from custom parameters.
        
        :param parameters: Parameters to create from.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Projected SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_vertical(name : str, vertical_datum : aspose.gis.spatialreferencing.VerticalDatum, vertical_unit : aspose.gis.rendering.Unit, vertical_axis : aspose.gis.spatialreferencing.Axis, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.VerticalSpatialReferenceSystem:
        '''Create vertical SRS.
        
        :param name: Name of SRS. If .
        :param vertical_datum: Datum to be used in SRS.
        :param vertical_unit: Unit to be used in SRS. If , :py:attr:`aspose.gis.spatialreferencing.Unit.meter` will be used.
        :param vertical_axis: Axis with "up" or "down" direction, to be used in SRS. If , axis with up direction will be used.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Vertical SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_compound(name : str, head : aspose.gis.spatialreferencing.SpatialReferenceSystem, tail : aspose.gis.spatialreferencing.SpatialReferenceSystem, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.CompoundSpatialReferenceSystem:
        '''Create compound SRS.
        
        :param name: Name of new SRS.
        :param head: Head SRS of new SRS.
        :param tail: Tail SRS of new SRS.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Compound SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_local(name : str, datum : aspose.gis.spatialreferencing.LocalDatum, unit : aspose.gis.rendering.Unit, axises : List[aspose.gis.spatialreferencing.Axis], identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.LocalSpatialReferenceSystem:
        raise NotImplementedError()
    
    def validate(self, error_message : List[String]) -> bool:
        '''Determine if this SRS is valid. See :py:func:`aspose.gis.spatialreferencing.SpatialReferenceSystem.validate` for validity description.
        
        :param error_message: Description of invalidity (if result is )
        :returns: If this SRS is valid - , otherwise - .'''
        raise NotImplementedError()
    
    def get_axis(self, dimension : int) -> aspose.gis.spatialreferencing.Axis:
        '''Get :py:class:`aspose.gis.spatialreferencing.Axis` that describes dimension.
        
        :param dimension: Number of dimension.
        :returns: Axis that describes dimension.'''
        raise NotImplementedError()
    
    def get_unit(self, dimension : int) -> aspose.gis.rendering.Unit:
        '''Get :py:class:`aspose.gis.spatialreferencing.Unit` of dimension.
        
        :param dimension: Number of dimension.
        :returns: Unit of dimension.'''
        raise NotImplementedError()
    
    def export_to_wkt(self) -> str:
        '''Returns representation of this SRS as WKT string.
        The result WKT string will match OGC 01-009 specification, usually named "WKT1".
        
        :returns: WKT representation of this SRS.'''
        raise NotImplementedError()
    
    def try_create_transformation_to(self, target_srs : aspose.gis.spatialreferencing.SpatialReferenceSystem, value : List[aspose.gis.spatialreferencing.SpatialReferenceSystemTransformation]) -> bool:
        '''Creates transformation from this ``SpatialReferenceSystem`` to another ``SpatialReferenceSystem``.
        
        :param target_srs: Another ``SpatialReferenceSystem``.
        :param value: When this methods returns , contains a transformation; otherwise, contains .
        :returns: Transformation from this ``SpatialReferenceSystem`` to another ``SpatialReferenceSystem``.
        :returns: if transformation was created successfully;  otherwise.'''
        raise NotImplementedError()
    
    def create_transformation_to(self, target_srs : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> aspose.gis.spatialreferencing.SpatialReferenceSystemTransformation:
        '''Creates transformation from this ``SpatialReferenceSystem`` to another ``SpatialReferenceSystem``.
        
        :param target_srs: Another ``SpatialReferenceSystem``.
        :returns: Transformation from this ``SpatialReferenceSystem`` to another ``SpatialReferenceSystem``.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Name of this object.'''
        raise NotImplementedError()
    
    @property
    def epsg_code(self) -> int:
        '''If this objects identifier is EPSG identifier - return its code. Otherwise - return -1.'''
        raise NotImplementedError()
    
    @property
    def identifier(self) -> aspose.gis.spatialreferencing.Identifier:
        '''Identifier of this identifiable object.'''
        raise NotImplementedError()
    
    wgs84 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''WGS 84 (EPSG:4326) spatial reference system.'''
    web_mercator : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem
    '''Web Mercator (EPSG:3857) spatial reference system.'''
    wgs72 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''WGS 72 (EPSG:4322) spatial reference system.'''
    nad83 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''NAD 83 (EPSG:4269) spatial reference system.'''
    etrs89 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''ETRS 89 (EPSG:4258) spatial reference system.'''
    etrs_89_lambert_conformal_conic : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem
    '''ETRS 89 / Lambert Conformal Conic (EPSG:3034) spatial reference system.'''
    etrs_89_lambert_azimuthal_equal_area : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem
    '''ETRS 89 / ETRS Lambert Azimuthal Equal Area (EPSG:3035) spatial reference system.'''
    osgb36 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''OSGB 36 (EPSG:4277) spatial reference system.'''
    osgb_36_british_national_grid : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem
    '''OSGB 36 / British National Grid (EPSG:27700) spatial reference system.'''
    @property
    def is_valid(self) -> bool:
        '''Same as :py:func:`aspose.gis.spatialreferencing.SpatialReferenceSystem.validate`, but don\'t return error message.'''
        raise NotImplementedError()
    
    @property
    def type(self) -> aspose.gis.spatialreferencing.SpatialReferenceSystemType:
        '''Return :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystemType.GEOCENTRIC`.'''
        raise NotImplementedError()
    
    @property
    def is_compound(self) -> bool:
        '''Returns whether this SRS is compound (a union of two SRS).
        Following combinations of SRS in compound SRS are considered valid:
        Geographic SRS + Vertical SRS, in this case type of compound SRS will be :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystemType.GEOGRAPHIC`.
        Projected SRS + Vertical SRS, in this case type of compound SRS will be :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystemType.PROJECTED`.
        If combination of SRSs differs, type of compound SRS will be :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystemType.UNKNOWN`.'''
        raise NotImplementedError()
    
    @property
    def is_single(self) -> bool:
        '''Returns whether this SRS is single (not a union of two SRS).'''
        raise NotImplementedError()
    
    @property
    def as_geographic(self) -> aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.type` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def as_projected(self) -> aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.type` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def as_geocentric(self) -> aspose.gis.spatialreferencing.GeocentricSpatialReferenceSystem:
        '''Return this.'''
        raise NotImplementedError()
    
    @property
    def as_vertical(self) -> aspose.gis.spatialreferencing.VerticalSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.VerticalSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.type` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def as_local(self) -> aspose.gis.spatialreferencing.LocalSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.LocalSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.type` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def as_compound(self) -> aspose.gis.spatialreferencing.CompoundSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.CompoundSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.is_compound` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def dimensions_count(self) -> int:
        '''Return 3, since geocentric SRS is always three dimensional.'''
        raise NotImplementedError()
    
    @property
    def has_prime_meridian(self) -> bool:
        '''Return , since geocentric SRS always have prime meridian.'''
        raise NotImplementedError()
    
    @property
    def prime_meridian(self) -> aspose.gis.spatialreferencing.PrimeMeridian:
        '''Return prime meridian of this SRS.'''
        raise NotImplementedError()
    
    @property
    def has_geographic_datum(self) -> bool:
        '''Return , since geocentric SRS always have geographic datum.'''
        raise NotImplementedError()
    
    @property
    def geographic_datum(self) -> aspose.gis.spatialreferencing.GeographicDatum:
        '''Return geographic datum of this SRS.'''
        raise NotImplementedError()
    
    @property
    def linear_unit(self) -> aspose.gis.rendering.Unit:
        '''Unit, used in this SRS.'''
        raise NotImplementedError()
    
    @property
    def axises_order(self) -> aspose.gis.spatialreferencing.GeocentricAxisesOrder:
        '''Order of axises in this SRS.
        If this SRS is not valid and has wrong axises directions, :py:attr:`aspose.gis.spatialreferencing.GeocentricAxisesOrder.INVALID` is returned.'''
        raise NotImplementedError()
    

class GeocentricSpatialReferenceSystemParameters:
    '''Parameters to create geocentric SRS.
    Parameters have reasonable defaults, so you will have to assign only some of them.
    If you assign  to any parameter, a default value will be used.'''
    
    @property
    def name(self) -> str:
        '''Name of geocentric SRS. Default is "Unnamed".'''
        raise NotImplementedError()
    
    @name.setter
    def name(self, value : str) -> None:
        '''Name of geocentric SRS. Default is "Unnamed".'''
        raise NotImplementedError()
    
    @property
    def datum(self) -> aspose.gis.spatialreferencing.GeographicDatum:
        '''Datum of geocentric SRS. Default is :py:attr:`aspose.gis.spatialreferencing.GeographicDatum.wgs84`.'''
        raise NotImplementedError()
    
    @datum.setter
    def datum(self, value : aspose.gis.spatialreferencing.GeographicDatum) -> None:
        '''Datum of geocentric SRS. Default is :py:attr:`aspose.gis.spatialreferencing.GeographicDatum.wgs84`.'''
        raise NotImplementedError()
    
    @property
    def prime_meridian(self) -> aspose.gis.spatialreferencing.PrimeMeridian:
        '''Prime meridian of this SRS. Default is :py:attr:`aspose.gis.spatialreferencing.PrimeMeridian.greenwich`.'''
        raise NotImplementedError()
    
    @prime_meridian.setter
    def prime_meridian(self, value : aspose.gis.spatialreferencing.PrimeMeridian) -> None:
        '''Prime meridian of this SRS. Default is :py:attr:`aspose.gis.spatialreferencing.PrimeMeridian.greenwich`.'''
        raise NotImplementedError()
    
    @property
    def linear_unit(self) -> aspose.gis.rendering.Unit:
        '''Units to be used in this SRS. Defaults to :py:attr:`aspose.gis.spatialreferencing.Unit.meter`.'''
        raise NotImplementedError()
    
    @linear_unit.setter
    def linear_unit(self, value : aspose.gis.rendering.Unit) -> None:
        '''Units to be used in this SRS. Defaults to :py:attr:`aspose.gis.spatialreferencing.Unit.meter`.'''
        raise NotImplementedError()
    
    @property
    def x_axis(self) -> aspose.gis.spatialreferencing.Axis:
        '''Axis of geocentric SRS that describes \'X\' dimension (axis that points at prime meridian).'''
        raise NotImplementedError()
    
    @x_axis.setter
    def x_axis(self, value : aspose.gis.spatialreferencing.Axis) -> None:
        '''Axis of geocentric SRS that describes \'X\' dimension (axis that points at prime meridian).'''
        raise NotImplementedError()
    
    @property
    def y_axis(self) -> aspose.gis.spatialreferencing.Axis:
        '''Axis of geocentric SRS that describes \'Y\' dimension (axis that points to the left or to the right of X axis on equatorial plane).
        Defaults to axis with :py:attr:`aspose.gis.spatialreferencing.AxisDirection.EAST` direction.'''
        raise NotImplementedError()
    
    @y_axis.setter
    def y_axis(self, value : aspose.gis.spatialreferencing.Axis) -> None:
        '''Axis of geocentric SRS that describes \'Y\' dimension (axis that points to the left or to the right of X axis on equatorial plane).
        Defaults to axis with :py:attr:`aspose.gis.spatialreferencing.AxisDirection.EAST` direction.'''
        raise NotImplementedError()
    
    @property
    def z_axis(self) -> aspose.gis.spatialreferencing.Axis:
        '''Axis of geocentric SRS that describes \'Z\' dimension (axis that points to the north or south pole).
        Defaults to axis with :py:attr:`aspose.gis.spatialreferencing.AxisDirection.NORTH` direction.'''
        raise NotImplementedError()
    
    @z_axis.setter
    def z_axis(self, value : aspose.gis.spatialreferencing.Axis) -> None:
        '''Axis of geocentric SRS that describes \'Z\' dimension (axis that points to the north or south pole).
        Defaults to axis with :py:attr:`aspose.gis.spatialreferencing.AxisDirection.NORTH` direction.'''
        raise NotImplementedError()
    
    @property
    def axises_order(self) -> aspose.gis.spatialreferencing.GeocentricAxisesOrder:
        '''Order of axises. Defaults to :py:attr:`aspose.gis.spatialreferencing.GeocentricAxisesOrder.XYZ`.'''
        raise NotImplementedError()
    
    @axises_order.setter
    def axises_order(self, value : aspose.gis.spatialreferencing.GeocentricAxisesOrder) -> None:
        '''Order of axises. Defaults to :py:attr:`aspose.gis.spatialreferencing.GeocentricAxisesOrder.XYZ`.'''
        raise NotImplementedError()
    

class GeographicDatum(IdentifiableObject):
    '''Geographic datum relates longitude and latitude to particular place on earth.'''
    
    @overload
    @staticmethod
    def is_equivalent(datum1 : aspose.gis.spatialreferencing.GeographicDatum, datum2 : aspose.gis.spatialreferencing.GeographicDatum) -> bool:
        '''Determines if two datums are equivalent.
        Same coordinates of equivalent datums match same place on Earth.
        Some parameters of equivalent datums can be different, for example :py:attr:`aspose.gis.spatialreferencing.IdentifiableObject.name`.
        
        :param datum1: First datum.
        :param datum2: Second datum.
        :returns: bool value, indicating whether two datums are equivalent.'''
        raise NotImplementedError()
    
    @overload
    def is_equivalent(self, other : aspose.gis.spatialreferencing.GeographicDatum) -> bool:
        '''Determines if two datums are equivalent.
        Same coordinates of equivalent datums match same place on Earth.
        Some parameters of equivalent datums can be different, for example :py:attr:`aspose.gis.spatialreferencing.IdentifiableObject.name`.
        
        :param other: Other datum.
        :returns: bool value, indicating whether two datums are equivalent.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Name of this object.'''
        raise NotImplementedError()
    
    @property
    def epsg_code(self) -> int:
        '''If this objects identifier is EPSG identifier - return its code. Otherwise - return -1.'''
        raise NotImplementedError()
    
    @property
    def identifier(self) -> aspose.gis.spatialreferencing.Identifier:
        '''Identifier of this identifiable object.'''
        raise NotImplementedError()
    
    wgs84 : aspose.gis.spatialreferencing.GeographicDatum
    '''WGS 84 datum.'''
    wgs72 : aspose.gis.spatialreferencing.GeographicDatum
    '''WGS 72 datum.'''
    nad83 : aspose.gis.spatialreferencing.GeographicDatum
    '''NAD 83 datum.'''
    etrs89 : aspose.gis.spatialreferencing.GeographicDatum
    '''ETRS 89 datum.'''
    osgb36 : aspose.gis.spatialreferencing.GeographicDatum
    '''OSGB 1936 datum.'''
    @property
    def ellipsoid(self) -> aspose.gis.spatialreferencing.Ellipsoid:
        '''Ellipsoid, used in this datum to approximate Earth.'''
        raise NotImplementedError()
    
    @property
    def to_wgs_84_parameters(self) -> aspose.gis.spatialreferencing.BursaWolfParameters:
        '''BursaWolfParamters that can be used to transform coordinates in this datum to coordinates in WGS84 datum.'''
        raise NotImplementedError()
    

class GeographicSpatialReferenceSystem(SpatialReferenceSystem):
    '''A Geographic SRS is an SRS that is based on longitude and latitude.
    A Geographic SRS can be two dimensional or three dimensional.
    If geographic SRS is three dimensional, then it is actually a compound SRS of two dimensional SRS and vertical SRS.'''
    
    @overload
    @staticmethod
    def is_equivalent(srs1 : aspose.gis.spatialreferencing.SpatialReferenceSystem, srs2 : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> bool:
        '''Determines if two SRS are equivalent.
        Same coordinates of equivalent SRS match same place on Earth.
        Some parameters of equivalent SRS can be different, for example :py:attr:`aspose.gis.spatialreferencing.IdentifiableObject.name`.
        
        :param srs1: First SRS.
        :param srs2: Second SRS.
        :returns: bool value, indicating whether two SRS are equivalent.'''
        raise NotImplementedError()
    
    @overload
    def is_equivalent(self, other : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> bool:
        '''Detects whether this SRS is equivalent to other SRS. :py:func:`aspose.gis.spatialreferencing.SpatialReferenceSystem.is_equivalent`.
        
        :param other: Other SRS.
        :returns: bool value, indicating whether this SRS is equivalent to other SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def try_create_from_wkt(wkt : str, value : List[aspose.gis.spatialreferencing.SpatialReferenceSystem]) -> bool:
        '''Creates a new ``SpatialReferenceSystem`` based on WKT (Well-Known Text) string.
        
        :param wkt: WKT string.
        :param value: When this methods returns , contains an SRS created from WKT; otherwise,
        contains .
        :returns: if SRS was successfully created;  otherwise.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_from_wkt(wkt : str) -> aspose.gis.spatialreferencing.SpatialReferenceSystem:
        '''Creates a new ``SpatialReferenceSystem`` based on WKT (Well-Known Text) string.
        
        :param wkt: WKT string.
        :returns: New ``SpatialReferenceSystem``.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_from_epsg(epsg : int) -> aspose.gis.spatialreferencing.SpatialReferenceSystem:
        '''Create a spatial reference system based the specified EPSG code.
        
        :param epsg: EPSG code of the spatial reference system.
        :returns: A new spatial reference system with the specified EPSG code.'''
        raise NotImplementedError()
    
    @staticmethod
    def try_create_from_epsg(epsg : int, value : List[aspose.gis.spatialreferencing.SpatialReferenceSystem]) -> bool:
        '''Create a spatial reference system based the specified EPSG code.
        
        :param epsg: EPSG code of the spatial reference system.
        :param value: When this methods returns , contains a SRS with the specified EPSG code; otherwise,
        contains .
        :returns: if specified EPSG code is known and SRS was created;  otherwise.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_geographic(parameters : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystemParameters, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem:
        '''Create geographic SRS from custom parameters.
        
        :param parameters: Parameters to create from.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Geographic SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_geocentric(parameters : aspose.gis.spatialreferencing.GeocentricSpatialReferenceSystemParameters, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.GeocentricSpatialReferenceSystem:
        '''Create geocentric SRS from custom parameters.
        
        :param parameters: Parameters to create from.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Geocentric SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_projected(parameters : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystemParameters, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem:
        '''Create projected SRS from custom parameters.
        
        :param parameters: Parameters to create from.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Projected SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_vertical(name : str, vertical_datum : aspose.gis.spatialreferencing.VerticalDatum, vertical_unit : aspose.gis.rendering.Unit, vertical_axis : aspose.gis.spatialreferencing.Axis, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.VerticalSpatialReferenceSystem:
        '''Create vertical SRS.
        
        :param name: Name of SRS. If .
        :param vertical_datum: Datum to be used in SRS.
        :param vertical_unit: Unit to be used in SRS. If , :py:attr:`aspose.gis.spatialreferencing.Unit.meter` will be used.
        :param vertical_axis: Axis with "up" or "down" direction, to be used in SRS. If , axis with up direction will be used.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Vertical SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_compound(name : str, head : aspose.gis.spatialreferencing.SpatialReferenceSystem, tail : aspose.gis.spatialreferencing.SpatialReferenceSystem, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.CompoundSpatialReferenceSystem:
        '''Create compound SRS.
        
        :param name: Name of new SRS.
        :param head: Head SRS of new SRS.
        :param tail: Tail SRS of new SRS.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Compound SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_local(name : str, datum : aspose.gis.spatialreferencing.LocalDatum, unit : aspose.gis.rendering.Unit, axises : List[aspose.gis.spatialreferencing.Axis], identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.LocalSpatialReferenceSystem:
        raise NotImplementedError()
    
    def validate(self, error_message : List[String]) -> bool:
        '''Determine if this SRS is valid.
        
        :param error_message: If method return , then this is description of invalidity.
        :returns: if SRS is valid,  otherwise.'''
        raise NotImplementedError()
    
    def get_axis(self, dimension : int) -> aspose.gis.spatialreferencing.Axis:
        '''Get :py:class:`aspose.gis.spatialreferencing.Axis` that describes dimension.
        
        :param dimension: Number of dimension.
        :returns: Axis that describes dimension.'''
        raise NotImplementedError()
    
    def get_unit(self, dimension : int) -> aspose.gis.rendering.Unit:
        '''Get :py:class:`aspose.gis.spatialreferencing.Unit` of dimension.
        
        :param dimension: Number of dimension.
        :returns: Unit of dimension.'''
        raise NotImplementedError()
    
    def export_to_wkt(self) -> str:
        '''Returns representation of this SRS as WKT string.
        The result WKT string will match OGC 01-009 specification, usually named "WKT1".
        
        :returns: WKT representation of this SRS.'''
        raise NotImplementedError()
    
    def try_create_transformation_to(self, target_srs : aspose.gis.spatialreferencing.SpatialReferenceSystem, value : List[aspose.gis.spatialreferencing.SpatialReferenceSystemTransformation]) -> bool:
        '''Creates transformation from this ``SpatialReferenceSystem`` to another ``SpatialReferenceSystem``.
        
        :param target_srs: Another ``SpatialReferenceSystem``.
        :param value: When this methods returns , contains a transformation; otherwise, contains .
        :returns: Transformation from this ``SpatialReferenceSystem`` to another ``SpatialReferenceSystem``.
        :returns: if transformation was created successfully;  otherwise.'''
        raise NotImplementedError()
    
    def create_transformation_to(self, target_srs : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> aspose.gis.spatialreferencing.SpatialReferenceSystemTransformation:
        '''Creates transformation from this ``SpatialReferenceSystem`` to another ``SpatialReferenceSystem``.
        
        :param target_srs: Another ``SpatialReferenceSystem``.
        :returns: Transformation from this ``SpatialReferenceSystem`` to another ``SpatialReferenceSystem``.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Name of this object.'''
        raise NotImplementedError()
    
    @property
    def epsg_code(self) -> int:
        '''If this objects identifier is EPSG identifier - return its code. Otherwise - return -1.'''
        raise NotImplementedError()
    
    @property
    def identifier(self) -> aspose.gis.spatialreferencing.Identifier:
        '''Identifier of this identifiable object.'''
        raise NotImplementedError()
    
    wgs84 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''WGS 84 (EPSG:4326) spatial reference system.'''
    web_mercator : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem
    '''Web Mercator (EPSG:3857) spatial reference system.'''
    wgs72 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''WGS 72 (EPSG:4322) spatial reference system.'''
    nad83 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''NAD 83 (EPSG:4269) spatial reference system.'''
    etrs89 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''ETRS 89 (EPSG:4258) spatial reference system.'''
    etrs_89_lambert_conformal_conic : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem
    '''ETRS 89 / Lambert Conformal Conic (EPSG:3034) spatial reference system.'''
    etrs_89_lambert_azimuthal_equal_area : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem
    '''ETRS 89 / ETRS Lambert Azimuthal Equal Area (EPSG:3035) spatial reference system.'''
    osgb36 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''OSGB 36 (EPSG:4277) spatial reference system.'''
    osgb_36_british_national_grid : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem
    '''OSGB 36 / British National Grid (EPSG:27700) spatial reference system.'''
    @property
    def is_valid(self) -> bool:
        '''Same as :py:func:`aspose.gis.spatialreferencing.SpatialReferenceSystem.validate`, but don\'t return error message.'''
        raise NotImplementedError()
    
    @property
    def type(self) -> aspose.gis.spatialreferencing.SpatialReferenceSystemType:
        '''Returns :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystemType.GEOGRAPHIC`.'''
        raise NotImplementedError()
    
    @property
    def is_compound(self) -> bool:
        '''Returns whether this SRS is compound (a union of two SRS).
        Following combinations of SRS in compound SRS are considered valid:
        Geographic SRS + Vertical SRS, in this case type of compound SRS will be :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystemType.GEOGRAPHIC`.
        Projected SRS + Vertical SRS, in this case type of compound SRS will be :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystemType.PROJECTED`.
        If combination of SRSs differs, type of compound SRS will be :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystemType.UNKNOWN`.'''
        raise NotImplementedError()
    
    @property
    def is_single(self) -> bool:
        '''Returns whether this SRS is single (not a union of two SRS).'''
        raise NotImplementedError()
    
    @property
    def as_geographic(self) -> aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem:
        '''Returns this.'''
        raise NotImplementedError()
    
    @property
    def as_projected(self) -> aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.type` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def as_geocentric(self) -> aspose.gis.spatialreferencing.GeocentricSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.GeocentricSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.type` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def as_vertical(self) -> aspose.gis.spatialreferencing.VerticalSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.VerticalSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.type` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def as_local(self) -> aspose.gis.spatialreferencing.LocalSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.LocalSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.type` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def as_compound(self) -> aspose.gis.spatialreferencing.CompoundSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.CompoundSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.is_compound` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def dimensions_count(self) -> int:
        '''Returns dimensions count in this SRS. For geographic SRS this can be:
        two - if this is single geographic SRS.
        three - if this is compound SRS, which consists of single, two dimensional, geographic SRS and vertical SRS, that adds third dimension.'''
        raise NotImplementedError()
    
    @property
    def has_prime_meridian(self) -> bool:
        '''Returns , since geographic SRS always have prime meridian.'''
        raise NotImplementedError()
    
    @property
    def prime_meridian(self) -> aspose.gis.spatialreferencing.PrimeMeridian:
        '''Returns prime meridian of this SRS.'''
        raise NotImplementedError()
    
    @property
    def has_geographic_datum(self) -> bool:
        '''Returns , since geographic SRS always have prime meridian.'''
        raise NotImplementedError()
    
    @property
    def geographic_datum(self) -> aspose.gis.spatialreferencing.GeographicDatum:
        '''Returns geographic datum of this SRS.'''
        raise NotImplementedError()
    
    @property
    def angular_unit(self) -> aspose.gis.rendering.Unit:
        '''Unit, used for angular dimensions, in this SRS.'''
        raise NotImplementedError()
    
    @property
    def axises_order(self) -> aspose.gis.spatialreferencing.GeographicAxisesOrder:
        '''Order of axises in this SRS.
        If this SRS is not valid and has wrong axises directions, :py:attr:`aspose.gis.spatialreferencing.GeographicAxisesOrder.INVALID` is returned.'''
        raise NotImplementedError()
    

class GeographicSpatialReferenceSystemParameters:
    '''Parameters to create geographic SRS.
    Parameters have reasonable defaults, so you will have to assign only some of them.
    If you assign  to any parameter, a default value will be used.'''
    
    @property
    def name(self) -> str:
        '''Name of geographic SRS. Default is "Unnamed".'''
        raise NotImplementedError()
    
    @name.setter
    def name(self, value : str) -> None:
        '''Name of geographic SRS. Default is "Unnamed".'''
        raise NotImplementedError()
    
    @property
    def datum(self) -> aspose.gis.spatialreferencing.GeographicDatum:
        '''Datum of geographic SRS. Default is :py:attr:`aspose.gis.spatialreferencing.GeographicDatum.wgs84`.'''
        raise NotImplementedError()
    
    @datum.setter
    def datum(self, value : aspose.gis.spatialreferencing.GeographicDatum) -> None:
        '''Datum of geographic SRS. Default is :py:attr:`aspose.gis.spatialreferencing.GeographicDatum.wgs84`.'''
        raise NotImplementedError()
    
    @property
    def prime_meridian(self) -> aspose.gis.spatialreferencing.PrimeMeridian:
        '''Prime meridian of this SRS. Default is :py:attr:`aspose.gis.spatialreferencing.PrimeMeridian.greenwich`.'''
        raise NotImplementedError()
    
    @prime_meridian.setter
    def prime_meridian(self, value : aspose.gis.spatialreferencing.PrimeMeridian) -> None:
        '''Prime meridian of this SRS. Default is :py:attr:`aspose.gis.spatialreferencing.PrimeMeridian.greenwich`.'''
        raise NotImplementedError()
    
    @property
    def angular_unit(self) -> aspose.gis.rendering.Unit:
        '''Units to be used in this SRS. Default is :py:attr:`aspose.gis.spatialreferencing.Unit.degree`.'''
        raise NotImplementedError()
    
    @angular_unit.setter
    def angular_unit(self, value : aspose.gis.rendering.Unit) -> None:
        '''Units to be used in this SRS. Default is :py:attr:`aspose.gis.spatialreferencing.Unit.degree`.'''
        raise NotImplementedError()
    
    @property
    def longitude_axis(self) -> aspose.gis.spatialreferencing.Axis:
        '''Axis that describes longitude. Default is axis with east direction.'''
        raise NotImplementedError()
    
    @longitude_axis.setter
    def longitude_axis(self, value : aspose.gis.spatialreferencing.Axis) -> None:
        '''Axis that describes longitude. Default is axis with east direction.'''
        raise NotImplementedError()
    
    @property
    def latitude_axis(self) -> aspose.gis.spatialreferencing.Axis:
        '''Axis that describes latitude. Defaults is axis with north direction.'''
        raise NotImplementedError()
    
    @latitude_axis.setter
    def latitude_axis(self, value : aspose.gis.spatialreferencing.Axis) -> None:
        '''Axis that describes latitude. Defaults is axis with north direction.'''
        raise NotImplementedError()
    
    @property
    def axises_order(self) -> aspose.gis.spatialreferencing.GeographicAxisesOrder:
        '''Order of axises. Defaults to :py:attr:`aspose.gis.spatialreferencing.GeographicAxisesOrder.LONGITUDE_LATITUDE`.'''
        raise NotImplementedError()
    
    @axises_order.setter
    def axises_order(self, value : aspose.gis.spatialreferencing.GeographicAxisesOrder) -> None:
        '''Order of axises. Defaults to :py:attr:`aspose.gis.spatialreferencing.GeographicAxisesOrder.LONGITUDE_LATITUDE`.'''
        raise NotImplementedError()
    

class IdentifiableObject:
    '''Represents an object that might have EPSG code and name.'''
    
    @property
    def name(self) -> str:
        '''Name of this object.'''
        raise NotImplementedError()
    
    @property
    def epsg_code(self) -> int:
        '''If this objects identifier is EPSG identifier - return its code. Otherwise - return -1.'''
        raise NotImplementedError()
    
    @property
    def identifier(self) -> aspose.gis.spatialreferencing.Identifier:
        '''Identifier of this identifiable object.'''
        raise NotImplementedError()
    

class Identifier:
    '''Represents an identifier - a reference to external description of an object.
    If you create a SRS from WKT, :py:class:`aspose.gis.spatialreferencing.Identifier` corresponds to "AUTHORITY" keyword.'''
    
    @staticmethod
    def epsg(epsg_code : int) -> aspose.gis.spatialreferencing.Identifier:
        '''Creates new Identifier that represents EPSG identifier with code ``epsgCode``.
        
        :param epsg_code: Epsg code.
        :returns: New identifier with :py:attr:`aspose.gis.spatialreferencing.Identifier.authority_name` "EPSG" and :py:attr:`aspose.gis.spatialreferencing.Identifier.authority_unique_identifier```epsgCode``.
        If ``epsgCode`` is less then 0 - return ;'''
        raise NotImplementedError()
    
    def get_epsg_code(self) -> int:
        '''If this object represents a valid EPSG identifier (e.g. - authority name is "EPSG" and authority unique identifier is integer) -
        return it. Otherwise - return -1.
        
        :returns: EPSG identifier represented by this object. If this object doesn\'t represent an EPSG identifier - return -1.'''
        raise NotImplementedError()
    
    def equals(self, other : aspose.gis.spatialreferencing.Identifier) -> bool:
        '''Indicates whether the current object is equal to another object of the same type.
        
        :param other: An object to compare with this object.
        :returns: true if the current object is equal to the ``other`` parameter; otherwise, false.'''
        raise NotImplementedError()
    
    @property
    def authority_name(self) -> str:
        '''A name of authority, which gave an :py:attr:`aspose.gis.spatialreferencing.Identifier.authority_unique_identifier`.'''
        raise NotImplementedError()
    
    @property
    def authority_unique_identifier(self) -> str:
        '''A unique way to represent an object within a :py:attr:`aspose.gis.spatialreferencing.Identifier.authority_name`.'''
        raise NotImplementedError()
    

class LocalDatum(IdentifiableObject):
    '''Indicates method used for measurements in local spatial reference system.'''
    
    @property
    def name(self) -> str:
        '''Name of this object.'''
        raise NotImplementedError()
    
    @property
    def epsg_code(self) -> int:
        '''If this objects identifier is EPSG identifier - return its code. Otherwise - return -1.'''
        raise NotImplementedError()
    
    @property
    def identifier(self) -> aspose.gis.spatialreferencing.Identifier:
        '''Identifier of this identifiable object.'''
        raise NotImplementedError()
    
    @property
    def datum_type(self) -> int:
        '''An integer number, indicating measurement method that had been used.'''
        raise NotImplementedError()
    

class LocalSpatialReferenceSystem(SpatialReferenceSystem):
    '''Local SRS related coordinates to some object, not earth.'''
    
    @overload
    def is_equivalent(self, other : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> bool:
        '''Detects whether this SRS is equivalent to other SRS. :py:func:`aspose.gis.spatialreferencing.SpatialReferenceSystem.is_equivalent`.
        
        :param other: Other SRS.
        :returns: bool value, indicating whether this SRS is equivalent to other SRS.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def is_equivalent(srs1 : aspose.gis.spatialreferencing.SpatialReferenceSystem, srs2 : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> bool:
        '''Determines if two SRS are equivalent.
        Same coordinates of equivalent SRS match same place on Earth.
        Some parameters of equivalent SRS can be different, for example :py:attr:`aspose.gis.spatialreferencing.IdentifiableObject.name`.
        
        :param srs1: First SRS.
        :param srs2: Second SRS.
        :returns: bool value, indicating whether two SRS are equivalent.'''
        raise NotImplementedError()
    
    @staticmethod
    def try_create_from_wkt(wkt : str, value : List[aspose.gis.spatialreferencing.SpatialReferenceSystem]) -> bool:
        '''Creates a new ``SpatialReferenceSystem`` based on WKT (Well-Known Text) string.
        
        :param wkt: WKT string.
        :param value: When this methods returns , contains an SRS created from WKT; otherwise,
        contains .
        :returns: if SRS was successfully created;  otherwise.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_from_wkt(wkt : str) -> aspose.gis.spatialreferencing.SpatialReferenceSystem:
        '''Creates a new ``SpatialReferenceSystem`` based on WKT (Well-Known Text) string.
        
        :param wkt: WKT string.
        :returns: New ``SpatialReferenceSystem``.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_from_epsg(epsg : int) -> aspose.gis.spatialreferencing.SpatialReferenceSystem:
        '''Create a spatial reference system based the specified EPSG code.
        
        :param epsg: EPSG code of the spatial reference system.
        :returns: A new spatial reference system with the specified EPSG code.'''
        raise NotImplementedError()
    
    @staticmethod
    def try_create_from_epsg(epsg : int, value : List[aspose.gis.spatialreferencing.SpatialReferenceSystem]) -> bool:
        '''Create a spatial reference system based the specified EPSG code.
        
        :param epsg: EPSG code of the spatial reference system.
        :param value: When this methods returns , contains a SRS with the specified EPSG code; otherwise,
        contains .
        :returns: if specified EPSG code is known and SRS was created;  otherwise.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_geographic(parameters : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystemParameters, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem:
        '''Create geographic SRS from custom parameters.
        
        :param parameters: Parameters to create from.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Geographic SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_geocentric(parameters : aspose.gis.spatialreferencing.GeocentricSpatialReferenceSystemParameters, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.GeocentricSpatialReferenceSystem:
        '''Create geocentric SRS from custom parameters.
        
        :param parameters: Parameters to create from.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Geocentric SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_projected(parameters : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystemParameters, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem:
        '''Create projected SRS from custom parameters.
        
        :param parameters: Parameters to create from.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Projected SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_vertical(name : str, vertical_datum : aspose.gis.spatialreferencing.VerticalDatum, vertical_unit : aspose.gis.rendering.Unit, vertical_axis : aspose.gis.spatialreferencing.Axis, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.VerticalSpatialReferenceSystem:
        '''Create vertical SRS.
        
        :param name: Name of SRS. If .
        :param vertical_datum: Datum to be used in SRS.
        :param vertical_unit: Unit to be used in SRS. If , :py:attr:`aspose.gis.spatialreferencing.Unit.meter` will be used.
        :param vertical_axis: Axis with "up" or "down" direction, to be used in SRS. If , axis with up direction will be used.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Vertical SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_compound(name : str, head : aspose.gis.spatialreferencing.SpatialReferenceSystem, tail : aspose.gis.spatialreferencing.SpatialReferenceSystem, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.CompoundSpatialReferenceSystem:
        '''Create compound SRS.
        
        :param name: Name of new SRS.
        :param head: Head SRS of new SRS.
        :param tail: Tail SRS of new SRS.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Compound SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_local(name : str, datum : aspose.gis.spatialreferencing.LocalDatum, unit : aspose.gis.rendering.Unit, axises : List[aspose.gis.spatialreferencing.Axis], identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.LocalSpatialReferenceSystem:
        raise NotImplementedError()
    
    def validate(self, error_message : List[String]) -> bool:
        '''Determine if this SRS is valid. See :py:func:`aspose.gis.spatialreferencing.SpatialReferenceSystem.validate` for validity description.
        
        :param error_message: Description of invalidity (if result is )
        :returns: If this SRS is valid - , otherwise - .'''
        raise NotImplementedError()
    
    def get_axis(self, dimension : int) -> aspose.gis.spatialreferencing.Axis:
        '''Get :py:class:`aspose.gis.spatialreferencing.Axis` that describes dimension.
        
        :param dimension: Number of dimension.
        :returns: Axis that describes dimension.'''
        raise NotImplementedError()
    
    def get_unit(self, dimension : int) -> aspose.gis.rendering.Unit:
        '''Get :py:attr:`aspose.gis.spatialreferencing.LocalSpatialReferenceSystem.unit` of dimension.
        
        :param dimension: Number of dimension.
        :returns: Unit of dimension.'''
        raise NotImplementedError()
    
    def export_to_wkt(self) -> str:
        '''Returns representation of this SRS as WKT string.
        The result WKT string will match OGC 01-009 specification, usually named "WKT1".
        
        :returns: WKT representation of this SRS.'''
        raise NotImplementedError()
    
    def try_create_transformation_to(self, target_srs : aspose.gis.spatialreferencing.SpatialReferenceSystem, value : List[aspose.gis.spatialreferencing.SpatialReferenceSystemTransformation]) -> bool:
        '''Creates transformation from this ``SpatialReferenceSystem`` to another ``SpatialReferenceSystem``.
        
        :param target_srs: Another ``SpatialReferenceSystem``.
        :param value: When this methods returns , contains a transformation; otherwise, contains .
        :returns: Transformation from this ``SpatialReferenceSystem`` to another ``SpatialReferenceSystem``.
        :returns: if transformation was created successfully;  otherwise.'''
        raise NotImplementedError()
    
    def create_transformation_to(self, target_srs : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> aspose.gis.spatialreferencing.SpatialReferenceSystemTransformation:
        '''Creates transformation from this ``SpatialReferenceSystem`` to another ``SpatialReferenceSystem``.
        
        :param target_srs: Another ``SpatialReferenceSystem``.
        :returns: Transformation from this ``SpatialReferenceSystem`` to another ``SpatialReferenceSystem``.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Name of this object.'''
        raise NotImplementedError()
    
    @property
    def epsg_code(self) -> int:
        '''If this objects identifier is EPSG identifier - return its code. Otherwise - return -1.'''
        raise NotImplementedError()
    
    @property
    def identifier(self) -> aspose.gis.spatialreferencing.Identifier:
        '''Identifier of this identifiable object.'''
        raise NotImplementedError()
    
    wgs84 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''WGS 84 (EPSG:4326) spatial reference system.'''
    web_mercator : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem
    '''Web Mercator (EPSG:3857) spatial reference system.'''
    wgs72 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''WGS 72 (EPSG:4322) spatial reference system.'''
    nad83 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''NAD 83 (EPSG:4269) spatial reference system.'''
    etrs89 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''ETRS 89 (EPSG:4258) spatial reference system.'''
    etrs_89_lambert_conformal_conic : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem
    '''ETRS 89 / Lambert Conformal Conic (EPSG:3034) spatial reference system.'''
    etrs_89_lambert_azimuthal_equal_area : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem
    '''ETRS 89 / ETRS Lambert Azimuthal Equal Area (EPSG:3035) spatial reference system.'''
    osgb36 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''OSGB 36 (EPSG:4277) spatial reference system.'''
    osgb_36_british_national_grid : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem
    '''OSGB 36 / British National Grid (EPSG:27700) spatial reference system.'''
    @property
    def is_valid(self) -> bool:
        '''Same as :py:func:`aspose.gis.spatialreferencing.SpatialReferenceSystem.validate`, but don\'t return error message.'''
        raise NotImplementedError()
    
    @property
    def type(self) -> aspose.gis.spatialreferencing.SpatialReferenceSystemType:
        '''Return :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystemType.LOCAL`.'''
        raise NotImplementedError()
    
    @property
    def is_compound(self) -> bool:
        '''Returns whether this SRS is compound (a union of two SRS).
        Following combinations of SRS in compound SRS are considered valid:
        Geographic SRS + Vertical SRS, in this case type of compound SRS will be :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystemType.GEOGRAPHIC`.
        Projected SRS + Vertical SRS, in this case type of compound SRS will be :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystemType.PROJECTED`.
        If combination of SRSs differs, type of compound SRS will be :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystemType.UNKNOWN`.'''
        raise NotImplementedError()
    
    @property
    def is_single(self) -> bool:
        '''Returns whether this SRS is single (not a union of two SRS).'''
        raise NotImplementedError()
    
    @property
    def as_geographic(self) -> aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.type` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def as_projected(self) -> aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.type` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def as_geocentric(self) -> aspose.gis.spatialreferencing.GeocentricSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.GeocentricSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.type` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def as_vertical(self) -> aspose.gis.spatialreferencing.VerticalSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.VerticalSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.type` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def as_local(self) -> aspose.gis.spatialreferencing.LocalSpatialReferenceSystem:
        '''Return this.'''
        raise NotImplementedError()
    
    @property
    def as_compound(self) -> aspose.gis.spatialreferencing.CompoundSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.CompoundSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.is_compound` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def dimensions_count(self) -> int:
        '''Number of dimensions in this SRS.'''
        raise NotImplementedError()
    
    @property
    def has_prime_meridian(self) -> bool:
        '''Returns , since Local SRS doesn\'t have prime meridian.'''
        raise NotImplementedError()
    
    @property
    def prime_meridian(self) -> aspose.gis.spatialreferencing.PrimeMeridian:
        '''Throws :py:class:`System.InvalidOperationException`, since Local SRS doesn\'t have prime meridian.'''
        raise NotImplementedError()
    
    @property
    def has_geographic_datum(self) -> bool:
        '''Returns , since Local SRS doesn\'t have geographic datum.'''
        raise NotImplementedError()
    
    @property
    def geographic_datum(self) -> aspose.gis.spatialreferencing.GeographicDatum:
        '''Throws :py:class:`System.InvalidOperationException`, since Local SRS doesn\'t have geographic datum.'''
        raise NotImplementedError()
    
    @property
    def local_datum(self) -> aspose.gis.spatialreferencing.LocalDatum:
        '''Datum, that describes measurements method.'''
        raise NotImplementedError()
    
    @property
    def unit(self) -> aspose.gis.rendering.Unit:
        '''Unit of this SRS.'''
        raise NotImplementedError()
    

class PrimeMeridian(IdentifiableObject):
    '''PrimeMeridian represents a meridian at which longitude is defined to be 0.'''
    
    @property
    def name(self) -> str:
        '''Name of this object.'''
        raise NotImplementedError()
    
    @property
    def epsg_code(self) -> int:
        '''If this objects identifier is EPSG identifier - return its code. Otherwise - return -1.'''
        raise NotImplementedError()
    
    @property
    def identifier(self) -> aspose.gis.spatialreferencing.Identifier:
        '''Identifier of this identifiable object.'''
        raise NotImplementedError()
    
    greenwich : aspose.gis.spatialreferencing.PrimeMeridian
    '''Greenwich meridian.'''
    @property
    def longitude(self) -> float:
        '''Distance from Greenwich meridian to prime meridian in degrees.'''
        raise NotImplementedError()
    

class ProjectedSpatialReferenceSystem(SpatialReferenceSystem):
    '''Projected SRS is a result of application a projection to geographic SRS.
    A projected SRS can be two dimensional or three dimensional.
    If projected SRS is three dimensional, then it is actually a compound SRS of two dimensional projected SRS and one dimensional vertical SRS.'''
    
    @overload
    @staticmethod
    def is_equivalent(srs1 : aspose.gis.spatialreferencing.SpatialReferenceSystem, srs2 : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> bool:
        '''Determines if two SRS are equivalent.
        Same coordinates of equivalent SRS match same place on Earth.
        Some parameters of equivalent SRS can be different, for example :py:attr:`aspose.gis.spatialreferencing.IdentifiableObject.name`.
        
        :param srs1: First SRS.
        :param srs2: Second SRS.
        :returns: bool value, indicating whether two SRS are equivalent.'''
        raise NotImplementedError()
    
    @overload
    def is_equivalent(self, other : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> bool:
        '''Detects whether this SRS is equivalent to other SRS. :py:func:`aspose.gis.spatialreferencing.SpatialReferenceSystem.is_equivalent`.
        
        :param other: Other SRS.
        :returns: bool value, indicating whether this SRS is equivalent to other SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def try_create_from_wkt(wkt : str, value : List[aspose.gis.spatialreferencing.SpatialReferenceSystem]) -> bool:
        '''Creates a new ``SpatialReferenceSystem`` based on WKT (Well-Known Text) string.
        
        :param wkt: WKT string.
        :param value: When this methods returns , contains an SRS created from WKT; otherwise,
        contains .
        :returns: if SRS was successfully created;  otherwise.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_from_wkt(wkt : str) -> aspose.gis.spatialreferencing.SpatialReferenceSystem:
        '''Creates a new ``SpatialReferenceSystem`` based on WKT (Well-Known Text) string.
        
        :param wkt: WKT string.
        :returns: New ``SpatialReferenceSystem``.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_from_epsg(epsg : int) -> aspose.gis.spatialreferencing.SpatialReferenceSystem:
        '''Create a spatial reference system based the specified EPSG code.
        
        :param epsg: EPSG code of the spatial reference system.
        :returns: A new spatial reference system with the specified EPSG code.'''
        raise NotImplementedError()
    
    @staticmethod
    def try_create_from_epsg(epsg : int, value : List[aspose.gis.spatialreferencing.SpatialReferenceSystem]) -> bool:
        '''Create a spatial reference system based the specified EPSG code.
        
        :param epsg: EPSG code of the spatial reference system.
        :param value: When this methods returns , contains a SRS with the specified EPSG code; otherwise,
        contains .
        :returns: if specified EPSG code is known and SRS was created;  otherwise.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_geographic(parameters : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystemParameters, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem:
        '''Create geographic SRS from custom parameters.
        
        :param parameters: Parameters to create from.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Geographic SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_geocentric(parameters : aspose.gis.spatialreferencing.GeocentricSpatialReferenceSystemParameters, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.GeocentricSpatialReferenceSystem:
        '''Create geocentric SRS from custom parameters.
        
        :param parameters: Parameters to create from.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Geocentric SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_projected(parameters : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystemParameters, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem:
        '''Create projected SRS from custom parameters.
        
        :param parameters: Parameters to create from.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Projected SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_vertical(name : str, vertical_datum : aspose.gis.spatialreferencing.VerticalDatum, vertical_unit : aspose.gis.rendering.Unit, vertical_axis : aspose.gis.spatialreferencing.Axis, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.VerticalSpatialReferenceSystem:
        '''Create vertical SRS.
        
        :param name: Name of SRS. If .
        :param vertical_datum: Datum to be used in SRS.
        :param vertical_unit: Unit to be used in SRS. If , :py:attr:`aspose.gis.spatialreferencing.Unit.meter` will be used.
        :param vertical_axis: Axis with "up" or "down" direction, to be used in SRS. If , axis with up direction will be used.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Vertical SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_compound(name : str, head : aspose.gis.spatialreferencing.SpatialReferenceSystem, tail : aspose.gis.spatialreferencing.SpatialReferenceSystem, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.CompoundSpatialReferenceSystem:
        '''Create compound SRS.
        
        :param name: Name of new SRS.
        :param head: Head SRS of new SRS.
        :param tail: Tail SRS of new SRS.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Compound SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_local(name : str, datum : aspose.gis.spatialreferencing.LocalDatum, unit : aspose.gis.rendering.Unit, axises : List[aspose.gis.spatialreferencing.Axis], identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.LocalSpatialReferenceSystem:
        raise NotImplementedError()
    
    def validate(self, error_message : List[String]) -> bool:
        '''Determine if this SRS is valid.
        
        :param error_message: If method return , then this is description of invalidity.
        :returns: if SRS is valid,  otherwise.'''
        raise NotImplementedError()
    
    def get_axis(self, dimension : int) -> aspose.gis.spatialreferencing.Axis:
        '''Get :py:class:`aspose.gis.spatialreferencing.Axis` that describes dimension.
        
        :param dimension: Number of dimension.
        :returns: Axis that describes dimension.'''
        raise NotImplementedError()
    
    def get_unit(self, dimension : int) -> aspose.gis.rendering.Unit:
        '''Get :py:class:`aspose.gis.spatialreferencing.Unit` of dimension.
        
        :param dimension: Number of dimension.
        :returns: Unit of dimension.'''
        raise NotImplementedError()
    
    def export_to_wkt(self) -> str:
        '''Returns representation of this SRS as WKT string.
        The result WKT string will match OGC 01-009 specification, usually named "WKT1".
        
        :returns: WKT representation of this SRS.'''
        raise NotImplementedError()
    
    def try_create_transformation_to(self, target_srs : aspose.gis.spatialreferencing.SpatialReferenceSystem, value : List[aspose.gis.spatialreferencing.SpatialReferenceSystemTransformation]) -> bool:
        '''Creates transformation from this ``SpatialReferenceSystem`` to another ``SpatialReferenceSystem``.
        
        :param target_srs: Another ``SpatialReferenceSystem``.
        :param value: When this methods returns , contains a transformation; otherwise, contains .
        :returns: Transformation from this ``SpatialReferenceSystem`` to another ``SpatialReferenceSystem``.
        :returns: if transformation was created successfully;  otherwise.'''
        raise NotImplementedError()
    
    def create_transformation_to(self, target_srs : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> aspose.gis.spatialreferencing.SpatialReferenceSystemTransformation:
        '''Creates transformation from this ``SpatialReferenceSystem`` to another ``SpatialReferenceSystem``.
        
        :param target_srs: Another ``SpatialReferenceSystem``.
        :returns: Transformation from this ``SpatialReferenceSystem`` to another ``SpatialReferenceSystem``.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Name of this object.'''
        raise NotImplementedError()
    
    @property
    def epsg_code(self) -> int:
        '''If this objects identifier is EPSG identifier - return its code. Otherwise - return -1.'''
        raise NotImplementedError()
    
    @property
    def identifier(self) -> aspose.gis.spatialreferencing.Identifier:
        '''Identifier of this identifiable object.'''
        raise NotImplementedError()
    
    wgs84 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''WGS 84 (EPSG:4326) spatial reference system.'''
    web_mercator : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem
    '''Web Mercator (EPSG:3857) spatial reference system.'''
    wgs72 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''WGS 72 (EPSG:4322) spatial reference system.'''
    nad83 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''NAD 83 (EPSG:4269) spatial reference system.'''
    etrs89 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''ETRS 89 (EPSG:4258) spatial reference system.'''
    etrs_89_lambert_conformal_conic : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem
    '''ETRS 89 / Lambert Conformal Conic (EPSG:3034) spatial reference system.'''
    etrs_89_lambert_azimuthal_equal_area : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem
    '''ETRS 89 / ETRS Lambert Azimuthal Equal Area (EPSG:3035) spatial reference system.'''
    osgb36 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''OSGB 36 (EPSG:4277) spatial reference system.'''
    osgb_36_british_national_grid : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem
    '''OSGB 36 / British National Grid (EPSG:27700) spatial reference system.'''
    @property
    def is_valid(self) -> bool:
        '''Same as :py:func:`aspose.gis.spatialreferencing.SpatialReferenceSystem.validate`, but don\'t return error message.'''
        raise NotImplementedError()
    
    @property
    def type(self) -> aspose.gis.spatialreferencing.SpatialReferenceSystemType:
        '''Returns :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystemType.PROJECTED`.'''
        raise NotImplementedError()
    
    @property
    def is_compound(self) -> bool:
        '''Returns whether this SRS is compound (a union of two SRS).
        Following combinations of SRS in compound SRS are considered valid:
        Geographic SRS + Vertical SRS, in this case type of compound SRS will be :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystemType.GEOGRAPHIC`.
        Projected SRS + Vertical SRS, in this case type of compound SRS will be :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystemType.PROJECTED`.
        If combination of SRSs differs, type of compound SRS will be :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystemType.UNKNOWN`.'''
        raise NotImplementedError()
    
    @property
    def is_single(self) -> bool:
        '''Returns whether this SRS is single (not a union of two SRS).'''
        raise NotImplementedError()
    
    @property
    def as_geographic(self) -> aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.type` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def as_projected(self) -> aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem:
        '''Return this.'''
        raise NotImplementedError()
    
    @property
    def as_geocentric(self) -> aspose.gis.spatialreferencing.GeocentricSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.GeocentricSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.type` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def as_vertical(self) -> aspose.gis.spatialreferencing.VerticalSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.VerticalSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.type` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def as_local(self) -> aspose.gis.spatialreferencing.LocalSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.LocalSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.type` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def as_compound(self) -> aspose.gis.spatialreferencing.CompoundSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.CompoundSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.is_compound` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def dimensions_count(self) -> int:
        '''Returns dimensions count in this SRS. For projected SRS this can be:
        two - if this is single projected SRS.
        three - if this is compound SRS, which consists of single, two dimensional, projected SRS and vertical SRS, that adds third dimension.'''
        raise NotImplementedError()
    
    @property
    def has_prime_meridian(self) -> bool:
        '''Returns true, since projected SRS always have prime meridian.'''
        raise NotImplementedError()
    
    @property
    def prime_meridian(self) -> aspose.gis.spatialreferencing.PrimeMeridian:
        '''Returns prime meridian of this SRS.'''
        raise NotImplementedError()
    
    @property
    def has_geographic_datum(self) -> bool:
        '''Returns true, since projected SRS always have prime meridian.'''
        raise NotImplementedError()
    
    @property
    def geographic_datum(self) -> aspose.gis.spatialreferencing.GeographicDatum:
        '''Returns geographic datum of this SRS.'''
        raise NotImplementedError()
    
    @property
    def base(self) -> aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem:
        '''Geographic SRS to which :py:attr:`aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem.projection` was applied to get this SRS.'''
        raise NotImplementedError()
    
    @property
    def projection(self) -> aspose.gis.projections.Projection:
        '''Projection, that was applied to :py:attr:`aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem.base` to get this SRS.'''
        raise NotImplementedError()
    
    @property
    def linear_unit(self) -> aspose.gis.rendering.Unit:
        '''Unit, that is used for linear dimensions in this SRS and for linear parameters of :py:attr:`aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem.projection`.'''
        raise NotImplementedError()
    
    @property
    def angular_unit(self) -> aspose.gis.rendering.Unit:
        '''Unit, that is used for angular values in this SRS and for angular parameters of :py:attr:`aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem.projection`.
        Matches angular unit of :py:attr:`aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem.base`.'''
        raise NotImplementedError()
    
    @property
    def axises_order(self) -> aspose.gis.spatialreferencing.ProjectedAxisesOrder:
        '''Order of axises in this SRS.
        If this SRS is not valid and has wrong axises directions, :py:attr:`aspose.gis.spatialreferencing.ProjectedAxisesOrder.INVALID` is returned.'''
        raise NotImplementedError()
    

class ProjectedSpatialReferenceSystemParameters:
    '''Parameters to create projected SRS. Some of parameters have defaults.
    Some parameters have reasonable defaults, so you don\'t have to assign only them.
    If you assign  to those parameters, a default value will be used.
    :py:attr:`aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystemParameters.projection_method_name` and :py:attr:`aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystemParameters.base` don\'t have defaults -
    you have to assign some non  value to this properties.'''
    
    def add_projection_parameter(self, parameter_name : str, value : float) -> None:
        '''Adds projection parameter to this SRS. If parameter with such name already was added - update it.
        
        :param parameter_name: Name of projection parameter.
        :param value: Value of parameter. Unit of value should be in :py:attr:`aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystemParameters.linear_unit`
        or :py:attr:`aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem.angular_unit` of :py:attr:`aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystemParameters.base`.'''
        raise NotImplementedError()
    
    def get_projection_parameter(self, parameter_name : str) -> float:
        '''Gets projection parameter with specified name.
        
        :param parameter_name: Name of parameter.
        :returns: Projection parameter value.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Name of projected SRS. Default is "Unnamed".'''
        raise NotImplementedError()
    
    @name.setter
    def name(self, value : str) -> None:
        '''Name of projected SRS. Default is "Unnamed".'''
        raise NotImplementedError()
    
    @property
    def linear_unit(self) -> aspose.gis.rendering.Unit:
        '''Units to be used in this SRS. Default is :py:attr:`aspose.gis.spatialreferencing.Unit.meter`.'''
        raise NotImplementedError()
    
    @linear_unit.setter
    def linear_unit(self, value : aspose.gis.rendering.Unit) -> None:
        '''Units to be used in this SRS. Default is :py:attr:`aspose.gis.spatialreferencing.Unit.meter`.'''
        raise NotImplementedError()
    
    @property
    def base(self) -> aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem:
        '''Base geographic SRS (SRS to which projection is applied).
        You MUST set this property to not  value in order to create valid SRS,
        this property does not have any default.'''
        raise NotImplementedError()
    
    @base.setter
    def base(self, value : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem) -> None:
        '''Base geographic SRS (SRS to which projection is applied).
        You MUST set this property to not  value in order to create valid SRS,
        this property does not have any default.'''
        raise NotImplementedError()
    
    @property
    def x_axis(self) -> aspose.gis.spatialreferencing.Axis:
        '''Axis that describes X (horizontal) dimension. Defaults to axis with east direction.'''
        raise NotImplementedError()
    
    @x_axis.setter
    def x_axis(self, value : aspose.gis.spatialreferencing.Axis) -> None:
        '''Axis that describes X (horizontal) dimension. Defaults to axis with east direction.'''
        raise NotImplementedError()
    
    @property
    def y_axis(self) -> aspose.gis.spatialreferencing.Axis:
        '''Axis that describes Y (vertical) dimension. Defaults to axis with north direction.'''
        raise NotImplementedError()
    
    @y_axis.setter
    def y_axis(self, value : aspose.gis.spatialreferencing.Axis) -> None:
        '''Axis that describes Y (vertical) dimension. Defaults to axis with north direction.'''
        raise NotImplementedError()
    
    @property
    def axises_order(self) -> aspose.gis.spatialreferencing.ProjectedAxisesOrder:
        '''Order of axises. Defaults to :py:attr:`aspose.gis.spatialreferencing.ProjectedAxisesOrder.XY`.'''
        raise NotImplementedError()
    
    @axises_order.setter
    def axises_order(self, value : aspose.gis.spatialreferencing.ProjectedAxisesOrder) -> None:
        '''Order of axises. Defaults to :py:attr:`aspose.gis.spatialreferencing.ProjectedAxisesOrder.XY`.'''
        raise NotImplementedError()
    
    @property
    def projection_method_name(self) -> str:
        '''Name of projection method. There is no default and you MUST set this parameter to not  value, since
        projected SRS with no projection name is useless.'''
        raise NotImplementedError()
    
    @projection_method_name.setter
    def projection_method_name(self, value : str) -> None:
        '''Name of projection method. There is no default and you MUST set this parameter to not  value, since
        projected SRS with no projection name is useless.'''
        raise NotImplementedError()
    
    @property
    def projection_method_identifier(self) -> aspose.gis.spatialreferencing.Identifier:
        '''Identifier of projection method. There is no default value, you might set this parameter to not  value,
        if you want attach identifier to projection. If you do so - its up to you to ensure that identifier in consistent projection method
        name (projection method name will not change when you set this property).'''
        raise NotImplementedError()
    
    @projection_method_identifier.setter
    def projection_method_identifier(self, value : aspose.gis.spatialreferencing.Identifier) -> None:
        '''Identifier of projection method. There is no default value, you might set this parameter to not  value,
        if you want attach identifier to projection. If you do so - its up to you to ensure that identifier in consistent projection method
        name (projection method name will not change when you set this property).'''
        raise NotImplementedError()
    

class Projection(IdentifiableObject):
    '''Represents a projection method with parameters, that transforms (longitude, latitude) to (x, y).'''
    
    def get_parameter_value(self, name : str, type : aspose.gis.spatialreferencing.ParameterType) -> float:
        '''Gets parameter with specified name of this projection.
        
        :param name: Name of parameter.
        :param type: Type of parameter.
        Defines unit factor that will be deapplied:
        if type is :py:attr:`aspose.gis.spatialreferencing.ParameterType.LINEAR` then :py:attr:`aspose.gis.spatialreferencing.Projection.linear_parameters_unit` will be deapplied and result will be in meters.
        if type is :py:attr:`aspose.gis.spatialreferencing.ParameterType.ANGULAR` then :py:attr:`aspose.gis.spatialreferencing.Projection.angular_parameters_unit` will be deapplied and result will be in radians.
        if type is :py:attr:`aspose.gis.spatialreferencing.ParameterType.OTHER` parameter value will be returned \'as is\'.
        :returns: Parameter with specified name.'''
        raise NotImplementedError()
    
    def try_get_parameter_value(self, name : str, type : aspose.gis.spatialreferencing.ParameterType) -> Optional[float]:
        '''Gets parameter with specified name of this projection. If there are no such parameter - returns .
        
        :param name: Name of parameter.
        :param type: Type of parameter.
        Defines unit factor that will be deapplied:
        if type is :py:attr:`aspose.gis.spatialreferencing.ParameterType.LINEAR` then :py:attr:`aspose.gis.spatialreferencing.Projection.linear_parameters_unit` will be deapplied and result will be in meters.
        if type is :py:attr:`aspose.gis.spatialreferencing.ParameterType.ANGULAR` then :py:attr:`aspose.gis.spatialreferencing.Projection.angular_parameters_unit` will be deapplied and result will be in radians.
        if type is :py:attr:`aspose.gis.spatialreferencing.ParameterType.OTHER` parameter value will be returned \'as is\'.
        :returns: Parameter with specified name or  if it is not present.'''
        raise NotImplementedError()
    
    def is_equivalent(self, other : aspose.gis.projections.Projection) -> bool:
        '''Determines is two projections are equivalent. Equivalent projections map (longitude, latitude) to (x, y) in the
        same way.
        
        :param other: Other projection
        :returns: if projections are equivalent,  otherwise.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Name of this object.'''
        raise NotImplementedError()
    
    @property
    def epsg_code(self) -> int:
        '''If this objects identifier is EPSG identifier - return its code. Otherwise - return -1.'''
        raise NotImplementedError()
    
    @property
    def identifier(self) -> aspose.gis.spatialreferencing.Identifier:
        '''Identifier of this identifiable object.'''
        raise NotImplementedError()
    
    @property
    def linear_parameters_unit(self) -> aspose.gis.rendering.Unit:
        '''Unit that is used for linear parameters.'''
        raise NotImplementedError()
    
    @property
    def angular_parameters_unit(self) -> aspose.gis.rendering.Unit:
        '''Unit that is used for angular parameters.'''
        raise NotImplementedError()
    
    @property
    def parameters_names(self) -> List[str]:
        '''Gets an enumerable collection of names of parameters given to this projection'''
        raise NotImplementedError()
    

class SpatialReferenceSystem(IdentifiableObject):
    '''Spatial reference system maps coordinates to places on Earth.
    There are different types of SRS, see :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.type`.
    What\'s more, if type of SRS is :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystemType.GEOGRAPHIC` or
    :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystemType.PROJECTED`, SRS can be compound or single, see :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.is_compound`.'''
    
    @overload
    @staticmethod
    def is_equivalent(srs1 : aspose.gis.spatialreferencing.SpatialReferenceSystem, srs2 : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> bool:
        '''Determines if two SRS are equivalent.
        Same coordinates of equivalent SRS match same place on Earth.
        Some parameters of equivalent SRS can be different, for example :py:attr:`aspose.gis.spatialreferencing.IdentifiableObject.name`.
        
        :param srs1: First SRS.
        :param srs2: Second SRS.
        :returns: bool value, indicating whether two SRS are equivalent.'''
        raise NotImplementedError()
    
    @overload
    def is_equivalent(self, other : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> bool:
        '''Detects whether this SRS is equivalent to other SRS. :py:func:`aspose.gis.spatialreferencing.SpatialReferenceSystem.is_equivalent`.
        
        :param other: Other SRS.
        :returns: bool value, indicating whether this SRS is equivalent to other SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def try_create_from_wkt(wkt : str, value : List[aspose.gis.spatialreferencing.SpatialReferenceSystem]) -> bool:
        '''Creates a new ``SpatialReferenceSystem`` based on WKT (Well-Known Text) string.
        
        :param wkt: WKT string.
        :param value: When this methods returns , contains an SRS created from WKT; otherwise,
        contains .
        :returns: if SRS was successfully created;  otherwise.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_from_wkt(wkt : str) -> aspose.gis.spatialreferencing.SpatialReferenceSystem:
        '''Creates a new ``SpatialReferenceSystem`` based on WKT (Well-Known Text) string.
        
        :param wkt: WKT string.
        :returns: New ``SpatialReferenceSystem``.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_from_epsg(epsg : int) -> aspose.gis.spatialreferencing.SpatialReferenceSystem:
        '''Create a spatial reference system based the specified EPSG code.
        
        :param epsg: EPSG code of the spatial reference system.
        :returns: A new spatial reference system with the specified EPSG code.'''
        raise NotImplementedError()
    
    @staticmethod
    def try_create_from_epsg(epsg : int, value : List[aspose.gis.spatialreferencing.SpatialReferenceSystem]) -> bool:
        '''Create a spatial reference system based the specified EPSG code.
        
        :param epsg: EPSG code of the spatial reference system.
        :param value: When this methods returns , contains a SRS with the specified EPSG code; otherwise,
        contains .
        :returns: if specified EPSG code is known and SRS was created;  otherwise.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_geographic(parameters : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystemParameters, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem:
        '''Create geographic SRS from custom parameters.
        
        :param parameters: Parameters to create from.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Geographic SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_geocentric(parameters : aspose.gis.spatialreferencing.GeocentricSpatialReferenceSystemParameters, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.GeocentricSpatialReferenceSystem:
        '''Create geocentric SRS from custom parameters.
        
        :param parameters: Parameters to create from.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Geocentric SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_projected(parameters : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystemParameters, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem:
        '''Create projected SRS from custom parameters.
        
        :param parameters: Parameters to create from.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Projected SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_vertical(name : str, vertical_datum : aspose.gis.spatialreferencing.VerticalDatum, vertical_unit : aspose.gis.rendering.Unit, vertical_axis : aspose.gis.spatialreferencing.Axis, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.VerticalSpatialReferenceSystem:
        '''Create vertical SRS.
        
        :param name: Name of SRS. If .
        :param vertical_datum: Datum to be used in SRS.
        :param vertical_unit: Unit to be used in SRS. If , :py:attr:`aspose.gis.spatialreferencing.Unit.meter` will be used.
        :param vertical_axis: Axis with "up" or "down" direction, to be used in SRS. If , axis with up direction will be used.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Vertical SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_compound(name : str, head : aspose.gis.spatialreferencing.SpatialReferenceSystem, tail : aspose.gis.spatialreferencing.SpatialReferenceSystem, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.CompoundSpatialReferenceSystem:
        '''Create compound SRS.
        
        :param name: Name of new SRS.
        :param head: Head SRS of new SRS.
        :param tail: Tail SRS of new SRS.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Compound SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_local(name : str, datum : aspose.gis.spatialreferencing.LocalDatum, unit : aspose.gis.rendering.Unit, axises : List[aspose.gis.spatialreferencing.Axis], identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.LocalSpatialReferenceSystem:
        raise NotImplementedError()
    
    def validate(self, error_message : List[String]) -> bool:
        '''Determine if this SRS is valid.
        
        :param error_message: If method return , then this is description of invalidity.
        :returns: if SRS is valid,  otherwise.'''
        raise NotImplementedError()
    
    def get_axis(self, dimension : int) -> aspose.gis.spatialreferencing.Axis:
        '''Get :py:class:`aspose.gis.spatialreferencing.Axis` that describes dimension.
        
        :param dimension: Number of dimension.
        :returns: Axis that describes dimension.'''
        raise NotImplementedError()
    
    def get_unit(self, dimension : int) -> aspose.gis.rendering.Unit:
        '''Get :py:class:`aspose.gis.spatialreferencing.Unit` of dimension.
        
        :param dimension: Number of dimension.
        :returns: Unit of dimension.'''
        raise NotImplementedError()
    
    def export_to_wkt(self) -> str:
        '''Returns representation of this SRS as WKT string.
        The result WKT string will match OGC 01-009 specification, usually named "WKT1".
        
        :returns: WKT representation of this SRS.'''
        raise NotImplementedError()
    
    def try_create_transformation_to(self, target_srs : aspose.gis.spatialreferencing.SpatialReferenceSystem, value : List[aspose.gis.spatialreferencing.SpatialReferenceSystemTransformation]) -> bool:
        '''Creates transformation from this ``SpatialReferenceSystem`` to another ``SpatialReferenceSystem``.
        
        :param target_srs: Another ``SpatialReferenceSystem``.
        :param value: When this methods returns , contains a transformation; otherwise, contains .
        :returns: Transformation from this ``SpatialReferenceSystem`` to another ``SpatialReferenceSystem``.
        :returns: if transformation was created successfully;  otherwise.'''
        raise NotImplementedError()
    
    def create_transformation_to(self, target_srs : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> aspose.gis.spatialreferencing.SpatialReferenceSystemTransformation:
        '''Creates transformation from this ``SpatialReferenceSystem`` to another ``SpatialReferenceSystem``.
        
        :param target_srs: Another ``SpatialReferenceSystem``.
        :returns: Transformation from this ``SpatialReferenceSystem`` to another ``SpatialReferenceSystem``.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Name of this object.'''
        raise NotImplementedError()
    
    @property
    def epsg_code(self) -> int:
        '''If this objects identifier is EPSG identifier - return its code. Otherwise - return -1.'''
        raise NotImplementedError()
    
    @property
    def identifier(self) -> aspose.gis.spatialreferencing.Identifier:
        '''Identifier of this identifiable object.'''
        raise NotImplementedError()
    
    wgs84 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''WGS 84 (EPSG:4326) spatial reference system.'''
    web_mercator : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem
    '''Web Mercator (EPSG:3857) spatial reference system.'''
    wgs72 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''WGS 72 (EPSG:4322) spatial reference system.'''
    nad83 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''NAD 83 (EPSG:4269) spatial reference system.'''
    etrs89 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''ETRS 89 (EPSG:4258) spatial reference system.'''
    etrs_89_lambert_conformal_conic : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem
    '''ETRS 89 / Lambert Conformal Conic (EPSG:3034) spatial reference system.'''
    etrs_89_lambert_azimuthal_equal_area : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem
    '''ETRS 89 / ETRS Lambert Azimuthal Equal Area (EPSG:3035) spatial reference system.'''
    osgb36 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''OSGB 36 (EPSG:4277) spatial reference system.'''
    osgb_36_british_national_grid : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem
    '''OSGB 36 / British National Grid (EPSG:27700) spatial reference system.'''
    @property
    def is_valid(self) -> bool:
        '''Same as :py:func:`aspose.gis.spatialreferencing.SpatialReferenceSystem.validate`, but don\'t return error message.'''
        raise NotImplementedError()
    
    @property
    def type(self) -> aspose.gis.spatialreferencing.SpatialReferenceSystemType:
        '''Gets type of this SRS, see :py:class:`aspose.gis.spatialreferencing.SpatialReferenceSystemType`.'''
        raise NotImplementedError()
    
    @property
    def is_compound(self) -> bool:
        '''Returns whether this SRS is compound (a union of two SRS).
        Following combinations of SRS in compound SRS are considered valid:
        Geographic SRS + Vertical SRS, in this case type of compound SRS will be :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystemType.GEOGRAPHIC`.
        Projected SRS + Vertical SRS, in this case type of compound SRS will be :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystemType.PROJECTED`.
        If combination of SRSs differs, type of compound SRS will be :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystemType.UNKNOWN`.'''
        raise NotImplementedError()
    
    @property
    def is_single(self) -> bool:
        '''Returns whether this SRS is single (not a union of two SRS).'''
        raise NotImplementedError()
    
    @property
    def as_geographic(self) -> aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.type` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def as_projected(self) -> aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.type` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def as_geocentric(self) -> aspose.gis.spatialreferencing.GeocentricSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.GeocentricSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.type` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def as_vertical(self) -> aspose.gis.spatialreferencing.VerticalSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.VerticalSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.type` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def as_local(self) -> aspose.gis.spatialreferencing.LocalSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.LocalSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.type` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def as_compound(self) -> aspose.gis.spatialreferencing.CompoundSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.CompoundSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.is_compound` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def dimensions_count(self) -> int:
        '''Returns number of dimensions in this SRS.'''
        raise NotImplementedError()
    
    @property
    def has_prime_meridian(self) -> bool:
        '''Returns whether this SRS has prime meridian.
        This is true for every geographic, projected and geocentric SRS.'''
        raise NotImplementedError()
    
    @property
    def prime_meridian(self) -> aspose.gis.spatialreferencing.PrimeMeridian:
        '''Returns prime meridian of this SRS.'''
        raise NotImplementedError()
    
    @property
    def has_geographic_datum(self) -> bool:
        '''Determines whether this SRS has geographic datum.
        This is true for every geographic, projected and geocentric SRS.'''
        raise NotImplementedError()
    
    @property
    def geographic_datum(self) -> aspose.gis.spatialreferencing.GeographicDatum:
        '''Returns geographic datum of this SRS.'''
        raise NotImplementedError()
    

class SpatialReferenceSystemTransformation:
    '''Spatial reference system transformation transforms geometries from source spatial reference system to target spatial reference system.'''
    
    def transform(self, geometry : aspose.gis.geometries.IGeometry) -> aspose.gis.geometries.Geometry:
        '''Transforms geometry from source spatial reference system to target spatial reference system.
        
        :param geometry: Geometry to transform.
        :returns: New geometry in target spatial reference system.'''
        raise NotImplementedError()
    
    @property
    def source(self) -> aspose.gis.spatialreferencing.SpatialReferenceSystem:
        '''Source spatial reference system.'''
        raise NotImplementedError()
    
    @property
    def target(self) -> aspose.gis.spatialreferencing.SpatialReferenceSystem:
        '''Target spatial reference system.'''
        raise NotImplementedError()
    

class TransformationException:
    '''Transformation exception is thrown when error occurs during transformation of coordinate or during transformation creation.'''
    

class Unit(IdentifiableObject):
    '''Represent measurement unit.'''
    
    def apply(self, value : float) -> float:
        '''Converts argument to unit, described by this instance.
        
        :param value: Value to convert. Must be in radians or meters.
        :returns: Value, converted to this unit.'''
        raise NotImplementedError()
    
    def deapply(self, value : float) -> float:
        '''Converts argument from unit, described by this instance, to radians or meters.
        
        :param value: Value to convert.
        :returns: Value converted to radians or meters.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Name of this object.'''
        raise NotImplementedError()
    
    @property
    def epsg_code(self) -> int:
        '''If this objects identifier is EPSG identifier - return its code. Otherwise - return -1.'''
        raise NotImplementedError()
    
    @property
    def identifier(self) -> aspose.gis.spatialreferencing.Identifier:
        '''Identifier of this identifiable object.'''
        raise NotImplementedError()
    
    meter : aspose.gis.rendering.Unit
    '''Get Unit that represents meters.'''
    radian : aspose.gis.rendering.Unit
    '''Get Unit that represents radians.'''
    degree : aspose.gis.rendering.Unit
    '''Get Unit that represents degrees.'''
    @property
    def factor(self) -> float:
        '''Factor to meter, if this is length unit, factor to radian, if this is angle unit.'''
        raise NotImplementedError()
    

class VerticalDatum(IdentifiableObject):
    '''Indicates method used for vertical measurements.'''
    
    @property
    def name(self) -> str:
        '''Name of this object.'''
        raise NotImplementedError()
    
    @property
    def epsg_code(self) -> int:
        '''If this objects identifier is EPSG identifier - return its code. Otherwise - return -1.'''
        raise NotImplementedError()
    
    @property
    def identifier(self) -> aspose.gis.spatialreferencing.Identifier:
        '''Identifier of this identifiable object.'''
        raise NotImplementedError()
    
    @property
    def datum_type(self) -> int:
        '''An integer number, indicating method that had been used.'''
        raise NotImplementedError()
    

class VerticalSpatialReferenceSystem(SpatialReferenceSystem):
    '''Vertical SRS is a one dimensional SRS that describes height coordinates.'''
    
    @overload
    def is_equivalent(self, other : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> bool:
        '''Detects whether this SRS is equivalent to other SRS. :py:func:`aspose.gis.spatialreferencing.SpatialReferenceSystem.is_equivalent`.
        
        :param other: Other SRS.
        :returns: bool value, indicating whether this SRS is equivalent to other SRS.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def is_equivalent(srs1 : aspose.gis.spatialreferencing.SpatialReferenceSystem, srs2 : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> bool:
        '''Determines if two SRS are equivalent.
        Same coordinates of equivalent SRS match same place on Earth.
        Some parameters of equivalent SRS can be different, for example :py:attr:`aspose.gis.spatialreferencing.IdentifiableObject.name`.
        
        :param srs1: First SRS.
        :param srs2: Second SRS.
        :returns: bool value, indicating whether two SRS are equivalent.'''
        raise NotImplementedError()
    
    @staticmethod
    def try_create_from_wkt(wkt : str, value : List[aspose.gis.spatialreferencing.SpatialReferenceSystem]) -> bool:
        '''Creates a new ``SpatialReferenceSystem`` based on WKT (Well-Known Text) string.
        
        :param wkt: WKT string.
        :param value: When this methods returns , contains an SRS created from WKT; otherwise,
        contains .
        :returns: if SRS was successfully created;  otherwise.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_from_wkt(wkt : str) -> aspose.gis.spatialreferencing.SpatialReferenceSystem:
        '''Creates a new ``SpatialReferenceSystem`` based on WKT (Well-Known Text) string.
        
        :param wkt: WKT string.
        :returns: New ``SpatialReferenceSystem``.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_from_epsg(epsg : int) -> aspose.gis.spatialreferencing.SpatialReferenceSystem:
        '''Create a spatial reference system based the specified EPSG code.
        
        :param epsg: EPSG code of the spatial reference system.
        :returns: A new spatial reference system with the specified EPSG code.'''
        raise NotImplementedError()
    
    @staticmethod
    def try_create_from_epsg(epsg : int, value : List[aspose.gis.spatialreferencing.SpatialReferenceSystem]) -> bool:
        '''Create a spatial reference system based the specified EPSG code.
        
        :param epsg: EPSG code of the spatial reference system.
        :param value: When this methods returns , contains a SRS with the specified EPSG code; otherwise,
        contains .
        :returns: if specified EPSG code is known and SRS was created;  otherwise.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_geographic(parameters : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystemParameters, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem:
        '''Create geographic SRS from custom parameters.
        
        :param parameters: Parameters to create from.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Geographic SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_geocentric(parameters : aspose.gis.spatialreferencing.GeocentricSpatialReferenceSystemParameters, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.GeocentricSpatialReferenceSystem:
        '''Create geocentric SRS from custom parameters.
        
        :param parameters: Parameters to create from.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Geocentric SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_projected(parameters : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystemParameters, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem:
        '''Create projected SRS from custom parameters.
        
        :param parameters: Parameters to create from.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Projected SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_vertical(name : str, vertical_datum : aspose.gis.spatialreferencing.VerticalDatum, vertical_unit : aspose.gis.rendering.Unit, vertical_axis : aspose.gis.spatialreferencing.Axis, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.VerticalSpatialReferenceSystem:
        '''Create vertical SRS.
        
        :param name: Name of SRS. If .
        :param vertical_datum: Datum to be used in SRS.
        :param vertical_unit: Unit to be used in SRS. If , :py:attr:`aspose.gis.spatialreferencing.Unit.meter` will be used.
        :param vertical_axis: Axis with "up" or "down" direction, to be used in SRS. If , axis with up direction will be used.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Vertical SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_compound(name : str, head : aspose.gis.spatialreferencing.SpatialReferenceSystem, tail : aspose.gis.spatialreferencing.SpatialReferenceSystem, identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.CompoundSpatialReferenceSystem:
        '''Create compound SRS.
        
        :param name: Name of new SRS.
        :param head: Head SRS of new SRS.
        :param tail: Tail SRS of new SRS.
        :param identifier: Identifier, that will be attached to SRS. Attaching an Identifier will not modify other SRS parameters.
        Its up to you to ensure consistency of identifier and SRS parameters.
        :returns: New Compound SRS.'''
        raise NotImplementedError()
    
    @staticmethod
    def create_local(name : str, datum : aspose.gis.spatialreferencing.LocalDatum, unit : aspose.gis.rendering.Unit, axises : List[aspose.gis.spatialreferencing.Axis], identifier : aspose.gis.spatialreferencing.Identifier) -> aspose.gis.spatialreferencing.LocalSpatialReferenceSystem:
        raise NotImplementedError()
    
    def validate(self, error_message : List[String]) -> bool:
        '''Determine if this SRS is valid. See :py:func:`aspose.gis.spatialreferencing.SpatialReferenceSystem.validate` for validity description.
        
        :param error_message: Description of invalidity (if result is )
        :returns: If this SRS is valid - , otherwise - .'''
        raise NotImplementedError()
    
    def get_axis(self, dimension : int) -> aspose.gis.spatialreferencing.Axis:
        '''Get :py:class:`aspose.gis.spatialreferencing.Axis` that describes dimension.
        
        :param dimension: Number of dimension.
        :returns: Axis that describes dimension.'''
        raise NotImplementedError()
    
    def get_unit(self, dimension : int) -> aspose.gis.rendering.Unit:
        '''Get :py:class:`aspose.gis.spatialreferencing.Unit` of dimension.
        
        :param dimension: Number of dimension.
        :returns: Unit of dimension.'''
        raise NotImplementedError()
    
    def export_to_wkt(self) -> str:
        '''Returns representation of this SRS as WKT string.
        The result WKT string will match OGC 01-009 specification, usually named "WKT1".
        
        :returns: WKT representation of this SRS.'''
        raise NotImplementedError()
    
    def try_create_transformation_to(self, target_srs : aspose.gis.spatialreferencing.SpatialReferenceSystem, value : List[aspose.gis.spatialreferencing.SpatialReferenceSystemTransformation]) -> bool:
        '''Creates transformation from this ``SpatialReferenceSystem`` to another ``SpatialReferenceSystem``.
        
        :param target_srs: Another ``SpatialReferenceSystem``.
        :param value: When this methods returns , contains a transformation; otherwise, contains .
        :returns: Transformation from this ``SpatialReferenceSystem`` to another ``SpatialReferenceSystem``.
        :returns: if transformation was created successfully;  otherwise.'''
        raise NotImplementedError()
    
    def create_transformation_to(self, target_srs : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> aspose.gis.spatialreferencing.SpatialReferenceSystemTransformation:
        '''Creates transformation from this ``SpatialReferenceSystem`` to another ``SpatialReferenceSystem``.
        
        :param target_srs: Another ``SpatialReferenceSystem``.
        :returns: Transformation from this ``SpatialReferenceSystem`` to another ``SpatialReferenceSystem``.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Name of this object.'''
        raise NotImplementedError()
    
    @property
    def epsg_code(self) -> int:
        '''If this objects identifier is EPSG identifier - return its code. Otherwise - return -1.'''
        raise NotImplementedError()
    
    @property
    def identifier(self) -> aspose.gis.spatialreferencing.Identifier:
        '''Identifier of this identifiable object.'''
        raise NotImplementedError()
    
    wgs84 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''WGS 84 (EPSG:4326) spatial reference system.'''
    web_mercator : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem
    '''Web Mercator (EPSG:3857) spatial reference system.'''
    wgs72 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''WGS 72 (EPSG:4322) spatial reference system.'''
    nad83 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''NAD 83 (EPSG:4269) spatial reference system.'''
    etrs89 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''ETRS 89 (EPSG:4258) spatial reference system.'''
    etrs_89_lambert_conformal_conic : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem
    '''ETRS 89 / Lambert Conformal Conic (EPSG:3034) spatial reference system.'''
    etrs_89_lambert_azimuthal_equal_area : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem
    '''ETRS 89 / ETRS Lambert Azimuthal Equal Area (EPSG:3035) spatial reference system.'''
    osgb36 : aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem
    '''OSGB 36 (EPSG:4277) spatial reference system.'''
    osgb_36_british_national_grid : aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem
    '''OSGB 36 / British National Grid (EPSG:27700) spatial reference system.'''
    @property
    def is_valid(self) -> bool:
        '''Same as :py:func:`aspose.gis.spatialreferencing.SpatialReferenceSystem.validate`, but don\'t return error message.'''
        raise NotImplementedError()
    
    @property
    def type(self) -> aspose.gis.spatialreferencing.SpatialReferenceSystemType:
        '''Return :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystemType.VERTICAL`.'''
        raise NotImplementedError()
    
    @property
    def is_compound(self) -> bool:
        '''Returns whether this SRS is compound (a union of two SRS).
        Following combinations of SRS in compound SRS are considered valid:
        Geographic SRS + Vertical SRS, in this case type of compound SRS will be :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystemType.GEOGRAPHIC`.
        Projected SRS + Vertical SRS, in this case type of compound SRS will be :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystemType.PROJECTED`.
        If combination of SRSs differs, type of compound SRS will be :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystemType.UNKNOWN`.'''
        raise NotImplementedError()
    
    @property
    def is_single(self) -> bool:
        '''Returns whether this SRS is single (not a union of two SRS).'''
        raise NotImplementedError()
    
    @property
    def as_geographic(self) -> aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.type` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def as_projected(self) -> aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.type` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def as_geocentric(self) -> aspose.gis.spatialreferencing.GeocentricSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.GeocentricSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.type` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def as_vertical(self) -> aspose.gis.spatialreferencing.VerticalSpatialReferenceSystem:
        '''Returns this SRS.'''
        raise NotImplementedError()
    
    @property
    def as_local(self) -> aspose.gis.spatialreferencing.LocalSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.LocalSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.type` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def as_compound(self) -> aspose.gis.spatialreferencing.CompoundSpatialReferenceSystem:
        '''Returns this SRS converted to :py:class:`aspose.gis.spatialreferencing.CompoundSpatialReferenceSystem`.
        Use :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.is_compound` to find out if conversion is possible.'''
        raise NotImplementedError()
    
    @property
    def dimensions_count(self) -> int:
        '''Returns 1, since vertical SRS is always one dimensional.'''
        raise NotImplementedError()
    
    @property
    def has_prime_meridian(self) -> bool:
        '''Returns , since Vertical SRS doesn\'t have prime meridian.'''
        raise NotImplementedError()
    
    @property
    def prime_meridian(self) -> aspose.gis.spatialreferencing.PrimeMeridian:
        '''Throws :py:class:`System.InvalidOperationException`, since Vertical SRS doesn\'t have prime meridian.'''
        raise NotImplementedError()
    
    @property
    def has_geographic_datum(self) -> bool:
        '''Returns , since Vertical SRS doesn\'t have geographic datum.'''
        raise NotImplementedError()
    
    @property
    def geographic_datum(self) -> aspose.gis.spatialreferencing.GeographicDatum:
        '''Throws :py:class:`System.InvalidOperationException`, since Vertical SRS doesn\'t have geographic datum.'''
        raise NotImplementedError()
    
    @property
    def vertical_unit(self) -> aspose.gis.rendering.Unit:
        '''Unit that is used in this SRS.'''
        raise NotImplementedError()
    
    @property
    def vertical_datum(self) -> aspose.gis.spatialreferencing.VerticalDatum:
        '''Datum that is used in this SRS.'''
        raise NotImplementedError()
    

class AxisDirection:
    '''Axis direction defines direction at which axis is pointing.'''
    
    INVALID : AxisDirection
    '''Default value.'''
    NORTH : AxisDirection
    '''Axis pointing to the north.'''
    SOUTH : AxisDirection
    '''Axis pointing to the south.'''
    EAST : AxisDirection
    '''Axis pointing to the east.'''
    WEST : AxisDirection
    '''Axis pointing to the west.'''
    UP : AxisDirection
    '''Axis pointing up.'''
    DOWN : AxisDirection
    '''Axis pointing down.'''
    OTHER : AxisDirection
    '''Axis pointing to some other direction. This might be \'X\' axis in geocentric SRS (it points to prime meridian).'''

class GeocentricAxisesOrder:
    '''Represents order of axises in geocentric SRS.'''
    
    INVALID : GeocentricAxisesOrder
    '''Geocentric SRS is invalid and axises order can not be determined.'''
    XYZ : GeocentricAxisesOrder
    '''Order is X, Y, Z.'''
    XZY : GeocentricAxisesOrder
    '''Order is X, Z, Y.'''
    YXZ : GeocentricAxisesOrder
    '''Order is Y, X, Z.'''
    YZX : GeocentricAxisesOrder
    '''Order is Y, Z, X.'''
    ZXY : GeocentricAxisesOrder
    '''Order is Z, X, Y.'''
    ZYX : GeocentricAxisesOrder
    '''Order is Z, Y, X.'''

class GeographicAxisesOrder:
    '''Represents order of axises in geographic SRS.'''
    
    INVALID : GeographicAxisesOrder
    '''Geographic SRS is invalid and axises order can not be determined.'''
    LONGITUDE_LATITUDE : GeographicAxisesOrder
    '''Order is (Longitude, Latitude).'''
    LATITUDE_LONGITUDE : GeographicAxisesOrder
    '''Order is (Latitude, Longitude).'''

class ParameterType:
    '''Determines type of parameter in :py:class:`aspose.gis.spatialreferencing.Projection`.'''
    
    OTHER : ParameterType
    '''Type of parameter is unknown or none of the below.'''
    LINEAR : ParameterType
    '''Type of parameter is linear (for example "false_easting").'''
    ANGULAR : ParameterType
    '''Type of parameter is angular (for example "longitude_of_origin").'''

class ProjectedAxisesOrder:
    '''Represents order of axises in geographic SRS.'''
    
    INVALID : ProjectedAxisesOrder
    '''Projected SRS is invalid and axises order can not be determined.'''
    XY : ProjectedAxisesOrder
    '''Order is (X, Y). (X is horizontal (East, West), Y is vertical (North, South)).'''
    YX : ProjectedAxisesOrder
    '''Order is (Y, X). (X is horizontal axis (East, West), Y is vertical axis (North, South)).'''

class SpatialReferenceSystemType:
    '''Represents type of spatial reference system.'''
    
    UNKNOWN : SpatialReferenceSystemType
    '''Default value.
    Can be returned from :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.type` if this is a compound SRS with invalid combination of
    underlying SRSs. See :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.is_compound`.'''
    GEOGRAPHIC : SpatialReferenceSystemType
    '''Geographic SRS is based on angular longitude and angular latitude.
    Geographic SRS can be converted to :py:class:`aspose.gis.spatialreferencing.GeographicSpatialReferenceSystem`
    via :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.as_geographic` method.'''
    GEOCENTRIC : SpatialReferenceSystemType
    '''Geocentric SRS is three dimensional cartesian SRS with origin at Earth center.
    Geocentric SRS can be converted to :py:class:`aspose.gis.spatialreferencing.GeocentricSpatialReferenceSystem`
    via :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.as_geocentric` method.'''
    PROJECTED : SpatialReferenceSystemType
    '''Projected SRS is based on linear X and linear Y. It is the result of application a projection on a :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystemType.GEOGRAPHIC` SRS.
    Projected SRS can be converted to :py:class:`aspose.gis.spatialreferencing.ProjectedSpatialReferenceSystem`
    via :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.as_projected` method.'''
    VERTICAL : SpatialReferenceSystemType
    '''Vertical SRS describes linear height coordinate.
    Vertical SRS can be converted to :py:class:`aspose.gis.spatialreferencing.VerticalSpatialReferenceSystem`
    via :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.as_vertical` method.'''
    LOCAL : SpatialReferenceSystemType
    '''Local SRS relates coordinates to some object, other them Earth.
    Local SRS can be converted to :py:class:`aspose.gis.spatialreferencing.LocalSpatialReferenceSystem`
    via :py:attr:`aspose.gis.spatialreferencing.SpatialReferenceSystem.as_local` method.'''

