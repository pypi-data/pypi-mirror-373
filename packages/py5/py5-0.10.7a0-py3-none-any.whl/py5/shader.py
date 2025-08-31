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
from typing import Any, Sequence, overload  # noqa

import numpy as np  # noqa
import numpy.typing as npt  # noqa
from jpype.types import JArray, JBoolean, JException, JFloat, JInt  # noqa

from . import spelling
from .image import Py5Image  # noqa
from .pmath import (  # noqa
    _numpy_to_pmatrix2d,
    _numpy_to_pmatrix3d,
    _numpy_to_pvector,
    _py5vector_to_pvector,
)
from .vector import Py5Vector


def _return_py5shader(f):
    @functools.wraps(f)
    def decorated(self_, *args):
        return Py5Shader(f(self_, *args))

    return decorated


def _load_py5shader(f):
    @functools.wraps(f)
    def decorated(self_, *args):
        try:
            return Py5Shader(f(self_, *args))
        except JException as e:
            msg = e.message()
            if msg == "None":
                msg = "shader file cannot be found"
        raise RuntimeError(
            "cannot load shader file " + str(args[0]) + ". error message: " + msg
        )

    return decorated


def _py5shader_set_wrapper(f):
    @functools.wraps(f)
    def decorated(self_, name, *args):
        if isinstance(args[0], np.ndarray):
            array = args[0]
            if array.shape in [(2,), (3,)]:
                args = _numpy_to_pvector(array), *args[1:]
            elif array.shape == (2, 3):
                args = _numpy_to_pmatrix2d(array), *args[1:]
            elif array.shape == (4, 4):
                args = _numpy_to_pmatrix3d(array), *args[1:]
        elif isinstance(args[0], Py5Vector):
            args = _py5vector_to_pvector(args[0]), *args[1:]
        else:

            def fix_type(arg):
                if isinstance(arg, bool):
                    return JBoolean(arg)
                elif isinstance(arg, int):
                    return JInt(arg)
                elif isinstance(arg, float):
                    return JFloat(arg)
                else:
                    return arg

            args = [fix_type(a) for a in args]
        return f(self_, name, *args)

    return decorated


class Py5Shader:
    """This class encapsulates a GLSL shader program, including a vertex and a fragment
    shader.

    Underlying Processing class: PShader.PShader

    Notes
    -----

    This class encapsulates a GLSL shader program, including a vertex and a fragment
    shader. It's compatible with the `P2D` and `P3D` renderers, but not with the
    default renderer. Use the `load_shader()` function to load your shader code and
    create `Py5Shader` objects."""

    _py5_object_cache = weakref.WeakSet()

    def __new__(cls, pshader):
        for o in cls._py5_object_cache:
            if pshader == o._instance:
                return o
        else:
            o = object.__new__(Py5Shader)
            o._instance = pshader
            cls._py5_object_cache.add(o)
            return o

    def __str__(self) -> str:
        return f"Py5Shader(id=" + str(id(self)) + ")"

    def __repr__(self) -> str:
        return self.__str__()

    def __getattr__(self, name):
        raise AttributeError(spelling.error_msg("Py5Shader", name, self))

    @overload
    def set(self, name: str, x: bool, /) -> None:
        """Sets the uniform variables inside the shader to modify the effect while the
        program is running.

        Underlying Processing method: PShader.set

        Methods
        -------

        You can use any of the following signatures:

         * set(name: str, boolvec: Sequence[bool], ncoords: int, /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], use3x3: bool, /) -> None
         * set(name: str, tex: Py5Image, /) -> None
         * set(name: str, vec: Py5Vector, /) -> None
         * set(name: str, vec: Sequence[bool], /) -> None
         * set(name: str, vec: Sequence[float], /) -> None
         * set(name: str, vec: Sequence[float], ncoords: int, /) -> None
         * set(name: str, vec: Sequence[int], /) -> None
         * set(name: str, vec: Sequence[int], ncoords: int, /) -> None
         * set(name: str, x: bool, /) -> None
         * set(name: str, x: bool, y: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, w: bool, /) -> None
         * set(name: str, x: float, /) -> None
         * set(name: str, x: float, y: float, /) -> None
         * set(name: str, x: float, y: float, z: float, /) -> None
         * set(name: str, x: float, y: float, z: float, w: float, /) -> None
         * set(name: str, x: int, /) -> None
         * set(name: str, x: int, y: int, /) -> None
         * set(name: str, x: int, y: int, z: int, /) -> None
         * set(name: str, x: int, y: int, z: int, w: int, /) -> None

        Parameters
        ----------

        boolvec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        mat: npt.NDArray[np.floating]
            2D numpy array of values with shape 2x3 for 2D matrices or 4x4 for 3D matrices

        name: str
            the name of the uniform variable to modify

        ncoords: int
            number of coordinates per element, max 4

        tex: Py5Image
            sets the sampler uniform variable to read from this image texture

        use3x3: bool
            enforces the numpy array is 3 x 3

        vec: Py5Vector
            vector of values to modify all the components of an array/vector uniform variable

        vec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        vec: Sequence[float]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        vec: Sequence[int]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        w: bool
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: float
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: int
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        x: bool
            first component of the variable to modify

        x: float
            first component of the variable to modify

        x: int
            first component of the variable to modify

        y: bool
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: float
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: int
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        z: bool
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: float
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: int
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        Notes
        -----

        Sets the uniform variables inside the shader to modify the effect while the
        program is running.
        """
        pass

    @overload
    def set(self, name: str, x: bool, y: bool, /) -> None:
        """Sets the uniform variables inside the shader to modify the effect while the
        program is running.

        Underlying Processing method: PShader.set

        Methods
        -------

        You can use any of the following signatures:

         * set(name: str, boolvec: Sequence[bool], ncoords: int, /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], use3x3: bool, /) -> None
         * set(name: str, tex: Py5Image, /) -> None
         * set(name: str, vec: Py5Vector, /) -> None
         * set(name: str, vec: Sequence[bool], /) -> None
         * set(name: str, vec: Sequence[float], /) -> None
         * set(name: str, vec: Sequence[float], ncoords: int, /) -> None
         * set(name: str, vec: Sequence[int], /) -> None
         * set(name: str, vec: Sequence[int], ncoords: int, /) -> None
         * set(name: str, x: bool, /) -> None
         * set(name: str, x: bool, y: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, w: bool, /) -> None
         * set(name: str, x: float, /) -> None
         * set(name: str, x: float, y: float, /) -> None
         * set(name: str, x: float, y: float, z: float, /) -> None
         * set(name: str, x: float, y: float, z: float, w: float, /) -> None
         * set(name: str, x: int, /) -> None
         * set(name: str, x: int, y: int, /) -> None
         * set(name: str, x: int, y: int, z: int, /) -> None
         * set(name: str, x: int, y: int, z: int, w: int, /) -> None

        Parameters
        ----------

        boolvec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        mat: npt.NDArray[np.floating]
            2D numpy array of values with shape 2x3 for 2D matrices or 4x4 for 3D matrices

        name: str
            the name of the uniform variable to modify

        ncoords: int
            number of coordinates per element, max 4

        tex: Py5Image
            sets the sampler uniform variable to read from this image texture

        use3x3: bool
            enforces the numpy array is 3 x 3

        vec: Py5Vector
            vector of values to modify all the components of an array/vector uniform variable

        vec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        vec: Sequence[float]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        vec: Sequence[int]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        w: bool
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: float
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: int
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        x: bool
            first component of the variable to modify

        x: float
            first component of the variable to modify

        x: int
            first component of the variable to modify

        y: bool
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: float
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: int
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        z: bool
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: float
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: int
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        Notes
        -----

        Sets the uniform variables inside the shader to modify the effect while the
        program is running.
        """
        pass

    @overload
    def set(self, name: str, x: bool, y: bool, z: bool, /) -> None:
        """Sets the uniform variables inside the shader to modify the effect while the
        program is running.

        Underlying Processing method: PShader.set

        Methods
        -------

        You can use any of the following signatures:

         * set(name: str, boolvec: Sequence[bool], ncoords: int, /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], use3x3: bool, /) -> None
         * set(name: str, tex: Py5Image, /) -> None
         * set(name: str, vec: Py5Vector, /) -> None
         * set(name: str, vec: Sequence[bool], /) -> None
         * set(name: str, vec: Sequence[float], /) -> None
         * set(name: str, vec: Sequence[float], ncoords: int, /) -> None
         * set(name: str, vec: Sequence[int], /) -> None
         * set(name: str, vec: Sequence[int], ncoords: int, /) -> None
         * set(name: str, x: bool, /) -> None
         * set(name: str, x: bool, y: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, w: bool, /) -> None
         * set(name: str, x: float, /) -> None
         * set(name: str, x: float, y: float, /) -> None
         * set(name: str, x: float, y: float, z: float, /) -> None
         * set(name: str, x: float, y: float, z: float, w: float, /) -> None
         * set(name: str, x: int, /) -> None
         * set(name: str, x: int, y: int, /) -> None
         * set(name: str, x: int, y: int, z: int, /) -> None
         * set(name: str, x: int, y: int, z: int, w: int, /) -> None

        Parameters
        ----------

        boolvec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        mat: npt.NDArray[np.floating]
            2D numpy array of values with shape 2x3 for 2D matrices or 4x4 for 3D matrices

        name: str
            the name of the uniform variable to modify

        ncoords: int
            number of coordinates per element, max 4

        tex: Py5Image
            sets the sampler uniform variable to read from this image texture

        use3x3: bool
            enforces the numpy array is 3 x 3

        vec: Py5Vector
            vector of values to modify all the components of an array/vector uniform variable

        vec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        vec: Sequence[float]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        vec: Sequence[int]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        w: bool
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: float
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: int
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        x: bool
            first component of the variable to modify

        x: float
            first component of the variable to modify

        x: int
            first component of the variable to modify

        y: bool
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: float
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: int
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        z: bool
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: float
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: int
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        Notes
        -----

        Sets the uniform variables inside the shader to modify the effect while the
        program is running.
        """
        pass

    @overload
    def set(self, name: str, x: bool, y: bool, z: bool, w: bool, /) -> None:
        """Sets the uniform variables inside the shader to modify the effect while the
        program is running.

        Underlying Processing method: PShader.set

        Methods
        -------

        You can use any of the following signatures:

         * set(name: str, boolvec: Sequence[bool], ncoords: int, /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], use3x3: bool, /) -> None
         * set(name: str, tex: Py5Image, /) -> None
         * set(name: str, vec: Py5Vector, /) -> None
         * set(name: str, vec: Sequence[bool], /) -> None
         * set(name: str, vec: Sequence[float], /) -> None
         * set(name: str, vec: Sequence[float], ncoords: int, /) -> None
         * set(name: str, vec: Sequence[int], /) -> None
         * set(name: str, vec: Sequence[int], ncoords: int, /) -> None
         * set(name: str, x: bool, /) -> None
         * set(name: str, x: bool, y: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, w: bool, /) -> None
         * set(name: str, x: float, /) -> None
         * set(name: str, x: float, y: float, /) -> None
         * set(name: str, x: float, y: float, z: float, /) -> None
         * set(name: str, x: float, y: float, z: float, w: float, /) -> None
         * set(name: str, x: int, /) -> None
         * set(name: str, x: int, y: int, /) -> None
         * set(name: str, x: int, y: int, z: int, /) -> None
         * set(name: str, x: int, y: int, z: int, w: int, /) -> None

        Parameters
        ----------

        boolvec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        mat: npt.NDArray[np.floating]
            2D numpy array of values with shape 2x3 for 2D matrices or 4x4 for 3D matrices

        name: str
            the name of the uniform variable to modify

        ncoords: int
            number of coordinates per element, max 4

        tex: Py5Image
            sets the sampler uniform variable to read from this image texture

        use3x3: bool
            enforces the numpy array is 3 x 3

        vec: Py5Vector
            vector of values to modify all the components of an array/vector uniform variable

        vec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        vec: Sequence[float]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        vec: Sequence[int]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        w: bool
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: float
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: int
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        x: bool
            first component of the variable to modify

        x: float
            first component of the variable to modify

        x: int
            first component of the variable to modify

        y: bool
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: float
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: int
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        z: bool
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: float
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: int
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        Notes
        -----

        Sets the uniform variables inside the shader to modify the effect while the
        program is running.
        """
        pass

    @overload
    def set(self, name: str, vec: Sequence[bool], /) -> None:
        """Sets the uniform variables inside the shader to modify the effect while the
        program is running.

        Underlying Processing method: PShader.set

        Methods
        -------

        You can use any of the following signatures:

         * set(name: str, boolvec: Sequence[bool], ncoords: int, /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], use3x3: bool, /) -> None
         * set(name: str, tex: Py5Image, /) -> None
         * set(name: str, vec: Py5Vector, /) -> None
         * set(name: str, vec: Sequence[bool], /) -> None
         * set(name: str, vec: Sequence[float], /) -> None
         * set(name: str, vec: Sequence[float], ncoords: int, /) -> None
         * set(name: str, vec: Sequence[int], /) -> None
         * set(name: str, vec: Sequence[int], ncoords: int, /) -> None
         * set(name: str, x: bool, /) -> None
         * set(name: str, x: bool, y: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, w: bool, /) -> None
         * set(name: str, x: float, /) -> None
         * set(name: str, x: float, y: float, /) -> None
         * set(name: str, x: float, y: float, z: float, /) -> None
         * set(name: str, x: float, y: float, z: float, w: float, /) -> None
         * set(name: str, x: int, /) -> None
         * set(name: str, x: int, y: int, /) -> None
         * set(name: str, x: int, y: int, z: int, /) -> None
         * set(name: str, x: int, y: int, z: int, w: int, /) -> None

        Parameters
        ----------

        boolvec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        mat: npt.NDArray[np.floating]
            2D numpy array of values with shape 2x3 for 2D matrices or 4x4 for 3D matrices

        name: str
            the name of the uniform variable to modify

        ncoords: int
            number of coordinates per element, max 4

        tex: Py5Image
            sets the sampler uniform variable to read from this image texture

        use3x3: bool
            enforces the numpy array is 3 x 3

        vec: Py5Vector
            vector of values to modify all the components of an array/vector uniform variable

        vec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        vec: Sequence[float]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        vec: Sequence[int]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        w: bool
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: float
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: int
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        x: bool
            first component of the variable to modify

        x: float
            first component of the variable to modify

        x: int
            first component of the variable to modify

        y: bool
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: float
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: int
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        z: bool
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: float
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: int
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        Notes
        -----

        Sets the uniform variables inside the shader to modify the effect while the
        program is running.
        """
        pass

    @overload
    def set(self, name: str, boolvec: Sequence[bool], ncoords: int, /) -> None:
        """Sets the uniform variables inside the shader to modify the effect while the
        program is running.

        Underlying Processing method: PShader.set

        Methods
        -------

        You can use any of the following signatures:

         * set(name: str, boolvec: Sequence[bool], ncoords: int, /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], use3x3: bool, /) -> None
         * set(name: str, tex: Py5Image, /) -> None
         * set(name: str, vec: Py5Vector, /) -> None
         * set(name: str, vec: Sequence[bool], /) -> None
         * set(name: str, vec: Sequence[float], /) -> None
         * set(name: str, vec: Sequence[float], ncoords: int, /) -> None
         * set(name: str, vec: Sequence[int], /) -> None
         * set(name: str, vec: Sequence[int], ncoords: int, /) -> None
         * set(name: str, x: bool, /) -> None
         * set(name: str, x: bool, y: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, w: bool, /) -> None
         * set(name: str, x: float, /) -> None
         * set(name: str, x: float, y: float, /) -> None
         * set(name: str, x: float, y: float, z: float, /) -> None
         * set(name: str, x: float, y: float, z: float, w: float, /) -> None
         * set(name: str, x: int, /) -> None
         * set(name: str, x: int, y: int, /) -> None
         * set(name: str, x: int, y: int, z: int, /) -> None
         * set(name: str, x: int, y: int, z: int, w: int, /) -> None

        Parameters
        ----------

        boolvec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        mat: npt.NDArray[np.floating]
            2D numpy array of values with shape 2x3 for 2D matrices or 4x4 for 3D matrices

        name: str
            the name of the uniform variable to modify

        ncoords: int
            number of coordinates per element, max 4

        tex: Py5Image
            sets the sampler uniform variable to read from this image texture

        use3x3: bool
            enforces the numpy array is 3 x 3

        vec: Py5Vector
            vector of values to modify all the components of an array/vector uniform variable

        vec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        vec: Sequence[float]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        vec: Sequence[int]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        w: bool
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: float
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: int
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        x: bool
            first component of the variable to modify

        x: float
            first component of the variable to modify

        x: int
            first component of the variable to modify

        y: bool
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: float
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: int
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        z: bool
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: float
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: int
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        Notes
        -----

        Sets the uniform variables inside the shader to modify the effect while the
        program is running.
        """
        pass

    @overload
    def set(self, name: str, x: float, /) -> None:
        """Sets the uniform variables inside the shader to modify the effect while the
        program is running.

        Underlying Processing method: PShader.set

        Methods
        -------

        You can use any of the following signatures:

         * set(name: str, boolvec: Sequence[bool], ncoords: int, /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], use3x3: bool, /) -> None
         * set(name: str, tex: Py5Image, /) -> None
         * set(name: str, vec: Py5Vector, /) -> None
         * set(name: str, vec: Sequence[bool], /) -> None
         * set(name: str, vec: Sequence[float], /) -> None
         * set(name: str, vec: Sequence[float], ncoords: int, /) -> None
         * set(name: str, vec: Sequence[int], /) -> None
         * set(name: str, vec: Sequence[int], ncoords: int, /) -> None
         * set(name: str, x: bool, /) -> None
         * set(name: str, x: bool, y: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, w: bool, /) -> None
         * set(name: str, x: float, /) -> None
         * set(name: str, x: float, y: float, /) -> None
         * set(name: str, x: float, y: float, z: float, /) -> None
         * set(name: str, x: float, y: float, z: float, w: float, /) -> None
         * set(name: str, x: int, /) -> None
         * set(name: str, x: int, y: int, /) -> None
         * set(name: str, x: int, y: int, z: int, /) -> None
         * set(name: str, x: int, y: int, z: int, w: int, /) -> None

        Parameters
        ----------

        boolvec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        mat: npt.NDArray[np.floating]
            2D numpy array of values with shape 2x3 for 2D matrices or 4x4 for 3D matrices

        name: str
            the name of the uniform variable to modify

        ncoords: int
            number of coordinates per element, max 4

        tex: Py5Image
            sets the sampler uniform variable to read from this image texture

        use3x3: bool
            enforces the numpy array is 3 x 3

        vec: Py5Vector
            vector of values to modify all the components of an array/vector uniform variable

        vec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        vec: Sequence[float]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        vec: Sequence[int]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        w: bool
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: float
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: int
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        x: bool
            first component of the variable to modify

        x: float
            first component of the variable to modify

        x: int
            first component of the variable to modify

        y: bool
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: float
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: int
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        z: bool
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: float
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: int
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        Notes
        -----

        Sets the uniform variables inside the shader to modify the effect while the
        program is running.
        """
        pass

    @overload
    def set(self, name: str, x: float, y: float, /) -> None:
        """Sets the uniform variables inside the shader to modify the effect while the
        program is running.

        Underlying Processing method: PShader.set

        Methods
        -------

        You can use any of the following signatures:

         * set(name: str, boolvec: Sequence[bool], ncoords: int, /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], use3x3: bool, /) -> None
         * set(name: str, tex: Py5Image, /) -> None
         * set(name: str, vec: Py5Vector, /) -> None
         * set(name: str, vec: Sequence[bool], /) -> None
         * set(name: str, vec: Sequence[float], /) -> None
         * set(name: str, vec: Sequence[float], ncoords: int, /) -> None
         * set(name: str, vec: Sequence[int], /) -> None
         * set(name: str, vec: Sequence[int], ncoords: int, /) -> None
         * set(name: str, x: bool, /) -> None
         * set(name: str, x: bool, y: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, w: bool, /) -> None
         * set(name: str, x: float, /) -> None
         * set(name: str, x: float, y: float, /) -> None
         * set(name: str, x: float, y: float, z: float, /) -> None
         * set(name: str, x: float, y: float, z: float, w: float, /) -> None
         * set(name: str, x: int, /) -> None
         * set(name: str, x: int, y: int, /) -> None
         * set(name: str, x: int, y: int, z: int, /) -> None
         * set(name: str, x: int, y: int, z: int, w: int, /) -> None

        Parameters
        ----------

        boolvec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        mat: npt.NDArray[np.floating]
            2D numpy array of values with shape 2x3 for 2D matrices or 4x4 for 3D matrices

        name: str
            the name of the uniform variable to modify

        ncoords: int
            number of coordinates per element, max 4

        tex: Py5Image
            sets the sampler uniform variable to read from this image texture

        use3x3: bool
            enforces the numpy array is 3 x 3

        vec: Py5Vector
            vector of values to modify all the components of an array/vector uniform variable

        vec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        vec: Sequence[float]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        vec: Sequence[int]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        w: bool
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: float
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: int
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        x: bool
            first component of the variable to modify

        x: float
            first component of the variable to modify

        x: int
            first component of the variable to modify

        y: bool
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: float
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: int
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        z: bool
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: float
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: int
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        Notes
        -----

        Sets the uniform variables inside the shader to modify the effect while the
        program is running.
        """
        pass

    @overload
    def set(self, name: str, x: float, y: float, z: float, /) -> None:
        """Sets the uniform variables inside the shader to modify the effect while the
        program is running.

        Underlying Processing method: PShader.set

        Methods
        -------

        You can use any of the following signatures:

         * set(name: str, boolvec: Sequence[bool], ncoords: int, /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], use3x3: bool, /) -> None
         * set(name: str, tex: Py5Image, /) -> None
         * set(name: str, vec: Py5Vector, /) -> None
         * set(name: str, vec: Sequence[bool], /) -> None
         * set(name: str, vec: Sequence[float], /) -> None
         * set(name: str, vec: Sequence[float], ncoords: int, /) -> None
         * set(name: str, vec: Sequence[int], /) -> None
         * set(name: str, vec: Sequence[int], ncoords: int, /) -> None
         * set(name: str, x: bool, /) -> None
         * set(name: str, x: bool, y: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, w: bool, /) -> None
         * set(name: str, x: float, /) -> None
         * set(name: str, x: float, y: float, /) -> None
         * set(name: str, x: float, y: float, z: float, /) -> None
         * set(name: str, x: float, y: float, z: float, w: float, /) -> None
         * set(name: str, x: int, /) -> None
         * set(name: str, x: int, y: int, /) -> None
         * set(name: str, x: int, y: int, z: int, /) -> None
         * set(name: str, x: int, y: int, z: int, w: int, /) -> None

        Parameters
        ----------

        boolvec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        mat: npt.NDArray[np.floating]
            2D numpy array of values with shape 2x3 for 2D matrices or 4x4 for 3D matrices

        name: str
            the name of the uniform variable to modify

        ncoords: int
            number of coordinates per element, max 4

        tex: Py5Image
            sets the sampler uniform variable to read from this image texture

        use3x3: bool
            enforces the numpy array is 3 x 3

        vec: Py5Vector
            vector of values to modify all the components of an array/vector uniform variable

        vec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        vec: Sequence[float]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        vec: Sequence[int]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        w: bool
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: float
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: int
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        x: bool
            first component of the variable to modify

        x: float
            first component of the variable to modify

        x: int
            first component of the variable to modify

        y: bool
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: float
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: int
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        z: bool
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: float
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: int
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        Notes
        -----

        Sets the uniform variables inside the shader to modify the effect while the
        program is running.
        """
        pass

    @overload
    def set(self, name: str, x: float, y: float, z: float, w: float, /) -> None:
        """Sets the uniform variables inside the shader to modify the effect while the
        program is running.

        Underlying Processing method: PShader.set

        Methods
        -------

        You can use any of the following signatures:

         * set(name: str, boolvec: Sequence[bool], ncoords: int, /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], use3x3: bool, /) -> None
         * set(name: str, tex: Py5Image, /) -> None
         * set(name: str, vec: Py5Vector, /) -> None
         * set(name: str, vec: Sequence[bool], /) -> None
         * set(name: str, vec: Sequence[float], /) -> None
         * set(name: str, vec: Sequence[float], ncoords: int, /) -> None
         * set(name: str, vec: Sequence[int], /) -> None
         * set(name: str, vec: Sequence[int], ncoords: int, /) -> None
         * set(name: str, x: bool, /) -> None
         * set(name: str, x: bool, y: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, w: bool, /) -> None
         * set(name: str, x: float, /) -> None
         * set(name: str, x: float, y: float, /) -> None
         * set(name: str, x: float, y: float, z: float, /) -> None
         * set(name: str, x: float, y: float, z: float, w: float, /) -> None
         * set(name: str, x: int, /) -> None
         * set(name: str, x: int, y: int, /) -> None
         * set(name: str, x: int, y: int, z: int, /) -> None
         * set(name: str, x: int, y: int, z: int, w: int, /) -> None

        Parameters
        ----------

        boolvec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        mat: npt.NDArray[np.floating]
            2D numpy array of values with shape 2x3 for 2D matrices or 4x4 for 3D matrices

        name: str
            the name of the uniform variable to modify

        ncoords: int
            number of coordinates per element, max 4

        tex: Py5Image
            sets the sampler uniform variable to read from this image texture

        use3x3: bool
            enforces the numpy array is 3 x 3

        vec: Py5Vector
            vector of values to modify all the components of an array/vector uniform variable

        vec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        vec: Sequence[float]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        vec: Sequence[int]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        w: bool
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: float
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: int
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        x: bool
            first component of the variable to modify

        x: float
            first component of the variable to modify

        x: int
            first component of the variable to modify

        y: bool
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: float
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: int
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        z: bool
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: float
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: int
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        Notes
        -----

        Sets the uniform variables inside the shader to modify the effect while the
        program is running.
        """
        pass

    @overload
    def set(self, name: str, vec: Sequence[float], /) -> None:
        """Sets the uniform variables inside the shader to modify the effect while the
        program is running.

        Underlying Processing method: PShader.set

        Methods
        -------

        You can use any of the following signatures:

         * set(name: str, boolvec: Sequence[bool], ncoords: int, /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], use3x3: bool, /) -> None
         * set(name: str, tex: Py5Image, /) -> None
         * set(name: str, vec: Py5Vector, /) -> None
         * set(name: str, vec: Sequence[bool], /) -> None
         * set(name: str, vec: Sequence[float], /) -> None
         * set(name: str, vec: Sequence[float], ncoords: int, /) -> None
         * set(name: str, vec: Sequence[int], /) -> None
         * set(name: str, vec: Sequence[int], ncoords: int, /) -> None
         * set(name: str, x: bool, /) -> None
         * set(name: str, x: bool, y: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, w: bool, /) -> None
         * set(name: str, x: float, /) -> None
         * set(name: str, x: float, y: float, /) -> None
         * set(name: str, x: float, y: float, z: float, /) -> None
         * set(name: str, x: float, y: float, z: float, w: float, /) -> None
         * set(name: str, x: int, /) -> None
         * set(name: str, x: int, y: int, /) -> None
         * set(name: str, x: int, y: int, z: int, /) -> None
         * set(name: str, x: int, y: int, z: int, w: int, /) -> None

        Parameters
        ----------

        boolvec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        mat: npt.NDArray[np.floating]
            2D numpy array of values with shape 2x3 for 2D matrices or 4x4 for 3D matrices

        name: str
            the name of the uniform variable to modify

        ncoords: int
            number of coordinates per element, max 4

        tex: Py5Image
            sets the sampler uniform variable to read from this image texture

        use3x3: bool
            enforces the numpy array is 3 x 3

        vec: Py5Vector
            vector of values to modify all the components of an array/vector uniform variable

        vec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        vec: Sequence[float]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        vec: Sequence[int]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        w: bool
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: float
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: int
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        x: bool
            first component of the variable to modify

        x: float
            first component of the variable to modify

        x: int
            first component of the variable to modify

        y: bool
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: float
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: int
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        z: bool
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: float
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: int
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        Notes
        -----

        Sets the uniform variables inside the shader to modify the effect while the
        program is running.
        """
        pass

    @overload
    def set(self, name: str, vec: Sequence[float], ncoords: int, /) -> None:
        """Sets the uniform variables inside the shader to modify the effect while the
        program is running.

        Underlying Processing method: PShader.set

        Methods
        -------

        You can use any of the following signatures:

         * set(name: str, boolvec: Sequence[bool], ncoords: int, /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], use3x3: bool, /) -> None
         * set(name: str, tex: Py5Image, /) -> None
         * set(name: str, vec: Py5Vector, /) -> None
         * set(name: str, vec: Sequence[bool], /) -> None
         * set(name: str, vec: Sequence[float], /) -> None
         * set(name: str, vec: Sequence[float], ncoords: int, /) -> None
         * set(name: str, vec: Sequence[int], /) -> None
         * set(name: str, vec: Sequence[int], ncoords: int, /) -> None
         * set(name: str, x: bool, /) -> None
         * set(name: str, x: bool, y: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, w: bool, /) -> None
         * set(name: str, x: float, /) -> None
         * set(name: str, x: float, y: float, /) -> None
         * set(name: str, x: float, y: float, z: float, /) -> None
         * set(name: str, x: float, y: float, z: float, w: float, /) -> None
         * set(name: str, x: int, /) -> None
         * set(name: str, x: int, y: int, /) -> None
         * set(name: str, x: int, y: int, z: int, /) -> None
         * set(name: str, x: int, y: int, z: int, w: int, /) -> None

        Parameters
        ----------

        boolvec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        mat: npt.NDArray[np.floating]
            2D numpy array of values with shape 2x3 for 2D matrices or 4x4 for 3D matrices

        name: str
            the name of the uniform variable to modify

        ncoords: int
            number of coordinates per element, max 4

        tex: Py5Image
            sets the sampler uniform variable to read from this image texture

        use3x3: bool
            enforces the numpy array is 3 x 3

        vec: Py5Vector
            vector of values to modify all the components of an array/vector uniform variable

        vec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        vec: Sequence[float]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        vec: Sequence[int]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        w: bool
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: float
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: int
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        x: bool
            first component of the variable to modify

        x: float
            first component of the variable to modify

        x: int
            first component of the variable to modify

        y: bool
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: float
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: int
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        z: bool
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: float
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: int
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        Notes
        -----

        Sets the uniform variables inside the shader to modify the effect while the
        program is running.
        """
        pass

    @overload
    def set(self, name: str, x: int, /) -> None:
        """Sets the uniform variables inside the shader to modify the effect while the
        program is running.

        Underlying Processing method: PShader.set

        Methods
        -------

        You can use any of the following signatures:

         * set(name: str, boolvec: Sequence[bool], ncoords: int, /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], use3x3: bool, /) -> None
         * set(name: str, tex: Py5Image, /) -> None
         * set(name: str, vec: Py5Vector, /) -> None
         * set(name: str, vec: Sequence[bool], /) -> None
         * set(name: str, vec: Sequence[float], /) -> None
         * set(name: str, vec: Sequence[float], ncoords: int, /) -> None
         * set(name: str, vec: Sequence[int], /) -> None
         * set(name: str, vec: Sequence[int], ncoords: int, /) -> None
         * set(name: str, x: bool, /) -> None
         * set(name: str, x: bool, y: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, w: bool, /) -> None
         * set(name: str, x: float, /) -> None
         * set(name: str, x: float, y: float, /) -> None
         * set(name: str, x: float, y: float, z: float, /) -> None
         * set(name: str, x: float, y: float, z: float, w: float, /) -> None
         * set(name: str, x: int, /) -> None
         * set(name: str, x: int, y: int, /) -> None
         * set(name: str, x: int, y: int, z: int, /) -> None
         * set(name: str, x: int, y: int, z: int, w: int, /) -> None

        Parameters
        ----------

        boolvec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        mat: npt.NDArray[np.floating]
            2D numpy array of values with shape 2x3 for 2D matrices or 4x4 for 3D matrices

        name: str
            the name of the uniform variable to modify

        ncoords: int
            number of coordinates per element, max 4

        tex: Py5Image
            sets the sampler uniform variable to read from this image texture

        use3x3: bool
            enforces the numpy array is 3 x 3

        vec: Py5Vector
            vector of values to modify all the components of an array/vector uniform variable

        vec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        vec: Sequence[float]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        vec: Sequence[int]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        w: bool
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: float
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: int
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        x: bool
            first component of the variable to modify

        x: float
            first component of the variable to modify

        x: int
            first component of the variable to modify

        y: bool
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: float
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: int
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        z: bool
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: float
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: int
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        Notes
        -----

        Sets the uniform variables inside the shader to modify the effect while the
        program is running.
        """
        pass

    @overload
    def set(self, name: str, x: int, y: int, /) -> None:
        """Sets the uniform variables inside the shader to modify the effect while the
        program is running.

        Underlying Processing method: PShader.set

        Methods
        -------

        You can use any of the following signatures:

         * set(name: str, boolvec: Sequence[bool], ncoords: int, /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], use3x3: bool, /) -> None
         * set(name: str, tex: Py5Image, /) -> None
         * set(name: str, vec: Py5Vector, /) -> None
         * set(name: str, vec: Sequence[bool], /) -> None
         * set(name: str, vec: Sequence[float], /) -> None
         * set(name: str, vec: Sequence[float], ncoords: int, /) -> None
         * set(name: str, vec: Sequence[int], /) -> None
         * set(name: str, vec: Sequence[int], ncoords: int, /) -> None
         * set(name: str, x: bool, /) -> None
         * set(name: str, x: bool, y: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, w: bool, /) -> None
         * set(name: str, x: float, /) -> None
         * set(name: str, x: float, y: float, /) -> None
         * set(name: str, x: float, y: float, z: float, /) -> None
         * set(name: str, x: float, y: float, z: float, w: float, /) -> None
         * set(name: str, x: int, /) -> None
         * set(name: str, x: int, y: int, /) -> None
         * set(name: str, x: int, y: int, z: int, /) -> None
         * set(name: str, x: int, y: int, z: int, w: int, /) -> None

        Parameters
        ----------

        boolvec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        mat: npt.NDArray[np.floating]
            2D numpy array of values with shape 2x3 for 2D matrices or 4x4 for 3D matrices

        name: str
            the name of the uniform variable to modify

        ncoords: int
            number of coordinates per element, max 4

        tex: Py5Image
            sets the sampler uniform variable to read from this image texture

        use3x3: bool
            enforces the numpy array is 3 x 3

        vec: Py5Vector
            vector of values to modify all the components of an array/vector uniform variable

        vec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        vec: Sequence[float]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        vec: Sequence[int]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        w: bool
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: float
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: int
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        x: bool
            first component of the variable to modify

        x: float
            first component of the variable to modify

        x: int
            first component of the variable to modify

        y: bool
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: float
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: int
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        z: bool
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: float
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: int
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        Notes
        -----

        Sets the uniform variables inside the shader to modify the effect while the
        program is running.
        """
        pass

    @overload
    def set(self, name: str, x: int, y: int, z: int, /) -> None:
        """Sets the uniform variables inside the shader to modify the effect while the
        program is running.

        Underlying Processing method: PShader.set

        Methods
        -------

        You can use any of the following signatures:

         * set(name: str, boolvec: Sequence[bool], ncoords: int, /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], use3x3: bool, /) -> None
         * set(name: str, tex: Py5Image, /) -> None
         * set(name: str, vec: Py5Vector, /) -> None
         * set(name: str, vec: Sequence[bool], /) -> None
         * set(name: str, vec: Sequence[float], /) -> None
         * set(name: str, vec: Sequence[float], ncoords: int, /) -> None
         * set(name: str, vec: Sequence[int], /) -> None
         * set(name: str, vec: Sequence[int], ncoords: int, /) -> None
         * set(name: str, x: bool, /) -> None
         * set(name: str, x: bool, y: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, w: bool, /) -> None
         * set(name: str, x: float, /) -> None
         * set(name: str, x: float, y: float, /) -> None
         * set(name: str, x: float, y: float, z: float, /) -> None
         * set(name: str, x: float, y: float, z: float, w: float, /) -> None
         * set(name: str, x: int, /) -> None
         * set(name: str, x: int, y: int, /) -> None
         * set(name: str, x: int, y: int, z: int, /) -> None
         * set(name: str, x: int, y: int, z: int, w: int, /) -> None

        Parameters
        ----------

        boolvec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        mat: npt.NDArray[np.floating]
            2D numpy array of values with shape 2x3 for 2D matrices or 4x4 for 3D matrices

        name: str
            the name of the uniform variable to modify

        ncoords: int
            number of coordinates per element, max 4

        tex: Py5Image
            sets the sampler uniform variable to read from this image texture

        use3x3: bool
            enforces the numpy array is 3 x 3

        vec: Py5Vector
            vector of values to modify all the components of an array/vector uniform variable

        vec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        vec: Sequence[float]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        vec: Sequence[int]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        w: bool
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: float
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: int
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        x: bool
            first component of the variable to modify

        x: float
            first component of the variable to modify

        x: int
            first component of the variable to modify

        y: bool
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: float
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: int
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        z: bool
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: float
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: int
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        Notes
        -----

        Sets the uniform variables inside the shader to modify the effect while the
        program is running.
        """
        pass

    @overload
    def set(self, name: str, x: int, y: int, z: int, w: int, /) -> None:
        """Sets the uniform variables inside the shader to modify the effect while the
        program is running.

        Underlying Processing method: PShader.set

        Methods
        -------

        You can use any of the following signatures:

         * set(name: str, boolvec: Sequence[bool], ncoords: int, /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], use3x3: bool, /) -> None
         * set(name: str, tex: Py5Image, /) -> None
         * set(name: str, vec: Py5Vector, /) -> None
         * set(name: str, vec: Sequence[bool], /) -> None
         * set(name: str, vec: Sequence[float], /) -> None
         * set(name: str, vec: Sequence[float], ncoords: int, /) -> None
         * set(name: str, vec: Sequence[int], /) -> None
         * set(name: str, vec: Sequence[int], ncoords: int, /) -> None
         * set(name: str, x: bool, /) -> None
         * set(name: str, x: bool, y: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, w: bool, /) -> None
         * set(name: str, x: float, /) -> None
         * set(name: str, x: float, y: float, /) -> None
         * set(name: str, x: float, y: float, z: float, /) -> None
         * set(name: str, x: float, y: float, z: float, w: float, /) -> None
         * set(name: str, x: int, /) -> None
         * set(name: str, x: int, y: int, /) -> None
         * set(name: str, x: int, y: int, z: int, /) -> None
         * set(name: str, x: int, y: int, z: int, w: int, /) -> None

        Parameters
        ----------

        boolvec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        mat: npt.NDArray[np.floating]
            2D numpy array of values with shape 2x3 for 2D matrices or 4x4 for 3D matrices

        name: str
            the name of the uniform variable to modify

        ncoords: int
            number of coordinates per element, max 4

        tex: Py5Image
            sets the sampler uniform variable to read from this image texture

        use3x3: bool
            enforces the numpy array is 3 x 3

        vec: Py5Vector
            vector of values to modify all the components of an array/vector uniform variable

        vec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        vec: Sequence[float]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        vec: Sequence[int]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        w: bool
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: float
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: int
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        x: bool
            first component of the variable to modify

        x: float
            first component of the variable to modify

        x: int
            first component of the variable to modify

        y: bool
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: float
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: int
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        z: bool
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: float
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: int
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        Notes
        -----

        Sets the uniform variables inside the shader to modify the effect while the
        program is running.
        """
        pass

    @overload
    def set(self, name: str, vec: Sequence[int], /) -> None:
        """Sets the uniform variables inside the shader to modify the effect while the
        program is running.

        Underlying Processing method: PShader.set

        Methods
        -------

        You can use any of the following signatures:

         * set(name: str, boolvec: Sequence[bool], ncoords: int, /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], use3x3: bool, /) -> None
         * set(name: str, tex: Py5Image, /) -> None
         * set(name: str, vec: Py5Vector, /) -> None
         * set(name: str, vec: Sequence[bool], /) -> None
         * set(name: str, vec: Sequence[float], /) -> None
         * set(name: str, vec: Sequence[float], ncoords: int, /) -> None
         * set(name: str, vec: Sequence[int], /) -> None
         * set(name: str, vec: Sequence[int], ncoords: int, /) -> None
         * set(name: str, x: bool, /) -> None
         * set(name: str, x: bool, y: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, w: bool, /) -> None
         * set(name: str, x: float, /) -> None
         * set(name: str, x: float, y: float, /) -> None
         * set(name: str, x: float, y: float, z: float, /) -> None
         * set(name: str, x: float, y: float, z: float, w: float, /) -> None
         * set(name: str, x: int, /) -> None
         * set(name: str, x: int, y: int, /) -> None
         * set(name: str, x: int, y: int, z: int, /) -> None
         * set(name: str, x: int, y: int, z: int, w: int, /) -> None

        Parameters
        ----------

        boolvec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        mat: npt.NDArray[np.floating]
            2D numpy array of values with shape 2x3 for 2D matrices or 4x4 for 3D matrices

        name: str
            the name of the uniform variable to modify

        ncoords: int
            number of coordinates per element, max 4

        tex: Py5Image
            sets the sampler uniform variable to read from this image texture

        use3x3: bool
            enforces the numpy array is 3 x 3

        vec: Py5Vector
            vector of values to modify all the components of an array/vector uniform variable

        vec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        vec: Sequence[float]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        vec: Sequence[int]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        w: bool
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: float
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: int
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        x: bool
            first component of the variable to modify

        x: float
            first component of the variable to modify

        x: int
            first component of the variable to modify

        y: bool
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: float
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: int
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        z: bool
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: float
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: int
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        Notes
        -----

        Sets the uniform variables inside the shader to modify the effect while the
        program is running.
        """
        pass

    @overload
    def set(self, name: str, vec: Sequence[int], ncoords: int, /) -> None:
        """Sets the uniform variables inside the shader to modify the effect while the
        program is running.

        Underlying Processing method: PShader.set

        Methods
        -------

        You can use any of the following signatures:

         * set(name: str, boolvec: Sequence[bool], ncoords: int, /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], use3x3: bool, /) -> None
         * set(name: str, tex: Py5Image, /) -> None
         * set(name: str, vec: Py5Vector, /) -> None
         * set(name: str, vec: Sequence[bool], /) -> None
         * set(name: str, vec: Sequence[float], /) -> None
         * set(name: str, vec: Sequence[float], ncoords: int, /) -> None
         * set(name: str, vec: Sequence[int], /) -> None
         * set(name: str, vec: Sequence[int], ncoords: int, /) -> None
         * set(name: str, x: bool, /) -> None
         * set(name: str, x: bool, y: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, w: bool, /) -> None
         * set(name: str, x: float, /) -> None
         * set(name: str, x: float, y: float, /) -> None
         * set(name: str, x: float, y: float, z: float, /) -> None
         * set(name: str, x: float, y: float, z: float, w: float, /) -> None
         * set(name: str, x: int, /) -> None
         * set(name: str, x: int, y: int, /) -> None
         * set(name: str, x: int, y: int, z: int, /) -> None
         * set(name: str, x: int, y: int, z: int, w: int, /) -> None

        Parameters
        ----------

        boolvec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        mat: npt.NDArray[np.floating]
            2D numpy array of values with shape 2x3 for 2D matrices or 4x4 for 3D matrices

        name: str
            the name of the uniform variable to modify

        ncoords: int
            number of coordinates per element, max 4

        tex: Py5Image
            sets the sampler uniform variable to read from this image texture

        use3x3: bool
            enforces the numpy array is 3 x 3

        vec: Py5Vector
            vector of values to modify all the components of an array/vector uniform variable

        vec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        vec: Sequence[float]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        vec: Sequence[int]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        w: bool
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: float
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: int
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        x: bool
            first component of the variable to modify

        x: float
            first component of the variable to modify

        x: int
            first component of the variable to modify

        y: bool
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: float
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: int
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        z: bool
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: float
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: int
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        Notes
        -----

        Sets the uniform variables inside the shader to modify the effect while the
        program is running.
        """
        pass

    @overload
    def set(self, name: str, tex: Py5Image, /) -> None:
        """Sets the uniform variables inside the shader to modify the effect while the
        program is running.

        Underlying Processing method: PShader.set

        Methods
        -------

        You can use any of the following signatures:

         * set(name: str, boolvec: Sequence[bool], ncoords: int, /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], use3x3: bool, /) -> None
         * set(name: str, tex: Py5Image, /) -> None
         * set(name: str, vec: Py5Vector, /) -> None
         * set(name: str, vec: Sequence[bool], /) -> None
         * set(name: str, vec: Sequence[float], /) -> None
         * set(name: str, vec: Sequence[float], ncoords: int, /) -> None
         * set(name: str, vec: Sequence[int], /) -> None
         * set(name: str, vec: Sequence[int], ncoords: int, /) -> None
         * set(name: str, x: bool, /) -> None
         * set(name: str, x: bool, y: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, w: bool, /) -> None
         * set(name: str, x: float, /) -> None
         * set(name: str, x: float, y: float, /) -> None
         * set(name: str, x: float, y: float, z: float, /) -> None
         * set(name: str, x: float, y: float, z: float, w: float, /) -> None
         * set(name: str, x: int, /) -> None
         * set(name: str, x: int, y: int, /) -> None
         * set(name: str, x: int, y: int, z: int, /) -> None
         * set(name: str, x: int, y: int, z: int, w: int, /) -> None

        Parameters
        ----------

        boolvec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        mat: npt.NDArray[np.floating]
            2D numpy array of values with shape 2x3 for 2D matrices or 4x4 for 3D matrices

        name: str
            the name of the uniform variable to modify

        ncoords: int
            number of coordinates per element, max 4

        tex: Py5Image
            sets the sampler uniform variable to read from this image texture

        use3x3: bool
            enforces the numpy array is 3 x 3

        vec: Py5Vector
            vector of values to modify all the components of an array/vector uniform variable

        vec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        vec: Sequence[float]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        vec: Sequence[int]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        w: bool
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: float
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: int
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        x: bool
            first component of the variable to modify

        x: float
            first component of the variable to modify

        x: int
            first component of the variable to modify

        y: bool
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: float
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: int
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        z: bool
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: float
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: int
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        Notes
        -----

        Sets the uniform variables inside the shader to modify the effect while the
        program is running.
        """
        pass

    @overload
    def set(self, name: str, mat: npt.NDArray[np.floating], /) -> None:
        """Sets the uniform variables inside the shader to modify the effect while the
        program is running.

        Underlying Processing method: PShader.set

        Methods
        -------

        You can use any of the following signatures:

         * set(name: str, boolvec: Sequence[bool], ncoords: int, /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], use3x3: bool, /) -> None
         * set(name: str, tex: Py5Image, /) -> None
         * set(name: str, vec: Py5Vector, /) -> None
         * set(name: str, vec: Sequence[bool], /) -> None
         * set(name: str, vec: Sequence[float], /) -> None
         * set(name: str, vec: Sequence[float], ncoords: int, /) -> None
         * set(name: str, vec: Sequence[int], /) -> None
         * set(name: str, vec: Sequence[int], ncoords: int, /) -> None
         * set(name: str, x: bool, /) -> None
         * set(name: str, x: bool, y: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, w: bool, /) -> None
         * set(name: str, x: float, /) -> None
         * set(name: str, x: float, y: float, /) -> None
         * set(name: str, x: float, y: float, z: float, /) -> None
         * set(name: str, x: float, y: float, z: float, w: float, /) -> None
         * set(name: str, x: int, /) -> None
         * set(name: str, x: int, y: int, /) -> None
         * set(name: str, x: int, y: int, z: int, /) -> None
         * set(name: str, x: int, y: int, z: int, w: int, /) -> None

        Parameters
        ----------

        boolvec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        mat: npt.NDArray[np.floating]
            2D numpy array of values with shape 2x3 for 2D matrices or 4x4 for 3D matrices

        name: str
            the name of the uniform variable to modify

        ncoords: int
            number of coordinates per element, max 4

        tex: Py5Image
            sets the sampler uniform variable to read from this image texture

        use3x3: bool
            enforces the numpy array is 3 x 3

        vec: Py5Vector
            vector of values to modify all the components of an array/vector uniform variable

        vec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        vec: Sequence[float]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        vec: Sequence[int]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        w: bool
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: float
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: int
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        x: bool
            first component of the variable to modify

        x: float
            first component of the variable to modify

        x: int
            first component of the variable to modify

        y: bool
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: float
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: int
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        z: bool
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: float
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: int
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        Notes
        -----

        Sets the uniform variables inside the shader to modify the effect while the
        program is running.
        """
        pass

    @overload
    def set(self, name: str, mat: npt.NDArray[np.floating], use3x3: bool, /) -> None:
        """Sets the uniform variables inside the shader to modify the effect while the
        program is running.

        Underlying Processing method: PShader.set

        Methods
        -------

        You can use any of the following signatures:

         * set(name: str, boolvec: Sequence[bool], ncoords: int, /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], use3x3: bool, /) -> None
         * set(name: str, tex: Py5Image, /) -> None
         * set(name: str, vec: Py5Vector, /) -> None
         * set(name: str, vec: Sequence[bool], /) -> None
         * set(name: str, vec: Sequence[float], /) -> None
         * set(name: str, vec: Sequence[float], ncoords: int, /) -> None
         * set(name: str, vec: Sequence[int], /) -> None
         * set(name: str, vec: Sequence[int], ncoords: int, /) -> None
         * set(name: str, x: bool, /) -> None
         * set(name: str, x: bool, y: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, w: bool, /) -> None
         * set(name: str, x: float, /) -> None
         * set(name: str, x: float, y: float, /) -> None
         * set(name: str, x: float, y: float, z: float, /) -> None
         * set(name: str, x: float, y: float, z: float, w: float, /) -> None
         * set(name: str, x: int, /) -> None
         * set(name: str, x: int, y: int, /) -> None
         * set(name: str, x: int, y: int, z: int, /) -> None
         * set(name: str, x: int, y: int, z: int, w: int, /) -> None

        Parameters
        ----------

        boolvec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        mat: npt.NDArray[np.floating]
            2D numpy array of values with shape 2x3 for 2D matrices or 4x4 for 3D matrices

        name: str
            the name of the uniform variable to modify

        ncoords: int
            number of coordinates per element, max 4

        tex: Py5Image
            sets the sampler uniform variable to read from this image texture

        use3x3: bool
            enforces the numpy array is 3 x 3

        vec: Py5Vector
            vector of values to modify all the components of an array/vector uniform variable

        vec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        vec: Sequence[float]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        vec: Sequence[int]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        w: bool
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: float
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: int
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        x: bool
            first component of the variable to modify

        x: float
            first component of the variable to modify

        x: int
            first component of the variable to modify

        y: bool
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: float
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: int
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        z: bool
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: float
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: int
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        Notes
        -----

        Sets the uniform variables inside the shader to modify the effect while the
        program is running.
        """
        pass

    @overload
    def set(self, name: str, vec: Py5Vector, /) -> None:
        """Sets the uniform variables inside the shader to modify the effect while the
        program is running.

        Underlying Processing method: PShader.set

        Methods
        -------

        You can use any of the following signatures:

         * set(name: str, boolvec: Sequence[bool], ncoords: int, /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], use3x3: bool, /) -> None
         * set(name: str, tex: Py5Image, /) -> None
         * set(name: str, vec: Py5Vector, /) -> None
         * set(name: str, vec: Sequence[bool], /) -> None
         * set(name: str, vec: Sequence[float], /) -> None
         * set(name: str, vec: Sequence[float], ncoords: int, /) -> None
         * set(name: str, vec: Sequence[int], /) -> None
         * set(name: str, vec: Sequence[int], ncoords: int, /) -> None
         * set(name: str, x: bool, /) -> None
         * set(name: str, x: bool, y: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, w: bool, /) -> None
         * set(name: str, x: float, /) -> None
         * set(name: str, x: float, y: float, /) -> None
         * set(name: str, x: float, y: float, z: float, /) -> None
         * set(name: str, x: float, y: float, z: float, w: float, /) -> None
         * set(name: str, x: int, /) -> None
         * set(name: str, x: int, y: int, /) -> None
         * set(name: str, x: int, y: int, z: int, /) -> None
         * set(name: str, x: int, y: int, z: int, w: int, /) -> None

        Parameters
        ----------

        boolvec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        mat: npt.NDArray[np.floating]
            2D numpy array of values with shape 2x3 for 2D matrices or 4x4 for 3D matrices

        name: str
            the name of the uniform variable to modify

        ncoords: int
            number of coordinates per element, max 4

        tex: Py5Image
            sets the sampler uniform variable to read from this image texture

        use3x3: bool
            enforces the numpy array is 3 x 3

        vec: Py5Vector
            vector of values to modify all the components of an array/vector uniform variable

        vec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        vec: Sequence[float]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        vec: Sequence[int]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        w: bool
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: float
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: int
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        x: bool
            first component of the variable to modify

        x: float
            first component of the variable to modify

        x: int
            first component of the variable to modify

        y: bool
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: float
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: int
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        z: bool
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: float
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: int
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        Notes
        -----

        Sets the uniform variables inside the shader to modify the effect while the
        program is running.
        """
        pass

    @_py5shader_set_wrapper
    def set(self, *args):
        """Sets the uniform variables inside the shader to modify the effect while the
        program is running.

        Underlying Processing method: PShader.set

        Methods
        -------

        You can use any of the following signatures:

         * set(name: str, boolvec: Sequence[bool], ncoords: int, /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], /) -> None
         * set(name: str, mat: npt.NDArray[np.floating], use3x3: bool, /) -> None
         * set(name: str, tex: Py5Image, /) -> None
         * set(name: str, vec: Py5Vector, /) -> None
         * set(name: str, vec: Sequence[bool], /) -> None
         * set(name: str, vec: Sequence[float], /) -> None
         * set(name: str, vec: Sequence[float], ncoords: int, /) -> None
         * set(name: str, vec: Sequence[int], /) -> None
         * set(name: str, vec: Sequence[int], ncoords: int, /) -> None
         * set(name: str, x: bool, /) -> None
         * set(name: str, x: bool, y: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, /) -> None
         * set(name: str, x: bool, y: bool, z: bool, w: bool, /) -> None
         * set(name: str, x: float, /) -> None
         * set(name: str, x: float, y: float, /) -> None
         * set(name: str, x: float, y: float, z: float, /) -> None
         * set(name: str, x: float, y: float, z: float, w: float, /) -> None
         * set(name: str, x: int, /) -> None
         * set(name: str, x: int, y: int, /) -> None
         * set(name: str, x: int, y: int, z: int, /) -> None
         * set(name: str, x: int, y: int, z: int, w: int, /) -> None

        Parameters
        ----------

        boolvec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        mat: npt.NDArray[np.floating]
            2D numpy array of values with shape 2x3 for 2D matrices or 4x4 for 3D matrices

        name: str
            the name of the uniform variable to modify

        ncoords: int
            number of coordinates per element, max 4

        tex: Py5Image
            sets the sampler uniform variable to read from this image texture

        use3x3: bool
            enforces the numpy array is 3 x 3

        vec: Py5Vector
            vector of values to modify all the components of an array/vector uniform variable

        vec: Sequence[bool]
            modifies all the components of an array/vector uniform variable

        vec: Sequence[float]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        vec: Sequence[int]
            1D numpy array of values to modify all the components of an array/vector uniform variable

        w: bool
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: float
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        w: int
            fourth component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[4], vec4)

        x: bool
            first component of the variable to modify

        x: float
            first component of the variable to modify

        x: int
            first component of the variable to modify

        y: bool
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: float
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        y: int
            second component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[2], vec2)

        z: bool
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: float
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        z: int
            third component of the variable to modify. The variable has to be declared with an array/vector type in the shader (i.e.: int[3], vec3)

        Notes
        -----

        Sets the uniform variables inside the shader to modify the effect while the
        program is running.
        """
        return self._instance.set(*args)
