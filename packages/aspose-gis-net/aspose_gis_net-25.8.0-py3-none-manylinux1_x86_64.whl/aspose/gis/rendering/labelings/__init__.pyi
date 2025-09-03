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

class LabelPlacement:
    '''Label placement specifies how labels are placed relatively to feature\'s geometry.'''
    
    def clone(self) -> aspose.gis.rendering.labelings.LabelPlacement:
        '''Clones this instance.
        
        :returns: A clone of this instance.'''
        raise NotImplementedError()
    

class Labeling:
    '''The abstract root class for labelings, classes that describe how to place labels on features.'''
    
    null : aspose.gis.rendering.labelings.NullLabeling
    '''Gets an instance of :py:class:`aspose.gis.rendering.labelings.NullLabeling`.'''

class LabelingRule:
    '''A user-defined rule for :py:class:`aspose.gis.rendering.labelings.RuleBasedLabeling`.'''
    
    @staticmethod
    def create_else_rule(labeling : aspose.gis.rendering.labelings.Labeling) -> aspose.gis.rendering.labelings.LabelingRule:
        '''Creates new rule that applies a labeling to feature whenever it doesn\'t match any filter rule.
        
        :param labeling: Labeling to apply.
        :returns: New LabelingRule object.'''
        raise NotImplementedError()
    
    @property
    def is_else_rule(self) -> bool:
        '''Gets a value indicating whether this rule is "else-rule".'''
        raise NotImplementedError()
    
    @property
    def is_filter_rule(self) -> bool:
        '''Gets a value indicating whether this rule is "filter-rule".'''
        raise NotImplementedError()
    
    @property
    def labeling(self) -> aspose.gis.rendering.labelings.Labeling:
        '''Labeling to apply to the feature.'''
        raise NotImplementedError()
    

class LineLabelPlacement(LabelPlacement):
    '''Line label placement places labels along line.'''
    
    def clone(self) -> aspose.gis.rendering.labelings.LabelPlacement:
        '''Clones this instance.
        
        :returns: A clone of this instance.'''
        raise NotImplementedError()
    
    @property
    def offset(self) -> aspose.gis.rendering.Measurement:
        '''The offset from the linear path.
        Positive values offset to the left of the line, negative to the right. Default is 0.'''
        raise NotImplementedError()
    
    @offset.setter
    def offset(self, value : aspose.gis.rendering.Measurement) -> None:
        '''The offset from the linear path.
        Positive values offset to the left of the line, negative to the right. Default is 0.'''
        raise NotImplementedError()
    
    @property
    def alignment(self) -> aspose.gis.rendering.labelings.LineLabelAlignment:
        '''Specifies how the label is aligned with the linear path. Default is :py:attr:`aspose.gis.rendering.labelings.LineLabelAlignment.PARALLEL`.'''
        raise NotImplementedError()
    
    @alignment.setter
    def alignment(self, value : aspose.gis.rendering.labelings.LineLabelAlignment) -> None:
        '''Specifies how the label is aligned with the linear path. Default is :py:attr:`aspose.gis.rendering.labelings.LineLabelAlignment.PARALLEL`.'''
        raise NotImplementedError()
    
    @property
    def max_angle_delta(self) -> float:
        '''When used with :py:attr:`aspose.gis.rendering.labelings.LineLabelAlignment.CURVED` sets the maximum angle in degrees between two
        subsequent characters in a curved label. Default is 25.'''
        raise NotImplementedError()
    
    @max_angle_delta.setter
    def max_angle_delta(self, value : float) -> None:
        '''When used with :py:attr:`aspose.gis.rendering.labelings.LineLabelAlignment.CURVED` sets the maximum angle in degrees between two
        subsequent characters in a curved label. Default is 25.'''
        raise NotImplementedError()
    

class NullLabeling(Labeling):
    '''The :py:class:`aspose.gis.rendering.labelings.NullLabeling` skips labeling of a geometry it is applied to.'''
    
    null : aspose.gis.rendering.labelings.NullLabeling
    '''Gets an instance of :py:class:`aspose.gis.rendering.labelings.NullLabeling`.'''
    instance : aspose.gis.rendering.labelings.NullLabeling
    '''Gets an instance of :py:class:`aspose.gis.rendering.labelings.NullLabeling`.'''

class PointLabelPlacement(LabelPlacement):
    '''Points label placement places labels near geometries centers.'''
    
    def clone(self) -> aspose.gis.rendering.labelings.LabelPlacement:
        '''Clones this instance.
        
        :returns: A clone of this instance.'''
        raise NotImplementedError()
    
    @property
    def horizontal_anchor_point(self) -> aspose.gis.rendering.symbolizers.HorizontalAnchor:
        '''Specifies which side of a label will be aligned horizontally with the point location.'''
        raise NotImplementedError()
    
    @horizontal_anchor_point.setter
    def horizontal_anchor_point(self, value : aspose.gis.rendering.symbolizers.HorizontalAnchor) -> None:
        '''Specifies which side of a label will be aligned horizontally with the point location.'''
        raise NotImplementedError()
    
    @property
    def vertical_anchor_point(self) -> aspose.gis.rendering.symbolizers.VerticalAnchor:
        '''Specifies which side of a label will be aligned vertically with the point location.'''
        raise NotImplementedError()
    
    @vertical_anchor_point.setter
    def vertical_anchor_point(self, value : aspose.gis.rendering.symbolizers.VerticalAnchor) -> None:
        '''Specifies which side of a label will be aligned vertically with the point location.'''
        raise NotImplementedError()
    
    @property
    def horizontal_offset(self) -> aspose.gis.rendering.Measurement:
        '''Specifies horizontal offset from a point location to the labels anchor point.'''
        raise NotImplementedError()
    
    @horizontal_offset.setter
    def horizontal_offset(self, value : aspose.gis.rendering.Measurement) -> None:
        '''Specifies horizontal offset from a point location to the labels anchor point.'''
        raise NotImplementedError()
    
    @property
    def vertical_offset(self) -> aspose.gis.rendering.Measurement:
        '''Specifies vertical offset from a point location to the labels anchor point.'''
        raise NotImplementedError()
    
    @vertical_offset.setter
    def vertical_offset(self, value : aspose.gis.rendering.Measurement) -> None:
        '''Specifies vertical offset from a point location to the labels anchor point.'''
        raise NotImplementedError()
    
    @property
    def rotation(self) -> float:
        '''Specifies rotation of label in degrees.'''
        raise NotImplementedError()
    
    @rotation.setter
    def rotation(self, value : float) -> None:
        '''Specifies rotation of label in degrees.'''
        raise NotImplementedError()
    

class RuleBasedLabeling(Labeling):
    '''Applies a labeling to feature according to user-defined rules.'''
    
    def add_else_rule(self, labeling : aspose.gis.rendering.labelings.Labeling) -> None:
        '''Adds a labeling that will be applied to features that don\'t match any filtering rule.
        
        :param labeling: A labeling.'''
        raise NotImplementedError()
    
    def add(self, rule : aspose.gis.rendering.labelings.LabelingRule) -> None:
        '''Adds a rule.
        
        :param rule: Rule to add.'''
        raise NotImplementedError()
    
    null : aspose.gis.rendering.labelings.NullLabeling
    '''Gets an instance of :py:class:`aspose.gis.rendering.labelings.NullLabeling`.'''

class SimpleLabeling(Labeling):
    '''A simple labeling places label on every feature.'''
    
    def clone(self) -> aspose.gis.rendering.labelings.SimpleLabeling:
        '''Clones this instance.
        
        :returns: A clone of this instance.'''
        raise NotImplementedError()
    
    null : aspose.gis.rendering.labelings.NullLabeling
    '''Gets an instance of :py:class:`aspose.gis.rendering.labelings.NullLabeling`.'''
    @property
    def label_attribute(self) -> str:
        '''Attribute name to use as a source of labels. Ignored if :py:attr:`aspose.gis.rendering.labelings.SimpleLabeling.LabelExpression` is set.
        Either :py:attr:`aspose.gis.rendering.labelings.SimpleLabeling.label_attribute` or :py:attr:`aspose.gis.rendering.labelings.SimpleLabeling.LabelExpression` must be set before rendering;
        :py:class:`System.InvalidOperationException` is thrown otherwise.'''
        raise NotImplementedError()
    
    @label_attribute.setter
    def label_attribute(self, value : str) -> None:
        '''Attribute name to use as a source of labels. Ignored if :py:attr:`aspose.gis.rendering.labelings.SimpleLabeling.LabelExpression` is set.
        Either :py:attr:`aspose.gis.rendering.labelings.SimpleLabeling.label_attribute` or :py:attr:`aspose.gis.rendering.labelings.SimpleLabeling.LabelExpression` must be set before rendering;
        :py:class:`System.InvalidOperationException` is thrown otherwise.'''
        raise NotImplementedError()
    
    @property
    def font_family(self) -> str:
        '''Font family to use to render text. The default is system dependent value.'''
        raise NotImplementedError()
    
    @font_family.setter
    def font_family(self, value : str) -> None:
        '''Font family to use to render text. The default is system dependent value.'''
        raise NotImplementedError()
    
    @property
    def font_style(self) -> aspose.gis.rendering.labelings.FontStyle:
        '''Style to apply to text.'''
        raise NotImplementedError()
    
    @font_style.setter
    def font_style(self, value : aspose.gis.rendering.labelings.FontStyle) -> None:
        '''Style to apply to text.'''
        raise NotImplementedError()
    
    @property
    def font_size(self) -> aspose.gis.rendering.Measurement:
        '''Size of the text.'''
        raise NotImplementedError()
    
    @font_size.setter
    def font_size(self, value : aspose.gis.rendering.Measurement) -> None:
        '''Size of the text.'''
        raise NotImplementedError()
    
    @property
    def font_color(self) -> aspose.pydrawing.Color:
        '''Determines color of text.'''
        raise NotImplementedError()
    
    @font_color.setter
    def font_color(self, value : aspose.pydrawing.Color) -> None:
        '''Determines color of text.'''
        raise NotImplementedError()
    
    @property
    def halo_size(self) -> aspose.gis.rendering.Measurement:
        '''Size of the halo (stroke) around text.'''
        raise NotImplementedError()
    
    @halo_size.setter
    def halo_size(self, value : aspose.gis.rendering.Measurement) -> None:
        '''Size of the halo (stroke) around text.'''
        raise NotImplementedError()
    
    @property
    def halo_color(self) -> aspose.pydrawing.Color:
        '''Color of the halo (stroke) around text.'''
        raise NotImplementedError()
    
    @halo_color.setter
    def halo_color(self, value : aspose.pydrawing.Color) -> None:
        '''Color of the halo (stroke) around text.'''
        raise NotImplementedError()
    
    @property
    def multipart_mode(self) -> aspose.gis.rendering.labelings.MultipartMode:
        '''Specifies rendering behavior for multipart geometries. Default is :py:attr:`aspose.gis.rendering.labelings.MultipartMode.ALL`.'''
        raise NotImplementedError()
    
    @multipart_mode.setter
    def multipart_mode(self, value : aspose.gis.rendering.labelings.MultipartMode) -> None:
        '''Specifies rendering behavior for multipart geometries. Default is :py:attr:`aspose.gis.rendering.labelings.MultipartMode.ALL`.'''
        raise NotImplementedError()
    
    @property
    def placement(self) -> aspose.gis.rendering.labelings.LabelPlacement:
        '''Label placement specifies how labels are placed relatively to feature\'s geometries.'''
        raise NotImplementedError()
    
    @placement.setter
    def placement(self, value : aspose.gis.rendering.labelings.LabelPlacement) -> None:
        '''Label placement specifies how labels are placed relatively to feature\'s geometries.'''
        raise NotImplementedError()
    
    @property
    def priority(self) -> int:
        '''Indicates priority of this label in case if it overlaps with another label. The label with lower priority is not rendered.
        Default is 1000.'''
        raise NotImplementedError()
    
    @priority.setter
    def priority(self, value : int) -> None:
        '''Indicates priority of this label in case if it overlaps with another label. The label with lower priority is not rendered.
        Default is 1000.'''
        raise NotImplementedError()
    

class FontStyle:
    '''Specifies style to be applied to text.'''
    
    REGULAR : FontStyle
    '''Regular text.'''
    BOLD : FontStyle
    '''Bold text.'''
    ITALIC : FontStyle
    '''Italic text.'''
    UNDERLINE : FontStyle
    '''Underlined text.'''
    STRIKEOUT : FontStyle
    '''Text with a line through the middle.'''

class LineLabelAlignment:
    '''Specifies how the label is aligned with the line.'''
    
    HORIZONTAL : LineLabelAlignment
    '''No alignment. The label is horizontal.'''
    PARALLEL : LineLabelAlignment
    '''The label is parallel to the line.'''
    CURVED : LineLabelAlignment
    '''The label follows the shape of the line.'''

class MultipartMode:
    '''Specifies how labels are rendered for features that contain multipart geometries.'''
    
    ALL : MultipartMode
    '''Places a label near each part of the geometry as long as there is space near the part.'''
    ANY : MultipartMode
    '''Places one label for the whole geometry.'''
    LARGEST : MultipartMode
    '''Places a label for the largest part of the geometry as long as there is space for the label.'''

