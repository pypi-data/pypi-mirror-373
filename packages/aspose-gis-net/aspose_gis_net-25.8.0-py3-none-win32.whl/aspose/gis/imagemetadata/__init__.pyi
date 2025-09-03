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

class GeoLocation:
    '''The class representing a geographic location'''
    
    @property
    def latitude(self) -> float:
        '''Latitude of GeoLocation'''
        raise NotImplementedError()
    
    @property
    def longitude(self) -> float:
        '''Longitude of GeoLocation'''
        raise NotImplementedError()
    

class ImageData:
    '''Class containing all extracted supported EXIF tags'''
    
    @property
    def artist(self) -> str:
        '''EXIF tag Artist'''
        raise NotImplementedError()
    
    @property
    def description(self) -> str:
        '''EXIF tag ImageDescription'''
        raise NotImplementedError()
    
    @property
    def modify_date(self) -> datetime:
        '''EXIF tag ModifyDate (DataTime)'''
        raise NotImplementedError()
    
    @property
    def image_size(self) -> aspose.gis.imagemetadata.ImageSize:
        '''EXIF tags tags ImageWidth and ImageHeight'''
        raise NotImplementedError()
    
    @property
    def geo_location(self) -> aspose.gis.imagemetadata.GeoLocation:
        '''EXIF tags tags GPSLatitude, GPSLongitude'''
        raise NotImplementedError()
    

class ImageMetadataReader:
    '''Class for editing, adding some EXIF tags'''
    
    @overload
    def save(self, file_name : str) -> None:
        '''Save to new file since the original one is locked for changes
        
        :param file_name: Full name of the destination file'''
        raise NotImplementedError()
    
    @overload
    def save(self, file_name : str, format : aspose.gis.imagemetadata.ImageFormat) -> None:
        '''Save to new file since the original one is locked for changes
        
        :param file_name: Full name of the destination file
        :param format: Specifies the format for saving'''
        raise NotImplementedError()
    
    @overload
    def save(self, stream : io.RawIOBase) -> None:
        '''Saving changes to a separate stream
        
        :param stream: Destination stream'''
        raise NotImplementedError()
    
    @overload
    def save(self, stream : io.RawIOBase, format : aspose.gis.imagemetadata.ImageFormat) -> None:
        '''Saving changes to a separate stream
        
        :param stream: Destination stream
        :param format: Specifies the format for saving'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def get_reader(file_name : str) -> aspose.gis.imagemetadata.ImageMetadataReader:
        '''Creates a reader instance for EXIF tags
        
        :param file_name: Full name of the image file.
        :returns: Metadata reader instance'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def get_reader(stream : io.RawIOBase) -> aspose.gis.imagemetadata.ImageMetadataReader:
        '''Creates a reader instance for EXIF tags
        
        :param stream: Image data source stream
        :returns: Metadata reader instance'''
        raise NotImplementedError()
    
    def try_get_artist(self, artist : List[String]) -> bool:
        '''It tries to find EXIF tag Artist, if the tag is not found it returns null
        
        :param artist: The artist.
        :returns: True if successful'''
        raise NotImplementedError()
    
    def set_artist(self, artist : str) -> None:
        '''Saving the EXIF Artist tag, adding or overwriting the data.
        
        :param artist: The artist.'''
        raise NotImplementedError()
    
    def try_get_description(self, description : List[String]) -> bool:
        '''It tries to find EXIF tag ImageDescription, if the tag is not found it returns null
        
        :param description: The description.
        :returns: True if successful'''
        raise NotImplementedError()
    
    def set_description(self, description : str) -> None:
        '''Saving the EXIF ImageDescription tag, adding or overwriting the data.
        
        :param description: The description.'''
        raise NotImplementedError()
    
    def try_get_modify_date(self, modify_date : List[datetime]) -> bool:
        '''It tries to find EXIF tag ModifyDate (DataTime), if the tag is not found it returns default DataTime value
        
        :param modify_date: The modify date.
        :returns: True if successful'''
        raise NotImplementedError()
    
    def set_modify_date(self, modify_date : datetime) -> None:
        '''Saving the EXIF ModifyDate (DataTime) tag, adding or overwriting the data.
        
        :param modify_date: The modify date.'''
        raise NotImplementedError()
    
    def try_get_image_size(self, image_size : List[aspose.gis.imagemetadata.ImageSize]) -> bool:
        '''It tries to find EXIF set of tags ImageWidth and ImageHeight, if the tags does not presented it returns null
        
        :param image_size: Size of the image.
        :returns: True if successful'''
        raise NotImplementedError()
    
    def set_image_size(self, width : int, height : int) -> None:
        '''Saving the EXIF ImageWidth and ImageHeight tags, adding or overwriting the data.
        
        :param width: The width.
        :param height: The height.'''
        raise NotImplementedError()
    
    def try_get_geo_location(self, geo_location : List[aspose.gis.imagemetadata.GeoLocation]) -> bool:
        '''It tries to find EXIF set of tags GPSLatitudeRef, GPSLongitudeRef, GPSLatitude, GPSLongitude, if the tags does not presented it returns null
        
        :param geo_location: The geo location.
        :returns: True if successful'''
        raise NotImplementedError()
    
    def set_geo_location(self, latitude : float, longitude : float) -> None:
        '''Saving the EXIF GPSLatitudeRef, GPSLongitudeRef, GPSLatitude and GPSLongitude tags, adding or overwriting the data.
        
        :param latitude: The latitude.
        :param longitude: The longitude.'''
        raise NotImplementedError()
    
    def read_data(self) -> aspose.gis.imagemetadata.ImageData:
        '''Extracts all supported EXIF tags
        
        :returns: ImageData that represented set of supported tags'''
        raise NotImplementedError()
    

class ImageSize:
    '''The class representing image size'''
    
    @property
    def width(self) -> int:
        '''Width of Image'''
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        '''Height of Image'''
        raise NotImplementedError()
    

class ImageFormat:
    '''Specifies the file format of the image.'''
    
    MEMORY_BMP : ImageFormat
    '''MemoryBmp image format'''
    BMP : ImageFormat
    '''Bmp image format'''
    EMF : ImageFormat
    '''Emf image format'''
    WMF : ImageFormat
    '''Wmf image format'''
    GIF : ImageFormat
    '''Gif image format'''
    JPEG : ImageFormat
    '''Jpeg image format'''
    PNG : ImageFormat
    '''Png image format'''
    TIFF : ImageFormat
    '''Tiff image format'''
    EXIF : ImageFormat
    '''Exif image format'''
    ICON : ImageFormat
    '''Icon image format'''

