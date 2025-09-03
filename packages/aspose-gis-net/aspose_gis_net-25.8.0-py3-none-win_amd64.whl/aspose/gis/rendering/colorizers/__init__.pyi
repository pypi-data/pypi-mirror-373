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

class BandColor:
    '''Associates band values and a color component for specified band index.
    There are band values between min and max will be interpolated linearly.'''
    
    @property
    def band_index(self) -> int:
        '''Specifies the index of the band. Numbering starts from 0.'''
        raise NotImplementedError()
    
    @band_index.setter
    def band_index(self, value : int) -> None:
        '''Specifies the index of the band. Numbering starts from 0.'''
        raise NotImplementedError()
    
    @property
    def min(self) -> float:
        '''Specifies the min value.'''
        raise NotImplementedError()
    
    @min.setter
    def min(self, value : float) -> None:
        '''Specifies the min value.'''
        raise NotImplementedError()
    
    @property
    def max(self) -> float:
        '''Specifies the max value.'''
        raise NotImplementedError()
    
    @max.setter
    def max(self, value : float) -> None:
        '''Specifies the max value.'''
        raise NotImplementedError()
    

class MultiBandColor(RasterColorizer):
    '''Multiband colorizer specifies red, green and blue components for a raster.'''
    
    null : aspose.gis.rendering.colorizers.NullColorizer
    '''The :py:class:`aspose.gis.rendering.colorizers.NullColorizer` draws nothing and effectively skips the rendering of cells it is applied to.'''
    @property
    def alpha_band(self) -> aspose.gis.rendering.colorizers.BandColor:
        '''Specifies the alpha component for our raster.'''
        raise NotImplementedError()
    
    @alpha_band.setter
    def alpha_band(self, value : aspose.gis.rendering.colorizers.BandColor) -> None:
        '''Specifies the alpha component for our raster.'''
        raise NotImplementedError()
    
    @property
    def red_band(self) -> aspose.gis.rendering.colorizers.BandColor:
        '''Specifies the red component for our raster.'''
        raise NotImplementedError()
    
    @red_band.setter
    def red_band(self, value : aspose.gis.rendering.colorizers.BandColor) -> None:
        '''Specifies the red component for our raster.'''
        raise NotImplementedError()
    
    @property
    def green_band(self) -> aspose.gis.rendering.colorizers.BandColor:
        '''Specifies the green component for our raster.'''
        raise NotImplementedError()
    
    @green_band.setter
    def green_band(self, value : aspose.gis.rendering.colorizers.BandColor) -> None:
        '''Specifies the green component for our raster.'''
        raise NotImplementedError()
    
    @property
    def blue_band(self) -> aspose.gis.rendering.colorizers.BandColor:
        '''Specifies the blue component for our raster.'''
        raise NotImplementedError()
    
    @blue_band.setter
    def blue_band(self, value : aspose.gis.rendering.colorizers.BandColor) -> None:
        '''Specifies the blue component for our raster.'''
        raise NotImplementedError()
    

class NullColorizer(RasterColorizer):
    '''The ``NullColorizer`` draws nothing and effectively skips rendering of a raster cell it is applied to.'''
    
    null : aspose.gis.rendering.colorizers.NullColorizer
    '''The :py:class:`aspose.gis.rendering.colorizers.NullColorizer` draws nothing and effectively skips the rendering of cells it is applied to.'''
    instance : aspose.gis.rendering.colorizers.NullColorizer
    '''Gets an instance of ``NullColorizer``.'''

class RasterColorizer:
    '''The abstract root class for the colorizer that render a raster.'''
    
    null : aspose.gis.rendering.colorizers.NullColorizer
    '''The :py:class:`aspose.gis.rendering.colorizers.NullColorizer` draws nothing and effectively skips the rendering of cells it is applied to.'''

class SingleBandColor(RasterColorizer):
    '''Single band colorizer specifies a gray component for a raster.'''
    
    null : aspose.gis.rendering.colorizers.NullColorizer
    '''The :py:class:`aspose.gis.rendering.colorizers.NullColorizer` draws nothing and effectively skips the rendering of cells it is applied to.'''
    @property
    def gray_band(self) -> aspose.gis.rendering.colorizers.BandColor:
        '''Specifies the gray component for our raster.'''
        raise NotImplementedError()
    
    @gray_band.setter
    def gray_band(self, value : aspose.gis.rendering.colorizers.BandColor) -> None:
        '''Specifies the gray component for our raster.'''
        raise NotImplementedError()
    

