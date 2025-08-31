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

import tempfile
import threading
from io import BytesIO
from pathlib import Path
from typing import Union, overload  # noqa

import jpype
import numpy as np
import numpy.typing as npt
from PIL import Image
from PIL.Image import Image as PIL_Image

from .. import bridge
from ..decorators import _hex_converter

_Sketch = jpype.JClass("py5.core.Sketch")


class PixelArray:
    """The `pixels[]` array contains the values for all the pixels in the display
    window.

    Underlying Processing field: PApplet.pixels

    Notes
    -----

    The `pixels[]` array contains the values for all the pixels in the display
    window. These values are of the color datatype. This array is defined by the
    size of the display window. For example, if the window is 100 x 100 pixels,
    there will be 10,000 values and if the window is 200 x 300 pixels, there will be
    60,000 values. When the pixel density is set to higher than 1 with the
    `pixel_density()` function, these values will change. See the reference for
    `pixel_width` or `pixel_height` for more information.

    Before accessing this array, the data must loaded with the `load_pixels()`
    function. Failure to do so may result in a Java `NullPointerException`.
    Subsequent changes to the display window will not be reflected in `pixels` until
    `load_pixels()` is called again. After `pixels` has been modified, the
    `update_pixels()` function must be run to update the content of the display
    window."""

    def __init__(self, instance):
        self._instance = instance

    def __getitem__(self, index):
        if self._instance.pixels is None:
            raise RuntimeError(
                "Cannot get pixel colors because load_pixels() has not been called"
            )

        return self._instance.pixels[index]

    def __setitem__(self, index, val):
        if self._instance.pixels is None:
            raise RuntimeError(
                "Cannot set pixel colors because load_pixels() has not been called"
            )

        if (newval := _hex_converter(val)) is not None:
            val = newval

        self._instance.pixels[index] = val

    def __len__(self):
        if self._instance.pixels is None:
            raise RuntimeError(
                "Cannot get pixel length because load_pixels() has not been called"
            )

        return len(self._instance.pixels)


class PixelMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._instance = kwargs["instance"]
        self._np_pixels = None
        self.pixels = PixelArray(self._instance)

    def _replace_instance(self, new_instance):
        self._instance = new_instance
        super()._replace_instance(new_instance)

    def _init_np_pixels(self):
        width = self.pixel_width if hasattr(self, "pixel_width") else self.width
        height = self.pixel_height if hasattr(self, "pixel_height") else self.height
        self._py_bb = bytearray(width * height * 4)
        self._java_bb = jpype.nio.convertToDirectBuffer(self._py_bb)
        self._np_pixels = np.asarray(self._py_bb, dtype=np.uint8).reshape(
            height, width, 4
        )

    # *** BEGIN METHODS ***

    def load_np_pixels(self) -> None:
        """Loads the pixel data of the current display window into the `np_pixels[]` array.

        Notes
        -----

        Loads the pixel data of the current display window into the `np_pixels[]` array.
        This method must always be called before reading from or writing to
        `np_pixels[]`. Subsequent changes to the display window will not be reflected in
        `np_pixels[]` until `load_np_pixels()` is called again.

        The `load_np_pixels()` method is similar to `load_pixels()` in that
        `load_np_pixels()` must be called before reading from or writing to
        `np_pixels[]` just as `load_pixels()` must be called before reading from or
        writing to `pixels[]`.

        Note that `load_np_pixels()` will as a side effect call `load_pixels()`, so if
        your code needs to read `np_pixels[]` and `pixels[]` simultaneously, there is no
        need for a separate call to `load_pixels()`. However, be aware that modifying
        both `np_pixels[]` and `pixels[]` simultaneously will likely result in the
        updates to `pixels[]` being discarded."""
        if self._np_pixels is None:
            self._init_np_pixels()
        self._instance.loadPixels()
        self._java_bb.asIntBuffer().put(self._instance.pixels)

    def update_np_pixels(self) -> None:
        """Updates the display window with the data in the `np_pixels[]` array.

        Notes
        -----

        Updates the display window with the data in the `np_pixels[]` array. Use in
        conjunction with `load_np_pixels()`. If you're only reading pixels from the
        array, there's no need to call `update_np_pixels()` — updating is only necessary
        to apply changes.

        The `update_np_pixels()` method is similar to `update_pixels()` in that
        `update_np_pixels()` must be called after modifying `np_pixels[]` just as
        `update_pixels()` must be called after modifying `pixels[]`."""
        if self._np_pixels is None:
            self._init_np_pixels()
        self._java_bb.asIntBuffer().get(self._instance.pixels)
        self._instance.updatePixels()

    def _get_np_pixels(self) -> npt.NDArray[np.uint8]:
        """The `np_pixels[]` array contains the values for all the pixels in the display
        window.

        Notes
        -----

        The `np_pixels[]` array contains the values for all the pixels in the display
        window. Unlike the one dimensional array `pixels[]`, the `np_pixels[]` array
        organizes the color data in a 3 dimensional numpy array. The size of the array's
        dimensions are defined by the size of the display window. The first dimension is
        the height, the second is the width, and the third represents the color
        channels. The color channels are ordered alpha, red, green, blue (ARGB). Every
        value in `np_pixels[]` is an integer between 0 and 255.

        This numpy array is very similar to the image arrays used by other popular
        Python image libraries, but note that many of them will arrange the channels in
        a different order such as RGBA or BGR.

        When the pixel density is set to higher than 1 with the `pixel_density()`
        function, the size of `np_pixels[]`'s height and width dimensions will change.
        See the reference for `pixel_width` or `pixel_height` for more information.
        Nothing about `np_pixels[]` will change as a result of calls to `color_mode()`.

        Much like the `pixels[]` array, there are load and update methods that must be
        called before and after making changes to the data in `np_pixels[]`. Before
        accessing `np_pixels[]`, the data must be loaded with the `load_np_pixels()`
        method. If this is not done, `np_pixels` will be equal to `None` and your code
        will likely result in Python exceptions. After `np_pixels[]` has been modified,
        the `update_np_pixels()` method must be called to update the content of the
        display window.

        To set the entire contents of `np_pixels[]` to the contents of another properly
        sized numpy array, consider using `set_np_pixels()`.

        Look at the online "Numpy, Arrays, and Images" Python Ecosystem Integration
        tutorial for more information about how to make best use of `np_pixels[]`."""
        return self._np_pixels

    np_pixels: npt.NDArray[np.uint8] = property(
        fget=_get_np_pixels,
        doc="""The `np_pixels[]` array contains the values for all the pixels in the display
        window.

        Notes
        -----

        The `np_pixels[]` array contains the values for all the pixels in the display
        window. Unlike the one dimensional array `pixels[]`, the `np_pixels[]` array
        organizes the color data in a 3 dimensional numpy array. The size of the array's
        dimensions are defined by the size of the display window. The first dimension is
        the height, the second is the width, and the third represents the color
        channels. The color channels are ordered alpha, red, green, blue (ARGB). Every
        value in `np_pixels[]` is an integer between 0 and 255.

        This numpy array is very similar to the image arrays used by other popular
        Python image libraries, but note that many of them will arrange the channels in
        a different order such as RGBA or BGR.

        When the pixel density is set to higher than 1 with the `pixel_density()`
        function, the size of `np_pixels[]`'s height and width dimensions will change.
        See the reference for `pixel_width` or `pixel_height` for more information.
        Nothing about `np_pixels[]` will change as a result of calls to `color_mode()`.

        Much like the `pixels[]` array, there are load and update methods that must be
        called before and after making changes to the data in `np_pixels[]`. Before
        accessing `np_pixels[]`, the data must be loaded with the `load_np_pixels()`
        method. If this is not done, `np_pixels` will be equal to `None` and your code
        will likely result in Python exceptions. After `np_pixels[]` has been modified,
        the `update_np_pixels()` method must be called to update the content of the
        display window.

        To set the entire contents of `np_pixels[]` to the contents of another properly
        sized numpy array, consider using `set_np_pixels()`.

        Look at the online "Numpy, Arrays, and Images" Python Ecosystem Integration
        tutorial for more information about how to make best use of `np_pixels[]`.""",
    )

    def set_np_pixels(self, array: npt.NDArray[np.uint8], bands: str = "ARGB") -> None:
        """Set the entire contents of `np_pixels[]` to the contents of another properly
        sized and typed numpy array.

        Parameters
        ----------

        array: npt.NDArray[np.uint8]
            properly sized numpy array to be copied to np_pixels[]

        bands: str = "ARGB"
            color channels in the array's third dimension

        Notes
        -----

        Set the entire contents of `np_pixels[]` to the contents of another properly
        sized and typed numpy array. The size of `array`'s first and second dimensions
        must match the height and width of the Sketch window, respectively. The array's
        `dtype` must be `np.uint8`.

        The `bands` parameter is used to interpret the `array`'s color channel dimension
        (the array's third dimension). It can be one of `'L'` (single-channel
        grayscale), `'ARGB'`, `'RGB'`, or `'RGBA'`. If there is no alpha channel,
        `array` is assumed to have no transparency, but recall that the display window's
        pixels can never be transparent so any transparency in `array` will have no
        effect. If the `bands` parameter is `'L'`, `array`'s third dimension is
        optional.

        This method makes its own calls to `load_np_pixels()` and `update_np_pixels()`
        so there is no need to call either explicitly.

        This method exists because setting the array contents with the code
        `py5.np_pixels = array` will cause an error, while the correct syntax,
        `py5.np_pixels[:] = array`, might also be unintuitive for beginners."""
        bands = bands.upper()

        self.load_np_pixels()
        if bands == "L":
            self._np_pixels[:, :, 0] = 255
            self._np_pixels[:, :, 1:] = array[:, :, None] if array.ndim == 2 else array
        elif bands == "ARGB":
            self._np_pixels[:] = array[:, :, :4]
        elif bands == "RGB":
            self._np_pixels[:, :, 0] = 255
            self._np_pixels[:, :, 1:] = array[:, :, :3]
        elif bands == "RGBA":
            self._np_pixels[:, :, 0] = array[:, :, 3]
            self._np_pixels[:, :, 1:] = array[:, :, :3]
        elif bands == "BGR":
            self._np_pixels[:, :, 0] = 255
            self._np_pixels[:, :, 1:] = array[:, :, 2::-1]
        elif bands == "BGRA":
            self._np_pixels[:, :, 0] = array[:, :, 3]
            self._np_pixels[:, :, 1:] = array[:, :, 2::-1]
        else:
            raise RuntimeError(
                f"Unknown `bands` value '{bands}'. Supported values are 'L', 'ARGB', 'RGB', 'RGBA', 'BGR', and 'BGRA'."
            )
        self.update_np_pixels()

    @overload
    def get_np_pixels(
        self, *, bands: str = "ARGB", dst: npt.NDArray[np.uint8] = None
    ) -> npt.NDArray[np.uint8]:
        """Get the contents of `np_pixels[]` as a numpy array.

        Methods
        -------

        You can use any of the following signatures:

         * get_np_pixels(*, bands: str = "ARGB", dst: npt.NDArray[np.uint8] = None) -> npt.NDArray[np.uint8]
         * get_np_pixels(x: int, y: int, w: int, h: int, /, *, bands: str = "ARGB", dst: npt.NDArray[np.uint8] = None, ) -> npt.NDArray[np.uint8]

        Parameters
        ----------

        bands: str = "ARGB"
            color channels in output array

        dst: npt.NDArray[np.uint8] = None
            destination array to copy pixel data into

        h: int
            source height

        w: int
            source width

        x: int
            x-coordinate of the source's upper left corner

        y: int
            y-coordinate of the source's upper left corner

        Notes
        -----

        Get the contents of `np_pixels[]` as a numpy array. The returned numpy array can
        be the entirety of `np_pixels[]` or a rectangular subsection. Use the `x`, `y`,
        `h`, and `w` parameters to specify the bounds of a rectangular subsection.

        The `bands` parameter is used to determine the ordering of the returned numpy
        array's color channel. It can be one of `'L'` (single-channel grayscale),
        `'ARGB'`, `'RGB'`, or `'RGBA'`. If the `bands` parameter is `'L'`, the returned
        array will have two dimensions, and each pixel value will be calculated as
        `0.299 * red + 0.587 * green + 0.114 * blue`. The alpha channel will also be
        ignored. For all other `bands` parameter values, the returned array will have
        three dimensions, with the third dimension representing the different color
        channels specified by the `bands` value.

        The returned array will always be a copy of the data in `np_pixels[]` and not a
        view into that array or any other array. Use the `dst` parameter to provide the
        numpy array to copy the pixel data into. The provided array must be sized
        correctly. The array's `dtype` should `np.uint8`, but this isn't required."""
        pass

    @overload
    def get_np_pixels(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        /,
        *,
        bands: str = "ARGB",
        dst: npt.NDArray[np.uint8] = None,
    ) -> npt.NDArray[np.uint8]:
        """Get the contents of `np_pixels[]` as a numpy array.

        Methods
        -------

        You can use any of the following signatures:

         * get_np_pixels(*, bands: str = "ARGB", dst: npt.NDArray[np.uint8] = None) -> npt.NDArray[np.uint8]
         * get_np_pixels(x: int, y: int, w: int, h: int, /, *, bands: str = "ARGB", dst: npt.NDArray[np.uint8] = None, ) -> npt.NDArray[np.uint8]

        Parameters
        ----------

        bands: str = "ARGB"
            color channels in output array

        dst: npt.NDArray[np.uint8] = None
            destination array to copy pixel data into

        h: int
            source height

        w: int
            source width

        x: int
            x-coordinate of the source's upper left corner

        y: int
            y-coordinate of the source's upper left corner

        Notes
        -----

        Get the contents of `np_pixels[]` as a numpy array. The returned numpy array can
        be the entirety of `np_pixels[]` or a rectangular subsection. Use the `x`, `y`,
        `h`, and `w` parameters to specify the bounds of a rectangular subsection.

        The `bands` parameter is used to determine the ordering of the returned numpy
        array's color channel. It can be one of `'L'` (single-channel grayscale),
        `'ARGB'`, `'RGB'`, or `'RGBA'`. If the `bands` parameter is `'L'`, the returned
        array will have two dimensions, and each pixel value will be calculated as
        `0.299 * red + 0.587 * green + 0.114 * blue`. The alpha channel will also be
        ignored. For all other `bands` parameter values, the returned array will have
        three dimensions, with the third dimension representing the different color
        channels specified by the `bands` value.

        The returned array will always be a copy of the data in `np_pixels[]` and not a
        view into that array or any other array. Use the `dst` parameter to provide the
        numpy array to copy the pixel data into. The provided array must be sized
        correctly. The array's `dtype` should `np.uint8`, but this isn't required."""
        pass

    def get_np_pixels(self, *args, **kwargs) -> npt.NDArray[np.uint8]:
        """Get the contents of `np_pixels[]` as a numpy array.

        Methods
        -------

        You can use any of the following signatures:

         * get_np_pixels(*, bands: str = "ARGB", dst: npt.NDArray[np.uint8] = None) -> npt.NDArray[np.uint8]
         * get_np_pixels(x: int, y: int, w: int, h: int, /, *, bands: str = "ARGB", dst: npt.NDArray[np.uint8] = None, ) -> npt.NDArray[np.uint8]

        Parameters
        ----------

        bands: str = "ARGB"
            color channels in output array

        dst: npt.NDArray[np.uint8] = None
            destination array to copy pixel data into

        h: int
            source height

        w: int
            source width

        x: int
            x-coordinate of the source's upper left corner

        y: int
            y-coordinate of the source's upper left corner

        Notes
        -----

        Get the contents of `np_pixels[]` as a numpy array. The returned numpy array can
        be the entirety of `np_pixels[]` or a rectangular subsection. Use the `x`, `y`,
        `h`, and `w` parameters to specify the bounds of a rectangular subsection.

        The `bands` parameter is used to determine the ordering of the returned numpy
        array's color channel. It can be one of `'L'` (single-channel grayscale),
        `'ARGB'`, `'RGB'`, or `'RGBA'`. If the `bands` parameter is `'L'`, the returned
        array will have two dimensions, and each pixel value will be calculated as
        `0.299 * red + 0.587 * green + 0.114 * blue`. The alpha channel will also be
        ignored. For all other `bands` parameter values, the returned array will have
        three dimensions, with the third dimension representing the different color
        channels specified by the `bands` value.

        The returned array will always be a copy of the data in `np_pixels[]` and not a
        view into that array or any other array. Use the `dst` parameter to provide the
        numpy array to copy the pixel data into. The provided array must be sized
        correctly. The array's `dtype` should `np.uint8`, but this isn't required."""
        self.load_np_pixels()

        if len(args) == 4:
            x, y, w, h = args
        elif len(args) == 0:
            x, y, h, w = 0, 0, *self.np_pixels.shape[:2]
        else:
            raise TypeError(
                f"Received {len(args)} out of 4 positional arguments for x, y, w, and h."
            )

        bands = kwargs.get("bands", "ARGB").upper()
        dst = kwargs.get("dst", None)

        x_slice = slice(x, x + w)
        y_slice = slice(y, y + h)

        if bands == "L":
            pixels = (
                self._np_pixels[y_slice, x_slice][:, :, 1:] @ [0.299, 0.587, 0.114]
            ).astype(np.uint8)
        elif bands == "ARGB":
            pixels = self._np_pixels[y_slice, x_slice]
        elif bands == "RGB":
            pixels = self._np_pixels[y_slice, x_slice, 1:]
        elif bands == "RGBA":
            pixels = np.roll(self._np_pixels[y_slice, x_slice], -1, axis=2)
        elif bands == "BGR":
            pixels = self._np_pixels[y_slice, x_slice, 3:0:-1]
        elif bands == "BGRA":
            pixels = np.dstack(
                [
                    self._np_pixels[y_slice, x_slice, 3:0:-1],
                    self._np_pixels[y_slice, x_slice, 0],
                ]
            )
        else:
            raise RuntimeError(
                f"Unknown `bands` value '{bands}'. Supported values are 'L', 'ARGB', 'RGB', 'RGBA', 'BGR', and 'BGRA'."
            )

        if dst is not None:
            if dst.shape != pixels.shape:
                raise ValueError(
                    f"Destination array has shape {dst.shape} but expected {pixels.shape}"
                )
            else:
                dst[:] = pixels
                return dst
        else:
            return pixels if pixels.base is None else pixels.copy()

    @overload
    def to_pil(self) -> PIL_Image:
        """Get the Sketch drawing surface as a PIL Image object.

        Methods
        -------

        You can use any of the following signatures:

         * to_pil() -> PIL_Image
         * to_pil(x: int, y: int, w: int, h: int, /) -> PIL_Image

        Parameters
        ----------

        h: int
            source height

        w: int
            source width

        x: int
            x-coordinate of the source's upper left corner

        y: int
            y-coordinate of the source's upper left corner

        Notes
        -----

        Get the Sketch drawing surface as a PIL Image object. The returned PIL Image
        object can include the entirety of the Sketch drawing surface or a rectangular
        subsection. Use the `x`, `y`, `h`, and `w` parameters to specify the bounds of a
        rectangular subsection."""
        pass

    @overload
    def to_pil(self, x: int, y: int, w: int, h: int, /) -> PIL_Image:
        """Get the Sketch drawing surface as a PIL Image object.

        Methods
        -------

        You can use any of the following signatures:

         * to_pil() -> PIL_Image
         * to_pil(x: int, y: int, w: int, h: int, /) -> PIL_Image

        Parameters
        ----------

        h: int
            source height

        w: int
            source width

        x: int
            x-coordinate of the source's upper left corner

        y: int
            y-coordinate of the source's upper left corner

        Notes
        -----

        Get the Sketch drawing surface as a PIL Image object. The returned PIL Image
        object can include the entirety of the Sketch drawing surface or a rectangular
        subsection. Use the `x`, `y`, `h`, and `w` parameters to specify the bounds of a
        rectangular subsection."""
        pass

    def to_pil(self, *args) -> PIL_Image:
        """Get the Sketch drawing surface as a PIL Image object.

        Methods
        -------

        You can use any of the following signatures:

         * to_pil() -> PIL_Image
         * to_pil(x: int, y: int, w: int, h: int, /) -> PIL_Image

        Parameters
        ----------

        h: int
            source height

        w: int
            source width

        x: int
            x-coordinate of the source's upper left corner

        y: int
            y-coordinate of the source's upper left corner

        Notes
        -----

        Get the Sketch drawing surface as a PIL Image object. The returned PIL Image
        object can include the entirety of the Sketch drawing surface or a rectangular
        subsection. Use the `x`, `y`, `h`, and `w` parameters to specify the bounds of a
        rectangular subsection."""
        return Image.fromarray(self.get_np_pixels(*args, bands="RGBA"))

    def save(
        self,
        filename: Union[str, Path, BytesIO],
        *,
        format: str = None,
        drop_alpha: bool = True,
        use_thread: bool = False,
        **params,
    ) -> None:
        """Save the drawing surface to an image file.

        Parameters
        ----------

        drop_alpha: bool = True
            remove the alpha channel when saving the image

        filename: Union[str, Path, BytesIO]
            output filename

        format: str = None
            image format, if not determined from filename extension

        params
            keyword arguments to pass to the PIL.Image save method

        use_thread: bool = False
            write file in separate thread

        Notes
        -----

        Save the drawing surface to an image file. This method uses the Python library
        Pillow to write the image, so it can save images in any format that that library
        supports.

        Use the `drop_alpha` parameter to drop the alpha channel from the image. This
        defaults to `True`. Some image formats such as JPG do not support alpha
        channels, and Pillow will throw an error if you try to save an image with the
        alpha channel in that format.

        The `use_thread` parameter will save the image in a separate Python thread. This
        improves performance by returning before the image has actually been written to
        the file."""
        sketch_instance = (
            self._instance
            if isinstance(self._instance, _Sketch)
            else self._instance.parent
        )
        if (
            isinstance(self._instance, _Sketch)
            and bridge.check_run_method_callstack()
            and self._py5_bridge.current_running_method not in ["setup", "draw"]
        ):
            if (
                drop_alpha
                # and not use_thread  # ignore use_thread because the alternative is always slower
                and format is None
                and isinstance((filename_param := Path(str(filename))), (str, Path))
                and filename_param.suffix.lower() in [".jpg", ".jpeg", ".png"]
            ):
                self._instance.save(filename)
                return

            with tempfile.TemporaryDirectory() as td:
                temp_filename = Path(td) / "temp.png"
                self._instance.save(temp_filename)
                arr = np.asarray(Image.open(temp_filename))
                if not drop_alpha:
                    arr = np.dstack([arr, np.full(arr.shape[:2], 255, dtype=np.uint8)])
        else:
            if not isinstance(filename, BytesIO):
                filename = Path(str(sketch_instance.savePath(str(filename))))
            self.load_np_pixels()
            arr = (
                self.np_pixels[:, :, 1:]
                if drop_alpha
                else np.roll(self.np_pixels, -1, axis=2)
            )

        if use_thread:

            def _save(arr, filename, format, params):
                Image.fromarray(arr).save(filename, format=format, **params)

            t = threading.Thread(
                target=_save, args=(arr, filename, format, params), daemon=True
            )
            t.start()
        else:
            Image.fromarray(arr).save(filename, format=format, **params)

    # *** END METHODS ***


# NOTE: changes to the below method signatures will not update the reference docs automatically
# could also add this information to generator/reference.py but it is simpler to copy-paste from
# the Sketch doc files to the Py5Graphics and Py5Image doc files.
# Both of these classes are necessary so that the docstings will be correct.


class PixelPy5GraphicsMixin(PixelMixin):
    def load_np_pixels(self) -> None:
        """Loads the pixel data of the current Py5Graphics drawing surface into the
        `Py5Graphics.np_pixels[]` array.

        Notes
        -----

        Loads the pixel data of the current Py5Graphics drawing surface into the
        `Py5Graphics.np_pixels[]` array. This method must always be called before
        reading from or writing to `Py5Graphics.np_pixels[]`. It should only be used
        between calls to `Py5Graphics.begin_draw()` and `Py5Graphics.end_draw()`.
        Subsequent changes to the Py5Graphics drawing surface will not be reflected in
        `Py5Graphics.np_pixels[]` until `load_np_pixels()` is called again.

        The `load_np_pixels()` method is similar to `Py5Graphics.load_pixels()` in that
        `load_np_pixels()` must be called before reading from or writing to
        `Py5Graphics.np_pixels[]` just as `Py5Graphics.load_pixels()` must be called
        before reading from or writing to `Py5Graphics.pixels[]`.

        Note that `load_np_pixels()` will as a side effect call
        `Py5Graphics.load_pixels()`, so if your code needs to read
        `Py5Graphics.np_pixels[]` and `Py5Graphics.pixels[]` simultaneously, there is no
        need for a separate call to `Py5Graphics.load_pixels()`. However, be aware that
        modifying both `Py5Graphics.np_pixels[]` and `Py5Graphics.pixels[]`
        simultaneously will likely result in the updates to `Py5Graphics.pixels[]` being
        discarded.

        This method is the same as `load_np_pixels()` but linked to a `Py5Graphics`
        object."""
        return super().load_np_pixels()

    def update_np_pixels(self) -> None:
        """Updates the Py5Graphics drawing surface with the data in the
        `Py5Graphics.np_pixels[]` array.

        Notes
        -----

        Updates the Py5Graphics drawing surface with the data in the
        `Py5Graphics.np_pixels[]` array. Use in conjunction with
        `Py5Graphics.load_np_pixels()`. If you're only reading pixels from the array,
        there's no need to call `update_np_pixels()` — updating is only necessary to
        apply changes. Working with `Py5Graphics.np_pixels[]` can only be done between
        calls to `Py5Graphics.begin_draw()` and `Py5Graphics.end_draw()`.

        The `update_np_pixels()` method is similar to `Py5Graphics.update_pixels()` in
        that `update_np_pixels()` must be called after modifying
        `Py5Graphics.np_pixels[]` just as `Py5Graphics.update_pixels()` must be called
        after modifying `Py5Graphics.pixels[]`.

        This method is the same as `update_np_pixels()` but linked to a `Py5Graphics`
        object."""
        return super().update_np_pixels()

    def _get_np_pixels(self) -> npt.NDArray[np.uint8]:
        """The `np_pixels[]` array contains the values for all the pixels in the
        Py5Graphics drawing surface.

        Notes
        -----

        The `np_pixels[]` array contains the values for all the pixels in the
        Py5Graphics drawing surface. Unlike the one dimensional array
        `Py5Graphics.pixels[]`, the `np_pixels[]` array organizes the color data in a 3
        dimensional numpy array. The size of the array's dimensions are defined by the
        size of the Py5Graphics drawing surface. The first dimension is the height, the
        second is the width, and the third represents the color channels. The color
        channels are ordered alpha, red, green, blue (ARGB). Every value in
        `np_pixels[]` is an integer between 0 and 255.

        This numpy array is very similar to the image arrays used by other popular
        Python image libraries, but note that some of them like opencv will by default
        order the color channels as RGBA.

        When the pixel density is set to higher than 1 with the
        `Py5Graphics.pixel_density` function, the size of `np_pixels[]`'s height and
        width dimensions will change. See the reference for `Py5Graphics.pixel_width` or
        `Py5Graphics.pixel_height` for more information. Nothing about `np_pixels[]`
        will change as a result of calls to `Py5Graphics.color_mode()`.

        Much like the `Py5Graphics.pixels[]` array, there are load and update methods
        that must be called before and after making changes to the data in
        `np_pixels[]`. Before accessing `np_pixels[]`, the data must be loaded with the
        `Py5Graphics.load_np_pixels()` method. If this is not done, `np_pixels` will be
        equal to `None` and your code will likely result in Python exceptions. After
        `np_pixels[]` has been modified, the `Py5Graphics.update_np_pixels()` method
        must be called to update the content of the Py5Graphics drawing surface.

        Working with `Py5Graphics.np_pixels[]` can only be done between calls to
        `Py5Graphics.begin_draw()` and `Py5Graphics.end_draw()`.

        To set the entire contents of `np_pixels[]` to the contents of another properly
        sized numpy array, consider using `Py5Graphics.set_np_pixels()`.

        Look at the online "Numpy, Arrays, and Images" Python Ecosystem Integration
        tutorial for more information about how to make best use of `np_pixels[]`.

        This field is the same as `np_pixels[]` but linked to a `Py5Graphics` object."""
        return super()._get_np_pixels()

    np_pixels: npt.NDArray[np.uint8] = property(
        fget=_get_np_pixels,
        doc="""The `np_pixels[]` array contains the values for all the pixels in the
        Py5Graphics drawing surface.

        Notes
        -----

        The `np_pixels[]` array contains the values for all the pixels in the
        Py5Graphics drawing surface. Unlike the one dimensional array
        `Py5Graphics.pixels[]`, the `np_pixels[]` array organizes the color data in a 3
        dimensional numpy array. The size of the array's dimensions are defined by the
        size of the Py5Graphics drawing surface. The first dimension is the height, the
        second is the width, and the third represents the color channels. The color
        channels are ordered alpha, red, green, blue (ARGB). Every value in
        `np_pixels[]` is an integer between 0 and 255.

        This numpy array is very similar to the image arrays used by other popular
        Python image libraries, but note that some of them like opencv will by default
        order the color channels as RGBA.

        When the pixel density is set to higher than 1 with the
        `Py5Graphics.pixel_density` function, the size of `np_pixels[]`'s height and
        width dimensions will change. See the reference for `Py5Graphics.pixel_width` or
        `Py5Graphics.pixel_height` for more information. Nothing about `np_pixels[]`
        will change as a result of calls to `Py5Graphics.color_mode()`.

        Much like the `Py5Graphics.pixels[]` array, there are load and update methods
        that must be called before and after making changes to the data in
        `np_pixels[]`. Before accessing `np_pixels[]`, the data must be loaded with the
        `Py5Graphics.load_np_pixels()` method. If this is not done, `np_pixels` will be
        equal to `None` and your code will likely result in Python exceptions. After
        `np_pixels[]` has been modified, the `Py5Graphics.update_np_pixels()` method
        must be called to update the content of the Py5Graphics drawing surface.

        Working with `Py5Graphics.np_pixels[]` can only be done between calls to
        `Py5Graphics.begin_draw()` and `Py5Graphics.end_draw()`.

        To set the entire contents of `np_pixels[]` to the contents of another properly
        sized numpy array, consider using `Py5Graphics.set_np_pixels()`.

        Look at the online "Numpy, Arrays, and Images" Python Ecosystem Integration
        tutorial for more information about how to make best use of `np_pixels[]`.

        This field is the same as `np_pixels[]` but linked to a `Py5Graphics` object.""",
    )

    def set_np_pixels(self, array: npt.NDArray[np.uint8], bands: str = "ARGB") -> None:
        """Set the entire contents of `Py5Graphics.np_pixels[]` to the contents of another
        properly sized and typed numpy array.

        Parameters
        ----------

        array: npt.NDArray[np.uint8]
            properly sized numpy array to be copied to np_pixels[]

        bands: str = "ARGB"
            color channels in the array's third dimension

        Notes
        -----

        Set the entire contents of `Py5Graphics.np_pixels[]` to the contents of another
        properly sized and typed numpy array. The size of `array`'s first and second
        dimensions must match the height and width of the Py5Graphics drawing surface,
        respectively. The array's `dtype` must be `np.uint8`. This must be used after
        `Py5Graphics.begin_draw()` but can be used after `Py5Graphics.end_draw()`.

        The `bands` parameter is used to interpret the `array`'s color channel dimension
        (the array's third dimension). It can be one of `'L'` (single-channel
        grayscale), `'ARGB'`, `'RGB'`, or `'RGBA'`. If there is no alpha channel,
        `array` is assumed to have no transparency. Unlike the main drawing window, a
        Py5Graphics drawing surface's pixels can be transparent so using the alpha
        channel will work properly. If the `bands` parameter is `'L'`, `array`'s third
        dimension is optional.

        This method makes its own calls to `Py5Graphics.load_np_pixels()` and
        `Py5Graphics.update_np_pixels()` so there is no need to call either explicitly.

        This method exists because setting the array contents with the code `g.np_pixels
        = array` will cause an error, while the correct syntax, `g.np_pixels[:] =
        array`, might also be unintuitive for beginners.

        This method is the same as `set_np_pixels()` but linked to a `Py5Graphics`
        object."""
        return super().set_np_pixels(array, bands)

    @overload
    def get_np_pixels(
        self, *, bands: str = "ARGB", dst: npt.NDArray[np.uint8] = None
    ) -> npt.NDArray[np.uint8]:
        """Get the contents of `Py5Graphics.np_pixels[]` as a numpy array.

        Methods
        -------

        You can use any of the following signatures:

         * get_np_pixels(*, bands: str = "ARGB", dst: npt.NDArray[np.uint8] = None) -> npt.NDArray[np.uint8]
         * get_np_pixels(x: int, y: int, w: int, h: int, /, *, bands: str = "ARGB", dst: npt.NDArray[np.uint8] = None) -> npt.NDArray[np.uint8]

        Parameters
        ----------

        bands: str = "ARGB"
            color channels in output array

        dst: npt.NDArray[np.uint8] = None
            destination array to copy pixel data into

        h: int
            source height

        w: int
            source width

        x: int
            x-coordinate of the source's upper left corner

        y: int
            y-coordinate of the source's upper left corner

        Notes
        -----

        Get the contents of `Py5Graphics.np_pixels[]` as a numpy array. The returned
        numpy array can be the entirety of `Py5Graphics.np_pixels[]` or a rectangular
        subsection. Use the `x`, `y`, `h`, and `w` parameters to specify the bounds of a
        rectangular subsection.

        The `bands` parameter is used to determine the ordering of the returned numpy
        array's color channel. It can be one of `'L'` (single-channel grayscale),
        `'ARGB'`, `'RGB'`, or `'RGBA'`. If the `bands` parameter is `'L'`, the returned
        array will have two dimensions, and each pixel value will be calculated as
        `0.299 * red + 0.587 * green + 0.114 * blue`. The alpha channel will also be
        ignored. For all other `bands` parameter values, the returned array will have
        three dimensions, with the third dimension representing the different color
        channels specified by the `bands` value.

        The returned array will always be a copy of the data in
        `Py5Graphics.np_pixels[]` and not a view into that array or any other array. Use
        the `dst` parameter to provide the numpy array to copy the pixel data into. The
        provided array must be sized correctly. The array's `dtype` should `np.uint8`,
        but this isn't required.

        This method is the same as `get_np_pixels()` but linked to a `Py5Graphics`
        object."""
        pass

    @overload
    def get_np_pixels(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        /,
        *,
        bands: str = "ARGB",
        dst: npt.NDArray[np.uint8] = None,
    ) -> npt.NDArray[np.uint8]:
        """Get the contents of `Py5Graphics.np_pixels[]` as a numpy array.

        Methods
        -------

        You can use any of the following signatures:

         * get_np_pixels(*, bands: str = "ARGB", dst: npt.NDArray[np.uint8] = None) -> npt.NDArray[np.uint8]
         * get_np_pixels(x: int, y: int, w: int, h: int, /, *, bands: str = "ARGB", dst: npt.NDArray[np.uint8] = None) -> npt.NDArray[np.uint8]

        Parameters
        ----------

        bands: str = "ARGB"
            color channels in output array

        dst: npt.NDArray[np.uint8] = None
            destination array to copy pixel data into

        h: int
            source height

        w: int
            source width

        x: int
            x-coordinate of the source's upper left corner

        y: int
            y-coordinate of the source's upper left corner

        Notes
        -----

        Get the contents of `Py5Graphics.np_pixels[]` as a numpy array. The returned
        numpy array can be the entirety of `Py5Graphics.np_pixels[]` or a rectangular
        subsection. Use the `x`, `y`, `h`, and `w` parameters to specify the bounds of a
        rectangular subsection.

        The `bands` parameter is used to determine the ordering of the returned numpy
        array's color channel. It can be one of `'L'` (single-channel grayscale),
        `'ARGB'`, `'RGB'`, or `'RGBA'`. If the `bands` parameter is `'L'`, the returned
        array will have two dimensions, and each pixel value will be calculated as
        `0.299 * red + 0.587 * green + 0.114 * blue`. The alpha channel will also be
        ignored. For all other `bands` parameter values, the returned array will have
        three dimensions, with the third dimension representing the different color
        channels specified by the `bands` value.

        The returned array will always be a copy of the data in
        `Py5Graphics.np_pixels[]` and not a view into that array or any other array. Use
        the `dst` parameter to provide the numpy array to copy the pixel data into. The
        provided array must be sized correctly. The array's `dtype` should `np.uint8`,
        but this isn't required.

        This method is the same as `get_np_pixels()` but linked to a `Py5Graphics`
        object."""
        pass

    def get_np_pixels(self, *args, **kwargs) -> npt.NDArray[np.uint8]:
        """Get the contents of `Py5Graphics.np_pixels[]` as a numpy array.

        Methods
        -------

        You can use any of the following signatures:

         * get_np_pixels(*, bands: str = "ARGB", dst: npt.NDArray[np.uint8] = None) -> npt.NDArray[np.uint8]
         * get_np_pixels(x: int, y: int, w: int, h: int, /, *, bands: str = "ARGB", dst: npt.NDArray[np.uint8] = None) -> npt.NDArray[np.uint8]

        Parameters
        ----------

        bands: str = "ARGB"
            color channels in output array

        dst: npt.NDArray[np.uint8] = None
            destination array to copy pixel data into

        h: int
            source height

        w: int
            source width

        x: int
            x-coordinate of the source's upper left corner

        y: int
            y-coordinate of the source's upper left corner

        Notes
        -----

        Get the contents of `Py5Graphics.np_pixels[]` as a numpy array. The returned
        numpy array can be the entirety of `Py5Graphics.np_pixels[]` or a rectangular
        subsection. Use the `x`, `y`, `h`, and `w` parameters to specify the bounds of a
        rectangular subsection.

        The `bands` parameter is used to determine the ordering of the returned numpy
        array's color channel. It can be one of `'L'` (single-channel grayscale),
        `'ARGB'`, `'RGB'`, or `'RGBA'`. If the `bands` parameter is `'L'`, the returned
        array will have two dimensions, and each pixel value will be calculated as
        `0.299 * red + 0.587 * green + 0.114 * blue`. The alpha channel will also be
        ignored. For all other `bands` parameter values, the returned array will have
        three dimensions, with the third dimension representing the different color
        channels specified by the `bands` value.

        The returned array will always be a copy of the data in
        `Py5Graphics.np_pixels[]` and not a view into that array or any other array. Use
        the `dst` parameter to provide the numpy array to copy the pixel data into. The
        provided array must be sized correctly. The array's `dtype` should `np.uint8`,
        but this isn't required.

        This method is the same as `get_np_pixels()` but linked to a `Py5Graphics`
        object."""
        return super().get_np_pixels(*args, **kwargs)

    @overload
    def to_pil(self) -> PIL_Image:
        """Get the Py5Graphics drawing surface as a PIL Image object.

        Methods
        -------

        You can use any of the following signatures:

         * to_pil() -> PIL_Image
         * to_pil(x: int, y: int, w: int, h: int) -> PIL_Image

        Parameters
        ----------

        h: int
            source height

        w: int
            source width

        x: int
            x-coordinate of the source's upper left corner

        y: int
            y-coordinate of the source's upper left corner

        Notes
        -----

        Get the Py5Graphics drawing surface as a PIL Image object. The returned PIL
        Image object can include the entirety of the Py5Graphics drawing surface or a
        rectangular subsection. Use the `x`, `y`, `h`, and `w` parameters to specify the
        bounds of a rectangular subsection.

        This method is the same as `to_pil()` but linked to a `Py5Graphics` object."""
        pass

    @overload
    def to_pil(self, x: int, y: int, w: int, h: int, /) -> PIL_Image:
        """Get the Py5Graphics drawing surface as a PIL Image object.

        Methods
        -------

        You can use any of the following signatures:

         * to_pil() -> PIL_Image
         * to_pil(x: int, y: int, w: int, h: int) -> PIL_Image

        Parameters
        ----------

        h: int
            source height

        w: int
            source width

        x: int
            x-coordinate of the source's upper left corner

        y: int
            y-coordinate of the source's upper left corner

        Notes
        -----

        Get the Py5Graphics drawing surface as a PIL Image object. The returned PIL
        Image object can include the entirety of the Py5Graphics drawing surface or a
        rectangular subsection. Use the `x`, `y`, `h`, and `w` parameters to specify the
        bounds of a rectangular subsection.

        This method is the same as `to_pil()` but linked to a `Py5Graphics` object."""
        pass

    def to_pil(self, *args) -> PIL_Image:
        """Get the Py5Graphics drawing surface as a PIL Image object.

        Methods
        -------

        You can use any of the following signatures:

         * to_pil() -> PIL_Image
         * to_pil(x: int, y: int, w: int, h: int) -> PIL_Image

        Parameters
        ----------

        h: int
            source height

        w: int
            source width

        x: int
            x-coordinate of the source's upper left corner

        y: int
            y-coordinate of the source's upper left corner

        Notes
        -----

        Get the Py5Graphics drawing surface as a PIL Image object. The returned PIL
        Image object can include the entirety of the Py5Graphics drawing surface or a
        rectangular subsection. Use the `x`, `y`, `h`, and `w` parameters to specify the
        bounds of a rectangular subsection.

        This method is the same as `to_pil()` but linked to a `Py5Graphics` object."""
        return super().to_pil(*args)

    def save(
        self,
        filename: Union[str, Path, BytesIO],
        *,
        format: str = None,
        drop_alpha: bool = True,
        use_thread: bool = False,
        **params,
    ) -> None:
        """Save the Py5Graphics drawing surface to an image file.

        Parameters
        ----------

        drop_alpha: bool = True
            remove the alpha channel when saving the image

        filename: Union[str, Path, BytesIO]
            output filename

        format: str = None
            image format, if not determined from filename extension

        params
            keyword arguments to pass to the PIL.Image save method

        use_thread: bool = False
            write file in separate thread

        Notes
        -----

        Save the Py5Graphics drawing surface to an image file. This method uses the
        Python library Pillow to write the image, so it can save images in any format
        that that library supports.

        Use the `drop_alpha` parameter to drop the alpha channel from the image. This
        defaults to `True`. Some image formats such as JPG do not support alpha
        channels, and Pillow will throw an error if you try to save an image with the
        alpha channel in that format.

        The `use_thread` parameter will save the image in a separate Python thread. This
        improves performance by returning before the image has actually been written to
        the file.

        This method is the same as `save()` but linked to a `Py5Graphics` object. To see
        example code for how it can be used, see `save()`."""
        return super().save(
            filename,
            format=format,
            drop_alpha=drop_alpha,
            use_thread=use_thread,
            **params,
        )


class PixelPy5ImageMixin(PixelMixin):
    def load_np_pixels(self) -> None:
        """Loads the pixel data of the image into the `Py5Image.np_pixels[]` array.

        Notes
        -----

        Loads the pixel data of the image into the `Py5Image.np_pixels[]` array. This
        method must always be called before reading from or writing to
        `Py5Image.np_pixels[]`. Subsequent changes to the image will not be reflected in
        `Py5Image.np_pixels[]` until `py5image_load_np_pixels()` is called again.

        The `load_np_pixels()` method is similar to `Py5Image.load_pixels()` in that
        `load_np_pixels()` must be called before reading from or writing to
        `Py5Image.np_pixels[]` just as `Py5Image.load_pixels()` must be called before
        reading from or writing to `Py5Image.pixels[]`.

        Note that `load_np_pixels()` will as a side effect call
        `Py5Image.load_pixels()`, so if your code needs to read `Py5Image.np_pixels[]`
        and `Py5Image.pixels[]` simultaneously, there is no need for a separate call to
        `Py5Image.load_pixels()`. However, be aware that modifying both
        `Py5Image.np_pixels[]` and `Py5Image.pixels[]` simultaneously will likely result
        in the updates to `Py5Image.pixels[]` being discarded."""
        return super().load_np_pixels()

    def update_np_pixels(self) -> None:
        """Updates the image with the data in the `Py5Image.np_pixels[]` array.

        Notes
        -----

        Updates the image with the data in the `Py5Image.np_pixels[]` array. Use in
        conjunction with `Py5Image.load_np_pixels()`. If you're only reading pixels from
        the array, there's no need to call `update_np_pixels()` — updating is only
        necessary to apply changes.

        The `update_np_pixels()` method is similar to `Py5Image.update_pixels()` in that
        `update_np_pixels()` must be called after modifying `Py5Image.np_pixels[]` just
        as `Py5Image.update_pixels()` must be called after modifying
        `Py5Image.pixels[]`."""
        return super().update_np_pixels()

    def _get_np_pixels(self) -> npt.NDArray[np.uint8]:
        """The `np_pixels[]` array contains the values for all the pixels in the image.

        Notes
        -----

        The `np_pixels[]` array contains the values for all the pixels in the image.
        Unlike the one dimensional array `Py5Image.pixels[]`, the `np_pixels[]` array
        organizes the color data in a 3 dimensional numpy array. The size of the array's
        dimensions are defined by the size of the image. The first dimension is the
        height, the second is the width, and the third represents the color channels.
        The color channels are ordered alpha, red, green, blue (ARGB). Every value in
        `np_pixels[]` is an integer between 0 and 255.

        This numpy array is very similar to the image arrays used by other popular
        Python image libraries, but note that some of them like opencv will by default
        order the color channels as RGBA.

        Much like the `Py5Image.pixels[]` array, there are load and update methods that
        must be called before and after making changes to the data in `np_pixels[]`.
        Before accessing `np_pixels[]`, the data must be loaded with the
        `Py5Image.load_np_pixels()` method. If this is not done, `np_pixels` will be
        equal to `None` and your code will likely result in Python exceptions. After
        `np_pixels[]` has been modified, the `Py5Image.update_np_pixels()` method must
        be called to update the content of the display window.

        To set the entire contents of `np_pixels[]` to the contents of another equally
        sized numpy array, consider using `Py5Image.set_np_pixels()`.

        Look at the online "Numpy, Arrays, and Images" Python Ecosystem Integration
        tutorial for more information about how to make best use of `np_pixels[]`."""
        return super()._get_np_pixels()

    np_pixels: npt.NDArray[np.uint8] = property(
        fget=_get_np_pixels,
        doc="""The `np_pixels[]` array contains the values for all the pixels in the image.

        Notes
        -----

        The `np_pixels[]` array contains the values for all the pixels in the image.
        Unlike the one dimensional array `Py5Image.pixels[]`, the `np_pixels[]` array
        organizes the color data in a 3 dimensional numpy array. The size of the array's
        dimensions are defined by the size of the image. The first dimension is the
        height, the second is the width, and the third represents the color channels.
        The color channels are ordered alpha, red, green, blue (ARGB). Every value in
        `np_pixels[]` is an integer between 0 and 255.

        This numpy array is very similar to the image arrays used by other popular
        Python image libraries, but note that some of them like opencv will by default
        order the color channels as RGBA.

        Much like the `Py5Image.pixels[]` array, there are load and update methods that
        must be called before and after making changes to the data in `np_pixels[]`.
        Before accessing `np_pixels[]`, the data must be loaded with the
        `Py5Image.load_np_pixels()` method. If this is not done, `np_pixels` will be
        equal to `None` and your code will likely result in Python exceptions. After
        `np_pixels[]` has been modified, the `Py5Image.update_np_pixels()` method must
        be called to update the content of the display window.

        To set the entire contents of `np_pixels[]` to the contents of another equally
        sized numpy array, consider using `Py5Image.set_np_pixels()`.

        Look at the online "Numpy, Arrays, and Images" Python Ecosystem Integration
        tutorial for more information about how to make best use of `np_pixels[]`.""",
    )

    def set_np_pixels(self, array: npt.NDArray[np.uint8], bands: str = "ARGB") -> None:
        """Set the entire contents of `Py5Image.np_pixels[]` to the contents of another
        properly sized and typed numpy array.

        Parameters
        ----------

        array: npt.NDArray[np.uint8]
            properly sized numpy array to be copied to np_pixels[]

        bands: str = "ARGB"
            color channels in the array's third dimension

        Notes
        -----

        Set the entire contents of `Py5Image.np_pixels[]` to the contents of another
        properly sized and typed numpy array. The size of `array`'s first and second
        dimensions must match the height and width of the image, respectively. The
        array's `dtype` must be `np.uint8`.

        The `bands` parameter is used to interpret the `array`'s color channel dimension
        (the array's third dimension). It can be one of `'L'` (single-channel
        grayscale), `'ARGB'`, `'RGB'`, or `'RGBA'`. If there is no alpha channel,
        `array` is assumed to have no transparency. If the `bands` parameter is `'L'`,
        `array`'s third dimension is optional.

        This method makes its own calls to `Py5Image.load_np_pixels()` and
        `Py5Image.update_np_pixels()` so there is no need to call either explicitly.

        This method exists because setting the array contents with the code
        `img.np_pixels = array` will cause an error, while the correct syntax,
        `img.np_pixels[:] = array`, might also be unintuitive for beginners.

        Note that the `convert_image()` method can also be used to convert a numpy array
        into a new Py5Image object."""
        return super().set_np_pixels(array, bands)

    @overload
    def get_np_pixels(
        self, *, bands: str = "ARGB", dst: npt.NDArray[np.uint8] = None
    ) -> npt.NDArray[np.uint8]:
        """Get the contents of `Py5Image.np_pixels[]` as a numpy array.

        Methods
        -------

        You can use any of the following signatures:

         * get_np_pixels(*, bands: str = "ARGB", dst: npt.NDArray[np.uint8] = None) -> npt.NDArray[np.uint8]
         * get_np_pixels(x: int, y: int, w: int, h: int, /, *, bands: str = "ARGB", dst: npt.NDArray[np.uint8] = None) -> npt.NDArray[np.uint8]

        Parameters
        ----------

        bands: str = "ARGB"
            color channels in output array

        dst: npt.NDArray[np.uint8] = None
            destination array to copy pixel data into

        h: int
            source height

        w: int
            source width

        x: int
            x-coordinate of the source's upper left corner

        y: int
            y-coordinate of the source's upper left corner

        Notes
        -----

        Get the contents of `Py5Image.np_pixels[]` as a numpy array. The returned numpy
        array can be the entirety of `Py5Image.np_pixels[]` or a rectangular subsection.
        Use the `x`, `y`, `h`, and `w` parameters to specify the bounds of a rectangular
        subsection.

        The `bands` parameter is used to determine the ordering of the returned numpy
        array's color channel. It can be one of `'L'` (single-channel grayscale),
        `'ARGB'`, `'RGB'`, or `'RGBA'`. If the `bands` parameter is `'L'`, the returned
        array will have two dimensions, and each pixel value will be calculated as
        `0.299 * red + 0.587 * green + 0.114 * blue`. The alpha channel will also be
        ignored. For all other `bands` parameter values, the returned array will have
        three dimensions, with the third dimension representing the different color
        channels specified by the `bands` value.

        The returned array will always be a copy of the data in `Py5Image.np_pixels[]`
        and not a view into that array or any other array. Use the `dst` parameter to
        provide the numpy array to copy the pixel data into. The provided array must be
        sized correctly. The array's `dtype` should `np.uint8`, but this isn't required.
        """
        pass

    @overload
    def get_np_pixels(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        /,
        *,
        bands: str = "ARGB",
        dst: npt.NDArray[np.uint8] = None,
    ) -> npt.NDArray[np.uint8]:
        """Get the contents of `Py5Image.np_pixels[]` as a numpy array.

        Methods
        -------

        You can use any of the following signatures:

         * get_np_pixels(*, bands: str = "ARGB", dst: npt.NDArray[np.uint8] = None) -> npt.NDArray[np.uint8]
         * get_np_pixels(x: int, y: int, w: int, h: int, /, *, bands: str = "ARGB", dst: npt.NDArray[np.uint8] = None) -> npt.NDArray[np.uint8]

        Parameters
        ----------

        bands: str = "ARGB"
            color channels in output array

        dst: npt.NDArray[np.uint8] = None
            destination array to copy pixel data into

        h: int
            source height

        w: int
            source width

        x: int
            x-coordinate of the source's upper left corner

        y: int
            y-coordinate of the source's upper left corner

        Notes
        -----

        Get the contents of `Py5Image.np_pixels[]` as a numpy array. The returned numpy
        array can be the entirety of `Py5Image.np_pixels[]` or a rectangular subsection.
        Use the `x`, `y`, `h`, and `w` parameters to specify the bounds of a rectangular
        subsection.

        The `bands` parameter is used to determine the ordering of the returned numpy
        array's color channel. It can be one of `'L'` (single-channel grayscale),
        `'ARGB'`, `'RGB'`, or `'RGBA'`. If the `bands` parameter is `'L'`, the returned
        array will have two dimensions, and each pixel value will be calculated as
        `0.299 * red + 0.587 * green + 0.114 * blue`. The alpha channel will also be
        ignored. For all other `bands` parameter values, the returned array will have
        three dimensions, with the third dimension representing the different color
        channels specified by the `bands` value.

        The returned array will always be a copy of the data in `Py5Image.np_pixels[]`
        and not a view into that array or any other array. Use the `dst` parameter to
        provide the numpy array to copy the pixel data into. The provided array must be
        sized correctly. The array's `dtype` should `np.uint8`, but this isn't required.
        """
        pass

    def get_np_pixels(self, *args, **kwargs) -> npt.NDArray[np.uint8]:
        """Get the contents of `Py5Image.np_pixels[]` as a numpy array.

        Methods
        -------

        You can use any of the following signatures:

         * get_np_pixels(*, bands: str = "ARGB", dst: npt.NDArray[np.uint8] = None) -> npt.NDArray[np.uint8]
         * get_np_pixels(x: int, y: int, w: int, h: int, /, *, bands: str = "ARGB", dst: npt.NDArray[np.uint8] = None) -> npt.NDArray[np.uint8]

        Parameters
        ----------

        bands: str = "ARGB"
            color channels in output array

        dst: npt.NDArray[np.uint8] = None
            destination array to copy pixel data into

        h: int
            source height

        w: int
            source width

        x: int
            x-coordinate of the source's upper left corner

        y: int
            y-coordinate of the source's upper left corner

        Notes
        -----

        Get the contents of `Py5Image.np_pixels[]` as a numpy array. The returned numpy
        array can be the entirety of `Py5Image.np_pixels[]` or a rectangular subsection.
        Use the `x`, `y`, `h`, and `w` parameters to specify the bounds of a rectangular
        subsection.

        The `bands` parameter is used to determine the ordering of the returned numpy
        array's color channel. It can be one of `'L'` (single-channel grayscale),
        `'ARGB'`, `'RGB'`, or `'RGBA'`. If the `bands` parameter is `'L'`, the returned
        array will have two dimensions, and each pixel value will be calculated as
        `0.299 * red + 0.587 * green + 0.114 * blue`. The alpha channel will also be
        ignored. For all other `bands` parameter values, the returned array will have
        three dimensions, with the third dimension representing the different color
        channels specified by the `bands` value.

        The returned array will always be a copy of the data in `Py5Image.np_pixels[]`
        and not a view into that array or any other array. Use the `dst` parameter to
        provide the numpy array to copy the pixel data into. The provided array must be
        sized correctly. The array's `dtype` should `np.uint8`, but this isn't required.
        """
        return super().get_np_pixels(*args, **kwargs)

    @overload
    def to_pil(self) -> PIL_Image:
        """Convert the Py5Image object to a PIL Image object.

        Methods
        -------

        You can use any of the following signatures:

         * to_pil() -> PIL_Image
         * to_pil(x: int, y: int, w: int, h: int) -> PIL_Image

        Parameters
        ----------

        h: int
            source height

        w: int
            source width

        x: int
            x-coordinate of the source's upper left corner

        y: int
            y-coordinate of the source's upper left corner

        Notes
        -----

        Convert the Py5Image object to a PIL Image object. The returned PIL Image object
        can include the entirety of the Py5Image's pixels or a rectangular subsection.
        Use the `x`, `y`, `h`, and `w` parameters to specify the bounds of a rectangular
        subsection."""
        pass

    @overload
    def to_pil(self, x: int, y: int, w: int, h: int, /) -> PIL_Image:
        """Convert the Py5Image object to a PIL Image object.

        Methods
        -------

        You can use any of the following signatures:

         * to_pil() -> PIL_Image
         * to_pil(x: int, y: int, w: int, h: int) -> PIL_Image

        Parameters
        ----------

        h: int
            source height

        w: int
            source width

        x: int
            x-coordinate of the source's upper left corner

        y: int
            y-coordinate of the source's upper left corner

        Notes
        -----

        Convert the Py5Image object to a PIL Image object. The returned PIL Image object
        can include the entirety of the Py5Image's pixels or a rectangular subsection.
        Use the `x`, `y`, `h`, and `w` parameters to specify the bounds of a rectangular
        subsection."""
        pass

    def to_pil(self, *args) -> PIL_Image:
        """Convert the Py5Image object to a PIL Image object.

        Methods
        -------

        You can use any of the following signatures:

         * to_pil() -> PIL_Image
         * to_pil(x: int, y: int, w: int, h: int) -> PIL_Image

        Parameters
        ----------

        h: int
            source height

        w: int
            source width

        x: int
            x-coordinate of the source's upper left corner

        y: int
            y-coordinate of the source's upper left corner

        Notes
        -----

        Convert the Py5Image object to a PIL Image object. The returned PIL Image object
        can include the entirety of the Py5Image's pixels or a rectangular subsection.
        Use the `x`, `y`, `h`, and `w` parameters to specify the bounds of a rectangular
        subsection."""
        return super().to_pil(*args)

    def save(
        self,
        filename: Union[str, Path, BytesIO],
        *,
        format: str = None,
        drop_alpha: bool = True,
        use_thread: bool = False,
        **params,
    ) -> None:
        """Save the Py5Image object to an image file.

        Parameters
        ----------

        drop_alpha: bool = True
            remove the alpha channel when saving the image

        filename: Union[str, Path, BytesIO]
            output filename

        format: str = None
            image format, if not determined from filename extension

        params
            keyword arguments to pass to the PIL.Image save method

        use_thread: bool = False
            write file in separate thread

        Notes
        -----

        Save the Py5Image object to an image file. This method uses the Python library
        Pillow to write the image, so it can save images in any format that that library
        supports.

        Use the `drop_alpha` parameter to drop the alpha channel from the image. This
        defaults to `True`. Some image formats such as JPG do not support alpha
        channels, and Pillow will throw an error if you try to save an image with the
        alpha channel in that format.

        The `use_thread` parameter will save the image in a separate Python thread. This
        improves performance by returning before the image has actually been written to
        the file."""
        return super().save(
            filename,
            format=format,
            drop_alpha=drop_alpha,
            use_thread=use_thread,
            **params,
        )
