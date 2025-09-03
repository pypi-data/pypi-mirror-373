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

class IconInfo(aspose.gis.XmlNodeLink):
    '''IconInfo Node from KML Format'''
    
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
    
    @property
    def href(self) -> str:
        '''Gets the href.'''
        raise NotImplementedError()
    
    @href.setter
    def href(self, value : str) -> None:
        '''Sets the href.'''
        raise NotImplementedError()
    

class KmlGroundOverlayInfo(aspose.gis.XmlNodeLink):
    '''Specifies object from Kml \'GroundOverlay\' node'''
    
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
    
    @property
    def name(self) -> str:
        '''Name of Ground Overlay'''
        raise NotImplementedError()
    
    @name.setter
    def name(self, value : str) -> None:
        '''Name of Ground Overlay'''
        raise NotImplementedError()
    
    @property
    def visibility(self) -> bool:
        '''Visibility of Ground Overlay'''
        raise NotImplementedError()
    
    @visibility.setter
    def visibility(self, value : bool) -> None:
        '''Visibility of Ground Overlay'''
        raise NotImplementedError()
    
    @property
    def icon(self) -> aspose.gis.formats.kml.specificfields.IconInfo:
        '''IconPath of \'GroundOverlay\' node.'''
        raise NotImplementedError()
    
    @icon.setter
    def icon(self, value : aspose.gis.formats.kml.specificfields.IconInfo) -> None:
        '''IconPath of \'GroundOverlay\' node.'''
        raise NotImplementedError()
    
    @property
    def lat_lon_box(self) -> aspose.gis.formats.kml.specificfields.KmlLatLonBox:
        '''Specifies object from Kml \'LatLonAltBox\' node.'''
        raise NotImplementedError()
    
    @lat_lon_box.setter
    def lat_lon_box(self, value : aspose.gis.formats.kml.specificfields.KmlLatLonBox) -> None:
        '''Specifies object from Kml \'LatLonAltBox\' node.'''
        raise NotImplementedError()
    
    @property
    def draw_order(self) -> float:
        '''DrawOrder of \'GroundOverlay\' node.'''
        raise NotImplementedError()
    
    @draw_order.setter
    def draw_order(self, value : float) -> None:
        '''DrawOrder of \'GroundOverlay\' node.'''
        raise NotImplementedError()
    

class KmlLatLonAltBox(aspose.gis.XmlNodeLink):
    '''KmlLatLonAltBox Node Wrapper'''
    
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
    
    @property
    def north(self) -> float:
        '''North of \'LatLonBox\' node.'''
        raise NotImplementedError()
    
    @north.setter
    def north(self, value : float) -> None:
        '''North of \'LatLonBox\' node.'''
        raise NotImplementedError()
    
    @property
    def south(self) -> float:
        '''South of \'LatLonBox\' node.'''
        raise NotImplementedError()
    
    @south.setter
    def south(self, value : float) -> None:
        '''South of \'LatLonBox\' node.'''
        raise NotImplementedError()
    
    @property
    def east(self) -> float:
        '''East of \'LatLonBox\' node.'''
        raise NotImplementedError()
    
    @east.setter
    def east(self, value : float) -> None:
        '''East of \'LatLonBox\' node.'''
        raise NotImplementedError()
    
    @property
    def west(self) -> float:
        '''West of \'LatLonBox\' node.'''
        raise NotImplementedError()
    
    @west.setter
    def west(self, value : float) -> None:
        '''West of \'LatLonBox\' node.'''
        raise NotImplementedError()
    
    @property
    def min_altitude(self) -> Optional[float]:
        '''MinAltitude of \'LatLonBox\' node.'''
        raise NotImplementedError()
    
    @min_altitude.setter
    def min_altitude(self, value : Optional[float]) -> None:
        '''MinAltitude of \'LatLonBox\' node.'''
        raise NotImplementedError()
    
    @property
    def max_altitude(self) -> Optional[float]:
        '''MaxAltitude of \'LatLonBox\' node.'''
        raise NotImplementedError()
    
    @max_altitude.setter
    def max_altitude(self, value : Optional[float]) -> None:
        '''MaxAltitude of \'LatLonBox\' node.'''
        raise NotImplementedError()
    
    @property
    def rotation(self) -> Optional[float]:
        '''Rotation of \'LatLonBox\' node.'''
        raise NotImplementedError()
    
    @rotation.setter
    def rotation(self, value : Optional[float]) -> None:
        '''Rotation of \'LatLonBox\' node.'''
        raise NotImplementedError()
    

class KmlLatLonBox(aspose.gis.XmlNodeLink):
    '''Specifies object from Kml \'LatLonBox\' node'''
    
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
    
    @property
    def north(self) -> float:
        '''North of \'LatLonBox\' node.'''
        raise NotImplementedError()
    
    @north.setter
    def north(self, value : float) -> None:
        '''North of \'LatLonBox\' node.'''
        raise NotImplementedError()
    
    @property
    def south(self) -> float:
        '''South of \'LatLonBox\' node.'''
        raise NotImplementedError()
    
    @south.setter
    def south(self, value : float) -> None:
        '''South of \'LatLonBox\' node.'''
        raise NotImplementedError()
    
    @property
    def east(self) -> float:
        '''East of \'LatLonBox\' node.'''
        raise NotImplementedError()
    
    @east.setter
    def east(self, value : float) -> None:
        '''East of \'LatLonBox\' node.'''
        raise NotImplementedError()
    
    @property
    def west(self) -> float:
        '''West of \'LatLonBox\' node.'''
        raise NotImplementedError()
    
    @west.setter
    def west(self, value : float) -> None:
        '''West of \'LatLonBox\' node.'''
        raise NotImplementedError()
    
    @property
    def min_altitude(self) -> Optional[float]:
        '''MinAltitude of \'LatLonBox\' node.'''
        raise NotImplementedError()
    
    @min_altitude.setter
    def min_altitude(self, value : Optional[float]) -> None:
        '''MinAltitude of \'LatLonBox\' node.'''
        raise NotImplementedError()
    
    @property
    def max_altitude(self) -> Optional[float]:
        '''MaxAltitude of \'LatLonBox\' node.'''
        raise NotImplementedError()
    
    @max_altitude.setter
    def max_altitude(self, value : Optional[float]) -> None:
        '''MaxAltitude of \'LatLonBox\' node.'''
        raise NotImplementedError()
    
    @property
    def rotation(self) -> Optional[float]:
        '''Rotation of \'LatLonBox\' node.'''
        raise NotImplementedError()
    
    @rotation.setter
    def rotation(self, value : Optional[float]) -> None:
        '''Rotation of \'LatLonBox\' node.'''
        raise NotImplementedError()
    

class KmlLodSettings(aspose.gis.XmlNodeLink):
    '''Specifies object from Kml \'Lod\' node'''
    
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
    
    @property
    def min_lod_pixels(self) -> int:
        '''MinLodPixels of \'Lod\' node.'''
        raise NotImplementedError()
    
    @min_lod_pixels.setter
    def min_lod_pixels(self, value : int) -> None:
        '''MinLodPixels of \'Lod\' node.'''
        raise NotImplementedError()
    
    @property
    def max_lod_pixels(self) -> int:
        '''MaxLodPixels of \'Lod\' node.'''
        raise NotImplementedError()
    
    @max_lod_pixels.setter
    def max_lod_pixels(self, value : int) -> None:
        '''MaxLodPixels of \'Lod\' node.'''
        raise NotImplementedError()
    
    @property
    def min_fade_extent(self) -> int:
        '''MinFadeExtent of \'Lod\' node.'''
        raise NotImplementedError()
    
    @min_fade_extent.setter
    def min_fade_extent(self, value : int) -> None:
        '''MinFadeExtent of \'Lod\' node.'''
        raise NotImplementedError()
    
    @property
    def max_fade_extent(self) -> int:
        '''MaxFadeExtent of \'Lod\' node.'''
        raise NotImplementedError()
    
    @max_fade_extent.setter
    def max_fade_extent(self, value : int) -> None:
        '''MaxFadeExtent of \'Lod\' node.'''
        raise NotImplementedError()
    

class KmlNetworkLinkInfo(aspose.gis.XmlNodeLink):
    '''Specifies object from Kml \'NetworkLink\' node'''
    
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
    
    @property
    def link(self) -> aspose.gis.formats.kml.specificfields.LinkInfo:
        raise NotImplementedError()
    
    @link.setter
    def link(self, value : aspose.gis.formats.kml.specificfields.LinkInfo) -> None:
        raise NotImplementedError()
    
    @property
    def region(self) -> aspose.gis.formats.kml.specificfields.KmlRegionInfo:
        raise NotImplementedError()
    
    @region.setter
    def region(self, value : aspose.gis.formats.kml.specificfields.KmlRegionInfo) -> None:
        raise NotImplementedError()
    

class KmlRegionInfo(aspose.gis.XmlNodeLink):
    '''Specifies object from Kml \'Region\' node'''
    
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
    
    @property
    def lat_lon_alt_box(self) -> aspose.gis.formats.kml.specificfields.KmlLatLonAltBox:
        '''Specifies object from Kml \'LatLonAltBox\' node.'''
        raise NotImplementedError()
    
    @lat_lon_alt_box.setter
    def lat_lon_alt_box(self, value : aspose.gis.formats.kml.specificfields.KmlLatLonAltBox) -> None:
        '''Specifies object from Kml \'LatLonAltBox\' node.'''
        raise NotImplementedError()
    
    @property
    def lod(self) -> aspose.gis.formats.kml.specificfields.KmlLodSettings:
        '''Specifies object from Kml \'Lod\' node.'''
        raise NotImplementedError()
    
    @lod.setter
    def lod(self, value : aspose.gis.formats.kml.specificfields.KmlLodSettings) -> None:
        '''Specifies object from Kml \'Lod\' node.'''
        raise NotImplementedError()
    
    @property
    def id(self) -> str:
        '''Id of \'Region\' node.'''
        raise NotImplementedError()
    
    @id.setter
    def id(self, value : str) -> None:
        '''Id of \'Region\' node.'''
        raise NotImplementedError()
    

class LinkInfo(aspose.gis.XmlNodeLink):
    '''The LinkInfo node of KML format'''
    
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
    
    @property
    def href(self) -> str:
        '''Gets the href.'''
        raise NotImplementedError()
    
    @href.setter
    def href(self, value : str) -> None:
        '''Sets the href.'''
        raise NotImplementedError()
    

