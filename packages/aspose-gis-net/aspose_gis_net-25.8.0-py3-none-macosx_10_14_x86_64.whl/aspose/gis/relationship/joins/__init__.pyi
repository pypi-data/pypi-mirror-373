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

class JoinByGeometryOptions:
    '''Options for layers joining.'''
    
    @property
    def radius(self) -> float:
        '''Specifies a radius to look for the joined geometry.'''
        raise NotImplementedError()
    
    @radius.setter
    def radius(self, value : float) -> None:
        '''Specifies a radius to look for the joined geometry.'''
        raise NotImplementedError()
    
    @property
    def joined_attributes_prefix(self) -> str:
        '''Specifies a prefix string for the joined attribute\'s names. Default is "joined_".'''
        raise NotImplementedError()
    
    @joined_attributes_prefix.setter
    def joined_attributes_prefix(self, value : str) -> None:
        '''Specifies a prefix string for the joined attribute\'s names. Default is "joined_".'''
        raise NotImplementedError()
    

class JoinOptions:
    '''Options for layers joining.'''
    
    @property
    def join_attribute_name(self) -> str:
        '''Specifies an attribute name of the joined layer which value will be used into :py:attr:`aspose.gis.relationship.joins.JoinOptions.ConditionComparer`.'''
        raise NotImplementedError()
    
    @join_attribute_name.setter
    def join_attribute_name(self, value : str) -> None:
        '''Specifies an attribute name of the joined layer which value will be used into :py:attr:`aspose.gis.relationship.joins.JoinOptions.ConditionComparer`.'''
        raise NotImplementedError()
    
    @property
    def target_attribute_name(self) -> str:
        '''Specifies an attribute name of the main layer which value will be used into :py:attr:`aspose.gis.relationship.joins.JoinOptions.ConditionComparer`.'''
        raise NotImplementedError()
    
    @target_attribute_name.setter
    def target_attribute_name(self, value : str) -> None:
        '''Specifies an attribute name of the main layer which value will be used into :py:attr:`aspose.gis.relationship.joins.JoinOptions.ConditionComparer`.'''
        raise NotImplementedError()
    
    @property
    def join_attribute_names(self) -> List[str]:
        '''Specifies a list of attribute names to be joined.
        If it is  or empty, all attributes of the joined layer will be joined.'''
        raise NotImplementedError()
    
    @join_attribute_names.setter
    def join_attribute_names(self, value : List[str]) -> None:
        '''Specifies a list of attribute names to be joined.
        If it is  or empty, all attributes of the joined layer will be joined.'''
        raise NotImplementedError()
    
    @property
    def joined_attributes_prefix(self) -> str:
        '''Specifies a prefix string for the joined attribute\'s names. Default is "joined_".'''
        raise NotImplementedError()
    
    @joined_attributes_prefix.setter
    def joined_attributes_prefix(self, value : str) -> None:
        '''Specifies a prefix string for the joined attribute\'s names. Default is "joined_".'''
        raise NotImplementedError()
    

