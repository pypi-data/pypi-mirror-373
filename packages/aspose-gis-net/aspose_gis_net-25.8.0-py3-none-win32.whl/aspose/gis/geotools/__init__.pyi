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

class GeneratorTiles:
    '''Generator of tiles'''
    
    @overload
    @staticmethod
    def generate_tiles(layers : Iterable[aspose.gis.VectorLayer], out_directory : str, zoom : int, options : aspose.gis.geotools.GeneratorTilesRenderOptions) -> None:
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def generate_tiles(layers : Iterable[aspose.gis.VectorLayer], out_directory : str, zoom : int, extent : aspose.gis.Extent, options : aspose.gis.geotools.GeneratorTilesRenderOptions) -> None:
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def generate_tiles(layer : aspose.gis.VectorLayer, out_directory : str, zoom : int, options : aspose.gis.geotools.GeneratorTilesRenderOptions) -> None:
        '''Generate tiles with zoom to output directory
        
        :param layer: Imput layer
        :param out_directory: Output directory
        :param zoom: Zoom level for tiles
        :param options: Options to render tiles'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def generate_tiles(layer : aspose.gis.VectorLayer, out_directory : str, zoom : int, extent : aspose.gis.Extent, options : aspose.gis.geotools.GeneratorTilesRenderOptions) -> None:
        '''Generate tiles with zoom to output directory
        
        :param layer: Imput layer
        :param out_directory: Output directory
        :param zoom: Zoom level for tiles
        :param extent: The bounding box to render tiles
        :param options: Options to render tiles'''
        raise NotImplementedError()
    

class GeneratorTilesRenderOptions:
    '''Options to render tiles'''
    
    @property
    def tile_size(self) -> float:
        '''Size of tile'''
        raise NotImplementedError()
    
    @tile_size.setter
    def tile_size(self, value : float) -> None:
        '''Size of tile'''
        raise NotImplementedError()
    
    @property
    def tile_name_template(self) -> str:
        '''Tile name template'''
        raise NotImplementedError()
    
    @tile_name_template.setter
    def tile_name_template(self, value : str) -> None:
        '''Tile name template'''
        raise NotImplementedError()
    
    @property
    def background_color(self) -> aspose.pydrawing.Color:
        '''Background color'''
        raise NotImplementedError()
    
    @background_color.setter
    def background_color(self, value : aspose.pydrawing.Color) -> None:
        '''Background color'''
        raise NotImplementedError()
    
    @property
    def geometry_symbolizer(self) -> aspose.gis.rendering.symbolizers.MixedGeometrySymbolizer:
        '''Applies correct symbolizer to a feature geometry according to its geometry type'''
        raise NotImplementedError()
    
    @geometry_symbolizer.setter
    def geometry_symbolizer(self, value : aspose.gis.rendering.symbolizers.MixedGeometrySymbolizer) -> None:
        '''Applies correct symbolizer to a feature geometry according to its geometry type'''
        raise NotImplementedError()
    

class GeoGenerator:
    '''Generator of random points, lines and polygons on given planes.'''
    
    @staticmethod
    def produce_points(rect : aspose.gis.Extent, options : aspose.gis.geotools.PointGeneratorOptions) -> Iterable[aspose.gis.geometries.IGeometry]:
        '''Creates an array of points belonging to the specified area.
        
        :param rect: Specified area (see :py:class:`aspose.gis.Extent`).
        :param options: Point creation options (see :py:class:`aspose.gis.geotools.PointGeneratorOptions`).
        :returns: Array of points (see enumeration of :py:class:`aspose.gis.geometries.IGeometry`).'''
        raise NotImplementedError()
    
    @staticmethod
    def produce_lines(rect : aspose.gis.Extent, options : aspose.gis.geotools.LineGeneratorOptions) -> Iterable[aspose.gis.geometries.ILineString]:
        '''Creates a new ILineString Enumerator with a given number of random items, all of them within a given extent.
        
        :param rect: Specified area (see :py:class:`aspose.gis.Extent`)
        :param options: Line creation options (see :py:class:`aspose.gis.geotools.LineGeneratorOptions`)
        :returns: Array of lines (see enumeration of :py:class:`aspose.gis.geometries.ILineString`)'''
        raise NotImplementedError()
    
    @staticmethod
    def produce_polygons(rect : aspose.gis.Extent, options : aspose.gis.geotools.PolygonGeneratorOptions) -> Iterable[aspose.gis.geometries.IPolygon]:
        '''Creates a new IPolygon Enumerator with a given number of random items, all of them within a given extent.
        
        :param rect: Specified area (see :py:class:`aspose.gis.Extent`)
        :param options: Polygon creation options (see :py:class:`aspose.gis.geotools.PolygonGeneratorOptions`)
        :returns: Array of polygons (see enumeration of :py:class:`aspose.gis.geometries.IPolygon`)'''
        raise NotImplementedError()
    
    @staticmethod
    def produce_stars(rect : aspose.gis.Extent, options : aspose.gis.geotools.StarGeneratorOptions) -> Iterable[aspose.gis.geometries.IPolygon]:
        '''Creates an array of stars, all of them within a given extent.
        
        :param rect: Specified area (see :py:class:`aspose.gis.Extent`)
        :param options: Polygon creation options (see :py:class:`aspose.gis.geotools.StarGeneratorOptions`)
        :returns: Array of stars (see enumeration of :py:class:`aspose.gis.geometries.IPolygon`)'''
        raise NotImplementedError()
    

class GeometryOperations:
    '''The geometry operations class provides additional geoprocessing algorithms for geometries.'''
    
    @overload
    @staticmethod
    def build_centerline(sites : Iterable[aspose.gis.geometries.Point]) -> List[aspose.gis.geometries.LineString]:
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def build_centerline(polygon : aspose.gis.geometries.Polygon) -> List[aspose.gis.geometries.LineString]:
        '''Build centerline diagram for polygon
        
        :param polygon: Polygon for centerline diagram
        :returns: Collection of centerline edges'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def get_centerline_length(sites : Iterable[aspose.gis.geometries.Point]) -> float:
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def get_centerline_length(polygon : aspose.gis.geometries.Polygon) -> float:
        '''Get centerline Length
        
        :param polygon: Polygon for centerline diagram
        :returns: Length of centerline edges'''
        raise NotImplementedError()
    
    @staticmethod
    def create_midpoints(geometry : aspose.gis.geometries.IGeometry) -> aspose.gis.geometries.IGeometry:
        '''Create midpoints by adding a new point in the middle to each segment.
        
        :param geometry: Geometry for processing.
        :returns: The geometry after processing.'''
        raise NotImplementedError()
    
    @staticmethod
    def close_linear_ring(geometry : aspose.gis.geometries.IGeometry) -> aspose.gis.geometries.IGeometry:
        '''Closes geometric segments in rings if it needs.
        
        :param geometry: Geometry for closing.
        :returns: The geometry after closing.'''
        raise NotImplementedError()
    
    @staticmethod
    def delete_near_points(geometry : aspose.gis.geometries.IGeometry, options : aspose.gis.geotools.NearPointsCleanerOptions) -> aspose.gis.geometries.IGeometry:
        '''Delete points that are too close to each other.
        
        :param geometry: Geometry for deleting the nearest points.
        :param options: Options for deleting the nearest points.
        :returns: The geometry after deleting nearest point.'''
        raise NotImplementedError()
    
    @staticmethod
    def simplify_segments(geometry : aspose.gis.geometries.IGeometry, options : aspose.gis.geotools.SimplifySegmentsOptions) -> aspose.gis.geometries.IGeometry:
        '''Delete points lying on the same segment.
        
        :param geometry: Geometry for deleting extra point
        :param options: Options for deleting extra point
        :returns: The geometry after deleting extra point'''
        raise NotImplementedError()
    
    @staticmethod
    def order_geometry_collection(geometry : aspose.gis.geometries.IGeometry) -> aspose.gis.geometries.IGeometry:
        '''Order geometry collection by type to four collection (point, line, polygon and other type)
        
        :param geometry: Geometry collection for order
        :returns: The collection contains four collections (point, line, polygon and other type)'''
        raise NotImplementedError()
    
    @staticmethod
    def extract_geometry_collection(layer : aspose.gis.VectorLayer) -> aspose.gis.geometries.IGeometry:
        '''Extract geometry collection from layer
        
        :param layer: Input layer
        :returns: The collection contains all geometries of input layer'''
        raise NotImplementedError()
    
    @staticmethod
    def make_voronoi_graph(sites : Iterable[aspose.gis.geometries.IPoint]) -> List[aspose.gis.geometries.LineString]:
        raise NotImplementedError()
    

class LineGeneratorOptions:
    '''Options from produce lines on surface or area.'''
    
    def clone(self) -> aspose.gis.geotools.LineGeneratorOptions:
        '''Clone object to one another.
        
        :returns: Clone object to one another :py:class:`aspose.gis.geotools.LineGeneratorOptions`.'''
        raise NotImplementedError()
    
    @property
    def count(self) -> int:
        '''Number of lines to create.'''
        raise NotImplementedError()
    
    @count.setter
    def count(self, value : int) -> None:
        '''Number of lines to create.'''
        raise NotImplementedError()
    
    @property
    def seed(self) -> int:
        '''A number used to calculate the seed value for a sequence of pseudo-random numbers.'''
        raise NotImplementedError()
    
    @seed.setter
    def seed(self, value : int) -> None:
        '''A number used to calculate the seed value for a sequence of pseudo-random numbers.'''
        raise NotImplementedError()
    
    @property
    def place(self) -> aspose.gis.geotools.GeneratorPlaces:
        '''Placing mode in generated cells.'''
        raise NotImplementedError()
    
    @place.setter
    def place(self, value : aspose.gis.geotools.GeneratorPlaces) -> None:
        '''Placing mode in generated cells.'''
        raise NotImplementedError()
    

class NearPointsCleanerOptions:
    '''Options for deleting points that are too close to each other.'''
    
    def clone(self) -> aspose.gis.geotools.NearPointsCleanerOptions:
        '''Create copy of object.
        
        :returns: The options clone.'''
        raise NotImplementedError()
    
    @property
    def distance(self) -> float:
        '''Parameter for check is point near to another point. Default value is 0.'''
        raise NotImplementedError()
    
    @distance.setter
    def distance(self, value : float) -> None:
        '''Parameter for check is point near to another point. Default value is 0.'''
        raise NotImplementedError()
    

class PointGeneratorOptions:
    '''Options from produce points on surface or area.'''
    
    def clone(self) -> aspose.gis.geotools.PointGeneratorOptions:
        '''Clone object to one another.
        
        :returns: Clone object to one another :py:class:`aspose.gis.geotools.PointGeneratorOptions`.'''
        raise NotImplementedError()
    
    @property
    def count(self) -> int:
        '''Number of points to create.'''
        raise NotImplementedError()
    
    @count.setter
    def count(self, value : int) -> None:
        '''Number of points to create.'''
        raise NotImplementedError()
    
    @property
    def seed(self) -> int:
        '''A number used to calculate the seed value for a sequence of pseudo-random numbers.'''
        raise NotImplementedError()
    
    @seed.setter
    def seed(self, value : int) -> None:
        '''A number used to calculate the seed value for a sequence of pseudo-random numbers.'''
        raise NotImplementedError()
    
    @property
    def place(self) -> aspose.gis.geotools.GeneratorPlaces:
        '''Placing mode in generated cells.'''
        raise NotImplementedError()
    
    @place.setter
    def place(self, value : aspose.gis.geotools.GeneratorPlaces) -> None:
        '''Placing mode in generated cells.'''
        raise NotImplementedError()
    

class PolygonGeneratorOptions:
    '''Options from produce lines on surface or area.'''
    
    def clone(self) -> aspose.gis.geotools.PolygonGeneratorOptions:
        '''Clone object to one another.
        
        :returns: Clone object to one another :py:class:`aspose.gis.geotools.PolygonGeneratorOptions`.'''
        raise NotImplementedError()
    
    @property
    def count(self) -> int:
        '''Number of polygons to create.'''
        raise NotImplementedError()
    
    @count.setter
    def count(self, value : int) -> None:
        '''Number of polygons to create.'''
        raise NotImplementedError()
    
    @property
    def minimum_polygon_points(self) -> int:
        '''The minimum length of the generated polygon.'''
        raise NotImplementedError()
    
    @minimum_polygon_points.setter
    def minimum_polygon_points(self, value : int) -> None:
        '''The minimum length of the generated polygon.'''
        raise NotImplementedError()
    
    @property
    def maximum_polygon_points(self) -> int:
        '''The maximum length of the generated polygon.'''
        raise NotImplementedError()
    
    @maximum_polygon_points.setter
    def maximum_polygon_points(self, value : int) -> None:
        '''The maximum length of the generated polygon.'''
        raise NotImplementedError()
    
    @property
    def seed(self) -> int:
        '''A number used to calculate the seed value for a sequence of pseudo-random numbers.'''
        raise NotImplementedError()
    
    @seed.setter
    def seed(self, value : int) -> None:
        '''A number used to calculate the seed value for a sequence of pseudo-random numbers.'''
        raise NotImplementedError()
    
    @property
    def place(self) -> aspose.gis.geotools.GeneratorPlaces:
        '''Placing mode in generated cells.'''
        raise NotImplementedError()
    
    @place.setter
    def place(self, value : aspose.gis.geotools.GeneratorPlaces) -> None:
        '''Placing mode in generated cells.'''
        raise NotImplementedError()
    

class SimplifySegmentsOptions:
    '''Options for :py:func:`aspose.gis.geotools.GeometryOperations.simplify_segments`.'''
    
    def clone(self) -> aspose.gis.geotools.SimplifySegmentsOptions:
        '''Create copy of object.
        
        :returns: The options clone.'''
        raise NotImplementedError()
    
    @property
    def distance(self) -> float:
        '''Parameter for check is point near to line segment. Default value is 0.'''
        raise NotImplementedError()
    
    @distance.setter
    def distance(self, value : float) -> None:
        '''Parameter for check is point near to line segment. Default value is 0.'''
        raise NotImplementedError()
    

class StarGeneratorOptions:
    '''Generator-specific options for :py:func:`aspose.gis.geotools.GeoGenerator.produce_polygons`.'''
    
    def clone(self) -> aspose.gis.geotools.StarGeneratorOptions:
        '''Clone object to one another.
        
        :returns: Clone object to one another :py:class:`aspose.gis.geotools.PolygonGeneratorOptions`.'''
        raise NotImplementedError()
    
    @property
    def count(self) -> int:
        '''Number of polygons to create.'''
        raise NotImplementedError()
    
    @count.setter
    def count(self, value : int) -> None:
        '''Number of polygons to create.'''
        raise NotImplementedError()
    
    @property
    def minimum_star_vertex(self) -> int:
        '''The minimum outside vertex of the generated side.'''
        raise NotImplementedError()
    
    @minimum_star_vertex.setter
    def minimum_star_vertex(self, value : int) -> None:
        '''The minimum outside vertex of the generated side.'''
        raise NotImplementedError()
    
    @property
    def maximum_star_vertex(self) -> int:
        '''The maximum outside vertex of the generated side.'''
        raise NotImplementedError()
    
    @maximum_star_vertex.setter
    def maximum_star_vertex(self, value : int) -> None:
        '''The maximum outside vertex of the generated side.'''
        raise NotImplementedError()
    
    @property
    def seed(self) -> int:
        '''A number used to calculate the seed value for a sequence of pseudo-random numbers.'''
        raise NotImplementedError()
    
    @seed.setter
    def seed(self, value : int) -> None:
        '''A number used to calculate the seed value for a sequence of pseudo-random numbers.'''
        raise NotImplementedError()
    
    @property
    def place(self) -> aspose.gis.geotools.GeneratorPlaces:
        '''Placing mode in generated cells.'''
        raise NotImplementedError()
    
    @place.setter
    def place(self, value : aspose.gis.geotools.GeneratorPlaces) -> None:
        '''Placing mode in generated cells.'''
        raise NotImplementedError()
    

class GeneratorPlaces:
    '''Describes the object places using by the :py:class:`aspose.gis.geotools.GeoGenerator`.'''
    
    RANDOM : GeneratorPlaces
    '''Places by random.'''
    REGULAR : GeneratorPlaces
    '''Places in centers'''

