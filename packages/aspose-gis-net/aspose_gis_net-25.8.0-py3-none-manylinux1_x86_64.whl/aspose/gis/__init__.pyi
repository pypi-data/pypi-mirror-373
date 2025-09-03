
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

class AbstractPath:
    '''An ``AbstractPath`` is a base class for classes that specify a unique location in an environment similar to a filesystem,
    like a local filesystem, a remote file storage or a ZIP archive, among others.'''
    
    @staticmethod
    def from_local_path(path : str) -> aspose.gis.AbstractPath:
        '''Creates an :py:class:`aspose.gis.AbstractPath` that represents a location on the local filesystem.
        
        :param path: A path on the local filesystem, like ``"C:\\file.shp"`` or ``"D:\\directory\\"``.
        :returns: An :py:class:`aspose.gis.AbstractPath` that represents the location defined by the ``path``.'''
        raise NotImplementedError()
    
    @staticmethod
    def from_stream(stream : io.RawIOBase) -> aspose.gis.AbstractPath:
        '''Creates an :py:class:`aspose.gis.AbstractPath` from a :py:class:`io.RawIOBase`.
        
        :param stream: A stream to create an :py:class:`aspose.gis.AbstractPath` from. ``Aspose.GIS`` does not dispose the stream.
        :returns: An instance of :py:class:`aspose.gis.AbstractPath` with the specified :py:class:`io.RawIOBase` as its content.'''
        raise NotImplementedError()
    
    def is_file(self) -> bool:
        '''Gets a value indicating whether this path points to an existing file that can be opened for reading.
        
        :returns: if location points to a file;  otherwise.'''
        raise NotImplementedError()
    
    def delete(self) -> None:
        '''Deletes a file pointed to by this path.'''
        raise NotImplementedError()
    
    def open(self, access : System.IO.FileAccess) -> io.RawIOBase:
        '''Opens this ``AbstractPath`` as a file.
        
        :param access: Specifies a subset of operations that can be performed on a :py:class:`io.RawIOBase`.
        :returns: A :py:class:`io.RawIOBase` opened with the specified :py:class:`System.IO.FileAccess`.'''
        raise NotImplementedError()
    
    def list_directory(self) -> Iterable[aspose.gis.AbstractPath]:
        '''Returns paths located inside this ``AbstractPath``, if it\'s a directory.
        
        :returns: Paths located inside this ``AbstractPath``.'''
        raise NotImplementedError()
    
    def combine(self, location : str) -> aspose.gis.AbstractPath:
        '''Combines this :py:class:`aspose.gis.AbstractPath` with specified path components.
        
        :param location: A path component to append to this :py:class:`aspose.gis.AbstractPath`.
        :returns: A new :py:class:`aspose.gis.AbstractPath` pointing to a :py:attr:`aspose.gis.AbstractPath.location` that is a combination of locations of this :py:class:`aspose.gis.AbstractPath` and
        the argument.'''
        raise NotImplementedError()
    
    def with_extension(self, new_extension : str) -> aspose.gis.AbstractPath:
        '''Returns a new :py:class:`aspose.gis.AbstractPath` with the file extension changed to the specified value.
        
        :param new_extension: A new extension.
        :returns: A new :py:class:`aspose.gis.AbstractPath`, that points to a file in the same directory, but with a new extension.'''
        raise NotImplementedError()
    
    def get_file_name(self) -> str:
        '''Returns the file name and extension of this :py:class:`aspose.gis.AbstractPath`.
        
        :returns: The characters after the last :py:attr:`aspose.gis.AbstractPath.separator` character in the :py:attr:`aspose.gis.AbstractPath.location`. If the
        last character is the :py:attr:`aspose.gis.AbstractPath.separator` character, an empty string is returned. If there is no
        :py:attr:`aspose.gis.AbstractPath.separator` characters in the :py:attr:`aspose.gis.AbstractPath.location`, the :py:attr:`aspose.gis.AbstractPath.location` itself
        is returned.'''
        raise NotImplementedError()
    
    def get_file_name_without_extension(self) -> str:
        '''Returns the file name of this :py:class:`aspose.gis.AbstractPath` without the extension.
        
        :returns: The string returned by :py:func:`aspose.gis.AbstractPath.get_file_name` minus the last period and all characters following it.'''
        raise NotImplementedError()
    
    def get_extension(self) -> str:
        '''Returns the extension of this :py:class:`aspose.gis.AbstractPath`.
        
        :returns: The extension of this :py:class:`aspose.gis.AbstractPath` (including the period ".") or
        an empty string if the :py:class:`aspose.gis.AbstractPath` has no extension.'''
        raise NotImplementedError()
    
    @property
    def location(self) -> str:
        '''Gets a string representation of the location of this ``AbstractPath``.'''
        raise NotImplementedError()
    
    @property
    def separator(self) -> str:
        '''Gets a separator character used to separate directory levels of the :py:attr:`aspose.gis.AbstractPath.location` string.'''
        raise NotImplementedError()
    

class AttributesConverterActions:
    '''Optional actions with attributes of the destination layer.'''
    
    @property
    def exclude(self) -> bool:
        '''Sets  to exclude the attribute from the destination layer. The initial value is .'''
        raise NotImplementedError()
    
    @exclude.setter
    def exclude(self, value : bool) -> None:
        '''Sets  to exclude the attribute from the destination layer. The initial value is .'''
        raise NotImplementedError()
    

class BaseFeatureAttributeCollection:
    '''A :py:class:`aspose.gis.FeatureAttributeCollection` defines what attributes are available for a :py:class:`aspose.gis.Feature`.'''
    
    @overload
    def remove(self, name : str) -> None:
        '''Removes the attribute from the collection.
        
        :param name: Name of the attribute.'''
        raise NotImplementedError()
    
    @overload
    def remove(self, index : int) -> None:
        '''Removes the attribute from the collection.
        
        :param index: Index of the attribute.'''
        raise NotImplementedError()
    
    def lock(self) -> None:
        '''Locks this attribute collection to prevent further modifications.'''
        raise NotImplementedError()
    
    def contains(self, name : str) -> bool:
        '''Determines whether the attribute collection contains an attribute with the specified name.
        
        :param name: Name of the attribute.
        :returns: if the attribute collection contains and attribute with the specified name; otherwise, .'''
        raise NotImplementedError()
    
    def index_of(self, name : str) -> int:
        '''Searches for the attribute and returns the its zero-based index.
        
        :param name: Name of the attribute.
        :returns: The zero-based index of the attribute within the collection, if found; otherwise, –1.'''
        raise NotImplementedError()
    
    def add(self, attribute : aspose.gis.FeatureAttribute) -> None:
        '''Adds an attribute to the collection.
        
        :param attribute: The attribute to add.'''
        raise NotImplementedError()
    
    @property
    def count(self) -> int:
        '''Gets the number of attributes in a :py:class:`aspose.gis.Feature`.'''
        raise NotImplementedError()
    
    @property
    def is_locked(self) -> bool:
        '''Gets a value indicating whether this attribute collection is locked.'''
        raise NotImplementedError()
    
    def __getitem__(self, key : int) -> aspose.gis.FeatureAttribute:
        '''Gets or sets the :py:class:`aspose.gis.FeatureAttribute` at the specified index.'''
        raise NotImplementedError()
    
    def __setitem__(self, key : int, value : aspose.gis.FeatureAttribute):
        raise NotImplementedError()
    

class ConversionOptions:
    '''Options for converting data between formats.'''
    
    @property
    def source_driver_options(self) -> aspose.gis.DriverOptions:
        '''Driver-specific options for the source layer.'''
        raise NotImplementedError()
    
    @source_driver_options.setter
    def source_driver_options(self, value : aspose.gis.DriverOptions) -> None:
        '''Driver-specific options for the source layer.'''
        raise NotImplementedError()
    
    @property
    def destination_driver_options(self) -> aspose.gis.DriverOptions:
        '''Driver-specific options for the destination layer.'''
        raise NotImplementedError()
    
    @destination_driver_options.setter
    def destination_driver_options(self, value : aspose.gis.DriverOptions) -> None:
        '''Driver-specific options for the destination layer.'''
        raise NotImplementedError()
    
    @property
    def attributes_converter(self) -> aspose.gis.IAttributesConverter:
        '''A custom converter for attributes. It allows us to rename or exclude destination attributes.
        If not , it is called for each attribute of the source layer and is expected to change it if necessary.'''
        raise NotImplementedError()
    
    @attributes_converter.setter
    def attributes_converter(self, value : aspose.gis.IAttributesConverter) -> None:
        '''A custom converter for attributes. It allows us to rename or exclude destination attributes.
        If not , it is called for each attribute of the source layer and is expected to change it if necessary.'''
        raise NotImplementedError()
    
    @property
    def destination_spatial_reference_system(self) -> aspose.gis.spatialreferencing.SpatialReferenceSystem:
        '''Spatial reference system to assign to destination layer.'''
        raise NotImplementedError()
    
    @destination_spatial_reference_system.setter
    def destination_spatial_reference_system(self, value : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> None:
        '''Spatial reference system to assign to destination layer.'''
        raise NotImplementedError()
    

class DatabaseDriver(Driver):
    '''A driver for a specific database based format.'''
    

class DatabaseDriverOptions(DriverOptions):
    '''Options for a :py:class:`aspose.gis.DatabaseDriver`.'''
    
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
    def spatial_reference_system_mode(self) -> aspose.gis.SpatialReferenceSystemMode:
        '''Determines how the unknown geometries\' SRS for the database should be handle when they are added to the layer.
        The default value is :py:attr:`aspose.gis.SpatialReferenceSystemMode.THROW_EXCEPTION`.'''
        raise NotImplementedError()
    
    @spatial_reference_system_mode.setter
    def spatial_reference_system_mode(self, value : aspose.gis.SpatialReferenceSystemMode) -> None:
        '''Determines how the unknown geometries\' SRS for the database should be handle when they are added to the layer.
        The default value is :py:attr:`aspose.gis.SpatialReferenceSystemMode.THROW_EXCEPTION`.'''
        raise NotImplementedError()
    

class Dataset:
    '''A dataset is the collection of :py:class:`aspose.gis.VectorLayer` instances.'''
    
    @overload
    @staticmethod
    def open(path : str, driver : aspose.gis.FileDriver) -> aspose.gis.Dataset:
        '''Opens the dataset.
        
        :param path: Path to the dataset.
        :param driver: Driver to use.
        :returns: An instance of :py:class:`aspose.gis.Dataset`.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def open(path : aspose.gis.AbstractPath, driver : aspose.gis.FileDriver) -> aspose.gis.Dataset:
        '''Opens the dataset.
        
        :param path: Path to the dataset.
        :param driver: Driver to use.
        :returns: An instance of :py:class:`aspose.gis.Dataset`.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def open(path : str, driver : aspose.gis.FileDriver, options : aspose.gis.DriverOptions) -> aspose.gis.Dataset:
        '''Opens the dataset.
        
        :param path: Path to the dataset.
        :param driver: Driver to use.
        :param options: Driver-specific options.
        :returns: An instance of :py:class:`aspose.gis.Dataset`.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def open(path : aspose.gis.AbstractPath, driver : aspose.gis.FileDriver, options : aspose.gis.DriverOptions) -> aspose.gis.Dataset:
        '''Opens the dataset.
        
        :param path: Path to the dataset.
        :param driver: Driver to use.
        :param options: Driver-specific options.
        :returns: An instance of :py:class:`aspose.gis.Dataset`.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def create(path : str, driver : aspose.gis.FileDriver) -> aspose.gis.Dataset:
        '''Creates a dataset.
        
        :param path: Path to the dataset.
        :param driver: Driver to use.
        :returns: An instance of :py:class:`aspose.gis.Dataset`.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def create(path : aspose.gis.AbstractPath, driver : aspose.gis.FileDriver) -> aspose.gis.Dataset:
        '''Creates a dataset.
        
        :param path: Path to the dataset.
        :param driver: Driver to use.
        :returns: An instance of :py:class:`aspose.gis.Dataset`.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def create(path : str, driver : aspose.gis.FileDriver, options : aspose.gis.DriverOptions) -> aspose.gis.Dataset:
        '''Creates a dataset.
        
        :param path: Path to the dataset.
        :param driver: Driver to use.
        :param options: Driver-specific options.
        :returns: An instance of :py:class:`aspose.gis.Dataset`.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def create(path : aspose.gis.AbstractPath, driver : aspose.gis.FileDriver, options : aspose.gis.DriverOptions) -> aspose.gis.Dataset:
        '''Creates a dataset.
        
        :param path: Path to the dataset.
        :param driver: Driver to use.
        :param options: Driver-specific options.
        :returns: An instance of :py:class:`aspose.gis.Dataset`.'''
        raise NotImplementedError()
    
    @overload
    def create_layer(self) -> aspose.gis.VectorLayer:
        '''Creates a new vector layer and opens it for appending.
        
        :returns: A :py:class:`aspose.gis.VectorLayer` opened for writing.'''
        raise NotImplementedError()
    
    @overload
    def create_layer(self, spatial_reference_system : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> aspose.gis.VectorLayer:
        '''Creates a new vector layer and opens it for appending.
        
        :param spatial_reference_system: Spatial reference system of the new layer.
        :returns: A :py:class:`aspose.gis.VectorLayer` opened for writing.'''
        raise NotImplementedError()
    
    @overload
    def create_layer(self, options : aspose.gis.DriverOptions, spatial_reference_system : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> aspose.gis.VectorLayer:
        '''Creates a new vector layer and opens it for appending.
        
        :param options: Open options.
        :param spatial_reference_system: Spatial reference system of the new layer.
        :returns: A :py:class:`aspose.gis.VectorLayer` opened for writing.'''
        raise NotImplementedError()
    
    @overload
    def create_layer(self, name : str, spatial_reference_system : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> aspose.gis.VectorLayer:
        '''Creates a new vector layer with specified name and opens it for appending.
        
        :param name: Name of the layer.
        :param spatial_reference_system: Spatial reference system of the new layer.
        :returns: A :py:class:`aspose.gis.VectorLayer` opened for writing.'''
        raise NotImplementedError()
    
    @overload
    def create_layer(self, name : str, options : aspose.gis.DriverOptions, spatial_reference_system : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> aspose.gis.VectorLayer:
        '''Creates a new vector layer with specified name and opens it for appending.
        
        :param name: Name of the layer.
        :param options: Open options.
        :param spatial_reference_system: Spatial reference system of the new layer.
        :returns: A :py:class:`aspose.gis.VectorLayer` opened for writing.'''
        raise NotImplementedError()
    
    def get_layer_name(self, index : int) -> str:
        '''Gets the name of the layer at specified index.
        
        :param index: Index of the layer.
        :returns: Name of the layer.'''
        raise NotImplementedError()
    
    def open_layer(self, name : str, options : aspose.gis.DriverOptions) -> aspose.gis.VectorLayer:
        '''Opens the layer with specified name for reading.
        
        :param name: Name of the layer to open.
        :param options: Open options.
        :returns: The layer opened for reading.'''
        raise NotImplementedError()
    
    def open_layer_at(self, index : int, options : aspose.gis.DriverOptions) -> aspose.gis.VectorLayer:
        '''Opens the layer at specified index for reading.
        
        :param index: Index of the layer to open.
        :param options: Open options.
        :returns: The layer opened for reading.'''
        raise NotImplementedError()
    
    def edit_layer(self, name : str, options : aspose.gis.DriverOptions, spatial_reference_system : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> aspose.gis.VectorLayer:
        '''Opens the layer with specified name for editing.
        
        :param name: Name of the layer to edit.
        :param options: Open options.
        :param spatial_reference_system: Spatial reference system for new geometries.
        :returns: The layer opened for editing.'''
        raise NotImplementedError()
    
    def edit_layer_at(self, index : int, options : aspose.gis.DriverOptions, spatial_reference_system : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> aspose.gis.VectorLayer:
        '''Opens the layer with specified name for editing.
        
        :param index: Index of the layer to edit.
        :param options: Open options.
        :param spatial_reference_system: Spatial reference system for new geometries.
        :returns: The layer opened for editing.'''
        raise NotImplementedError()
    
    def remove_layer(self, name : str) -> None:
        '''Removes the vector layer with specified name.
        
        :param name: Name of the layer'''
        raise NotImplementedError()
    
    def remove_layer_at(self, index : int) -> None:
        '''Removes the vector layer at specified index.
        
        :param index: Index of the layer'''
        raise NotImplementedError()
    
    def has_layer_with_name(self, name : str) -> bool:
        '''Check has current dataset a layer with specific name
        
        :param name: Name of the layer
        :returns: , if dataset has layer with this name; otherwise,'''
        raise NotImplementedError()
    
    def rename_layer(self, current_name : str, new_name : str) -> None:
        '''Rename layer in dataset
        
        :param current_name: Current name of the layer
        :param new_name: New name for the layer'''
        raise NotImplementedError()
    
    @property
    def can_create_layers(self) -> bool:
        '''Gets a value indicating whether this dataset can create vector layers.'''
        raise NotImplementedError()
    
    @property
    def can_remove_layers(self) -> bool:
        '''Gets a value indicating whether this dataset can remove vector layers.'''
        raise NotImplementedError()
    
    @property
    def driver(self) -> aspose.gis.Driver:
        '''Gets the :py:attr:`aspose.gis.Dataset.driver` that instantiated this dataset.'''
        raise NotImplementedError()
    
    @property
    def layers_count(self) -> int:
        '''Gets the number of layers in this dataset.'''
        raise NotImplementedError()
    

class Driver:
    '''A base class for drivers to GIS data.'''
    

class DriverOptions:
    '''Options for a :py:class:`aspose.gis.Driver`.'''
    
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
    

class Drivers:
    '''Drivers for all supported formats.'''
    
    esri_json : aspose.gis.formats.esrijson.EsriJsonDriver
    '''A driver for the EsriJson format.'''
    gdal : aspose.gis.formats.gdal.GdalDriver
    '''A driver for the GDAL format.'''
    geo_json : aspose.gis.formats.geojson.GeoJsonDriver
    '''A driver for the GeoJSON format.'''
    geo_json_seq : aspose.gis.formats.geojsonseq.GeoJsonSeqDriver
    '''A driver for the GeoJsonSeq: sequence of GeoJSON features.'''
    in_memory : aspose.gis.formats.inmemory.InMemoryDriver
    '''A driver for work with data in memory.'''
    in_file : aspose.gis.formats.infile.InFileDriver
    '''A driver for work with data and save changes in file on HDD.'''
    kml : aspose.gis.formats.kml.KmlDriver
    '''A driver for the KML format.'''
    shapefile : aspose.gis.formats.shapefile.ShapefileDriver
    '''A driver for the Shapefile format.'''
    osm_xml : aspose.gis.formats.osmxml.OsmXmlDriver
    '''A driver for the OSM XML format.'''
    gpx : aspose.gis.formats.gpx.GpxDriver
    '''A driver for the GPX format.'''
    gml : aspose.gis.formats.gml.GmlDriver
    '''A driver for the GML format.'''
    file_gdb : aspose.gis.formats.filegdb.FileGdbDriver
    '''A driver for the ESRI File Geodatabase format.'''
    topo_json : aspose.gis.formats.topojson.TopoJsonDriver
    '''A driver for the TopoJSON format.'''
    map_info_interchange : aspose.gis.formats.mapinfointerchange.MapInfoInterchangeDriver
    '''A driver for the MapInfo Interchange Format.'''
    map_info_tab : aspose.gis.formats.mapinfotab.MapInfoTabDriver
    '''A driver for the MapInfo Tab format.'''
    post_gis : aspose.gis.formats.postgis.PostGisDriver
    '''A driver for the PostGIS database.'''
    sql_server : aspose.gis.formats.sqlserver.SqlServerDriver
    '''A driver for the SQL Server database.'''
    esri_ascii : aspose.gis.formats.esriascii.EsriAsciiDriver
    '''A driver for the Esri AscII raster format.'''
    geo_tiff : aspose.gis.formats.geotiff.GeoTiffDriver
    '''A driver for the GeoTIFF or TIFF raster format.'''
    world_raster : aspose.gis.formats.worldfile.WorldRasterDriver
    '''A driver for raster.formats with world file'''
    jpeg_w : aspose.gis.formats.jpegw.JpegWDriver
    '''A driver for the JpegW raster format.'''
    png_w : aspose.gis.formats.pngw.PngWDriver
    '''A driver for the PngW raster format.'''
    bmp_w : aspose.gis.formats.bmpw.BmpWDriver
    '''A driver for the BmpW raster format.'''
    tiff_w : aspose.gis.formats.tiffw.TiffWDriver
    '''A driver for the TiffW raster format.'''
    xyz_tiles : aspose.gis.formats.xyztile.XyzTilesDriver
    '''A driver for the tiled web map like OpenStreetMaps, Google Maps, etc.'''
    csv : aspose.gis.formats.csv.CsvDriver
    '''A driver for the CSV format.'''
    geo_package : aspose.gis.formats.geopackage.GeoPackageDriver
    '''A driver for the GeoPackage format.'''

class DynamicFeature(Feature):
    '''A geographic feature composed of a geometry and user-defined attributes.'''
    
    @overload
    def get_values(self, values : List[Any], default_value : Any) -> int:
        '''Returns the values for all the attributes in an array.
        
        :param values: The array into which to copy the attributes values.
        :param default_value: The value to return if the attribute value is missing (unset). Default value is .
        Consider to use \':py:class:`System.DBNull`.Value\' for separating \'unset\' and \'\' values.
        :returns: A number of attributes copied.'''
        raise NotImplementedError()
    
    @overload
    def get_values(self, values_count : int, default_value : Any) -> List[Any]:
        '''Returns the values for all the attributes in an array.
        
        :param values_count: The values count.
        :param default_value: The value to return if the attribute value is missing (unset). Default value is .
        Consider to use \':py:class:`System.DBNull`.Value\' for separating \'unset\' and \'\' values.
        :returns: A number of attributes copied.'''
        raise NotImplementedError()
    
    def get_value(self, attribute_name : str) -> Any:
        '''Gets the value of an attribute.
        
        :param attribute_name: Name of the attribute.
        :returns: Value of the attribute.'''
        raise NotImplementedError()
    
    def get_values_list(self, attribute_name : str, separator : str, count : int) -> List[Any]:
        '''Gets the values list. Non-generic analog of List T GetValuesList
        
        :param attribute_name: Name of the attribute.
        :param separator: A string which is used to separate attribute name and index value of sequence.
        :param count: Count of values to return (missed value fill as null)
        :returns: List of values of the attributes which names different by sequence index value.'''
        raise NotImplementedError()
    
    def get_value_or_default(self, attribute_name : str, default_value : Any) -> Any:
        '''Gets the value of an attribute, or :py:attr:`aspose.gis.FeatureAttribute.default_value` if the value is unset or ``null``.
        
        :param attribute_name: Name of the attribute.
        :param default_value: The value to return if the attribute value is missing. Default value is .
        :returns: Value of the attribute.'''
        raise NotImplementedError()
    
    def set_value(self, attribute_name : str, value : Any) -> None:
        '''Sets the value. Non-generic analog of void SetValue (string attributeName, T value)
        
        :param attribute_name: The name of the attribute.
        :param value: The value of the attribute.'''
        raise NotImplementedError()
    
    def is_value_null(self, attribute_name : str) -> bool:
        '''Determines whether the specified attribute has been explicitly set to ``null`` value.
        
        :param attribute_name: Name of the attribute.
        :returns: if the attribute value is ``null``; otherwise, .'''
        raise NotImplementedError()
    
    def set_value_null(self, attribute_name : str) -> None:
        '''Sets value of the attribute to ``null``.
        
        :param attribute_name: The name of the attribute.'''
        raise NotImplementedError()
    
    def unset_value(self, attribute_name : str) -> None:
        '''Removes the attribute value from this feature.
        
        :param attribute_name: Name of the attribute.'''
        raise NotImplementedError()
    
    def is_value_set(self, attribute_name : str) -> bool:
        '''Checks if the attribute value is set in this feature.
        
        :param attribute_name: Name of the attribute.
        :returns: if value for the specified attribute is set; otherwise, .'''
        raise NotImplementedError()
    
    def copy_values(self, input_feature : aspose.gis.Feature) -> None:
        '''Copies values of attributes from another feature.
        
        :param input_feature: The feature to copy values from.'''
        raise NotImplementedError()
    
    def get_values_dump(self, default_value : Any) -> List[Any]:
        '''Returns the values for all the attributes in an array.
        Consider to use :py:func:`aspose.gis.DynamicFeature.get_values` method to avoid additional memory allocation.
        
        :param default_value: The value to return if the attribute value is missing (unset). Default value is .
        Consider to use \':py:class:`System.DBNull`.Value\' for separating \'unset\' and \'\' values.
        :returns: A new array into which to copy the attributes values.'''
        raise NotImplementedError()
    
    def set_values(self, values : List[Any]) -> int:
        '''Sets new values for all of the attributes.
        Also consider to use :py:func:`aspose.gis.DynamicFeature.copy_values` method to streamline setting values in one call.
        
        :param values: The array of new values.
        :returns: The number of attribute values set.'''
        raise NotImplementedError()
    
    def get_as_node(self) -> aspose.gis.NodeLink:
        '''Gets the feature as node. This can be helpful for the custom data
        
        :returns: The NodeLink to feature'''
        raise NotImplementedError()
    
    @property
    def geometry(self) -> aspose.gis.geometries.IGeometry:
        '''Gets geometry of the feature.
        Cannot be , use :py:attr:`aspose.gis.geometries.Geometry.null` to indicate missing geometry.'''
        raise NotImplementedError()
    
    @geometry.setter
    def geometry(self, value : aspose.gis.geometries.IGeometry) -> None:
        '''Sets geometry of the feature.
        Cannot be , use :py:attr:`aspose.gis.geometries.Geometry.null` to indicate missing geometry.'''
        raise NotImplementedError()
    

class Extent:
    '''A two-dimensional spatial bounding box.'''
    
    @overload
    def grow(self, extent : aspose.gis.Extent) -> None:
        '''Grows this extent so it includes the argument.
        
        :param extent: Other extent.'''
        raise NotImplementedError()
    
    @overload
    def grow(self, x : float, y : float) -> None:
        '''Grows this extent so it includes the specified point.
        
        :param x: X coordinate to include.
        :param y: Y coordinate to include.'''
        raise NotImplementedError()
    
    @overload
    def contains(self, x : float, y : float) -> bool:
        '''Determines whether this extent contains a coordinate defined by the arguments.
        
        :param x: X of the coordinate.
        :param y: Y of the coordinate.
        :returns: Value, indicating whether coordinate is inside bounding box.'''
        raise NotImplementedError()
    
    @overload
    def contains(self, extent : aspose.gis.Extent) -> bool:
        '''Determines whether this extent contains the argument.
        
        :param extent: Another extent.
        :returns: Value, indicating whether this extent contains the argument.'''
        raise NotImplementedError()
    
    @overload
    def contains(self, geometry : aspose.gis.geometries.IGeometry) -> bool:
        '''Determines whether this extent contains the argument.
        
        :param geometry: A geometry to test for containment.
        :returns: Value, indicating whether this extent contains the argument.'''
        raise NotImplementedError()
    
    @overload
    def intersects(self, extent : aspose.gis.Extent) -> bool:
        '''Determines whether this extent intersects with the argument.
        
        :param extent: Another extent.
        :returns: Value, indicating whether this extent intersects with the argument.'''
        raise NotImplementedError()
    
    @overload
    def intersects(self, geometry : aspose.gis.geometries.IGeometry) -> bool:
        '''Determines whether this extent intersects with the argument.
        
        :param geometry: A geometry to test for intersection
        :returns: Value, indicating whether this extent intersects with the argument.'''
        raise NotImplementedError()
    
    def get_transformed(self, target_srs : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> aspose.gis.Extent:
        '''Returns new extent in specified :py:class:`aspose.gis.spatialreferencing.SpatialReferenceSystem` that contains this extent.
        
        :param target_srs: :py:class:`aspose.gis.spatialreferencing.SpatialReferenceSystem` to transform to.
        :returns: The result of transformation this extent to the specified SRS.'''
        raise NotImplementedError()
    
    def normalize(self) -> None:
        '''Swaps :py:attr:`aspose.gis.Extent.x_min` with :py:attr:`aspose.gis.Extent.x_max` if :py:attr:`aspose.gis.Extent.width` is negative and
        :py:attr:`aspose.gis.Extent.y_min` with :py:attr:`aspose.gis.Extent.y_max` if :py:attr:`aspose.gis.Extent.height` is negative.'''
        raise NotImplementedError()
    
    def clone(self) -> aspose.gis.Extent:
        '''Clones this instance.
        
        :returns: Clone of this instance.'''
        raise NotImplementedError()
    
    def to_polygon(self) -> aspose.gis.geometries.Polygon:
        '''Converts this extent to a rectangular polygon that represents it.
        
        :returns: A rectangular :py:class:`aspose.gis.geometries.Polygon` that represents this extent. For invalid extents
        an empty polygon is returned.'''
        raise NotImplementedError()
    
    def grow_x(self, value : float) -> None:
        '''Grows this extent along the X axis so it includes the specified value.
        
        :param value: Value to include.'''
        raise NotImplementedError()
    
    def grow_y(self, value : float) -> None:
        '''Grows this extent along the Y axis so it includes the specified value.
        
        :param value: Value to include.'''
        raise NotImplementedError()
    
    def equals(self, other : aspose.gis.Extent) -> bool:
        '''Indicates whether the current object is equal to another object of the same type.
        
        :param other: An object to compare with this object.
        :returns: if the current object is equal to the ``other`` parameter; otherwise, .'''
        raise NotImplementedError()
    
    @property
    def x_min(self) -> float:
        '''Minimum value of the X coordinate.'''
        raise NotImplementedError()
    
    @x_min.setter
    def x_min(self, value : float) -> None:
        '''Minimum value of the X coordinate.'''
        raise NotImplementedError()
    
    @property
    def x_max(self) -> float:
        '''Maximum value of the X coordinate.'''
        raise NotImplementedError()
    
    @x_max.setter
    def x_max(self, value : float) -> None:
        '''Maximum value of the X coordinate.'''
        raise NotImplementedError()
    
    @property
    def y_min(self) -> float:
        '''Minimum value of the Y coordinate.'''
        raise NotImplementedError()
    
    @y_min.setter
    def y_min(self, value : float) -> None:
        '''Minimum value of the Y coordinate.'''
        raise NotImplementedError()
    
    @property
    def y_max(self) -> float:
        '''Maximum value of the Y coordinate.'''
        raise NotImplementedError()
    
    @y_max.setter
    def y_max(self, value : float) -> None:
        '''Maximum value of the Y coordinate.'''
        raise NotImplementedError()
    
    @property
    def spatial_reference_system(self) -> aspose.gis.spatialreferencing.SpatialReferenceSystem:
        ''':py:class:`aspose.gis.spatialreferencing.SpatialReferenceSystem` associated with this extent.
        Can be  if :py:attr:`aspose.gis.Extent.spatial_reference_system` is unknown.
        Use :py:func:`aspose.gis.Extent.get_transformed`
        in order to transform extent between difference spatial reference systems.'''
        raise NotImplementedError()
    
    @spatial_reference_system.setter
    def spatial_reference_system(self, value : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> None:
        ''':py:class:`aspose.gis.spatialreferencing.SpatialReferenceSystem` associated with this extent.
        Can be  if :py:attr:`aspose.gis.Extent.spatial_reference_system` is unknown.
        Use :py:func:`aspose.gis.Extent.get_transformed`
        in order to transform extent between difference spatial reference systems.'''
        raise NotImplementedError()
    
    @property
    def center(self) -> aspose.gis.geometries.IPoint:
        '''Center of the extent.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Width of the extent.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Height of the extent.'''
        raise NotImplementedError()
    
    @property
    def is_valid(self) -> bool:
        '''Determines whether this :py:class:`aspose.gis.Extent` is valid.'''
        raise NotImplementedError()
    

class Feature:
    '''A geographic feature composed of a geometry and user-defined attributes.'''
    
    @overload
    def get_values(self, values_count : int, default_value : Any) -> List[Any]:
        '''Returns the values for all the attributes in an array.
        
        :param values_count: The values count.
        :param default_value: The value to return if the attribute value is missing (unset). Default value is .
        Consider to use \':py:class:`System.DBNull`.Value\' for separating \'unset\' and \'\' values.
        :returns: A number of attributes copied.'''
        raise NotImplementedError()
    
    @overload
    def get_values(self, values : List[Any], default_value : Any) -> int:
        '''Returns the values for all the attributes in an array.
        
        :param values: The array into which to copy the attributes values.
        :param default_value: The value to return if the attribute value is missing (unset). Default value is .
        Consider to use \':py:class:`System.DBNull`.Value\' for separating \'unset\' and \'\' values.
        :returns: A number of attributes copied.'''
        raise NotImplementedError()
    
    def get_value(self, attribute_name : str) -> Any:
        '''Gets the value of an attribute.
        
        :param attribute_name: Name of the attribute.
        :returns: Value of the attribute.'''
        raise NotImplementedError()
    
    def get_values_list(self, attribute_name : str, separator : str, count : int) -> List[Any]:
        '''Gets the values list. Non-generic analog of List T GetValuesList
        
        :param attribute_name: Name of the attribute.
        :param separator: A string which is used to separate attribute name and index value of sequence.
        :param count: Count of values to return (missed value fill as null)
        :returns: List of values of the attributes which names different by sequence index value.'''
        raise NotImplementedError()
    
    def get_value_or_default(self, attribute_name : str, default_value : Any) -> Any:
        '''Gets the value of an attribute, or :py:attr:`aspose.gis.FeatureAttribute.default_value` if the value is unset or ``null``.
        
        :param attribute_name: Name of the attribute.
        :param default_value: The value to return if the attribute value is missing. Default value is .
        :returns: Value of the attribute.'''
        raise NotImplementedError()
    
    def set_value(self, attribute_name : str, value : Any) -> None:
        '''Sets the value. Non-generic analog of void SetValue (string attributeName, T value)
        
        :param attribute_name: The name of the attribute.
        :param value: The value of the attribute.'''
        raise NotImplementedError()
    
    def is_value_null(self, attribute_name : str) -> bool:
        '''Determines whether the specified attribute has been explicitly set to ``null`` value.
        
        :param attribute_name: Name of the attribute.
        :returns: if the attribute value is ``null``; otherwise, .'''
        raise NotImplementedError()
    
    def set_value_null(self, attribute_name : str) -> None:
        '''Sets value of the attribute to ``null``.
        
        :param attribute_name: The name of the attribute.'''
        raise NotImplementedError()
    
    def unset_value(self, attribute_name : str) -> None:
        '''Removes the attribute value from this feature.
        
        :param attribute_name: Name of the attribute.'''
        raise NotImplementedError()
    
    def is_value_set(self, attribute_name : str) -> bool:
        '''Checks if the attribute value is set in this feature.
        
        :param attribute_name: Name of the attribute.
        :returns: if value for the specified attribute is set; otherwise, .'''
        raise NotImplementedError()
    
    def copy_values(self, input_feature : aspose.gis.Feature) -> None:
        '''Copies values of attributes from another feature.
        
        :param input_feature: The feature to copy values from.'''
        raise NotImplementedError()
    
    def get_values_dump(self, default_value : Any) -> List[Any]:
        '''Returns the values for all the attributes in an array.
        Consider to use :py:func:`aspose.gis.Feature.get_values` method to avoid additional memory allocation.
        
        :param default_value: The value to return if the attribute value is missing (unset). Default value is .
        Consider to use \':py:class:`System.DBNull`.Value\' for separating \'unset\' and \'\' values.
        :returns: A new array into which to copy the attributes values.'''
        raise NotImplementedError()
    
    def set_values(self, values : List[Any]) -> int:
        '''Sets new values for all of the attributes.
        Also consider to use :py:func:`aspose.gis.Feature.copy_values` method to streamline setting values in one call.
        
        :param values: The array of new values.
        :returns: The number of attribute values set.'''
        raise NotImplementedError()
    
    @property
    def geometry(self) -> aspose.gis.geometries.IGeometry:
        '''Gets geometry of the feature.
        Cannot be , use :py:attr:`aspose.gis.geometries.Geometry.null` to indicate missing geometry.'''
        raise NotImplementedError()
    
    @geometry.setter
    def geometry(self, value : aspose.gis.geometries.IGeometry) -> None:
        '''Sets geometry of the feature.
        Cannot be , use :py:attr:`aspose.gis.geometries.Geometry.null` to indicate missing geometry.'''
        raise NotImplementedError()
    

class FeatureAttribute:
    '''An attribute of a :py:class:`aspose.gis.Feature`.'''
    
    def lock(self) -> None:
        '''Locks this attribute.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Gets the name of the attribute.'''
        raise NotImplementedError()
    
    @name.setter
    def name(self, value : str) -> None:
        '''Gets the name of the attribute.'''
        raise NotImplementedError()
    
    @property
    def data_type(self) -> aspose.gis.AttributeDataType:
        '''Gets the data type of the attribute.'''
        raise NotImplementedError()
    
    @data_type.setter
    def data_type(self, value : aspose.gis.AttributeDataType) -> None:
        '''Gets the data type of the attribute.'''
        raise NotImplementedError()
    
    @property
    def type_name(self) -> str:
        '''The type name of the attribute.'''
        raise NotImplementedError()
    
    @type_name.setter
    def type_name(self, value : str) -> None:
        '''The type name of the attribute.'''
        raise NotImplementedError()
    
    @property
    def can_be_null(self) -> bool:
        '''Gets a value indicating whether this instance can be null.'''
        raise NotImplementedError()
    
    @can_be_null.setter
    def can_be_null(self, value : bool) -> None:
        '''Gets a value indicating whether this instance can be null.'''
        raise NotImplementedError()
    
    @property
    def can_be_unset(self) -> bool:
        '''Gets a value indicating whether value for this attribute can be omitted.'''
        raise NotImplementedError()
    
    @can_be_unset.setter
    def can_be_unset(self, value : bool) -> None:
        '''Sets a value indicating whether value for this attribute can be omitted.'''
        raise NotImplementedError()
    
    @property
    def default_value(self) -> Any:
        '''Gets a value for the attribute, that indicates missing data.'''
        raise NotImplementedError()
    
    @default_value.setter
    def default_value(self, value : Any) -> None:
        '''Sets a value for the attribute, that indicates missing data.'''
        raise NotImplementedError()
    
    @property
    def has_custom_default_value(self) -> bool:
        '''Gets a value indicating whether the pre-defined default value for this attribute was overridden with a custom value.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> Optional[int]:
        '''Gets maximum allowed width of character representation of the attribute.'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : Optional[int]) -> None:
        '''Sets maximum allowed width of character representation of the attribute.'''
        raise NotImplementedError()
    
    @property
    def precision(self) -> Optional[int]:
        '''Gets maximum number of decimal digits to store.'''
        raise NotImplementedError()
    
    @precision.setter
    def precision(self, value : Optional[int]) -> None:
        '''Sets maximum number of decimal digits to store.'''
        raise NotImplementedError()
    
    @property
    def is_locked(self) -> bool:
        '''Gets a value indicating whether this attribute is locked.'''
        raise NotImplementedError()
    

class FeatureAttributeCollection(BaseFeatureAttributeCollection):
    '''A :py:class:`aspose.gis.FeatureAttributeCollection` defines what attributes are available for a :py:class:`aspose.gis.Feature`.'''
    
    @overload
    def remove(self, name : str) -> None:
        '''Removes the attribute from the collection.
        
        :param name: Name of the attribute.'''
        raise NotImplementedError()
    
    @overload
    def remove(self, index : int) -> None:
        '''Removes the attribute from the collection.
        
        :param index: Index of the attribute.'''
        raise NotImplementedError()
    
    def lock(self) -> None:
        '''Locks this attribute collection to prevent further modifications.'''
        raise NotImplementedError()
    
    def contains(self, name : str) -> bool:
        '''Determines whether the attribute collection contains an attribute with the specified name.
        
        :param name: Name of the attribute.
        :returns: if the attribute collection contains and attribute with the specified name; otherwise, .'''
        raise NotImplementedError()
    
    def index_of(self, name : str) -> int:
        '''Searches for the attribute and returns the its zero-based index.
        
        :param name: Name of the attribute.
        :returns: The zero-based index of the attribute within the collection, if found; otherwise, –1.'''
        raise NotImplementedError()
    
    def add(self, attribute : aspose.gis.FeatureAttribute) -> None:
        '''Adds an attribute to the collection.
        
        :param attribute: The attribute to add.'''
        raise NotImplementedError()
    
    @property
    def count(self) -> int:
        '''Gets the number of attributes in a :py:class:`aspose.gis.Feature`.'''
        raise NotImplementedError()
    
    @property
    def is_locked(self) -> bool:
        '''Gets a value indicating whether this attribute collection is locked.'''
        raise NotImplementedError()
    
    def __getitem__(self, key : int) -> aspose.gis.FeatureAttribute:
        raise NotImplementedError()
    
    def __setitem__(self, key : int, value : aspose.gis.FeatureAttribute):
        raise NotImplementedError()
    

class FeatureStyle(IFeatureStyle):
    '''The abstract root class of the feature styles hierarchy.'''
    
    null : aspose.gis.IFeatureStyle
    '''Gets an instance of null style.'''

class FeaturesSequence:
    ''':py:class:`aspose.gis.FeaturesSequence` represents a set of vector features.'''
    
    @overload
    def where_intersects(self, sequence : aspose.gis.FeaturesSequence) -> aspose.gis.FeaturesSequence:
        '''Filters features based on the union of all geometries in other features sequence.
        
        :param sequence: Other features sequence.
        :returns: Features that intersect with the union of all geometries in other features sequence.'''
        raise NotImplementedError()
    
    @overload
    def where_intersects(self, geometry : aspose.gis.geometries.IGeometry) -> aspose.gis.FeaturesSequence:
        '''Filters features based on the provided geometry.
        
        :param geometry: Filter geometry.
        :returns: Features that intersect with the provided geometry.'''
        raise NotImplementedError()
    
    @overload
    def where_intersects(self, extent : aspose.gis.Extent) -> aspose.gis.FeaturesSequence:
        '''Filters features based on the extent.
        
        :param extent: Filter extent.
        :returns: Features that intersect with the provided geometry.'''
        raise NotImplementedError()
    
    @overload
    def save_to(self, destination_path : str, destination_driver : aspose.gis.FileDriver) -> None:
        '''Saves features sequence to layer.
        
        :param destination_path: Path to the output layer.
        :param destination_driver: The format driver for the output layer.'''
        raise NotImplementedError()
    
    @overload
    def save_to(self, destination_path : aspose.gis.AbstractPath, destination_driver : aspose.gis.FileDriver) -> None:
        '''Saves features sequence to layer.
        
        :param destination_path: Path to the output layer.
        :param destination_driver: The format driver for the output layer.'''
        raise NotImplementedError()
    
    @overload
    def save_to(self, destination_path : str, destination_driver : aspose.gis.FileDriver, options : aspose.gis.SavingOptions) -> None:
        '''Saves features sequence to layer.
        
        :param destination_path: Path to the output layer.
        :param destination_driver: The format driver for the output layer.
        :param options: Options for the saving procedure.'''
        raise NotImplementedError()
    
    @overload
    def save_to(self, destination_path : aspose.gis.AbstractPath, destination_driver : aspose.gis.FileDriver, options : aspose.gis.SavingOptions) -> None:
        '''Saves features sequence to layer.
        
        :param destination_path: Path to the output layer.
        :param destination_driver: The format driver for the output layer.
        :param options: Options for the saving procedure.'''
        raise NotImplementedError()
    
    def get_extent(self) -> aspose.gis.Extent:
        '''Gets a spatial extent of this layer.
        
        :returns: A spatial extent of this layer.'''
        raise NotImplementedError()
    
    def where_greater(self, attribute_name : str, value : Any) -> aspose.gis.FeaturesSequence:
        '''Selects features with attribute value greater than the provided value.
        
        :param attribute_name: Attribute to filter by.
        :param value: Value to compare against.
        :returns: Features with attribute value greater than the provided value.'''
        raise NotImplementedError()
    
    def where_greater_or_equal(self, attribute_name : str, value : Any) -> aspose.gis.FeaturesSequence:
        '''Selects features with attribute value greater or equal to the provided value.
        
        :param attribute_name: Attribute to filter by.
        :param value: Value to compare against.
        :returns: Features with attribute value greater or equal to the provided value.'''
        raise NotImplementedError()
    
    def where_smaller(self, attribute_name : str, value : Any) -> aspose.gis.FeaturesSequence:
        '''Selects features with attribute value smaller than the provided value.
        
        :param attribute_name: Attribute to filter by.
        :param value: Value to compare against.
        :returns: Features with attribute value smaller than the provided value.'''
        raise NotImplementedError()
    
    def where_smaller_or_equal(self, attribute_name : str, value : Any) -> aspose.gis.FeaturesSequence:
        '''Selects features with attribute value smaller or equal to the provided value.
        
        :param attribute_name: Attribute to filter by.
        :param value: Value to compare against.
        :returns: Features with attribute value smaller or equal to the provided value.'''
        raise NotImplementedError()
    
    def where_equal(self, attribute_name : str, value : Any) -> aspose.gis.FeaturesSequence:
        '''Selects features with attribute value equal to the provided value.
        
        :param attribute_name: Attribute to filter by.
        :param value: Value to compare against.
        :returns: Features with attribute value equal to the provided value.'''
        raise NotImplementedError()
    
    def where_not_equal(self, attribute_name : str, value : Any) -> aspose.gis.FeaturesSequence:
        '''Selects features with attribute value not equal to the provided value.
        
        :param attribute_name: Attribute to filter by.
        :param value: Value to compare against.
        :returns: Features with attribute value not equal to the provided value.'''
        raise NotImplementedError()
    
    def where_null(self, attribute_name : str) -> aspose.gis.FeaturesSequence:
        '''Selects features with attribute equal to null.
        
        :param attribute_name: Attribute to filter by.
        :returns: Features with attribute value equal to null.'''
        raise NotImplementedError()
    
    def where_not_null(self, attribute_name : str) -> aspose.gis.FeaturesSequence:
        '''Selects features with attribute not equal to null.
        
        :param attribute_name: Attribute to filter by.
        :returns: Features with attribute value not equal to null.'''
        raise NotImplementedError()
    
    def where_set(self, attribute_name : str) -> aspose.gis.FeaturesSequence:
        '''Selects features with attribute set.
        
        :param attribute_name: Attribute to filter by.
        :returns: Features with set attribute value.'''
        raise NotImplementedError()
    
    def where_unset(self, attribute_name : str) -> aspose.gis.FeaturesSequence:
        '''Selects features where specified attribute is not set.
        
        :param attribute_name: Attribute to filter by.
        :returns: Features with unset attribute value.'''
        raise NotImplementedError()
    
    def split_to(self) -> List[aspose.gis.VectorLayer]:
        '''Split features by geometry type.
        
        :returns: Layers with the same type of geometry.'''
        raise NotImplementedError()
    
    @property
    def spatial_reference_system(self) -> aspose.gis.spatialreferencing.SpatialReferenceSystem:
        '''Gets spatial reference system of this features sequence.'''
        raise NotImplementedError()
    
    @property
    def attributes(self) -> aspose.gis.BaseFeatureAttributeCollection:
        '''Gets the collection of custom attributes for features in this :py:class:`aspose.gis.VectorLayer`.'''
        raise NotImplementedError()
    

class FileDriver(Driver):
    '''A driver for a specific file based format.'''
    
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
    def open_layer(self, path : aspose.gis.AbstractPath, options : aspose.gis.DriverOptions) -> aspose.gis.VectorLayer:
        '''Opens the layer for reading.
        
        :param path: Path to the file.
        :param options: Driver-specific options.
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
    def create_layer(self, path : aspose.gis.AbstractPath, options : aspose.gis.DriverOptions, spatial_reference_system : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> aspose.gis.VectorLayer:
        '''Creates the layer and opens it for appending.
        
        :param path: Path to the file.
        :param options: Driver-specific options.
        :param spatial_reference_system: Spatial reference system.
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
    def edit_layer(self, path : aspose.gis.AbstractPath, options : aspose.gis.DriverOptions) -> aspose.gis.VectorLayer:
        '''Opens a layer for editing.
        
        :param path: Path to the file.
        :param options: Driver-specific options.
        :returns: An instance of :py:class:`aspose.gis.VectorLayer`.'''
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
    def open_dataset(self, path : aspose.gis.AbstractPath, options : aspose.gis.DriverOptions) -> aspose.gis.Dataset:
        '''Opens the dataset.
        
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
    
    @overload
    def create_dataset(self, path : aspose.gis.AbstractPath, options : aspose.gis.DriverOptions) -> aspose.gis.Dataset:
        '''Creates a dataset.
        
        :param path: Path to the dataset.
        :param options: Driver-specific options.
        :returns: An instance of :py:class:`aspose.gis.Dataset`.'''
        raise NotImplementedError()
    
    def supports_spatial_reference_system(self, spatial_reference_system : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> bool:
        '''Determines, whether specified spatial reference system is supported by the driver.
        
        :param spatial_reference_system: Spatial reference system.
        :returns: Boolean value, indicating whether specified spatial reference system is supported by the driver.
        is considered supported by any driver.'''
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
    

class GeoConvert:
    '''Converts coordinates to/from the different formats.'''
    
    @overload
    @staticmethod
    def as_point_text(latitude : float, longitude : float, format : aspose.gis.PointFormats) -> str:
        '''Returns the calculated position as a string in the specified format.
        
        :param latitude: Position latitude.
        :param longitude: Position longitude.
        :param format: Format of the result.
        :returns: Position as string.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def as_point_text(point : aspose.gis.geometries.IPoint, format : aspose.gis.PointFormats) -> str:
        '''Returns the calculated position as a string in the specified format.
        
        :param point: IPoint object.
        :param format: Format of the result.
        :returns: Position as string.'''
        raise NotImplementedError()
    
    @staticmethod
    def parse_point_text(text : str) -> aspose.gis.geometries.IPoint:
        '''Converts the string that contains сoordinates to IPoint object.
        
        :param text: A string that contains coordinates to convert.
        The string should contain both coordinate latitude and longitude.
        Coordinates should be separated by whitespace, by comma or by semicolon.
        :returns: IPoint object with coordinates that are equivalent to the input string.'''
        raise NotImplementedError()
    
    @staticmethod
    def try_parse_point_text(text : str, point : List[aspose.gis.geometries.IPoint]) -> bool:
        '''Converts the string that contains сoordinates to IPoint object. A return value indicates whether the conversion succeeded or failed.
        
        :param text: A string that contains coordinates to convert.
        The string should contain both coordinate latitude and longitude.
        Coordinates should be separated by whitespace, by comma or by semicolon.
        :param point: When this method returns, contains the IPoint object with parsed coordinates, if the conversion succeeded, or null if the conversion failed.
        :returns: True if text was parsed successfully, otherwise False.'''
        raise NotImplementedError()
    

class GisException:
    '''The exception that is thrown when an error occurs during GIS data processing.'''
    

class IAttributesConverter:
    '''A custom converter for layer attributes.'''
    
    def modify_attribute(self, attribute : aspose.gis.FeatureAttribute, actions : aspose.gis.AttributesConverterActions) -> None:
        '''Adjusts a :py:class:`aspose.gis.FeatureAttribute` as necessary for the target layer.
        
        :param attribute: A copy of an attribute of the source layer.
        :param actions: Specifies optional actions with attributes of the destination layer.
        For example, allows us to exclude our attribute.'''
        raise NotImplementedError()
    

class IFeatureStyle:
    '''The interface root class of the feature styles hierarchy.'''
    

class License:
    '''Provides methods to license the component.'''
    
    @overload
    def set_license(self, license_name : str) -> None:
        '''Licenses the component.'''
        raise NotImplementedError()
    
    @overload
    def set_license(self, stream : io.RawIOBase) -> None:
        '''Licenses the component.
        
        :param stream: A stream that contains the license.'''
        raise NotImplementedError()
    

class Metered:
    '''Provides methods to set metered key.'''
    
    @staticmethod
    def set_metered_key(public_key : str, private_key : str) -> None:
        '''Sets metered public and private key
        
        :param public_key: public key
        :param private_key: private key'''
        raise NotImplementedError()
    
    @staticmethod
    def get_consumption_quantity() -> float:
        '''Gets consumption file size
        
        :returns: consumption quantity'''
        raise NotImplementedError()
    
    @staticmethod
    def reset_metered_key() -> None:
        '''Removes previously setup license'''
        raise NotImplementedError()
    
    @staticmethod
    def get_consumption_credit() -> float:
        '''Gets consumption credit
        
        :returns: consumption quantity'''
        raise NotImplementedError()
    

class MultiStreamPath(AbstractPath):
    '''This class works with formats which contains several files.'''
    
    @staticmethod
    def from_local_path(path : str) -> aspose.gis.AbstractPath:
        '''Creates an :py:class:`aspose.gis.AbstractPath` that represents a location on the local filesystem.
        
        :param path: A path on the local filesystem, like ``"C:\\file.shp"`` or ``"D:\\directory\\"``.
        :returns: An :py:class:`aspose.gis.AbstractPath` that represents the location defined by the ``path``.'''
        raise NotImplementedError()
    
    @staticmethod
    def from_stream(stream : io.RawIOBase) -> aspose.gis.AbstractPath:
        '''Creates an :py:class:`aspose.gis.AbstractPath` from a :py:class:`io.RawIOBase`.
        
        :param stream: A stream to create an :py:class:`aspose.gis.AbstractPath` from. ``Aspose.GIS`` does not dispose the stream.
        :returns: An instance of :py:class:`aspose.gis.AbstractPath` with the specified :py:class:`io.RawIOBase` as its content.'''
        raise NotImplementedError()
    
    def is_file(self) -> bool:
        '''Gets a value indicating whether this path points to an existing file that can be opened for reading.
        
        :returns: if location points to a file;  otherwise.'''
        raise NotImplementedError()
    
    def delete(self) -> None:
        '''Deletes a file pointed to by this path.'''
        raise NotImplementedError()
    
    def open(self, access : System.IO.FileAccess) -> io.RawIOBase:
        '''Abstracts a set of open streaming multi-file formats a path for accessing data.
        
        :param access: Specifies a subset of operations that can be performed on a :py:class:`io.RawIOBase`.
        :returns: This can be either a  :py:class:`System.IO.MemoryStream` or the stream originally passed by the client.'''
        raise NotImplementedError()
    
    def list_directory(self) -> Iterable[aspose.gis.AbstractPath]:
        '''Returns paths located inside this ``AbstractPath``, if it\'s a directory.
        
        :returns: Paths located inside this ``AbstractPath``.'''
        raise NotImplementedError()
    
    def combine(self, location : str) -> aspose.gis.AbstractPath:
        '''Combines this :py:class:`aspose.gis.AbstractPath` with specified path components.
        
        :param location: A path component to append to this :py:class:`aspose.gis.AbstractPath`.
        :returns: A new :py:class:`aspose.gis.AbstractPath` pointing to a :py:attr:`aspose.gis.AbstractPath.location` that is a combination of locations of this :py:class:`aspose.gis.AbstractPath` and
        the argument.'''
        raise NotImplementedError()
    
    def with_extension(self, new_extension : str) -> aspose.gis.AbstractPath:
        '''Returns a new :py:class:`aspose.gis.AbstractPath` with the file extension changed to the specified value.
        
        :param new_extension: A new extension.
        :returns: A new :py:class:`aspose.gis.AbstractPath`, that points to a file in the same directory, but with a new extension.'''
        raise NotImplementedError()
    
    def get_file_name(self) -> str:
        '''Returns the file name and extension of this :py:class:`aspose.gis.AbstractPath`.
        
        :returns: The characters after the last :py:attr:`aspose.gis.AbstractPath.separator` character in the :py:attr:`aspose.gis.AbstractPath.location`. If the
        last character is the :py:attr:`aspose.gis.AbstractPath.separator` character, an empty string is returned. If there is no
        :py:attr:`aspose.gis.AbstractPath.separator` characters in the :py:attr:`aspose.gis.AbstractPath.location`, the :py:attr:`aspose.gis.AbstractPath.location` itself
        is returned.'''
        raise NotImplementedError()
    
    def get_file_name_without_extension(self) -> str:
        '''Returns the file name of this :py:class:`aspose.gis.AbstractPath` without the extension.
        
        :returns: The string returned by :py:func:`aspose.gis.AbstractPath.get_file_name` minus the last period and all characters following it.'''
        raise NotImplementedError()
    
    def get_extension(self) -> str:
        '''Returns the extension of this :py:class:`aspose.gis.AbstractPath`.
        
        :returns: The extension of this :py:class:`aspose.gis.AbstractPath` (including the period ".") or
        an empty string if the :py:class:`aspose.gis.AbstractPath` has no extension.'''
        raise NotImplementedError()
    
    @property
    def location(self) -> str:
        '''Gets a string representation of the location of this ``AbstractPath``.'''
        raise NotImplementedError()
    
    @property
    def separator(self) -> str:
        '''Gets a separator character used to separate directory levels of the :py:attr:`aspose.gis.MultiStreamPath.location` string.'''
        raise NotImplementedError()
    

class NodeLink:
    '''Node-based link to the parts of resources'''
    
    def get_node_by_name(self, name : str) -> aspose.gis.NodeLink:
        '''Gets the node by name. Please note, this method will return the first found Node.
        Doesn\'t matter in what level it will be found
        
        :param name: The name of the node you want to find.
        :returns: The found node with NodeLink API'''
        raise NotImplementedError()
    
    def get_nodes_by_name(self, names : List[str]) -> List[aspose.gis.NodeLink]:
        '''Gets the all nodes with the specified name.
        Doesn\'t matter in what level it will be found
        
        :param names: The names.
        :returns: The array of found nodes.'''
        raise NotImplementedError()
    
    def as_double(self) -> float:
        '''Returns value casted to the double.
        
        :returns: The double value of node'''
        raise NotImplementedError()
    
    def as_int(self) -> int:
        '''Returns value casted to the int.
        
        :returns: The int value of node'''
        raise NotImplementedError()
    
    def as_bool(self) -> bool:
        '''Returns value casted to the bool
        
        :returns: The bool value of node'''
        raise NotImplementedError()
    
    def get_node_content(self) -> str:
        '''Gets the content of the node.
        
        :returns: The content of node'''
        raise NotImplementedError()
    
    def find_nodes_by_name(self, name : str) -> List[aspose.gis.NodeLink]:
        '''Finds the nodes by the name
        
        :param name: The name of the node
        :returns: Array of Nodes of format by name'''
        raise NotImplementedError()
    
    def add_child(self, child : aspose.gis.NodeLink) -> None:
        '''Adds the child.
        
        :param child: The child.'''
        raise NotImplementedError()
    
    @property
    def node_name(self) -> str:
        '''Gets the name.'''
        raise NotImplementedError()
    
    @node_name.setter
    def node_name(self, value : str) -> None:
        '''Sets the name.'''
        raise NotImplementedError()
    
    @property
    def node_value(self) -> str:
        '''Gets the value.'''
        raise NotImplementedError()
    
    @node_value.setter
    def node_value(self, value : str) -> None:
        '''Sets the value.'''
        raise NotImplementedError()
    
    @property
    def children(self) -> List[aspose.gis.NodeLink]:
        '''Gets the children.'''
        raise NotImplementedError()
    

class NumericFormat:
    ''':py:class:`aspose.gis.NumericFormat` are used to format common numeric types in text.'''
    
    @staticmethod
    def general(precision : int) -> aspose.gis.NumericFormat:
        '''Converts a number to the more compact of either fixed-point or scientific notation,
        depending on the type of the number and whether a precision specifier is present. Recommended to use.
        
        :param precision: The precision defines the maximum number of significant digits that can appear in the result string.
        If the precision is zero, the value "15" is used. The maximum available precision is "17".
        :returns: The General Format Specifier.'''
        raise NotImplementedError()
    
    @staticmethod
    def flat(significant_digits : int) -> aspose.gis.NumericFormat:
        '''Converts a number to a fixed-point text without a scientific notation.
        
        :param significant_digits: Number of significant digits. The maximum available precision is "308"
        :returns: The Rounding Precision Specifier.'''
        raise NotImplementedError()
    
    round_trip : aspose.gis.NumericFormat
    '''Converts and attempts to ensure that a numeric value that is converted to
    a string is parsed back into the same numeric value.'''

class PrecisionModel:
    ''':py:class:`aspose.gis.PrecisionModel` specifies a number of significant digits in a coordinate.'''
    
    @staticmethod
    def rounding(significant_digits : int) -> aspose.gis.PrecisionModel:
        '''Returns a rounding precision model.
        According to rounding precision model only a limited number of digits are significant.
        
        :param significant_digits: Number of significant digits.
        :returns: Rounding Precision model.'''
        raise NotImplementedError()
    
    def equals(self, other : aspose.gis.PrecisionModel) -> bool:
        '''Indicates whether the current object is equal to another object of the same type.
        
        :param other: An object to compare with this object.
        :returns: true if the current object is equal to the ``other`` parameter; otherwise, false.'''
        raise NotImplementedError()
    
    exact : aspose.gis.PrecisionModel
    '''Returns an exact precision model.
    According to exact precision model all digits in a double value are significant.'''
    @property
    def is_exact(self) -> bool:
        '''Gets a value indicating whether this precision model is exact.'''
        raise NotImplementedError()
    
    @property
    def is_rounding(self) -> bool:
        '''Gets a value indicating whether this precision model is rounding.'''
        raise NotImplementedError()
    
    @property
    def significant_digits(self) -> int:
        '''Gets a number of significant digits in a precision model if it is rounding.'''
        raise NotImplementedError()
    

class RasterDriver(Driver):
    '''A driver for a specific raster based format.'''
    
    @overload
    def open_layer(self, path : aspose.gis.AbstractPath, options : aspose.gis.RasterDriverOptions) -> aspose.gis.raster.RasterLayer:
        '''Opens the layer for reading.
        
        :param path: Path to the file.
        :param options: Driver-specific options.
        :returns: An instance of :py:class:`aspose.gis.raster.RasterLayer`.'''
        raise NotImplementedError()
    
    @overload
    def open_layer(self, path : str) -> aspose.gis.raster.RasterLayer:
        '''Opens the layer for reading.
        
        :param path: Path to the file.
        :returns: An instance of :py:class:`aspose.gis.raster.RasterLayer`.'''
        raise NotImplementedError()
    
    @overload
    def open_layer(self, path : aspose.gis.AbstractPath) -> aspose.gis.raster.RasterLayer:
        '''Opens the layer for reading.
        
        :param path: Path to the file.
        :returns: An instance of :py:class:`aspose.gis.raster.RasterLayer`.'''
        raise NotImplementedError()
    
    @overload
    def open_layer(self, path : str, options : aspose.gis.RasterDriverOptions) -> aspose.gis.raster.RasterLayer:
        '''Opens the layer for reading.
        
        :param path: Path to the file.
        :param options: Driver-specific options.
        :returns: An instance of :py:class:`aspose.gis.raster.RasterLayer`.'''
        raise NotImplementedError()
    
    @property
    def can_open_layers(self) -> bool:
        '''Gets a value indicating whether this driver can open raster layers.'''
        raise NotImplementedError()
    

class RasterDriverOptions(DriverOptions):
    '''Options for a :py:class:`aspose.gis.RasterDriver`.'''
    
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
    

class SavingOptions:
    '''Options for saving :py:class:`aspose.gis.FeaturesSequence` to file.'''
    
    @property
    def driver_options(self) -> aspose.gis.DriverOptions:
        '''Driver-specific options for the output layer.'''
        raise NotImplementedError()
    
    @driver_options.setter
    def driver_options(self, value : aspose.gis.DriverOptions) -> None:
        '''Driver-specific options for the output layer.'''
        raise NotImplementedError()
    
    @property
    def spatial_reference_system(self) -> aspose.gis.spatialreferencing.SpatialReferenceSystem:
        '''Driver-specific options for the output layer.'''
        raise NotImplementedError()
    
    @spatial_reference_system.setter
    def spatial_reference_system(self, value : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> None:
        '''Driver-specific options for the output layer.'''
        raise NotImplementedError()
    
    @property
    def attributes_converter(self) -> aspose.gis.IAttributesConverter:
        '''A custom converter for attributes.
        If not , it is called for each attribute of the source layer and is expected to change it if necessary.'''
        raise NotImplementedError()
    
    @attributes_converter.setter
    def attributes_converter(self, value : aspose.gis.IAttributesConverter) -> None:
        '''A custom converter for attributes.
        If not , it is called for each attribute of the source layer and is expected to change it if necessary.'''
        raise NotImplementedError()
    

class VectorLayer(FeaturesSequence):
    '''Represents a vector layer.
    A vector layer is a collection of geographic features, stored in a file.'''
    
    @overload
    def where_intersects(self, sequence : aspose.gis.FeaturesSequence) -> aspose.gis.FeaturesSequence:
        '''Filters features based on the union of all geometries in other features sequence.
        
        :param sequence: Other features sequence.
        :returns: Features that intersect with the union of all geometries in other features sequence.'''
        raise NotImplementedError()
    
    @overload
    def where_intersects(self, geometry : aspose.gis.geometries.IGeometry) -> aspose.gis.FeaturesSequence:
        '''Filters features based on the provided geometry.
        
        :param geometry: Filter geometry.
        :returns: Features that intersect with the provided geometry.'''
        raise NotImplementedError()
    
    @overload
    def where_intersects(self, extent : aspose.gis.Extent) -> aspose.gis.FeaturesSequence:
        '''Filters features based on the extent.
        
        :param extent: Filter extent.
        :returns: Features that intersect with the provided geometry.'''
        raise NotImplementedError()
    
    @overload
    def save_to(self, destination_path : str, destination_driver : aspose.gis.FileDriver) -> None:
        '''Saves features sequence to layer.
        
        :param destination_path: Path to the output layer.
        :param destination_driver: The format driver for the output layer.'''
        raise NotImplementedError()
    
    @overload
    def save_to(self, destination_path : aspose.gis.AbstractPath, destination_driver : aspose.gis.FileDriver) -> None:
        '''Saves features sequence to layer.
        
        :param destination_path: Path to the output layer.
        :param destination_driver: The format driver for the output layer.'''
        raise NotImplementedError()
    
    @overload
    def save_to(self, destination_path : str, destination_driver : aspose.gis.FileDriver, options : aspose.gis.SavingOptions) -> None:
        '''Saves features sequence to layer.
        
        :param destination_path: Path to the output layer.
        :param destination_driver: The format driver for the output layer.
        :param options: Options for the saving procedure.'''
        raise NotImplementedError()
    
    @overload
    def save_to(self, destination_path : aspose.gis.AbstractPath, destination_driver : aspose.gis.FileDriver, options : aspose.gis.SavingOptions) -> None:
        '''Saves features sequence to layer.
        
        :param destination_path: Path to the output layer.
        :param destination_driver: The format driver for the output layer.
        :param options: Options for the saving procedure.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def open(path : str, driver : aspose.gis.FileDriver) -> aspose.gis.VectorLayer:
        '''Open the layer for reading.
        
        :param path: Path to the file.
        :param driver: Driver to use.
        :returns: A read-only layer.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def open(path : aspose.gis.AbstractPath, driver : aspose.gis.FileDriver) -> aspose.gis.VectorLayer:
        '''Open the layer for reading.
        
        :param path: Path to the file.
        :param driver: Driver to use.
        :returns: A read-only layer.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def open(path : str, driver : aspose.gis.FileDriver, options : aspose.gis.DriverOptions) -> aspose.gis.VectorLayer:
        '''Open the layer for reading.
        
        :param path: Path to the file.
        :param driver: Driver to use.
        :param options: Driver-specific options.
        :returns: A read-only layer.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def open(path : aspose.gis.AbstractPath, driver : aspose.gis.FileDriver, options : aspose.gis.DriverOptions) -> aspose.gis.VectorLayer:
        '''Open the layer for reading.
        
        :param path: Path to the file.
        :param driver: Driver to use.
        :param options: Driver-specific options.
        :returns: A read-only layer.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def create(path : str, driver : aspose.gis.FileDriver) -> aspose.gis.VectorLayer:
        '''Creates the layer and opens it for adding new features.
        
        :param path: Path to the file.
        :param driver: Driver to use.
        :returns: A write-only layer.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def create(path : str, driver : aspose.gis.FileDriver, options : aspose.gis.DriverOptions) -> aspose.gis.VectorLayer:
        '''Creates the layer and opens it for adding new features.
        
        :param path: Path to the file.
        :param driver: Driver to use.
        :param options: Driver-specific options.
        :returns: A write-only layer.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def create(path : aspose.gis.AbstractPath, driver : aspose.gis.FileDriver) -> aspose.gis.VectorLayer:
        '''Creates the layer and opens it for adding new features.
        
        :param path: Path to the file.
        :param driver: Driver to use.
        :returns: A write-only layer.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def create(path : aspose.gis.AbstractPath, driver : aspose.gis.FileDriver, options : aspose.gis.DriverOptions) -> aspose.gis.VectorLayer:
        '''Creates the layer and opens it for adding new features.
        
        :param path: Path to the file.
        :param driver: Driver to use.
        :param options: Driver-specific options.
        :returns: A write-only layer.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def create(path : str, driver : aspose.gis.FileDriver, spatial_reference_system : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> aspose.gis.VectorLayer:
        '''Creates the layer and opens it for appending.
        
        :param path: Path to the file.
        :param driver: Driver to use.
        :param spatial_reference_system: Spatial reference system.
        :returns: An instance of :py:class:`aspose.gis.VectorLayer`.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def create(path : aspose.gis.AbstractPath, driver : aspose.gis.FileDriver, spatial_reference_system : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> aspose.gis.VectorLayer:
        '''Creates the layer and opens it for appending.
        
        :param path: Path to the file.
        :param driver: Driver to use.
        :param spatial_reference_system: Spatial reference system.
        :returns: An instance of :py:class:`aspose.gis.VectorLayer`.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def create(path : str, driver : aspose.gis.FileDriver, options : aspose.gis.DriverOptions, spatial_reference_system : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> aspose.gis.VectorLayer:
        '''Creates the layer and opens it for appending.
        
        :param path: Path to the file.
        :param driver: Driver to use.
        :param options: Driver-specific options.
        :param spatial_reference_system: Spatial reference system.
        :returns: An instance of :py:class:`aspose.gis.VectorLayer`.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def create(path : aspose.gis.AbstractPath, driver : aspose.gis.FileDriver, options : aspose.gis.DriverOptions, spatial_reference_system : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> aspose.gis.VectorLayer:
        '''Creates the layer and opens it for appending.
        
        :param path: Path to the file.
        :param driver: Driver to use.
        :param options: Driver-specific options.
        :param spatial_reference_system: Spatial reference system.
        :returns: An instance of :py:class:`aspose.gis.VectorLayer`.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def convert(source_path : str, source_driver : aspose.gis.FileDriver, destination_path : str, destination_driver : aspose.gis.FileDriver) -> None:
        '''Convert a layer to a different format.
        
        :param source_path: Path to the layer that will be converted.
        :param source_driver: The format driver for the source layer.
        :param destination_path: Path to the layer that will created as a result of conversion.
        :param destination_driver: The format driver for the destination layer.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def convert(source_path : aspose.gis.AbstractPath, source_driver : aspose.gis.FileDriver, destination_path : aspose.gis.AbstractPath, destination_driver : aspose.gis.FileDriver) -> None:
        '''Convert a layer to a different format.
        
        :param source_path: Path to the layer that will be converted.
        :param source_driver: The format driver for the source layer.
        :param destination_path: Path to the layer that will created as a result of conversion.
        :param destination_driver: The format driver for the destination layer.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def convert(source_path : str, source_driver : aspose.gis.FileDriver, destination_path : str, destination_driver : aspose.gis.FileDriver, options : aspose.gis.ConversionOptions) -> None:
        '''Convert a layer to a different format.
        
        :param source_path: Path to the layer that will be converted.
        :param source_driver: The format driver for the source layer.
        :param destination_path: Path to the layer that will created as a result of conversion.
        :param destination_driver: The format driver for the destination layer.
        :param options: Options for the conversion procedure.'''
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def convert(source_path : aspose.gis.AbstractPath, source_driver : aspose.gis.FileDriver, destination_path : aspose.gis.AbstractPath, destination_driver : aspose.gis.FileDriver, options : aspose.gis.ConversionOptions) -> None:
        '''Convert a layer to a different format.
        
        :param source_path: Path to the layer that will be converted.
        :param source_driver: The format driver for the source layer.
        :param destination_path: Path to the layer that will created as a result of conversion.
        :param destination_driver: The format driver for the destination layer.
        :param options: Options for the conversion procedure.'''
        raise NotImplementedError()
    
    @overload
    def copy_attributes(self, features_sequence : aspose.gis.FeaturesSequence) -> None:
        '''Copies attributes of other :py:class:`aspose.gis.VectorLayer` to this one.
        
        :param features_sequence: The features sequence to copy attributes from.'''
        raise NotImplementedError()
    
    @overload
    def copy_attributes(self, features_sequence : aspose.gis.FeaturesSequence, converter : aspose.gis.IAttributesConverter) -> None:
        '''Copies attributes of other :py:class:`aspose.gis.VectorLayer` to this one.
        
        :param features_sequence: The features sequence to copy attributes from.
        :param converter: An instance of custom :py:class:`aspose.gis.IAttributesConverter` that will process the attributes one by one.'''
        raise NotImplementedError()
    
    @overload
    def add(self, feature : aspose.gis.Feature) -> None:
        '''Adds a new feature to the layer, if supported by the :py:class:`aspose.gis.VectorLayer`\'s :py:attr:`aspose.gis.VectorLayer.driver`.
        
        :param feature: The feature to add.'''
        raise NotImplementedError()
    
    @overload
    def add(self, feature : aspose.gis.Feature, style : aspose.gis.IFeatureStyle) -> None:
        '''Adds a new feature with the specified style to the layer, if supported by the :py:class:`aspose.gis.VectorLayer`\'s :py:attr:`aspose.gis.VectorLayer.driver`.
        
        :param feature: The feature to add.
        :param style: The feature style. Use  to indicate missing style.'''
        raise NotImplementedError()
    
    @overload
    def nearest_to(self, x : float, y : float) -> aspose.gis.Feature:
        '''Gets the nearest feature to the provided coordinate.
        
        :param x: X of the coordinate.
        :param y: Y of the coordinate.
        :returns: The nearest feature to the provided coordinate.'''
        raise NotImplementedError()
    
    @overload
    def nearest_to(self, point : aspose.gis.geometries.IPoint) -> aspose.gis.Feature:
        '''Gets the nearest feature to the provided point.
        
        :param point: The point.
        :returns: The nearest feature to the provided point.'''
        raise NotImplementedError()
    
    @overload
    def use_attributes_index(self, index_path : str, attribute_name : str, force_rebuild : bool) -> None:
        '''Loads attribute index to speed up filtering by attributes value in filter methods like :py:func:`aspose.gis.FeaturesSequence.WhereGreater``1`.
        If index does not exist creates it first. Use ``forceRebuild`` to force index recreation.
        
        :param index_path: Path to the index file.
        :param attribute_name: Name of the attribute to build index on.
        :param force_rebuild: Whether to recreate index even if it already exists.'''
        raise NotImplementedError()
    
    @overload
    def use_attributes_index(self, index_path : aspose.gis.AbstractPath, attribute_name : str, force_rebuild : bool) -> None:
        '''Loads attribute index to speed up filtering by attributes value in filter methods like :py:func:`aspose.gis.FeaturesSequence.WhereGreater``1`.
        If index does not exist creates it first. Use ``forceRebuild`` to force index recreation.
        
        :param index_path: Path to the index file.
        :param attribute_name: Name of the attribute to build index on.
        :param force_rebuild: Whether to recreate index even if it already exists.'''
        raise NotImplementedError()
    
    @overload
    def use_spatial_index(self, index_path : str, force_rebuild : bool) -> None:
        '''Loads spatial index to speed up filtering by attributes value in filter methods like :py:func:`aspose.gis.FeaturesSequence.where_intersects`
        and :py:func:`aspose.gis.VectorLayer.nearest_to`.
        If index does not exist creates it first. Use ``forceRebuild`` to force index recreation.
        
        :param index_path: Path to the index file.
        :param force_rebuild: Whether to recreate index even if it already exists.'''
        raise NotImplementedError()
    
    @overload
    def use_spatial_index(self, index_path : aspose.gis.AbstractPath, force_rebuild : bool) -> None:
        '''Loads spatial index to speed up filtering by attributes value in filter methods like :py:func:`aspose.gis.FeaturesSequence.where_intersects`
        and :py:func:`aspose.gis.VectorLayer.nearest_to`.
        If index does not exist creates it first. Use ``forceRebuild`` to force index recreation.
        
        :param index_path: Path to the index file.
        :param force_rebuild: Whether to recreate index even if it already exists.'''
        raise NotImplementedError()
    
    def get_extent(self) -> aspose.gis.Extent:
        '''Gets a spatial extent of this layer.
        
        :returns: A spatial extent of this layer.'''
        raise NotImplementedError()
    
    def where_greater(self, attribute_name : str, value : Any) -> aspose.gis.FeaturesSequence:
        '''Selects features with attribute value greater than the provided value.
        
        :param attribute_name: Attribute to filter by.
        :param value: Value to compare against.
        :returns: Features with attribute value greater than the provided value.'''
        raise NotImplementedError()
    
    def where_greater_or_equal(self, attribute_name : str, value : Any) -> aspose.gis.FeaturesSequence:
        '''Selects features with attribute value greater or equal to the provided value.
        
        :param attribute_name: Attribute to filter by.
        :param value: Value to compare against.
        :returns: Features with attribute value greater or equal to the provided value.'''
        raise NotImplementedError()
    
    def where_smaller(self, attribute_name : str, value : Any) -> aspose.gis.FeaturesSequence:
        '''Selects features with attribute value smaller than the provided value.
        
        :param attribute_name: Attribute to filter by.
        :param value: Value to compare against.
        :returns: Features with attribute value smaller than the provided value.'''
        raise NotImplementedError()
    
    def where_smaller_or_equal(self, attribute_name : str, value : Any) -> aspose.gis.FeaturesSequence:
        '''Selects features with attribute value smaller or equal to the provided value.
        
        :param attribute_name: Attribute to filter by.
        :param value: Value to compare against.
        :returns: Features with attribute value smaller or equal to the provided value.'''
        raise NotImplementedError()
    
    def where_equal(self, attribute_name : str, value : Any) -> aspose.gis.FeaturesSequence:
        '''Selects features with attribute value equal to the provided value.
        
        :param attribute_name: Attribute to filter by.
        :param value: Value to compare against.
        :returns: Features with attribute value equal to the provided value.'''
        raise NotImplementedError()
    
    def where_not_equal(self, attribute_name : str, value : Any) -> aspose.gis.FeaturesSequence:
        '''Selects features with attribute value not equal to the provided value.
        
        :param attribute_name: Attribute to filter by.
        :param value: Value to compare against.
        :returns: Features with attribute value not equal to the provided value.'''
        raise NotImplementedError()
    
    def where_null(self, attribute_name : str) -> aspose.gis.FeaturesSequence:
        '''Selects features with attribute equal to null.
        
        :param attribute_name: Attribute to filter by.
        :returns: Features with attribute value equal to null.'''
        raise NotImplementedError()
    
    def where_not_null(self, attribute_name : str) -> aspose.gis.FeaturesSequence:
        '''Selects features with attribute not equal to null.
        
        :param attribute_name: Attribute to filter by.
        :returns: Features with attribute value not equal to null.'''
        raise NotImplementedError()
    
    def where_set(self, attribute_name : str) -> aspose.gis.FeaturesSequence:
        '''Selects features with attribute set.
        
        :param attribute_name: Attribute to filter by.
        :returns: Features with set attribute value.'''
        raise NotImplementedError()
    
    def where_unset(self, attribute_name : str) -> aspose.gis.FeaturesSequence:
        '''Selects features where specified attribute is not set.
        
        :param attribute_name: Attribute to filter by.
        :returns: Features with unset attribute value.'''
        raise NotImplementedError()
    
    def split_to(self) -> List[aspose.gis.VectorLayer]:
        '''Split features by geometry type.
        
        :returns: Layers with the same type of geometry.'''
        raise NotImplementedError()
    
    def construct_feature(self) -> aspose.gis.Feature:
        '''Creates (but does not add to the layer) a new feature with attributes matching the collection of attributes of this layer.
        When done with setting data for the feature, use :py:func:`aspose.gis.VectorLayer.add` to add the feature to the layer.
        
        :returns: A new feature.'''
        raise NotImplementedError()
    
    def remove_at(self, index : int) -> None:
        '''Remove the :py:class:`aspose.gis.Feature` at the specified index.
        
        :param index: The index of the feature.'''
        raise NotImplementedError()
    
    def replace_at(self, index : int, feature : aspose.gis.Feature) -> None:
        '''Replace the :py:class:`aspose.gis.Feature` at the specified index.
        
        :param index: The index of the feature.
        :param feature: The feature to set.'''
        raise NotImplementedError()
    
    def join(self, layer : aspose.gis.VectorLayer, options : aspose.gis.relationship.joins.JoinOptions) -> aspose.gis.VectorLayer:
        '''Joins a layer to the current layer.
        
        :param layer: A layer to join.
        :param options: Join parameters.
        :returns: A new layer as a result of join two layers.'''
        raise NotImplementedError()
    
    def join_by_geometry(self, layer : aspose.gis.VectorLayer, options : aspose.gis.relationship.joins.JoinByGeometryOptions) -> aspose.gis.VectorLayer:
        '''Joins a layer to the current layer by geometry.
        
        :param layer: A layer to join.
        :param options: Join parameters.
        :returns: A new layer as a result of join two layers.'''
        raise NotImplementedError()
    
    def as_in_memory(self) -> aspose.gis.VectorLayer:
        '''Create a layer clon as the InMemory format.
        
        :returns: The InMemory Layer.'''
        raise NotImplementedError()
    
    @property
    def spatial_reference_system(self) -> aspose.gis.spatialreferencing.SpatialReferenceSystem:
        '''Gets spatial reference system of this features sequence.'''
        raise NotImplementedError()
    
    @property
    def attributes(self) -> aspose.gis.BaseFeatureAttributeCollection:
        '''Gets the collection of custom attributes for features in this :py:class:`aspose.gis.VectorLayer`.'''
        raise NotImplementedError()
    
    @property
    def count(self) -> int:
        '''Gets the number of features in this layer.'''
        raise NotImplementedError()
    
    @property
    def geometry_type(self) -> aspose.gis.geometries.GeometryType:
        '''Gets the type of the geometry for the layer.'''
        raise NotImplementedError()
    
    @property
    def driver(self) -> aspose.gis.Driver:
        '''Gets the :py:attr:`aspose.gis.VectorLayer.driver` that instantiated this layer.'''
        raise NotImplementedError()
    
    def __getitem__(self, key : int) -> aspose.gis.Feature:
        '''Gets the :py:class:`aspose.gis.Feature` at the specified index.'''
        raise NotImplementedError()
    

class XmlNodeLink(NodeLink):
    '''XML Node-Based links to parts of sources'''
    
    def get_node_by_name(self, name : str) -> aspose.gis.NodeLink:
        '''Gets the node by name. Please note, this method will return the first found Node.
        Doesn\'t matter in what level it will be found
        
        :param name: The name of the node you want to find.
        :returns: The found node with NodeLink API'''
        raise NotImplementedError()
    
    def get_nodes_by_name(self, names : List[str]) -> List[aspose.gis.NodeLink]:
        '''Gets the all nodes with the specified name.
        Doesn\'t matter in what level it will be found
        
        :param names: The names.
        :returns: The array of found nodes.'''
        raise NotImplementedError()
    
    def as_double(self) -> float:
        '''Returns value casted to the double.
        
        :returns: The double value of node'''
        raise NotImplementedError()
    
    def as_int(self) -> int:
        '''Returns value casted to the int.
        
        :returns: The int value of node'''
        raise NotImplementedError()
    
    def as_bool(self) -> bool:
        '''Returns value casted to the bool
        
        :returns: The bool value of node'''
        raise NotImplementedError()
    
    def get_node_content(self) -> str:
        '''Gets the content of the node.
        
        :returns: The content of node'''
        raise NotImplementedError()
    
    def find_nodes_by_name(self, name : str) -> List[aspose.gis.NodeLink]:
        '''Finds the XML nodes by the name
        
        :param name: The name of the node
        :returns: Array of XML Nodes by name'''
        raise NotImplementedError()
    
    def add_child(self, child : aspose.gis.NodeLink) -> None:
        '''Adds the child.
        
        :param child: The child.'''
        raise NotImplementedError()
    
    @property
    def node_name(self) -> str:
        '''Gets the name.'''
        raise NotImplementedError()
    
    @node_name.setter
    def node_name(self, value : str) -> None:
        '''Sets the name.'''
        raise NotImplementedError()
    
    @property
    def node_value(self) -> str:
        '''Gets the value.'''
        raise NotImplementedError()
    
    @node_value.setter
    def node_value(self, value : str) -> None:
        '''Sets the value.'''
        raise NotImplementedError()
    
    @property
    def children(self) -> List[aspose.gis.NodeLink]:
        '''Gets the children.'''
        raise NotImplementedError()
    
    @property
    def name_without_prefix(self) -> str:
        '''Gets the name without prefix.'''
        raise NotImplementedError()
    
    @property
    def prefix(self) -> str:
        '''Gets the prefix.'''
        raise NotImplementedError()
    

class AttributeDataType:
    '''The data type of a feature attribute.'''
    
    INTEGER : AttributeDataType
    '''32-bit integer.'''
    LONG : AttributeDataType
    '''64-bit integer.'''
    GUID : AttributeDataType
    '''A globally unique identifier (GUID).'''
    BOOLEAN : AttributeDataType
    '''Boolean (true/false) value.'''
    DOUBLE : AttributeDataType
    '''Double-precision real number.'''
    DATE : AttributeDataType
    '''Date value.'''
    TIME : AttributeDataType
    '''Time value.'''
    DATE_TIME : AttributeDataType
    '''Date and time value.'''
    STRING : AttributeDataType
    '''String value.'''

class AutoIds:
    '''Auto-generate ids.'''
    
    NONE : AutoIds
    '''Hide Auto Ids.'''
    NUMBER : AutoIds
    '''Increment Number Ids.'''
    GUID : AutoIds
    '''Generate Guid Ids.'''

class PointFormats:
    ''':py:class:`aspose.gis.PointFormats` are used to convert coordinates in text.'''
    
    DECIMAL_DEGREES : PointFormats
    '''Decimal Degrees (DD) format.'''
    DEGREE_MINUTES_SECONDS : PointFormats
    '''Degree Minutes Seconds (DMS) format.'''
    DEGREE_DECIMAL_MINUTES : PointFormats
    '''Degree Decimal Minutes (DDM) format.'''
    GEO_REF : PointFormats
    '''World Geographic Reference System.'''
    MGRS : PointFormats
    '''Military Grid Reference System with WGS 84 datum.'''
    USNG : PointFormats
    '''United States National Grid with WGS 84 datum.'''
    GARS : PointFormats
    '''Global Area Reference System'''
    PLUS_CODE : PointFormats
    '''The Open Location Code (OLC) or Plus Code'''
    MAIDENHEAD : PointFormats
    '''The Maidenhead Locator System (a.k.a. QTH Locator and IARU Locator)'''
    UTM : PointFormats
    '''Universal Transverse Mercator'''
    UPS : PointFormats
    '''Universal polar stereographic coordinate system'''

class SpatialReferenceSystemMode:
    '''Specifies a mode of Spatial Reference System (SRS) writing in database
    if it\'s an unknown SRS.'''
    
    THROW_EXCEPTION : SpatialReferenceSystemMode
    '''Throw exceptions if it\'s an unknown SRS for the database.'''
    WRITE_IN_SYSTEM_TABLE : SpatialReferenceSystemMode
    '''Write SRS info in system table if it\'s an unknown SRS for the database.'''
    SETUP_TO_ZERO : SpatialReferenceSystemMode
    '''Setup the SRID of a geometry to \'zero\' if it\'s an unknown SRS for the database.'''

