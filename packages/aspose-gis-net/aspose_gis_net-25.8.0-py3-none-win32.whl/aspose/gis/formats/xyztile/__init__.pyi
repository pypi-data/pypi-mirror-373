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

class XyzConnection:
    '''A connection for the XyzTiles format.'''
    
    @property
    def url(self) -> str:
        '''Url template.'''
        raise NotImplementedError()
    

class XyzTiles(aspose.gis.raster.web.WebTiles):
    '''A XyzTiles provide access to :py:class:`Aspose.Gis.Formats.XyzTile.XyzTile` objects.'''
    
    @overload
    def get_tiles(self, zoom : int, extent : aspose.gis.Extent) -> Iterable[aspose.gis.raster.web.WebTile]:
        '''Loads tiles by the spatial bounding box and zoom level.
        
        :param zoom: The zoom level for loading tiles. The highest zoom level is 0. Most tile providers have about 22 maximum zoom levels.
        :param extent: The bounding box to load tiles. The Wgs84 spatial reference will be used if it is missed.
        :returns: The web tiles.'''
        raise NotImplementedError()
    
    @overload
    def get_tiles(self, zoom : int, extent : aspose.gis.Extent, tile_size : int) -> Iterable[aspose.gis.raster.web.WebTile]:
        '''Loads tiles by the spatial bounding box and zoom level.
        
        :param zoom: The zoom level for loading tiles. The highest zoom level is 0. Most tile providers have about 22 maximum zoom levels.
        :param extent: The bounding box to load tiles. The Wgs84 spatial reference will be used if it is missed.
        :param tile_size: Size of tiles, by default is 256 (it is standard for tiles size)
        :returns: The web tiles.'''
        raise NotImplementedError()
    
    @overload
    def get_tile(self, zoom : int, x : int, y : int) -> aspose.gis.raster.web.WebTile:
        '''Loads the specified tile.
        
        :param zoom: The zoom level for loading tiles. The highest zoom level is 0. Most tile providers have about 22 maximum zoom levels.
        :param x: An x-column of a tile.
        :param y: A y-row of a tile.
        :returns: The web tile.'''
        raise NotImplementedError()
    
    @overload
    def get_tile(self, zoom : int, x : int, y : int, tile_size : int) -> aspose.gis.raster.web.WebTile:
        '''Loads the specified tile.
        
        :param zoom: The zoom level for loading tiles. The highest zoom level is 0. Most tile providers have about 22 maximum zoom levels.
        :param x: An x-column of a tile.
        :param y: A y-row of a tile.
        :param tile_size: Size of tiles, by default is 256 (it is standard for tiles size)
        :returns: The web tile.'''
        raise NotImplementedError()
    

class XyzTilesDriver(aspose.gis.Driver):
    '''A driver for the XYZ tiled web maps.'''
    
    def open_layer(self, connection : aspose.gis.formats.xyztile.XyzConnection) -> aspose.gis.formats.xyztile.XyzTiles:
        '''Opens the tiles set.
        
        :param connection: A connection for the XyzTiles format.
        :returns: An instance of :py:class:`aspose.gis.formats.xyztile.XyzTiles`.'''
        raise NotImplementedError()
    

