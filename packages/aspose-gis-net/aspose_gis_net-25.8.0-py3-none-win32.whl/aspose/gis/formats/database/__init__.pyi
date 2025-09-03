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

class DatabaseDataSourceBuilder:
    '''Provides the ability to configure a database data source object.'''
    
    def from_query(self, query : str) -> aspose.gis.formats.database.DatabaseQueryDataSourceBuilder:
        '''Configuring the data source for custom database queries.
        
        :param query: Query string.
        :returns: :py:class:`aspose.gis.formats.database.DatabaseQueryDataSourceBuilder`'''
        raise NotImplementedError()
    

class DatabaseExternalSrsSettingsBuilder:
    '''Provides the possibility of configuring a database query to retrieve a list of used spatial reference systems.'''
    
    def external_srs_fields(self, auth_srid_field : str, sr_text_field : str) -> aspose.gis.formats.database.DatabaseExternalSrsSettingsBuilder:
        '''Specifies special field names from which to read information about additionally requested spatial reference systems.
        
        :param auth_srid_field: Field for reading spatial reference id, default: auth_srid.
        :param sr_text_field: Field for reading the spatial coordinate system represented by WKT, default: srtext.
        :returns: :py:class:`aspose.gis.formats.database.DatabaseExternalSrsSettingsBuilder`'''
        raise NotImplementedError()
    
    def end_external_srs(self) -> aspose.gis.formats.database.DatabaseQueryDataSourceBuilder:
        '''Complete the configuration of the external srs and return the parent context.
        
        :returns: :py:class:`aspose.gis.formats.database.DatabaseQueryDataSourceBuilder`'''
        raise NotImplementedError()
    

class DatabaseQueryDataSourceBuilder:
    '''Provides the ability to configure a query to database to to extract geospatial information.'''
    
    def geometry_field(self, name : str) -> aspose.gis.formats.database.DatabaseQueryDataSourceBuilder:
        '''Configures the name of the field from which the geometry will be extracted.
        
        :param name: Name of gemetry field.
        :returns: :py:class:`aspose.gis.formats.database.DatabaseQueryDataSourceBuilder`'''
        raise NotImplementedError()
    
    def add_attribute(self, name : str, type : aspose.gis.AttributeDataType) -> aspose.gis.formats.database.DatabaseQueryDataSourceBuilder:
        '''Configures the name of the field that will contain information for the feature attribute.
        
        :param name: Name of query field for attribute.
        :param type: Type of data into which data from the database should be converted.
        :returns: :py:class:`aspose.gis.formats.database.DatabaseQueryDataSourceBuilder`'''
        raise NotImplementedError()
    
    def srid_field(self, name : str) -> aspose.gis.formats.database.DatabaseQueryDataSourceBuilder:
        '''Configuring the name of the query field that will contain the spatial reference system identifier (srid).
        
        :param name: Name of the query field containing the spatial reference system identifier.
        :returns: :py:class:`aspose.gis.formats.database.DatabaseQueryDataSourceBuilder`'''
        raise NotImplementedError()
    
    def as_trackable_for_changes(self, table_name : str, identity_attribute : str, overwrite_same_key : bool, db_func : str) -> aspose.gis.formats.database.dataediting.DatabaseEditableDataSourceBuilder:
        '''Configure the resulting layer to track changes and create a data source to synchronize the changes made.
        
        :param table_name: The name of the table where the changes will be made.
        :param identity_attribute: An attribute of a feature that will be treated as uniquely identifying the feature.
        :param overwrite_same_key: If this flag is set to true, then newly added features with a unique identifier the same that is already present in the layer, the current one will be overwritten, and the data will be read as updated if differences are found.
        :param db_func: Function that will be supplied in SQL query to transform binary data into geographic data representation of the current database.
        :returns: :py:class:`aspose.gis.formats.database.dataediting.DatabaseEditableDataSourceBuilder`'''
        raise NotImplementedError()
    
    def use_external_srs_from_query(self, srs_query : str) -> aspose.gis.formats.database.DatabaseExternalSrsSettingsBuilder:
        '''Allows you to configure the data source to use third-party spatial reference system data, bypassing the pre-installed data in the Aspose.GIS library.
        
        :param srs_query: Query to retrieve information about additional spatial coordinate systems used in the main query to retrieve features.
        :returns: :py:class:`aspose.gis.formats.database.DatabaseExternalSrsSettingsBuilder`'''
        raise NotImplementedError()
    
    def build(self) -> aspose.gis.formats.database.IDatabaseDataSource:
        '''The method retrieves an implementation of the :py:class:`aspose.gis.formats.database.IDatabaseDataSource`
        
        :returns: Implementation of the :py:class:`aspose.gis.formats.database.IDatabaseDataSource`'''
        raise NotImplementedError()
    

class IDatabaseDataSource:
    '''Provide the ability to read geospatial data from the database.'''
    

