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

class KmlAbstractColorStyle:
    '''Provides elements for specifying the color and color mode of style types that derive from it.'''
    
    @property
    def color(self) -> aspose.pydrawing.Color:
        '''Specifies the color of the graphic element. Default value :py:attr:`aspose.pydrawing.Color.White`.'''
        raise NotImplementedError()
    
    @color.setter
    def color(self, value : aspose.pydrawing.Color) -> None:
        '''Specifies the color of the graphic element. Default value :py:attr:`aspose.pydrawing.Color.White`.'''
        raise NotImplementedError()
    
    @property
    def color_mode(self) -> aspose.gis.formats.kml.styles.KmlColorModes:
        '''Specifies the color mode of the graphic element. Default Value: normal.'''
        raise NotImplementedError()
    
    @color_mode.setter
    def color_mode(self, value : aspose.gis.formats.kml.styles.KmlColorModes) -> None:
        '''Specifies the color mode of the graphic element. Default Value: normal.'''
        raise NotImplementedError()
    

class KmlBalloonStyle:
    '''Specifies how the description balloon is drawn.'''
    
    @property
    def background_color(self) -> aspose.pydrawing.Color:
        '''Specifies the background color of the graphic element. Default value is :py:attr:`aspose.pydrawing.Color.White`.'''
        raise NotImplementedError()
    
    @background_color.setter
    def background_color(self, value : aspose.pydrawing.Color) -> None:
        '''Specifies the background color of the graphic element. Default value is :py:attr:`aspose.pydrawing.Color.White`.'''
        raise NotImplementedError()
    
    @property
    def text_color(self) -> aspose.pydrawing.Color:
        '''Specifies the foreground color of the text. Default value is :py:attr:`aspose.pydrawing.Color.Black`.'''
        raise NotImplementedError()
    
    @text_color.setter
    def text_color(self, value : aspose.pydrawing.Color) -> None:
        '''Specifies the foreground color of the text. Default value is :py:attr:`aspose.pydrawing.Color.Black`.'''
        raise NotImplementedError()
    
    @property
    def text(self) -> str:
        '''Specifies the text displayed in the balloon. Default value is .'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''Specifies the text displayed in the balloon. Default value is .'''
        raise NotImplementedError()
    
    @property
    def display_mode(self) -> aspose.gis.formats.kml.styles.KmlDisplayModes:
        '''Controls whether the balloon is displayed or hidden. Default value is :py:attr:`aspose.gis.formats.kml.styles.KmlDisplayModes.SHOW`'''
        raise NotImplementedError()
    
    @display_mode.setter
    def display_mode(self, value : aspose.gis.formats.kml.styles.KmlDisplayModes) -> None:
        '''Controls whether the balloon is displayed or hidden. Default value is :py:attr:`aspose.gis.formats.kml.styles.KmlDisplayModes.SHOW`'''
        raise NotImplementedError()
    

class KmlCoordinate:
    '''Specifies an image coordinate system.'''
    
    @property
    def x(self) -> float:
        '''The X component of a point. Default value is 0.5.'''
        raise NotImplementedError()
    
    @x.setter
    def x(self, value : float) -> None:
        '''The X component of a point. Default value is 0.5.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''The Y component of a point. Default value is 0.5.'''
        raise NotImplementedError()
    
    @y.setter
    def y(self, value : float) -> None:
        '''The Y component of a point. Default value is 0.5.'''
        raise NotImplementedError()
    
    @property
    def x_units(self) -> aspose.gis.formats.kml.styles.KmlUnits:
        '''Units in which the X value is specified. Default value is :py:attr:`aspose.gis.formats.kml.styles.KmlUnits.FRACTION`.'''
        raise NotImplementedError()
    
    @x_units.setter
    def x_units(self, value : aspose.gis.formats.kml.styles.KmlUnits) -> None:
        '''Units in which the X value is specified. Default value is :py:attr:`aspose.gis.formats.kml.styles.KmlUnits.FRACTION`.'''
        raise NotImplementedError()
    
    @property
    def y_units(self) -> aspose.gis.formats.kml.styles.KmlUnits:
        '''Units in which the Y value is specified. Default value is :py:attr:`aspose.gis.formats.kml.styles.KmlUnits.FRACTION`.'''
        raise NotImplementedError()
    
    @y_units.setter
    def y_units(self, value : aspose.gis.formats.kml.styles.KmlUnits) -> None:
        '''Units in which the Y value is specified. Default value is :py:attr:`aspose.gis.formats.kml.styles.KmlUnits.FRACTION`.'''
        raise NotImplementedError()
    

class KmlFeatureStyle(aspose.gis.FeatureStyle):
    '''Styles affect how Geometry is presented.
    Ths styles are encoded in the document section and have a unique identifier for each style.
    These are known as \'shared styles\' in the kml specification.'''
    
    null : aspose.gis.IFeatureStyle
    '''Gets an instance of null style.'''
    @property
    def line(self) -> aspose.gis.formats.kml.styles.KmlLineStyle:
        '''Specifies the drawing style (color, color mode, and line width) for all line geometry.
        Use  to indicate a missing style.
        Default Value is .'''
        raise NotImplementedError()
    
    @line.setter
    def line(self, value : aspose.gis.formats.kml.styles.KmlLineStyle) -> None:
        '''Specifies the drawing style (color, color mode, and line width) for all line geometry.
        Use  to indicate a missing style.
        Default Value is .'''
        raise NotImplementedError()
    
    @property
    def polygon(self) -> aspose.gis.formats.kml.styles.KmlPolygonStyle:
        '''Specifies the drawing style for all polygons, including polygon extrusions and line extrusions.
        Use  to indicate a missing style.
        Default Value is .'''
        raise NotImplementedError()
    
    @polygon.setter
    def polygon(self, value : aspose.gis.formats.kml.styles.KmlPolygonStyle) -> None:
        '''Specifies the drawing style for all polygons, including polygon extrusions and line extrusions.
        Use  to indicate a missing style.
        Default Value is .'''
        raise NotImplementedError()
    
    @property
    def icon(self) -> aspose.gis.formats.kml.styles.KmlIconStyle:
        '''Specifies how icons for point Placemarks are drawn.
        Use  to indicate a missing style.
        Default Value is .'''
        raise NotImplementedError()
    
    @icon.setter
    def icon(self, value : aspose.gis.formats.kml.styles.KmlIconStyle) -> None:
        '''Specifies how icons for point Placemarks are drawn.
        Use  to indicate a missing style.
        Default Value is .'''
        raise NotImplementedError()
    
    @property
    def label(self) -> aspose.gis.formats.kml.styles.KmlLabelStyle:
        '''Specifies how labels of a Feature are drawn.
        Use  to indicate a missing style.
        Default Value is .'''
        raise NotImplementedError()
    
    @label.setter
    def label(self, value : aspose.gis.formats.kml.styles.KmlLabelStyle) -> None:
        '''Specifies how labels of a Feature are drawn.
        Use  to indicate a missing style.
        Default Value is .'''
        raise NotImplementedError()
    
    @property
    def balloon(self) -> aspose.gis.formats.kml.styles.KmlBalloonStyle:
        '''Specifies how the description balloon for placemarks is drawn.
        Use  to indicate a missing style.
        Default Value is .'''
        raise NotImplementedError()
    
    @balloon.setter
    def balloon(self, value : aspose.gis.formats.kml.styles.KmlBalloonStyle) -> None:
        '''Specifies how the description balloon for placemarks is drawn.
        Use  to indicate a missing style.
        Default Value is .'''
        raise NotImplementedError()
    
    @property
    def list(self) -> aspose.gis.formats.kml.styles.KmlListStyle:
        '''Specifies how a Feature is displayed in the list view.
        Use  to indicate a missing style.
        Default Value is .'''
        raise NotImplementedError()
    
    @list.setter
    def list(self, value : aspose.gis.formats.kml.styles.KmlListStyle) -> None:
        '''Specifies how a Feature is displayed in the list view.
        Use  to indicate a missing style.
        Default Value is .'''
        raise NotImplementedError()
    

class KmlIconResource:
    '''Specifies an icon resource location'''
    
    @property
    def href(self) -> str:
        '''Specifies the the resource location as a URL.
        Default value is  means the href is none.'''
        raise NotImplementedError()
    
    @href.setter
    def href(self, value : str) -> None:
        '''Specifies the the resource location as a URL.
        Default value is  means the href is none.'''
        raise NotImplementedError()
    

class KmlIconStyle(KmlAbstractColorStyle):
    '''Specifies how icons for kml:Placemarks and kml:PhotoOverlay with a kml:Point geometry are drawn
    in an earth browser\'s list and geographic views.'''
    
    @property
    def color(self) -> aspose.pydrawing.Color:
        '''Specifies the color of the graphic element. Default value :py:attr:`aspose.pydrawing.Color.White`.'''
        raise NotImplementedError()
    
    @color.setter
    def color(self, value : aspose.pydrawing.Color) -> None:
        '''Specifies the color of the graphic element. Default value :py:attr:`aspose.pydrawing.Color.White`.'''
        raise NotImplementedError()
    
    @property
    def color_mode(self) -> aspose.gis.formats.kml.styles.KmlColorModes:
        '''Specifies the color mode of the graphic element. Default Value: normal.'''
        raise NotImplementedError()
    
    @color_mode.setter
    def color_mode(self, value : aspose.gis.formats.kml.styles.KmlColorModes) -> None:
        '''Specifies the color mode of the graphic element. Default Value: normal.'''
        raise NotImplementedError()
    
    @property
    def scale(self) -> float:
        '''Specifies a scale factor that shall be applied to the graphic element. Default Value is \'1\'.'''
        raise NotImplementedError()
    
    @scale.setter
    def scale(self, value : float) -> None:
        '''Specifies a scale factor that shall be applied to the graphic element. Default Value is \'1\'.'''
        raise NotImplementedError()
    
    @property
    def heading(self) -> float:
        '''Direction (North, South, East, West), in decimal degrees. Values range from 0 (North) to 360 degrees. Default Value is \'0\'.'''
        raise NotImplementedError()
    
    @heading.setter
    def heading(self, value : float) -> None:
        '''Direction (North, South, East, West), in decimal degrees. Values range from 0 (North) to 360 degrees. Default Value is \'0\'.'''
        raise NotImplementedError()
    
    @property
    def resource(self) -> aspose.gis.formats.kml.styles.KmlIconResource:
        '''Specifies the resource location. Default value is  means the Icon is missed.'''
        raise NotImplementedError()
    
    @resource.setter
    def resource(self, value : aspose.gis.formats.kml.styles.KmlIconResource) -> None:
        '''Specifies the resource location. Default value is  means the Icon is missed.'''
        raise NotImplementedError()
    
    @property
    def hot_spot(self) -> aspose.gis.formats.kml.styles.KmlCoordinate:
        '''Specifies the position of the reference point on the icon that is anchored to the Point specified in the Placemark.
        Default value is  means the HotSpot is missed.'''
        raise NotImplementedError()
    
    @hot_spot.setter
    def hot_spot(self, value : aspose.gis.formats.kml.styles.KmlCoordinate) -> None:
        '''Specifies the position of the reference point on the icon that is anchored to the Point specified in the Placemark.
        Default value is  means the HotSpot is missed.'''
        raise NotImplementedError()
    

class KmlItemIcon:
    '''Specifies an icon resource location in a list.'''
    
    @property
    def state(self) -> aspose.gis.formats.kml.styles.KmlItemIconStates:
        '''Specifies the current state of the NetworkLink or Folder.
        Default value is :py:attr:`aspose.gis.formats.kml.styles.KmlItemIconStates.NONE`.'''
        raise NotImplementedError()
    
    @state.setter
    def state(self, value : aspose.gis.formats.kml.styles.KmlItemIconStates) -> None:
        '''Specifies the current state of the NetworkLink or Folder.
        Default value is :py:attr:`aspose.gis.formats.kml.styles.KmlItemIconStates.NONE`.'''
        raise NotImplementedError()
    
    @property
    def sub_state(self) -> aspose.gis.formats.kml.styles.KmlItemIconStates:
        '''Specifies the additional state of the NetworkLink or Folder.
        Default value is :py:attr:`aspose.gis.formats.kml.styles.KmlItemIconStates.NONE`.'''
        raise NotImplementedError()
    
    @sub_state.setter
    def sub_state(self, value : aspose.gis.formats.kml.styles.KmlItemIconStates) -> None:
        '''Specifies the additional state of the NetworkLink or Folder.
        Default value is :py:attr:`aspose.gis.formats.kml.styles.KmlItemIconStates.NONE`.'''
        raise NotImplementedError()
    
    @property
    def href(self) -> str:
        '''Specifies the resource location as a URL.
        Default value is  means the href is none.'''
        raise NotImplementedError()
    
    @href.setter
    def href(self, value : str) -> None:
        '''Specifies the resource location as a URL.
        Default value is  means the href is none.'''
        raise NotImplementedError()
    

class KmlLabelStyle(KmlAbstractColorStyle):
    '''Specifies how the label is drawn in the geographic view.'''
    
    @property
    def color(self) -> aspose.pydrawing.Color:
        '''Specifies the color of the graphic element. Default value :py:attr:`aspose.pydrawing.Color.White`.'''
        raise NotImplementedError()
    
    @color.setter
    def color(self, value : aspose.pydrawing.Color) -> None:
        '''Specifies the color of the graphic element. Default value :py:attr:`aspose.pydrawing.Color.White`.'''
        raise NotImplementedError()
    
    @property
    def color_mode(self) -> aspose.gis.formats.kml.styles.KmlColorModes:
        '''Specifies the color mode of the graphic element. Default Value: normal.'''
        raise NotImplementedError()
    
    @color_mode.setter
    def color_mode(self, value : aspose.gis.formats.kml.styles.KmlColorModes) -> None:
        '''Specifies the color mode of the graphic element. Default Value: normal.'''
        raise NotImplementedError()
    
    @property
    def scale(self) -> float:
        '''Specifies a scale factor to be applied to the label. Default value is \'1\'.'''
        raise NotImplementedError()
    
    @scale.setter
    def scale(self, value : float) -> None:
        '''Specifies a scale factor to be applied to the label. Default value is \'1\'.'''
        raise NotImplementedError()
    

class KmlLineStyle(KmlAbstractColorStyle):
    '''Specifies how the name of a kml:AbstractFeatureGroup is drawn in the geographic view.'''
    
    @property
    def color(self) -> aspose.pydrawing.Color:
        '''Specifies the color of the graphic element. Default value :py:attr:`aspose.pydrawing.Color.White`.'''
        raise NotImplementedError()
    
    @color.setter
    def color(self, value : aspose.pydrawing.Color) -> None:
        '''Specifies the color of the graphic element. Default value :py:attr:`aspose.pydrawing.Color.White`.'''
        raise NotImplementedError()
    
    @property
    def color_mode(self) -> aspose.gis.formats.kml.styles.KmlColorModes:
        '''Specifies the color mode of the graphic element. Default Value: normal.'''
        raise NotImplementedError()
    
    @color_mode.setter
    def color_mode(self, value : aspose.gis.formats.kml.styles.KmlColorModes) -> None:
        '''Specifies the color mode of the graphic element. Default Value: normal.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Width of the line, in pixels. Default Value is \'1\'.'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : float) -> None:
        '''Width of the line, in pixels. Default Value is \'1\'.'''
        raise NotImplementedError()
    

class KmlListStyle:
    '''Specifies how a Feature is displayed in the list view.'''
    
    @property
    def item_type(self) -> aspose.gis.formats.kml.styles.KmlItemTypes:
        '''Specifies how a kml:Folder and its contents shall be displayed as items in the list view.
        Default value is :py:attr:`aspose.gis.formats.kml.styles.KmlItemTypes.CHECK`.'''
        raise NotImplementedError()
    
    @item_type.setter
    def item_type(self, value : aspose.gis.formats.kml.styles.KmlItemTypes) -> None:
        '''Specifies how a kml:Folder and its contents shall be displayed as items in the list view.
        Default value is :py:attr:`aspose.gis.formats.kml.styles.KmlItemTypes.CHECK`.'''
        raise NotImplementedError()
    
    @property
    def background_color(self) -> aspose.pydrawing.Color:
        '''Specifies the background color of the graphic element. Default value is :py:attr:`aspose.pydrawing.Color.White`.'''
        raise NotImplementedError()
    
    @background_color.setter
    def background_color(self, value : aspose.pydrawing.Color) -> None:
        '''Specifies the background color of the graphic element. Default value is :py:attr:`aspose.pydrawing.Color.White`.'''
        raise NotImplementedError()
    
    @property
    def item_icons(self) -> Sequence[aspose.gis.formats.kml.styles.KmlItemIcon]:
        '''Icon used in the List view that reflects the state of a Folder or Link fetch.
        Default value is  means the icons are none.'''
        raise NotImplementedError()
    
    @item_icons.setter
    def item_icons(self, value : Sequence[aspose.gis.formats.kml.styles.KmlItemIcon]) -> None:
        '''Icon used in the List view that reflects the state of a Folder or Link fetch.
        Default value is  means the icons are none.'''
        raise NotImplementedError()
    
    @property
    def max_snippet_lines(self) -> int:
        '''Specifies the maximum number of lines to display in the list view. Default value is \'2\'.'''
        raise NotImplementedError()
    
    @max_snippet_lines.setter
    def max_snippet_lines(self, value : int) -> None:
        '''Specifies the maximum number of lines to display in the list view. Default value is \'2\'.'''
        raise NotImplementedError()
    

class KmlPolygonStyle(KmlAbstractColorStyle):
    '''Specifies the drawing style for a Polygon,
    including a Polygon and the extruded portion of a kml:Polygon or LineString.'''
    
    @property
    def color(self) -> aspose.pydrawing.Color:
        '''Specifies the color of the graphic element. Default value :py:attr:`aspose.pydrawing.Color.White`.'''
        raise NotImplementedError()
    
    @color.setter
    def color(self, value : aspose.pydrawing.Color) -> None:
        '''Specifies the color of the graphic element. Default value :py:attr:`aspose.pydrawing.Color.White`.'''
        raise NotImplementedError()
    
    @property
    def color_mode(self) -> aspose.gis.formats.kml.styles.KmlColorModes:
        '''Specifies the color mode of the graphic element. Default Value: normal.'''
        raise NotImplementedError()
    
    @color_mode.setter
    def color_mode(self, value : aspose.gis.formats.kml.styles.KmlColorModes) -> None:
        '''Specifies the color mode of the graphic element. Default Value: normal.'''
        raise NotImplementedError()
    
    @property
    def fill(self) -> bool:
        '''Specifies whether to fill the polygon. Default value is .'''
        raise NotImplementedError()
    
    @fill.setter
    def fill(self, value : bool) -> None:
        '''Specifies whether to fill the polygon. Default value is .'''
        raise NotImplementedError()
    
    @property
    def outline(self) -> bool:
        '''Specifies whether to outline the polygon. Default value is .'''
        raise NotImplementedError()
    
    @outline.setter
    def outline(self, value : bool) -> None:
        '''Specifies whether to outline the polygon. Default value is .'''
        raise NotImplementedError()
    

class KmlColorModes:
    '''Specifies the color mode for a graphic element.'''
    
    NORMAL : KmlColorModes
    '''Specifies a single color value.'''
    RANDOM : KmlColorModes
    '''Specifies to use a random color value.'''

class KmlDisplayModes:
    '''Controls whether the element is displayed or hidden.'''
    
    SHOW : KmlDisplayModes
    '''Specifies to show the element (known as \'default\' in the kml specification).'''
    HIDE : KmlDisplayModes
    '''Specifies to hide the element.'''

class KmlItemIconStates:
    '''Specifies the current state of a kml:NetworkLink or kml:Folder.'''
    
    NONE : KmlItemIconStates
    '''Undefined (none).'''
    OPEN : KmlItemIconStates
    '''Open folder.'''
    CLOSED : KmlItemIconStates
    '''Closed folder.'''
    ERROR : KmlItemIconStates
    '''Error in fetch.'''
    FETCHING0 : KmlItemIconStates
    '''Fetch state 0.'''
    FETCHING1 : KmlItemIconStates
    '''Fetch state 1.'''
    FETCHING2 : KmlItemIconStates
    '''Fetch state 2.'''

class KmlItemTypes:
    '''Specifies how a kml:Feature and its contents shall be displayed as items in a list view.'''
    
    RADIO_FOLDER : KmlItemTypes
    '''Only one of items shall be visible at a time.'''
    CHECK : KmlItemTypes
    '''The visibility is tied to its item\'s checkbox'''
    CHECK_HIDE_CHILDREN : KmlItemTypes
    '''Use a normal checkbox for visibility but do not display the item\'s children in the list view.'''
    CHECK_OFF_ONLY : KmlItemTypes
    '''Prevents all items from being made visible at once—that is,
    the user can turn everything in the Container Group off but cannot turn everything on at the same time.'''

class KmlUnits:
    '''Specifies units fof an image coordinate system.'''
    
    PIXELS : KmlUnits
    '''Indicates the x value in pixels.'''
    FRACTION : KmlUnits
    '''Indicates the x value is a fraction of the icon.'''
    INSET_PIXELS : KmlUnits
    '''Indicates the indent from the right edge of the icon.'''

