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

class KmlDriver(aspose.gis.FileDriver):
    '''A driver for the KML format'''
    
    @overload
    def open_layer(self, path : str, options : aspose.gis.formats.kml.KmlOptions) -> aspose.gis.VectorLayer:
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
    def open_layer(self, path : aspose.gis.AbstractPath, options : aspose.gis.formats.kml.KmlOptions) -> aspose.gis.VectorLayer:
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
    def create_layer(self, path : str, options : aspose.gis.formats.kml.KmlOptions) -> aspose.gis.VectorLayer:
        '''Creates a layer and opens it for adding new features.
        
        :param path: Path to the file.
        :param options: Driver-specific options.
        :returns: An instance of :py:class:`aspose.gis.VectorLayer`.'''
        raise NotImplementedError()
    
    @overload
    def create_layer(self, path : aspose.gis.AbstractPath, options : aspose.gis.formats.kml.KmlOptions) -> aspose.gis.VectorLayer:
        '''Creates a layer and opens it for adding new features.
        
        :param path: Path to the file.
        :param options: Driver-specific options.
        :returns: An instance of :py:class:`aspose.gis.VectorLayer`.'''
        raise NotImplementedError()
    
    @overload
    def create_layer(self, path : aspose.gis.AbstractPath, options : aspose.gis.DriverOptions, spatial_reference_system : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> aspose.gis.VectorLayer:
        '''Creates a layer and opens it for adding new features.
        
        :param path: Path to the file.
        :param options: Driver-specific options.
        :param spatial_reference_system: Spatial reference system.
        :returns: An instance of :py:class:`aspose.gis.VectorLayer`.'''
        raise NotImplementedError()
    
    @overload
    def create_layer(self, path : aspose.gis.AbstractPath, options : aspose.gis.formats.kml.KmlOptions, spatial_reference_system : aspose.gis.spatialreferencing.SpatialReferenceSystem) -> aspose.gis.VectorLayer:
        '''Creates a layer and opens it for adding new features.
        
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
        :returns: Boolean value, indicating whether specified spatial reference system is supported by the driver.'''
        raise NotImplementedError()
    
    def open_as_kml_layer(self, path : aspose.gis.AbstractPath, options : aspose.gis.formats.kml.KmlOptions) -> aspose.gis.formats.kml.KmlLayer:
        '''Opens a Kml layer for reading.
        
        :param path: Path to the file.
        :param options: Driver-specific options.
        :returns: KmlLayer with specific fields'''
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
    

class KmlLayer(aspose.gis.VectorLayer):
    '''Represents a Kml layer with non-destructive behavior that supports read and writing of features and attributes at one time.
    A Kml layer is a collection of geographic features, stored in a file.'''
    
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
        '''Get spatial reference system of this layer. For KML this is always WGS84.'''
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
        '''Gets the :py:attr:`aspose.gis.formats.kml.KmlLayer.driver` that instantiated this layer.'''
        raise NotImplementedError()
    
    @property
    def region_list(self) -> List[aspose.gis.formats.kml.specificfields.KmlRegionInfo]:
        '''List of KmlRegionInfo from Region nodes'''
        raise NotImplementedError()
    
    @property
    def ground_overlay_list(self) -> List[aspose.gis.formats.kml.specificfields.KmlGroundOverlayInfo]:
        '''List of KmlGroundOverlayInfo from GroundOverlay nodes'''
        raise NotImplementedError()
    
    @property
    def network_link_list(self) -> List[aspose.gis.formats.kml.specificfields.KmlNetworkLinkInfo]:
        '''List of KmlNetworkLinkInfo from NetworkLink nodes'''
        raise NotImplementedError()
    
    @property
    def features(self) -> List[aspose.gis.Feature]:
        '''Gets the list features.'''
        raise NotImplementedError()
    
    def __getitem__(self, key : int) -> aspose.gis.Feature:
        '''Gets the :py:class:`aspose.gis.Feature` at the specified index.'''
        raise NotImplementedError()
    

class KmlOptions(aspose.gis.DriverOptions):
    '''Driver-specific options for KML format.'''
    
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
    def symbol_to_replace_invalid_chars(self) -> str:
        '''Determines which symbol will be used to replace invalid characters on reading.
        Replacing is skipped if value is \'\0\'. By default value is \'\0\' char.'''
        raise NotImplementedError()
    
    @symbol_to_replace_invalid_chars.setter
    def symbol_to_replace_invalid_chars(self, value : str) -> None:
        '''Determines which symbol will be used to replace invalid characters on reading.
        Replacing is skipped if value is \'\0\'. By default value is \'\0\' char.'''
        raise NotImplementedError()
    
    @property
    def document_id(self) -> str:
        '''Used to specified the id of the root \'Document\' node'''
        raise NotImplementedError()
    
    @document_id.setter
    def document_id(self, value : str) -> None:
        '''Used to specified the id of the root \'Document\' node'''
        raise NotImplementedError()
    
    @property
    def auto_id(self) -> aspose.gis.AutoIds:
        '''Auto-generate ids'''
        raise NotImplementedError()
    
    @auto_id.setter
    def auto_id(self, value : aspose.gis.AutoIds) -> None:
        '''Auto-generate ids'''
        raise NotImplementedError()
    
    @property
    def altitude_mode(self) -> aspose.gis.formats.kml.AltitudeModes:
        '''Allows you to specify the AltitudeModes to use for KML geometries'''
        raise NotImplementedError()
    
    @altitude_mode.setter
    def altitude_mode(self, value : aspose.gis.formats.kml.AltitudeModes) -> None:
        '''Allows you to specify the AltitudeModes to use for KML geometries'''
        raise NotImplementedError()
    

class AltitudeModes:
    '''Altitude mode for KML geometries.'''
    
    NONE : AltitudeModes
    '''Without altitude mode.'''
    RELATIVE_TO_GROUND : AltitudeModes
    '''Interprets the altitude as a value in meters above the ground.'''
    CLAMP_TO_GROUND : AltitudeModes
    '''For a camera, this setting also places the camera relativeToGround,
    since putting the camera exactly at terrain height would mean that
    the eye would intersect the terrain (and the view would be blocked).'''
    ABSOLUTE : AltitudeModes
    '''Interprets the altitude as a value in meters above sea level.'''

