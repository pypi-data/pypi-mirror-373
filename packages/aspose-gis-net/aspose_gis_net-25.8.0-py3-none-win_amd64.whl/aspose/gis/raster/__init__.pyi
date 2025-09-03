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

class IRasterBand:
    '''Contains metadata about a raster band.'''
    
    @property
    def data_type(self) -> aspose.gis.raster.BandTypes:
        '''Gets type of values stored in each cell.'''
        raise NotImplementedError()
    

class IRasterCellSize:
    '''Describes the size, scale and rotation of a raster cell on a map.'''
    
    @property
    def height(self) -> float:
        '''Gets the cell or pixel height, always positive.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the cell or pixel width, always positive.'''
        raise NotImplementedError()
    
    @property
    def scale_x(self) -> float:
        '''Gets x-component of the cell or pixel width (x-scale).'''
        raise NotImplementedError()
    
    @property
    def scale_y(self) -> float:
        '''Gets y-component of the cell or pixel height (y-scale), typically negative.'''
        raise NotImplementedError()
    
    @property
    def skew_x(self) -> float:
        '''Gets x-component of the cell or pixel height (x-skew).'''
        raise NotImplementedError()
    
    @property
    def skew_y(self) -> float:
        '''Gets y-component of the cell or pixel width (y-skew).'''
        raise NotImplementedError()
    

class IRasterValues:
    '''Provides access to the values of raster bands.'''
    
    def is_null(self, band_index : int) -> bool:
        '''Checks if the raster value is set in the specified band.
        
        :param band_index: The index of the band. Numbering starts from 0.
        :returns: Return \'false\' if not exist.'''
        raise NotImplementedError()
    
    def equals_no_data(self, band_index : int) -> bool:
        '''Checks if the value represents background or \'no data\' in the specified band.
        
        :param band_index: The index of the band. Numbering starts from 0.
        :returns: Return \'true\' if represents background or \'no data\'.'''
        raise NotImplementedError()
    
    def as_boolean(self, band_index : int) -> bool:
        '''Converts the specified band data to a  value.
        
        :param band_index: The index of the band. Numbering starts from 0.
        :returns: The converted value.'''
        raise NotImplementedError()
    
    def as_byte(self, band_index : int) -> int:
        '''Converts the specified band data to a  value.
        
        :param band_index: The index of the band. Numbering starts from 0.
        :returns: The converted value.'''
        raise NotImplementedError()
    
    def as_short(self, band_index : int) -> int:
        '''Converts the specified band data to a  value.
        
        :param band_index: The index of the band. Numbering starts from 0.
        :returns: The converted value.'''
        raise NotImplementedError()
    
    def as_integer(self, band_index : int) -> int:
        '''Converts the specified band data to a  value.
        
        :param band_index: The index of the band. Numbering starts from 0.
        :returns: The converted value.'''
        raise NotImplementedError()
    
    def as_long(self, band_index : int) -> int:
        '''Converts the specified band data to a  value.
        
        :param band_index: The index of the band. Numbering starts from 0.
        :returns: The converted value.'''
        raise NotImplementedError()
    
    def as_float(self, band_index : int) -> float:
        '''Converts the specified band data to a  value.
        
        :param band_index: The index of the band. Numbering starts from 0.
        :returns: The converted value.'''
        raise NotImplementedError()
    
    def as_double(self, band_index : int) -> float:
        '''Converts the specified band data to a  value.
        
        :param band_index: The index of the band. Numbering starts from 0.
        :returns: The converted value.'''
        raise NotImplementedError()
    
    def get_data_type(self, band_index : int) -> aspose.gis.raster.BandTypes:
        '''Gets type of values.
        
        :param band_index: The index of the band. Numbering starts from 0.
        :returns: The type of values.'''
        raise NotImplementedError()
    
    def __getitem__(self, key : int) -> float:
        '''Gets the band value as a  type.'''
        raise NotImplementedError()
    

class RasterBand(IRasterBand):
    '''Contains data about a raster Band.'''
    
    @property
    def data_type(self) -> aspose.gis.raster.BandTypes:
        '''Gets type of values stored in each cell.'''
        raise NotImplementedError()
    

class RasterCellSize(IRasterCellSize):
    '''Describes the size, scale and rotation of a raster cell on a map.'''
    
    @property
    def height(self) -> float:
        '''Compute the pixel height.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Compute the pixel width.'''
        raise NotImplementedError()
    
    @property
    def scale_x(self) -> float:
        '''Gets x-component of the pixel width (x-scale).'''
        raise NotImplementedError()
    
    @scale_x.setter
    def scale_x(self, value : float) -> None:
        '''Sets x-component of the pixel width (x-scale).'''
        raise NotImplementedError()
    
    @property
    def scale_y(self) -> float:
        '''Gets y-component of the pixel height (y-scale), typically negative.'''
        raise NotImplementedError()
    
    @scale_y.setter
    def scale_y(self, value : float) -> None:
        '''Sets y-component of the pixel height (y-scale), typically negative.'''
        raise NotImplementedError()
    
    @property
    def skew_x(self) -> float:
        '''Gets x-component of the pixel height (x-skew).'''
        raise NotImplementedError()
    
    @skew_x.setter
    def skew_x(self, value : float) -> None:
        '''Sets x-component of the pixel height (x-skew).'''
        raise NotImplementedError()
    
    @property
    def skew_y(self) -> float:
        '''Gets y-component of the pixel width (y-skew).'''
        raise NotImplementedError()
    
    @skew_y.setter
    def skew_y(self, value : float) -> None:
        '''Sets y-component of the pixel width (y-skew).'''
        raise NotImplementedError()
    

class RasterExpressionContext:
    '''This class describes the value context when it reads raster a band.'''
    
    def equals(self, other : aspose.gis.raster.RasterExpressionContext) -> bool:
        '''Indicates whether the current object is equal to another object of the same type.
        
        :param other: An object to compare with this object.
        :returns: true if the current object is equal to the ``other`` parameter; otherwise, false.'''
        raise NotImplementedError()
    
    @property
    def cell_x(self) -> int:
        '''Gets column value (x-coordinate). Numbering starts at 0.'''
        raise NotImplementedError()
    
    @property
    def cell_y(self) -> int:
        '''Gets row value (y-coordinate). Numbering starts at 0.'''
        raise NotImplementedError()
    

class RasterLayer:
    '''Represents a raster layer.'''
    
    @overload
    def crop(self, geometry : aspose.gis.geometries.IGeometry, masks : List[float]) -> aspose.gis.raster.RasterLayer:
        '''Crops the raster layer using a shape form (and band mask).
        
        :param geometry: Geometry represented the shape form.
        :param masks: Mask for crop layer
        :returns: The cropped raster layer. If no intersections found returns .'''
        raise NotImplementedError()
    
    @overload
    def crop(self, masks : List[float]) -> aspose.gis.raster.RasterLayer:
        '''Crops the raster layer using a band mask).
        
        :param masks: Mask for crop layer
        :returns: The cropped raster layer. If no intersections found returns .'''
        raise NotImplementedError()
    
    def get_band(self, index : int) -> aspose.gis.raster.IRasterBand:
        '''Gets a band by the specified index.
        
        :param index: Band numbers start at 0 and band is assumed to be 0 if not specified.
        :returns: Returns basic meta data about a raster band.'''
        raise NotImplementedError()
    
    def get_extent(self) -> aspose.gis.Extent:
        '''Calculates a spatial extent of this layer.
        
        :returns: A spatial extent of this layer.'''
        raise NotImplementedError()
    
    def get_spatial_point(self, cell_x : int, cell_y : int) -> aspose.gis.geometries.IPoint:
        '''Converts the specified column and row to the spatial coordinate.
        
        :param cell_x: The value for column (x-coordinate). Numbering starts at 0.
        :param cell_y: The value for row (y-coordinate). Numbering starts at 0.
        :returns: Returns the x-coordinate of upper left corner given a column and row.'''
        raise NotImplementedError()
    
    def get_statistics(self, band_index : int, exclude_nodata_value : bool) -> aspose.gis.raster.RasterStatistics:
        '''Calculate summary statistics consisting of count, sum, mean, min, max.
        
        :param band_index: The index of the band. Numbering starts from 0.
        :param exclude_nodata_value: Allows to exclude \'nodata\' values. If \'excludeNodataValue\' is set to false, then all pixels are considered.
        :returns: The summary statistics.'''
        raise NotImplementedError()
    
    def get_values_dump(self, rect : aspose.gis.raster.RasterRect) -> List[aspose.gis.raster.IRasterValues]:
        '''Reads the values in the specified block as a 1-dimension array.
        
        :param rect: Block of raster cells where dump is read.
        :returns: The dump of values.'''
        raise NotImplementedError()
    
    def get_values(self, cell_x : int, cell_y : int) -> aspose.gis.raster.IRasterValues:
        '''Reads the values in the specified cell.
        
        :param cell_x: The value for column (x-coordinate). Numbering starts at 0.
        :param cell_y: The value for row (y-coordinate). Numbering starts at 0.
        :returns: The raster values.'''
        raise NotImplementedError()
    
    def warp(self, options : aspose.gis.raster.WarpOptions) -> aspose.gis.raster.RasterLayer:
        '''Warps the raster layer to another.
        
        :param options: Options for the reprojection procedure.
        :returns: The warp raster layer.'''
        raise NotImplementedError()
    
    @property
    def band_count(self) -> int:
        '''Gets the number of bands in the raster layer.'''
        raise NotImplementedError()
    
    @property
    def no_data_values(self) -> aspose.gis.raster.IRasterValues:
        '''Gets the values that represents background or \'no data\' of the raster.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> int:
        '''Gets the width of the raster in pixels. Also it is known as columns count.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        '''Gets the height of the raster in pixels. Also it is known as rows count.'''
        raise NotImplementedError()
    
    @property
    def upper_left_x(self) -> float:
        '''Gets x-coordinate of the raster upper left corner.'''
        raise NotImplementedError()
    
    @property
    def upper_left_y(self) -> float:
        '''Gets y-coordinate of the raster upper left corner.'''
        raise NotImplementedError()
    
    @property
    def cell_size(self) -> aspose.gis.raster.IRasterCellSize:
        '''Gets cell or pixel size of the raster.'''
        raise NotImplementedError()
    
    @property
    def spatial_reference_system(self) -> aspose.gis.spatialreferencing.SpatialReferenceSystem:
        '''Gets a spatial reference system of raster.
        Can be  if it is unknown.'''
        raise NotImplementedError()
    
    @property
    def driver(self) -> aspose.gis.Driver:
        '''Gets the :py:attr:`aspose.gis.raster.RasterLayer.driver` that instantiated this layer.'''
        raise NotImplementedError()
    
    @property
    def bounds(self) -> aspose.gis.raster.RasterRect:
        '''Gets the raster bounds.'''
        raise NotImplementedError()
    

class RasterRect:
    '''Block of raster cells.'''
    
    @property
    def x(self) -> int:
        '''Gets start column (x-coordinate).'''
        raise NotImplementedError()
    
    @property
    def y(self) -> int:
        '''Gets start row (y-coordinate).'''
        raise NotImplementedError()
    
    @property
    def width(self) -> int:
        '''Gets width (columns count).'''
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        '''Gets height (row count).'''
        raise NotImplementedError()
    

class RasterStatistics:
    '''The statistics for any raster layer.'''
    
    @property
    def min(self) -> Optional[float]:
        '''Minimum value of counted cells or pixel values.'''
        raise NotImplementedError()
    
    @property
    def max(self) -> Optional[float]:
        '''Maximum value of counted cells or pixel values.'''
        raise NotImplementedError()
    
    @property
    def mean(self) -> Optional[float]:
        '''Arithmetic mean of all counted cells or pixel values.'''
        raise NotImplementedError()
    
    @property
    def sum(self) -> Optional[float]:
        '''Sum of all counted cells or pixel values.'''
        raise NotImplementedError()
    
    @property
    def count(self) -> Optional[float]:
        '''Number of cells or pixels counted for the summary statistics.'''
        raise NotImplementedError()
    

class WarpOptions:
    '''Options for raster warping.'''
    
    @property
    def width(self) -> int:
        '''Specifies output raster width in pixels and columns.
        If the value is set to 0, the width is automatically computed. The default value is "0".'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : int) -> None:
        '''Specifies output raster width in pixels and columns.
        If the value is set to 0, the width is automatically computed. The default value is "0".'''
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        '''Specifies output raster height in pixels and columns.
        If the value is set to 0, the height is automatically computed. The default value is "0".'''
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : int) -> None:
        '''Specifies output raster height in pixels and columns.
        If the value is set to 0, the height is automatically computed. The default value is "0".'''
        raise NotImplementedError()
    
    @property
    def cell_width(self) -> float:
        '''Specifies a new width of the raster cell (in target georeferenced units).
        If the value is set to 0, the :py:attr:`aspose.gis.raster.WarpOptions.cell_width` is automatically computed. The default value is "0".'''
        raise NotImplementedError()
    
    @cell_width.setter
    def cell_width(self, value : float) -> None:
        '''Specifies a new width of the raster cell (in target georeferenced units).
        If the value is set to 0, the :py:attr:`aspose.gis.raster.WarpOptions.cell_width` is automatically computed. The default value is "0".'''
        raise NotImplementedError()
    
    @property
    def cell_height(self) -> float:
        '''Specifies a new height of the raster cell (in target georeferenced units).
        If the value is set to 0, the :py:attr:`aspose.gis.raster.WarpOptions.cell_height` is automatically computed. The default value is "0".'''
        raise NotImplementedError()
    
    @cell_height.setter
    def cell_height(self, value : float) -> None:
        '''Specifies a new height of the raster cell (in target georeferenced units).
        If the value is set to 0, the :py:attr:`aspose.gis.raster.WarpOptions.cell_height` is automatically computed. The default value is "0".'''
        raise NotImplementedError()
    
    @property
    def target_extent(self) -> aspose.gis.Extent:
        '''Specifies bounds of raster layer to warp.
        If set to , extent is calculated during warping to include all cells from raster.'''
        raise NotImplementedError()
    
    @target_extent.setter
    def target_extent(self, value : aspose.gis.Extent) -> None:
        '''Specifies bounds of raster layer to warp.
        If set to , extent is calculated during warping to include all cells from raster.'''
        raise NotImplementedError()
    
    @property
    def target_spatial_reference_system(self) -> aspose.gis.spatialreferencing.SpatialReferenceSystem:
        '''Specifies target spatial reference.
        If set to , default or source spatial reference is used.'''
        raise NotImplementedError()
    
    @target_spatial_reference_system.setter
    def target_spatial_reference_system(self, value : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> None:
        '''Specifies target spatial reference.
        If set to , default or source spatial reference is used.'''
        raise NotImplementedError()
    
    @property
    def default_spatial_reference_system(self) -> aspose.gis.spatialreferencing.SpatialReferenceSystem:
        '''Specifies a value for a source spatial reference if that is missing.'''
        raise NotImplementedError()
    
    @default_spatial_reference_system.setter
    def default_spatial_reference_system(self, value : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> None:
        '''Specifies a value for a source spatial reference if that is missing.'''
        raise NotImplementedError()
    

class BandTypes:
    '''The types of a raster band.'''
    
    RAW_BITS : BandTypes
    '''Unknown band type. See :py:func:`aspose.gis.raster.IRasterValues.AsRawBits` for values.'''
    BIT : BandTypes
    '''1-bit. It known as :py:class:`bool`.'''
    S_BYTE : BandTypes
    '''8-bit signed integer. It known as :py:class:`int`.'''
    BYTE : BandTypes
    '''8-bit unsigned integer. It known as :py:class:`int`.'''
    SHORT : BandTypes
    '''16-bit signed integer. It known as :py:class:`int`.'''
    U_SHORT : BandTypes
    '''16-bit unsigned integer. It known as :py:class:`int`.'''
    INTEGER : BandTypes
    '''32-bit integer. It known as :py:class:`int`.'''
    U_INTEGER : BandTypes
    '''32-bit unsigned integer. It known as :py:class:`int`.'''
    LONG : BandTypes
    '''64-bit integer. It known as :py:class:`int`.'''
    U_LONG : BandTypes
    '''64-bit unsigned integer. It known as :py:class:`int`.'''
    FLOAT : BandTypes
    '''64-bit float. float. It known as :py:class:`float`.'''
    DOUBLE : BandTypes
    '''64-bit float. It known as :py:class:`float`.'''

