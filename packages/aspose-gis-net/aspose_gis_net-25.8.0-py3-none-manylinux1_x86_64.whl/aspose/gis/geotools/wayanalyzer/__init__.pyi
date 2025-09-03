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

class WayLayerGenerator:
    '''Way layers generator'''
    
    def add_road(self, start_point : aspose.gis.geometries.Point, end_point : aspose.gis.geometries.Point, velocity : float) -> None:
        '''Add road to the cell
        
        :param start_point: the start point.
        :param end_point: the end point.
        :param velocity: the velocity.'''
        raise NotImplementedError()
    
    def add_block(self, x : int, y : int, size_x : int, size_y : int, velocity : float) -> None:
        '''Add block to the cell
        
        :param x: the x of block
        :param y: the y of block
        :param size_x: the sizeX of block
        :param size_y: the sizeY of block
        :param velocity: the velocity of block'''
        raise NotImplementedError()
    
    def find_the_way(self, start_point : aspose.gis.geometries.Point, goal_point : aspose.gis.geometries.Point, radius : float) -> aspose.gis.geometries.LineString:
        '''Find the way from start point to goal
        
        :param start_point: the start Point
        :param goal_point: the goa lPoint
        :param radius: the radius to look for
        :returns: The Found Way.'''
        raise NotImplementedError()
    

class WayOptions:
    '''Options to find a way on the map'''
    
    def clone(self) -> aspose.gis.geotools.wayanalyzer.WayOptions:
        '''Clone object to one another.
        
        :returns: Clone object to one another :py:class:`aspose.gis.geotools.wayanalyzer.WayOptions`.'''
        raise NotImplementedError()
    
    @property
    def start_point(self) -> aspose.gis.geometries.Point:
        '''Start point of the way'''
        raise NotImplementedError()
    
    @start_point.setter
    def start_point(self, value : aspose.gis.geometries.Point) -> None:
        '''Start point of the way'''
        raise NotImplementedError()
    
    @property
    def goal_point(self) -> aspose.gis.geometries.Point:
        '''Goal point of the way'''
        raise NotImplementedError()
    
    @goal_point.setter
    def goal_point(self, value : aspose.gis.geometries.Point) -> None:
        '''Goal point of the way'''
        raise NotImplementedError()
    
    @property
    def scale(self) -> int:
        '''Scale of the map'''
        raise NotImplementedError()
    
    @scale.setter
    def scale(self, value : int) -> None:
        '''Scale of the map'''
        raise NotImplementedError()
    
    @property
    def radius(self) -> float:
        '''Radius for search'''
        raise NotImplementedError()
    
    @radius.setter
    def radius(self, value : float) -> None:
        '''Radius for search'''
        raise NotImplementedError()
    
    @property
    def is_move_only_road(self) -> bool:
        '''Find the way only by road'''
        raise NotImplementedError()
    
    @is_move_only_road.setter
    def is_move_only_road(self, value : bool) -> None:
        '''Find the way only by road'''
        raise NotImplementedError()
    
    @property
    def is_scale_fixed(self) -> bool:
        '''Is scale constant'''
        raise NotImplementedError()
    

