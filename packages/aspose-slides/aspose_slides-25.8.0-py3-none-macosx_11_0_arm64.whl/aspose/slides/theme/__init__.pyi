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

class BaseOverrideThemeManager(BaseThemeManager):
    '''Base class for classes that provide access to different types of overriden themes.'''
    def create_theme_effective(self) -> aspose.slides.theme.IThemeEffectiveData:
        '''Returns the theme object.'''
        ...

    def apply_color_scheme(self, scheme: aspose.slides.theme.IExtraColorScheme) -> None:
        '''Applies extra color scheme to a slide.'''
        ...

    @property
    def override_theme(self) -> aspose.slides.theme.IOverrideTheme:
        ...

    @override_theme.setter
    def override_theme(self, value: aspose.slides.theme.IOverrideTheme):
        ...

    @property
    def is_override_theme_enabled(self) -> bool:
        ...

    ...

class BaseThemeManager:
    '''Base class for classes that provide access to different types of themes.'''
    ...

class ChartThemeManager(BaseOverrideThemeManager):
    '''Provides access to chart theme overriden.'''
    def create_theme_effective(self) -> aspose.slides.theme.IThemeEffectiveData:
        '''Returns the theme object.'''
        ...

    def apply_color_scheme(self, scheme: aspose.slides.theme.IExtraColorScheme) -> None:
        '''Applies extra color scheme to a slide.'''
        ...

    @property
    def override_theme(self) -> aspose.slides.theme.IOverrideTheme:
        ...

    @override_theme.setter
    def override_theme(self, value: aspose.slides.theme.IOverrideTheme):
        ...

    @property
    def is_override_theme_enabled(self) -> bool:
        ...

    ...

class ColorScheme:
    '''Stores theme-defined colors.'''
    @property
    def dark1(self) -> aspose.slides.IColorFormat:
        '''First dark color in the scheme.
                    Read-only :py:class:`aspose.slides.IColorFormat`.'''
        ...

    @property
    def light1(self) -> aspose.slides.IColorFormat:
        '''First light color in the scheme.
                    Read-only :py:class:`aspose.slides.IColorFormat`.'''
        ...

    @property
    def dark2(self) -> aspose.slides.IColorFormat:
        '''Second dark color in the scheme.
                    Read-only :py:class:`aspose.slides.IColorFormat`.'''
        ...

    @property
    def light2(self) -> aspose.slides.IColorFormat:
        '''Second light color in the scheme.
                    Read-only :py:class:`aspose.slides.IColorFormat`.'''
        ...

    @property
    def accent1(self) -> aspose.slides.IColorFormat:
        '''First accent color in the scheme.
                    Read-only :py:class:`aspose.slides.IColorFormat`.'''
        ...

    @property
    def accent2(self) -> aspose.slides.IColorFormat:
        '''Second accent color in the scheme.
                    Read-only :py:class:`aspose.slides.IColorFormat`.'''
        ...

    @property
    def accent3(self) -> aspose.slides.IColorFormat:
        '''Third accent color in the scheme.
                    Read-only :py:class:`aspose.slides.IColorFormat`.'''
        ...

    @property
    def accent4(self) -> aspose.slides.IColorFormat:
        '''Fourth accent color in the scheme.
                    Read-only :py:class:`aspose.slides.IColorFormat`.'''
        ...

    @property
    def accent5(self) -> aspose.slides.IColorFormat:
        '''Fifth accent color in the scheme.
                    Read-only :py:class:`aspose.slides.IColorFormat`.'''
        ...

    @property
    def accent6(self) -> aspose.slides.IColorFormat:
        '''Sixth accent color in the scheme.
                    Read-only :py:class:`aspose.slides.IColorFormat`.'''
        ...

    @property
    def hyperlink(self) -> aspose.slides.IColorFormat:
        '''Color for the hyperlinks.
                    Read-only :py:class:`aspose.slides.IColorFormat`.'''
        ...

    @property
    def followed_hyperlink(self) -> aspose.slides.IColorFormat:
        ...

    @property
    def slide(self) -> aspose.slides.IBaseSlide:
        '''Returns the parent slide.
                    Read-only :py:class:`aspose.slides.IBaseSlide`.'''
        ...

    @property
    def presentation(self) -> aspose.slides.IPresentation:
        '''Returns the parent presentation.
                    Read-only :py:class:`aspose.slides.IPresentation`.'''
        ...

    ...

class EffectStyle:
    '''Represents an effect style.'''
    @property
    def effect_format(self) -> aspose.slides.IEffectFormat:
        ...

    @property
    def three_d_format(self) -> aspose.slides.IThreeDFormat:
        ...

    ...

class EffectStyleCollection:
    '''Represents a collection of effect styles.'''
    @property
    def as_i_collection(self) -> list:
        ...

    @property
    def as_i_enumerable(self) -> collections.abc.Iterable:
        ...

    def __getitem__(self, key: int) -> aspose.slides.theme.IEffectStyle
        '''Returns an element at specified position.
                    Read-only :py:class:`aspose.slides.theme.EffectStyle`.'''
        ...

    ...

class ExtraColorScheme:
    '''Represents an additional color scheme which can be assigned to a slide.'''
    @property
    def name(self) -> str:
        '''Returns a name of this scheme.
                    Read-only :py:class:`str`.'''
        ...

    @property
    def color_scheme(self) -> aspose.slides.theme.IColorScheme:
        ...

    ...

class ExtraColorSchemeCollection:
    '''Represents a collection of additional color schemes.'''
    @property
    def as_i_collection(self) -> list:
        ...

    @property
    def as_i_enumerable(self) -> collections.abc.Iterable:
        ...

    def __getitem__(self, key: int) -> aspose.slides.theme.IExtraColorScheme
        '''Returns an color scheme by index.
                    Read-only :py:class:`aspose.slides.theme.ExtraColorScheme`.'''
        ...

    ...

class FillFormatCollection:
    '''Represents the collection of fill styles.'''
    @property
    def as_i_collection(self) -> list:
        ...

    @property
    def as_i_enumerable(self) -> collections.abc.Iterable:
        ...

    def __getitem__(self, key: int) -> aspose.slides.IFillFormat
        '''Gets the element at the specified index.
                    Read-only :py:class:`aspose.slides.IFillFormat`.'''
        ...

    ...

class FontScheme:
    '''Stores theme-defined fonts.'''
    @property
    def minor(self) -> aspose.slides.IFonts:
        '''Returns the fonts collection for a "body" part of the slide.
                    Read-only :py:class:`aspose.slides.IFonts`.'''
        ...

    @property
    def major(self) -> aspose.slides.IFonts:
        '''Returns the fonts collection for a "heading" part of the slide.
                    Read-only :py:class:`aspose.slides.IFonts`.'''
        ...

    @property
    def name(self) -> str:
        '''Returns the font scheme name.
                    Read/write :py:class:`str`.'''
        ...

    @name.setter
    def name(self, value: str):
        '''Returns the font scheme name.
                    Read/write :py:class:`str`.'''
        ...

    ...

class FormatScheme:
    '''Stores theme-defined formats for the shapes.'''
    @property
    def fill_styles(self) -> aspose.slides.theme.IFillFormatCollection:
        ...

    @property
    def line_styles(self) -> aspose.slides.theme.ILineFormatCollection:
        ...

    @property
    def effect_styles(self) -> aspose.slides.theme.IEffectStyleCollection:
        ...

    @property
    def background_fill_styles(self) -> aspose.slides.theme.IFillFormatCollection:
        ...

    @property
    def slide(self) -> aspose.slides.IBaseSlide:
        '''Returns the parent slide.
                    Read-only :py:class:`aspose.slides.IBaseSlide`.'''
        ...

    @property
    def presentation(self) -> aspose.slides.IPresentation:
        '''Returns the parent presentation.
                    Read-only :py:class:`aspose.slides.IPresentation`.'''
        ...

    ...

class IColorScheme:
    '''Stores theme-defined colors.'''
    @property
    def dark1(self) -> aspose.slides.IColorFormat:
        '''First dark color in the scheme.
                    Read-only :py:class:`aspose.slides.IColorFormat`.'''
        ...

    @property
    def light1(self) -> aspose.slides.IColorFormat:
        '''First light color in the scheme.
                    Read-only :py:class:`aspose.slides.IColorFormat`.'''
        ...

    @property
    def dark2(self) -> aspose.slides.IColorFormat:
        '''Second dark color in the scheme.
                    Read-only :py:class:`aspose.slides.IColorFormat`.'''
        ...

    @property
    def light2(self) -> aspose.slides.IColorFormat:
        '''Second light color in the scheme.
                    Read-only :py:class:`aspose.slides.IColorFormat`.'''
        ...

    @property
    def accent1(self) -> aspose.slides.IColorFormat:
        '''First accent color in the scheme.
                    Read-only :py:class:`aspose.slides.IColorFormat`.'''
        ...

    @property
    def accent2(self) -> aspose.slides.IColorFormat:
        '''Second accent color in the scheme.
                    Read-only :py:class:`aspose.slides.IColorFormat`.'''
        ...

    @property
    def accent3(self) -> aspose.slides.IColorFormat:
        '''Third accent color in the scheme.
                    Read-only :py:class:`aspose.slides.IColorFormat`.'''
        ...

    @property
    def accent4(self) -> aspose.slides.IColorFormat:
        '''Fourth accent color in the scheme.
                    Read-only :py:class:`aspose.slides.IColorFormat`.'''
        ...

    @property
    def accent5(self) -> aspose.slides.IColorFormat:
        '''Fifth accent color in the scheme.
                    Read-only :py:class:`aspose.slides.IColorFormat`.'''
        ...

    @property
    def accent6(self) -> aspose.slides.IColorFormat:
        '''Sixth accent color in the scheme.
                    Read-only :py:class:`aspose.slides.IColorFormat`.'''
        ...

    @property
    def hyperlink(self) -> aspose.slides.IColorFormat:
        '''Color for the hyperlinks.
                    Read-only :py:class:`aspose.slides.IColorFormat`.'''
        ...

    @property
    def followed_hyperlink(self) -> aspose.slides.IColorFormat:
        ...

    @property
    def as_i_slide_component(self) -> aspose.slides.ISlideComponent:
        ...

    ...

class IColorSchemeEffectiveData:
    '''Immutable object which contains effective color scheme properties.'''
    @property
    def dark1(self) -> aspose.pydrawing.Color:
        '''First dark color in the scheme.
                    Read-only :py:class:`aspose.pydrawing.Color`.'''
        ...

    @property
    def light1(self) -> aspose.pydrawing.Color:
        '''First light color in the scheme.
                    Read-only :py:class:`aspose.pydrawing.Color`.'''
        ...

    @property
    def dark2(self) -> aspose.pydrawing.Color:
        '''Second dark color in the scheme.
                    Read-only :py:class:`aspose.pydrawing.Color`.'''
        ...

    @property
    def light2(self) -> aspose.pydrawing.Color:
        '''Second light color in the scheme.
                    Read-only :py:class:`aspose.pydrawing.Color`.'''
        ...

    @property
    def accent1(self) -> aspose.pydrawing.Color:
        '''First accent color in the scheme.
                    Read-only :py:class:`aspose.pydrawing.Color`.'''
        ...

    @property
    def accent2(self) -> aspose.pydrawing.Color:
        '''Second accent color in the scheme.
                    Read-only :py:class:`aspose.pydrawing.Color`.'''
        ...

    @property
    def accent3(self) -> aspose.pydrawing.Color:
        '''Third accent color in the scheme.
                    Read-only :py:class:`aspose.pydrawing.Color`.'''
        ...

    @property
    def accent4(self) -> aspose.pydrawing.Color:
        '''Fourth accent color in the scheme.
                    Read-only :py:class:`aspose.pydrawing.Color`.'''
        ...

    @property
    def accent5(self) -> aspose.pydrawing.Color:
        '''Fifth accent color in the scheme.
                    Read-only :py:class:`aspose.pydrawing.Color`.'''
        ...

    @property
    def accent6(self) -> aspose.pydrawing.Color:
        '''Sixth accent color in the scheme.
                    Read-only :py:class:`aspose.pydrawing.Color`.'''
        ...

    @property
    def hyperlink(self) -> aspose.pydrawing.Color:
        '''Color for the hyperlinks.
                    Read-only :py:class:`aspose.pydrawing.Color`.'''
        ...

    @property
    def followed_hyperlink(self) -> aspose.pydrawing.Color:
        ...

    ...

class IEffectStyle:
    '''Represents an effect style.'''
    @property
    def effect_format(self) -> aspose.slides.IEffectFormat:
        ...

    @property
    def three_d_format(self) -> aspose.slides.IThreeDFormat:
        ...

    ...

class IEffectStyleCollection:
    '''Represents a collection of effect styles.'''
    @property
    def as_i_collection(self) -> list:
        ...

    @property
    def as_i_enumerable(self) -> collections.abc.Iterable:
        ...

    def __getitem__(self, key: int) -> aspose.slides.theme.IEffectStyle
        '''Returns an element at specified position.
                    Read-only :py:class:`aspose.slides.theme.IEffectStyle`.'''
        ...

    ...

class IEffectStyleCollectionEffectiveData:
    '''Immutable object that represents a readonly collection of effective effect styles.'''
    @property
    def as_i_collection(self) -> list:
        ...

    @property
    def as_i_enumerable(self) -> collections.abc.Iterable:
        ...

    def __getitem__(self, key: int) -> aspose.slides.theme.IEffectStyleEffectiveData
        '''Gets the element at the specified index.
                    Read-only :py:class:`aspose.slides.theme.IEffectStyleEffectiveData`.'''
        ...

    ...

class IEffectStyleEffectiveData:
    '''Immutable object which contains effective effect style properties.'''
    @property
    def effect_format(self) -> aspose.slides.IEffectFormatEffectiveData:
        ...

    @property
    def three_d_format(self) -> aspose.slides.IThreeDFormatEffectiveData:
        ...

    ...

class IExtraColorScheme:
    '''Represents an additional color scheme which can be assigned to a slide.'''
    @property
    def name(self) -> str:
        '''Returns a name of this scheme.
                    Read-only :py:class:`str`.'''
        ...

    @property
    def color_scheme(self) -> aspose.slides.theme.IColorScheme:
        ...

    ...

class IExtraColorSchemeCollection:
    '''Represents a collection of additional color schemes.'''
    @property
    def as_i_collection(self) -> list:
        ...

    @property
    def as_i_enumerable(self) -> collections.abc.Iterable:
        ...

    def __getitem__(self, key: int) -> aspose.slides.theme.IExtraColorScheme
        '''Returns an color scheme by index.
                    Read-only :py:class:`aspose.slides.theme.IExtraColorScheme`.'''
        ...

    ...

class IFillFormatCollection:
    '''Represents the collection of fill styles.'''
    @property
    def as_i_collection(self) -> list:
        ...

    @property
    def as_i_enumerable(self) -> collections.abc.Iterable:
        ...

    def __getitem__(self, key: int) -> aspose.slides.IFillFormat
        '''Gets the element at the specified index.
                    Read-only :py:class:`aspose.slides.IFillFormat`.'''
        ...

    ...

class IFillFormatCollectionEffectiveData:
    '''Immutable object that represents a readonly collection of effective fill formats.'''
    @property
    def as_i_collection(self) -> list:
        ...

    @property
    def as_i_enumerable(self) -> collections.abc.Iterable:
        ...

    def __getitem__(self, key: int) -> aspose.slides.IFillFormatEffectiveData
        '''Gets the element at the specified index.
                    Read-only :py:class:`aspose.slides.IFillFormatEffectiveData`.'''
        ...

    ...

class IFontScheme:
    '''Stores theme-defined fonts.'''
    @property
    def minor(self) -> aspose.slides.IFonts:
        '''Returns the fonts collection for a "body" part of the slide.
                    Read-only :py:class:`aspose.slides.IFonts`.'''
        ...

    @property
    def major(self) -> aspose.slides.IFonts:
        '''Returns the fonts collection for a "heading" part of the slide.
                    Read-only :py:class:`aspose.slides.IFonts`.'''
        ...

    @property
    def name(self) -> str:
        '''Returns the font scheme name.
                    Read/write :py:class:`str`.'''
        ...

    @name.setter
    def name(self, value: str):
        '''Returns the font scheme name.
                    Read/write :py:class:`str`.'''
        ...

    ...

class IFontSchemeEffectiveData:
    '''Immutable object which contains effective font scheme properties.'''
    @property
    def minor(self) -> aspose.slides.IFontsEffectiveData:
        '''Returns the fonts collection for a "body" part of the slide.
                    Read-only :py:class:`aspose.slides.IFontsEffectiveData`.'''
        ...

    @property
    def major(self) -> aspose.slides.IFontsEffectiveData:
        '''Returns the fonts collection for a "heading" part of the slide.
                    Read-only :py:class:`aspose.slides.IFontsEffectiveData`.'''
        ...

    @property
    def name(self) -> str:
        '''Returns the font scheme name.
                    Read-only :py:class:`str`.'''
        ...

    ...

class IFormatScheme:
    '''Stores theme-defined formats for the shapes.'''
    @property
    def fill_styles(self) -> aspose.slides.theme.IFillFormatCollection:
        ...

    @property
    def line_styles(self) -> aspose.slides.theme.ILineFormatCollection:
        ...

    @property
    def effect_styles(self) -> aspose.slides.theme.IEffectStyleCollection:
        ...

    @property
    def background_fill_styles(self) -> aspose.slides.theme.IFillFormatCollection:
        ...

    @property
    def as_i_slide_component(self) -> aspose.slides.ISlideComponent:
        ...

    ...

class IFormatSchemeEffectiveData:
    '''Immutable object which contains effective format scheme properties.'''
    def get_fill_styles(self, style_color: aspose.pydrawing.Color) -> aspose.slides.theme.IFillFormatCollectionEffectiveData:
        '''Returns a collection of theme defined fill styles.
        :param style_color: Color :py:class:`aspose.pydrawing.Color`
        :returns: Collection of effective fill formats :py:class:`aspose.slides.theme.IFillFormatCollectionEffectiveData`'''
        ...

    def get_line_styles(self, style_color: aspose.pydrawing.Color) -> aspose.slides.theme.ILineFormatCollectionEffectiveData:
        '''Returns a collection of theme defined line styles.
        :param style_color: Color :py:class:`aspose.pydrawing.Color`
        :returns: Collection of effective line formats :py:class:`aspose.slides.theme.ILineFormatCollectionEffectiveData`'''
        ...

    def get_effect_styles(self, style_color: aspose.pydrawing.Color) -> aspose.slides.theme.IEffectStyleCollectionEffectiveData:
        '''Returns a collection of theme defined effect styles.
        :param style_color: Color :py:class:`aspose.pydrawing.Color`
        :returns: Collection of effective effect styles :py:class:`aspose.slides.theme.IEffectStyleCollectionEffectiveData`'''
        ...

    def get_background_fill_styles(self, style_color: aspose.pydrawing.Color) -> aspose.slides.theme.IFillFormatCollectionEffectiveData:
        '''Returns a collection of theme defined background fill styles.
        :param style_color: Color :py:class:`aspose.pydrawing.Color`
        :returns: Collection of effective background fill formats :py:class:`aspose.slides.theme.IFillFormatCollectionEffectiveData`'''
        ...

    ...

class ILineFormatCollection:
    '''Represents the collection of line styles.'''
    @property
    def as_i_collection(self) -> list:
        ...

    @property
    def as_i_enumerable(self) -> collections.abc.Iterable:
        ...

    def __getitem__(self, key: int) -> aspose.slides.ILineFormat
        '''Gets the element at the specified index.
                    Read-only :py:class:`aspose.slides.ILineFormat`.'''
        ...

    ...

class ILineFormatCollectionEffectiveData:
    '''Immutable object that represents a readonly collection of effective line formats.'''
    @property
    def as_i_collection(self) -> list:
        ...

    @property
    def as_i_enumerable(self) -> collections.abc.Iterable:
        ...

    def __getitem__(self, key: int) -> aspose.slides.ILineFormatEffectiveData
        '''Gets the element at the specified index.
                    Read-only :py:class:`aspose.slides.ILineFormatEffectiveData`.'''
        ...

    ...

class IMasterTheme:
    '''Represents a master theme.'''
    @property
    def extra_color_schemes(self) -> aspose.slides.theme.IExtraColorSchemeCollection:
        ...

    @property
    def name(self) -> str:
        '''Returns the name of a theme.
                    Read/write :py:class:`str`.'''
        ...

    @name.setter
    def name(self, value: str):
        '''Returns the name of a theme.
                    Read/write :py:class:`str`.'''
        ...

    @property
    def as_i_theme(self) -> aspose.slides.theme.ITheme:
        ...

    ...

class IMasterThemeManager:
    '''Provides access to presentation master theme.'''
    @property
    def is_override_theme_enabled(self) -> bool:
        ...

    @is_override_theme_enabled.setter
    def is_override_theme_enabled(self, value: bool):
        ...

    @property
    def override_theme(self) -> aspose.slides.theme.IMasterTheme:
        ...

    @override_theme.setter
    def override_theme(self, value: aspose.slides.theme.IMasterTheme):
        ...

    @property
    def as_i_theme_manager(self) -> aspose.slides.theme.IThemeManager:
        ...

    ...

class IMasterThemeable:
    '''Represent master theme manager.'''
    @property
    def theme_manager(self) -> aspose.slides.theme.IMasterThemeManager:
        ...

    @property
    def as_i_themeable(self) -> aspose.slides.theme.IThemeable:
        ...

    ...

class IOverrideTheme:
    '''Represents a overriding theme.'''
    def init_color_scheme(self) -> None:
        '''Init ColorScheme with new object for overriding ColorScheme of InheritedTheme.'''
        ...

    def init_color_scheme_from(self, color_scheme: aspose.slides.theme.IColorScheme) -> None:
        '''Init ColorScheme with new object for overriding ColorScheme of InheritedTheme.
        :param color_scheme: Data to initialize from.'''
        ...

    def init_color_scheme_from_inherited(self) -> None:
        '''Init ColorScheme with new object for overriding ColorScheme of InheritedTheme. And initialize data of this new object with data of the ColorScheme of InheritedTheme.'''
        ...

    def init_font_scheme(self) -> None:
        '''Init FontScheme with new object for overriding FontScheme of InheritedTheme.'''
        ...

    def init_font_scheme_from(self, font_scheme: aspose.slides.theme.IFontScheme) -> None:
        '''Init FontScheme with new object for overriding FontScheme of InheritedTheme.
        :param font_scheme: Data to initialize from.'''
        ...

    def init_font_scheme_from_inherited(self) -> None:
        '''Init FontScheme with new object for overriding FontScheme of InheritedTheme. And initialize data of this new object with data of the FontScheme of InheritedTheme.'''
        ...

    def init_format_scheme(self) -> None:
        '''Init FormatScheme with new object for overriding FormatScheme of InheritedTheme.'''
        ...

    def init_format_scheme_from(self, format_scheme: aspose.slides.theme.IFormatScheme) -> None:
        '''Init FormatScheme with new object for overriding FormatScheme of InheritedTheme.
        :param format_scheme: Data to initialize from.'''
        ...

    def init_format_scheme_from_inherited(self) -> None:
        '''Init FormatScheme with new object for overriding FormatScheme of InheritedTheme. And initialize data of this new object with data of the FormatScheme of InheritedTheme.'''
        ...

    def clear(self) -> None:
        '''Set ColorScheme, FontScheme, FormatScheme to None to disable any overriding with this theme object.'''
        ...

    @property
    def is_empty(self) -> bool:
        ...

    @property
    def as_i_theme(self) -> aspose.slides.theme.ITheme:
        ...

    ...

class IOverrideThemeManager:
    '''Provides access to different types of overriden themes.'''
    @property
    def is_override_theme_enabled(self) -> bool:
        ...

    @property
    def override_theme(self) -> aspose.slides.theme.IOverrideTheme:
        ...

    @override_theme.setter
    def override_theme(self, value: aspose.slides.theme.IOverrideTheme):
        ...

    @property
    def as_i_theme_manager(self) -> aspose.slides.theme.IThemeManager:
        ...

    ...

class IOverrideThemeable:
    '''Represents override theme manager.'''
    @property
    def theme_manager(self) -> aspose.slides.theme.IOverrideThemeManager:
        ...

    @property
    def as_i_themeable(self) -> aspose.slides.theme.IThemeable:
        ...

    ...

class ITheme:
    '''Represents a theme.'''
    def get_effective(self) -> aspose.slides.theme.IThemeEffectiveData:
        '''Gets effective theme data with the inheritance applied.
        :returns: A :py:class:`aspose.slides.theme.IThemeEffectiveData`.'''
        ...

    @property
    def color_scheme(self) -> aspose.slides.theme.IColorScheme:
        ...

    @property
    def font_scheme(self) -> aspose.slides.theme.IFontScheme:
        ...

    @property
    def format_scheme(self) -> aspose.slides.theme.IFormatScheme:
        ...

    @property
    def as_i_presentation_component(self) -> aspose.slides.IPresentationComponent:
        ...

    ...

class IThemeEffectiveData:
    '''Immutable object which contains effective theme properties.'''
    def get_color_scheme(self, style_color: aspose.pydrawing.Color) -> aspose.slides.theme.IColorSchemeEffectiveData:
        '''Returns the color scheme.
        :param style_color: Color :py:class:`aspose.pydrawing.Color`
        :returns: Color scheme :py:class:`aspose.slides.theme.IColorSchemeEffectiveData`'''
        ...

    @property
    def font_scheme(self) -> aspose.slides.theme.IFontSchemeEffectiveData:
        ...

    @property
    def format_scheme(self) -> aspose.slides.theme.IFormatSchemeEffectiveData:
        ...

    ...

class IThemeManager:
    '''Represent theme properties.'''
    def create_theme_effective(self) -> aspose.slides.theme.IThemeEffectiveData:
        '''Returns the theme object.
        :returns: Theme object :py:class:`aspose.slides.theme.IThemeEffectiveData`'''
        ...

    def apply_color_scheme(self, scheme: aspose.slides.theme.IExtraColorScheme) -> None:
        '''Applies extra color scheme to a slide.
        :param scheme: Extra color scheme :py:class:`aspose.slides.theme.IExtraColorScheme`'''
        ...

    ...

class IThemeable:
    '''Represents objects that can be themed with :py:class:`aspose.slides.theme.ITheme`.'''
    def create_theme_effective(self) -> aspose.slides.theme.IThemeEffectiveData:
        '''Returns an effective theme for this themeable object.
        :returns: Effective theme :py:class:`aspose.slides.theme.IThemeEffectiveData`'''
        ...

    @property
    def as_i_slide_component(self) -> aspose.slides.ISlideComponent:
        ...

    ...

class LayoutSlideThemeManager(BaseOverrideThemeManager):
    '''Provides access to layout slide theme overriden.'''
    def create_theme_effective(self) -> aspose.slides.theme.IThemeEffectiveData:
        '''Returns the theme object.'''
        ...

    def apply_color_scheme(self, scheme: aspose.slides.theme.IExtraColorScheme) -> None:
        '''Applies extra color scheme to a slide.'''
        ...

    @property
    def override_theme(self) -> aspose.slides.theme.IOverrideTheme:
        ...

    @override_theme.setter
    def override_theme(self, value: aspose.slides.theme.IOverrideTheme):
        ...

    @property
    def is_override_theme_enabled(self) -> bool:
        ...

    ...

class LineFormatCollection:
    '''Represents the collection of line styles.'''
    @property
    def as_i_collection(self) -> list:
        ...

    @property
    def as_i_enumerable(self) -> collections.abc.Iterable:
        ...

    def __getitem__(self, key: int) -> aspose.slides.ILineFormat
        '''Gets the element at the specified index.
                    Read-only :py:class:`aspose.slides.ILineFormat`.'''
        ...

    ...

class MasterTheme(Theme):
    '''Represents a master theme.'''
    def get_effective(self) -> aspose.slides.theme.IThemeEffectiveData:
        '''Gets effective theme data with the inheritance applied.
        :returns: A :py:class:`aspose.slides.theme.IThemeEffectiveData`.'''
        ...

    @property
    def color_scheme(self) -> aspose.slides.theme.IColorScheme:
        ...

    @property
    def font_scheme(self) -> aspose.slides.theme.IFontScheme:
        ...

    @property
    def format_scheme(self) -> aspose.slides.theme.IFormatScheme:
        ...

    @property
    def presentation(self) -> aspose.slides.IPresentation:
        '''Returns the parent presentation.
                    Read-only :py:class:`aspose.slides.IPresentation`.'''
        ...

    @property
    def extra_color_schemes(self) -> aspose.slides.theme.IExtraColorSchemeCollection:
        ...

    @property
    def name(self) -> str:
        '''Returns the name of a theme.
                    Read/write :py:class:`str`.'''
        ...

    @name.setter
    def name(self, value: str):
        '''Returns the name of a theme.
                    Read/write :py:class:`str`.'''
        ...

    ...

class MasterThemeManager(BaseThemeManager):
    '''Provides access to presentation master theme.'''
    def create_theme_effective(self) -> aspose.slides.theme.IThemeEffectiveData:
        '''Returns the theme object.'''
        ...

    def apply_color_scheme(self, scheme: aspose.slides.theme.IExtraColorScheme) -> None:
        '''Applies extra color scheme to a slide.'''
        ...

    @property
    def override_theme(self) -> aspose.slides.theme.IMasterTheme:
        ...

    @override_theme.setter
    def override_theme(self, value: aspose.slides.theme.IMasterTheme):
        ...

    @property
    def is_override_theme_enabled(self) -> bool:
        ...

    @is_override_theme_enabled.setter
    def is_override_theme_enabled(self, value: bool):
        ...

    ...

class NotesSlideThemeManager(BaseOverrideThemeManager):
    '''Provides access to notes slide theme overriden.'''
    def create_theme_effective(self) -> aspose.slides.theme.IThemeEffectiveData:
        '''Returns the theme object.'''
        ...

    def apply_color_scheme(self, scheme: aspose.slides.theme.IExtraColorScheme) -> None:
        '''Applies extra color scheme to a slide.'''
        ...

    @property
    def override_theme(self) -> aspose.slides.theme.IOverrideTheme:
        ...

    @override_theme.setter
    def override_theme(self, value: aspose.slides.theme.IOverrideTheme):
        ...

    @property
    def is_override_theme_enabled(self) -> bool:
        ...

    ...

class OverrideTheme(Theme):
    '''Represents a overriding theme.'''
    def get_effective(self) -> aspose.slides.theme.IThemeEffectiveData:
        '''Gets effective theme data with the inheritance applied.
        :returns: A :py:class:`aspose.slides.theme.IThemeEffectiveData`.'''
        ...

    def init_color_scheme(self) -> None:
        '''Init ColorScheme with new object for overriding ColorScheme of InheritedTheme.'''
        ...

    def init_color_scheme_from(self, color_scheme: aspose.slides.theme.IColorScheme) -> None:
        '''Init ColorScheme with new object for overriding ColorScheme of InheritedTheme.
        :param color_scheme: Data to initialize from.'''
        ...

    def init_color_scheme_from_inherited(self) -> None:
        '''Init ColorScheme with new object for overriding ColorScheme of InheritedTheme. And initialize data of this new object with data of the ColorScheme of InheritedTheme.'''
        ...

    def init_font_scheme(self) -> None:
        '''Init FontScheme with new object for overriding FontScheme of InheritedTheme.'''
        ...

    def init_font_scheme_from(self, font_scheme: aspose.slides.theme.IFontScheme) -> None:
        '''Init FontScheme with new object for overriding FontScheme of InheritedTheme.
        :param font_scheme: Data to initialize from.'''
        ...

    def init_font_scheme_from_inherited(self) -> None:
        '''Init FontScheme with new object for overriding FontScheme of InheritedTheme. And initialize data of this new object with data of the FontScheme of InheritedTheme.'''
        ...

    def init_format_scheme(self) -> None:
        '''Init FormatScheme with new object for overriding FormatScheme of InheritedTheme.'''
        ...

    def init_format_scheme_from(self, format_scheme: aspose.slides.theme.IFormatScheme) -> None:
        '''Init FormatScheme with new object for overriding FormatScheme of InheritedTheme.
        :param format_scheme: Data to initialize from.'''
        ...

    def init_format_scheme_from_inherited(self) -> None:
        '''Init FormatScheme with new object for overriding FormatScheme of InheritedTheme. And initialize data of this new object with data of the FormatScheme of InheritedTheme.'''
        ...

    def clear(self) -> None:
        '''Set ColorScheme, FontScheme, FormatScheme to None to disable any overriding with this theme object.'''
        ...

    @property
    def color_scheme(self) -> aspose.slides.theme.IColorScheme:
        ...

    @property
    def font_scheme(self) -> aspose.slides.theme.IFontScheme:
        ...

    @property
    def format_scheme(self) -> aspose.slides.theme.IFormatScheme:
        ...

    @property
    def presentation(self) -> aspose.slides.IPresentation:
        '''Returns the parent presentation.
                    Read-only :py:class:`aspose.slides.IPresentation`.'''
        ...

    @property
    def is_empty(self) -> bool:
        ...

    ...

class SlideThemeManager(BaseOverrideThemeManager):
    '''Provides access to slide theme overriden.'''
    def create_theme_effective(self) -> aspose.slides.theme.IThemeEffectiveData:
        '''Returns the theme object.'''
        ...

    def apply_color_scheme(self, scheme: aspose.slides.theme.IExtraColorScheme) -> None:
        '''Applies extra color scheme to a slide.'''
        ...

    @property
    def override_theme(self) -> aspose.slides.theme.IOverrideTheme:
        ...

    @override_theme.setter
    def override_theme(self, value: aspose.slides.theme.IOverrideTheme):
        ...

    @property
    def is_override_theme_enabled(self) -> bool:
        ...

    ...

class Theme:
    '''Represents a theme.'''
    def get_effective(self) -> aspose.slides.theme.IThemeEffectiveData:
        '''Gets effective theme data with the inheritance applied.
        :returns: A :py:class:`aspose.slides.theme.IThemeEffectiveData`.'''
        ...

    @property
    def color_scheme(self) -> aspose.slides.theme.IColorScheme:
        ...

    @property
    def font_scheme(self) -> aspose.slides.theme.IFontScheme:
        ...

    @property
    def format_scheme(self) -> aspose.slides.theme.IFormatScheme:
        ...

    @property
    def presentation(self) -> aspose.slides.IPresentation:
        '''Returns the parent presentation.
                    Read-only :py:class:`aspose.slides.IPresentation`.'''
        ...

    ...

