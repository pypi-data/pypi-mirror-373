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

class FileGdbCoordinatePrecisionGrid:
    '''A coordinate precision grid inside a FileGDB layer.'''
    
    @staticmethod
    def create_from_rectangle(p1 : aspose.gis.geometries.IPoint, p2 : aspose.gis.geometries.IPoint) -> aspose.gis.formats.filegdb.FileGdbCoordinatePrecisionGrid:
        '''Creates new ``FileGdbCoordinatePrecisionGrid`` such that all values within a rectangle are representable.
        
        :param p1: One corner of the rectangle.
        :param p2: Opposite corner of the rectangle. Must have same dimensions as ``p1``.
        :returns: The ``FileGdbCoordinatePrecisionGrid`` such that all values within a rectangle are representable.
        Values outside of the rectangle are not representable, so all coordinates that will be written to FileGDB layer
        must be inside the rectangle.'''
        raise NotImplementedError()
    
    @property
    def x_origin(self) -> Optional[float]:
        '''Gets the origin of X coordinate. If set to  the default is used.'''
        raise NotImplementedError()
    
    @x_origin.setter
    def x_origin(self, value : Optional[float]) -> None:
        '''Sets the origin of X coordinate. If set to  the default is used.'''
        raise NotImplementedError()
    
    @property
    def y_origin(self) -> Optional[float]:
        '''Gets the origin of Y coordinate. If set to  the default is used.'''
        raise NotImplementedError()
    
    @y_origin.setter
    def y_origin(self, value : Optional[float]) -> None:
        '''Sets the origin of Y coordinate. If set to  the default is used.'''
        raise NotImplementedError()
    
    @property
    def z_origin(self) -> Optional[float]:
        '''Gets the origin of Z coordinate. If set to  the default is used.'''
        raise NotImplementedError()
    
    @z_origin.setter
    def z_origin(self, value : Optional[float]) -> None:
        '''Sets the origin of Z coordinate. If set to  the default is used.'''
        raise NotImplementedError()
    
    @property
    def m_origin(self) -> Optional[float]:
        '''Gets the origin of M coordinate. If set to  the default is used.'''
        raise NotImplementedError()
    
    @m_origin.setter
    def m_origin(self, value : Optional[float]) -> None:
        '''Sets the origin of M coordinate. If set to  the default is used.'''
        raise NotImplementedError()
    
    @property
    def xy_scale(self) -> Optional[float]:
        '''Gets the scale of X and Y coordinates. If set to  the default is used.'''
        raise NotImplementedError()
    
    @xy_scale.setter
    def xy_scale(self, value : Optional[float]) -> None:
        '''Sets the scale of X and Y coordinates. If set to  the default is used.'''
        raise NotImplementedError()
    
    @property
    def z_scale(self) -> Optional[float]:
        '''Gets the scale of Z coordinate. If set to  the default is used.'''
        raise NotImplementedError()
    
    @z_scale.setter
    def z_scale(self, value : Optional[float]) -> None:
        '''Sets the scale of Z coordinate. If set to  the default is used.'''
        raise NotImplementedError()
    
    @property
    def m_scale(self) -> Optional[float]:
        '''Gets the scale of M coordinate. If set to  the default is used.'''
        raise NotImplementedError()
    
    @m_scale.setter
    def m_scale(self, value : Optional[float]) -> None:
        '''Sets the scale of M coordinate. If set to  the default is used.'''
        raise NotImplementedError()
    

class FileGdbDriver(aspose.gis.FileDriver):
    '''A driver for the ESRI File Geodatabase format.'''
    
    @overload
    def open_layer(self, path : str, options : aspose.gis.formats.filegdb.FileGdbOptions) -> aspose.gis.VectorLayer:
        '''Opens a layer for reading.
        
        :param path: Path to the file.
        :param options: Driver-specific options.
        :returns: An instance of :py:class:`aspose.gis.VectorLayer`.'''
        raise NotImplementedError()
    
    @overload
    def open_layer(self, path : aspose.gis.AbstractPath, options : aspose.gis.DriverOptions) -> aspose.gis.VectorLayer:
        '''Opens a layer for reading.
        
        :param path: Path to the file.
        :param options: Driver-specific options.
        :returns: An instance of :py:class:`aspose.gis.VectorLayer`.'''
        raise NotImplementedError()
    
    @overload
    def open_layer(self, path : aspose.gis.AbstractPath, options : aspose.gis.formats.filegdb.FileGdbOptions) -> aspose.gis.VectorLayer:
        '''Opens a layer for reading.
        
        :param path: Path to the file.
        :param options: Driver-specific options.
        :returns: An instance of :py:class:`aspose.gis.VectorLayer`.'''
        raise NotImplementedError()
    
    @overload
    def open_layer(self, path : str) -> aspose.gis.VectorLayer:
        '''Opens the layer for reading.
        
        :param path: Path to the file.
        :returns: An instance of :py:class:`aspose.gis.VectorLayer`.'''
        raise NotImplementedError()
    
    @overload
    def open_layer(self, path : aspose.gis.AbstractPath) -> aspose.gis.VectorLayer:
        '''Opens the layer for reading.
        
        :param path: Path to the file.
        :returns: An instance of :py:class:`aspose.gis.VectorLayer`.'''
        raise NotImplementedError()
    
    @overload
    def open_layer(self, path : str, options : aspose.gis.DriverOptions) -> aspose.gis.VectorLayer:
        '''Opens the layer for reading.
        
        :param path: Path to the file.
        :param options: Driver-specific options.
        :returns: An instance of :py:class:`aspose.gis.VectorLayer`.'''
        raise NotImplementedError()
    
    @overload
    def create_layer(self, path : str, options : aspose.gis.formats.filegdb.FileGdbOptions) -> aspose.gis.VectorLayer:
        '''Creates a layer and opens it for adding new features.
        
        :param path: Path to the file.
        :param options: Driver-specific options.
        :returns: An instance of :py:class:`aspose.gis.VectorLayer`.'''
        raise NotImplementedError()
    
    @overload
    def create_layer(self, path : str, options : aspose.gis.formats.filegdb.FileGdbOptions, spatial_reference_system : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> aspose.gis.VectorLayer:
        '''Creates a layer and opens it for appending.
        
        :param path: Path to the file.
        :param options: Driver-specific options.
        :param spatial_reference_system: Spatial reference system.
        :returns: An instance of :py:class:`aspose.gis.VectorLayer`.'''
        raise NotImplementedError()
    
    @overload
    def create_layer(self, path : aspose.gis.AbstractPath, options : aspose.gis.DriverOptions, spatial_reference_system : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> aspose.gis.VectorLayer:
        '''Creates a layer and opens it for appending.
        
        :param path: Path to the file.
        :param options: Driver-specific options.
        :param spatial_reference_system: Spatial reference system.
        :returns: An instance of :py:class:`aspose.gis.VectorLayer`.'''
        raise NotImplementedError()
    
    @overload
    def create_layer(self, path : aspose.gis.AbstractPath, options : aspose.gis.formats.filegdb.FileGdbOptions, spatial_reference_system : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> aspose.gis.VectorLayer:
        '''Creates a layer and opens it for appending.
        
        :param path: Path to the file.
        :param options: Driver-specific options.
        :param spatial_reference_system: Spatial reference system.
        :returns: An instance of :py:class:`aspose.gis.VectorLayer`.'''
        raise NotImplementedError()
    
    @overload
    def create_layer(self, path : str) -> aspose.gis.VectorLayer:
        '''Creates the layer and opens it for appending.
        
        :param path: Path to the file.
        :returns: An instance of :py:class:`aspose.gis.VectorLayer`.'''
        raise NotImplementedError()
    
    @overload
    def create_layer(self, path : aspose.gis.AbstractPath) -> aspose.gis.VectorLayer:
        '''Creates the layer and opens it for appending.
        
        :param path: Path to the file.
        :returns: An instance of :py:class:`aspose.gis.VectorLayer`.'''
        raise NotImplementedError()
    
    @overload
    def create_layer(self, path : str, options : aspose.gis.DriverOptions) -> aspose.gis.VectorLayer:
        '''Creates the layer and opens it for appending.
        
        :param path: Path to the file.
        :param options: Driver-specific options.
        :returns: An instance of :py:class:`aspose.gis.VectorLayer`.'''
        raise NotImplementedError()
    
    @overload
    def create_layer(self, path : aspose.gis.AbstractPath, options : aspose.gis.DriverOptions) -> aspose.gis.VectorLayer:
        '''Creates the layer and opens it for appending.
        
        :param path: Path to the file.
        :param options: Driver-specific options.
        :returns: An instance of :py:class:`aspose.gis.VectorLayer`.'''
        raise NotImplementedError()
    
    @overload
    def create_layer(self, path : str, spatial_reference_system : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> aspose.gis.VectorLayer:
        '''Creates the layer and opens it for appending.
        
        :param path: Path to the file.
        :param spatial_reference_system: Spatial reference system.
        :returns: An instance of :py:class:`aspose.gis.VectorLayer`.'''
        raise NotImplementedError()
    
    @overload
    def create_layer(self, path : aspose.gis.AbstractPath, spatial_reference_system : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> aspose.gis.VectorLayer:
        '''Creates the layer and opens it for appending.
        
        :param path: Path to the file.
        :param spatial_reference_system: Spatial reference system.
        :returns: An instance of :py:class:`aspose.gis.VectorLayer`.'''
        raise NotImplementedError()
    
    @overload
    def create_layer(self, path : str, options : aspose.gis.DriverOptions, spatial_reference_system : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> aspose.gis.VectorLayer:
        '''Creates the layer and opens it for appending.
        
        :param path: Path to the file.
        :param options: Driver-specific options.
        :param spatial_reference_system: Spatial reference system.
        :returns: An instance of :py:class:`aspose.gis.VectorLayer`.'''
        raise NotImplementedError()
    
    @overload
    def edit_layer(self, path : aspose.gis.AbstractPath, options : aspose.gis.DriverOptions) -> aspose.gis.VectorLayer:
        '''Opens a layer for editing.
        
        :param path: Path to the file.
        :param options: Driver-specific options.
        :returns: An instance of :py:class:`aspose.gis.VectorLayer`.'''
        raise NotImplementedError()
    
    @overload
    def edit_layer(self, path : str, options : aspose.gis.DriverOptions) -> aspose.gis.VectorLayer:
        '''Opens a layer for editing.
        
        :param path: Path to the file.
        :param options: Driver-specific options.
        :returns: An instance of :py:class:`aspose.gis.VectorLayer`.'''
        raise NotImplementedError()
    
    @overload
    def open_dataset(self, path : str, options : aspose.gis.formats.filegdb.FileGdbOptions) -> aspose.gis.Dataset:
        '''Opens the dataset.
        
        :param path: Path to the dataset.
        :param options: Driver-specific options.
        :returns: An instance of :py:class:`aspose.gis.Dataset`.'''
        raise NotImplementedError()
    
    @overload
    def open_dataset(self, path : aspose.gis.AbstractPath, options : aspose.gis.DriverOptions) -> aspose.gis.Dataset:
        '''Opens the dataset.
        
        :param path: Path to the dataset.
        :param options: Driver-specific options.
        :returns: An instance of :py:class:`aspose.gis.Dataset`.'''
        raise NotImplementedError()
    
    @overload
    def open_dataset(self, path : aspose.gis.AbstractPath, options : aspose.gis.formats.filegdb.FileGdbOptions) -> aspose.gis.Dataset:
        '''Opens the dataset.
        
        :param path: Path to the dataset.
        :param options: Driver-specific options.
        :returns: An instance of :py:class:`aspose.gis.Dataset`.'''
        raise NotImplementedError()
    
    @overload
    def open_dataset(self, path : str) -> aspose.gis.Dataset:
        '''Opens the dataset.
        
        :param path: Path to the dataset.
        :returns: An instance of :py:class:`aspose.gis.Dataset`.'''
        raise NotImplementedError()
    
    @overload
    def open_dataset(self, path : aspose.gis.AbstractPath) -> aspose.gis.Dataset:
        '''Opens the dataset.
        
        :param path: Path to the dataset.
        :returns: An instance of :py:class:`aspose.gis.Dataset`.'''
        raise NotImplementedError()
    
    @overload
    def open_dataset(self, path : str, options : aspose.gis.DriverOptions) -> aspose.gis.Dataset:
        '''Opens the dataset.
        
        :param path: Path to the dataset.
        :param options: Driver-specific options.
        :returns: An instance of :py:class:`aspose.gis.Dataset`.'''
        raise NotImplementedError()
    
    @overload
    def create_dataset(self, path : str, options : aspose.gis.formats.filegdb.FileGdbOptions) -> aspose.gis.Dataset:
        '''Creates a dataset.
        
        :param path: Path to the dataset.
        :param options: Driver-specific options.
        :returns: An instance of :py:class:`aspose.gis.Dataset`.'''
        raise NotImplementedError()
    
    @overload
    def create_dataset(self, path : aspose.gis.AbstractPath, options : aspose.gis.DriverOptions) -> aspose.gis.Dataset:
        '''Creates a dataset.
        
        :param path: Path to the dataset.
        :param options: Driver-specific options.
        :returns: An instance of :py:class:`aspose.gis.Dataset`.'''
        raise NotImplementedError()
    
    @overload
    def create_dataset(self, path : aspose.gis.AbstractPath, options : aspose.gis.formats.filegdb.FileGdbOptions) -> aspose.gis.Dataset:
        '''Creates a dataset.
        
        :param path: Path to the dataset.
        :param options: Driver-specific options.
        :returns: An instance of :py:class:`aspose.gis.Dataset`.'''
        raise NotImplementedError()
    
    @overload
    def create_dataset(self, path : str) -> aspose.gis.Dataset:
        '''Creates a dataset.
        
        :param path: Path to the dataset.
        :returns: An instance of :py:class:`aspose.gis.Dataset`.'''
        raise NotImplementedError()
    
    @overload
    def create_dataset(self, path : aspose.gis.AbstractPath) -> aspose.gis.Dataset:
        '''Creates a dataset.
        
        :param path: Path to the dataset.
        :returns: An instance of :py:class:`aspose.gis.Dataset`.'''
        raise NotImplementedError()
    
    @overload
    def create_dataset(self, path : str, options : aspose.gis.DriverOptions) -> aspose.gis.Dataset:
        '''Creates a dataset.
        
        :param path: Path to the dataset.
        :param options: Driver-specific options.
        :returns: An instance of :py:class:`aspose.gis.Dataset`.'''
        raise NotImplementedError()
    
    def supports_spatial_reference_system(self, spatial_reference_system : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> bool:
        '''Determines, whether specified spatial reference system is supported by the driver.
        
        :param spatial_reference_system: Spatial reference system.
        :returns: Boolean value, indicating whether specified spatial reference system is supported by the driver.'''
        raise NotImplementedError()
    
    @property
    def can_create_layers(self) -> bool:
        '''Gets a value indicating whether this driver can create vector layers.'''
        raise NotImplementedError()
    
    @property
    def can_open_layers(self) -> bool:
        '''Gets a value indicating whether this driver can open vector layers.'''
        raise NotImplementedError()
    
    @property
    def can_open_datasets(self) -> bool:
        '''Gets a value indicating whether this driver can open datasets.'''
        raise NotImplementedError()
    
    @property
    def can_create_datasets(self) -> bool:
        '''Gets a value indicating whether this driver can create datasets.'''
        raise NotImplementedError()
    

class FileGdbOptions(aspose.gis.DriverOptions):
    '''Driver-specific options for FileGDB format.'''
    
    @property
    def validate_geometries_on_write(self) -> bool:
        '''Determines if geometries should be validated when they are added to the layer.
        If set to , :py:attr:`aspose.gis.geometries.Geometry.is_valid` is called for each
        geometry when it\'s added to the layer, and if validation fails (:py:attr:`aspose.gis.geometries.Geometry.is_valid` is ), :py:class:`aspose.gis.GisException` is thrown.'''
        raise NotImplementedError()
    
    @validate_geometries_on_write.setter
    def validate_geometries_on_write(self, value : bool) -> None:
        '''Determines if geometries should be validated when they are added to the layer.
        If set to , :py:attr:`aspose.gis.geometries.Geometry.is_valid` is called for each
        geometry when it\'s added to the layer, and if validation fails (:py:attr:`aspose.gis.geometries.Geometry.is_valid` is ), :py:class:`aspose.gis.GisException` is thrown.'''
        raise NotImplementedError()
    
    @property
    def write_polygons_as_lines(self) -> bool:
        '''Determines if transformation of polygon or multipolygon to linestring is allowed. Defaults to .'''
        raise NotImplementedError()
    
    @write_polygons_as_lines.setter
    def write_polygons_as_lines(self, value : bool) -> None:
        '''Determines if transformation of polygon or multipolygon to linestring is allowed. Defaults to .'''
        raise NotImplementedError()
    
    @property
    def create_midpoints(self) -> bool:
        '''Determines if add a new point in the middle to each segment of geometry. Defaults to .'''
        raise NotImplementedError()
    
    @create_midpoints.setter
    def create_midpoints(self, value : bool) -> None:
        '''Determines if add a new point in the middle to each segment of geometry. Defaults to .'''
        raise NotImplementedError()
    
    @property
    def close_linear_ring(self) -> bool:
        '''Determines if close a unclosed :py:attr:`aspose.gis.geometries.GeometryType.LINEAR_RING` in each geometry. Defaults to .'''
        raise NotImplementedError()
    
    @close_linear_ring.setter
    def close_linear_ring(self, value : bool) -> None:
        '''Determines if close a unclosed :py:attr:`aspose.gis.geometries.GeometryType.LINEAR_RING` in each geometry. Defaults to .'''
        raise NotImplementedError()
    
    @property
    def delete_near_points(self) -> bool:
        '''Determines if delete near points in each geometry. Defaults to .'''
        raise NotImplementedError()
    
    @delete_near_points.setter
    def delete_near_points(self, value : bool) -> None:
        '''Determines if delete near points in each geometry. Defaults to .'''
        raise NotImplementedError()
    
    @property
    def delete_near_points_distance(self) -> float:
        '''Determines distance for :py:attr:`aspose.gis.DriverOptions.delete_near_points`. Defaults to .'''
        raise NotImplementedError()
    
    @delete_near_points_distance.setter
    def delete_near_points_distance(self, value : float) -> None:
        '''Determines distance for :py:attr:`aspose.gis.DriverOptions.delete_near_points`. Defaults to .'''
        raise NotImplementedError()
    
    @property
    def simplify_segments(self) -> bool:
        '''Determines if delete points lying on the same segment in each geometry. Defaults to .'''
        raise NotImplementedError()
    
    @simplify_segments.setter
    def simplify_segments(self, value : bool) -> None:
        '''Determines if delete points lying on the same segment in each geometry. Defaults to .'''
        raise NotImplementedError()
    
    @property
    def simplify_segments_distance(self) -> float:
        '''Determines distance for :py:attr:`aspose.gis.DriverOptions.simplify_segments`. Defaults to .'''
        raise NotImplementedError()
    
    @simplify_segments_distance.setter
    def simplify_segments_distance(self, value : float) -> None:
        '''Determines distance for :py:attr:`aspose.gis.DriverOptions.simplify_segments`. Defaults to .'''
        raise NotImplementedError()
    
    @property
    def xy_precision_model(self) -> aspose.gis.PrecisionModel:
        '''A :py:class:`aspose.gis.PrecisionModel` that will be applied to X and Y coordinates
        when geometries are added to the :py:class:`aspose.gis.VectorLayer` or when they are read from the :py:class:`aspose.gis.VectorLayer`.
        The default value is :py:attr:`aspose.gis.PrecisionModel.exact`.'''
        raise NotImplementedError()
    
    @xy_precision_model.setter
    def xy_precision_model(self, value : aspose.gis.PrecisionModel) -> None:
        '''A :py:class:`aspose.gis.PrecisionModel` that will be applied to X and Y coordinates
        when geometries are added to the :py:class:`aspose.gis.VectorLayer` or when they are read from the :py:class:`aspose.gis.VectorLayer`.
        The default value is :py:attr:`aspose.gis.PrecisionModel.exact`.'''
        raise NotImplementedError()
    
    @property
    def z_precision_model(self) -> aspose.gis.PrecisionModel:
        '''A :py:class:`aspose.gis.PrecisionModel` that will be applied to Z coordinate
        when geometries are added to the :py:class:`aspose.gis.VectorLayer` or when they are read from the :py:class:`aspose.gis.VectorLayer`.
        The default value is :py:attr:`aspose.gis.PrecisionModel.exact`.'''
        raise NotImplementedError()
    
    @z_precision_model.setter
    def z_precision_model(self, value : aspose.gis.PrecisionModel) -> None:
        '''A :py:class:`aspose.gis.PrecisionModel` that will be applied to Z coordinate
        when geometries are added to the :py:class:`aspose.gis.VectorLayer` or when they are read from the :py:class:`aspose.gis.VectorLayer`.
        The default value is :py:attr:`aspose.gis.PrecisionModel.exact`.'''
        raise NotImplementedError()
    
    @property
    def m_precision_model(self) -> aspose.gis.PrecisionModel:
        '''A :py:class:`aspose.gis.PrecisionModel` that will be applied to M coordinate
        when geometries are added to the :py:class:`aspose.gis.VectorLayer` or when they are read from the :py:class:`aspose.gis.VectorLayer`.
        The default value is :py:attr:`aspose.gis.PrecisionModel.exact`.'''
        raise NotImplementedError()
    
    @m_precision_model.setter
    def m_precision_model(self, value : aspose.gis.PrecisionModel) -> None:
        '''A :py:class:`aspose.gis.PrecisionModel` that will be applied to M coordinate
        when geometries are added to the :py:class:`aspose.gis.VectorLayer` or when they are read from the :py:class:`aspose.gis.VectorLayer`.
        The default value is :py:attr:`aspose.gis.PrecisionModel.exact`.'''
        raise NotImplementedError()
    
    @property
    def linearization_tolerance(self) -> float:
        '''A tolerance to use to linearize curve geometries.'''
        raise NotImplementedError()
    
    @linearization_tolerance.setter
    def linearization_tolerance(self, value : float) -> None:
        '''A tolerance to use to linearize curve geometries.'''
        raise NotImplementedError()
    
    @property
    def object_id_field_name(self) -> str:
        '''Name of the object ID field.'''
        raise NotImplementedError()
    
    @object_id_field_name.setter
    def object_id_field_name(self, value : str) -> None:
        '''Name of the object ID field.'''
        raise NotImplementedError()
    
    @property
    def geometry_field_name(self) -> str:
        '''Name of the geometry field.'''
        raise NotImplementedError()
    
    @geometry_field_name.setter
    def geometry_field_name(self, value : str) -> None:
        '''Name of the geometry field.'''
        raise NotImplementedError()
    
    @property
    def expected_geometry_type(self) -> Optional[aspose.gis.geometries.GeometryType]:
        '''Expected geometry type for layer. If this option is set then we allow adding only geometries with this type'''
        raise NotImplementedError()
    
    @expected_geometry_type.setter
    def expected_geometry_type(self, value : Optional[aspose.gis.geometries.GeometryType]) -> None:
        '''Expected geometry type for layer. If this option is set then we allow adding only geometries with this type'''
        raise NotImplementedError()
    
    @property
    def has_z(self) -> bool:
        '''Can geometries of layer have \'z\' coordinate. By defualt is true'''
        raise NotImplementedError()
    
    @has_z.setter
    def has_z(self, value : bool) -> None:
        '''Can geometries of layer have \'z\' coordinate. By defualt is true'''
        raise NotImplementedError()
    
    @property
    def has_m(self) -> bool:
        '''Can geometries of layer have \'m\' coordinate. By defualt is true'''
        raise NotImplementedError()
    
    @has_m.setter
    def has_m(self, value : bool) -> None:
        '''Can geometries of layer have \'m\' coordinate. By defualt is true'''
        raise NotImplementedError()
    
    @property
    def xy_tolerance(self) -> Optional[float]:
        '''X and Y snapping tolerance.'''
        raise NotImplementedError()
    
    @xy_tolerance.setter
    def xy_tolerance(self, value : Optional[float]) -> None:
        '''X and Y snapping tolerance.'''
        raise NotImplementedError()
    
    @property
    def z_tolerance(self) -> Optional[float]:
        '''Z snapping tolerance.'''
        raise NotImplementedError()
    
    @z_tolerance.setter
    def z_tolerance(self, value : Optional[float]) -> None:
        '''Z snapping tolerance.'''
        raise NotImplementedError()
    
    @property
    def m_tolerance(self) -> Optional[float]:
        '''M snapping tolerance.'''
        raise NotImplementedError()
    
    @m_tolerance.setter
    def m_tolerance(self, value : Optional[float]) -> None:
        '''M snapping tolerance.'''
        raise NotImplementedError()
    
    @property
    def coordinate_precision_grid(self) -> aspose.gis.formats.filegdb.FileGdbCoordinatePrecisionGrid:
        '''A coordinate precision grid to use in new layer.'''
        raise NotImplementedError()
    
    @coordinate_precision_grid.setter
    def coordinate_precision_grid(self, value : aspose.gis.formats.filegdb.FileGdbCoordinatePrecisionGrid) -> None:
        '''A coordinate precision grid to use in new layer.'''
        raise NotImplementedError()
    
    @property
    def ensure_valid_coordinates_range(self) -> bool:
        '''Whether coordinates should be in valid range.'''
        raise NotImplementedError()
    
    @ensure_valid_coordinates_range.setter
    def ensure_valid_coordinates_range(self, value : bool) -> None:
        '''Whether coordinates should be in valid range.'''
        raise NotImplementedError()
    

