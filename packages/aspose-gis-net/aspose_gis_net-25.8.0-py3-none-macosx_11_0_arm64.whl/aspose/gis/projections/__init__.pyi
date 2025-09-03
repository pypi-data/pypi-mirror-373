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

class EllipsoidProperties:
    
    @property
    def is_valid(self) -> bool:
        raise NotImplementedError()
    
    @property
    def is_sphere(self) -> bool:
        raise NotImplementedError()
    
    @property
    def semi_major_axis(self) -> float:
        raise NotImplementedError()
    
    @property
    def semi_minor_axis(self) -> float:
        raise NotImplementedError()
    
    @property
    def inverse_flattening(self) -> float:
        raise NotImplementedError()
    
    @property
    def first_eccentricity(self) -> float:
        raise NotImplementedError()
    
    @property
    def first_eccentricity_squared(self) -> float:
        raise NotImplementedError()
    

class Projection:
    
    @staticmethod
    def create(projection_method_id : aspose.gis.projections.ProjectionMethodIdentifier, parameters : aspose.gis.projections.ProjectionParameters) -> aspose.gis.projections.Projection:
        raise NotImplementedError()
    
    def to_projected(self, longitude : float, latitude : float, easting : List[Double], northing : List[Double]) -> bool:
        raise NotImplementedError()
    
    def to_geographic(self, easting : float, northing : float, longitude : List[Double], latitude : List[Double]) -> bool:
        raise NotImplementedError()
    

class ProjectionException:
    

class ProjectionParameters:
    
    @property
    def ellipsoid_properties(self) -> aspose.gis.projections.EllipsoidProperties:
        raise NotImplementedError()
    
    @ellipsoid_properties.setter
    def ellipsoid_properties(self, value : aspose.gis.projections.EllipsoidProperties) -> None:
        raise NotImplementedError()
    
    @property
    def false_easting(self) -> float:
        raise NotImplementedError()
    
    @false_easting.setter
    def false_easting(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def false_northing(self) -> float:
        raise NotImplementedError()
    
    @false_northing.setter
    def false_northing(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def latitude_of_origin(self) -> float:
        raise NotImplementedError()
    
    @latitude_of_origin.setter
    def latitude_of_origin(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def longitude_of_origin(self) -> float:
        raise NotImplementedError()
    
    @longitude_of_origin.setter
    def longitude_of_origin(self, value : float) -> None:
        raise NotImplementedError()
    
    @property
    def scale_factor(self) -> Optional[float]:
        raise NotImplementedError()
    
    @scale_factor.setter
    def scale_factor(self, value : Optional[float]) -> None:
        raise NotImplementedError()
    
    @property
    def latitude_of_first_standard_parallel(self) -> Optional[float]:
        raise NotImplementedError()
    
    @latitude_of_first_standard_parallel.setter
    def latitude_of_first_standard_parallel(self, value : Optional[float]) -> None:
        raise NotImplementedError()
    
    @property
    def latitude_of_second_standard_parallel(self) -> Optional[float]:
        raise NotImplementedError()
    
    @latitude_of_second_standard_parallel.setter
    def latitude_of_second_standard_parallel(self, value : Optional[float]) -> None:
        raise NotImplementedError()
    
    @property
    def latitude_of_pseudo_standard_parallel(self) -> Optional[float]:
        raise NotImplementedError()
    
    @latitude_of_pseudo_standard_parallel.setter
    def latitude_of_pseudo_standard_parallel(self, value : Optional[float]) -> None:
        raise NotImplementedError()
    
    @property
    def azimuth(self) -> Optional[float]:
        raise NotImplementedError()
    
    @azimuth.setter
    def azimuth(self, value : Optional[float]) -> None:
        raise NotImplementedError()
    
    @property
    def rectified_grid_angle(self) -> Optional[float]:
        raise NotImplementedError()
    
    @rectified_grid_angle.setter
    def rectified_grid_angle(self, value : Optional[float]) -> None:
        raise NotImplementedError()
    
    @property
    def height_of_origin(self) -> float:
        raise NotImplementedError()
    
    @height_of_origin.setter
    def height_of_origin(self, value : float) -> None:
        raise NotImplementedError()
    

class ProjectionMethodIdentifier:
    
    INVALID : ProjectionMethodIdentifier
    CYLINDRICAL_EQUAL_AREA : ProjectionMethodIdentifier
    BONNE : ProjectionMethodIdentifier
    CASSINI_SOLDNER : ProjectionMethodIdentifier
    NEW_ZEALAND_MAP_GRID : ProjectionMethodIdentifier
    TRANSVERSE_MERCATOR : ProjectionMethodIdentifier
    TRANSVERSE_MERCATOR_SOUTH_ORIENTED : ProjectionMethodIdentifier
    MERCATOR_ONE_STANDARD_PARALLEL : ProjectionMethodIdentifier
    MERCATOR_TWO_STANDARD_PARALLELS : ProjectionMethodIdentifier
    OBLIQUE_STEREOGRAPHIC : ProjectionMethodIdentifier
    STEREOGRAPHIC : ProjectionMethodIdentifier
    POLAR_STEREOGRAPHIC : ProjectionMethodIdentifier
    EQUIRECTANGULAR : ProjectionMethodIdentifier
    GNOMONIC : ProjectionMethodIdentifier
    ORTHOGRAPHIC : ProjectionMethodIdentifier
    LAMBERT_AZIMUTHAL_EQUAL_AREA : ProjectionMethodIdentifier
    AZIMUTHAL_EQUIDISTANT : ProjectionMethodIdentifier
    AZIMUTHAL_EQUIDISTANT_GUAM : ProjectionMethodIdentifier
    POLYCONIC : ProjectionMethodIdentifier
    ALBERS_CONIC_EQUAL_AREA : ProjectionMethodIdentifier
    LAMBERT_CONFORMAL_CONIC_ONE_STANDARD_PARALLEL : ProjectionMethodIdentifier
    LAMBERT_CONFORMAL_CONIC_TWO_STANDARD_PARALLELS : ProjectionMethodIdentifier
    LAMBERT_CONFORMAL_CONIC_BELGIUM : ProjectionMethodIdentifier
    HOTINE_OBLIQUE_MERCATOR : ProjectionMethodIdentifier
    HOTINE_OBLIQUE_MERCATOR_AZIMUTH_CENTER : ProjectionMethodIdentifier
    KROVAK : ProjectionMethodIdentifier
    TUNISIA_MINING_GRID : ProjectionMethodIdentifier
    COLOMBIA_URBAN : ProjectionMethodIdentifier
    PSEUDO_PLATE_CARREE : ProjectionMethodIdentifier
    GOOGLE_MERCATOR : ProjectionMethodIdentifier
    LABORDE_OBLIQUE_MERCATOR : ProjectionMethodIdentifier
    SWISS_OBLIQUE_CYLINDRICAL : ProjectionMethodIdentifier

