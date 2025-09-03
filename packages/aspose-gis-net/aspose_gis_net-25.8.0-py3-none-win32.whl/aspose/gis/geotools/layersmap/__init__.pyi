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

class LayersMapBuilder:
    '''Contains a method for creating maps and all the functions it depends on.'''
    

class MapLayerOptions:
    '''Vector Layer Options for creating maps using :py:class:`aspose.gis.geotools.layersmap.LayersMapBuilder`'''
    
    @property
    def layer(self) -> aspose.gis.VectorLayer:
        '''Vector layer.'''
        raise NotImplementedError()
    
    @layer.setter
    def layer(self, value : aspose.gis.VectorLayer) -> None:
        '''Vector layer.'''
        raise NotImplementedError()
    
    @property
    def symbolyzer(self) -> aspose.gis.rendering.symbolizers.VectorSymbolizer:
        '''Vector symbolyzer.'''
        raise NotImplementedError()
    
    @symbolyzer.setter
    def symbolyzer(self, value : aspose.gis.rendering.symbolizers.VectorSymbolizer) -> None:
        '''Vector symbolyzer.'''
        raise NotImplementedError()
    
    @property
    def labeling(self) -> aspose.gis.rendering.labelings.Labeling:
        '''Labeling of the features. Defaults to null.'''
        raise NotImplementedError()
    
    @labeling.setter
    def labeling(self, value : aspose.gis.rendering.labelings.Labeling) -> None:
        '''Labeling of the features. Defaults to null.'''
        raise NotImplementedError()
    
    @property
    def layer_spatial_ref_sys(self) -> aspose.gis.spatialreferencing.SpatialReferenceSystem:
        '''Specifies a value for a layer spatial reference.'''
        raise NotImplementedError()
    
    @layer_spatial_ref_sys.setter
    def layer_spatial_ref_sys(self, value : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> None:
        '''Specifies a value for a layer spatial reference.'''
        raise NotImplementedError()
    

class MapOptions:
    '''Map Options for creating maps using :py:class:`aspose.gis.geotools.layersmap.LayersMapBuilder`'''
    
    @property
    def layers(self) -> List[aspose.gis.geotools.layersmap.MapLayerOptions]:
        '''A collection of options for vector layers to represent by Aspose.Gis.GeoTools.LayersMap.MapLayerOptions.'''
        raise NotImplementedError()
    
    @layers.setter
    def layers(self, value : List[aspose.gis.geotools.layersmap.MapLayerOptions]) -> None:
        '''A collection of options for vector layers to represent by Aspose.Gis.GeoTools.LayersMap.MapLayerOptions.'''
        raise NotImplementedError()
    
    @property
    def rasters(self) -> List[aspose.gis.geotools.layersmap.MapRasterOptions]:
        '''A collection of options for rasters layers to represent by Aspose.Gis.GeoTools.LayersMap.MapRasterOptions.'''
        raise NotImplementedError()
    
    @rasters.setter
    def rasters(self, value : List[aspose.gis.geotools.layersmap.MapRasterOptions]) -> None:
        '''A collection of options for rasters layers to represent by Aspose.Gis.GeoTools.LayersMap.MapRasterOptions.'''
        raise NotImplementedError()
    
    @property
    def tiles(self) -> aspose.gis.geotools.layersmap.MapTilesOptions:
        '''Tiles options.'''
        raise NotImplementedError()
    
    @tiles.setter
    def tiles(self, value : aspose.gis.geotools.layersmap.MapTilesOptions) -> None:
        '''Tiles options.'''
        raise NotImplementedError()
    
    @property
    def size_mode(self) -> aspose.gis.geotools.layersmap.MapSizeModes:
        '''Size Mode. Defaults to :py:attr:`aspose.gis.geotools.layersmap.MapSizeModes.AUTO`'''
        raise NotImplementedError()
    
    @size_mode.setter
    def size_mode(self, value : aspose.gis.geotools.layersmap.MapSizeModes) -> None:
        '''Size Mode. Defaults to :py:attr:`aspose.gis.geotools.layersmap.MapSizeModes.AUTO`'''
        raise NotImplementedError()
    
    @property
    def width(self) -> int:
        '''Visual width of the map. Defaults to 400. Used when :py:attr:`aspose.gis.geotools.layersmap.MapSizeModes.CUSTOM`.'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : int) -> None:
        '''Visual width of the map. Defaults to 400. Used when :py:attr:`aspose.gis.geotools.layersmap.MapSizeModes.CUSTOM`.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        '''Visual height of the map. Defaults to 400. Used when :py:attr:`aspose.gis.geotools.layersmap.MapSizeModes.CUSTOM`.'''
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : int) -> None:
        '''Visual height of the map. Defaults to 400. Used when :py:attr:`aspose.gis.geotools.layersmap.MapSizeModes.CUSTOM`.'''
        raise NotImplementedError()
    
    @property
    def background_color(self) -> aspose.pydrawing.Color:
        '''Background color of the map. Defaults to System.Drawing.Color.Transparent.'''
        raise NotImplementedError()
    
    @background_color.setter
    def background_color(self, value : aspose.pydrawing.Color) -> None:
        '''Background color of the map. Defaults to System.Drawing.Color.Transparent.'''
        raise NotImplementedError()
    
    @property
    def renderer(self) -> aspose.gis.rendering.Renderer:
        '''Renderer to use. Defaults to Aspose.Gis.Rendering.Renders.Jpeg.'''
        raise NotImplementedError()
    
    @renderer.setter
    def renderer(self, value : aspose.gis.rendering.Renderer) -> None:
        '''Renderer to use. Defaults to Aspose.Gis.Rendering.Renders.Jpeg.'''
        raise NotImplementedError()
    
    @property
    def spatial_reference(self) -> aspose.gis.spatialreferencing.SpatialReferenceSystem:
        '''Spatial Reference. Defaults to Aspose.Gis.SpatialReferencing.SpatialReferenceSystem.WebMercator.'''
        raise NotImplementedError()
    
    @spatial_reference.setter
    def spatial_reference(self, value : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> None:
        '''Spatial Reference. Defaults to Aspose.Gis.SpatialReferencing.SpatialReferenceSystem.WebMercator.'''
        raise NotImplementedError()
    

class MapRasterOptions:
    '''Raster layer options for creating maps using :py:class:`aspose.gis.geotools.layersmap.LayersMapBuilder`'''
    
    @property
    def raster(self) -> aspose.gis.raster.RasterLayer:
        '''Raster layer.'''
        raise NotImplementedError()
    
    @raster.setter
    def raster(self, value : aspose.gis.raster.RasterLayer) -> None:
        '''Raster layer.'''
        raise NotImplementedError()
    
    @property
    def pixel_per_row(self) -> int:
        '''Height of the raster in pixels.'''
        raise NotImplementedError()
    
    @pixel_per_row.setter
    def pixel_per_row(self, value : int) -> None:
        '''Height of the raster in pixels.'''
        raise NotImplementedError()
    
    @property
    def pixel_per_column(self) -> int:
        '''Width of the raster in pixels.'''
        raise NotImplementedError()
    
    @pixel_per_column.setter
    def pixel_per_column(self, value : int) -> None:
        '''Width of the raster in pixels.'''
        raise NotImplementedError()
    
    @property
    def layer_spatial_ref_sys(self) -> aspose.gis.spatialreferencing.SpatialReferenceSystem:
        '''Specifies a value for a layer spatial reference.'''
        raise NotImplementedError()
    
    @layer_spatial_ref_sys.setter
    def layer_spatial_ref_sys(self, value : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> None:
        '''Specifies a value for a layer spatial reference.'''
        raise NotImplementedError()
    

class MapTilesOptions:
    '''Tiles options for creating maps using :py:class:`aspose.gis.geotools.layersmap.LayersMapBuilder`'''
    
    @property
    def url(self) -> str:
        '''Url or Path to a file.'''
        raise NotImplementedError()
    
    @url.setter
    def url(self, value : str) -> None:
        '''Url or Path to a file.'''
        raise NotImplementedError()
    
    @property
    def level(self) -> int:
        '''The zoom level for loading tiles. Defaults to 3.'''
        raise NotImplementedError()
    
    @level.setter
    def level(self, value : int) -> None:
        '''The zoom level for loading tiles. Defaults to 3.'''
        raise NotImplementedError()
    

class MapSizeModes:
    '''Map size modes for :py:class:`aspose.gis.geotools.layersmap.LayersMapBuilder`.'''
    
    NONE : MapSizeModes
    '''Unknown Size Mode.'''
    AUTO : MapSizeModes
    '''Auto map sizes.'''
    CUSTOM : MapSizeModes
    '''Use sizes from options :py:attr:`aspose.gis.geotools.layersmap.MapOptions.width` and :py:attr:`aspose.gis.geotools.layersmap.MapOptions.height`.'''

