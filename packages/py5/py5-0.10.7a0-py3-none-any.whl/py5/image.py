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
from typing import Sequence, Union, overload  # noqa

from . import spelling
from .base import Py5Base
from .mixins import PixelPy5ImageMixin


def _return_py5image(f):
    @functools.wraps(f)
    def decorated(self_, *args):
        ret = f(self_, *args)
        if ret is None or isinstance(ret, int):
            return ret
        else:
            return Py5Image(ret)

    return decorated


class Py5Image(PixelPy5ImageMixin, Py5Base):
    """Datatype for storing images.

    Underlying Processing class: PImage.PImage

    Notes
    -----

    Datatype for storing images. Py5 can load `.gif`, `.jpg`, `.tga`, and `.png`
    images using the `load_image()` function. Py5 can also convert common Python
    image objects using the `convert_image()` function. Images may be displayed in
    2D and 3D space. The `Py5Image` class contains fields for the `Py5Image.width`
    and `Py5Image.height` of the image, as well as arrays called `Py5Image.pixels[]`
    and `Py5Image.np_pixels[]` that contain the values for every pixel in the image.
    The methods described below allow easy access to the image's pixels and alpha
    channel and simplify the process of compositing.

    Before using the `Py5Image.pixels[]` array, be sure to use the
    `Py5Image.load_pixels()` method on the image to make sure that the pixel data is
    properly loaded. Similarly, be sure to use the `Py5Image.load_np_pixels()`
    method on the image before using the `Py5Image.np_pixels[]` array.

    To create a new image, use the `create_image()` function. Do not use the syntax
    `Py5Image()`."""

    _py5_object_cache = weakref.WeakSet()

    def __new__(cls, pimage):
        for o in cls._py5_object_cache:
            if pimage == o._instance:
                return o
        else:
            o = object.__new__(Py5Image)
            cls._py5_object_cache.add(o)
            return o

    def __init__(self, pimage):
        if pimage == getattr(self, "_instance", None):
            # this is a cached Py5Image object, don't re-run __init__()
            return

        self._instance = pimage
        super().__init__(instance=pimage)

    def __str__(self) -> str:
        return (
            f"Py5Image(width="
            + str(self._get_width())
            + ", height="
            + str(self._get_height())
            + ")"
        )

    def __repr__(self) -> str:
        return self.__str__()

    def __getattr__(self, name):
        raise AttributeError(spelling.error_msg("Py5Image", name, self))

    ADD = 2
    ALPHA = 4
    ALPHA_MASK = -16777216
    ARGB = 2
    BICUBIC = 2
    BILINEAR = 1
    BLEND = 1
    BLUE_MASK = 255
    BLUR = 11
    BURN = 8192
    DARKEST = 16
    DIFFERENCE = 32
    DILATE = 18
    DODGE = 4096
    ERODE = 17
    EXCLUSION = 64
    GRAY = 12
    GREEN_MASK = 65280
    HARD_LIGHT = 1024
    HSB = 3
    INVERT = 13
    LIGHTEST = 8
    MULTIPLY = 128
    NEAREST_NEIGHBOR = 0
    OPAQUE = 14
    OVERLAY = 512
    POSTERIZE = 15
    RED_MASK = 16711680
    REPLACE = 0
    RGB = 1
    SCREEN = 256
    SOFT_LIGHT = 2048
    SUBTRACT = 4
    THRESHOLD = 16

    def _get_height(self) -> int:
        """The height of the image in units of pixels.

        Underlying Processing field: PImage.height

        Notes
        -----

        The height of the image in units of pixels.
        """
        return self._instance.height

    height: int = property(
        fget=_get_height,
        doc="""The height of the image in units of pixels.

        Underlying Processing field: PImage.height

        Notes
        -----

        The height of the image in units of pixels.""",
    )

    def _get_pixel_density(self) -> int:
        """Pixel density of the Py5Image object.

        Underlying Processing field: PImage.pixelDensity

        Notes
        -----

        Pixel density of the Py5Image object. This will always be equal to 1, even if
        the Sketch used `pixel_density()` to set the pixel density to a value greater
        than 1.
        """
        return self._instance.pixelDensity

    pixel_density: int = property(
        fget=_get_pixel_density,
        doc="""Pixel density of the Py5Image object.

        Underlying Processing field: PImage.pixelDensity

        Notes
        -----

        Pixel density of the Py5Image object. This will always be equal to 1, even if
        the Sketch used `pixel_density()` to set the pixel density to a value greater
        than 1.""",
    )

    def _get_pixel_height(self) -> int:
        """Height of the Py5Image object in pixels.

        Underlying Processing field: PImage.pixelHeight

        Notes
        -----

        Height of the Py5Image object in pixels. This will be the same as
        `Py5Image.height`, even if the Sketch used `pixel_density()` to set the pixel
        density to a value greater than 1.
        """
        return self._instance.pixelHeight

    pixel_height: int = property(
        fget=_get_pixel_height,
        doc="""Height of the Py5Image object in pixels.

        Underlying Processing field: PImage.pixelHeight

        Notes
        -----

        Height of the Py5Image object in pixels. This will be the same as
        `Py5Image.height`, even if the Sketch used `pixel_density()` to set the pixel
        density to a value greater than 1.""",
    )

    def _get_pixel_width(self) -> int:
        """Width of the Py5Image object in pixels.

        Underlying Processing field: PImage.pixelWidth

        Notes
        -----

        Width of the Py5Image object in pixels. This will be the same as
        `Py5Image.width`, even if the Sketch used `pixel_density()` to set the pixel
        density to a value greater than 1.
        """
        return self._instance.pixelWidth

    pixel_width: int = property(
        fget=_get_pixel_width,
        doc="""Width of the Py5Image object in pixels.

        Underlying Processing field: PImage.pixelWidth

        Notes
        -----

        Width of the Py5Image object in pixels. This will be the same as
        `Py5Image.width`, even if the Sketch used `pixel_density()` to set the pixel
        density to a value greater than 1.""",
    )

    def _get_width(self) -> int:
        """The width of the image in units of pixels.

        Underlying Processing field: PImage.width

        Notes
        -----

        The width of the image in units of pixels.
        """
        return self._instance.width

    width: int = property(
        fget=_get_width,
        doc="""The width of the image in units of pixels.

        Underlying Processing field: PImage.width

        Notes
        -----

        The width of the image in units of pixels.""",
    )

    @overload
    def blend(
        self,
        sx: int,
        sy: int,
        sw: int,
        sh: int,
        dx: int,
        dy: int,
        dw: int,
        dh: int,
        mode: int,
        /,
    ) -> None:
        """Blends a region of pixels into the image specified by the `img` parameter.

        Underlying Processing method: PImage.blend

        Methods
        -------

        You can use any of the following signatures:

         * blend(src: Py5Image, sx: int, sy: int, sw: int, sh: int, dx: int, dy: int, dw: int, dh: int, mode: int, /) -> None
         * blend(sx: int, sy: int, sw: int, sh: int, dx: int, dy: int, dw: int, dh: int, mode: int, /) -> None

        Parameters
        ----------

        dh: int
            destination image height

        dw: int
            destination image width

        dx: int
            x-coordinate of the destinations's upper left corner

        dy: int
            y-coordinate of the destinations's upper left corner

        mode: int
            Either BLEND, ADD, SUBTRACT, LIGHTEST, DARKEST, DIFFERENCE, EXCLUSION, MULTIPLY, SCREEN, OVERLAY, HARD_LIGHT, SOFT_LIGHT, DODGE, BURN

        sh: int
            source image height

        src: Py5Image
            an image variable referring to the source image

        sw: int
            source image width

        sx: int
            x-coordinate of the source's upper left corner

        sy: int
            y-coordinate of the source's upper left corner

        Notes
        -----

        Blends a region of pixels into the image specified by the `img` parameter. These
        copies utilize full alpha channel support and a choice of the following modes to
        blend the colors of source pixels (A) with the ones of pixels in the destination
        image (B):

        * BLEND: linear interpolation of colours: `C = A*factor + B`
        * ADD: additive blending with white clip: `C = min(A*factor + B, 255)`
        * SUBTRACT: subtractive blending with black clip: `C = max(B - A*factor, 0)`
        * DARKEST: only the darkest colour succeeds: `C = min(A*factor, B)`
        * LIGHTEST: only the lightest colour succeeds: `C = max(A*factor, B)`
        * DIFFERENCE: subtract colors from underlying image.
        * EXCLUSION: similar to DIFFERENCE, but less extreme.
        * MULTIPLY: Multiply the colors, result will always be darker.
        * SCREEN: Opposite multiply, uses inverse values of the colors.
        * OVERLAY: A mix of MULTIPLY and SCREEN. Multiplies dark values, and screens
        light values.
        * HARD_LIGHT: SCREEN when greater than 50% gray, MULTIPLY when lower.
        * SOFT_LIGHT: Mix of DARKEST and LIGHTEST.  Works like OVERLAY, but not as
        harsh.
        * DODGE: Lightens light tones and increases contrast, ignores darks. Called
        "Color Dodge" in Illustrator and Photoshop.
        * BURN: Darker areas are applied, increasing contrast, ignores lights. Called
        "Color Burn" in Illustrator and Photoshop.

        All modes use the alpha information (highest byte) of source image pixels as the
        blending factor. If the source and destination regions are different sizes, the
        image will be automatically resized to match the destination size. If the `src`
        parameter is not used, the display window is used as the source image.

        This function ignores `image_mode()`.
        """
        pass

    @overload
    def blend(
        self,
        src: Py5Image,
        sx: int,
        sy: int,
        sw: int,
        sh: int,
        dx: int,
        dy: int,
        dw: int,
        dh: int,
        mode: int,
        /,
    ) -> None:
        """Blends a region of pixels into the image specified by the `img` parameter.

        Underlying Processing method: PImage.blend

        Methods
        -------

        You can use any of the following signatures:

         * blend(src: Py5Image, sx: int, sy: int, sw: int, sh: int, dx: int, dy: int, dw: int, dh: int, mode: int, /) -> None
         * blend(sx: int, sy: int, sw: int, sh: int, dx: int, dy: int, dw: int, dh: int, mode: int, /) -> None

        Parameters
        ----------

        dh: int
            destination image height

        dw: int
            destination image width

        dx: int
            x-coordinate of the destinations's upper left corner

        dy: int
            y-coordinate of the destinations's upper left corner

        mode: int
            Either BLEND, ADD, SUBTRACT, LIGHTEST, DARKEST, DIFFERENCE, EXCLUSION, MULTIPLY, SCREEN, OVERLAY, HARD_LIGHT, SOFT_LIGHT, DODGE, BURN

        sh: int
            source image height

        src: Py5Image
            an image variable referring to the source image

        sw: int
            source image width

        sx: int
            x-coordinate of the source's upper left corner

        sy: int
            y-coordinate of the source's upper left corner

        Notes
        -----

        Blends a region of pixels into the image specified by the `img` parameter. These
        copies utilize full alpha channel support and a choice of the following modes to
        blend the colors of source pixels (A) with the ones of pixels in the destination
        image (B):

        * BLEND: linear interpolation of colours: `C = A*factor + B`
        * ADD: additive blending with white clip: `C = min(A*factor + B, 255)`
        * SUBTRACT: subtractive blending with black clip: `C = max(B - A*factor, 0)`
        * DARKEST: only the darkest colour succeeds: `C = min(A*factor, B)`
        * LIGHTEST: only the lightest colour succeeds: `C = max(A*factor, B)`
        * DIFFERENCE: subtract colors from underlying image.
        * EXCLUSION: similar to DIFFERENCE, but less extreme.
        * MULTIPLY: Multiply the colors, result will always be darker.
        * SCREEN: Opposite multiply, uses inverse values of the colors.
        * OVERLAY: A mix of MULTIPLY and SCREEN. Multiplies dark values, and screens
        light values.
        * HARD_LIGHT: SCREEN when greater than 50% gray, MULTIPLY when lower.
        * SOFT_LIGHT: Mix of DARKEST and LIGHTEST.  Works like OVERLAY, but not as
        harsh.
        * DODGE: Lightens light tones and increases contrast, ignores darks. Called
        "Color Dodge" in Illustrator and Photoshop.
        * BURN: Darker areas are applied, increasing contrast, ignores lights. Called
        "Color Burn" in Illustrator and Photoshop.

        All modes use the alpha information (highest byte) of source image pixels as the
        blending factor. If the source and destination regions are different sizes, the
        image will be automatically resized to match the destination size. If the `src`
        parameter is not used, the display window is used as the source image.

        This function ignores `image_mode()`.
        """
        pass

    def blend(self, *args):
        """Blends a region of pixels into the image specified by the `img` parameter.

        Underlying Processing method: PImage.blend

        Methods
        -------

        You can use any of the following signatures:

         * blend(src: Py5Image, sx: int, sy: int, sw: int, sh: int, dx: int, dy: int, dw: int, dh: int, mode: int, /) -> None
         * blend(sx: int, sy: int, sw: int, sh: int, dx: int, dy: int, dw: int, dh: int, mode: int, /) -> None

        Parameters
        ----------

        dh: int
            destination image height

        dw: int
            destination image width

        dx: int
            x-coordinate of the destinations's upper left corner

        dy: int
            y-coordinate of the destinations's upper left corner

        mode: int
            Either BLEND, ADD, SUBTRACT, LIGHTEST, DARKEST, DIFFERENCE, EXCLUSION, MULTIPLY, SCREEN, OVERLAY, HARD_LIGHT, SOFT_LIGHT, DODGE, BURN

        sh: int
            source image height

        src: Py5Image
            an image variable referring to the source image

        sw: int
            source image width

        sx: int
            x-coordinate of the source's upper left corner

        sy: int
            y-coordinate of the source's upper left corner

        Notes
        -----

        Blends a region of pixels into the image specified by the `img` parameter. These
        copies utilize full alpha channel support and a choice of the following modes to
        blend the colors of source pixels (A) with the ones of pixels in the destination
        image (B):

        * BLEND: linear interpolation of colours: `C = A*factor + B`
        * ADD: additive blending with white clip: `C = min(A*factor + B, 255)`
        * SUBTRACT: subtractive blending with black clip: `C = max(B - A*factor, 0)`
        * DARKEST: only the darkest colour succeeds: `C = min(A*factor, B)`
        * LIGHTEST: only the lightest colour succeeds: `C = max(A*factor, B)`
        * DIFFERENCE: subtract colors from underlying image.
        * EXCLUSION: similar to DIFFERENCE, but less extreme.
        * MULTIPLY: Multiply the colors, result will always be darker.
        * SCREEN: Opposite multiply, uses inverse values of the colors.
        * OVERLAY: A mix of MULTIPLY and SCREEN. Multiplies dark values, and screens
        light values.
        * HARD_LIGHT: SCREEN when greater than 50% gray, MULTIPLY when lower.
        * SOFT_LIGHT: Mix of DARKEST and LIGHTEST.  Works like OVERLAY, but not as
        harsh.
        * DODGE: Lightens light tones and increases contrast, ignores darks. Called
        "Color Dodge" in Illustrator and Photoshop.
        * BURN: Darker areas are applied, increasing contrast, ignores lights. Called
        "Color Burn" in Illustrator and Photoshop.

        All modes use the alpha information (highest byte) of source image pixels as the
        blending factor. If the source and destination regions are different sizes, the
        image will be automatically resized to match the destination size. If the `src`
        parameter is not used, the display window is used as the source image.

        This function ignores `image_mode()`.
        """
        return self._instance.blend(*args)

    @overload
    def copy(self) -> Py5Image:
        """Copies a region of pixels from one image into another.

        Underlying Processing method: PImage.copy

        Methods
        -------

        You can use any of the following signatures:

         * copy() -> Py5Image
         * copy(src: Py5Image, sx: int, sy: int, sw: int, sh: int, dx: int, dy: int, dw: int, dh: int, /) -> None
         * copy(sx: int, sy: int, sw: int, sh: int, dx: int, dy: int, dw: int, dh: int, /) -> None

        Parameters
        ----------

        dh: int
            destination image height

        dw: int
            destination image width

        dx: int
            x-coordinate of the destination's upper left corner

        dy: int
            y-coordinate of the destination's upper left corner

        sh: int
            source image height

        src: Py5Image
            a source image to copy pixels from

        sw: int
            source image width

        sx: int
            x-coordinate of the source's upper left corner

        sy: int
            y-coordinate of the source's upper left corner

        Notes
        -----

        Copies a region of pixels from one image into another. If the source and
        destination regions aren't the same size, it will automatically resize source
        pixels to fit the specified target region. No alpha information is used in the
        process, however if the source image has an alpha channel set, it will be copied
        as well.

        This function ignores `image_mode()`.

        If you want to create a new image with the contents of a rectangular region of a
        `Py5Image` object, check out the `Py5Image.get_pixels()` method, where x, y, w,
        h, are the position and dimensions of the area to be copied. It will return a
        `Py5Image` object.
        """
        pass

    @overload
    def copy(
        self, sx: int, sy: int, sw: int, sh: int, dx: int, dy: int, dw: int, dh: int, /
    ) -> None:
        """Copies a region of pixels from one image into another.

        Underlying Processing method: PImage.copy

        Methods
        -------

        You can use any of the following signatures:

         * copy() -> Py5Image
         * copy(src: Py5Image, sx: int, sy: int, sw: int, sh: int, dx: int, dy: int, dw: int, dh: int, /) -> None
         * copy(sx: int, sy: int, sw: int, sh: int, dx: int, dy: int, dw: int, dh: int, /) -> None

        Parameters
        ----------

        dh: int
            destination image height

        dw: int
            destination image width

        dx: int
            x-coordinate of the destination's upper left corner

        dy: int
            y-coordinate of the destination's upper left corner

        sh: int
            source image height

        src: Py5Image
            a source image to copy pixels from

        sw: int
            source image width

        sx: int
            x-coordinate of the source's upper left corner

        sy: int
            y-coordinate of the source's upper left corner

        Notes
        -----

        Copies a region of pixels from one image into another. If the source and
        destination regions aren't the same size, it will automatically resize source
        pixels to fit the specified target region. No alpha information is used in the
        process, however if the source image has an alpha channel set, it will be copied
        as well.

        This function ignores `image_mode()`.

        If you want to create a new image with the contents of a rectangular region of a
        `Py5Image` object, check out the `Py5Image.get_pixels()` method, where x, y, w,
        h, are the position and dimensions of the area to be copied. It will return a
        `Py5Image` object.
        """
        pass

    @overload
    def copy(
        self,
        src: Py5Image,
        sx: int,
        sy: int,
        sw: int,
        sh: int,
        dx: int,
        dy: int,
        dw: int,
        dh: int,
        /,
    ) -> None:
        """Copies a region of pixels from one image into another.

        Underlying Processing method: PImage.copy

        Methods
        -------

        You can use any of the following signatures:

         * copy() -> Py5Image
         * copy(src: Py5Image, sx: int, sy: int, sw: int, sh: int, dx: int, dy: int, dw: int, dh: int, /) -> None
         * copy(sx: int, sy: int, sw: int, sh: int, dx: int, dy: int, dw: int, dh: int, /) -> None

        Parameters
        ----------

        dh: int
            destination image height

        dw: int
            destination image width

        dx: int
            x-coordinate of the destination's upper left corner

        dy: int
            y-coordinate of the destination's upper left corner

        sh: int
            source image height

        src: Py5Image
            a source image to copy pixels from

        sw: int
            source image width

        sx: int
            x-coordinate of the source's upper left corner

        sy: int
            y-coordinate of the source's upper left corner

        Notes
        -----

        Copies a region of pixels from one image into another. If the source and
        destination regions aren't the same size, it will automatically resize source
        pixels to fit the specified target region. No alpha information is used in the
        process, however if the source image has an alpha channel set, it will be copied
        as well.

        This function ignores `image_mode()`.

        If you want to create a new image with the contents of a rectangular region of a
        `Py5Image` object, check out the `Py5Image.get_pixels()` method, where x, y, w,
        h, are the position and dimensions of the area to be copied. It will return a
        `Py5Image` object.
        """
        pass

    @_return_py5image
    def copy(self, *args):
        """Copies a region of pixels from one image into another.

        Underlying Processing method: PImage.copy

        Methods
        -------

        You can use any of the following signatures:

         * copy() -> Py5Image
         * copy(src: Py5Image, sx: int, sy: int, sw: int, sh: int, dx: int, dy: int, dw: int, dh: int, /) -> None
         * copy(sx: int, sy: int, sw: int, sh: int, dx: int, dy: int, dw: int, dh: int, /) -> None

        Parameters
        ----------

        dh: int
            destination image height

        dw: int
            destination image width

        dx: int
            x-coordinate of the destination's upper left corner

        dy: int
            y-coordinate of the destination's upper left corner

        sh: int
            source image height

        src: Py5Image
            a source image to copy pixels from

        sw: int
            source image width

        sx: int
            x-coordinate of the source's upper left corner

        sy: int
            y-coordinate of the source's upper left corner

        Notes
        -----

        Copies a region of pixels from one image into another. If the source and
        destination regions aren't the same size, it will automatically resize source
        pixels to fit the specified target region. No alpha information is used in the
        process, however if the source image has an alpha channel set, it will be copied
        as well.

        This function ignores `image_mode()`.

        If you want to create a new image with the contents of a rectangular region of a
        `Py5Image` object, check out the `Py5Image.get_pixels()` method, where x, y, w,
        h, are the position and dimensions of the area to be copied. It will return a
        `Py5Image` object.
        """
        return self._instance.copy(*args)

    @overload
    def apply_filter(self, kind: int, /) -> None:
        """Apply an image filter.

        Underlying Processing method: PImage.filter

        Methods
        -------

        You can use any of the following signatures:

         * apply_filter(kind: int, /) -> None
         * apply_filter(kind: int, param: float, /) -> None

        Parameters
        ----------

        kind: int
            Either THRESHOLD, GRAY, OPAQUE, INVERT, POSTERIZE, BLUR, ERODE, or DILATE

        param: float
            unique for each filter, see description

        Notes
        -----

        Apply an image filter.

        Filters the image as defined by one of the following modes:

        * THRESHOLD: Converts the image to black and white pixels depending if they are
        above or below the threshold defined by the level parameter. The parameter must
        be between 0.0 (black) and 1.0 (white). If no level is specified, 0.5 is used.
        * GRAY: Converts any colors in the image to grayscale equivalents. No parameter
        is used.
        * OPAQUE: Sets the alpha channel to entirely opaque. No parameter is used.
        * INVERT: Sets each pixel to its inverse value. No parameter is used.
        * POSTERIZE: Limits each channel of the image to the number of colors specified
        as the parameter. The parameter can be set to values between 2 and 255, but
        results are most noticeable in the lower ranges.
        * BLUR: Executes a Gaussian blur with the level parameter specifying the extent
        of the blurring. If no parameter is used, the blur is equivalent to Gaussian
        blur of radius 1. Larger values increase the blur.
        * ERODE: Reduces the light areas. No parameter is used.
        * DILATE: Increases the light areas. No parameter is used.
        """
        pass

    @overload
    def apply_filter(self, kind: int, param: float, /) -> None:
        """Apply an image filter.

        Underlying Processing method: PImage.filter

        Methods
        -------

        You can use any of the following signatures:

         * apply_filter(kind: int, /) -> None
         * apply_filter(kind: int, param: float, /) -> None

        Parameters
        ----------

        kind: int
            Either THRESHOLD, GRAY, OPAQUE, INVERT, POSTERIZE, BLUR, ERODE, or DILATE

        param: float
            unique for each filter, see description

        Notes
        -----

        Apply an image filter.

        Filters the image as defined by one of the following modes:

        * THRESHOLD: Converts the image to black and white pixels depending if they are
        above or below the threshold defined by the level parameter. The parameter must
        be between 0.0 (black) and 1.0 (white). If no level is specified, 0.5 is used.
        * GRAY: Converts any colors in the image to grayscale equivalents. No parameter
        is used.
        * OPAQUE: Sets the alpha channel to entirely opaque. No parameter is used.
        * INVERT: Sets each pixel to its inverse value. No parameter is used.
        * POSTERIZE: Limits each channel of the image to the number of colors specified
        as the parameter. The parameter can be set to values between 2 and 255, but
        results are most noticeable in the lower ranges.
        * BLUR: Executes a Gaussian blur with the level parameter specifying the extent
        of the blurring. If no parameter is used, the blur is equivalent to Gaussian
        blur of radius 1. Larger values increase the blur.
        * ERODE: Reduces the light areas. No parameter is used.
        * DILATE: Increases the light areas. No parameter is used.
        """
        pass

    def apply_filter(self, *args):
        """Apply an image filter.

        Underlying Processing method: PImage.filter

        Methods
        -------

        You can use any of the following signatures:

         * apply_filter(kind: int, /) -> None
         * apply_filter(kind: int, param: float, /) -> None

        Parameters
        ----------

        kind: int
            Either THRESHOLD, GRAY, OPAQUE, INVERT, POSTERIZE, BLUR, ERODE, or DILATE

        param: float
            unique for each filter, see description

        Notes
        -----

        Apply an image filter.

        Filters the image as defined by one of the following modes:

        * THRESHOLD: Converts the image to black and white pixels depending if they are
        above or below the threshold defined by the level parameter. The parameter must
        be between 0.0 (black) and 1.0 (white). If no level is specified, 0.5 is used.
        * GRAY: Converts any colors in the image to grayscale equivalents. No parameter
        is used.
        * OPAQUE: Sets the alpha channel to entirely opaque. No parameter is used.
        * INVERT: Sets each pixel to its inverse value. No parameter is used.
        * POSTERIZE: Limits each channel of the image to the number of colors specified
        as the parameter. The parameter can be set to values between 2 and 255, but
        results are most noticeable in the lower ranges.
        * BLUR: Executes a Gaussian blur with the level parameter specifying the extent
        of the blurring. If no parameter is used, the blur is equivalent to Gaussian
        blur of radius 1. Larger values increase the blur.
        * ERODE: Reduces the light areas. No parameter is used.
        * DILATE: Increases the light areas. No parameter is used.
        """
        return self._instance.filter(*args)

    @overload
    def get_pixels(self) -> Py5Image:
        """Reads the color of any pixel or grabs a section of an image.

        Underlying Processing method: PImage.get

        Methods
        -------

        You can use any of the following signatures:

         * get_pixels() -> Py5Image
         * get_pixels(x: int, y: int, /) -> int
         * get_pixels(x: int, y: int, w: int, h: int, /) -> Py5Image

        Parameters
        ----------

        h: int
            height of pixel rectangle to get

        w: int
            width of pixel rectangle to get

        x: int
            x-coordinate of the pixel

        y: int
            y-coordinate of the pixel

        Notes
        -----

        Reads the color of any pixel or grabs a section of an image. If no parameters
        are specified, the entire image is returned. Use the `x` and `y` parameters to
        get the value of one pixel. Get a section of the image by specifying additional
        `w` and `h` parameters. When getting an image, the `x` and `y` parameters define
        the coordinates for the upper-left corner of the returned image, regardless of
        the current `image_mode()`.

        If the pixel requested is outside of the image, black is returned. The numbers
        returned are scaled according to the current color ranges, but only `RGB` values
        are returned by this function. For example, even though you may have drawn a
        shape with `color_mode(HSB)`, the numbers returned will be in `RGB` format.

        Getting the color of a single pixel with `get_pixels(x, y)` is easy, but not as
        fast as grabbing the data directly from `Py5Image.pixels[]`. The equivalent
        statement to `get_pixels(x, y)` using `Py5Image.pixels[]` is
        `pixels[y*width+x]`. See the reference for `Py5Image.pixels[]` for more
        information.
        """
        pass

    @overload
    def get_pixels(self, x: int, y: int, /) -> int:
        """Reads the color of any pixel or grabs a section of an image.

        Underlying Processing method: PImage.get

        Methods
        -------

        You can use any of the following signatures:

         * get_pixels() -> Py5Image
         * get_pixels(x: int, y: int, /) -> int
         * get_pixels(x: int, y: int, w: int, h: int, /) -> Py5Image

        Parameters
        ----------

        h: int
            height of pixel rectangle to get

        w: int
            width of pixel rectangle to get

        x: int
            x-coordinate of the pixel

        y: int
            y-coordinate of the pixel

        Notes
        -----

        Reads the color of any pixel or grabs a section of an image. If no parameters
        are specified, the entire image is returned. Use the `x` and `y` parameters to
        get the value of one pixel. Get a section of the image by specifying additional
        `w` and `h` parameters. When getting an image, the `x` and `y` parameters define
        the coordinates for the upper-left corner of the returned image, regardless of
        the current `image_mode()`.

        If the pixel requested is outside of the image, black is returned. The numbers
        returned are scaled according to the current color ranges, but only `RGB` values
        are returned by this function. For example, even though you may have drawn a
        shape with `color_mode(HSB)`, the numbers returned will be in `RGB` format.

        Getting the color of a single pixel with `get_pixels(x, y)` is easy, but not as
        fast as grabbing the data directly from `Py5Image.pixels[]`. The equivalent
        statement to `get_pixels(x, y)` using `Py5Image.pixels[]` is
        `pixels[y*width+x]`. See the reference for `Py5Image.pixels[]` for more
        information.
        """
        pass

    @overload
    def get_pixels(self, x: int, y: int, w: int, h: int, /) -> Py5Image:
        """Reads the color of any pixel or grabs a section of an image.

        Underlying Processing method: PImage.get

        Methods
        -------

        You can use any of the following signatures:

         * get_pixels() -> Py5Image
         * get_pixels(x: int, y: int, /) -> int
         * get_pixels(x: int, y: int, w: int, h: int, /) -> Py5Image

        Parameters
        ----------

        h: int
            height of pixel rectangle to get

        w: int
            width of pixel rectangle to get

        x: int
            x-coordinate of the pixel

        y: int
            y-coordinate of the pixel

        Notes
        -----

        Reads the color of any pixel or grabs a section of an image. If no parameters
        are specified, the entire image is returned. Use the `x` and `y` parameters to
        get the value of one pixel. Get a section of the image by specifying additional
        `w` and `h` parameters. When getting an image, the `x` and `y` parameters define
        the coordinates for the upper-left corner of the returned image, regardless of
        the current `image_mode()`.

        If the pixel requested is outside of the image, black is returned. The numbers
        returned are scaled according to the current color ranges, but only `RGB` values
        are returned by this function. For example, even though you may have drawn a
        shape with `color_mode(HSB)`, the numbers returned will be in `RGB` format.

        Getting the color of a single pixel with `get_pixels(x, y)` is easy, but not as
        fast as grabbing the data directly from `Py5Image.pixels[]`. The equivalent
        statement to `get_pixels(x, y)` using `Py5Image.pixels[]` is
        `pixels[y*width+x]`. See the reference for `Py5Image.pixels[]` for more
        information.
        """
        pass

    @_return_py5image
    def get_pixels(self, *args):
        """Reads the color of any pixel or grabs a section of an image.

        Underlying Processing method: PImage.get

        Methods
        -------

        You can use any of the following signatures:

         * get_pixels() -> Py5Image
         * get_pixels(x: int, y: int, /) -> int
         * get_pixels(x: int, y: int, w: int, h: int, /) -> Py5Image

        Parameters
        ----------

        h: int
            height of pixel rectangle to get

        w: int
            width of pixel rectangle to get

        x: int
            x-coordinate of the pixel

        y: int
            y-coordinate of the pixel

        Notes
        -----

        Reads the color of any pixel or grabs a section of an image. If no parameters
        are specified, the entire image is returned. Use the `x` and `y` parameters to
        get the value of one pixel. Get a section of the image by specifying additional
        `w` and `h` parameters. When getting an image, the `x` and `y` parameters define
        the coordinates for the upper-left corner of the returned image, regardless of
        the current `image_mode()`.

        If the pixel requested is outside of the image, black is returned. The numbers
        returned are scaled according to the current color ranges, but only `RGB` values
        are returned by this function. For example, even though you may have drawn a
        shape with `color_mode(HSB)`, the numbers returned will be in `RGB` format.

        Getting the color of a single pixel with `get_pixels(x, y)` is easy, but not as
        fast as grabbing the data directly from `Py5Image.pixels[]`. The equivalent
        statement to `get_pixels(x, y)` using `Py5Image.pixels[]` is
        `pixels[y*width+x]`. See the reference for `Py5Image.pixels[]` for more
        information.
        """
        return self._instance.get(*args)

    def load_pixels(self) -> None:
        """Loads the pixel data for the image into its `Py5Image.pixels[]` array.

        Underlying Processing method: PImage.loadPixels

        Notes
        -----

        Loads the pixel data for the image into its `Py5Image.pixels[]` array. This
        function must always be called before reading from or writing to
        `Py5Image.pixels[]`.
        """
        return self._instance.loadPixels()

    @overload
    def mask(self, mask_array: Sequence[int], /) -> None:
        """Masks part of an image from displaying by loading another image and using it as
        an alpha channel.

        Underlying Processing method: PImage.mask

        Methods
        -------

        You can use any of the following signatures:

         * mask(img: Py5Image, /) -> None
         * mask(mask_array: Sequence[int], /) -> None

        Parameters
        ----------

        img: Py5Image
            image to use as the mask

        mask_array: Sequence[int]
            1D array of integers used as the alpha channel, needs to be the same length as the image's pixel array

        Notes
        -----

        Masks part of an image from displaying by loading another image and using it as
        an alpha channel. This mask image should only contain grayscale data, but only
        the blue color channel is used. The mask image needs to be the same size as the
        image to which it is applied.

        In addition to using a mask image, an integer array containing the alpha channel
        data can be specified directly. This method is useful for creating dynamically
        generated alpha masks. This array must be of the same length as the target
        image's pixels array and should contain only grayscale data of values between
        0-255.
        """
        pass

    @overload
    def mask(self, img: Py5Image, /) -> None:
        """Masks part of an image from displaying by loading another image and using it as
        an alpha channel.

        Underlying Processing method: PImage.mask

        Methods
        -------

        You can use any of the following signatures:

         * mask(img: Py5Image, /) -> None
         * mask(mask_array: Sequence[int], /) -> None

        Parameters
        ----------

        img: Py5Image
            image to use as the mask

        mask_array: Sequence[int]
            1D array of integers used as the alpha channel, needs to be the same length as the image's pixel array

        Notes
        -----

        Masks part of an image from displaying by loading another image and using it as
        an alpha channel. This mask image should only contain grayscale data, but only
        the blue color channel is used. The mask image needs to be the same size as the
        image to which it is applied.

        In addition to using a mask image, an integer array containing the alpha channel
        data can be specified directly. This method is useful for creating dynamically
        generated alpha masks. This array must be of the same length as the target
        image's pixels array and should contain only grayscale data of values between
        0-255.
        """
        pass

    def mask(self, *args):
        """Masks part of an image from displaying by loading another image and using it as
        an alpha channel.

        Underlying Processing method: PImage.mask

        Methods
        -------

        You can use any of the following signatures:

         * mask(img: Py5Image, /) -> None
         * mask(mask_array: Sequence[int], /) -> None

        Parameters
        ----------

        img: Py5Image
            image to use as the mask

        mask_array: Sequence[int]
            1D array of integers used as the alpha channel, needs to be the same length as the image's pixel array

        Notes
        -----

        Masks part of an image from displaying by loading another image and using it as
        an alpha channel. This mask image should only contain grayscale data, but only
        the blue color channel is used. The mask image needs to be the same size as the
        image to which it is applied.

        In addition to using a mask image, an integer array containing the alpha channel
        data can be specified directly. This method is useful for creating dynamically
        generated alpha masks. This array must be of the same length as the target
        image's pixels array and should contain only grayscale data of values between
        0-255.
        """
        return self._instance.mask(*args)

    @overload
    def resize(self, w: int, h: int, /) -> None:
        """Resize the Py5Image object to a new height and width.

        Underlying Processing method: PImage.resize

        Methods
        -------

        You can use any of the following signatures:

         * resize(w: int, h: int, /) -> None
         * resize(w: int, h: int, interpolation_mode: int, /) -> None

        Parameters
        ----------

        h: int
            height to size image to

        interpolation_mode: int
            interpolation method for resize operation

        w: int
            width to size image to

        Notes
        -----

        Resize the Py5Image object to a new height and width. This will modify the
        Py5Image object in place, meaning that rather than returning a resized copy, it
        will modify your existing Py5Image object. If this isn't what you want, pair
        this method with `Py5Image.copy()`, as shown in the example.

        To make the image scale proportionally, use 0 as the value for either the `w` or
        `h` parameter.

        The default resize interpolation mode is `BILINEAR`. Alternatively you can use
        the `interpolation_mode` parameter to interpolate using the `NEAREST_NEIGHBOR`
        method, which is faster but yields lower quality results. You can also use
        `BICUBIC` interpolation, which is the most computationally intensive but looks
        the best, particularly for up-scaling operations.
        """
        pass

    @overload
    def resize(self, w: int, h: int, interpolation_mode: int, /) -> None:
        """Resize the Py5Image object to a new height and width.

        Underlying Processing method: PImage.resize

        Methods
        -------

        You can use any of the following signatures:

         * resize(w: int, h: int, /) -> None
         * resize(w: int, h: int, interpolation_mode: int, /) -> None

        Parameters
        ----------

        h: int
            height to size image to

        interpolation_mode: int
            interpolation method for resize operation

        w: int
            width to size image to

        Notes
        -----

        Resize the Py5Image object to a new height and width. This will modify the
        Py5Image object in place, meaning that rather than returning a resized copy, it
        will modify your existing Py5Image object. If this isn't what you want, pair
        this method with `Py5Image.copy()`, as shown in the example.

        To make the image scale proportionally, use 0 as the value for either the `w` or
        `h` parameter.

        The default resize interpolation mode is `BILINEAR`. Alternatively you can use
        the `interpolation_mode` parameter to interpolate using the `NEAREST_NEIGHBOR`
        method, which is faster but yields lower quality results. You can also use
        `BICUBIC` interpolation, which is the most computationally intensive but looks
        the best, particularly for up-scaling operations.
        """
        pass

    def resize(self, *args):
        """Resize the Py5Image object to a new height and width.

        Underlying Processing method: PImage.resize

        Methods
        -------

        You can use any of the following signatures:

         * resize(w: int, h: int, /) -> None
         * resize(w: int, h: int, interpolation_mode: int, /) -> None

        Parameters
        ----------

        h: int
            height to size image to

        interpolation_mode: int
            interpolation method for resize operation

        w: int
            width to size image to

        Notes
        -----

        Resize the Py5Image object to a new height and width. This will modify the
        Py5Image object in place, meaning that rather than returning a resized copy, it
        will modify your existing Py5Image object. If this isn't what you want, pair
        this method with `Py5Image.copy()`, as shown in the example.

        To make the image scale proportionally, use 0 as the value for either the `w` or
        `h` parameter.

        The default resize interpolation mode is `BILINEAR`. Alternatively you can use
        the `interpolation_mode` parameter to interpolate using the `NEAREST_NEIGHBOR`
        method, which is faster but yields lower quality results. You can also use
        `BICUBIC` interpolation, which is the most computationally intensive but looks
        the best, particularly for up-scaling operations.
        """
        return self._instance.resize(*args)

    @overload
    def set_pixels(self, x: int, y: int, c: int, /) -> None:
        """Changes the color of any pixel or writes an image directly into the Py5Image
        object.

        Underlying Processing method: PImage.set

        Methods
        -------

        You can use any of the following signatures:

         * set_pixels(x: int, y: int, c: int, /) -> None
         * set_pixels(x: int, y: int, img: Py5Image, /) -> None

        Parameters
        ----------

        c: int
            any color value

        img: Py5Image
            image to copy into the Py5Image object

        x: int
            x-coordinate of the pixel

        y: int
            y-coordinate of the pixel

        Notes
        -----

        Changes the color of any pixel or writes an image directly into the Py5Image
        object.

        The `x` and `y` parameters specify the pixel to change and the color parameter
        specifies the color value. The color parameter `c` is affected by the current
        color mode (the default is RGB values from 0 to 255). When setting an image, the
        `x` and `y` parameters define the coordinates for the upper-left corner of the
        image, regardless of the current `image_mode()`.

        Setting the color of a single pixel with `set_pixels(x, y)` is easy, but not as
        fast as putting the data directly into `Py5Image.pixels[]`. The equivalent
        statement to `set_pixels(x, y, 0)` using `Py5Image.pixels[]` is
        `pixels[y*py5.width+x] = 0`. See the reference for `Py5Image.pixels[]` for more
        information.
        """
        pass

    @overload
    def set_pixels(self, x: int, y: int, img: Py5Image, /) -> None:
        """Changes the color of any pixel or writes an image directly into the Py5Image
        object.

        Underlying Processing method: PImage.set

        Methods
        -------

        You can use any of the following signatures:

         * set_pixels(x: int, y: int, c: int, /) -> None
         * set_pixels(x: int, y: int, img: Py5Image, /) -> None

        Parameters
        ----------

        c: int
            any color value

        img: Py5Image
            image to copy into the Py5Image object

        x: int
            x-coordinate of the pixel

        y: int
            y-coordinate of the pixel

        Notes
        -----

        Changes the color of any pixel or writes an image directly into the Py5Image
        object.

        The `x` and `y` parameters specify the pixel to change and the color parameter
        specifies the color value. The color parameter `c` is affected by the current
        color mode (the default is RGB values from 0 to 255). When setting an image, the
        `x` and `y` parameters define the coordinates for the upper-left corner of the
        image, regardless of the current `image_mode()`.

        Setting the color of a single pixel with `set_pixels(x, y)` is easy, but not as
        fast as putting the data directly into `Py5Image.pixels[]`. The equivalent
        statement to `set_pixels(x, y, 0)` using `Py5Image.pixels[]` is
        `pixels[y*py5.width+x] = 0`. See the reference for `Py5Image.pixels[]` for more
        information.
        """
        pass

    def set_pixels(self, *args):
        """Changes the color of any pixel or writes an image directly into the Py5Image
        object.

        Underlying Processing method: PImage.set

        Methods
        -------

        You can use any of the following signatures:

         * set_pixels(x: int, y: int, c: int, /) -> None
         * set_pixels(x: int, y: int, img: Py5Image, /) -> None

        Parameters
        ----------

        c: int
            any color value

        img: Py5Image
            image to copy into the Py5Image object

        x: int
            x-coordinate of the pixel

        y: int
            y-coordinate of the pixel

        Notes
        -----

        Changes the color of any pixel or writes an image directly into the Py5Image
        object.

        The `x` and `y` parameters specify the pixel to change and the color parameter
        specifies the color value. The color parameter `c` is affected by the current
        color mode (the default is RGB values from 0 to 255). When setting an image, the
        `x` and `y` parameters define the coordinates for the upper-left corner of the
        image, regardless of the current `image_mode()`.

        Setting the color of a single pixel with `set_pixels(x, y)` is easy, but not as
        fast as putting the data directly into `Py5Image.pixels[]`. The equivalent
        statement to `set_pixels(x, y, 0)` using `Py5Image.pixels[]` is
        `pixels[y*py5.width+x] = 0`. See the reference for `Py5Image.pixels[]` for more
        information.
        """
        return self._instance.set(*args)

    @overload
    def update_pixels(self) -> None:
        """Updates the image with the data in its `Py5Image.pixels[]` array.

        Underlying Processing method: PImage.updatePixels

        Methods
        -------

        You can use any of the following signatures:

         * update_pixels() -> None
         * update_pixels(x: int, y: int, w: int, h: int, /) -> None

        Parameters
        ----------

        h: int
            height

        w: int
            width

        x: int
            x-coordinate of the upper-left corner

        y: int
            y-coordinate of the upper-left corner

        Notes
        -----

        Updates the image with the data in its `Py5Image.pixels[]` array. Use in
        conjunction with `Py5Image.load_pixels()`. If you're only reading pixels from
        the array, there's no need to call `update_pixels()`.
        """
        pass

    @overload
    def update_pixels(self, x: int, y: int, w: int, h: int, /) -> None:
        """Updates the image with the data in its `Py5Image.pixels[]` array.

        Underlying Processing method: PImage.updatePixels

        Methods
        -------

        You can use any of the following signatures:

         * update_pixels() -> None
         * update_pixels(x: int, y: int, w: int, h: int, /) -> None

        Parameters
        ----------

        h: int
            height

        w: int
            width

        x: int
            x-coordinate of the upper-left corner

        y: int
            y-coordinate of the upper-left corner

        Notes
        -----

        Updates the image with the data in its `Py5Image.pixels[]` array. Use in
        conjunction with `Py5Image.load_pixels()`. If you're only reading pixels from
        the array, there's no need to call `update_pixels()`.
        """
        pass

    def update_pixels(self, *args):
        """Updates the image with the data in its `Py5Image.pixels[]` array.

        Underlying Processing method: PImage.updatePixels

        Methods
        -------

        You can use any of the following signatures:

         * update_pixels() -> None
         * update_pixels(x: int, y: int, w: int, h: int, /) -> None

        Parameters
        ----------

        h: int
            height

        w: int
            width

        x: int
            x-coordinate of the upper-left corner

        y: int
            y-coordinate of the upper-left corner

        Notes
        -----

        Updates the image with the data in its `Py5Image.pixels[]` array. Use in
        conjunction with `Py5Image.load_pixels()`. If you're only reading pixels from
        the array, there's no need to call `update_pixels()`.
        """
        return self._instance.updatePixels(*args)
