# *****************************************************************************
#
#   Part of the py5 library
#   Copyright (C) 2020-2025 Jim Schmitz
#
#   This library is free software: you can redistribute it and/or modify it
#   under the terms of the GNU Lesser General Public License as published by
#   the Free Software Foundation, either version 2.1 of the License, or (at
#   your option) any later version.
#
#   This library is distributed in the hope that it will be useful, but
#   WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
#   General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with this library. If not, see <https://www.gnu.org/licenses/>.
#
# *****************************************************************************
from __future__ import annotations

import functools
import weakref
from typing import overload  # noqa

import jpype
from jpype import JArray, JException, JString  # noqa

from . import spelling
from .decorators import _ret_str  # noqa
from .shape import Py5Shape, _return_py5shape  # noqa


def _return_py5font(f):
    @functools.wraps(f)
    def decorated(self_, *args):
        return Py5Font(f(self_, *args))

    return decorated


def _load_py5font(f):
    @functools.wraps(f)
    def decorated(self_, *args):
        # TODO: for load_font this prints a Java exception to strerr if the file cannot be found or read
        try:
            ret = f(self_, *args)
        except JException as e:
            msg = e.message()
        else:
            if ret is None:
                msg = "font file is missing or inaccessible."
            else:
                return Py5Font(ret)
        raise RuntimeError(
            "cannot load font file " + str(args[0]) + ". error message: " + msg
        )

    return decorated


def _return_list_str(f):
    @functools.wraps(f)
    def decorated(cls_, *args):
        return [str(x) for x in f(cls_, *args) or []]

    return decorated


class Py5Font:
    """Py5Font is the font class for py5.

    Underlying Processing class: PFont.PFont

    Notes
    -----

    Py5Font is the font class for py5. To create a font to use with py5, use
    `create_font_file()`. This will create a font in the format py5 requires. Py5
    displays fonts using the .vlw font format, which uses images for each letter,
    rather than defining them through vector data. The `load_font()` function
    constructs a new font and `text_font()` makes a font active. The
    `Py5Font.list()` method creates a list of the fonts installed on the computer,
    which is useful information to use with the `create_font()` function for
    dynamically converting fonts into a format to use with py5.

    To create a new font dynamically, use the `create_font()` function. Do not use
    the syntax `Py5Font()`."""

    _cls = jpype.JClass("processing.core.PFont")
    CHARSET = _cls.CHARSET

    _py5_object_cache = weakref.WeakSet()

    def __new__(cls, pfont):
        for o in cls._py5_object_cache:
            if pfont == o._instance:
                return o
        else:
            o = object.__new__(Py5Font)
            o._instance = pfont
            cls._py5_object_cache.add(o)
            return o

    def __str__(self) -> str:
        return (
            "Py5Font(font_name='"
            + self.get_name()
            + "', font_size="
            + str(self.get_size())
            + ")"
        )

    def __repr__(self) -> str:
        return self.__str__()

    def __getattr__(self, name):
        raise AttributeError(spelling.error_msg("Py5Font", name, self))

    def ascent(self) -> float:
        """Get the ascent of this font from the baseline.

        Underlying Processing method: PFont.ascent

        Notes
        -----

        Get the ascent of this font from the baseline. The value is based on a font of
        size 1. Multiply it by the font size to get the offset from the baseline.
        """
        return self._instance.ascent()

    def descent(self) -> float:
        """Get the descent of this font from the baseline.

        Underlying Processing method: PFont.descent

        Notes
        -----

        Get the descent of this font from the baseline. The value is based on a font of
        size 1. Multiply it by the font size to get the offset from the baseline.
        """
        return self._instance.descent()

    def get_default_size(self) -> int:
        """Get the font's size that will be used when `text_font()` is called.

        Underlying Processing method: PFont.getDefaultSize

        Notes
        -----

        Get the font's size that will be used when `text_font()` is called. When drawing
        with 2x pixel density, bitmap fonts in OpenGL need to be created at double the
        requested size. This ensures that they're shown at half on displays (so folks
        don't have to change their sketch code).
        """
        return self._instance.getDefaultSize()

    def get_glyph_count(self) -> int:
        """Get the number of glyphs contained in the font.

        Underlying Processing method: PFont.getGlyphCount

        Notes
        -----

        Get the number of glyphs contained in the font. This will be 0 if the font is a
        "lazy font" that creates glyphs as they are needed by the Sketch. This will be
        the case if the font was created with `create_font()` without using the
        `charset` parameter.
        """
        return self._instance.getGlyphCount()

    @_ret_str
    def get_name(self) -> str:
        """Get the font's name.

        Underlying Processing method: PFont.getName

        Notes
        -----

        Get the font's name.
        """
        return self._instance.getName()

    @_ret_str
    def get_post_script_name(self) -> str:
        """Get the font's postscript name.

        Underlying Processing method: PFont.getPostScriptName

        Notes
        -----

        Get the font's postscript name.
        """
        return self._instance.getPostScriptName()

    @overload
    def get_shape(self, ch: chr, /) -> Py5Shape:
        """Get a single character as a `Py5Shape` object.

        Underlying Processing method: PFont.getShape

        Methods
        -------

        You can use any of the following signatures:

         * get_shape(ch: chr, /) -> Py5Shape
         * get_shape(ch: chr, detail: float, /) -> Py5Shape

        Parameters
        ----------

        ch: chr
            single character

        detail: float
            level of shape detail

        Notes
        -----

        Get a single character as a `Py5Shape` object. Use the `detail` parameter to
        draw the shape with only straight line segments.

        Calling `Py5Shape.disable_style()` on the returned `Py5Shape` object seems to be
        necessary for these to be drawable.

        This method only works on fonts loaded with `create_font()`.
        """
        pass

    @overload
    def get_shape(self, ch: chr, detail: float, /) -> Py5Shape:
        """Get a single character as a `Py5Shape` object.

        Underlying Processing method: PFont.getShape

        Methods
        -------

        You can use any of the following signatures:

         * get_shape(ch: chr, /) -> Py5Shape
         * get_shape(ch: chr, detail: float, /) -> Py5Shape

        Parameters
        ----------

        ch: chr
            single character

        detail: float
            level of shape detail

        Notes
        -----

        Get a single character as a `Py5Shape` object. Use the `detail` parameter to
        draw the shape with only straight line segments.

        Calling `Py5Shape.disable_style()` on the returned `Py5Shape` object seems to be
        necessary for these to be drawable.

        This method only works on fonts loaded with `create_font()`.
        """
        pass

    @_return_py5shape
    def get_shape(self, *args):
        """Get a single character as a `Py5Shape` object.

        Underlying Processing method: PFont.getShape

        Methods
        -------

        You can use any of the following signatures:

         * get_shape(ch: chr, /) -> Py5Shape
         * get_shape(ch: chr, detail: float, /) -> Py5Shape

        Parameters
        ----------

        ch: chr
            single character

        detail: float
            level of shape detail

        Notes
        -----

        Get a single character as a `Py5Shape` object. Use the `detail` parameter to
        draw the shape with only straight line segments.

        Calling `Py5Shape.disable_style()` on the returned `Py5Shape` object seems to be
        necessary for these to be drawable.

        This method only works on fonts loaded with `create_font()`.
        """
        return self._instance.getShape(*args)

    def get_size(self) -> int:
        """Get the font's size.

        Underlying Processing method: PFont.getSize

        Notes
        -----

        Get the font's size.
        """
        return self._instance.getSize()

    def is_smooth(self) -> bool:
        """Boolean value reflecting if smoothing (anti-aliasing) was used when the font was
        created.

        Underlying Processing method: PFont.isSmooth

        Notes
        -----

        Boolean value reflecting if smoothing (anti-aliasing) was used when the font was
        created. By default, `create_font()` will use smoothing.
        """
        return self._instance.isSmooth()

    @classmethod
    @_return_list_str
    def list(cls) -> list[str]:
        """Gets a list of the fonts installed on the system.

        Underlying Processing method: PFont.list

        Notes
        -----

        Gets a list of the fonts installed on the system. The data is returned as a list
        of strings. This list provides the names of each font for input into
        `create_font()`, which allows py5 to dynamically format fonts.

        This works outside of a running Sketch.
        """
        return cls._cls.list()

    def width(self, c: chr, /) -> float:
        """Get the width of a character in this font.

        Underlying Processing method: PFont.width

        Parameters
        ----------

        c: chr
            single character

        Notes
        -----

        Get the width of a character in this font. The value is based on a font of size
        1. Multiply it by the font size to get the horizontal space of the character.

        This will return 0 if the character is not in the font's character set.
        """
        return self._instance.width(c)
