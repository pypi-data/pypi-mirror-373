from typing import List, Optional, Dict, Iterable
import aspose.pycore
import aspose.pydrawing
import aspose.slides
import aspose.slides.ai
import aspose.slides.animation
import aspose.slides.charts
import aspose.slides.dom.ole
import aspose.slides.effects
import aspose.slides.excel
import aspose.slides.export
import aspose.slides.export.xaml
import aspose.slides.importing
import aspose.slides.ink
import aspose.slides.lowcode
import aspose.slides.mathtext
import aspose.slides.slideshow
import aspose.slides.smartart
import aspose.slides.spreadsheet
import aspose.slides.theme
import aspose.slides.util
import aspose.slides.vba
import aspose.slides.warnings

class ShapeUtil:
    '''Offer methods which helps to process shapes objects.'''
    @staticmethod
    def graphics_path_to_geometry_path(graphics_path: aspose.pydrawing.Drawing2D.GraphicsPath) -> aspose.slides.IGeometryPath:
        '''Converts a :py:class:`aspose.pydrawing.Drawing2D.GraphicsPath` to the :py:class:`aspose.slides.IGeometryPath`
        :param graphics_path: Graphics path
        :returns: Geometry path'''
        ...

    @staticmethod
    def geometry_path_to_graphics_path(geometry_path: aspose.slides.IGeometryPath) -> aspose.pydrawing.Drawing2D.GraphicsPath:
        '''Converts :py:class:`aspose.slides.IGeometryPath` to :py:class:`aspose.pydrawing.Drawing2D.GraphicsPath`.
                    
                    GraphicsPath can be transformed in a different ways using its convenient methods and then transformed back into
                    the :py:class:`aspose.slides.IGeometryPath` to use in :py:class:`aspose.slides.GeometryShape` via :py:func:`aspose.slides.util.ShapeUtil.graphics_path_to_geometry_path` method.
        :returns: Graphics path'''
        ...

    ...

class SlideUtil:
    '''Offer methods which help to search shapes and text in a presentation.'''
    @overload
    @staticmethod
    def find_shape(pres: aspose.slides.IPresentation, alt_text: str) -> aspose.slides.IShape:
        '''Find shape by alternative text in a PPTX presentation.
        :param pres: Scanned presentation.
        :param alt_text: Alternative text of a shape.
        :returns: Shape or None.'''
        ...

    @overload
    @staticmethod
    def find_shape(slide: aspose.slides.IBaseSlide, alt_text: str) -> aspose.slides.IShape:
        '''Find shape by alternative text on a slide in a PPTX presentation.
        :param slide: Scanned slide.
        :param alt_text: Alternative text of a shape.
        :returns: Shape or None.'''
        ...

    @overload
    @staticmethod
    def align_shapes(alignment_type: aspose.slides.ShapesAlignmentType, align_to_slide: bool, slide: aspose.slides.IBaseSlide) -> None:
        '''Changes the placement of all shapes on the slide. Aligns shapes to the margins or the edge of the slide
                    or align them relative to each other.
        :param alignment_type: Determines which type of alignment will be applied.
        :param align_to_slide: If true, shapes will be aligned relative to the slide edges.
        :param slide: Parent slide.'''
        ...

    @overload
    @staticmethod
    def align_shapes(alignment_type: aspose.slides.ShapesAlignmentType, align_to_slide: bool, slide: aspose.slides.IBaseSlide, shape_indexes: List[int]) -> None:
        '''Changes the placement of selected shapes on the slide. Aligns shapes to the margins or the edge of the slide
                     or align them relative to each other.
        :param alignment_type: Determines which type of alignment will be applied.
        :param align_to_slide: If true, shapes will be aligned relative to the slide edges.
        :param slide: Parent slide.
        :param shape_indexes: Indexes of shapes to be aligned.'''
        ...

    @overload
    @staticmethod
    def align_shapes(alignment_type: aspose.slides.ShapesAlignmentType, align_to_slide: bool, group_shape: aspose.slides.IGroupShape) -> None:
        '''Changes the placement of all shapes within group shape. Aligns shapes to the margins or the edge of the slide
                    or align them relative to each other.
        :param alignment_type: Determines which type of alignment will be applied.
        :param align_to_slide: If true, shapes will be aligned relative to the slide edges.
        :param group_shape: Parent group shape.'''
        ...

    @overload
    @staticmethod
    def align_shapes(alignment_type: aspose.slides.ShapesAlignmentType, align_to_slide: bool, group_shape: aspose.slides.IGroupShape, shape_indexes: List[int]) -> None:
        '''Changes the placement of selected shapes within group shape. Aligns shapes to the margins or the edge of the slide
                    or align them relative to each other.
        :param alignment_type: Determines which type of alignment will be applied.
        :param align_to_slide: If true, shapes will be aligned relative to the slide edges.
        :param group_shape: Parent group shape.
        :param shape_indexes: Indexes of shapes to be aligned.'''
        ...

    @staticmethod
    def find_shapes_by_placeholder_type(slide: aspose.slides.IBaseSlide, placeholder_type: aspose.slides.PlaceholderType) -> List[aspose.slides.IShape]:
        '''Searches for all shapes on the specified slide that match the given placeholder type.
        :param slide: The slide to search for shapes.
        :param placeholder_type: The type of placeholder to filter shapes by.
        :returns: An array of :py:class:`aspose.slides.IShape` objects that match the specified placeholder type.'''
        ...

    @staticmethod
    def find_and_replace_text(presentation: aspose.slides.IPresentation, with_masters: bool, find: str, replace: str, format: aspose.slides.PortionFormat) -> None:
        '''Finds and replaces text in presentation with given format
        :param presentation: Scanned presentation.
        :param with_masters: Determines whether master slides should be scanned.
        :param find: String value to find.
        :param replace: String value to replace.
        :param format: Format for replacing text portion. If None then will be used format of the first 
                    character of the found string'''
        ...

    @staticmethod
    def get_all_text_boxes(slide: aspose.slides.IBaseSlide) -> List[aspose.slides.ITextFrame]:
        '''Returns all text frames on a slide in a PPTX presentation.
        :param slide: Scanned slide.
        :returns: Array of :py:class:`aspose.slides.TextFrame` objects.'''
        ...

    @staticmethod
    def get_text_boxes_contains_text(slide: aspose.slides.IBaseSlide, text: str, check_placeholder_text: bool) -> List[aspose.slides.ITextFrame]:
        '''Returns all text frames on the specified slide that contain the given text.
        :param slide: The slide to search.
        :param text: The text to search for within text frames.
        :param check_placeholder_text: Indicates whether to include text frames that are empty, but whose placeholder text contains the search text.
        :returns: An array of :py:class:`aspose.slides.ITextFrame` objects that contain the specified text.'''
        ...

    @staticmethod
    def get_all_text_frames(pres: aspose.slides.IPresentation, with_masters: bool) -> List[aspose.slides.ITextFrame]:
        '''Returns all text frames in a PPTX presentation.
        :param pres: Scanned presentation.
        :param with_masters: Determines whether master slides should be scanned.
        :returns: Array of :py:class:`aspose.slides.TextFrame` objects.'''
        ...

    ...

