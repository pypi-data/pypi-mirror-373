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
import types
import weakref
from pathlib import Path
from typing import Sequence, overload  # noqa

import numpy as np
import numpy.typing as npt  # noqa
from jpype import JClass, JException
from jpype.types import JBoolean, JFloat, JInt

from . import spelling
from .decorators import (
    _context_wrapper,
    _convert_hex_color,
    _convert_hex_color2,
    _ret_str,
    _return_color,
)
from .pmath import _get_pvector_wrapper  # noqa


def _return_list_py5shapes(f):
    @functools.wraps(f)
    def decorated(self_, *args):
        try:
            return [Py5Shape(s) for s in f(self_, *args)]
        except Exception as e:
            return []

    return decorated


def _return_py5shape(f):
    @functools.wraps(f)
    def decorated(self_, *args):
        result = f(self_, *args)
        if result:
            return Py5Shape(result)

    return decorated


def _py5shape_type_fixer(f):
    @functools.wraps(f)
    def decorated(self_, *args):
        def fix_type(arg):
            if isinstance(arg, bool):
                return JBoolean(arg)
            elif isinstance(arg, (int, np.integer)):
                return JInt(arg)
            elif isinstance(arg, float):
                return JFloat(arg)
            else:
                return arg

        args = [fix_type(a) for a in args]
        return f(self_, *args)

    return decorated


def _load_py5shape(f):
    @functools.wraps(f)
    def decorated(self_, *args):
        msg, pshape = "", None

        try:
            if (pshape := f(self_, *args)) is None:
                msg = "Processing unable to read shape file"
        except Exception as e:
            msg = e.message()
            if msg == "None":
                msg = "shape file cannot be found"

        if pshape is None:
            raise RuntimeError(
                "cannot load shape " + str(args[0]) + ". error message: " + msg
            )
        else:
            return Py5Shape(pshape)

    return decorated


def _return_numpy_array(f):
    @functools.wraps(f)
    def decorated(self_, *args):
        result = f(self_, *args)
        return np.array(result) if result is not None else None

    return decorated


_Py5ShapeHelper = JClass("py5.core.Py5ShapeHelper")


class Py5Shape:
    """Datatype for storing shapes.

    Underlying Processing class: PShape.PShape

    Notes
    -----

    Datatype for storing shapes. Before a shape is used, it must be loaded with the
    `load_shape()` or created with the `create_shape()`. The `shape()` function is
    used to draw the shape to the display window. Py5 can currently load and display
    SVG (Scalable Vector Graphics) and OBJ shapes. OBJ files can only be opened
    using the `P3D` renderer. The `load_shape()` function supports SVG files created
    with Inkscape and Adobe Illustrator. It is not a full SVG implementation, but
    offers some straightforward support for handling vector data. A more complete
    SVG implementation can be provided by `convert_image()` if Cairo is installed.
    See installation instructions for additional detail.

    The `Py5Shape` object contains a group of methods that can operate on the shape
    data.

    To create a new shape, use the `create_shape()` function. Do not use the syntax
    `Py5Shape()`."""

    _py5_object_cache = weakref.WeakSet()

    def __new__(cls, pshape):
        for o in cls._py5_object_cache:
            if pshape == o._instance:
                return o
        else:
            o = object.__new__(Py5Shape)
            o._instance = pshape
            cls._py5_object_cache.add(o)
            return o

    def __str__(self):
        name = "'" + self.get_name() + "'" if self.get_name() else str(None)
        return f"Py5Shape(name=" + name + ")"

    def __repr__(self):
        return self.__str__()

    def __getattr__(self, name):
        raise AttributeError(spelling.error_msg("Py5Shape", name, self))

    # *** BEGIN METHODS ***

    def _get_width(self) -> float:
        """Get the `Py5Shape` object's width.

        Underlying Processing field: PShape.width

        Notes
        -----

        Get the `Py5Shape` object's width. When using the `P2D` or `P3D` renderers, the
        value should be the width of the drawn shape. When using the default renderer,
        this will be the width of the drawing area, which will not necessarily be the
        same as the width of the drawn shape. Consider that the shape's vertices might
        have negative values or the shape may be offset from the shape's origin. To get
        the shape's actual width, calculate the range of the vertices obtained with
        `Py5Shape.get_vertex_x()`."""
        return self._instance.getWidth()

    width: float = property(
        fget=_get_width,
        doc="""Get the `Py5Shape` object's width.

        Underlying Processing field: PShape.width

        Notes
        -----

        Get the `Py5Shape` object's width. When using the `P2D` or `P3D` renderers, the
        value should be the width of the drawn shape. When using the default renderer,
        this will be the width of the drawing area, which will not necessarily be the
        same as the width of the drawn shape. Consider that the shape's vertices might
        have negative values or the shape may be offset from the shape's origin. To get
        the shape's actual width, calculate the range of the vertices obtained with
        `Py5Shape.get_vertex_x()`.""",
    )

    def _get_height(self) -> float:
        """Get the `Py5Shape` object's height.

        Underlying Processing field: PShape.height

        Notes
        -----

        Get the `Py5Shape` object's height. When using the `P2D` or `P3D` renderers, the
        value should be the height of the drawn shape. When using the default renderer,
        this will be the height of the drawing area, which will not necessarily be the
        same as the height of the drawn shape. Consider that the shape's vertices might
        have negative values or the shape may be offset from the shape's origin. To get
        the shape's actual height, calculate the range of the vertices obtained with
        `Py5Shape.get_vertex_y()`."""
        return self._instance.getHeight()

    height: float = property(
        fget=_get_height,
        doc="""Get the `Py5Shape` object's height.

        Underlying Processing field: PShape.height

        Notes
        -----

        Get the `Py5Shape` object's height. When using the `P2D` or `P3D` renderers, the
        value should be the height of the drawn shape. When using the default renderer,
        this will be the height of the drawing area, which will not necessarily be the
        same as the height of the drawn shape. Consider that the shape's vertices might
        have negative values or the shape may be offset from the shape's origin. To get
        the shape's actual height, calculate the range of the vertices obtained with
        `Py5Shape.get_vertex_y()`.""",
    )

    def _get_depth(self) -> float:
        """Get the `Py5Shape` object's depth.

        Underlying Processing field: PShape.depth

        Notes
        -----

        Get the `Py5Shape` object's depth. This property only makes sense when using the
        `P3D` renderer. The value will be equal to 0 when using default renderer."""
        return self._instance.getDepth()

    depth: float = property(
        fget=_get_depth,
        doc="""Get the `Py5Shape` object's depth.

        Underlying Processing field: PShape.depth

        Notes
        -----

        Get the `Py5Shape` object's depth. This property only makes sense when using the
        `P3D` renderer. The value will be equal to 0 when using default renderer.""",
    )

    def set_strokes(self, strokes: Sequence[int], /) -> None:
        """Set the stroke color for each of the individual vertices of a `Py5Shape`.

        Parameters
        ----------

        strokes: Sequence[int]
            array of stroke colors

        Notes
        -----

        Set the stroke color for each of the individual vertices of a `Py5Shape`. The
        length of the passed `strokes` array must equal the number of vertices in the
        shape. This method exists to provide an alternative to repeatedly calling
        `Py5Shape.set_fill()` in a loop.

        This method can only be used after the shape has been created. Do not use this
        method between the calls to `Py5Shape.begin_shape()` and `Py5Shape.end_shape()`.
        """
        if isinstance(strokes, types.GeneratorType):
            strokes = list(strokes)
        _Py5ShapeHelper.setStrokes(self._instance, strokes)

    def set_fills(self, fills: Sequence[int], /) -> None:
        """Set the fill color for each of the individual vertices of a `Py5Shape`.

        Parameters
        ----------

        fills: Sequence[int]
            array of fill colors

        Notes
        -----

        Set the fill color for each of the individual vertices of a `Py5Shape`. The
        length of the passed `fills` array must equal the number of vertices in the
        shape. This method exists to provide an alternative to repeatedly calling
        `Py5Shape.set_fill()` in a loop.

        This method can only be used after the shape has been created. Do not use this
        method between the calls to `Py5Shape.begin_shape()` and `Py5Shape.end_shape()`.
        """
        if isinstance(fills, types.GeneratorType):
            fills = list(fills)
        _Py5ShapeHelper.setFills(self._instance, fills)

    def vertices(self, coordinates: Sequence[Sequence[float]], /) -> None:
        """Create a collection of vertices.

        Parameters
        ----------

        coordinates: Sequence[Sequence[float]]
            2D array of vertex coordinates and optional UV texture mapping values

        Notes
        -----

        Create a collection of vertices. The purpose of this method is to provide an
        alternative to repeatedly calling `Py5Shape.vertex()` in a loop. For a large
        number of vertices, the performance of `vertices()` will be much faster.

        The `coordinates` parameter should be a numpy array with one row for each
        vertex. There should be two or three columns for 2D or 3D points, respectively.
        There may also be an additional two columns for UV texture mapping values."""
        if isinstance(coordinates, types.GeneratorType):
            coordinates = list(coordinates)
        _Py5ShapeHelper.vertices(self._instance, coordinates)

    def bezier_vertices(self, coordinates: Sequence[Sequence[float]], /) -> None:
        """Create a collection of bezier vertices.

        Parameters
        ----------

        coordinates: Sequence[Sequence[float]]
            2D array of bezier vertex coordinates with 6 or 9 columns for 2D or 3D points, respectively

        Notes
        -----

        Create a collection of bezier vertices. The purpose of this method is to provide
        an alternative to repeatedly calling `Py5Shape.bezier_vertex()` in a loop. For a
        large number of bezier vertices, the performance of `bezier_vertices()` will be
        much faster.

        The `coordinates` parameter should be a numpy array with one row for each bezier
        vertex. The first few columns are for the first control point, the next few
        columns are for the second control point, and the final few columns are for the
        anchor point. There should be six or nine columns for 2D or 3D points,
        respectively.

        Drawing 2D bezier curves requires using the `P2D` renderer and drawing 3D bezier
        curves requires using the `P3D` renderer. When drawing directly with `Py5Shape`
        objects, bezier curves do not work at all using the default renderer.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair."""
        if isinstance(coordinates, types.GeneratorType):
            coordinates = list(coordinates)
        _Py5ShapeHelper.bezierVertices(self._instance, coordinates)

    def curve_vertices(self, coordinates: Sequence[Sequence[float]], /) -> None:
        """Create a collection of curve vertices.

        Parameters
        ----------

        coordinates: Sequence[Sequence[float]]
            2D array of curve vertex coordinates with 2 or 3 columns for 2D or 3D points, respectively

        Notes
        -----

        Create a collection of curve vertices. The purpose of this method is to provide
        an alternative to repeatedly calling `Py5Shape.curve_vertex()` in a loop. For a
        large number of curve vertices, the performance of `curve_vertices()` will be
        much faster.

        The `coordinates` parameter should be a numpy array with one row for each curve
        vertex.  There should be two or three columns for 2D or 3D points, respectively.

        Drawing 2D curves requires using the `P2D` renderer and drawing 3D curves
        requires using the `P3D` renderer. When drawing directly with `Py5Shape`
        objects, curves do not work at all using the default renderer.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair."""
        if isinstance(coordinates, types.GeneratorType):
            coordinates = list(coordinates)
        _Py5ShapeHelper.curveVertices(self._instance, coordinates)

    def quadratic_vertices(self, coordinates: Sequence[Sequence[float]], /) -> None:
        """Create a collection of quadratic vertices.

        Parameters
        ----------

        coordinates: Sequence[Sequence[float]]
            2D array of quadratic vertex coordinates with 4 or 6 columns for 2D or 3D points, respectively

        Notes
        -----

        Create a collection of quadratic vertices. The purpose of this method is to
        provide an alternative to repeatedly calling `Py5Shape.quadratic_vertex()` in a
        loop. For a large number of quadratic vertices, the performance of
        `quadratic_vertices()` will be much faster.

        The `coordinates` parameter should be a numpy array with one row for each
        quadratic vertex. The first few columns are for the control point and the next
        few columns are for the anchor point. There should be four or six columns for 2D
        or 3D points, respectively.

        Drawing 2D bezier curves requires using the `P2D` renderer and drawing 3D bezier
        curves requires using the `P3D` renderer. When drawing directly with `Py5Shape`
        objects, bezier curves do not work at all using the default renderer."""
        if isinstance(coordinates, types.GeneratorType):
            coordinates = list(coordinates)
        _Py5ShapeHelper.quadraticVertices(self._instance, coordinates)

    ARC = 32
    BEVEL = 32
    BEZIER_VERTEX = 1
    BOX = 41
    BREAK = 4
    CLOSE = 2
    CURVE_VERTEX = 3
    ELLIPSE = 31
    GEOMETRY = 103
    GROUP = 0
    HSB = 3
    LINE = 4
    LINES = 5
    LINE_LOOP = 51
    LINE_STRIP = 50
    MITER = 8
    PATH = 102
    POINT = 2
    POINTS = 3
    POLYGON = 20
    PRIMITIVE = 101
    PROJECT = 4
    QUAD = 16
    QUADRATIC_VERTEX = 2
    QUADS = 17
    QUAD_BEZIER_VERTEX = 2
    QUAD_STRIP = 18
    RECT = 30
    RGB = 1
    ROUND = 2
    SPHERE = 40
    SQUARE = 1
    TRIANGLE = 8
    TRIANGLES = 9
    TRIANGLE_FAN = 11
    TRIANGLE_STRIP = 10
    VERTEX = 0

    @overload
    def add_child(self, who: Py5Shape, /) -> None:
        """Adds a child `Py5Shape` object to a parent `Py5Shape` object that is defined as
        a `GROUP`.

        Underlying Processing method: PShape.addChild

        Methods
        -------

        You can use any of the following signatures:

         * add_child(who: Py5Shape, /) -> None
         * add_child(who: Py5Shape, idx: int, /) -> None

        Parameters
        ----------

        idx: int
            the layer position in which to insert the new child

        who: Py5Shape
            any variable of type Py5Shape

        Notes
        -----

        Adds a child `Py5Shape` object to a parent `Py5Shape` object that is defined as
        a `GROUP`. In the example, the three shapes `path`, `rectangle`, and `circle`
        are added to a parent `Py5Shape` variable named `house` that is a `GROUP`.
        """
        pass

    @overload
    def add_child(self, who: Py5Shape, idx: int, /) -> None:
        """Adds a child `Py5Shape` object to a parent `Py5Shape` object that is defined as
        a `GROUP`.

        Underlying Processing method: PShape.addChild

        Methods
        -------

        You can use any of the following signatures:

         * add_child(who: Py5Shape, /) -> None
         * add_child(who: Py5Shape, idx: int, /) -> None

        Parameters
        ----------

        idx: int
            the layer position in which to insert the new child

        who: Py5Shape
            any variable of type Py5Shape

        Notes
        -----

        Adds a child `Py5Shape` object to a parent `Py5Shape` object that is defined as
        a `GROUP`. In the example, the three shapes `path`, `rectangle`, and `circle`
        are added to a parent `Py5Shape` variable named `house` that is a `GROUP`.
        """
        pass

    def add_child(self, *args):
        """Adds a child `Py5Shape` object to a parent `Py5Shape` object that is defined as
        a `GROUP`.

        Underlying Processing method: PShape.addChild

        Methods
        -------

        You can use any of the following signatures:

         * add_child(who: Py5Shape, /) -> None
         * add_child(who: Py5Shape, idx: int, /) -> None

        Parameters
        ----------

        idx: int
            the layer position in which to insert the new child

        who: Py5Shape
            any variable of type Py5Shape

        Notes
        -----

        Adds a child `Py5Shape` object to a parent `Py5Shape` object that is defined as
        a `GROUP`. In the example, the three shapes `path`, `rectangle`, and `circle`
        are added to a parent `Py5Shape` variable named `house` that is a `GROUP`.
        """
        return self._instance.addChild(*args)

    @overload
    def ambient(self, gray: float, /) -> None:
        """Sets a `Py5Shape` object's ambient reflectance.

        Underlying Processing method: PShape.ambient

        Methods
        -------

        You can use any of the following signatures:

         * ambient(gray: float, /) -> None
         * ambient(rgb: int, /) -> None
         * ambient(x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        gray: float
            number specifying value between white and black

        rgb: int
            any value of the color datatype

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets a `Py5Shape` object's ambient reflectance. This is combined with the
        ambient light component of the environment. The color components set through the
        parameters define the reflectance. For example in the default color mode,
        setting `ambient(255, 127, 0)`, would cause all the red light to reflect and
        half of the green light to reflect. Use in combination with
        `Py5Shape.emissive()`, `Py5Shape.specular()`, and `Py5Shape.shininess()` to set
        the material properties of a `Py5Shape` object.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair. The ambient color setting will be applied to
        vertices added after the call to this method.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def ambient(self, x: float, y: float, z: float, /) -> None:
        """Sets a `Py5Shape` object's ambient reflectance.

        Underlying Processing method: PShape.ambient

        Methods
        -------

        You can use any of the following signatures:

         * ambient(gray: float, /) -> None
         * ambient(rgb: int, /) -> None
         * ambient(x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        gray: float
            number specifying value between white and black

        rgb: int
            any value of the color datatype

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets a `Py5Shape` object's ambient reflectance. This is combined with the
        ambient light component of the environment. The color components set through the
        parameters define the reflectance. For example in the default color mode,
        setting `ambient(255, 127, 0)`, would cause all the red light to reflect and
        half of the green light to reflect. Use in combination with
        `Py5Shape.emissive()`, `Py5Shape.specular()`, and `Py5Shape.shininess()` to set
        the material properties of a `Py5Shape` object.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair. The ambient color setting will be applied to
        vertices added after the call to this method.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def ambient(self, rgb: int, /) -> None:
        """Sets a `Py5Shape` object's ambient reflectance.

        Underlying Processing method: PShape.ambient

        Methods
        -------

        You can use any of the following signatures:

         * ambient(gray: float, /) -> None
         * ambient(rgb: int, /) -> None
         * ambient(x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        gray: float
            number specifying value between white and black

        rgb: int
            any value of the color datatype

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets a `Py5Shape` object's ambient reflectance. This is combined with the
        ambient light component of the environment. The color components set through the
        parameters define the reflectance. For example in the default color mode,
        setting `ambient(255, 127, 0)`, would cause all the red light to reflect and
        half of the green light to reflect. Use in combination with
        `Py5Shape.emissive()`, `Py5Shape.specular()`, and `Py5Shape.shininess()` to set
        the material properties of a `Py5Shape` object.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair. The ambient color setting will be applied to
        vertices added after the call to this method.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @_convert_hex_color()
    def ambient(self, *args):
        """Sets a `Py5Shape` object's ambient reflectance.

        Underlying Processing method: PShape.ambient

        Methods
        -------

        You can use any of the following signatures:

         * ambient(gray: float, /) -> None
         * ambient(rgb: int, /) -> None
         * ambient(x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        gray: float
            number specifying value between white and black

        rgb: int
            any value of the color datatype

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets a `Py5Shape` object's ambient reflectance. This is combined with the
        ambient light component of the environment. The color components set through the
        parameters define the reflectance. For example in the default color mode,
        setting `ambient(255, 127, 0)`, would cause all the red light to reflect and
        half of the green light to reflect. Use in combination with
        `Py5Shape.emissive()`, `Py5Shape.specular()`, and `Py5Shape.shininess()` to set
        the material properties of a `Py5Shape` object.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair. The ambient color setting will be applied to
        vertices added after the call to this method.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        return self._instance.ambient(*args)

    @overload
    def apply_matrix(
        self, n00: float, n01: float, n02: float, n10: float, n11: float, n12: float, /
    ) -> None:
        """Apply a transformation matrix to a `Py5Shape` object.

        Underlying Processing method: PShape.applyMatrix

        Methods
        -------

        You can use any of the following signatures:

         * apply_matrix(n00: float, n01: float, n02: float, n03: float, n10: float, n11: float, n12: float, n13: float, n20: float, n21: float, n22: float, n23: float, n30: float, n31: float, n32: float, n33: float, /) -> None
         * apply_matrix(n00: float, n01: float, n02: float, n10: float, n11: float, n12: float, /) -> None
         * apply_matrix(source: npt.NDArray[np.floating], /) -> None

        Parameters
        ----------

        n00: float
            numeric value in row 0 and column 0 of the matrix

        n01: float
            numeric value in row 0 and column 1 of the matrix

        n02: float
            numeric value in row 0 and column 2 of the matrix

        n03: float
            numeric value in row 0 and column 3 of the matrix

        n10: float
            numeric value in row 1 and column 0 of the matrix

        n11: float
            numeric value in row 1 and column 1 of the matrix

        n12: float
            numeric value in row 1 and column 2 of the matrix

        n13: float
            numeric value in row 1 and column 3 of the matrix

        n20: float
            numeric value in row 2 and column 0 of the matrix

        n21: float
            numeric value in row 2 and column 1 of the matrix

        n22: float
            numeric value in row 2 and column 2 of the matrix

        n23: float
            numeric value in row 2 and column 3 of the matrix

        n30: float
            numeric value in row 3 and column 0 of the matrix

        n31: float
            numeric value in row 3 and column 1 of the matrix

        n32: float
            numeric value in row 3 and column 2 of the matrix

        n33: float
            numeric value in row 3 and column 3 of the matrix

        source: npt.NDArray[np.floating]
            transformation matrix with a shape of 2x3 for 2D transforms or 4x4 for 3D transforms

        Notes
        -----

        Apply a transformation matrix to a `Py5Shape` object. This can be used to scale,
        rotate, and translate a shape with one call.

        Making productive use of this method requires some knowledge of 2D or 3D
        transformation matrices, and perhaps some knowledge of Processing's source code.

        Transformations are cummulative and therefore will be applied on top of existing
        transformations. Use `Py5Shape.reset_matrix()` to set the transformation matrix
        to the identity matrix.
        """
        pass

    @overload
    def apply_matrix(
        self,
        n00: float,
        n01: float,
        n02: float,
        n03: float,
        n10: float,
        n11: float,
        n12: float,
        n13: float,
        n20: float,
        n21: float,
        n22: float,
        n23: float,
        n30: float,
        n31: float,
        n32: float,
        n33: float,
        /,
    ) -> None:
        """Apply a transformation matrix to a `Py5Shape` object.

        Underlying Processing method: PShape.applyMatrix

        Methods
        -------

        You can use any of the following signatures:

         * apply_matrix(n00: float, n01: float, n02: float, n03: float, n10: float, n11: float, n12: float, n13: float, n20: float, n21: float, n22: float, n23: float, n30: float, n31: float, n32: float, n33: float, /) -> None
         * apply_matrix(n00: float, n01: float, n02: float, n10: float, n11: float, n12: float, /) -> None
         * apply_matrix(source: npt.NDArray[np.floating], /) -> None

        Parameters
        ----------

        n00: float
            numeric value in row 0 and column 0 of the matrix

        n01: float
            numeric value in row 0 and column 1 of the matrix

        n02: float
            numeric value in row 0 and column 2 of the matrix

        n03: float
            numeric value in row 0 and column 3 of the matrix

        n10: float
            numeric value in row 1 and column 0 of the matrix

        n11: float
            numeric value in row 1 and column 1 of the matrix

        n12: float
            numeric value in row 1 and column 2 of the matrix

        n13: float
            numeric value in row 1 and column 3 of the matrix

        n20: float
            numeric value in row 2 and column 0 of the matrix

        n21: float
            numeric value in row 2 and column 1 of the matrix

        n22: float
            numeric value in row 2 and column 2 of the matrix

        n23: float
            numeric value in row 2 and column 3 of the matrix

        n30: float
            numeric value in row 3 and column 0 of the matrix

        n31: float
            numeric value in row 3 and column 1 of the matrix

        n32: float
            numeric value in row 3 and column 2 of the matrix

        n33: float
            numeric value in row 3 and column 3 of the matrix

        source: npt.NDArray[np.floating]
            transformation matrix with a shape of 2x3 for 2D transforms or 4x4 for 3D transforms

        Notes
        -----

        Apply a transformation matrix to a `Py5Shape` object. This can be used to scale,
        rotate, and translate a shape with one call.

        Making productive use of this method requires some knowledge of 2D or 3D
        transformation matrices, and perhaps some knowledge of Processing's source code.

        Transformations are cummulative and therefore will be applied on top of existing
        transformations. Use `Py5Shape.reset_matrix()` to set the transformation matrix
        to the identity matrix.
        """
        pass

    @overload
    def apply_matrix(self, source: npt.NDArray[np.floating], /) -> None:
        """Apply a transformation matrix to a `Py5Shape` object.

        Underlying Processing method: PShape.applyMatrix

        Methods
        -------

        You can use any of the following signatures:

         * apply_matrix(n00: float, n01: float, n02: float, n03: float, n10: float, n11: float, n12: float, n13: float, n20: float, n21: float, n22: float, n23: float, n30: float, n31: float, n32: float, n33: float, /) -> None
         * apply_matrix(n00: float, n01: float, n02: float, n10: float, n11: float, n12: float, /) -> None
         * apply_matrix(source: npt.NDArray[np.floating], /) -> None

        Parameters
        ----------

        n00: float
            numeric value in row 0 and column 0 of the matrix

        n01: float
            numeric value in row 0 and column 1 of the matrix

        n02: float
            numeric value in row 0 and column 2 of the matrix

        n03: float
            numeric value in row 0 and column 3 of the matrix

        n10: float
            numeric value in row 1 and column 0 of the matrix

        n11: float
            numeric value in row 1 and column 1 of the matrix

        n12: float
            numeric value in row 1 and column 2 of the matrix

        n13: float
            numeric value in row 1 and column 3 of the matrix

        n20: float
            numeric value in row 2 and column 0 of the matrix

        n21: float
            numeric value in row 2 and column 1 of the matrix

        n22: float
            numeric value in row 2 and column 2 of the matrix

        n23: float
            numeric value in row 2 and column 3 of the matrix

        n30: float
            numeric value in row 3 and column 0 of the matrix

        n31: float
            numeric value in row 3 and column 1 of the matrix

        n32: float
            numeric value in row 3 and column 2 of the matrix

        n33: float
            numeric value in row 3 and column 3 of the matrix

        source: npt.NDArray[np.floating]
            transformation matrix with a shape of 2x3 for 2D transforms or 4x4 for 3D transforms

        Notes
        -----

        Apply a transformation matrix to a `Py5Shape` object. This can be used to scale,
        rotate, and translate a shape with one call.

        Making productive use of this method requires some knowledge of 2D or 3D
        transformation matrices, and perhaps some knowledge of Processing's source code.

        Transformations are cummulative and therefore will be applied on top of existing
        transformations. Use `Py5Shape.reset_matrix()` to set the transformation matrix
        to the identity matrix.
        """
        pass

    def apply_matrix(self, *args):
        """Apply a transformation matrix to a `Py5Shape` object.

        Underlying Processing method: PShape.applyMatrix

        Methods
        -------

        You can use any of the following signatures:

         * apply_matrix(n00: float, n01: float, n02: float, n03: float, n10: float, n11: float, n12: float, n13: float, n20: float, n21: float, n22: float, n23: float, n30: float, n31: float, n32: float, n33: float, /) -> None
         * apply_matrix(n00: float, n01: float, n02: float, n10: float, n11: float, n12: float, /) -> None
         * apply_matrix(source: npt.NDArray[np.floating], /) -> None

        Parameters
        ----------

        n00: float
            numeric value in row 0 and column 0 of the matrix

        n01: float
            numeric value in row 0 and column 1 of the matrix

        n02: float
            numeric value in row 0 and column 2 of the matrix

        n03: float
            numeric value in row 0 and column 3 of the matrix

        n10: float
            numeric value in row 1 and column 0 of the matrix

        n11: float
            numeric value in row 1 and column 1 of the matrix

        n12: float
            numeric value in row 1 and column 2 of the matrix

        n13: float
            numeric value in row 1 and column 3 of the matrix

        n20: float
            numeric value in row 2 and column 0 of the matrix

        n21: float
            numeric value in row 2 and column 1 of the matrix

        n22: float
            numeric value in row 2 and column 2 of the matrix

        n23: float
            numeric value in row 2 and column 3 of the matrix

        n30: float
            numeric value in row 3 and column 0 of the matrix

        n31: float
            numeric value in row 3 and column 1 of the matrix

        n32: float
            numeric value in row 3 and column 2 of the matrix

        n33: float
            numeric value in row 3 and column 3 of the matrix

        source: npt.NDArray[np.floating]
            transformation matrix with a shape of 2x3 for 2D transforms or 4x4 for 3D transforms

        Notes
        -----

        Apply a transformation matrix to a `Py5Shape` object. This can be used to scale,
        rotate, and translate a shape with one call.

        Making productive use of this method requires some knowledge of 2D or 3D
        transformation matrices, and perhaps some knowledge of Processing's source code.

        Transformations are cummulative and therefore will be applied on top of existing
        transformations. Use `Py5Shape.reset_matrix()` to set the transformation matrix
        to the identity matrix.
        """
        return self._instance.applyMatrix(*args)

    @_context_wrapper("end_contour")
    def begin_contour(self) -> None:
        """Use the `begin_contour()` and `Py5Shape.end_contour()` methods to create
        negative shapes within a `Py5Shape` object such as the center of the letter 'O'.

        Underlying Processing method: PShape.beginContour

        Notes
        -----

        Use the `begin_contour()` and `Py5Shape.end_contour()` methods to create
        negative shapes within a `Py5Shape` object such as the center of the letter 'O'.
        The `begin_contour()` method begins recording vertices for the shape and
        `Py5Shape.end_contour()` stops recording. The vertices that define a negative
        shape must "wind" in the opposite direction from the exterior shape. First draw
        vertices for the exterior shape in clockwise order, then for internal shapes,
        draw vertices counterclockwise.

        These methods can only be used within a `Py5Shape.begin_shape()` &
        `Py5Shape.end_shape()` pair and transformations such as `Py5Shape.translate()`,
        `Py5Shape.rotate()`, and `Py5Shape.scale()` do not work within a
        `begin_contour()` & `Py5Shape.end_contour()` pair. It is also not possible to
        use other shapes, such as `ellipse()` or `rect()` within.

        This method can be used as a context manager to ensure that
        `Py5Shape.end_contour()` always gets called, as shown in the second example.
        """
        return self._instance.beginContour()

    @overload
    def begin_shape(self) -> None:
        """This method is used to start a custom shape created with the `create_shape()`
        function.

        Underlying Processing method: PShape.beginShape

        Methods
        -------

        You can use any of the following signatures:

         * begin_shape() -> None
         * begin_shape(kind: int, /) -> None

        Parameters
        ----------

        kind: int
            Either POINTS, LINES, TRIANGLES, TRIANGLE_FAN, TRIANGLE_STRIP, QUADS, or QUAD_STRIP

        Notes
        -----

        This method is used to start a custom shape created with the `create_shape()`
        function. It's always and only used with `create_shape()`.

        Drawing commands to a custom shape must always conclude with a call to the
        `Py5Shape.end_shape()` method. This method can be used as a context manager to
        ensure that `Py5Shape.end_shape()` always gets called, as shown in the second
        example. Use `Py5Shape.begin_closed_shape()` to create a context manager that
        will pass the `CLOSE` parameter to `end_shape()`, closing the shape.
        """
        pass

    @overload
    def begin_shape(self, kind: int, /) -> None:
        """This method is used to start a custom shape created with the `create_shape()`
        function.

        Underlying Processing method: PShape.beginShape

        Methods
        -------

        You can use any of the following signatures:

         * begin_shape() -> None
         * begin_shape(kind: int, /) -> None

        Parameters
        ----------

        kind: int
            Either POINTS, LINES, TRIANGLES, TRIANGLE_FAN, TRIANGLE_STRIP, QUADS, or QUAD_STRIP

        Notes
        -----

        This method is used to start a custom shape created with the `create_shape()`
        function. It's always and only used with `create_shape()`.

        Drawing commands to a custom shape must always conclude with a call to the
        `Py5Shape.end_shape()` method. This method can be used as a context manager to
        ensure that `Py5Shape.end_shape()` always gets called, as shown in the second
        example. Use `Py5Shape.begin_closed_shape()` to create a context manager that
        will pass the `CLOSE` parameter to `end_shape()`, closing the shape.
        """
        pass

    @_context_wrapper("end_shape")
    def begin_shape(self, *args):
        """This method is used to start a custom shape created with the `create_shape()`
        function.

        Underlying Processing method: PShape.beginShape

        Methods
        -------

        You can use any of the following signatures:

         * begin_shape() -> None
         * begin_shape(kind: int, /) -> None

        Parameters
        ----------

        kind: int
            Either POINTS, LINES, TRIANGLES, TRIANGLE_FAN, TRIANGLE_STRIP, QUADS, or QUAD_STRIP

        Notes
        -----

        This method is used to start a custom shape created with the `create_shape()`
        function. It's always and only used with `create_shape()`.

        Drawing commands to a custom shape must always conclude with a call to the
        `Py5Shape.end_shape()` method. This method can be used as a context manager to
        ensure that `Py5Shape.end_shape()` always gets called, as shown in the second
        example. Use `Py5Shape.begin_closed_shape()` to create a context manager that
        will pass the `CLOSE` parameter to `end_shape()`, closing the shape.
        """
        return self._instance.beginShape(*args)

    @overload
    def begin_closed_shape(self) -> None:
        """This method is used to start a custom closed shape created with the
        `create_shape()` function.

        Underlying Processing method: PShape.beginShape

        Methods
        -------

        You can use any of the following signatures:

         * begin_closed_shape() -> None
         * begin_closed_shape(kind: int, /) -> None

        Parameters
        ----------

        kind: int
            Either POINTS, LINES, TRIANGLES, TRIANGLE_FAN, TRIANGLE_STRIP, QUADS, or QUAD_STRIP

        Notes
        -----

        This method is used to start a custom closed shape created with the
        `create_shape()` function. It's always and only used with `create_shape()`.

        This method should only be used as a context manager, as shown in the example.
        When used as a context manager, this will ensure that `Py5Shape.end_shape()`
        always gets called, just like when using `Py5Shape.begin_shape()` as a context
        manager. The difference is that when exiting, the parameter `CLOSE` will be
        passed to `Py5Shape.end_shape()`, connecting the last vertex to the first. This
        will close the shape. If this method were to be used not as a context manager,
        it won't be able to close the shape by making the call to
        `Py5Shape.end_shape()`.
        """
        pass

    @overload
    def begin_closed_shape(self, kind: int, /) -> None:
        """This method is used to start a custom closed shape created with the
        `create_shape()` function.

        Underlying Processing method: PShape.beginShape

        Methods
        -------

        You can use any of the following signatures:

         * begin_closed_shape() -> None
         * begin_closed_shape(kind: int, /) -> None

        Parameters
        ----------

        kind: int
            Either POINTS, LINES, TRIANGLES, TRIANGLE_FAN, TRIANGLE_STRIP, QUADS, or QUAD_STRIP

        Notes
        -----

        This method is used to start a custom closed shape created with the
        `create_shape()` function. It's always and only used with `create_shape()`.

        This method should only be used as a context manager, as shown in the example.
        When used as a context manager, this will ensure that `Py5Shape.end_shape()`
        always gets called, just like when using `Py5Shape.begin_shape()` as a context
        manager. The difference is that when exiting, the parameter `CLOSE` will be
        passed to `Py5Shape.end_shape()`, connecting the last vertex to the first. This
        will close the shape. If this method were to be used not as a context manager,
        it won't be able to close the shape by making the call to
        `Py5Shape.end_shape()`.
        """
        pass

    @_context_wrapper("end_shape", exit_attr_args=("CLOSE",))
    def begin_closed_shape(self, *args):
        """This method is used to start a custom closed shape created with the
        `create_shape()` function.

        Underlying Processing method: PShape.beginShape

        Methods
        -------

        You can use any of the following signatures:

         * begin_closed_shape() -> None
         * begin_closed_shape(kind: int, /) -> None

        Parameters
        ----------

        kind: int
            Either POINTS, LINES, TRIANGLES, TRIANGLE_FAN, TRIANGLE_STRIP, QUADS, or QUAD_STRIP

        Notes
        -----

        This method is used to start a custom closed shape created with the
        `create_shape()` function. It's always and only used with `create_shape()`.

        This method should only be used as a context manager, as shown in the example.
        When used as a context manager, this will ensure that `Py5Shape.end_shape()`
        always gets called, just like when using `Py5Shape.begin_shape()` as a context
        manager. The difference is that when exiting, the parameter `CLOSE` will be
        passed to `Py5Shape.end_shape()`, connecting the last vertex to the first. This
        will close the shape. If this method were to be used not as a context manager,
        it won't be able to close the shape by making the call to
        `Py5Shape.end_shape()`.
        """
        return self._instance.beginShape(*args)

    def bezier_detail(self, detail: int, /) -> None:
        """Sets a `Py5Shape` object's resolution at which Beziers display.

        Underlying Processing method: PShape.bezierDetail

        Parameters
        ----------

        detail: int
            resolution of the curves

        Notes
        -----

        Sets a `Py5Shape` object's resolution at which Beziers display. The default
        value is 20.

        Drawing 2D bezier curves requires using the `P2D` renderer and drawing 3D bezier
        curves requires using the `P3D` renderer. When drawing directly with `Py5Shape`
        objects, bezier curves do not work at all using the default renderer.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair.
        """
        return self._instance.bezierDetail(detail)

    @overload
    def bezier_vertex(
        self, x2: float, y2: float, x3: float, y3: float, x4: float, y4: float, /
    ) -> None:
        """Specifies a `Py5Shape` object's vertex coordinates for Bezier curves.

        Underlying Processing method: PShape.bezierVertex

        Methods
        -------

        You can use any of the following signatures:

         * bezier_vertex(x2: float, y2: float, x3: float, y3: float, x4: float, y4: float, /) -> None
         * bezier_vertex(x2: float, y2: float, z2: float, x3: float, y3: float, z3: float, x4: float, y4: float, z4: float, /) -> None

        Parameters
        ----------

        x2: float
            the x-coordinate of the 1st control point

        x3: float
            the x-coordinate of the 2nd control point

        x4: float
            the x-coordinate of the anchor point

        y2: float
            the y-coordinate of the 1st control point

        y3: float
            the y-coordinate of the 2nd control point

        y4: float
            the y-coordinate of the anchor point

        z2: float
            the z-coordinate of the 1st control point

        z3: float
            the z-coordinate of the 2nd control point

        z4: float
            the z-coordinate of the anchor point

        Notes
        -----

        Specifies a `Py5Shape` object's vertex coordinates for Bezier curves. Each call
        to `bezier_vertex()` defines the position of two control points and one anchor
        point of a Bezier curve, adding a new segment to a line or shape. The first time
        `bezier_vertex()` is used within a `Py5Shape.begin_shape()` call, it must be
        prefaced with a call to `Py5Shape.vertex()` to set the first anchor point. This
        method must be used between `Py5Shape.begin_shape()` and `Py5Shape.end_shape()`
        and only when there is no `MODE` parameter specified to
        `Py5Shape.begin_shape()`.

        Drawing 2D bezier curves requires using the `P2D` renderer and drawing 3D bezier
        curves requires using the `P3D` renderer. When drawing directly with `Py5Shape`
        objects, bezier curves do not work at all using the default renderer.
        """
        pass

    @overload
    def bezier_vertex(
        self,
        x2: float,
        y2: float,
        z2: float,
        x3: float,
        y3: float,
        z3: float,
        x4: float,
        y4: float,
        z4: float,
        /,
    ) -> None:
        """Specifies a `Py5Shape` object's vertex coordinates for Bezier curves.

        Underlying Processing method: PShape.bezierVertex

        Methods
        -------

        You can use any of the following signatures:

         * bezier_vertex(x2: float, y2: float, x3: float, y3: float, x4: float, y4: float, /) -> None
         * bezier_vertex(x2: float, y2: float, z2: float, x3: float, y3: float, z3: float, x4: float, y4: float, z4: float, /) -> None

        Parameters
        ----------

        x2: float
            the x-coordinate of the 1st control point

        x3: float
            the x-coordinate of the 2nd control point

        x4: float
            the x-coordinate of the anchor point

        y2: float
            the y-coordinate of the 1st control point

        y3: float
            the y-coordinate of the 2nd control point

        y4: float
            the y-coordinate of the anchor point

        z2: float
            the z-coordinate of the 1st control point

        z3: float
            the z-coordinate of the 2nd control point

        z4: float
            the z-coordinate of the anchor point

        Notes
        -----

        Specifies a `Py5Shape` object's vertex coordinates for Bezier curves. Each call
        to `bezier_vertex()` defines the position of two control points and one anchor
        point of a Bezier curve, adding a new segment to a line or shape. The first time
        `bezier_vertex()` is used within a `Py5Shape.begin_shape()` call, it must be
        prefaced with a call to `Py5Shape.vertex()` to set the first anchor point. This
        method must be used between `Py5Shape.begin_shape()` and `Py5Shape.end_shape()`
        and only when there is no `MODE` parameter specified to
        `Py5Shape.begin_shape()`.

        Drawing 2D bezier curves requires using the `P2D` renderer and drawing 3D bezier
        curves requires using the `P3D` renderer. When drawing directly with `Py5Shape`
        objects, bezier curves do not work at all using the default renderer.
        """
        pass

    def bezier_vertex(self, *args):
        """Specifies a `Py5Shape` object's vertex coordinates for Bezier curves.

        Underlying Processing method: PShape.bezierVertex

        Methods
        -------

        You can use any of the following signatures:

         * bezier_vertex(x2: float, y2: float, x3: float, y3: float, x4: float, y4: float, /) -> None
         * bezier_vertex(x2: float, y2: float, z2: float, x3: float, y3: float, z3: float, x4: float, y4: float, z4: float, /) -> None

        Parameters
        ----------

        x2: float
            the x-coordinate of the 1st control point

        x3: float
            the x-coordinate of the 2nd control point

        x4: float
            the x-coordinate of the anchor point

        y2: float
            the y-coordinate of the 1st control point

        y3: float
            the y-coordinate of the 2nd control point

        y4: float
            the y-coordinate of the anchor point

        z2: float
            the z-coordinate of the 1st control point

        z3: float
            the z-coordinate of the 2nd control point

        z4: float
            the z-coordinate of the anchor point

        Notes
        -----

        Specifies a `Py5Shape` object's vertex coordinates for Bezier curves. Each call
        to `bezier_vertex()` defines the position of two control points and one anchor
        point of a Bezier curve, adding a new segment to a line or shape. The first time
        `bezier_vertex()` is used within a `Py5Shape.begin_shape()` call, it must be
        prefaced with a call to `Py5Shape.vertex()` to set the first anchor point. This
        method must be used between `Py5Shape.begin_shape()` and `Py5Shape.end_shape()`
        and only when there is no `MODE` parameter specified to
        `Py5Shape.begin_shape()`.

        Drawing 2D bezier curves requires using the `P2D` renderer and drawing 3D bezier
        curves requires using the `P3D` renderer. When drawing directly with `Py5Shape`
        objects, bezier curves do not work at all using the default renderer.
        """
        return self._instance.bezierVertex(*args)

    @overload
    def color_mode(self, mode: int, /) -> None:
        """Changes the way a `Py5Shape` object interprets color data.

        Underlying Processing method: PShape.colorMode

        Methods
        -------

        You can use any of the following signatures:

         * color_mode(mode: int, /) -> None
         * color_mode(mode: int, max: float, /) -> None
         * color_mode(mode: int, max_x: float, max_y: float, max_z: float, /) -> None
         * color_mode(mode: int, max_x: float, max_y: float, max_z: float, max_a: float, /) -> None

        Parameters
        ----------

        max: float
            range for all color elements

        max_a: float
            range for the alpha

        max_x: float
            range for the red or hue depending on the current color mode

        max_y: float
            range for the green or saturation depending on the current color mode

        max_z: float
            range for the blue or brightness depending on the current color mode

        mode: int
            Either RGB or HSB, corresponding to Red/Green/Blue and Hue/Saturation/Brightness

        Notes
        -----

        Changes the way a `Py5Shape` object interprets color data. By default, the
        parameters for `Py5Shape.fill()` and `Py5Shape.stroke()` are defined by values
        between 0 and 255 using the `RGB` color model. The `color_mode()` function is
        used to change the numerical range used for specifying colors and to switch
        color systems. For example, calling `color_mode(RGB, 1.0)` will specify that
        values are specified between 0 and 1. The limits for defining colors are altered
        by setting the parameters `max`, `max_x`, `max_y`, `max_z`, and `max_a`.

        After changing the range of values for colors with code like `color_mode(HSB,
        360, 100, 100)`, those ranges remain in use until they are explicitly changed
        again. For example, after running `color_mode(HSB, 360, 100, 100)` and then
        changing back to `color_mode(RGB)`, the range for R will be 0 to 360 and the
        range for G and B will be 0 to 100. To avoid this, be explicit about the ranges
        when changing the color mode. For instance, instead of `color_mode(RGB)`, write
        `color_mode(RGB, 255, 255, 255)`.
        """
        pass

    @overload
    def color_mode(self, mode: int, max: float, /) -> None:
        """Changes the way a `Py5Shape` object interprets color data.

        Underlying Processing method: PShape.colorMode

        Methods
        -------

        You can use any of the following signatures:

         * color_mode(mode: int, /) -> None
         * color_mode(mode: int, max: float, /) -> None
         * color_mode(mode: int, max_x: float, max_y: float, max_z: float, /) -> None
         * color_mode(mode: int, max_x: float, max_y: float, max_z: float, max_a: float, /) -> None

        Parameters
        ----------

        max: float
            range for all color elements

        max_a: float
            range for the alpha

        max_x: float
            range for the red or hue depending on the current color mode

        max_y: float
            range for the green or saturation depending on the current color mode

        max_z: float
            range for the blue or brightness depending on the current color mode

        mode: int
            Either RGB or HSB, corresponding to Red/Green/Blue and Hue/Saturation/Brightness

        Notes
        -----

        Changes the way a `Py5Shape` object interprets color data. By default, the
        parameters for `Py5Shape.fill()` and `Py5Shape.stroke()` are defined by values
        between 0 and 255 using the `RGB` color model. The `color_mode()` function is
        used to change the numerical range used for specifying colors and to switch
        color systems. For example, calling `color_mode(RGB, 1.0)` will specify that
        values are specified between 0 and 1. The limits for defining colors are altered
        by setting the parameters `max`, `max_x`, `max_y`, `max_z`, and `max_a`.

        After changing the range of values for colors with code like `color_mode(HSB,
        360, 100, 100)`, those ranges remain in use until they are explicitly changed
        again. For example, after running `color_mode(HSB, 360, 100, 100)` and then
        changing back to `color_mode(RGB)`, the range for R will be 0 to 360 and the
        range for G and B will be 0 to 100. To avoid this, be explicit about the ranges
        when changing the color mode. For instance, instead of `color_mode(RGB)`, write
        `color_mode(RGB, 255, 255, 255)`.
        """
        pass

    @overload
    def color_mode(
        self, mode: int, max_x: float, max_y: float, max_z: float, /
    ) -> None:
        """Changes the way a `Py5Shape` object interprets color data.

        Underlying Processing method: PShape.colorMode

        Methods
        -------

        You can use any of the following signatures:

         * color_mode(mode: int, /) -> None
         * color_mode(mode: int, max: float, /) -> None
         * color_mode(mode: int, max_x: float, max_y: float, max_z: float, /) -> None
         * color_mode(mode: int, max_x: float, max_y: float, max_z: float, max_a: float, /) -> None

        Parameters
        ----------

        max: float
            range for all color elements

        max_a: float
            range for the alpha

        max_x: float
            range for the red or hue depending on the current color mode

        max_y: float
            range for the green or saturation depending on the current color mode

        max_z: float
            range for the blue or brightness depending on the current color mode

        mode: int
            Either RGB or HSB, corresponding to Red/Green/Blue and Hue/Saturation/Brightness

        Notes
        -----

        Changes the way a `Py5Shape` object interprets color data. By default, the
        parameters for `Py5Shape.fill()` and `Py5Shape.stroke()` are defined by values
        between 0 and 255 using the `RGB` color model. The `color_mode()` function is
        used to change the numerical range used for specifying colors and to switch
        color systems. For example, calling `color_mode(RGB, 1.0)` will specify that
        values are specified between 0 and 1. The limits for defining colors are altered
        by setting the parameters `max`, `max_x`, `max_y`, `max_z`, and `max_a`.

        After changing the range of values for colors with code like `color_mode(HSB,
        360, 100, 100)`, those ranges remain in use until they are explicitly changed
        again. For example, after running `color_mode(HSB, 360, 100, 100)` and then
        changing back to `color_mode(RGB)`, the range for R will be 0 to 360 and the
        range for G and B will be 0 to 100. To avoid this, be explicit about the ranges
        when changing the color mode. For instance, instead of `color_mode(RGB)`, write
        `color_mode(RGB, 255, 255, 255)`.
        """
        pass

    @overload
    def color_mode(
        self, mode: int, max_x: float, max_y: float, max_z: float, max_a: float, /
    ) -> None:
        """Changes the way a `Py5Shape` object interprets color data.

        Underlying Processing method: PShape.colorMode

        Methods
        -------

        You can use any of the following signatures:

         * color_mode(mode: int, /) -> None
         * color_mode(mode: int, max: float, /) -> None
         * color_mode(mode: int, max_x: float, max_y: float, max_z: float, /) -> None
         * color_mode(mode: int, max_x: float, max_y: float, max_z: float, max_a: float, /) -> None

        Parameters
        ----------

        max: float
            range for all color elements

        max_a: float
            range for the alpha

        max_x: float
            range for the red or hue depending on the current color mode

        max_y: float
            range for the green or saturation depending on the current color mode

        max_z: float
            range for the blue or brightness depending on the current color mode

        mode: int
            Either RGB or HSB, corresponding to Red/Green/Blue and Hue/Saturation/Brightness

        Notes
        -----

        Changes the way a `Py5Shape` object interprets color data. By default, the
        parameters for `Py5Shape.fill()` and `Py5Shape.stroke()` are defined by values
        between 0 and 255 using the `RGB` color model. The `color_mode()` function is
        used to change the numerical range used for specifying colors and to switch
        color systems. For example, calling `color_mode(RGB, 1.0)` will specify that
        values are specified between 0 and 1. The limits for defining colors are altered
        by setting the parameters `max`, `max_x`, `max_y`, `max_z`, and `max_a`.

        After changing the range of values for colors with code like `color_mode(HSB,
        360, 100, 100)`, those ranges remain in use until they are explicitly changed
        again. For example, after running `color_mode(HSB, 360, 100, 100)` and then
        changing back to `color_mode(RGB)`, the range for R will be 0 to 360 and the
        range for G and B will be 0 to 100. To avoid this, be explicit about the ranges
        when changing the color mode. For instance, instead of `color_mode(RGB)`, write
        `color_mode(RGB, 255, 255, 255)`.
        """
        pass

    def color_mode(self, *args):
        """Changes the way a `Py5Shape` object interprets color data.

        Underlying Processing method: PShape.colorMode

        Methods
        -------

        You can use any of the following signatures:

         * color_mode(mode: int, /) -> None
         * color_mode(mode: int, max: float, /) -> None
         * color_mode(mode: int, max_x: float, max_y: float, max_z: float, /) -> None
         * color_mode(mode: int, max_x: float, max_y: float, max_z: float, max_a: float, /) -> None

        Parameters
        ----------

        max: float
            range for all color elements

        max_a: float
            range for the alpha

        max_x: float
            range for the red or hue depending on the current color mode

        max_y: float
            range for the green or saturation depending on the current color mode

        max_z: float
            range for the blue or brightness depending on the current color mode

        mode: int
            Either RGB or HSB, corresponding to Red/Green/Blue and Hue/Saturation/Brightness

        Notes
        -----

        Changes the way a `Py5Shape` object interprets color data. By default, the
        parameters for `Py5Shape.fill()` and `Py5Shape.stroke()` are defined by values
        between 0 and 255 using the `RGB` color model. The `color_mode()` function is
        used to change the numerical range used for specifying colors and to switch
        color systems. For example, calling `color_mode(RGB, 1.0)` will specify that
        values are specified between 0 and 1. The limits for defining colors are altered
        by setting the parameters `max`, `max_x`, `max_y`, `max_z`, and `max_a`.

        After changing the range of values for colors with code like `color_mode(HSB,
        360, 100, 100)`, those ranges remain in use until they are explicitly changed
        again. For example, after running `color_mode(HSB, 360, 100, 100)` and then
        changing back to `color_mode(RGB)`, the range for R will be 0 to 360 and the
        range for G and B will be 0 to 100. To avoid this, be explicit about the ranges
        when changing the color mode. For instance, instead of `color_mode(RGB)`, write
        `color_mode(RGB, 255, 255, 255)`.
        """
        return self._instance.colorMode(*args)

    def contains(self, x: float, y: float, /) -> bool:
        """Boolean value reflecting if the given coordinates are or are not contained
        within the `Py5Shape` object.

        Underlying Processing method: PShape.contains

        Parameters
        ----------

        x: float
            x-coordinate

        y: float
            y-coordinate

        Notes
        -----

        Boolean value reflecting if the given coordinates are or are not contained
        within the `Py5Shape` object. This method will only work for a `Py5Shape` object
        that is a `PATH` shape or a `GROUP` of `PATH` shapes. Use
        `Py5Shape.get_family()` to determine how a `Py5Shape` object was defined.

        This method uses a coordinate system that is unique to the shape and how the
        paths were created. To get the range of relevant coordinates, start by finding
        the minimum and maximum values for the vertices using `Py5Shape.get_vertex_x()`
        and `Py5Shape.get_vertex_y()`. Do not use `Py5Shape.get_width()` or
        `Py5Shape.get_height()`.
        """
        return self._instance.contains(x, y)

    def curve_detail(self, detail: int, /) -> None:
        """Sets the resolution at which a `Py5Shape` object's curves display.

        Underlying Processing method: PShape.curveDetail

        Parameters
        ----------

        detail: int
            resolution of the curves

        Notes
        -----

        Sets the resolution at which a `Py5Shape` object's curves display. The default
        value is 20.

        Drawing 2D curves requires using the `P2D` renderer and drawing 3D curves
        requires using the `P3D` renderer. When drawing directly with `Py5Shape`
        objects, curves do not work at all using the default renderer.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair.
        """
        return self._instance.curveDetail(detail)

    def curve_tightness(self, tightness: float, /) -> None:
        """Modifies the quality of a `Py5Shape` object's forms created with
        `Py5Shape.curve_vertex()`.

        Underlying Processing method: PShape.curveTightness

        Parameters
        ----------

        tightness: float
            amount of deformation from the original vertices

        Notes
        -----

        Modifies the quality of a `Py5Shape` object's forms created with
        `Py5Shape.curve_vertex()`. The parameter `tightness` determines how the curve
        fits to the vertex points. The value 0.0 is the default value for `tightness`
        (this value defines the curves to be Catmull-Rom splines) and the value 1.0
        connects all the points with straight lines. Values within the range -5.0 and
        5.0 will deform the curves but will leave them recognizable and as values
        increase in magnitude, they will continue to deform.

        Drawing 2D curves requires using the `P2D` renderer and drawing 3D curves
        requires using the `P3D` renderer. When drawing directly with `Py5Shape`
        objects, curves do not work at all using the default renderer.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair.
        """
        return self._instance.curveTightness(tightness)

    @overload
    def curve_vertex(self, x: float, y: float, /) -> None:
        """Specifies a `Py5Shape` object's vertex coordinates for curves.

        Underlying Processing method: PShape.curveVertex

        Methods
        -------

        You can use any of the following signatures:

         * curve_vertex(x: float, y: float, /) -> None
         * curve_vertex(x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        x: float
            the x-coordinate of the vertex

        y: float
            the y-coordinate of the vertex

        z: float
            the z-coordinate of the vertex

        Notes
        -----

        Specifies a `Py5Shape` object's vertex coordinates for curves. This method may
        only be used between `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` and
        only when there is no `MODE` parameter specified to `Py5Shape.begin_shape()`.
        The first and last points in a series of `curve_vertex()` lines will be used to
        guide the beginning and end of the curve. A minimum of four points is required
        to draw a tiny curve between the second and third points. Adding a fifth point
        with `curve_vertex()` will draw the curve between the second, third, and fourth
        points. The `curve_vertex()` method is an implementation of Catmull-Rom splines.

        Drawing 2D curves requires using the `P2D` renderer and drawing 3D curves
        requires using the `P3D` renderer. When drawing directly with `Py5Shape`
        objects, curves do not work at all using the default renderer.
        """
        pass

    @overload
    def curve_vertex(self, x: float, y: float, z: float, /) -> None:
        """Specifies a `Py5Shape` object's vertex coordinates for curves.

        Underlying Processing method: PShape.curveVertex

        Methods
        -------

        You can use any of the following signatures:

         * curve_vertex(x: float, y: float, /) -> None
         * curve_vertex(x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        x: float
            the x-coordinate of the vertex

        y: float
            the y-coordinate of the vertex

        z: float
            the z-coordinate of the vertex

        Notes
        -----

        Specifies a `Py5Shape` object's vertex coordinates for curves. This method may
        only be used between `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` and
        only when there is no `MODE` parameter specified to `Py5Shape.begin_shape()`.
        The first and last points in a series of `curve_vertex()` lines will be used to
        guide the beginning and end of the curve. A minimum of four points is required
        to draw a tiny curve between the second and third points. Adding a fifth point
        with `curve_vertex()` will draw the curve between the second, third, and fourth
        points. The `curve_vertex()` method is an implementation of Catmull-Rom splines.

        Drawing 2D curves requires using the `P2D` renderer and drawing 3D curves
        requires using the `P3D` renderer. When drawing directly with `Py5Shape`
        objects, curves do not work at all using the default renderer.
        """
        pass

    def curve_vertex(self, *args):
        """Specifies a `Py5Shape` object's vertex coordinates for curves.

        Underlying Processing method: PShape.curveVertex

        Methods
        -------

        You can use any of the following signatures:

         * curve_vertex(x: float, y: float, /) -> None
         * curve_vertex(x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        x: float
            the x-coordinate of the vertex

        y: float
            the y-coordinate of the vertex

        z: float
            the z-coordinate of the vertex

        Notes
        -----

        Specifies a `Py5Shape` object's vertex coordinates for curves. This method may
        only be used between `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` and
        only when there is no `MODE` parameter specified to `Py5Shape.begin_shape()`.
        The first and last points in a series of `curve_vertex()` lines will be used to
        guide the beginning and end of the curve. A minimum of four points is required
        to draw a tiny curve between the second and third points. Adding a fifth point
        with `curve_vertex()` will draw the curve between the second, third, and fourth
        points. The `curve_vertex()` method is an implementation of Catmull-Rom splines.

        Drawing 2D curves requires using the `P2D` renderer and drawing 3D curves
        requires using the `P3D` renderer. When drawing directly with `Py5Shape`
        objects, curves do not work at all using the default renderer.
        """
        return self._instance.curveVertex(*args)

    def disable_style(self) -> None:
        """Disables the shape's style data and uses py5's current styles.

        Underlying Processing method: PShape.disableStyle

        Notes
        -----

        Disables the shape's style data and uses py5's current styles. Styles include
        attributes such as colors, stroke weight, and stroke joints.
        """
        return self._instance.disableStyle()

    @overload
    def emissive(self, gray: float, /) -> None:
        """Sets the emissive color of a `Py5Shape` object's material.

        Underlying Processing method: PShape.emissive

        Methods
        -------

        You can use any of the following signatures:

         * emissive(gray: float, /) -> None
         * emissive(rgb: int, /) -> None
         * emissive(x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        gray: float
            value between black and white, by default 0 to 255

        rgb: int
            color to set

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the emissive color of a `Py5Shape` object's material. Use in combination
        with `Py5Shape.ambient()`, `Py5Shape.specular()`, and `Py5Shape.shininess()` to
        set the material properties of a `Py5Shape` object.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair. The emissive color setting will be applied to
        vertices added after the call to this method.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def emissive(self, x: float, y: float, z: float, /) -> None:
        """Sets the emissive color of a `Py5Shape` object's material.

        Underlying Processing method: PShape.emissive

        Methods
        -------

        You can use any of the following signatures:

         * emissive(gray: float, /) -> None
         * emissive(rgb: int, /) -> None
         * emissive(x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        gray: float
            value between black and white, by default 0 to 255

        rgb: int
            color to set

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the emissive color of a `Py5Shape` object's material. Use in combination
        with `Py5Shape.ambient()`, `Py5Shape.specular()`, and `Py5Shape.shininess()` to
        set the material properties of a `Py5Shape` object.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair. The emissive color setting will be applied to
        vertices added after the call to this method.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def emissive(self, rgb: int, /) -> None:
        """Sets the emissive color of a `Py5Shape` object's material.

        Underlying Processing method: PShape.emissive

        Methods
        -------

        You can use any of the following signatures:

         * emissive(gray: float, /) -> None
         * emissive(rgb: int, /) -> None
         * emissive(x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        gray: float
            value between black and white, by default 0 to 255

        rgb: int
            color to set

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the emissive color of a `Py5Shape` object's material. Use in combination
        with `Py5Shape.ambient()`, `Py5Shape.specular()`, and `Py5Shape.shininess()` to
        set the material properties of a `Py5Shape` object.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair. The emissive color setting will be applied to
        vertices added after the call to this method.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @_convert_hex_color()
    def emissive(self, *args):
        """Sets the emissive color of a `Py5Shape` object's material.

        Underlying Processing method: PShape.emissive

        Methods
        -------

        You can use any of the following signatures:

         * emissive(gray: float, /) -> None
         * emissive(rgb: int, /) -> None
         * emissive(x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        gray: float
            value between black and white, by default 0 to 255

        rgb: int
            color to set

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the emissive color of a `Py5Shape` object's material. Use in combination
        with `Py5Shape.ambient()`, `Py5Shape.specular()`, and `Py5Shape.shininess()` to
        set the material properties of a `Py5Shape` object.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair. The emissive color setting will be applied to
        vertices added after the call to this method.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        return self._instance.emissive(*args)

    def enable_style(self) -> None:
        """Enables the shape's style data and ignores py5's current styles.

        Underlying Processing method: PShape.enableStyle

        Notes
        -----

        Enables the shape's style data and ignores py5's current styles. Styles include
        attributes such as colors, stroke weight, and stroke joints.
        """
        return self._instance.enableStyle()

    def end_contour(self) -> None:
        """Use the `Py5Shape.begin_contour()` and `end_contour()` methods to create
        negative shapes within a `Py5Shape` object such as the center of the letter 'O'.

        Underlying Processing method: PShape.endContour

        Notes
        -----

        Use the `Py5Shape.begin_contour()` and `end_contour()` methods to create
        negative shapes within a `Py5Shape` object such as the center of the letter 'O'.
        The `Py5Shape.begin_contour()` method begins recording vertices for the shape
        and `end_contour()` stops recording. The vertices that define a negative shape
        must "wind" in the opposite direction from the exterior shape. First draw
        vertices for the exterior shape in clockwise order, then for internal shapes,
        draw vertices counterclockwise.

        These methods can only be used within a `Py5Shape.begin_shape()` &
        `Py5Shape.end_shape()` pair and transformations such as `Py5Shape.translate()`,
        `Py5Shape.rotate()`, and `Py5Shape.scale()` do not work within a
        `Py5Shape.begin_contour()` & `end_contour()` pair. It is also not possible to
        use other shapes, such as `ellipse()` or `rect()` within.
        """
        return self._instance.endContour()

    @overload
    def end_shape(self) -> None:
        """This method is used to complete a custom shape created with the `create_shape()`
        function.

        Underlying Processing method: PShape.endShape

        Methods
        -------

        You can use any of the following signatures:

         * end_shape() -> None
         * end_shape(mode: int, /) -> None

        Parameters
        ----------

        mode: int
            Either OPEN or CLOSE

        Notes
        -----

        This method is used to complete a custom shape created with the `create_shape()`
        function. It's always and only used with `create_shape()`.
        """
        pass

    @overload
    def end_shape(self, mode: int, /) -> None:
        """This method is used to complete a custom shape created with the `create_shape()`
        function.

        Underlying Processing method: PShape.endShape

        Methods
        -------

        You can use any of the following signatures:

         * end_shape() -> None
         * end_shape(mode: int, /) -> None

        Parameters
        ----------

        mode: int
            Either OPEN or CLOSE

        Notes
        -----

        This method is used to complete a custom shape created with the `create_shape()`
        function. It's always and only used with `create_shape()`.
        """
        pass

    def end_shape(self, *args):
        """This method is used to complete a custom shape created with the `create_shape()`
        function.

        Underlying Processing method: PShape.endShape

        Methods
        -------

        You can use any of the following signatures:

         * end_shape() -> None
         * end_shape(mode: int, /) -> None

        Parameters
        ----------

        mode: int
            Either OPEN or CLOSE

        Notes
        -----

        This method is used to complete a custom shape created with the `create_shape()`
        function. It's always and only used with `create_shape()`.
        """
        return self._instance.endShape(*args)

    @overload
    def fill(self, gray: float, /) -> None:
        """Sets the color used to fill the `Py5Shape` object.

        Underlying Processing method: PShape.fill

        Methods
        -------

        You can use any of the following signatures:

         * fill(gray: float, /) -> None
         * fill(gray: float, alpha: float, /) -> None
         * fill(rgb: int, /) -> None
         * fill(rgb: int, alpha: float, /) -> None
         * fill(x: float, y: float, z: float, /) -> None
         * fill(x: float, y: float, z: float, a: float, /) -> None

        Parameters
        ----------

        a: float
            opacity of the fill

        alpha: float
            opacity of the fill

        gray: float
            number specifying value between white and black

        rgb: int
            color variable or hex value

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the color used to fill the `Py5Shape` object. For example, if you run
        `fill(204, 102, 0)`, the shape will be filled with orange. This color is either
        specified in terms of the `RGB` or `HSB` color depending on the current
        `color_mode()`. The default color space is `RGB`, with each value in the range
        from 0 to 255.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair.

        When using hexadecimal notation to specify a color, use "`0x`" before the values
        (e.g., `0xFFCCFFAA`). The hexadecimal value must be specified with eight
        characters; the first two characters define the alpha component, and the
        remainder define the red, green, and blue components.

        When using web color notation to specify a color, create a string beginning with
        the "`#`" character followed by three, four, six, or eight characters. The
        example colors `"#D93"` and `"#DD9933"` specify red, green, and blue values (in
        that order) for the color and assume the color has no transparency. The example
        colors `"#D93F"` and `"#DD9933FF"` specify red, green, blue, and alpha values
        (in that order) for the color. Notice that in web color notation the alpha
        channel is last, which is consistent with CSS colors, and in hexadecimal
        notation the alpha channel is first, which is consistent with Processing color
        values.

        The value for the "gray" parameter must be less than or equal to the current
        maximum value as specified by `color_mode()`. The default maximum value is 255.

        To change the color of a `Py5Shape` object's image or a texture, use
        `Py5Shape.tint()`.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def fill(self, gray: float, alpha: float, /) -> None:
        """Sets the color used to fill the `Py5Shape` object.

        Underlying Processing method: PShape.fill

        Methods
        -------

        You can use any of the following signatures:

         * fill(gray: float, /) -> None
         * fill(gray: float, alpha: float, /) -> None
         * fill(rgb: int, /) -> None
         * fill(rgb: int, alpha: float, /) -> None
         * fill(x: float, y: float, z: float, /) -> None
         * fill(x: float, y: float, z: float, a: float, /) -> None

        Parameters
        ----------

        a: float
            opacity of the fill

        alpha: float
            opacity of the fill

        gray: float
            number specifying value between white and black

        rgb: int
            color variable or hex value

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the color used to fill the `Py5Shape` object. For example, if you run
        `fill(204, 102, 0)`, the shape will be filled with orange. This color is either
        specified in terms of the `RGB` or `HSB` color depending on the current
        `color_mode()`. The default color space is `RGB`, with each value in the range
        from 0 to 255.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair.

        When using hexadecimal notation to specify a color, use "`0x`" before the values
        (e.g., `0xFFCCFFAA`). The hexadecimal value must be specified with eight
        characters; the first two characters define the alpha component, and the
        remainder define the red, green, and blue components.

        When using web color notation to specify a color, create a string beginning with
        the "`#`" character followed by three, four, six, or eight characters. The
        example colors `"#D93"` and `"#DD9933"` specify red, green, and blue values (in
        that order) for the color and assume the color has no transparency. The example
        colors `"#D93F"` and `"#DD9933FF"` specify red, green, blue, and alpha values
        (in that order) for the color. Notice that in web color notation the alpha
        channel is last, which is consistent with CSS colors, and in hexadecimal
        notation the alpha channel is first, which is consistent with Processing color
        values.

        The value for the "gray" parameter must be less than or equal to the current
        maximum value as specified by `color_mode()`. The default maximum value is 255.

        To change the color of a `Py5Shape` object's image or a texture, use
        `Py5Shape.tint()`.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def fill(self, x: float, y: float, z: float, /) -> None:
        """Sets the color used to fill the `Py5Shape` object.

        Underlying Processing method: PShape.fill

        Methods
        -------

        You can use any of the following signatures:

         * fill(gray: float, /) -> None
         * fill(gray: float, alpha: float, /) -> None
         * fill(rgb: int, /) -> None
         * fill(rgb: int, alpha: float, /) -> None
         * fill(x: float, y: float, z: float, /) -> None
         * fill(x: float, y: float, z: float, a: float, /) -> None

        Parameters
        ----------

        a: float
            opacity of the fill

        alpha: float
            opacity of the fill

        gray: float
            number specifying value between white and black

        rgb: int
            color variable or hex value

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the color used to fill the `Py5Shape` object. For example, if you run
        `fill(204, 102, 0)`, the shape will be filled with orange. This color is either
        specified in terms of the `RGB` or `HSB` color depending on the current
        `color_mode()`. The default color space is `RGB`, with each value in the range
        from 0 to 255.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair.

        When using hexadecimal notation to specify a color, use "`0x`" before the values
        (e.g., `0xFFCCFFAA`). The hexadecimal value must be specified with eight
        characters; the first two characters define the alpha component, and the
        remainder define the red, green, and blue components.

        When using web color notation to specify a color, create a string beginning with
        the "`#`" character followed by three, four, six, or eight characters. The
        example colors `"#D93"` and `"#DD9933"` specify red, green, and blue values (in
        that order) for the color and assume the color has no transparency. The example
        colors `"#D93F"` and `"#DD9933FF"` specify red, green, blue, and alpha values
        (in that order) for the color. Notice that in web color notation the alpha
        channel is last, which is consistent with CSS colors, and in hexadecimal
        notation the alpha channel is first, which is consistent with Processing color
        values.

        The value for the "gray" parameter must be less than or equal to the current
        maximum value as specified by `color_mode()`. The default maximum value is 255.

        To change the color of a `Py5Shape` object's image or a texture, use
        `Py5Shape.tint()`.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def fill(self, x: float, y: float, z: float, a: float, /) -> None:
        """Sets the color used to fill the `Py5Shape` object.

        Underlying Processing method: PShape.fill

        Methods
        -------

        You can use any of the following signatures:

         * fill(gray: float, /) -> None
         * fill(gray: float, alpha: float, /) -> None
         * fill(rgb: int, /) -> None
         * fill(rgb: int, alpha: float, /) -> None
         * fill(x: float, y: float, z: float, /) -> None
         * fill(x: float, y: float, z: float, a: float, /) -> None

        Parameters
        ----------

        a: float
            opacity of the fill

        alpha: float
            opacity of the fill

        gray: float
            number specifying value between white and black

        rgb: int
            color variable or hex value

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the color used to fill the `Py5Shape` object. For example, if you run
        `fill(204, 102, 0)`, the shape will be filled with orange. This color is either
        specified in terms of the `RGB` or `HSB` color depending on the current
        `color_mode()`. The default color space is `RGB`, with each value in the range
        from 0 to 255.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair.

        When using hexadecimal notation to specify a color, use "`0x`" before the values
        (e.g., `0xFFCCFFAA`). The hexadecimal value must be specified with eight
        characters; the first two characters define the alpha component, and the
        remainder define the red, green, and blue components.

        When using web color notation to specify a color, create a string beginning with
        the "`#`" character followed by three, four, six, or eight characters. The
        example colors `"#D93"` and `"#DD9933"` specify red, green, and blue values (in
        that order) for the color and assume the color has no transparency. The example
        colors `"#D93F"` and `"#DD9933FF"` specify red, green, blue, and alpha values
        (in that order) for the color. Notice that in web color notation the alpha
        channel is last, which is consistent with CSS colors, and in hexadecimal
        notation the alpha channel is first, which is consistent with Processing color
        values.

        The value for the "gray" parameter must be less than or equal to the current
        maximum value as specified by `color_mode()`. The default maximum value is 255.

        To change the color of a `Py5Shape` object's image or a texture, use
        `Py5Shape.tint()`.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def fill(self, rgb: int, /) -> None:
        """Sets the color used to fill the `Py5Shape` object.

        Underlying Processing method: PShape.fill

        Methods
        -------

        You can use any of the following signatures:

         * fill(gray: float, /) -> None
         * fill(gray: float, alpha: float, /) -> None
         * fill(rgb: int, /) -> None
         * fill(rgb: int, alpha: float, /) -> None
         * fill(x: float, y: float, z: float, /) -> None
         * fill(x: float, y: float, z: float, a: float, /) -> None

        Parameters
        ----------

        a: float
            opacity of the fill

        alpha: float
            opacity of the fill

        gray: float
            number specifying value between white and black

        rgb: int
            color variable or hex value

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the color used to fill the `Py5Shape` object. For example, if you run
        `fill(204, 102, 0)`, the shape will be filled with orange. This color is either
        specified in terms of the `RGB` or `HSB` color depending on the current
        `color_mode()`. The default color space is `RGB`, with each value in the range
        from 0 to 255.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair.

        When using hexadecimal notation to specify a color, use "`0x`" before the values
        (e.g., `0xFFCCFFAA`). The hexadecimal value must be specified with eight
        characters; the first two characters define the alpha component, and the
        remainder define the red, green, and blue components.

        When using web color notation to specify a color, create a string beginning with
        the "`#`" character followed by three, four, six, or eight characters. The
        example colors `"#D93"` and `"#DD9933"` specify red, green, and blue values (in
        that order) for the color and assume the color has no transparency. The example
        colors `"#D93F"` and `"#DD9933FF"` specify red, green, blue, and alpha values
        (in that order) for the color. Notice that in web color notation the alpha
        channel is last, which is consistent with CSS colors, and in hexadecimal
        notation the alpha channel is first, which is consistent with Processing color
        values.

        The value for the "gray" parameter must be less than or equal to the current
        maximum value as specified by `color_mode()`. The default maximum value is 255.

        To change the color of a `Py5Shape` object's image or a texture, use
        `Py5Shape.tint()`.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def fill(self, rgb: int, alpha: float, /) -> None:
        """Sets the color used to fill the `Py5Shape` object.

        Underlying Processing method: PShape.fill

        Methods
        -------

        You can use any of the following signatures:

         * fill(gray: float, /) -> None
         * fill(gray: float, alpha: float, /) -> None
         * fill(rgb: int, /) -> None
         * fill(rgb: int, alpha: float, /) -> None
         * fill(x: float, y: float, z: float, /) -> None
         * fill(x: float, y: float, z: float, a: float, /) -> None

        Parameters
        ----------

        a: float
            opacity of the fill

        alpha: float
            opacity of the fill

        gray: float
            number specifying value between white and black

        rgb: int
            color variable or hex value

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the color used to fill the `Py5Shape` object. For example, if you run
        `fill(204, 102, 0)`, the shape will be filled with orange. This color is either
        specified in terms of the `RGB` or `HSB` color depending on the current
        `color_mode()`. The default color space is `RGB`, with each value in the range
        from 0 to 255.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair.

        When using hexadecimal notation to specify a color, use "`0x`" before the values
        (e.g., `0xFFCCFFAA`). The hexadecimal value must be specified with eight
        characters; the first two characters define the alpha component, and the
        remainder define the red, green, and blue components.

        When using web color notation to specify a color, create a string beginning with
        the "`#`" character followed by three, four, six, or eight characters. The
        example colors `"#D93"` and `"#DD9933"` specify red, green, and blue values (in
        that order) for the color and assume the color has no transparency. The example
        colors `"#D93F"` and `"#DD9933FF"` specify red, green, blue, and alpha values
        (in that order) for the color. Notice that in web color notation the alpha
        channel is last, which is consistent with CSS colors, and in hexadecimal
        notation the alpha channel is first, which is consistent with Processing color
        values.

        The value for the "gray" parameter must be less than or equal to the current
        maximum value as specified by `color_mode()`. The default maximum value is 255.

        To change the color of a `Py5Shape` object's image or a texture, use
        `Py5Shape.tint()`.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @_convert_hex_color()
    def fill(self, *args):
        """Sets the color used to fill the `Py5Shape` object.

        Underlying Processing method: PShape.fill

        Methods
        -------

        You can use any of the following signatures:

         * fill(gray: float, /) -> None
         * fill(gray: float, alpha: float, /) -> None
         * fill(rgb: int, /) -> None
         * fill(rgb: int, alpha: float, /) -> None
         * fill(x: float, y: float, z: float, /) -> None
         * fill(x: float, y: float, z: float, a: float, /) -> None

        Parameters
        ----------

        a: float
            opacity of the fill

        alpha: float
            opacity of the fill

        gray: float
            number specifying value between white and black

        rgb: int
            color variable or hex value

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the color used to fill the `Py5Shape` object. For example, if you run
        `fill(204, 102, 0)`, the shape will be filled with orange. This color is either
        specified in terms of the `RGB` or `HSB` color depending on the current
        `color_mode()`. The default color space is `RGB`, with each value in the range
        from 0 to 255.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair.

        When using hexadecimal notation to specify a color, use "`0x`" before the values
        (e.g., `0xFFCCFFAA`). The hexadecimal value must be specified with eight
        characters; the first two characters define the alpha component, and the
        remainder define the red, green, and blue components.

        When using web color notation to specify a color, create a string beginning with
        the "`#`" character followed by three, four, six, or eight characters. The
        example colors `"#D93"` and `"#DD9933"` specify red, green, and blue values (in
        that order) for the color and assume the color has no transparency. The example
        colors `"#D93F"` and `"#DD9933FF"` specify red, green, blue, and alpha values
        (in that order) for the color. Notice that in web color notation the alpha
        channel is last, which is consistent with CSS colors, and in hexadecimal
        notation the alpha channel is first, which is consistent with Processing color
        values.

        The value for the "gray" parameter must be less than or equal to the current
        maximum value as specified by `color_mode()`. The default maximum value is 255.

        To change the color of a `Py5Shape` object's image or a texture, use
        `Py5Shape.tint()`.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        return self._instance.fill(*args)

    @_return_py5shape
    def find_child(self, target: str, /) -> Py5Shape:
        """Find a target `Py5Shape` object from anywhere within a `Py5Shape` object that is
        defined as a `GROUP`.

        Underlying Processing method: PShape.findChild

        Parameters
        ----------

        target: str
            name of child object

        Notes
        -----

        Find a target `Py5Shape` object from anywhere within a `Py5Shape` object that is
        defined as a `GROUP`. This is similar to `Py5Shape.get_child()` in that it
        locates a child `Py5Shape` object, except that it can start the search from
        another child shape instead of the parent.
        """
        return self._instance.findChild(target)

    @_return_color
    def get_ambient(self, index: int, /) -> int:
        """Get the ambient reflectance setting for one of a `Py5Shape` object's vertices.

        Underlying Processing method: PShape.getAmbient

        Parameters
        ----------

        index: int
            vertex index

        Notes
        -----

        Get the ambient reflectance setting for one of a `Py5Shape` object's vertices.
        This setting is combined with the ambient light component of the environment.
        Use `Py5Shape.set_ambient()` to change the setting.

        This method can only be used for a complete `Py5Shape` object, and never within
        a `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` pair.
        """
        return self._instance.getAmbient(index)

    @overload
    def get_child(self, index: int, /) -> Py5Shape:
        """Extracts a child `Py5Shape` object from a parent `Py5Shape` object that is
        defined as a `GROUP`.

        Underlying Processing method: PShape.getChild

        Methods
        -------

        You can use any of the following signatures:

         * get_child(index: int, /) -> Py5Shape
         * get_child(target: str, /) -> Py5Shape

        Parameters
        ----------

        index: int
            the layer position of the shape to get

        target: str
            the name of the shape to get

        Notes
        -----

        Extracts a child `Py5Shape` object from a parent `Py5Shape` object that is
        defined as a `GROUP`. Specify the name of the shape with the `target` parameter,
        or use the index with the `index` parameter. The shape is returned as a
        `Py5Shape` object, or `None` is returned if there is an error.
        """
        pass

    @overload
    def get_child(self, target: str, /) -> Py5Shape:
        """Extracts a child `Py5Shape` object from a parent `Py5Shape` object that is
        defined as a `GROUP`.

        Underlying Processing method: PShape.getChild

        Methods
        -------

        You can use any of the following signatures:

         * get_child(index: int, /) -> Py5Shape
         * get_child(target: str, /) -> Py5Shape

        Parameters
        ----------

        index: int
            the layer position of the shape to get

        target: str
            the name of the shape to get

        Notes
        -----

        Extracts a child `Py5Shape` object from a parent `Py5Shape` object that is
        defined as a `GROUP`. Specify the name of the shape with the `target` parameter,
        or use the index with the `index` parameter. The shape is returned as a
        `Py5Shape` object, or `None` is returned if there is an error.
        """
        pass

    @_return_py5shape
    def get_child(self, *args):
        """Extracts a child `Py5Shape` object from a parent `Py5Shape` object that is
        defined as a `GROUP`.

        Underlying Processing method: PShape.getChild

        Methods
        -------

        You can use any of the following signatures:

         * get_child(index: int, /) -> Py5Shape
         * get_child(target: str, /) -> Py5Shape

        Parameters
        ----------

        index: int
            the layer position of the shape to get

        target: str
            the name of the shape to get

        Notes
        -----

        Extracts a child `Py5Shape` object from a parent `Py5Shape` object that is
        defined as a `GROUP`. Specify the name of the shape with the `target` parameter,
        or use the index with the `index` parameter. The shape is returned as a
        `Py5Shape` object, or `None` is returned if there is an error.
        """
        return self._instance.getChild(*args)

    def get_child_count(self) -> int:
        """Returns the number of children within the `Py5Shape` object.

        Underlying Processing method: PShape.getChildCount

        Notes
        -----

        Returns the number of children within the `Py5Shape` object.
        """
        return self._instance.getChildCount()

    def get_child_index(self, who: Py5Shape, /) -> int:
        """Get a child `Py5Shape` object's index from a parent `Py5Shape` object that is
        defined as a `GROUP`.

        Underlying Processing method: PShape.getChildIndex

        Parameters
        ----------

        who: Py5Shape
            Py5Shape object

        Notes
        -----

        Get a child `Py5Shape` object's index from a parent `Py5Shape` object that is
        defined as a `GROUP`. Inside Processing, a group `Py5Shape` object is an ordered
        list of child shapes. This method will retrieve the index for a particular child
        in that ordered list. That index value is useful when using other methods such
        as `Py5Shape.get_child()` or `Py5Shape.remove_child()`.
        """
        return self._instance.getChildIndex(who)

    @_return_list_py5shapes
    def get_children(self) -> list[Py5Shape]:
        """Get the children of a `Py5Shape` object as a list of `Py5Shape` objects.

        Underlying Processing method: PShape.getChildren

        Notes
        -----

        Get the children of a `Py5Shape` object as a list of `Py5Shape` objects. When
        Processing loads shape objects, it may create a hierarchy of `Py5Shape` objects,
        depending on the organization of the source data file. This method will retrieve
        the list of Py5Shapes that are the child objects to a given object.
        """
        return self._instance.getChildren()

    def get_depth(self) -> float:
        """Get the `Py5Shape` object's depth.

        Underlying Processing method: PShape.getDepth

        Notes
        -----

        Get the `Py5Shape` object's depth. This method only makes sense when using the
        `P3D` renderer. It will return 0 when using default renderer.
        """
        return self._instance.getDepth()

    @_return_color
    def get_emissive(self, index: int, /) -> int:
        """Get the emissive color setting for one of a `Py5Shape` object's vertices.

        Underlying Processing method: PShape.getEmissive

        Parameters
        ----------

        index: int
            vertex index

        Notes
        -----

        Get the emissive color setting for one of a `Py5Shape` object's vertices. Use
        `Py5Shape.set_emissive()` to change the setting.

        This method can only be used for a complete `Py5Shape` object, and never within
        a `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` pair.
        """
        return self._instance.getEmissive(index)

    def get_family(self) -> int:
        """Get the Py5Shape object's "family" number.

        Underlying Processing method: PShape.getFamily

        Notes
        -----

        Get the Py5Shape object's "family" number.
        """
        return self._instance.getFamily()

    @_return_color
    def get_fill(self, index: int, /) -> int:
        """Gets the fill color used for a `Py5Shape` object.

        Underlying Processing method: PShape.getFill

        Parameters
        ----------

        index: int
            vertex index

        Notes
        -----

        Gets the fill color used for a `Py5Shape` object. This method can get the fill
        assigned to each vertex, but most likely the value will be the same for all
        vertices.

        This method can only be used for a complete `Py5Shape` object, and never within
        a `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` pair.
        """
        return self._instance.getFill(index)

    def get_height(self) -> float:
        """Get the `Py5Shape` object's height.

        Underlying Processing method: PShape.getHeight

        Notes
        -----

        Get the `Py5Shape` object's height. When using the `P2D` or `P3D` renderers, the
        returned value should be the height of the drawn shape. When using the default
        renderer, this will be the height of the drawing area, which will not
        necessarily be the same as the height of the drawn shape. Consider that the
        shape's vertices might have negative values or the shape may be offset from the
        shape's origin. To get the shape's actual height, calculate the range of the
        vertices obtained with `Py5Shape.get_vertex_y()`.
        """
        return self._instance.getHeight()

    def get_kind(self) -> int:
        """Get the Py5Shape object's "kind" number.

        Underlying Processing method: PShape.getKind

        Notes
        -----

        Get the Py5Shape object's "kind" number.
        """
        return self._instance.getKind()

    @_ret_str
    def get_name(self) -> str:
        """Get the name assigned to a Py5Shape object.

        Underlying Processing method: PShape.getName

        Notes
        -----

        Get the name assigned to a Py5Shape object. Will return `None` if the object has
        no name.
        """
        return self._instance.getName()

    @overload
    def get_normal(self, index: int, /) -> Py5Vector:
        """Get the normal vector for one of a `Py5Shape` object's vertices.

        Underlying Processing method: PShape.getNormal

        Methods
        -------

        You can use any of the following signatures:

         * get_normal(index: int, /) -> Py5Vector
         * get_normal(index: int, vec: Py5Vector, /) -> Py5Vector

        Parameters
        ----------

        index: int
            vertex index

        vec: Py5Vector
            target object to place vertex normal vector into

        Notes
        -----

        Get the normal vector for one of a `Py5Shape` object's vertices. A normal vector
        is used for drawing three dimensional shapes and surfaces, and specifies a
        vector perpendicular to a shape's surface which, in turn, determines how
        lighting affects it. Py5 attempts to automatically assign normals to shapes, and
        this method can be used to inspect that vector.

        This method can only be used for a complete `Py5Shape` object, and never within
        a `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` pair.
        """
        pass

    @overload
    def get_normal(self, index: int, vec: Py5Vector, /) -> Py5Vector:
        """Get the normal vector for one of a `Py5Shape` object's vertices.

        Underlying Processing method: PShape.getNormal

        Methods
        -------

        You can use any of the following signatures:

         * get_normal(index: int, /) -> Py5Vector
         * get_normal(index: int, vec: Py5Vector, /) -> Py5Vector

        Parameters
        ----------

        index: int
            vertex index

        vec: Py5Vector
            target object to place vertex normal vector into

        Notes
        -----

        Get the normal vector for one of a `Py5Shape` object's vertices. A normal vector
        is used for drawing three dimensional shapes and surfaces, and specifies a
        vector perpendicular to a shape's surface which, in turn, determines how
        lighting affects it. Py5 attempts to automatically assign normals to shapes, and
        this method can be used to inspect that vector.

        This method can only be used for a complete `Py5Shape` object, and never within
        a `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` pair.
        """
        pass

    @_get_pvector_wrapper
    def get_normal(self, *args):
        """Get the normal vector for one of a `Py5Shape` object's vertices.

        Underlying Processing method: PShape.getNormal

        Methods
        -------

        You can use any of the following signatures:

         * get_normal(index: int, /) -> Py5Vector
         * get_normal(index: int, vec: Py5Vector, /) -> Py5Vector

        Parameters
        ----------

        index: int
            vertex index

        vec: Py5Vector
            target object to place vertex normal vector into

        Notes
        -----

        Get the normal vector for one of a `Py5Shape` object's vertices. A normal vector
        is used for drawing three dimensional shapes and surfaces, and specifies a
        vector perpendicular to a shape's surface which, in turn, determines how
        lighting affects it. Py5 attempts to automatically assign normals to shapes, and
        this method can be used to inspect that vector.

        This method can only be used for a complete `Py5Shape` object, and never within
        a `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` pair.
        """
        return self._instance.getNormal(*args)

    def get_normal_x(self, index: int, /) -> float:
        """Get the normal vector's x value for one of a `Py5Shape` object's vertices.

        Underlying Processing method: PShape.getNormalX

        Parameters
        ----------

        index: int
            vertex index

        Notes
        -----

        Get the normal vector's x value for one of a `Py5Shape` object's vertices. A
        normal vector is used for drawing three dimensional shapes and surfaces, and
        specifies a vector perpendicular to a shape's surface which, in turn, determines
        how lighting affects it. Py5 attempts to automatically assign normals to shapes,
        and this method can be used to inspect that vector.

        This method can only be used for a complete `Py5Shape` object, and never within
        a `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` pair.
        """
        return self._instance.getNormalX(index)

    def get_normal_y(self, index: int, /) -> float:
        """Get the normal vector's y value for one of a `Py5Shape` object's vertices.

        Underlying Processing method: PShape.getNormalY

        Parameters
        ----------

        index: int
            vertex index

        Notes
        -----

        Get the normal vector's y value for one of a `Py5Shape` object's vertices. A
        normal vector is used for drawing three dimensional shapes and surfaces, and
        specifies a vector perpendicular to a shape's surface which, in turn, determines
        how lighting affects it. Py5 attempts to automatically assign normals to shapes,
        and this method can be used to inspect that vector.

        This method can only be used for a complete `Py5Shape` object, and never within
        a `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` pair.
        """
        return self._instance.getNormalY(index)

    def get_normal_z(self, index: int, /) -> float:
        """Get the normal vector's z value for one of a `Py5Shape` object's vertices.

        Underlying Processing method: PShape.getNormalZ

        Parameters
        ----------

        index: int
            vertex index

        Notes
        -----

        Get the normal vector's z value for one of a `Py5Shape` object's vertices. A
        normal vector is used for drawing three dimensional shapes and surfaces, and
        specifies a vector perpendicular to a shape's surface which, in turn, determines
        how lighting affects it. Py5 attempts to automatically assign normals to shapes,
        and this method can be used to inspect that vector.

        This method can only be used for a complete `Py5Shape` object, and never within
        a `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` pair.
        """
        return self._instance.getNormalZ(index)

    @_return_py5shape
    def get_parent(self) -> Py5Shape:
        """Locate a child `Py5Shape` object's parent `GROUP` `Py5Shape` object.

        Underlying Processing method: PShape.getParent

        Notes
        -----

        Locate a child `Py5Shape` object's parent `GROUP` `Py5Shape` object. This will
        return `None` if the shape has no parent, such as when the shape is the parent
        object or the shape is not a part of a group.
        """
        return self._instance.getParent()

    def get_shininess(self, index: int, /) -> float:
        """Get the shininess setting for one of a `Py5Shape` object's vertices.

        Underlying Processing method: PShape.getShininess

        Parameters
        ----------

        index: int
            vertex index

        Notes
        -----

        Get the shininess setting for one of a `Py5Shape` object's vertices. Use
        `Py5Shape.set_shininess()` to change the setting.

        This method can only be used for a complete `Py5Shape` object, and never within
        a `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` pair.
        """
        return self._instance.getShininess(index)

    @_return_color
    def get_specular(self, index: int, /) -> int:
        """Get the specular color setting for one of a `Py5Shape` object's vertices.

        Underlying Processing method: PShape.getSpecular

        Parameters
        ----------

        index: int
            vertex index

        Notes
        -----

        Get the specular color setting for one of a `Py5Shape` object's vertices. Use
        `Py5Shape.set_specular()` to change the setting.

        This method can only be used for a complete `Py5Shape` object, and never within
        a `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` pair.
        """
        return self._instance.getSpecular(index)

    @_return_color
    def get_stroke(self, index: int, /) -> int:
        """Gets the stroke color used for lines and points in a `Py5Shape` object.

        Underlying Processing method: PShape.getStroke

        Parameters
        ----------

        index: int
            vertex index

        Notes
        -----

        Gets the stroke color used for lines and points in a `Py5Shape` object. This
        method can get the stroke assigned to each vertex, but most likely the value
        will be the same for all vertices.

        This method can only be used for a complete `Py5Shape` object, and never within
        a `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` pair.
        """
        return self._instance.getStroke(index)

    def get_stroke_weight(self, index: int, /) -> float:
        """Gets the width of the stroke used for lines and points in a `Py5Shape` object.

        Underlying Processing method: PShape.getStrokeWeight

        Parameters
        ----------

        index: int
            vertex index

        Notes
        -----

        Gets the width of the stroke used for lines and points in a `Py5Shape` object.
        All widths are set in units of pixels. This method can get the stroke weight
        assigned to each vertex, but most likely the value will be the same for all
        vertices.

        This method can only be used for a complete `Py5Shape` object, and never within
        a `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` pair.
        """
        return self._instance.getStrokeWeight(index)

    def get_texture_u(self, index: int, /) -> float:
        """Get the horizontal texture mapping coordinate for a particular vertex.

        Underlying Processing method: PShape.getTextureU

        Parameters
        ----------

        index: int
            vertex index

        Notes
        -----

        Get the horizontal texture mapping coordinate for a particular vertex. Returned
        values will always range from 0 to 1, regardless of what the Sketch's
        `texture_mode()` setting is.
        """
        return self._instance.getTextureU(index)

    def get_texture_v(self, index: int, /) -> float:
        """Get the vertical texture mapping coordinate for a particular vertex.

        Underlying Processing method: PShape.getTextureV

        Parameters
        ----------

        index: int
            vertex index

        Notes
        -----

        Get the vertical texture mapping coordinate for a particular vertex. Returned
        values will always range from 0 to 1, regardless of what the Sketch's
        `texture_mode()` setting is.
        """
        return self._instance.getTextureV(index)

    @_return_color
    def get_tint(self, index: int, /) -> int:
        """Get the texture tint color assigned to one vertex in a `Py5Shape` object.

        Underlying Processing method: PShape.getTint

        Parameters
        ----------

        index: int
            vertex index

        Notes
        -----

        Get the texture tint color assigned to one vertex in a `Py5Shape` object. If the
        vertex has no assigned tint, the returned color value will be white.
        """
        return self._instance.getTint(index)

    @overload
    def get_vertex(self, index: int, /) -> Py5Vector:
        """The `get_vertex()` method returns a Py5Vector with the coordinates of the vertex
        point located at the position defined by the `index` parameter.

        Underlying Processing method: PShape.getVertex

        Methods
        -------

        You can use any of the following signatures:

         * get_vertex(index: int, /) -> Py5Vector
         * get_vertex(index: int, vec: Py5Vector, /) -> Py5Vector

        Parameters
        ----------

        index: int
            vertex index

        vec: Py5Vector
            target object to place vertex coordinates into

        Notes
        -----

        The `get_vertex()` method returns a Py5Vector with the coordinates of the vertex
        point located at the position defined by the `index` parameter. This method
        works when shapes are created as shown in the example, but won't work properly
        when a shape is defined explicitly (e.g. `create_shape(RECT, 20, 20, 80, 80)`.
        """
        pass

    @overload
    def get_vertex(self, index: int, vec: Py5Vector, /) -> Py5Vector:
        """The `get_vertex()` method returns a Py5Vector with the coordinates of the vertex
        point located at the position defined by the `index` parameter.

        Underlying Processing method: PShape.getVertex

        Methods
        -------

        You can use any of the following signatures:

         * get_vertex(index: int, /) -> Py5Vector
         * get_vertex(index: int, vec: Py5Vector, /) -> Py5Vector

        Parameters
        ----------

        index: int
            vertex index

        vec: Py5Vector
            target object to place vertex coordinates into

        Notes
        -----

        The `get_vertex()` method returns a Py5Vector with the coordinates of the vertex
        point located at the position defined by the `index` parameter. This method
        works when shapes are created as shown in the example, but won't work properly
        when a shape is defined explicitly (e.g. `create_shape(RECT, 20, 20, 80, 80)`.
        """
        pass

    @_get_pvector_wrapper
    def get_vertex(self, *args):
        """The `get_vertex()` method returns a Py5Vector with the coordinates of the vertex
        point located at the position defined by the `index` parameter.

        Underlying Processing method: PShape.getVertex

        Methods
        -------

        You can use any of the following signatures:

         * get_vertex(index: int, /) -> Py5Vector
         * get_vertex(index: int, vec: Py5Vector, /) -> Py5Vector

        Parameters
        ----------

        index: int
            vertex index

        vec: Py5Vector
            target object to place vertex coordinates into

        Notes
        -----

        The `get_vertex()` method returns a Py5Vector with the coordinates of the vertex
        point located at the position defined by the `index` parameter. This method
        works when shapes are created as shown in the example, but won't work properly
        when a shape is defined explicitly (e.g. `create_shape(RECT, 20, 20, 80, 80)`.
        """
        return self._instance.getVertex(*args)

    def get_vertex_code(self, index: int, /) -> int:
        """Get the vertex code for a particular vertex code index.

        Underlying Processing method: PShape.getVertexCode

        Parameters
        ----------

        index: int
            vertex code index

        Notes
        -----

        Get the vertex code for a particular vertex code index. The vertex codes can be
        used to inspect a shape's geometry to determine what kind of vertices it has.
        Each can be one of `BREAK`, `VERTEX`, `BEZIER_VERTEX`, `QUADRATIC_VERTEX` or
        `CURVE_VERTEX`.

        The vertex codes will not necessarily align with the vertices because number of
        vertex codes may be larger than the number of vertices. This will be the case
        for shapes that use contours, and therefore contain `BREAK` codes.
        """
        return self._instance.getVertexCode(index)

    def get_vertex_code_count(self) -> int:
        """Get the number of vertex codes within a `Py5Shape` object.

        Underlying Processing method: PShape.getVertexCodeCount

        Notes
        -----

        Get the number of vertex codes within a `Py5Shape` object. The vertex codes can
        be used to inspect a shape's geometry to determine what kind of vertices it has.
        Each can be one of `BREAK`, `VERTEX`, `BEZIER_VERTEX`, `QUADRATIC_VERTEX` or
        `CURVE_VERTEX`.

        The vertex codes will not necessarily align with the vertices because number of
        vertex codes may be larger than the number of vertices. This will be the case
        for shapes that use contours, and therefore contain `BREAK` codes.
        """
        return self._instance.getVertexCodeCount()

    @_return_numpy_array
    def get_vertex_codes(self) -> npt.NDArray[np.integer]:
        """Get the vertex codes for a `Py5Shape` object.

        Underlying Processing method: PShape.getVertexCodes

        Notes
        -----

        Get the vertex codes for a `Py5Shape` object. The vertex codes can be used to
        inspect a shape's geometry to determine what kind of vertices it has. Each can
        be one of `BREAK`, `VERTEX`, `BEZIER_VERTEX`, `QUADRATIC_VERTEX` or
        `CURVE_VERTEX`.

        The vertex codes will not necessarily align with the vertices because number of
        vertex codes may be larger than the number of vertices. This will be the case
        for shapes that use contours, and therefore contain `BREAK` codes.
        """
        return self._instance.getVertexCodes()

    @overload
    def get_vertex_count(self) -> int:
        """The `get_vertex_count()` method returns the number of vertices that make up a
        `Py5Shape`.

        Underlying Processing method: PShape.getVertexCount

        Methods
        -------

        You can use any of the following signatures:

         * get_vertex_count() -> int
         * get_vertex_count(include_children: bool, /) -> int

        Parameters
        ----------

        include_children: bool
            include vertices in the shape's children

        Notes
        -----

        The `get_vertex_count()` method returns the number of vertices that make up a
        `Py5Shape`. In the example, the value 4 is returned by the `get_vertex_count()`
        method because 4 vertices are defined in `setup()`.

        Use the `include_children` parameter to include the shape's children if the
        shape happens to be a `GROUP` shape. By default, a shape's children will not be
        included in the count.
        """
        pass

    @overload
    def get_vertex_count(self, include_children: bool, /) -> int:
        """The `get_vertex_count()` method returns the number of vertices that make up a
        `Py5Shape`.

        Underlying Processing method: PShape.getVertexCount

        Methods
        -------

        You can use any of the following signatures:

         * get_vertex_count() -> int
         * get_vertex_count(include_children: bool, /) -> int

        Parameters
        ----------

        include_children: bool
            include vertices in the shape's children

        Notes
        -----

        The `get_vertex_count()` method returns the number of vertices that make up a
        `Py5Shape`. In the example, the value 4 is returned by the `get_vertex_count()`
        method because 4 vertices are defined in `setup()`.

        Use the `include_children` parameter to include the shape's children if the
        shape happens to be a `GROUP` shape. By default, a shape's children will not be
        included in the count.
        """
        pass

    def get_vertex_count(self, *args):
        """The `get_vertex_count()` method returns the number of vertices that make up a
        `Py5Shape`.

        Underlying Processing method: PShape.getVertexCount

        Methods
        -------

        You can use any of the following signatures:

         * get_vertex_count() -> int
         * get_vertex_count(include_children: bool, /) -> int

        Parameters
        ----------

        include_children: bool
            include vertices in the shape's children

        Notes
        -----

        The `get_vertex_count()` method returns the number of vertices that make up a
        `Py5Shape`. In the example, the value 4 is returned by the `get_vertex_count()`
        method because 4 vertices are defined in `setup()`.

        Use the `include_children` parameter to include the shape's children if the
        shape happens to be a `GROUP` shape. By default, a shape's children will not be
        included in the count.
        """
        return self._instance.getVertexCount(*args)

    def get_vertex_x(self, index: int, /) -> float:
        """Get the value of the x coordinate for the vertex `index`.

        Underlying Processing method: PShape.getVertexX

        Parameters
        ----------

        index: int
            vertex index

        Notes
        -----

        Get the value of the x coordinate for the vertex `index`.
        """
        return self._instance.getVertexX(index)

    def get_vertex_y(self, index: int, /) -> float:
        """Get the value of the y coordinate for the vertex `index`.

        Underlying Processing method: PShape.getVertexY

        Parameters
        ----------

        index: int
            vertex index

        Notes
        -----

        Get the value of the y coordinate for the vertex `index`.
        """
        return self._instance.getVertexY(index)

    def get_vertex_z(self, index: int, /) -> float:
        """Get the value of the z coordinate for the vertex `index`.

        Underlying Processing method: PShape.getVertexZ

        Parameters
        ----------

        index: int
            vertex index

        Notes
        -----

        Get the value of the z coordinate for the vertex `index`.
        """
        return self._instance.getVertexZ(index)

    def get_width(self) -> float:
        """Get the `Py5Shape` object's width.

        Underlying Processing method: PShape.getWidth

        Notes
        -----

        Get the `Py5Shape` object's width. When using the `P2D` or `P3D` renderers, the
        returned value should be the width of the drawn shape. When using the default
        renderer, this will be the width of the drawing area, which will not necessarily
        be the same as the width of the drawn shape. Consider that the shape's vertices
        might have negative values or the shape may be offset from the shape's origin.
        To get the shape's actual width, calculate the range of the vertices obtained
        with `Py5Shape.get_vertex_x()`.
        """
        return self._instance.getWidth()

    def is2d(self) -> bool:
        """Boolean value reflecting if the shape is or is not a 2D shape.

        Underlying Processing method: PShape.is2D

        Notes
        -----

        Boolean value reflecting if the shape is or is not a 2D shape.

        If the shape is created in a Sketch using the `P3D` renderer, this will be
        `False`, even if it only uses 2D coordinates.
        """
        return self._instance.is2D()

    def is3d(self) -> bool:
        """Boolean value reflecting if the shape is or is not a 3D shape.

        Underlying Processing method: PShape.is3D

        Notes
        -----

        Boolean value reflecting if the shape is or is not a 3D shape.

        This will be `True` if the shape is created in a Sketch using a 3D renderer such
        as `P3D`, even if it only uses 2D coordinates.
        """
        return self._instance.is3D()

    def is_visible(self) -> bool:
        """Returns a boolean value `True` if the image is set to be visible, `False` if
        not.

        Underlying Processing method: PShape.isVisible

        Notes
        -----

        Returns a boolean value `True` if the image is set to be visible, `False` if
        not. This value can be modified with the `Py5Shape.set_visible()` method.

        The default visibility of a shape is usually controlled by whatever program
        created the SVG file. For instance, this parameter is controlled by showing or
        hiding the shape in the layers palette in Adobe Illustrator.
        """
        return self._instance.isVisible()

    def no_fill(self) -> None:
        """Disables the `Py5Shape` object's filling geometry.

        Underlying Processing method: PShape.noFill

        Notes
        -----

        Disables the `Py5Shape` object's filling geometry. If both
        `Py5Shape.no_stroke()` and `no_fill()` are called, nothing will be drawn to the
        screen.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair.
        """
        return self._instance.noFill()

    def no_stroke(self) -> None:
        """Disables the `Py5Shape` object's stroke (outline).

        Underlying Processing method: PShape.noStroke

        Notes
        -----

        Disables the `Py5Shape` object's stroke (outline). If both `no_stroke()` and
        `Py5Shape.no_fill()` are called, nothing will be drawn to the screen.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair.
        """
        return self._instance.noStroke()

    def no_tint(self) -> None:
        """Stop applying a color tint to a shape's texture map.

        Underlying Processing method: PShape.noTint

        Notes
        -----

        Stop applying a color tint to a shape's texture map. Use `Py5Shape.tint()` to
        start applying a color tint.

        Both `Py5Shape.tint()` and `no_tint()` can be used to control the coloring of
        textures in 3D.
        """
        return self._instance.noTint()

    def normal(self, nx: float, ny: float, nz: float, /) -> None:
        """Sets the current normal vector for a `Py5Shape` object's vertices.

        Underlying Processing method: PShape.normal

        Parameters
        ----------

        nx: float
            x direction

        ny: float
            y direction

        nz: float
            z direction

        Notes
        -----

        Sets the current normal vector for a `Py5Shape` object's vertices. Used for
        drawing three dimensional shapes and surfaces, `normal()` specifies a vector
        perpendicular to a shape's surface which, in turn, determines how lighting
        affects it. Py5 attempts to automatically assign normals to shapes, but since
        that's imperfect, this is a better option when you want more control.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair. The normal setting will be applied to vertices
        added after the call to this method.
        """
        return self._instance.normal(nx, ny, nz)

    @overload
    def quadratic_vertex(self, cx: float, cy: float, x3: float, y3: float, /) -> None:
        """Specifies a `Py5Shape` object's vertex coordinates for quadratic Bezier curves.

        Underlying Processing method: PShape.quadraticVertex

        Methods
        -------

        You can use any of the following signatures:

         * quadratic_vertex(cx: float, cy: float, cz: float, x3: float, y3: float, z3: float, /) -> None
         * quadratic_vertex(cx: float, cy: float, x3: float, y3: float, /) -> None

        Parameters
        ----------

        cx: float
            the x-coordinate of the control point

        cy: float
            the y-coordinate of the control point

        cz: float
            the z-coordinate of the control point

        x3: float
            the x-coordinate of the anchor point

        y3: float
            the y-coordinate of the anchor point

        z3: float
            the z-coordinate of the anchor point

        Notes
        -----

        Specifies a `Py5Shape` object's vertex coordinates for quadratic Bezier curves.
        Each call to `quadratic_vertex()` defines the position of one control point and
        one anchor point of a Bezier curve, adding a new segment to a line or shape. The
        first time `quadratic_vertex()` is used within a `Py5Shape.begin_shape()` call,
        it must be prefaced with a call to `Py5Shape.vertex()` to set the first anchor
        point. This method must be used between `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` and only when there is no `MODE` parameter specified to
        `Py5Shape.begin_shape()`.

        Drawing 2D bezier curves requires using the `P2D` renderer and drawing 3D bezier
        curves requires using the `P3D` renderer. When drawing directly with `Py5Shape`
        objects, bezier curves do not work at all using the default renderer.
        """
        pass

    @overload
    def quadratic_vertex(
        self, cx: float, cy: float, cz: float, x3: float, y3: float, z3: float, /
    ) -> None:
        """Specifies a `Py5Shape` object's vertex coordinates for quadratic Bezier curves.

        Underlying Processing method: PShape.quadraticVertex

        Methods
        -------

        You can use any of the following signatures:

         * quadratic_vertex(cx: float, cy: float, cz: float, x3: float, y3: float, z3: float, /) -> None
         * quadratic_vertex(cx: float, cy: float, x3: float, y3: float, /) -> None

        Parameters
        ----------

        cx: float
            the x-coordinate of the control point

        cy: float
            the y-coordinate of the control point

        cz: float
            the z-coordinate of the control point

        x3: float
            the x-coordinate of the anchor point

        y3: float
            the y-coordinate of the anchor point

        z3: float
            the z-coordinate of the anchor point

        Notes
        -----

        Specifies a `Py5Shape` object's vertex coordinates for quadratic Bezier curves.
        Each call to `quadratic_vertex()` defines the position of one control point and
        one anchor point of a Bezier curve, adding a new segment to a line or shape. The
        first time `quadratic_vertex()` is used within a `Py5Shape.begin_shape()` call,
        it must be prefaced with a call to `Py5Shape.vertex()` to set the first anchor
        point. This method must be used between `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` and only when there is no `MODE` parameter specified to
        `Py5Shape.begin_shape()`.

        Drawing 2D bezier curves requires using the `P2D` renderer and drawing 3D bezier
        curves requires using the `P3D` renderer. When drawing directly with `Py5Shape`
        objects, bezier curves do not work at all using the default renderer.
        """
        pass

    def quadratic_vertex(self, *args):
        """Specifies a `Py5Shape` object's vertex coordinates for quadratic Bezier curves.

        Underlying Processing method: PShape.quadraticVertex

        Methods
        -------

        You can use any of the following signatures:

         * quadratic_vertex(cx: float, cy: float, cz: float, x3: float, y3: float, z3: float, /) -> None
         * quadratic_vertex(cx: float, cy: float, x3: float, y3: float, /) -> None

        Parameters
        ----------

        cx: float
            the x-coordinate of the control point

        cy: float
            the y-coordinate of the control point

        cz: float
            the z-coordinate of the control point

        x3: float
            the x-coordinate of the anchor point

        y3: float
            the y-coordinate of the anchor point

        z3: float
            the z-coordinate of the anchor point

        Notes
        -----

        Specifies a `Py5Shape` object's vertex coordinates for quadratic Bezier curves.
        Each call to `quadratic_vertex()` defines the position of one control point and
        one anchor point of a Bezier curve, adding a new segment to a line or shape. The
        first time `quadratic_vertex()` is used within a `Py5Shape.begin_shape()` call,
        it must be prefaced with a call to `Py5Shape.vertex()` to set the first anchor
        point. This method must be used between `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` and only when there is no `MODE` parameter specified to
        `Py5Shape.begin_shape()`.

        Drawing 2D bezier curves requires using the `P2D` renderer and drawing 3D bezier
        curves requires using the `P3D` renderer. When drawing directly with `Py5Shape`
        objects, bezier curves do not work at all using the default renderer.
        """
        return self._instance.quadraticVertex(*args)

    def remove_child(self, idx: int, /) -> None:
        """Removes a child `Py5Shape` object from a parent `Py5Shape` object that is
        defined as a `GROUP`.

        Underlying Processing method: PShape.removeChild

        Parameters
        ----------

        idx: int
            index value

        Notes
        -----

        Removes a child `Py5Shape` object from a parent `Py5Shape` object that is
        defined as a `GROUP`.
        """
        return self._instance.removeChild(idx)

    def reset_matrix(self) -> None:
        """Replaces the current matrix of a shape with the identity matrix.

        Underlying Processing method: PShape.resetMatrix

        Notes
        -----

        Replaces the current matrix of a shape with the identity matrix. The equivalent
        function in OpenGL is `gl_load_identity()`.
        """
        return self._instance.resetMatrix()

    @overload
    def rotate(self, angle: float, /) -> None:
        """Rotates the shape the amount specified by the `angle` parameter.

        Underlying Processing method: PShape.rotate

        Methods
        -------

        You can use any of the following signatures:

         * rotate(angle: float, /) -> None
         * rotate(angle: float, v0: float, v1: float, v2: float, /) -> None

        Parameters
        ----------

        angle: float
            angle of rotation specified in radians

        v0: float
            x-coordinate of vector to rotate around

        v1: float
            y-coordinate of vector to rotate around

        v2: float
            z-coordinate of vector to rotate around

        Notes
        -----

        Rotates the shape the amount specified by the `angle` parameter. Angles should
        be specified in radians (values from 0 to `TWO_PI`) or converted from degrees to
        radians with the `radians()` method.

        Shapes are always rotated around the upper-left corner of their bounding box.
        Positive numbers rotate objects in a clockwise direction. Transformations apply
        to everything that happens after and subsequent calls to the method accumulates
        the effect. For example, calling `rotate(HALF_PI)` and then `rotate(HALF_PI)` is
        the same as `rotate(PI)`. This transformation is applied directly to the shape,
        it's not refreshed each time `draw()` is run.
        """
        pass

    @overload
    def rotate(self, angle: float, v0: float, v1: float, v2: float, /) -> None:
        """Rotates the shape the amount specified by the `angle` parameter.

        Underlying Processing method: PShape.rotate

        Methods
        -------

        You can use any of the following signatures:

         * rotate(angle: float, /) -> None
         * rotate(angle: float, v0: float, v1: float, v2: float, /) -> None

        Parameters
        ----------

        angle: float
            angle of rotation specified in radians

        v0: float
            x-coordinate of vector to rotate around

        v1: float
            y-coordinate of vector to rotate around

        v2: float
            z-coordinate of vector to rotate around

        Notes
        -----

        Rotates the shape the amount specified by the `angle` parameter. Angles should
        be specified in radians (values from 0 to `TWO_PI`) or converted from degrees to
        radians with the `radians()` method.

        Shapes are always rotated around the upper-left corner of their bounding box.
        Positive numbers rotate objects in a clockwise direction. Transformations apply
        to everything that happens after and subsequent calls to the method accumulates
        the effect. For example, calling `rotate(HALF_PI)` and then `rotate(HALF_PI)` is
        the same as `rotate(PI)`. This transformation is applied directly to the shape,
        it's not refreshed each time `draw()` is run.
        """
        pass

    def rotate(self, *args):
        """Rotates the shape the amount specified by the `angle` parameter.

        Underlying Processing method: PShape.rotate

        Methods
        -------

        You can use any of the following signatures:

         * rotate(angle: float, /) -> None
         * rotate(angle: float, v0: float, v1: float, v2: float, /) -> None

        Parameters
        ----------

        angle: float
            angle of rotation specified in radians

        v0: float
            x-coordinate of vector to rotate around

        v1: float
            y-coordinate of vector to rotate around

        v2: float
            z-coordinate of vector to rotate around

        Notes
        -----

        Rotates the shape the amount specified by the `angle` parameter. Angles should
        be specified in radians (values from 0 to `TWO_PI`) or converted from degrees to
        radians with the `radians()` method.

        Shapes are always rotated around the upper-left corner of their bounding box.
        Positive numbers rotate objects in a clockwise direction. Transformations apply
        to everything that happens after and subsequent calls to the method accumulates
        the effect. For example, calling `rotate(HALF_PI)` and then `rotate(HALF_PI)` is
        the same as `rotate(PI)`. This transformation is applied directly to the shape,
        it's not refreshed each time `draw()` is run.
        """
        return self._instance.rotate(*args)

    def rotate_x(self, angle: float, /) -> None:
        """Rotates the shape around the x-axis the amount specified by the `angle`
        parameter.

        Underlying Processing method: PShape.rotateX

        Parameters
        ----------

        angle: float
            angle of rotation specified in radians

        Notes
        -----

        Rotates the shape around the x-axis the amount specified by the `angle`
        parameter. Angles should be specified in radians (values from 0 to `TWO_PI`) or
        converted from degrees to radians with the `radians()` method.

        Shapes are always rotated around the upper-left corner of their bounding box.
        Positive numbers rotate objects in a clockwise direction. Subsequent calls to
        the method accumulates the effect. For example, calling `rotate_x(HALF_PI)` and
        then `rotate_x(HALF_PI)` is the same as `rotate_x(PI)`. This transformation is
        applied directly to the shape, it's not refreshed each time `draw()` is run.

        This method requires a 3D renderer. You need to use `P3D` as a third parameter
        for the `size()` function as shown in the example.
        """
        return self._instance.rotateX(angle)

    def rotate_y(self, angle: float, /) -> None:
        """Rotates the shape around the y-axis the amount specified by the `angle`
        parameter.

        Underlying Processing method: PShape.rotateY

        Parameters
        ----------

        angle: float
            angle of rotation specified in radians

        Notes
        -----

        Rotates the shape around the y-axis the amount specified by the `angle`
        parameter. Angles should be specified in radians (values from 0 to `TWO_PI`) or
        converted from degrees to radians with the `radians()` method.

        Shapes are always rotated around the upper-left corner of their bounding box.
        Positive numbers rotate objects in a clockwise direction. Subsequent calls to
        the method accumulates the effect. For example, calling `rotate_y(HALF_PI)` and
        then `rotate_y(HALF_PI)` is the same as `rotate_y(PI)`. This transformation is
        applied directly to the shape, it's not refreshed each time `draw()` is run.

        This method requires a 3D renderer. You need to use `P3D` as a third parameter
        for the `size()` function as shown in the example.
        """
        return self._instance.rotateY(angle)

    def rotate_z(self, angle: float, /) -> None:
        """Rotates the shape around the z-axis the amount specified by the `angle`
        parameter.

        Underlying Processing method: PShape.rotateZ

        Parameters
        ----------

        angle: float
            angle of rotation specified in radians

        Notes
        -----

        Rotates the shape around the z-axis the amount specified by the `angle`
        parameter. Angles should be specified in radians (values from 0 to `TWO_PI`) or
        converted from degrees to radians with the `radians()` method.

        Shapes are always rotated around the upper-left corner of their bounding box.
        Positive numbers rotate objects in a clockwise direction. Subsequent calls to
        the method accumulates the effect. For example, calling `rotate_z(HALF_PI)` and
        then `rotate_z(HALF_PI)` is the same as `rotate_z(PI)`. This transformation is
        applied directly to the shape, it's not refreshed each time `draw()` is run.

        This method requires a 3D renderer. You need to use `P3D` as a third parameter
        for the `size()` function as shown in the example.
        """
        return self._instance.rotateZ(angle)

    @overload
    def scale(self, s: float, /) -> None:
        """Increases or decreases the size of a shape by expanding and contracting
        vertices.

        Underlying Processing method: PShape.scale

        Methods
        -------

        You can use any of the following signatures:

         * scale(s: float, /) -> None
         * scale(x: float, y: float, /) -> None
         * scale(x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        s: float
            percentate to scale the object

        x: float
            percentage to scale the object in the x-axis

        y: float
            percentage to scale the object in the y-axis

        z: float
            percentage to scale the object in the z-axis

        Notes
        -----

        Increases or decreases the size of a shape by expanding and contracting
        vertices. Shapes always scale from the relative origin of their bounding box.
        Scale values are specified as decimal percentages. For example, the method call
        `scale(2.0)` increases the dimension of a shape by 200%. Subsequent calls to the
        method multiply the effect. For example, calling `scale(2.0)` and then
        `scale(1.5)` is the same as `scale(3.0)`. This transformation is applied
        directly to the shape; it's not refreshed each time `draw()` is run.

        Using this method with the `z` parameter requires using the `P3D` parameter in
        combination with size.
        """
        pass

    @overload
    def scale(self, x: float, y: float, /) -> None:
        """Increases or decreases the size of a shape by expanding and contracting
        vertices.

        Underlying Processing method: PShape.scale

        Methods
        -------

        You can use any of the following signatures:

         * scale(s: float, /) -> None
         * scale(x: float, y: float, /) -> None
         * scale(x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        s: float
            percentate to scale the object

        x: float
            percentage to scale the object in the x-axis

        y: float
            percentage to scale the object in the y-axis

        z: float
            percentage to scale the object in the z-axis

        Notes
        -----

        Increases or decreases the size of a shape by expanding and contracting
        vertices. Shapes always scale from the relative origin of their bounding box.
        Scale values are specified as decimal percentages. For example, the method call
        `scale(2.0)` increases the dimension of a shape by 200%. Subsequent calls to the
        method multiply the effect. For example, calling `scale(2.0)` and then
        `scale(1.5)` is the same as `scale(3.0)`. This transformation is applied
        directly to the shape; it's not refreshed each time `draw()` is run.

        Using this method with the `z` parameter requires using the `P3D` parameter in
        combination with size.
        """
        pass

    @overload
    def scale(self, x: float, y: float, z: float, /) -> None:
        """Increases or decreases the size of a shape by expanding and contracting
        vertices.

        Underlying Processing method: PShape.scale

        Methods
        -------

        You can use any of the following signatures:

         * scale(s: float, /) -> None
         * scale(x: float, y: float, /) -> None
         * scale(x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        s: float
            percentate to scale the object

        x: float
            percentage to scale the object in the x-axis

        y: float
            percentage to scale the object in the y-axis

        z: float
            percentage to scale the object in the z-axis

        Notes
        -----

        Increases or decreases the size of a shape by expanding and contracting
        vertices. Shapes always scale from the relative origin of their bounding box.
        Scale values are specified as decimal percentages. For example, the method call
        `scale(2.0)` increases the dimension of a shape by 200%. Subsequent calls to the
        method multiply the effect. For example, calling `scale(2.0)` and then
        `scale(1.5)` is the same as `scale(3.0)`. This transformation is applied
        directly to the shape; it's not refreshed each time `draw()` is run.

        Using this method with the `z` parameter requires using the `P3D` parameter in
        combination with size.
        """
        pass

    def scale(self, *args):
        """Increases or decreases the size of a shape by expanding and contracting
        vertices.

        Underlying Processing method: PShape.scale

        Methods
        -------

        You can use any of the following signatures:

         * scale(s: float, /) -> None
         * scale(x: float, y: float, /) -> None
         * scale(x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        s: float
            percentate to scale the object

        x: float
            percentage to scale the object in the x-axis

        y: float
            percentage to scale the object in the y-axis

        z: float
            percentage to scale the object in the z-axis

        Notes
        -----

        Increases or decreases the size of a shape by expanding and contracting
        vertices. Shapes always scale from the relative origin of their bounding box.
        Scale values are specified as decimal percentages. For example, the method call
        `scale(2.0)` increases the dimension of a shape by 200%. Subsequent calls to the
        method multiply the effect. For example, calling `scale(2.0)` and then
        `scale(1.5)` is the same as `scale(3.0)`. This transformation is applied
        directly to the shape; it's not refreshed each time `draw()` is run.

        Using this method with the `z` parameter requires using the `P3D` parameter in
        combination with size.
        """
        return self._instance.scale(*args)

    @overload
    def set_ambient(self, ambient: int, /) -> None:
        """Sets a `Py5Shape` object's ambient reflectance.

        Underlying Processing method: PShape.setAmbient

        Methods
        -------

        You can use any of the following signatures:

         * set_ambient(ambient: int, /) -> None
         * set_ambient(index: int, ambient: int, /) -> None

        Parameters
        ----------

        ambient: int
            any color value

        index: int
            vertex index

        Notes
        -----

        Sets a `Py5Shape` object's ambient reflectance. This is combined with the
        ambient light component of the environment. The color components set through the
        parameters define the reflectance. For example in the default color mode,
        calling `set_ambient(255, 127, 0)`, would cause all the red light to reflect and
        half of the green light to reflect. Use in combination with
        `Py5Shape.set_emissive()`, `Py5Shape.set_specular()`, and
        `Py5Shape.set_shininess()` to set the material properties of a `Py5Shape`
        object.

        The `ambient` parameter can be applied to the entire `Py5Shape` object or to a
        single vertex.

        This method can only be used for a complete `Py5Shape` object, and never within
        a `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` pair.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def set_ambient(self, index: int, ambient: int, /) -> None:
        """Sets a `Py5Shape` object's ambient reflectance.

        Underlying Processing method: PShape.setAmbient

        Methods
        -------

        You can use any of the following signatures:

         * set_ambient(ambient: int, /) -> None
         * set_ambient(index: int, ambient: int, /) -> None

        Parameters
        ----------

        ambient: int
            any color value

        index: int
            vertex index

        Notes
        -----

        Sets a `Py5Shape` object's ambient reflectance. This is combined with the
        ambient light component of the environment. The color components set through the
        parameters define the reflectance. For example in the default color mode,
        calling `set_ambient(255, 127, 0)`, would cause all the red light to reflect and
        half of the green light to reflect. Use in combination with
        `Py5Shape.set_emissive()`, `Py5Shape.set_specular()`, and
        `Py5Shape.set_shininess()` to set the material properties of a `Py5Shape`
        object.

        The `ambient` parameter can be applied to the entire `Py5Shape` object or to a
        single vertex.

        This method can only be used for a complete `Py5Shape` object, and never within
        a `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` pair.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @_convert_hex_color2
    def set_ambient(self, *args):
        """Sets a `Py5Shape` object's ambient reflectance.

        Underlying Processing method: PShape.setAmbient

        Methods
        -------

        You can use any of the following signatures:

         * set_ambient(ambient: int, /) -> None
         * set_ambient(index: int, ambient: int, /) -> None

        Parameters
        ----------

        ambient: int
            any color value

        index: int
            vertex index

        Notes
        -----

        Sets a `Py5Shape` object's ambient reflectance. This is combined with the
        ambient light component of the environment. The color components set through the
        parameters define the reflectance. For example in the default color mode,
        calling `set_ambient(255, 127, 0)`, would cause all the red light to reflect and
        half of the green light to reflect. Use in combination with
        `Py5Shape.set_emissive()`, `Py5Shape.set_specular()`, and
        `Py5Shape.set_shininess()` to set the material properties of a `Py5Shape`
        object.

        The `ambient` parameter can be applied to the entire `Py5Shape` object or to a
        single vertex.

        This method can only be used for a complete `Py5Shape` object, and never within
        a `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` pair.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        return self._instance.setAmbient(*args)

    @overload
    def set_emissive(self, emissive: int, /) -> None:
        """Sets a `Py5Shape` object's emissive color.

        Underlying Processing method: PShape.setEmissive

        Methods
        -------

        You can use any of the following signatures:

         * set_emissive(emissive: int, /) -> None
         * set_emissive(index: int, emissive: int, /) -> None

        Parameters
        ----------

        emissive: int
            any color value

        index: int
            vertex index

        Notes
        -----

        Sets a `Py5Shape` object's emissive color. This is part of the material
        properties of a `Py5Shape` object.

        The `emissive` parameter can be applied to the entire `Py5Shape` object or to a
        single vertex.

        This method can only be used for a complete `Py5Shape` object, and never within
        a `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` pair.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def set_emissive(self, index: int, emissive: int, /) -> None:
        """Sets a `Py5Shape` object's emissive color.

        Underlying Processing method: PShape.setEmissive

        Methods
        -------

        You can use any of the following signatures:

         * set_emissive(emissive: int, /) -> None
         * set_emissive(index: int, emissive: int, /) -> None

        Parameters
        ----------

        emissive: int
            any color value

        index: int
            vertex index

        Notes
        -----

        Sets a `Py5Shape` object's emissive color. This is part of the material
        properties of a `Py5Shape` object.

        The `emissive` parameter can be applied to the entire `Py5Shape` object or to a
        single vertex.

        This method can only be used for a complete `Py5Shape` object, and never within
        a `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` pair.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @_convert_hex_color2
    def set_emissive(self, *args):
        """Sets a `Py5Shape` object's emissive color.

        Underlying Processing method: PShape.setEmissive

        Methods
        -------

        You can use any of the following signatures:

         * set_emissive(emissive: int, /) -> None
         * set_emissive(index: int, emissive: int, /) -> None

        Parameters
        ----------

        emissive: int
            any color value

        index: int
            vertex index

        Notes
        -----

        Sets a `Py5Shape` object's emissive color. This is part of the material
        properties of a `Py5Shape` object.

        The `emissive` parameter can be applied to the entire `Py5Shape` object or to a
        single vertex.

        This method can only be used for a complete `Py5Shape` object, and never within
        a `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` pair.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        return self._instance.setEmissive(*args)

    @overload
    def set_fill(self, fill: bool, /) -> None:
        """The `set_fill()` method defines the fill color of a `Py5Shape`.

        Underlying Processing method: PShape.setFill

        Methods
        -------

        You can use any of the following signatures:

         * set_fill(fill: bool, /) -> None
         * set_fill(fill: int, /) -> None
         * set_fill(index: int, fill: int, /) -> None

        Parameters
        ----------

        fill: bool
            allow fill

        fill: int
            any color value

        index: int
            vertex index

        Notes
        -----

        The `set_fill()` method defines the fill color of a `Py5Shape`. This method is
        used after shapes are created or when a shape is defined explicitly (e.g.
        `create_shape(RECT, 20, 20, 60, 60)`) as shown in the example. When a shape is
        created with `Py5Shape.begin_shape()` and `Py5Shape.end_shape()`, its attributes
        may be changed with `Py5Shape.fill()` and `Py5Shape.stroke()` between the calls
        to `Py5Shape.begin_shape()` and `Py5Shape.end_shape()`. However, after the shape
        is created, only the `set_fill()` method can define a new fill value for the
        `Py5Shape`.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def set_fill(self, fill: int, /) -> None:
        """The `set_fill()` method defines the fill color of a `Py5Shape`.

        Underlying Processing method: PShape.setFill

        Methods
        -------

        You can use any of the following signatures:

         * set_fill(fill: bool, /) -> None
         * set_fill(fill: int, /) -> None
         * set_fill(index: int, fill: int, /) -> None

        Parameters
        ----------

        fill: bool
            allow fill

        fill: int
            any color value

        index: int
            vertex index

        Notes
        -----

        The `set_fill()` method defines the fill color of a `Py5Shape`. This method is
        used after shapes are created or when a shape is defined explicitly (e.g.
        `create_shape(RECT, 20, 20, 60, 60)`) as shown in the example. When a shape is
        created with `Py5Shape.begin_shape()` and `Py5Shape.end_shape()`, its attributes
        may be changed with `Py5Shape.fill()` and `Py5Shape.stroke()` between the calls
        to `Py5Shape.begin_shape()` and `Py5Shape.end_shape()`. However, after the shape
        is created, only the `set_fill()` method can define a new fill value for the
        `Py5Shape`.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def set_fill(self, index: int, fill: int, /) -> None:
        """The `set_fill()` method defines the fill color of a `Py5Shape`.

        Underlying Processing method: PShape.setFill

        Methods
        -------

        You can use any of the following signatures:

         * set_fill(fill: bool, /) -> None
         * set_fill(fill: int, /) -> None
         * set_fill(index: int, fill: int, /) -> None

        Parameters
        ----------

        fill: bool
            allow fill

        fill: int
            any color value

        index: int
            vertex index

        Notes
        -----

        The `set_fill()` method defines the fill color of a `Py5Shape`. This method is
        used after shapes are created or when a shape is defined explicitly (e.g.
        `create_shape(RECT, 20, 20, 60, 60)`) as shown in the example. When a shape is
        created with `Py5Shape.begin_shape()` and `Py5Shape.end_shape()`, its attributes
        may be changed with `Py5Shape.fill()` and `Py5Shape.stroke()` between the calls
        to `Py5Shape.begin_shape()` and `Py5Shape.end_shape()`. However, after the shape
        is created, only the `set_fill()` method can define a new fill value for the
        `Py5Shape`.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @_py5shape_type_fixer
    @_convert_hex_color2
    def set_fill(self, *args):
        """The `set_fill()` method defines the fill color of a `Py5Shape`.

        Underlying Processing method: PShape.setFill

        Methods
        -------

        You can use any of the following signatures:

         * set_fill(fill: bool, /) -> None
         * set_fill(fill: int, /) -> None
         * set_fill(index: int, fill: int, /) -> None

        Parameters
        ----------

        fill: bool
            allow fill

        fill: int
            any color value

        index: int
            vertex index

        Notes
        -----

        The `set_fill()` method defines the fill color of a `Py5Shape`. This method is
        used after shapes are created or when a shape is defined explicitly (e.g.
        `create_shape(RECT, 20, 20, 60, 60)`) as shown in the example. When a shape is
        created with `Py5Shape.begin_shape()` and `Py5Shape.end_shape()`, its attributes
        may be changed with `Py5Shape.fill()` and `Py5Shape.stroke()` between the calls
        to `Py5Shape.begin_shape()` and `Py5Shape.end_shape()`. However, after the shape
        is created, only the `set_fill()` method can define a new fill value for the
        `Py5Shape`.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        return self._instance.setFill(*args)

    def set_name(self, name: str, /) -> None:
        """Assign a name to a `Py5Shape` object.

        Underlying Processing method: PShape.setName

        Parameters
        ----------

        name: str
            name to be assigned to shape

        Notes
        -----

        Assign a name to a `Py5Shape` object. This can be used to later find the shape
        in a `GROUP` shape.
        """
        return self._instance.setName(name)

    def set_path(self, vcount: int, verts: Sequence[Sequence[float]], /) -> None:
        """Set many vertex points at the same time, using a numpy array.

        Underlying Processing method: PShape.setPath

        Parameters
        ----------

        vcount: int
            number of vertices

        verts: Sequence[Sequence[float]]
            2D array of vertex coordinates

        Notes
        -----

        Set many vertex points at the same time, using a numpy array. This will be
        faster and more efficient than repeatedly calling `Py5Shape.set_vertex()` in a
        loop. Setting the vertex codes is not supported, so the vertices will be regular
        vertices and not bezier, quadratic or curve vertices.

        The `vcount` parameter cannot be larger than the first dimension of the `verts`
        array.
        """
        return self._instance.setPath(vcount, verts)

    @overload
    def set_shininess(self, shine: float, /) -> None:
        """Sets the amount of gloss a `Py5Shape` object's surface has.

        Underlying Processing method: PShape.setShininess

        Methods
        -------

        You can use any of the following signatures:

         * set_shininess(index: int, shine: float, /) -> None
         * set_shininess(shine: float, /) -> None

        Parameters
        ----------

        index: int
            vertex index

        shine: float
            degree of shininess

        Notes
        -----

        Sets the amount of gloss a `Py5Shape` object's surface has. This is part of the
        material properties of a `Py5Shape` object.

        The `shine` parameter can be applied to the entire `Py5Shape` object or to a
        single vertex.

        This method can only be used for a complete `Py5Shape` object, and never within
        a `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` pair.
        """
        pass

    @overload
    def set_shininess(self, index: int, shine: float, /) -> None:
        """Sets the amount of gloss a `Py5Shape` object's surface has.

        Underlying Processing method: PShape.setShininess

        Methods
        -------

        You can use any of the following signatures:

         * set_shininess(index: int, shine: float, /) -> None
         * set_shininess(shine: float, /) -> None

        Parameters
        ----------

        index: int
            vertex index

        shine: float
            degree of shininess

        Notes
        -----

        Sets the amount of gloss a `Py5Shape` object's surface has. This is part of the
        material properties of a `Py5Shape` object.

        The `shine` parameter can be applied to the entire `Py5Shape` object or to a
        single vertex.

        This method can only be used for a complete `Py5Shape` object, and never within
        a `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` pair.
        """
        pass

    def set_shininess(self, *args):
        """Sets the amount of gloss a `Py5Shape` object's surface has.

        Underlying Processing method: PShape.setShininess

        Methods
        -------

        You can use any of the following signatures:

         * set_shininess(index: int, shine: float, /) -> None
         * set_shininess(shine: float, /) -> None

        Parameters
        ----------

        index: int
            vertex index

        shine: float
            degree of shininess

        Notes
        -----

        Sets the amount of gloss a `Py5Shape` object's surface has. This is part of the
        material properties of a `Py5Shape` object.

        The `shine` parameter can be applied to the entire `Py5Shape` object or to a
        single vertex.

        This method can only be used for a complete `Py5Shape` object, and never within
        a `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` pair.
        """
        return self._instance.setShininess(*args)

    @overload
    def set_specular(self, specular: int, /) -> None:
        """Sets the specular color of a `Py5Shape` object's material, which sets the color
        of highlight.

        Underlying Processing method: PShape.setSpecular

        Methods
        -------

        You can use any of the following signatures:

         * set_specular(index: int, specular: int, /) -> None
         * set_specular(specular: int, /) -> None

        Parameters
        ----------

        index: int
            vertex index

        specular: int
            any color value

        Notes
        -----

        Sets the specular color of a `Py5Shape` object's material, which sets the color
        of highlight. This is part of the material properties of a `Py5Shape` object.

        The `specular` parameter can be applied to the entire `Py5Shape` object or to a
        single vertex.

        This method can only be used for a complete `Py5Shape` object, and never within
        a `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` pair.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def set_specular(self, index: int, specular: int, /) -> None:
        """Sets the specular color of a `Py5Shape` object's material, which sets the color
        of highlight.

        Underlying Processing method: PShape.setSpecular

        Methods
        -------

        You can use any of the following signatures:

         * set_specular(index: int, specular: int, /) -> None
         * set_specular(specular: int, /) -> None

        Parameters
        ----------

        index: int
            vertex index

        specular: int
            any color value

        Notes
        -----

        Sets the specular color of a `Py5Shape` object's material, which sets the color
        of highlight. This is part of the material properties of a `Py5Shape` object.

        The `specular` parameter can be applied to the entire `Py5Shape` object or to a
        single vertex.

        This method can only be used for a complete `Py5Shape` object, and never within
        a `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` pair.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @_convert_hex_color2
    def set_specular(self, *args):
        """Sets the specular color of a `Py5Shape` object's material, which sets the color
        of highlight.

        Underlying Processing method: PShape.setSpecular

        Methods
        -------

        You can use any of the following signatures:

         * set_specular(index: int, specular: int, /) -> None
         * set_specular(specular: int, /) -> None

        Parameters
        ----------

        index: int
            vertex index

        specular: int
            any color value

        Notes
        -----

        Sets the specular color of a `Py5Shape` object's material, which sets the color
        of highlight. This is part of the material properties of a `Py5Shape` object.

        The `specular` parameter can be applied to the entire `Py5Shape` object or to a
        single vertex.

        This method can only be used for a complete `Py5Shape` object, and never within
        a `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` pair.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        return self._instance.setSpecular(*args)

    @overload
    def set_stroke(self, stroke: bool, /) -> None:
        """The `set_stroke()` method defines the outline color of a `Py5Shape`.

        Underlying Processing method: PShape.setStroke

        Methods
        -------

        You can use any of the following signatures:

         * set_stroke(index: int, stroke: int, /) -> None
         * set_stroke(stroke: bool, /) -> None
         * set_stroke(stroke: int, /) -> None

        Parameters
        ----------

        index: int
            vertex index

        stroke: bool
            allow stroke

        stroke: int
            any color value

        Notes
        -----

        The `set_stroke()` method defines the outline color of a `Py5Shape`. This method
        is used after shapes are created or when a shape is defined explicitly (e.g.
        `create_shape(RECT, 20, 20, 60, 60)`) as shown in the example. When a shape is
        created with `Py5Shape.begin_shape()` and `Py5Shape.end_shape()`, its attributes
        may be changed with `Py5Shape.fill()` and `Py5Shape.stroke()` within
        `Py5Shape.begin_shape()` and `Py5Shape.end_shape()`. However, after the shape is
        created, only the `set_stroke()` method can define a new stroke value for the
        `Py5Shape`.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def set_stroke(self, stroke: int, /) -> None:
        """The `set_stroke()` method defines the outline color of a `Py5Shape`.

        Underlying Processing method: PShape.setStroke

        Methods
        -------

        You can use any of the following signatures:

         * set_stroke(index: int, stroke: int, /) -> None
         * set_stroke(stroke: bool, /) -> None
         * set_stroke(stroke: int, /) -> None

        Parameters
        ----------

        index: int
            vertex index

        stroke: bool
            allow stroke

        stroke: int
            any color value

        Notes
        -----

        The `set_stroke()` method defines the outline color of a `Py5Shape`. This method
        is used after shapes are created or when a shape is defined explicitly (e.g.
        `create_shape(RECT, 20, 20, 60, 60)`) as shown in the example. When a shape is
        created with `Py5Shape.begin_shape()` and `Py5Shape.end_shape()`, its attributes
        may be changed with `Py5Shape.fill()` and `Py5Shape.stroke()` within
        `Py5Shape.begin_shape()` and `Py5Shape.end_shape()`. However, after the shape is
        created, only the `set_stroke()` method can define a new stroke value for the
        `Py5Shape`.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def set_stroke(self, index: int, stroke: int, /) -> None:
        """The `set_stroke()` method defines the outline color of a `Py5Shape`.

        Underlying Processing method: PShape.setStroke

        Methods
        -------

        You can use any of the following signatures:

         * set_stroke(index: int, stroke: int, /) -> None
         * set_stroke(stroke: bool, /) -> None
         * set_stroke(stroke: int, /) -> None

        Parameters
        ----------

        index: int
            vertex index

        stroke: bool
            allow stroke

        stroke: int
            any color value

        Notes
        -----

        The `set_stroke()` method defines the outline color of a `Py5Shape`. This method
        is used after shapes are created or when a shape is defined explicitly (e.g.
        `create_shape(RECT, 20, 20, 60, 60)`) as shown in the example. When a shape is
        created with `Py5Shape.begin_shape()` and `Py5Shape.end_shape()`, its attributes
        may be changed with `Py5Shape.fill()` and `Py5Shape.stroke()` within
        `Py5Shape.begin_shape()` and `Py5Shape.end_shape()`. However, after the shape is
        created, only the `set_stroke()` method can define a new stroke value for the
        `Py5Shape`.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @_py5shape_type_fixer
    @_convert_hex_color2
    def set_stroke(self, *args):
        """The `set_stroke()` method defines the outline color of a `Py5Shape`.

        Underlying Processing method: PShape.setStroke

        Methods
        -------

        You can use any of the following signatures:

         * set_stroke(index: int, stroke: int, /) -> None
         * set_stroke(stroke: bool, /) -> None
         * set_stroke(stroke: int, /) -> None

        Parameters
        ----------

        index: int
            vertex index

        stroke: bool
            allow stroke

        stroke: int
            any color value

        Notes
        -----

        The `set_stroke()` method defines the outline color of a `Py5Shape`. This method
        is used after shapes are created or when a shape is defined explicitly (e.g.
        `create_shape(RECT, 20, 20, 60, 60)`) as shown in the example. When a shape is
        created with `Py5Shape.begin_shape()` and `Py5Shape.end_shape()`, its attributes
        may be changed with `Py5Shape.fill()` and `Py5Shape.stroke()` within
        `Py5Shape.begin_shape()` and `Py5Shape.end_shape()`. However, after the shape is
        created, only the `set_stroke()` method can define a new stroke value for the
        `Py5Shape`.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        return self._instance.setStroke(*args)

    def set_stroke_cap(self, cap: int, /) -> None:
        """Sets the style for rendering line endings in a `Py5Shape` object.

        Underlying Processing method: PShape.setStrokeCap

        Parameters
        ----------

        cap: int
            either SQUARE, PROJECT, or ROUND

        Notes
        -----

        Sets the style for rendering line endings in a `Py5Shape` object. These ends are
        either squared, extended, or rounded, each of which specified with the
        corresponding parameters: `SQUARE`, `PROJECT`, and `ROUND`. The default cap is
        `ROUND`.

        This method differs from `Py5Shape.stroke_cap()` in that it is only to be used
        outside the `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` methods.
        """
        return self._instance.setStrokeCap(cap)

    def set_stroke_join(self, join: int, /) -> None:
        """Sets the style of the joints which connect line segments in a `Py5Shape` object.

        Underlying Processing method: PShape.setStrokeJoin

        Parameters
        ----------

        join: int
            either MITER, BEVEL, ROUND

        Notes
        -----

        Sets the style of the joints which connect line segments in a `Py5Shape` object.
        These joints are either mitered, beveled, or rounded and specified with the
        corresponding parameters `MITER`, `BEVEL`, and `ROUND`. The default joint is
        `MITER`.

        This method differs from `Py5Shape.stroke_join()` in that it is only to be used
        outside the `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` methods.
        """
        return self._instance.setStrokeJoin(join)

    @overload
    def set_stroke_weight(self, weight: float, /) -> None:
        """Sets the width of the stroke used for lines and points in a `Py5Shape` object.

        Underlying Processing method: PShape.setStrokeWeight

        Methods
        -------

        You can use any of the following signatures:

         * set_stroke_weight(index: int, weight: float, /) -> None
         * set_stroke_weight(weight: float, /) -> None

        Parameters
        ----------

        index: int
            vertex index

        weight: float
            the weight (in pixels) of the stroke

        Notes
        -----

        Sets the width of the stroke used for lines and points in a `Py5Shape` object.
        All widths are set in units of pixels. Attempting to set this for individual
        vertices may not work, depending on the renderer used and other factors.

        This method differs from `Py5Shape.stroke_weight()` in that it is only to be
        used outside the `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` methods.
        """
        pass

    @overload
    def set_stroke_weight(self, index: int, weight: float, /) -> None:
        """Sets the width of the stroke used for lines and points in a `Py5Shape` object.

        Underlying Processing method: PShape.setStrokeWeight

        Methods
        -------

        You can use any of the following signatures:

         * set_stroke_weight(index: int, weight: float, /) -> None
         * set_stroke_weight(weight: float, /) -> None

        Parameters
        ----------

        index: int
            vertex index

        weight: float
            the weight (in pixels) of the stroke

        Notes
        -----

        Sets the width of the stroke used for lines and points in a `Py5Shape` object.
        All widths are set in units of pixels. Attempting to set this for individual
        vertices may not work, depending on the renderer used and other factors.

        This method differs from `Py5Shape.stroke_weight()` in that it is only to be
        used outside the `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` methods.
        """
        pass

    def set_stroke_weight(self, *args):
        """Sets the width of the stroke used for lines and points in a `Py5Shape` object.

        Underlying Processing method: PShape.setStrokeWeight

        Methods
        -------

        You can use any of the following signatures:

         * set_stroke_weight(index: int, weight: float, /) -> None
         * set_stroke_weight(weight: float, /) -> None

        Parameters
        ----------

        index: int
            vertex index

        weight: float
            the weight (in pixels) of the stroke

        Notes
        -----

        Sets the width of the stroke used for lines and points in a `Py5Shape` object.
        All widths are set in units of pixels. Attempting to set this for individual
        vertices may not work, depending on the renderer used and other factors.

        This method differs from `Py5Shape.stroke_weight()` in that it is only to be
        used outside the `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` methods.
        """
        return self._instance.setStrokeWeight(*args)

    def set_texture(self, tex: Py5Image, /) -> None:
        """Set a `Py5Shape` object's texture.

        Underlying Processing method: PShape.setTexture

        Parameters
        ----------

        tex: Py5Image
            reference to a Py5Image object

        Notes
        -----

        Set a `Py5Shape` object's texture. This method differs from `Py5Shape.texture()`
        in that it is only to be used outside the `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` methods. This method only works with the `P2D` and `P3D`
        renderers. This method can be used in conjunction with
        `Py5Shape.set_texture_mode()` and `Py5Shape.set_texture_uv()`.

        When textures are in use, the fill color is ignored. Instead, use
        `Py5Shape.tint()` to specify the color of the texture as it is applied to the
        shape.
        """
        return self._instance.setTexture(tex)

    def set_texture_mode(self, mode: int, /) -> None:
        """Sets a `Py5Shape` object's coordinate space for texture mapping.

        Underlying Processing method: PShape.setTextureMode

        Parameters
        ----------

        mode: int
            either IMAGE or NORMAL

        Notes
        -----

        Sets a `Py5Shape` object's coordinate space for texture mapping. This method
        differs from `Py5Shape.texture_mode()` in that it is only to be used outside the
        `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` methods. Use of this method
        should be followed by calls to `Py5Shape.set_texture_uv()` to set the mapping
        coordinates using the new mode.

        The default mode is `IMAGE`, which refers to the actual pixel coordinates of the
        image. `NORMAL` refers to a normalized space of values ranging from 0 to 1. This
        function only works with the `P2D` and `P3D` renderers.

        With `IMAGE`, if an image is 100 x 200 pixels, mapping the image onto the entire
        size of a quad would require the points (0,0) (100,0) (100,200) (0,200). The
        same mapping in `NORMAL` is (0,0) (1,0) (1,1) (0,1).
        """
        return self._instance.setTextureMode(mode)

    def set_texture_uv(self, index: int, u: float, v: float, /) -> None:
        """Set the uv texture mapping coordinates for a given vertex in a `Py5Shape`
        object.

        Underlying Processing method: PShape.setTextureUV

        Parameters
        ----------

        index: int
            vertex index

        u: float
            horizontal coordinate for the texture mapping

        v: float
            vertical coordinate for the texture mapping

        Notes
        -----

        Set the uv texture mapping coordinates for a given vertex in a `Py5Shape`
        object. This method can only be used outside the `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` methods.

        The `u` and `v` coordinates define the mapping of a `Py5Shape` object's texture
        to the form. By default, the coordinates used for `u` and `v` are specified in
        relation to the image's size in pixels, but this relation can be changed with
        the `Py5Shape` object's `Py5Shape.set_texture_mode()` method.
        """
        return self._instance.setTextureUV(index, u, v)

    @overload
    def set_tint(self, tint: bool, /) -> None:
        """Apply a color tint to a shape's texture map.

        Underlying Processing method: PShape.setTint

        Methods
        -------

        You can use any of the following signatures:

         * set_tint(fill: int, /) -> None
         * set_tint(index: int, tint: int, /) -> None
         * set_tint(tint: bool, /) -> None

        Parameters
        ----------

        fill: int
            color value in hexadecimal notation

        index: int
            vertex index

        tint: bool
            allow tint

        tint: int
            color value in hexadecimal notation

        Notes
        -----

        Apply a color tint to a shape's texture map. This can be done for either the
        entire shape or one vertex.

        This method differs from `Py5Shape.tint()` in that it is only to be used outside
        the `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` methods. This method
        only works with the `P2D` and `P3D` renderers.

        Calling this method with the boolean parameter `False` will delete the assigned
        tint. A later call with the boolean parameter `True` will not restore it; you
        must reassign the tint color, as shown in the second example.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def set_tint(self, fill: int, /) -> None:
        """Apply a color tint to a shape's texture map.

        Underlying Processing method: PShape.setTint

        Methods
        -------

        You can use any of the following signatures:

         * set_tint(fill: int, /) -> None
         * set_tint(index: int, tint: int, /) -> None
         * set_tint(tint: bool, /) -> None

        Parameters
        ----------

        fill: int
            color value in hexadecimal notation

        index: int
            vertex index

        tint: bool
            allow tint

        tint: int
            color value in hexadecimal notation

        Notes
        -----

        Apply a color tint to a shape's texture map. This can be done for either the
        entire shape or one vertex.

        This method differs from `Py5Shape.tint()` in that it is only to be used outside
        the `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` methods. This method
        only works with the `P2D` and `P3D` renderers.

        Calling this method with the boolean parameter `False` will delete the assigned
        tint. A later call with the boolean parameter `True` will not restore it; you
        must reassign the tint color, as shown in the second example.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def set_tint(self, index: int, tint: int, /) -> None:
        """Apply a color tint to a shape's texture map.

        Underlying Processing method: PShape.setTint

        Methods
        -------

        You can use any of the following signatures:

         * set_tint(fill: int, /) -> None
         * set_tint(index: int, tint: int, /) -> None
         * set_tint(tint: bool, /) -> None

        Parameters
        ----------

        fill: int
            color value in hexadecimal notation

        index: int
            vertex index

        tint: bool
            allow tint

        tint: int
            color value in hexadecimal notation

        Notes
        -----

        Apply a color tint to a shape's texture map. This can be done for either the
        entire shape or one vertex.

        This method differs from `Py5Shape.tint()` in that it is only to be used outside
        the `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` methods. This method
        only works with the `P2D` and `P3D` renderers.

        Calling this method with the boolean parameter `False` will delete the assigned
        tint. A later call with the boolean parameter `True` will not restore it; you
        must reassign the tint color, as shown in the second example.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @_py5shape_type_fixer
    @_convert_hex_color2
    def set_tint(self, *args):
        """Apply a color tint to a shape's texture map.

        Underlying Processing method: PShape.setTint

        Methods
        -------

        You can use any of the following signatures:

         * set_tint(fill: int, /) -> None
         * set_tint(index: int, tint: int, /) -> None
         * set_tint(tint: bool, /) -> None

        Parameters
        ----------

        fill: int
            color value in hexadecimal notation

        index: int
            vertex index

        tint: bool
            allow tint

        tint: int
            color value in hexadecimal notation

        Notes
        -----

        Apply a color tint to a shape's texture map. This can be done for either the
        entire shape or one vertex.

        This method differs from `Py5Shape.tint()` in that it is only to be used outside
        the `Py5Shape.begin_shape()` and `Py5Shape.end_shape()` methods. This method
        only works with the `P2D` and `P3D` renderers.

        Calling this method with the boolean parameter `False` will delete the assigned
        tint. A later call with the boolean parameter `True` will not restore it; you
        must reassign the tint color, as shown in the second example.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        return self._instance.setTint(*args)

    @overload
    def set_vertex(self, index: int, x: float, y: float, /) -> None:
        """The `set_vertex()` method defines the coordinates of the vertex point located at
        the position defined by the `index` parameter.

        Underlying Processing method: PShape.setVertex

        Methods
        -------

        You can use any of the following signatures:

         * set_vertex(index: int, vec: Py5Vector, /) -> None
         * set_vertex(index: int, x: float, y: float, /) -> None
         * set_vertex(index: int, x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        index: int
            the location of the vertex

        vec: Py5Vector
            the vector to define the x, y, z coordinates

        x: float
            the x value for the vertex

        y: float
            the y value for the vertex

        z: float
            the z value for the vertex

        Notes
        -----

        The `set_vertex()` method defines the coordinates of the vertex point located at
        the position defined by the `index` parameter. This method works when shapes are
        created as shown in the example, but won't work properly when a shape is defined
        explicitly (e.g. `create_shape(RECT, 20, 20, 80, 80)`.
        """
        pass

    @overload
    def set_vertex(self, index: int, x: float, y: float, z: float, /) -> None:
        """The `set_vertex()` method defines the coordinates of the vertex point located at
        the position defined by the `index` parameter.

        Underlying Processing method: PShape.setVertex

        Methods
        -------

        You can use any of the following signatures:

         * set_vertex(index: int, vec: Py5Vector, /) -> None
         * set_vertex(index: int, x: float, y: float, /) -> None
         * set_vertex(index: int, x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        index: int
            the location of the vertex

        vec: Py5Vector
            the vector to define the x, y, z coordinates

        x: float
            the x value for the vertex

        y: float
            the y value for the vertex

        z: float
            the z value for the vertex

        Notes
        -----

        The `set_vertex()` method defines the coordinates of the vertex point located at
        the position defined by the `index` parameter. This method works when shapes are
        created as shown in the example, but won't work properly when a shape is defined
        explicitly (e.g. `create_shape(RECT, 20, 20, 80, 80)`.
        """
        pass

    @overload
    def set_vertex(self, index: int, vec: Py5Vector, /) -> None:
        """The `set_vertex()` method defines the coordinates of the vertex point located at
        the position defined by the `index` parameter.

        Underlying Processing method: PShape.setVertex

        Methods
        -------

        You can use any of the following signatures:

         * set_vertex(index: int, vec: Py5Vector, /) -> None
         * set_vertex(index: int, x: float, y: float, /) -> None
         * set_vertex(index: int, x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        index: int
            the location of the vertex

        vec: Py5Vector
            the vector to define the x, y, z coordinates

        x: float
            the x value for the vertex

        y: float
            the y value for the vertex

        z: float
            the z value for the vertex

        Notes
        -----

        The `set_vertex()` method defines the coordinates of the vertex point located at
        the position defined by the `index` parameter. This method works when shapes are
        created as shown in the example, but won't work properly when a shape is defined
        explicitly (e.g. `create_shape(RECT, 20, 20, 80, 80)`.
        """
        pass

    def set_vertex(self, *args):
        """The `set_vertex()` method defines the coordinates of the vertex point located at
        the position defined by the `index` parameter.

        Underlying Processing method: PShape.setVertex

        Methods
        -------

        You can use any of the following signatures:

         * set_vertex(index: int, vec: Py5Vector, /) -> None
         * set_vertex(index: int, x: float, y: float, /) -> None
         * set_vertex(index: int, x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        index: int
            the location of the vertex

        vec: Py5Vector
            the vector to define the x, y, z coordinates

        x: float
            the x value for the vertex

        y: float
            the y value for the vertex

        z: float
            the z value for the vertex

        Notes
        -----

        The `set_vertex()` method defines the coordinates of the vertex point located at
        the position defined by the `index` parameter. This method works when shapes are
        created as shown in the example, but won't work properly when a shape is defined
        explicitly (e.g. `create_shape(RECT, 20, 20, 80, 80)`.
        """
        return self._instance.setVertex(*args)

    def set_visible(self, visible: bool, /) -> None:
        """Sets the shape to be visible or invisible.

        Underlying Processing method: PShape.setVisible

        Parameters
        ----------

        visible: bool
            False makes the shape invisible and True makes it visible

        Notes
        -----

        Sets the shape to be visible or invisible. This is determined by the value of
        the `visible` parameter.

        The default visibility of a shape is usually controlled by whatever program
        created the SVG file. For instance, this parameter is controlled by showing or
        hiding the shape in the layers palette in Adobe Illustrator.
        """
        return self._instance.setVisible(visible)

    def shininess(self, shine: float, /) -> None:
        """Sets the amount of gloss in the surface of a `Py5Shape` object.

        Underlying Processing method: PShape.shininess

        Parameters
        ----------

        shine: float
            degree of shininess

        Notes
        -----

        Sets the amount of gloss in the surface of a `Py5Shape` object. Use in
        combination with `Py5Shape.ambient()`, `Py5Shape.specular()`, and
        `Py5Shape.emissive()` to set the material properties of a `Py5Shape` object.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair. The shininess color setting will be applied to
        vertices added after the call to this method.
        """
        return self._instance.shininess(shine)

    @overload
    def specular(self, gray: float, /) -> None:
        """Sets the specular color of a `Py5Shape` object's material, which sets the color
        of highlight.

        Underlying Processing method: PShape.specular

        Methods
        -------

        You can use any of the following signatures:

         * specular(gray: float, /) -> None
         * specular(rgb: int, /) -> None
         * specular(x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        gray: float
            value between black and white, by default 0 to 255

        rgb: int
            color to set

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the specular color of a `Py5Shape` object's material, which sets the color
        of highlight. Specular refers to light which bounces off a surface in a
        preferred direction (rather than bouncing in all directions like a diffuse
        light). Use in combination with `Py5Shape.emissive()`, `Py5Shape.ambient()`, and
        `Py5Shape.shininess()` to set the material properties of a `Py5Shape` object.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair. The specular color setting will be applied to
        vertices added after the call to this method.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def specular(self, x: float, y: float, z: float, /) -> None:
        """Sets the specular color of a `Py5Shape` object's material, which sets the color
        of highlight.

        Underlying Processing method: PShape.specular

        Methods
        -------

        You can use any of the following signatures:

         * specular(gray: float, /) -> None
         * specular(rgb: int, /) -> None
         * specular(x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        gray: float
            value between black and white, by default 0 to 255

        rgb: int
            color to set

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the specular color of a `Py5Shape` object's material, which sets the color
        of highlight. Specular refers to light which bounces off a surface in a
        preferred direction (rather than bouncing in all directions like a diffuse
        light). Use in combination with `Py5Shape.emissive()`, `Py5Shape.ambient()`, and
        `Py5Shape.shininess()` to set the material properties of a `Py5Shape` object.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair. The specular color setting will be applied to
        vertices added after the call to this method.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def specular(self, rgb: int, /) -> None:
        """Sets the specular color of a `Py5Shape` object's material, which sets the color
        of highlight.

        Underlying Processing method: PShape.specular

        Methods
        -------

        You can use any of the following signatures:

         * specular(gray: float, /) -> None
         * specular(rgb: int, /) -> None
         * specular(x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        gray: float
            value between black and white, by default 0 to 255

        rgb: int
            color to set

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the specular color of a `Py5Shape` object's material, which sets the color
        of highlight. Specular refers to light which bounces off a surface in a
        preferred direction (rather than bouncing in all directions like a diffuse
        light). Use in combination with `Py5Shape.emissive()`, `Py5Shape.ambient()`, and
        `Py5Shape.shininess()` to set the material properties of a `Py5Shape` object.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair. The specular color setting will be applied to
        vertices added after the call to this method.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @_convert_hex_color()
    def specular(self, *args):
        """Sets the specular color of a `Py5Shape` object's material, which sets the color
        of highlight.

        Underlying Processing method: PShape.specular

        Methods
        -------

        You can use any of the following signatures:

         * specular(gray: float, /) -> None
         * specular(rgb: int, /) -> None
         * specular(x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        gray: float
            value between black and white, by default 0 to 255

        rgb: int
            color to set

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the specular color of a `Py5Shape` object's material, which sets the color
        of highlight. Specular refers to light which bounces off a surface in a
        preferred direction (rather than bouncing in all directions like a diffuse
        light). Use in combination with `Py5Shape.emissive()`, `Py5Shape.ambient()`, and
        `Py5Shape.shininess()` to set the material properties of a `Py5Shape` object.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair. The specular color setting will be applied to
        vertices added after the call to this method.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        return self._instance.specular(*args)

    @overload
    def stroke(self, gray: float, /) -> None:
        """Sets the color used to draw the `Py5Shape` object's lines.

        Underlying Processing method: PShape.stroke

        Methods
        -------

        You can use any of the following signatures:

         * stroke(gray: float, /) -> None
         * stroke(gray: float, alpha: float, /) -> None
         * stroke(rgb: int, /) -> None
         * stroke(rgb: int, alpha: float, /) -> None
         * stroke(x: float, y: float, z: float, /) -> None
         * stroke(x: float, y: float, z: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the stroke

        gray: float
            specifies a value between white and black

        rgb: int
            color value in hexadecimal notation

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the color used to draw the `Py5Shape` object's lines. This color is either
        specified in terms of the RGB or HSB color depending on the current
        `color_mode()`. The default color space is RGB, with each value in the range
        from 0 to 255.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair.

        When using hexadecimal notation to specify a color, use "`0x`" before the values
        (e.g., `0xFFCCFFAA`). The hexadecimal value must be specified with eight
        characters; the first two characters define the alpha component, and the
        remainder define the red, green, and blue components.

        When using web color notation to specify a color, create a string beginning with
        the "`#`" character followed by three, four, six, or eight characters. The
        example colors `"#D93"` and `"#DD9933"` specify red, green, and blue values (in
        that order) for the color and assume the color has no transparency. The example
        colors `"#D93F"` and `"#DD9933FF"` specify red, green, blue, and alpha values
        (in that order) for the color. Notice that in web color notation the alpha
        channel is last, which is consistent with CSS colors, and in hexadecimal
        notation the alpha channel is first, which is consistent with Processing color
        values.

        The value for the gray parameter must be less than or equal to the current
        maximum value as specified by `color_mode()`. The default maximum value is 255.

        When drawing in 2D with the default renderer, you may need
        `hint(ENABLE_STROKE_PURE)` to improve drawing quality (at the expense of
        performance). See the `hint()` documentation for more details.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def stroke(self, gray: float, alpha: float, /) -> None:
        """Sets the color used to draw the `Py5Shape` object's lines.

        Underlying Processing method: PShape.stroke

        Methods
        -------

        You can use any of the following signatures:

         * stroke(gray: float, /) -> None
         * stroke(gray: float, alpha: float, /) -> None
         * stroke(rgb: int, /) -> None
         * stroke(rgb: int, alpha: float, /) -> None
         * stroke(x: float, y: float, z: float, /) -> None
         * stroke(x: float, y: float, z: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the stroke

        gray: float
            specifies a value between white and black

        rgb: int
            color value in hexadecimal notation

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the color used to draw the `Py5Shape` object's lines. This color is either
        specified in terms of the RGB or HSB color depending on the current
        `color_mode()`. The default color space is RGB, with each value in the range
        from 0 to 255.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair.

        When using hexadecimal notation to specify a color, use "`0x`" before the values
        (e.g., `0xFFCCFFAA`). The hexadecimal value must be specified with eight
        characters; the first two characters define the alpha component, and the
        remainder define the red, green, and blue components.

        When using web color notation to specify a color, create a string beginning with
        the "`#`" character followed by three, four, six, or eight characters. The
        example colors `"#D93"` and `"#DD9933"` specify red, green, and blue values (in
        that order) for the color and assume the color has no transparency. The example
        colors `"#D93F"` and `"#DD9933FF"` specify red, green, blue, and alpha values
        (in that order) for the color. Notice that in web color notation the alpha
        channel is last, which is consistent with CSS colors, and in hexadecimal
        notation the alpha channel is first, which is consistent with Processing color
        values.

        The value for the gray parameter must be less than or equal to the current
        maximum value as specified by `color_mode()`. The default maximum value is 255.

        When drawing in 2D with the default renderer, you may need
        `hint(ENABLE_STROKE_PURE)` to improve drawing quality (at the expense of
        performance). See the `hint()` documentation for more details.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def stroke(self, x: float, y: float, z: float, /) -> None:
        """Sets the color used to draw the `Py5Shape` object's lines.

        Underlying Processing method: PShape.stroke

        Methods
        -------

        You can use any of the following signatures:

         * stroke(gray: float, /) -> None
         * stroke(gray: float, alpha: float, /) -> None
         * stroke(rgb: int, /) -> None
         * stroke(rgb: int, alpha: float, /) -> None
         * stroke(x: float, y: float, z: float, /) -> None
         * stroke(x: float, y: float, z: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the stroke

        gray: float
            specifies a value between white and black

        rgb: int
            color value in hexadecimal notation

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the color used to draw the `Py5Shape` object's lines. This color is either
        specified in terms of the RGB or HSB color depending on the current
        `color_mode()`. The default color space is RGB, with each value in the range
        from 0 to 255.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair.

        When using hexadecimal notation to specify a color, use "`0x`" before the values
        (e.g., `0xFFCCFFAA`). The hexadecimal value must be specified with eight
        characters; the first two characters define the alpha component, and the
        remainder define the red, green, and blue components.

        When using web color notation to specify a color, create a string beginning with
        the "`#`" character followed by three, four, six, or eight characters. The
        example colors `"#D93"` and `"#DD9933"` specify red, green, and blue values (in
        that order) for the color and assume the color has no transparency. The example
        colors `"#D93F"` and `"#DD9933FF"` specify red, green, blue, and alpha values
        (in that order) for the color. Notice that in web color notation the alpha
        channel is last, which is consistent with CSS colors, and in hexadecimal
        notation the alpha channel is first, which is consistent with Processing color
        values.

        The value for the gray parameter must be less than or equal to the current
        maximum value as specified by `color_mode()`. The default maximum value is 255.

        When drawing in 2D with the default renderer, you may need
        `hint(ENABLE_STROKE_PURE)` to improve drawing quality (at the expense of
        performance). See the `hint()` documentation for more details.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def stroke(self, x: float, y: float, z: float, alpha: float, /) -> None:
        """Sets the color used to draw the `Py5Shape` object's lines.

        Underlying Processing method: PShape.stroke

        Methods
        -------

        You can use any of the following signatures:

         * stroke(gray: float, /) -> None
         * stroke(gray: float, alpha: float, /) -> None
         * stroke(rgb: int, /) -> None
         * stroke(rgb: int, alpha: float, /) -> None
         * stroke(x: float, y: float, z: float, /) -> None
         * stroke(x: float, y: float, z: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the stroke

        gray: float
            specifies a value between white and black

        rgb: int
            color value in hexadecimal notation

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the color used to draw the `Py5Shape` object's lines. This color is either
        specified in terms of the RGB or HSB color depending on the current
        `color_mode()`. The default color space is RGB, with each value in the range
        from 0 to 255.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair.

        When using hexadecimal notation to specify a color, use "`0x`" before the values
        (e.g., `0xFFCCFFAA`). The hexadecimal value must be specified with eight
        characters; the first two characters define the alpha component, and the
        remainder define the red, green, and blue components.

        When using web color notation to specify a color, create a string beginning with
        the "`#`" character followed by three, four, six, or eight characters. The
        example colors `"#D93"` and `"#DD9933"` specify red, green, and blue values (in
        that order) for the color and assume the color has no transparency. The example
        colors `"#D93F"` and `"#DD9933FF"` specify red, green, blue, and alpha values
        (in that order) for the color. Notice that in web color notation the alpha
        channel is last, which is consistent with CSS colors, and in hexadecimal
        notation the alpha channel is first, which is consistent with Processing color
        values.

        The value for the gray parameter must be less than or equal to the current
        maximum value as specified by `color_mode()`. The default maximum value is 255.

        When drawing in 2D with the default renderer, you may need
        `hint(ENABLE_STROKE_PURE)` to improve drawing quality (at the expense of
        performance). See the `hint()` documentation for more details.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def stroke(self, rgb: int, /) -> None:
        """Sets the color used to draw the `Py5Shape` object's lines.

        Underlying Processing method: PShape.stroke

        Methods
        -------

        You can use any of the following signatures:

         * stroke(gray: float, /) -> None
         * stroke(gray: float, alpha: float, /) -> None
         * stroke(rgb: int, /) -> None
         * stroke(rgb: int, alpha: float, /) -> None
         * stroke(x: float, y: float, z: float, /) -> None
         * stroke(x: float, y: float, z: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the stroke

        gray: float
            specifies a value between white and black

        rgb: int
            color value in hexadecimal notation

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the color used to draw the `Py5Shape` object's lines. This color is either
        specified in terms of the RGB or HSB color depending on the current
        `color_mode()`. The default color space is RGB, with each value in the range
        from 0 to 255.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair.

        When using hexadecimal notation to specify a color, use "`0x`" before the values
        (e.g., `0xFFCCFFAA`). The hexadecimal value must be specified with eight
        characters; the first two characters define the alpha component, and the
        remainder define the red, green, and blue components.

        When using web color notation to specify a color, create a string beginning with
        the "`#`" character followed by three, four, six, or eight characters. The
        example colors `"#D93"` and `"#DD9933"` specify red, green, and blue values (in
        that order) for the color and assume the color has no transparency. The example
        colors `"#D93F"` and `"#DD9933FF"` specify red, green, blue, and alpha values
        (in that order) for the color. Notice that in web color notation the alpha
        channel is last, which is consistent with CSS colors, and in hexadecimal
        notation the alpha channel is first, which is consistent with Processing color
        values.

        The value for the gray parameter must be less than or equal to the current
        maximum value as specified by `color_mode()`. The default maximum value is 255.

        When drawing in 2D with the default renderer, you may need
        `hint(ENABLE_STROKE_PURE)` to improve drawing quality (at the expense of
        performance). See the `hint()` documentation for more details.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def stroke(self, rgb: int, alpha: float, /) -> None:
        """Sets the color used to draw the `Py5Shape` object's lines.

        Underlying Processing method: PShape.stroke

        Methods
        -------

        You can use any of the following signatures:

         * stroke(gray: float, /) -> None
         * stroke(gray: float, alpha: float, /) -> None
         * stroke(rgb: int, /) -> None
         * stroke(rgb: int, alpha: float, /) -> None
         * stroke(x: float, y: float, z: float, /) -> None
         * stroke(x: float, y: float, z: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the stroke

        gray: float
            specifies a value between white and black

        rgb: int
            color value in hexadecimal notation

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the color used to draw the `Py5Shape` object's lines. This color is either
        specified in terms of the RGB or HSB color depending on the current
        `color_mode()`. The default color space is RGB, with each value in the range
        from 0 to 255.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair.

        When using hexadecimal notation to specify a color, use "`0x`" before the values
        (e.g., `0xFFCCFFAA`). The hexadecimal value must be specified with eight
        characters; the first two characters define the alpha component, and the
        remainder define the red, green, and blue components.

        When using web color notation to specify a color, create a string beginning with
        the "`#`" character followed by three, four, six, or eight characters. The
        example colors `"#D93"` and `"#DD9933"` specify red, green, and blue values (in
        that order) for the color and assume the color has no transparency. The example
        colors `"#D93F"` and `"#DD9933FF"` specify red, green, blue, and alpha values
        (in that order) for the color. Notice that in web color notation the alpha
        channel is last, which is consistent with CSS colors, and in hexadecimal
        notation the alpha channel is first, which is consistent with Processing color
        values.

        The value for the gray parameter must be less than or equal to the current
        maximum value as specified by `color_mode()`. The default maximum value is 255.

        When drawing in 2D with the default renderer, you may need
        `hint(ENABLE_STROKE_PURE)` to improve drawing quality (at the expense of
        performance). See the `hint()` documentation for more details.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @_convert_hex_color()
    def stroke(self, *args):
        """Sets the color used to draw the `Py5Shape` object's lines.

        Underlying Processing method: PShape.stroke

        Methods
        -------

        You can use any of the following signatures:

         * stroke(gray: float, /) -> None
         * stroke(gray: float, alpha: float, /) -> None
         * stroke(rgb: int, /) -> None
         * stroke(rgb: int, alpha: float, /) -> None
         * stroke(x: float, y: float, z: float, /) -> None
         * stroke(x: float, y: float, z: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the stroke

        gray: float
            specifies a value between white and black

        rgb: int
            color value in hexadecimal notation

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the color used to draw the `Py5Shape` object's lines. This color is either
        specified in terms of the RGB or HSB color depending on the current
        `color_mode()`. The default color space is RGB, with each value in the range
        from 0 to 255.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair.

        When using hexadecimal notation to specify a color, use "`0x`" before the values
        (e.g., `0xFFCCFFAA`). The hexadecimal value must be specified with eight
        characters; the first two characters define the alpha component, and the
        remainder define the red, green, and blue components.

        When using web color notation to specify a color, create a string beginning with
        the "`#`" character followed by three, four, six, or eight characters. The
        example colors `"#D93"` and `"#DD9933"` specify red, green, and blue values (in
        that order) for the color and assume the color has no transparency. The example
        colors `"#D93F"` and `"#DD9933FF"` specify red, green, blue, and alpha values
        (in that order) for the color. Notice that in web color notation the alpha
        channel is last, which is consistent with CSS colors, and in hexadecimal
        notation the alpha channel is first, which is consistent with Processing color
        values.

        The value for the gray parameter must be less than or equal to the current
        maximum value as specified by `color_mode()`. The default maximum value is 255.

        When drawing in 2D with the default renderer, you may need
        `hint(ENABLE_STROKE_PURE)` to improve drawing quality (at the expense of
        performance). See the `hint()` documentation for more details.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        return self._instance.stroke(*args)

    def stroke_cap(self, cap: int, /) -> None:
        """Sets the style for rendering line endings in a `Py5Shape` object.

        Underlying Processing method: PShape.strokeCap

        Parameters
        ----------

        cap: int
            either SQUARE, PROJECT, or ROUND

        Notes
        -----

        Sets the style for rendering line endings in a `Py5Shape` object. These ends are
        either squared, extended, or rounded, each of which specified with the
        corresponding parameters: `SQUARE`, `PROJECT`, and `ROUND`. The default cap is
        `ROUND`.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair.
        """
        return self._instance.strokeCap(cap)

    def stroke_join(self, join: int, /) -> None:
        """Sets the style of the joints which connect line segments in a `Py5Shape` object.

        Underlying Processing method: PShape.strokeJoin

        Parameters
        ----------

        join: int
            either MITER, BEVEL, ROUND

        Notes
        -----

        Sets the style of the joints which connect line segments in a `Py5Shape` object.
        These joints are either mitered, beveled, or rounded and specified with the
        corresponding parameters `MITER`, `BEVEL`, and `ROUND`. The default joint is
        `MITER`.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair.
        """
        return self._instance.strokeJoin(join)

    def stroke_weight(self, weight: float, /) -> None:
        """Sets the width of the stroke used for lines and points in a `Py5Shape` object.

        Underlying Processing method: PShape.strokeWeight

        Parameters
        ----------

        weight: float
            the weight (in pixels) of the stroke

        Notes
        -----

        Sets the width of the stroke used for lines and points in a `Py5Shape` object.
        All widths are set in units of pixels.

        This method can only be used within a `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` pair.
        """
        return self._instance.strokeWeight(weight)

    def texture(self, tex: Py5Image, /) -> None:
        """Sets a texture to be applied to a `Py5Shape` object's vertex points.

        Underlying Processing method: PShape.texture

        Parameters
        ----------

        tex: Py5Image
            reference to a Py5Image object

        Notes
        -----

        Sets a texture to be applied to a `Py5Shape` object's vertex points. The
        `texture()` function must be called between `Py5Shape.begin_shape()` and
        `Py5Shape.end_shape()` and before any calls to `Py5Shape.vertex()`. This method
        only works with the `P2D` and `P3D` renderers.

        When textures are in use, the fill color is ignored. Instead, use
        `Py5Shape.tint()` to specify the color of the texture as it is applied to the
        shape.
        """
        return self._instance.texture(tex)

    def texture_mode(self, mode: int, /) -> None:
        """Sets a `Py5Shape` object's coordinate space for texture mapping.

        Underlying Processing method: PShape.textureMode

        Parameters
        ----------

        mode: int
            either IMAGE or NORMAL

        Notes
        -----

        Sets a `Py5Shape` object's coordinate space for texture mapping. The default
        mode is `IMAGE`, which refers to the actual pixel coordinates of the image.
        `NORMAL` refers to a normalized space of values ranging from 0 to 1. This
        function only works with the `P2D` and `P3D` renderers.

        If this method is not used, it will inherit the current texture mode setting
        from the Sketch when the shape is created.

        With `IMAGE`, if an image is 100 x 200 pixels, mapping the image onto the entire
        size of a quad would require the points (0,0) (100,0) (100,200) (0,200). The
        same mapping in `NORMAL` is (0,0) (1,0) (1,1) (0,1).
        """
        return self._instance.textureMode(mode)

    @overload
    def tint(self, gray: float, /) -> None:
        """Apply a color tint to a shape's texture map.

        Underlying Processing method: PShape.tint

        Methods
        -------

        You can use any of the following signatures:

         * tint(gray: float, /) -> None
         * tint(gray: float, alpha: float, /) -> None
         * tint(rgb: int, /) -> None
         * tint(rgb: int, alpha: float, /) -> None
         * tint(x: float, y: float, z: float, /) -> None
         * tint(x: float, y: float, z: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the image

        gray: float
            specifies a value between white and black

        rgb: int
            color value in hexadecimal notation

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Apply a color tint to a shape's texture map. The tint will be applied only to
        vertices after the call to `tint()`. Use `Py5Shape.no_tint()` to deactivate the
        tint.

        Images can be tinted to specified colors or made transparent by including an
        alpha value. To apply transparency to an image without affecting its color, use
        white as the tint color and specify an alpha value. For instance, `tint(255,
        128)` will make an image 50% transparent (assuming the default alpha range of
        0-255, which can be changed with `color_mode()`).

        When using hexadecimal notation to specify a color, use "`0x`" before the values
        (e.g., `0xFFCCFFAA`). The hexadecimal value must be specified with eight
        characters; the first two characters define the alpha component, and the
        remainder define the red, green, and blue components.

        When using web color notation to specify a color, create a string beginning with
        the "`#`" character followed by three, four, six, or eight characters. The
        example colors `"#D93"` and `"#DD9933"` specify red, green, and blue values (in
        that order) for the color and assume the color has no transparency. The example
        colors `"#D93F"` and `"#DD9933FF"` specify red, green, blue, and alpha values
        (in that order) for the color. Notice that in web color notation the alpha
        channel is last, which is consistent with CSS colors, and in hexadecimal
        notation the alpha channel is first, which is consistent with Processing color
        values.

        The value for the gray parameter must be less than or equal to the current
        maximum value as specified by `color_mode()`. The default maximum value is 255.

        The `tint()` function is also used to control the coloring of textures in 3D.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def tint(self, gray: float, alpha: float, /) -> None:
        """Apply a color tint to a shape's texture map.

        Underlying Processing method: PShape.tint

        Methods
        -------

        You can use any of the following signatures:

         * tint(gray: float, /) -> None
         * tint(gray: float, alpha: float, /) -> None
         * tint(rgb: int, /) -> None
         * tint(rgb: int, alpha: float, /) -> None
         * tint(x: float, y: float, z: float, /) -> None
         * tint(x: float, y: float, z: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the image

        gray: float
            specifies a value between white and black

        rgb: int
            color value in hexadecimal notation

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Apply a color tint to a shape's texture map. The tint will be applied only to
        vertices after the call to `tint()`. Use `Py5Shape.no_tint()` to deactivate the
        tint.

        Images can be tinted to specified colors or made transparent by including an
        alpha value. To apply transparency to an image without affecting its color, use
        white as the tint color and specify an alpha value. For instance, `tint(255,
        128)` will make an image 50% transparent (assuming the default alpha range of
        0-255, which can be changed with `color_mode()`).

        When using hexadecimal notation to specify a color, use "`0x`" before the values
        (e.g., `0xFFCCFFAA`). The hexadecimal value must be specified with eight
        characters; the first two characters define the alpha component, and the
        remainder define the red, green, and blue components.

        When using web color notation to specify a color, create a string beginning with
        the "`#`" character followed by three, four, six, or eight characters. The
        example colors `"#D93"` and `"#DD9933"` specify red, green, and blue values (in
        that order) for the color and assume the color has no transparency. The example
        colors `"#D93F"` and `"#DD9933FF"` specify red, green, blue, and alpha values
        (in that order) for the color. Notice that in web color notation the alpha
        channel is last, which is consistent with CSS colors, and in hexadecimal
        notation the alpha channel is first, which is consistent with Processing color
        values.

        The value for the gray parameter must be less than or equal to the current
        maximum value as specified by `color_mode()`. The default maximum value is 255.

        The `tint()` function is also used to control the coloring of textures in 3D.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def tint(self, x: float, y: float, z: float, /) -> None:
        """Apply a color tint to a shape's texture map.

        Underlying Processing method: PShape.tint

        Methods
        -------

        You can use any of the following signatures:

         * tint(gray: float, /) -> None
         * tint(gray: float, alpha: float, /) -> None
         * tint(rgb: int, /) -> None
         * tint(rgb: int, alpha: float, /) -> None
         * tint(x: float, y: float, z: float, /) -> None
         * tint(x: float, y: float, z: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the image

        gray: float
            specifies a value between white and black

        rgb: int
            color value in hexadecimal notation

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Apply a color tint to a shape's texture map. The tint will be applied only to
        vertices after the call to `tint()`. Use `Py5Shape.no_tint()` to deactivate the
        tint.

        Images can be tinted to specified colors or made transparent by including an
        alpha value. To apply transparency to an image without affecting its color, use
        white as the tint color and specify an alpha value. For instance, `tint(255,
        128)` will make an image 50% transparent (assuming the default alpha range of
        0-255, which can be changed with `color_mode()`).

        When using hexadecimal notation to specify a color, use "`0x`" before the values
        (e.g., `0xFFCCFFAA`). The hexadecimal value must be specified with eight
        characters; the first two characters define the alpha component, and the
        remainder define the red, green, and blue components.

        When using web color notation to specify a color, create a string beginning with
        the "`#`" character followed by three, four, six, or eight characters. The
        example colors `"#D93"` and `"#DD9933"` specify red, green, and blue values (in
        that order) for the color and assume the color has no transparency. The example
        colors `"#D93F"` and `"#DD9933FF"` specify red, green, blue, and alpha values
        (in that order) for the color. Notice that in web color notation the alpha
        channel is last, which is consistent with CSS colors, and in hexadecimal
        notation the alpha channel is first, which is consistent with Processing color
        values.

        The value for the gray parameter must be less than or equal to the current
        maximum value as specified by `color_mode()`. The default maximum value is 255.

        The `tint()` function is also used to control the coloring of textures in 3D.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def tint(self, x: float, y: float, z: float, alpha: float, /) -> None:
        """Apply a color tint to a shape's texture map.

        Underlying Processing method: PShape.tint

        Methods
        -------

        You can use any of the following signatures:

         * tint(gray: float, /) -> None
         * tint(gray: float, alpha: float, /) -> None
         * tint(rgb: int, /) -> None
         * tint(rgb: int, alpha: float, /) -> None
         * tint(x: float, y: float, z: float, /) -> None
         * tint(x: float, y: float, z: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the image

        gray: float
            specifies a value between white and black

        rgb: int
            color value in hexadecimal notation

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Apply a color tint to a shape's texture map. The tint will be applied only to
        vertices after the call to `tint()`. Use `Py5Shape.no_tint()` to deactivate the
        tint.

        Images can be tinted to specified colors or made transparent by including an
        alpha value. To apply transparency to an image without affecting its color, use
        white as the tint color and specify an alpha value. For instance, `tint(255,
        128)` will make an image 50% transparent (assuming the default alpha range of
        0-255, which can be changed with `color_mode()`).

        When using hexadecimal notation to specify a color, use "`0x`" before the values
        (e.g., `0xFFCCFFAA`). The hexadecimal value must be specified with eight
        characters; the first two characters define the alpha component, and the
        remainder define the red, green, and blue components.

        When using web color notation to specify a color, create a string beginning with
        the "`#`" character followed by three, four, six, or eight characters. The
        example colors `"#D93"` and `"#DD9933"` specify red, green, and blue values (in
        that order) for the color and assume the color has no transparency. The example
        colors `"#D93F"` and `"#DD9933FF"` specify red, green, blue, and alpha values
        (in that order) for the color. Notice that in web color notation the alpha
        channel is last, which is consistent with CSS colors, and in hexadecimal
        notation the alpha channel is first, which is consistent with Processing color
        values.

        The value for the gray parameter must be less than or equal to the current
        maximum value as specified by `color_mode()`. The default maximum value is 255.

        The `tint()` function is also used to control the coloring of textures in 3D.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def tint(self, rgb: int, /) -> None:
        """Apply a color tint to a shape's texture map.

        Underlying Processing method: PShape.tint

        Methods
        -------

        You can use any of the following signatures:

         * tint(gray: float, /) -> None
         * tint(gray: float, alpha: float, /) -> None
         * tint(rgb: int, /) -> None
         * tint(rgb: int, alpha: float, /) -> None
         * tint(x: float, y: float, z: float, /) -> None
         * tint(x: float, y: float, z: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the image

        gray: float
            specifies a value between white and black

        rgb: int
            color value in hexadecimal notation

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Apply a color tint to a shape's texture map. The tint will be applied only to
        vertices after the call to `tint()`. Use `Py5Shape.no_tint()` to deactivate the
        tint.

        Images can be tinted to specified colors or made transparent by including an
        alpha value. To apply transparency to an image without affecting its color, use
        white as the tint color and specify an alpha value. For instance, `tint(255,
        128)` will make an image 50% transparent (assuming the default alpha range of
        0-255, which can be changed with `color_mode()`).

        When using hexadecimal notation to specify a color, use "`0x`" before the values
        (e.g., `0xFFCCFFAA`). The hexadecimal value must be specified with eight
        characters; the first two characters define the alpha component, and the
        remainder define the red, green, and blue components.

        When using web color notation to specify a color, create a string beginning with
        the "`#`" character followed by three, four, six, or eight characters. The
        example colors `"#D93"` and `"#DD9933"` specify red, green, and blue values (in
        that order) for the color and assume the color has no transparency. The example
        colors `"#D93F"` and `"#DD9933FF"` specify red, green, blue, and alpha values
        (in that order) for the color. Notice that in web color notation the alpha
        channel is last, which is consistent with CSS colors, and in hexadecimal
        notation the alpha channel is first, which is consistent with Processing color
        values.

        The value for the gray parameter must be less than or equal to the current
        maximum value as specified by `color_mode()`. The default maximum value is 255.

        The `tint()` function is also used to control the coloring of textures in 3D.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def tint(self, rgb: int, alpha: float, /) -> None:
        """Apply a color tint to a shape's texture map.

        Underlying Processing method: PShape.tint

        Methods
        -------

        You can use any of the following signatures:

         * tint(gray: float, /) -> None
         * tint(gray: float, alpha: float, /) -> None
         * tint(rgb: int, /) -> None
         * tint(rgb: int, alpha: float, /) -> None
         * tint(x: float, y: float, z: float, /) -> None
         * tint(x: float, y: float, z: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the image

        gray: float
            specifies a value between white and black

        rgb: int
            color value in hexadecimal notation

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Apply a color tint to a shape's texture map. The tint will be applied only to
        vertices after the call to `tint()`. Use `Py5Shape.no_tint()` to deactivate the
        tint.

        Images can be tinted to specified colors or made transparent by including an
        alpha value. To apply transparency to an image without affecting its color, use
        white as the tint color and specify an alpha value. For instance, `tint(255,
        128)` will make an image 50% transparent (assuming the default alpha range of
        0-255, which can be changed with `color_mode()`).

        When using hexadecimal notation to specify a color, use "`0x`" before the values
        (e.g., `0xFFCCFFAA`). The hexadecimal value must be specified with eight
        characters; the first two characters define the alpha component, and the
        remainder define the red, green, and blue components.

        When using web color notation to specify a color, create a string beginning with
        the "`#`" character followed by three, four, six, or eight characters. The
        example colors `"#D93"` and `"#DD9933"` specify red, green, and blue values (in
        that order) for the color and assume the color has no transparency. The example
        colors `"#D93F"` and `"#DD9933FF"` specify red, green, blue, and alpha values
        (in that order) for the color. Notice that in web color notation the alpha
        channel is last, which is consistent with CSS colors, and in hexadecimal
        notation the alpha channel is first, which is consistent with Processing color
        values.

        The value for the gray parameter must be less than or equal to the current
        maximum value as specified by `color_mode()`. The default maximum value is 255.

        The `tint()` function is also used to control the coloring of textures in 3D.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @_convert_hex_color()
    def tint(self, *args):
        """Apply a color tint to a shape's texture map.

        Underlying Processing method: PShape.tint

        Methods
        -------

        You can use any of the following signatures:

         * tint(gray: float, /) -> None
         * tint(gray: float, alpha: float, /) -> None
         * tint(rgb: int, /) -> None
         * tint(rgb: int, alpha: float, /) -> None
         * tint(x: float, y: float, z: float, /) -> None
         * tint(x: float, y: float, z: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the image

        gray: float
            specifies a value between white and black

        rgb: int
            color value in hexadecimal notation

        x: float
            red or hue value (depending on current color mode)

        y: float
            green or saturation value (depending on current color mode)

        z: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Apply a color tint to a shape's texture map. The tint will be applied only to
        vertices after the call to `tint()`. Use `Py5Shape.no_tint()` to deactivate the
        tint.

        Images can be tinted to specified colors or made transparent by including an
        alpha value. To apply transparency to an image without affecting its color, use
        white as the tint color and specify an alpha value. For instance, `tint(255,
        128)` will make an image 50% transparent (assuming the default alpha range of
        0-255, which can be changed with `color_mode()`).

        When using hexadecimal notation to specify a color, use "`0x`" before the values
        (e.g., `0xFFCCFFAA`). The hexadecimal value must be specified with eight
        characters; the first two characters define the alpha component, and the
        remainder define the red, green, and blue components.

        When using web color notation to specify a color, create a string beginning with
        the "`#`" character followed by three, four, six, or eight characters. The
        example colors `"#D93"` and `"#DD9933"` specify red, green, and blue values (in
        that order) for the color and assume the color has no transparency. The example
        colors `"#D93F"` and `"#DD9933FF"` specify red, green, blue, and alpha values
        (in that order) for the color. Notice that in web color notation the alpha
        channel is last, which is consistent with CSS colors, and in hexadecimal
        notation the alpha channel is first, which is consistent with Processing color
        values.

        The value for the gray parameter must be less than or equal to the current
        maximum value as specified by `color_mode()`. The default maximum value is 255.

        The `tint()` function is also used to control the coloring of textures in 3D.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        return self._instance.tint(*args)

    @overload
    def translate(self, x: float, y: float, /) -> None:
        """Specifies an amount to displace the shape.

        Underlying Processing method: PShape.translate

        Methods
        -------

        You can use any of the following signatures:

         * translate(x: float, y: float, /) -> None
         * translate(x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        x: float
            left/right translation

        y: float
            up/down translation

        z: float
            forward/back translation

        Notes
        -----

        Specifies an amount to displace the shape. The `x` parameter specifies
        left/right translation, the `y` parameter specifies up/down translation, and the
        `z` parameter specifies translations toward/away from the screen. Subsequent
        calls to the method accumulates the effect. For example, calling `translate(50,
        0)` and then `translate(20, 0)` is the same as `translate(70, 0)`. This
        transformation is applied directly to the shape, it's not refreshed each time
        `draw()` is run.

        Using this method with the `z` parameter requires using the `P3D` parameter in
        combination with size.
        """
        pass

    @overload
    def translate(self, x: float, y: float, z: float, /) -> None:
        """Specifies an amount to displace the shape.

        Underlying Processing method: PShape.translate

        Methods
        -------

        You can use any of the following signatures:

         * translate(x: float, y: float, /) -> None
         * translate(x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        x: float
            left/right translation

        y: float
            up/down translation

        z: float
            forward/back translation

        Notes
        -----

        Specifies an amount to displace the shape. The `x` parameter specifies
        left/right translation, the `y` parameter specifies up/down translation, and the
        `z` parameter specifies translations toward/away from the screen. Subsequent
        calls to the method accumulates the effect. For example, calling `translate(50,
        0)` and then `translate(20, 0)` is the same as `translate(70, 0)`. This
        transformation is applied directly to the shape, it's not refreshed each time
        `draw()` is run.

        Using this method with the `z` parameter requires using the `P3D` parameter in
        combination with size.
        """
        pass

    def translate(self, *args):
        """Specifies an amount to displace the shape.

        Underlying Processing method: PShape.translate

        Methods
        -------

        You can use any of the following signatures:

         * translate(x: float, y: float, /) -> None
         * translate(x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        x: float
            left/right translation

        y: float
            up/down translation

        z: float
            forward/back translation

        Notes
        -----

        Specifies an amount to displace the shape. The `x` parameter specifies
        left/right translation, the `y` parameter specifies up/down translation, and the
        `z` parameter specifies translations toward/away from the screen. Subsequent
        calls to the method accumulates the effect. For example, calling `translate(50,
        0)` and then `translate(20, 0)` is the same as `translate(70, 0)`. This
        transformation is applied directly to the shape, it's not refreshed each time
        `draw()` is run.

        Using this method with the `z` parameter requires using the `P3D` parameter in
        combination with size.
        """
        return self._instance.translate(*args)

    @overload
    def vertex(self, x: float, y: float, /) -> None:
        """Add a new vertex to a `Py5Shape` object.

        Underlying Processing method: PShape.vertex

        Methods
        -------

        You can use any of the following signatures:

         * vertex(x: float, y: float, /) -> None
         * vertex(x: float, y: float, u: float, v: float, /) -> None
         * vertex(x: float, y: float, z: float, /) -> None
         * vertex(x: float, y: float, z: float, u: float, v: float, /) -> None

        Parameters
        ----------

        u: float
            horizontal coordinate for the texture mapping

        v: float
            vertical coordinate for the texture mapping

        x: float
            x-coordinate of the vertex

        y: float
            y-coordinate of the vertex

        z: float
            z-coordinate of the vertex

        Notes
        -----

        Add a new vertex to a `Py5Shape` object. All shapes are constructed by
        connecting a series of vertices. The `vertex()` method is used to specify the
        vertex coordinates for points, lines, triangles, quads, and polygons. It is used
        exclusively within the `Py5Shape.begin_shape()` and `Py5Shape.end_shape()`
        methods.

        Drawing a vertex in 3D using the `z` parameter requires the `P3D` renderer, as
        shown in the second example.

        This method is also used to map a texture onto geometry. The
        `Py5Shape.texture()` function declares the texture to apply to the geometry and
        the `u` and `v` coordinates define the mapping of this texture to the form. By
        default, the coordinates used for `u` and `v` are specified in relation to the
        image's size in pixels, but this relation can be changed with the `Py5Shape`
        object's `Py5Shape.texture_mode()` method or by calling the Sketch's
        `texture_mode()` method before the shape is created.
        """
        pass

    @overload
    def vertex(self, x: float, y: float, z: float, /) -> None:
        """Add a new vertex to a `Py5Shape` object.

        Underlying Processing method: PShape.vertex

        Methods
        -------

        You can use any of the following signatures:

         * vertex(x: float, y: float, /) -> None
         * vertex(x: float, y: float, u: float, v: float, /) -> None
         * vertex(x: float, y: float, z: float, /) -> None
         * vertex(x: float, y: float, z: float, u: float, v: float, /) -> None

        Parameters
        ----------

        u: float
            horizontal coordinate for the texture mapping

        v: float
            vertical coordinate for the texture mapping

        x: float
            x-coordinate of the vertex

        y: float
            y-coordinate of the vertex

        z: float
            z-coordinate of the vertex

        Notes
        -----

        Add a new vertex to a `Py5Shape` object. All shapes are constructed by
        connecting a series of vertices. The `vertex()` method is used to specify the
        vertex coordinates for points, lines, triangles, quads, and polygons. It is used
        exclusively within the `Py5Shape.begin_shape()` and `Py5Shape.end_shape()`
        methods.

        Drawing a vertex in 3D using the `z` parameter requires the `P3D` renderer, as
        shown in the second example.

        This method is also used to map a texture onto geometry. The
        `Py5Shape.texture()` function declares the texture to apply to the geometry and
        the `u` and `v` coordinates define the mapping of this texture to the form. By
        default, the coordinates used for `u` and `v` are specified in relation to the
        image's size in pixels, but this relation can be changed with the `Py5Shape`
        object's `Py5Shape.texture_mode()` method or by calling the Sketch's
        `texture_mode()` method before the shape is created.
        """
        pass

    @overload
    def vertex(self, x: float, y: float, u: float, v: float, /) -> None:
        """Add a new vertex to a `Py5Shape` object.

        Underlying Processing method: PShape.vertex

        Methods
        -------

        You can use any of the following signatures:

         * vertex(x: float, y: float, /) -> None
         * vertex(x: float, y: float, u: float, v: float, /) -> None
         * vertex(x: float, y: float, z: float, /) -> None
         * vertex(x: float, y: float, z: float, u: float, v: float, /) -> None

        Parameters
        ----------

        u: float
            horizontal coordinate for the texture mapping

        v: float
            vertical coordinate for the texture mapping

        x: float
            x-coordinate of the vertex

        y: float
            y-coordinate of the vertex

        z: float
            z-coordinate of the vertex

        Notes
        -----

        Add a new vertex to a `Py5Shape` object. All shapes are constructed by
        connecting a series of vertices. The `vertex()` method is used to specify the
        vertex coordinates for points, lines, triangles, quads, and polygons. It is used
        exclusively within the `Py5Shape.begin_shape()` and `Py5Shape.end_shape()`
        methods.

        Drawing a vertex in 3D using the `z` parameter requires the `P3D` renderer, as
        shown in the second example.

        This method is also used to map a texture onto geometry. The
        `Py5Shape.texture()` function declares the texture to apply to the geometry and
        the `u` and `v` coordinates define the mapping of this texture to the form. By
        default, the coordinates used for `u` and `v` are specified in relation to the
        image's size in pixels, but this relation can be changed with the `Py5Shape`
        object's `Py5Shape.texture_mode()` method or by calling the Sketch's
        `texture_mode()` method before the shape is created.
        """
        pass

    @overload
    def vertex(self, x: float, y: float, z: float, u: float, v: float, /) -> None:
        """Add a new vertex to a `Py5Shape` object.

        Underlying Processing method: PShape.vertex

        Methods
        -------

        You can use any of the following signatures:

         * vertex(x: float, y: float, /) -> None
         * vertex(x: float, y: float, u: float, v: float, /) -> None
         * vertex(x: float, y: float, z: float, /) -> None
         * vertex(x: float, y: float, z: float, u: float, v: float, /) -> None

        Parameters
        ----------

        u: float
            horizontal coordinate for the texture mapping

        v: float
            vertical coordinate for the texture mapping

        x: float
            x-coordinate of the vertex

        y: float
            y-coordinate of the vertex

        z: float
            z-coordinate of the vertex

        Notes
        -----

        Add a new vertex to a `Py5Shape` object. All shapes are constructed by
        connecting a series of vertices. The `vertex()` method is used to specify the
        vertex coordinates for points, lines, triangles, quads, and polygons. It is used
        exclusively within the `Py5Shape.begin_shape()` and `Py5Shape.end_shape()`
        methods.

        Drawing a vertex in 3D using the `z` parameter requires the `P3D` renderer, as
        shown in the second example.

        This method is also used to map a texture onto geometry. The
        `Py5Shape.texture()` function declares the texture to apply to the geometry and
        the `u` and `v` coordinates define the mapping of this texture to the form. By
        default, the coordinates used for `u` and `v` are specified in relation to the
        image's size in pixels, but this relation can be changed with the `Py5Shape`
        object's `Py5Shape.texture_mode()` method or by calling the Sketch's
        `texture_mode()` method before the shape is created.
        """
        pass

    def vertex(self, *args):
        """Add a new vertex to a `Py5Shape` object.

        Underlying Processing method: PShape.vertex

        Methods
        -------

        You can use any of the following signatures:

         * vertex(x: float, y: float, /) -> None
         * vertex(x: float, y: float, u: float, v: float, /) -> None
         * vertex(x: float, y: float, z: float, /) -> None
         * vertex(x: float, y: float, z: float, u: float, v: float, /) -> None

        Parameters
        ----------

        u: float
            horizontal coordinate for the texture mapping

        v: float
            vertical coordinate for the texture mapping

        x: float
            x-coordinate of the vertex

        y: float
            y-coordinate of the vertex

        z: float
            z-coordinate of the vertex

        Notes
        -----

        Add a new vertex to a `Py5Shape` object. All shapes are constructed by
        connecting a series of vertices. The `vertex()` method is used to specify the
        vertex coordinates for points, lines, triangles, quads, and polygons. It is used
        exclusively within the `Py5Shape.begin_shape()` and `Py5Shape.end_shape()`
        methods.

        Drawing a vertex in 3D using the `z` parameter requires the `P3D` renderer, as
        shown in the second example.

        This method is also used to map a texture onto geometry. The
        `Py5Shape.texture()` function declares the texture to apply to the geometry and
        the `u` and `v` coordinates define the mapping of this texture to the form. By
        default, the coordinates used for `u` and `v` are specified in relation to the
        image's size in pixels, but this relation can be changed with the `Py5Shape`
        object's `Py5Shape.texture_mode()` method or by calling the Sketch's
        `texture_mode()` method before the shape is created.
        """
        return self._instance.vertex(*args)
