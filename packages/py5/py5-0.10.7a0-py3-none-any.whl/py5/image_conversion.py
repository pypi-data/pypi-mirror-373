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
import io
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np
from PIL import Image

pimage_functions = []

_TEMP_DIR = Path(tempfile.TemporaryDirectory().name)
_TEMP_DIR.mkdir(exist_ok=True, parents=True)


def _convertable(obj):
    return any(pre(obj) for pre, _ in pimage_functions)


def _convert(sketch, obj, **kwargs):
    for precondition, convert_function in pimage_functions:
        if precondition(obj):
            obj = convert_function(sketch, obj, **kwargs)
            break
    else:
        classname = f"{obj.__class__.__module__}.{obj.__class__.__name__}"
        raise RuntimeError(
            f"py5 convert_image() method is not able to convert objects of type {classname}"
        )

    return obj


def register_image_conversion(
    precondition: Callable, convert_function: Callable
) -> None:
    """Register new image conversion functionality to be used by `convert_image()`.

    Parameters
    ----------

    convert_function: Callable
        function to convert object to relevant image data

    precondition: Callable
        predicate determining if an object can be converted

    Notes
    -----

    Register new image conversion functionality to be used by `convert_image()`.
    This will allow users to extend py5's capabilities and compatability within the
    Python ecosystem.

    The `precondition` parameter must be a function that accepts an object as a
    parameter and returns `True` if and only if the `convert_function` can
    successfully convert the object.

    The `convert_function` parameter must be a function that accepts an object as a
    parameter and returns either a filename that can be read by `load_image()`, a
    `py5.NumpyImageArray` object, or a `Py5Image` object. View py5's source code for
    detailed information about `py5.NumpyImageArray` objects. The `convert_function`
    will take care of loading an image from a returned image filename or converting
    the `py5.NumpyImageArray` object into a Py5Image object."""
    pimage_functions.insert(0, (precondition, convert_function))


###############################################################################
# BUILT-IN CONVERSTION FUNCTIONS
###############################################################################


@dataclass
class NumpyImageArray:
    array: np.ndarray
    bands: str = "ARGB"

    def __post_init__(self):
        if not isinstance(self.array, np.ndarray):
            raise RuntimeError("array parameter must be a numpy array")
        if not self.array.dtype == np.uint8:
            raise RuntimeError("array parameter must have uint8 dtype")
        if not isinstance(self.bands, str):
            raise RuntimeError("bands parameter must be a string")
        if self.bands in ["RGBA", "ARGB", "RGB"]:
            if self.array.ndim != 3:
                raise RuntimeError(
                    f"array parameter must have 3 dimensions for '{self.bands}' image arrays"
                )
            if self.array.shape[2] != len(self.bands):
                raise RuntimeError(
                    "third dimension of array parameter equal the length of the bands parameter"
                )
        elif self.bands == "L":
            if not (
                self.array.ndim == 2
                or (self.array.ndim == 3 and self.array.shape[2] == 1)
            ):
                raise RuntimeError(
                    "for 'L' image arrays, array must have 2 dimensions or a 3rd dimension of size 1"
                )
        else:
            raise RuntimeError(
                "bands parameter must be one of 'RGBA', 'ARGB', 'RGB', or 'L'"
            )


def numpy_image_array_precondition(obj):
    return isinstance(obj, NumpyImageArray)


def numpy_image_array_converter(sketch, obj, **kwargs):
    return obj


register_image_conversion(numpy_image_array_precondition, numpy_image_array_converter)


def pillow_image_to_ndarray_precondition(obj):
    return isinstance(obj, Image.Image)


def pillow_image_to_ndarray_converter(sketch, img, **kwargs):
    if img.mode not in ["RGB", "RGBA"]:
        img = img.convert(mode="RGB")
    return NumpyImageArray(np.asarray(img), img.mode)


register_image_conversion(
    pillow_image_to_ndarray_precondition, pillow_image_to_ndarray_converter
)


###############################################################################
# Py5 requires Pillow and numpy to be installed. The below libraries may or may
# not be installed. If they are, this registers their associated conversion
# functions.
###############################################################################


try:
    import cairocffi  # noqa
    import cairosvg  # noqa

    def svg_file_to_ndarray_precondition(obj):
        if isinstance(obj, (str, Path)):
            return Path(obj).suffix.lower() == ".svg"
        else:
            return False

    def svg_file_to_ndarray_converter(sketch, filename, **kwargs):
        parent_width = kwargs.get("parent_width", None)
        parent_height = kwargs.get("parent_height", None)
        dpi = kwargs.get("dpi", 96)
        scale = kwargs.get("scale", 1)
        unsafe = kwargs.get("unsafe", False)
        background_color = kwargs.get("background_color", None)
        negate_colors = kwargs.get("negate_colors", False)
        invert_images = kwargs.get("invert_images", False)
        output_width = kwargs.get("output_width", None)
        output_height = kwargs.get("output_height", None)

        filename = Path(filename)
        with open(filename, "r") as f:
            img = Image.open(
                io.BytesIO(
                    cairosvg.svg2png(
                        file_obj=f,
                        dpi=dpi,
                        parent_width=parent_width,
                        parent_height=parent_height,
                        scale=scale,
                        unsafe=unsafe,
                        background_color=background_color,
                        negate_colors=negate_colors,
                        invert_images=invert_images,
                        output_width=output_width,
                        output_height=output_height,
                    )
                )
            )
            return pillow_image_to_ndarray_converter(sketch, img, **kwargs)

    register_image_conversion(
        svg_file_to_ndarray_precondition, svg_file_to_ndarray_converter
    )
except Exception:
    pass


try:
    import cairocffi  # noqa

    def cairocffi_surface_to_tempfile_precondition(obj):
        return isinstance(obj, cairocffi.Surface)

    def cairocffi_surface_to_tempfile_converter(sketch, surface, **kwargs):
        temp_png = _TEMP_DIR / f"{uuid.uuid4()}.png"
        surface.write_to_png(temp_png.as_posix())
        return temp_png

    register_image_conversion(
        cairocffi_surface_to_tempfile_precondition,
        cairocffi_surface_to_tempfile_converter,
    )
except Exception:
    pass


try:
    import cairo  # noqa

    def cairo_surface_to_tempfile_precondition(obj):
        return isinstance(obj, cairo.Surface)

    def cairo_surface_to_tempfile_converter(sketch, surface, **kwargs):
        temp_png = _TEMP_DIR / f"{uuid.uuid4()}.png"
        surface.write_to_png(temp_png.as_posix())
        return temp_png

    register_image_conversion(
        cairo_surface_to_tempfile_precondition, cairo_surface_to_tempfile_converter
    )
except Exception:
    pass


try:
    from matplotlib.backends.backend_agg import FigureCanvasAgg  # noqa
    from matplotlib.figure import Figure  # noqa

    def figure_to_ndarray_precondition(obj):
        return isinstance(obj, Figure)

    def figure_to_ndarray_converter(sketch, figure, **kwargs):
        canvas = FigureCanvasAgg(figure)
        canvas.draw()
        return NumpyImageArray(np.asarray(canvas.buffer_rgba()), "RGBA")

    register_image_conversion(
        figure_to_ndarray_precondition, figure_to_ndarray_converter
    )
except Exception:
    pass
