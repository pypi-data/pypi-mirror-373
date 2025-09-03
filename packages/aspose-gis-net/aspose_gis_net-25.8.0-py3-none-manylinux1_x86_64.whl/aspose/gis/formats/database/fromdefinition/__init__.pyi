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

class FromDefinitionDataSourceBuilder:
    '''Provides the ability to configure a data source object'''
    
    def add_attribute(self, name : str, type : aspose.gis.AttributeDataType) -> aspose.gis.formats.database.fromdefinition.FromDefinitionDataSourceBuilder:
        '''Configures the name of the field that will contain information for the feature attribute.
        
        :param name: Name of database field for attribute.
        :param type: Type of data into which data from the database should be converted.
        :returns: :py:class:`aspose.gis.formats.database.fromdefinition.FromDefinitionDataSourceBuilder`'''
        raise NotImplementedError()
    
    def geometry_field(self, name : str) -> aspose.gis.formats.database.fromdefinition.FromDefinitionDataSourceBuilder:
        '''Configures the name of the field from which the geometry will be extracted.
        
        :param name: Name of gemetry field.
        :returns: :py:class:`aspose.gis.formats.database.fromdefinition.FromDefinitionDataSourceBuilder`'''
        raise NotImplementedError()
    
    def identity_attribute(self, name : str, overwrite_same_key : bool) -> aspose.gis.formats.database.fromdefinition.FromDefinitionDataSourceBuilder:
        '''Mandatory setting that allows tracking changes.
        
        :param name: An attribute of a feature that will be treated as uniquely identifying the feature.
        :param overwrite_same_key: If this flag is set to true, then newly added features with a unique identifier the same that is already present in the layer,
        the current one will be overwritten, and the data will be read as updated if differences are found.
        Otherwise, an exception will be thrown.
        :returns: :py:class:`aspose.gis.formats.database.fromdefinition.FromDefinitionDataSourceBuilder`'''
        raise NotImplementedError()
    
    def build(self) -> aspose.gis.formats.database.fromdefinition.IFromDefinitionDataSource:
        '''The method retrieves an implementation of the :py:class:`aspose.gis.formats.database.fromdefinition.IFromDefinitionDataSource`
        
        :returns: Implementation of the :py:class:`aspose.gis.formats.database.fromdefinition.IFromDefinitionDataSource`'''
        raise NotImplementedError()
    

class IFromDefinitionDataSource:
    '''Provide the ability to read geospatial data from the database through LINQ and update them.'''
    
    def get_empty_layer(self) -> aspose.gis.VectorLayer:
        '''Allows to create an empty layer. This can be useful when just adding a new record to the database.
        But later the layer can be used to edit newly added records.
        
        :returns: :py:class:`aspose.gis.VectorLayer`'''
        raise NotImplementedError()
    

class QueryableLayerExtension:
    '''Helper class that contains extension methods to directly run the database extraction process.'''
    

