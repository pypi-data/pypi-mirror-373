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
import inspect
import os
import platform
import sys
import time
import types
import uuid
import warnings
from io import BytesIO
from pathlib import Path
from typing import Any, Callable, Sequence, Union, overload  # noqa

import jpype
import numpy as np
import numpy.typing as npt
import py5_tools
from jpype.types import JArray, JClass, JException, JInt  # noqa
from py5_tools.printstreams import _DefaultPrintlnStream, _DisplayPubPrintlnStream

from . import image_conversion, reference, shape_conversion, spelling
from .base import Py5Base
from .bridge import Py5Bridge, _extract_py5_user_function_data
from .color import Py5Color  # noqa
from .decorators import (
    _context_wrapper,
    _convert_hex_color,
    _hex_converter,
    _return_color,
    _text_fix_str,
)
from .font import Py5Font, _load_py5font, _return_list_str, _return_py5font  # noqa
from .graphics import Py5Graphics, _return_py5graphics  # noqa
from .image import Py5Image, _return_py5image  # noqa
from .keyevent import Py5KeyEvent, _convert_jchar_to_chr, _convert_jint_to_int  # noqa
from .mixins import DataMixin, MathMixin, PixelMixin, PrintlnStream, ThreadsMixin
from .mixins.threads import Py5Promise  # noqa
from .mouseevent import Py5MouseEvent  # noqa
from .pmath import _get_matrix_wrapper  # noqa
from .shader import Py5Shader, _load_py5shader, _return_py5shader  # noqa
from .shape import Py5Shape, _load_py5shape, _return_py5shape  # noqa
from .surface import Py5Surface, _return_py5surface  # noqa
from .utilities import Py5Utilities

try:
    import matplotlib as mpl
    import matplotlib.colors as mcolors
    from matplotlib.colors import Colormap
except:
    mpl = None
    mcolors = None
    Colormap = "matplotlib.colors.Colormap"


_Sketch = jpype.JClass("py5.core.Sketch")
_SketchBase = jpype.JClass("py5.core.SketchBase")

_PY5_LAST_WINDOW_X = None
_PY5_LAST_WINDOW_Y = None


# def _deprecated_g(f):
#     @functools.wraps(f)
#     def decorated(self_, *args):
#         warnings.warn(
#             "Accessing the primary Py5Graphics object with `g` is deprecated. Please use `get_graphics()` instead.",
#             category=DeprecationWarning,
#             stacklevel=3 if py5_tools.imported.get_imported_mode() else 4,
#         )
#         return f(self_, *args)

#     return decorated


def _auto_convert_to_py5image(argnum):
    def _decorator(f):
        @functools.wraps(f)
        def decorated(self_, *args):
            if len(args) > argnum:
                args = list(args)
                img = args[argnum]
                if isinstance(img, image_conversion.NumpyImageArray):
                    args[argnum] = self_.create_image_from_numpy(img.array, img.bands)
                elif not isinstance(
                    img, (Py5Image, Py5Graphics)
                ) and image_conversion._convertable(img):
                    args[argnum] = self_.convert_image(img)
            return f(self_, *args)

        return decorated

    return _decorator


def _auto_convert_to_py5shape(f):
    @functools.wraps(f)
    def decorated(self_, *args):
        if len(args) >= 1:
            args = list(args)
            shape = args[0]
            if not isinstance(shape, Py5Shape) and shape_conversion._convertable(shape):
                args[0] = self_.convert_shape(shape)
        return f(self_, *args)

    return decorated


def _generator_to_list(f):
    @functools.wraps(f)
    def decorated(self_, *args):
        if isinstance(args[0], types.GeneratorType):
            args = list(args[0]), *args[1:]
        return f(self_, *args)

    return decorated


def _settings_only(name):
    def _decorator(f):
        @functools.wraps(f)
        def decorated(self_, *args):
            if self_._py5_bridge.current_running_method == "settings":
                return f(self_, *args)
            else:
                raise RuntimeError(
                    "Cannot call the "
                    + name
                    + "() method here. Either move it to a settings() function or move it to closer to the start of setup()."
                )

        return decorated

    return _decorator


class Sketch(MathMixin, DataMixin, ThreadsMixin, PixelMixin, PrintlnStream, Py5Base):
    """Core py5 class for leveraging py5's functionality.

    Underlying Processing class: PApplet.PApplet

    Notes
    -----

    Core py5 class for leveraging py5's functionality. This is analogous to the
    PApplet class in Processing. Launch the Sketch with the `run_sketch()` method.

    The core functions to be implemented by the py5 coder are `setup` and `draw`.
    The first will be run once at Sketch initialization and the second will be run
    in an animation thread, once per frame. The following event functions are also
    supported:

    * `exiting`
    * `key_pressed`
    * `key_released`
    * `key_typed`
    * `mouse_clicked`
    * `mouse_dragged`
    * `mouse_entered`
    * `mouse_exited`
    * `mouse_moved`
    * `mouse_pressed`
    * `mouse_released`
    * `mouse_wheel`
    * `movie_event`
    * `predraw_update`
    * `post_draw`
    * `pre_draw`

    When coding in class mode, all of the above functions should be instance
    methods. When coding in module mode or imported mode, the above functions should
    be stand-alone functions available in the local namespace in which
    `run_sketch()` was called.

    For more information, look at the online "User Functions" documentation."""

    _py5_object_cache = set()
    _cls = _Sketch

    def __new__(cls, *args, **kwargs):
        _instance = kwargs.get("_instance")

        # remove dead or malformed Sketch instances from the object cache
        cls._py5_object_cache = set(
            s
            for s in cls._py5_object_cache
            if hasattr(s, "_instance") and not s.is_dead
        )
        if _instance:
            for s in cls._py5_object_cache:
                if _instance == s._instance:
                    return s
            else:
                raise RuntimeError(
                    "Failed to locate cached Sketch class for provided py5.core.Sketch instance"
                )
        else:
            s = object.__new__(cls)
            cls._py5_object_cache.add(s)
            return s

    def __init__(self, *args, **kwargs):
        _instance = kwargs.get("_instance")
        jclassname = kwargs.get("jclassname")
        jclass_params = kwargs.get("jclass_params", ())

        if _instance:
            if _instance == getattr(self, "_instance", None):
                # this is a cached Sketch object, don't re-run __init__()
                return
            else:
                raise RuntimeError(
                    "Unexpected Situation: Passed py5.core.Sketch instance does not match existing py5.core.Sketch instance. What is going on?"
                )

        Sketch._cls = JClass(jclassname) if jclassname else _Sketch
        instance = Sketch._cls(*jclass_params)
        if not isinstance(instance, _SketchBase):
            raise RuntimeError("Java instance must inherit from py5.core.SketchBase")

        super().__init__(instance=instance)
        self._methods_to_profile = []
        self._pre_hooks_to_add = []
        self._post_hooks_to_add = []
        # must always keep the _py5_bridge reference count from hitting zero.
        # otherwise, it will be garbage collected and lead to segmentation faults!
        self._py5_bridge = None
        # TODO: shouldn't this be like the base_path variable in __init__.py?
        iconPath = Path(__file__).parent.parent / "py5_tools/resources/logo-64x64.png"
        if iconPath.exists() and hasattr(self._instance, "setPy5IconPath"):
            self._instance.setPy5IconPath(str(iconPath))
        elif hasattr(sys, "_MEIPASS"):
            warnings.warn(
                "py5 logo image cannot be found. You are running this Sketch with pyinstaller and the image is missing from the packaging. I'm going to nag you about this until you fix it.",
                stacklevel=3,
            )
        Sketch._cls.setJOGLProperties(str(Path(__file__).parent))
        self.utils = Py5Utilities(self)
        self._sync_draw = None

        self._py5_convert_image_cache = dict()
        self._py5_convert_shape_cache = dict()
        self._cmap = None
        self._cmap_range = 0
        self._cmap_alpha_range = 0

    def __str__(self):
        return (
            f"Sketch(width="
            + str(self._get_width())
            + ", height="
            + str(self._get_height())
            + ", renderer="
            + str(self._instance.getRendererName())
            + ")"
        )

    def __repr__(self):
        return self.__str__()

    def __getattr__(self, name):
        raise AttributeError(spelling.error_msg("Sketch", name, self))

    def run_sketch(
        self,
        block: bool = None,
        *,
        py5_options: list = None,
        sketch_args: list = None,
        _osx_alt_run_method: bool = True,
    ) -> None:
        """Run the Sketch.

        Parameters
        ----------

        block: bool = None
            method returns immediately (False) or blocks until Sketch exits (True)

        jclass_params: tuple[Any] = ()
            parameters to pass to constructor when using py5 in processing mode

        jclassname: str = None
            canonical name of class to instantiate when using py5 in processing mode

        py5_options: list[str] = None
            command line arguments to pass to Processing as arguments

        sketch_args: list[str] = None
            command line arguments that become Sketch arguments

        sketch_functions: dict[str, Callable] = None
            sketch methods when using [module mode](content-py5-modes-module-mode)

        Notes
        -----

        Run the Sketch. Code in the `settings()`, `setup()`, and `draw()` functions will
        be used to actualize your Sketch.

        Use the `block` parameter to specify if the call to `run_sketch()` should return
        immediately (asynchronous Sketch execution) or block until the Sketch exits. If
        the `block` parameter is not specified, py5 will first attempt to determine if
        the Sketch is running in a Jupyter Notebook or an IPython shell. If it is,
        `block` will default to `False`, and `True` otherwise. However, on macOS, these
        default values are required, as py5 cannot work on macOS without them.

        A list of strings passed to `py5_options` will be passed to the Processing
        PApplet class as arguments to specify characteristics such as the window's
        location on the screen. A list of strings passed to `sketch_args` will be
        available to a running Sketch using `pargs`. See the third example for an
        example of how this can be used.

        When calling `run_sketch()` in module mode, py5 will by default search for
        functions such as `setup()`,  `draw()`, etc. in the caller's stack frame and use
        those in the Sketch. If for some reason that is not what you want or does not
        work because you are hacking py5 to do something unusual, you can use the
        `sketch_functions` parameter to pass a dictionary of the desired callable
        functions. The `sketch_functions` parameter is not available when coding py5 in
        class mode. Don't forget you can always replace the `draw()` function in a
        running Sketch using `hot_reload_draw()`.

        When programming in module mode and imported mode, py5 will inspect the
        `setup()` function and will attempt to split it into synthetic `settings()` and
        `setup()` functions if both were not created by the user and the real `setup()`
        function contains calls to `size()`, `full_screen()`, `smooth()`, `no_smooth()`,
        or `pixel_density()`. Calls to those functions must be at the very beginning of
        `setup()`, before any other Python code (except for comments). This feature
        allows the user to omit the `settings()` function, much like what can be done
        while programming in the Processing IDE. This feature is not available when
        programming in class mode.

        When running a Sketch asynchronously through Jupyter Notebook, any `print`
        statements using Python's builtin function will always appear in the output of
        the currently active cell. This will rarely be desirable, as the active cell
        will keep changing as the user executes code elsewhere in the notebook. As an
        alternative, use py5's `println()` method, which will place all text in the
        output of the cell that made the `run_sketch()` call. This will continue to be
        true if the user moves on to execute code in other Notebook cells. Use
        `set_println_stream()` to customize this behavior. All py5 error messages and
        stack traces are routed through the `println()` method. Be aware that some error
        messages and warnings generated inside the Processing Jars cannot be controlled
        in the same way, and may appear in the output of the active cell or mixed in
        with the Jupyter Kernel logs.

        The `jclassname` parameter should only be used when programming in Processing
        Mode. This value must be the canonical name of your Processing Sketch class
        (i.e. `"org.test.MySketch"`). The class must inherit from `py5.core.SketchBase`.
        To pass parameters to your Processing Sketch class constructor, use the
        `jclass_params` parameter. Read py5's online documentation to learn more about
        Processing Mode."""
        if not hasattr(self, "_instance"):
            raise RuntimeError(
                (
                    "py5 internal problem: did you create a class with an `__init__()` "
                    "method without a call to `super().__init__()`?"
                )
            )

        methods, method_param_counts = _extract_py5_user_function_data(
            dict(
                [
                    (e, getattr(self, e))
                    for e in reference.METHODS.keys()
                    if hasattr(self, e)
                ]
            )
        )

        caller_locals = inspect.stack()[1].frame.f_locals
        caller_globals = inspect.stack()[1].frame.f_globals

        self._run_sketch(
            methods,
            method_param_counts,
            block,
            py5_options=py5_options,
            sketch_args=sketch_args,
            _caller_locals=caller_locals,
            _caller_globals=caller_globals,
            _osx_alt_run_method=_osx_alt_run_method,
        )

    def _run_sketch(
        self,
        methods: dict[str, Callable],
        method_param_counts: dict[str, int],
        block: bool,
        *,
        py5_options: list[str] = None,
        sketch_args: list[str] = None,
        _caller_locals: dict[str, Any] = None,
        _caller_globals: dict[str, Any] = None,
        _osx_alt_run_method: bool = True,
    ) -> None:
        self._environ = py5_tools.environ.Environment()
        self.set_println_stream(
            _DisplayPubPrintlnStream()
            if self._environ.in_jupyter_zmq_shell
            else _DefaultPrintlnStream()
        )

        self._py5_bridge = Py5Bridge(self)
        self._py5_bridge.set_caller_locals_globals(_caller_locals, _caller_globals)
        self._py5_bridge.add_functions(methods, method_param_counts)
        self._py5_bridge.profile_functions(self._methods_to_profile)
        self._py5_bridge.add_pre_hooks(self._pre_hooks_to_add)
        self._py5_bridge.add_post_hooks(self._post_hooks_to_add)
        self._instance.buildPy5Bridge(
            self._py5_bridge,
            self._environ.in_ipython_session,
            self._environ.in_jupyter_zmq_shell,
        )

        if not py5_options:
            py5_options = []
        if not sketch_args:
            sketch_args = []
        if not any([a.startswith("--sketch-path") for a in py5_options]):
            py5_options.append("--sketch-path=" + os.getcwd())
        if (
            not any([a.startswith("--location") for a in py5_options])
            and _PY5_LAST_WINDOW_X is not None
            and _PY5_LAST_WINDOW_Y is not None
        ):
            py5_options.append(
                "--location=" + str(_PY5_LAST_WINDOW_X) + "," + str(_PY5_LAST_WINDOW_Y)
            )
        args = py5_options + [""] + sketch_args

        try:
            if _osx_alt_run_method and platform.system() == "Darwin":
                from PyObjCTools import AppHelper  # type: ignore

                def run():
                    Sketch._cls.runSketch(args, self._instance)
                    if not self._environ.in_ipython_session:
                        # need to call System.exit() in Java to stop the sketch
                        # would never get past runConsoleEventLoop() anyway
                        # because that doesn't return
                        try:
                            self._instance.allowSystemExit()
                            while not self.is_dead:
                                time.sleep(0.05)
                            if self.is_dead_from_error:
                                surface = self.get_surface()
                                while not surface.is_stopped():
                                    time.sleep(0.05)
                            AppHelper.stopEventLoop()
                        except Exception as e:
                            # exception might be thrown because the JVM gets
                            # shut down forcefully
                            pass

                if block == False and not self._environ.in_ipython_session:
                    self.println(
                        "On macOS, blocking is mandatory when Sketch is not run through Jupyter. This applies to all renderers.",
                        stderr=True,
                    )

                proxy = jpype.JProxy("java.lang.Runnable", dict(run=run))
                jpype.JClass("java.lang.Thread")(proxy).start()
                if not self._environ.in_ipython_session:
                    AppHelper.runConsoleEventLoop()
            else:
                Sketch._cls.runSketch(args, self._instance)
        except Exception as e:
            self.println(
                "Java exception thrown by Sketch.runSketch:\n" + str(e), stderr=True
            )

        if platform.system() == "Darwin" and self._environ.in_ipython_session and block:
            if (renderer := self._instance.getRendererName()) in [
                "JAVA2D",
                "P2D",
                "P3D",
                "FX2D",
            ]:
                self.println(
                    "On macOS, blocking is not allowed when Sketch using the",
                    renderer,
                    "renderer is run though Jupyter.",
                    stderr=True,
                )
                block = False

        if block or (block is None and not self._environ.in_ipython_session):
            # wait for the sketch to finish
            surface = self.get_surface()
            if surface._instance is not None:
                while not surface.is_stopped() and not hasattr(
                    self, "_shutdown_initiated"
                ):
                    time.sleep(0.25)

            # Wait no more than 1 second for any shutdown tasks to complete.
            # This will not wait for the user's `exiting` method, as it has
            # already been called. It will not wait for any threads to exit, as
            # that code calls `stop_all_threads(wait=False)` in its shutdown
            # procedure. Bottom line, this currently doesn't do very much but
            # might if a mixin had more complex shutdown steps.
            time_waited = 0
            while time_waited < 1.0 and not hasattr(self, "_shutdown_complete"):
                pause = 0.01
                time_waited += pause
                time.sleep(pause)

    def _shutdown(self):
        global _PY5_LAST_WINDOW_X
        global _PY5_LAST_WINDOW_Y
        if (
            hasattr(self._instance, "lastWindowX")
            and hasattr(self._instance, "lastWindowY")
            and self._instance.lastWindowX is not None
            and self._instance.lastWindowY is not None
        ):
            _PY5_LAST_WINDOW_X = int(self._instance.lastWindowX)
            _PY5_LAST_WINDOW_Y = int(self._instance.lastWindowY)
        super()._shutdown()

    def _terminate_sketch(self):
        self._instance.noLoop()
        self._shutdown_initiated = True
        self._shutdown()

    def _add_pre_hook(self, method_name, hook_name, function):
        if self._py5_bridge is None:
            self._pre_hooks_to_add.append((method_name, hook_name, function))
        else:
            self._py5_bridge.add_pre_hook(method_name, hook_name, function)

    def _remove_pre_hook(self, method_name, hook_name):
        if self._py5_bridge is None:
            self._pre_hooks_to_add = [
                x
                for x in self._pre_hooks_to_add
                if x[0] != method_name and x[1] != hook_name
            ]
        else:
            self._py5_bridge.remove_pre_hook(method_name, hook_name)

    def _add_post_hook(self, method_name, hook_name, function):
        if self._py5_bridge is None:
            self._post_hooks_to_add.append((method_name, hook_name, function))
        else:
            self._py5_bridge.add_post_hook(method_name, hook_name, function)

    def _remove_post_hook(self, method_name, hook_name):
        if self._py5_bridge is None:
            self._post_hooks_to_add = [
                x
                for x in self._post_hooks_to_add
                if x[0] != method_name and x[1] != hook_name
            ]
        else:
            self._py5_bridge.remove_post_hook(method_name, hook_name)

    # *** BEGIN METHODS ***

    PI = np.pi  # CODEBUILDER INCLUDE
    HALF_PI = np.pi / 2  # CODEBUILDER INCLUDE
    THIRD_PI = np.pi / 3  # CODEBUILDER INCLUDE
    QUARTER_PI = np.pi / 4  # CODEBUILDER INCLUDE
    TWO_PI = 2 * np.pi  # CODEBUILDER INCLUDE
    TAU = 2 * np.pi  # CODEBUILDER INCLUDE
    RAD_TO_DEG = 180 / np.pi  # CODEBUILDER INCLUDE
    DEG_TO_RAD = np.pi / 180  # CODEBUILDER INCLUDE
    CMAP = 6  # CODEBUILDER INCLUDE

    @overload
    def sketch_path(self) -> Path:
        """The Sketch's current path.

        Underlying Processing method: PApplet.sketchPath

        Methods
        -------

        You can use any of the following signatures:

         * sketch_path() -> Path
         * sketch_path(where: str, /) -> Path

        Parameters
        ----------

        where: str
            subdirectories relative to the sketch path

        Notes
        -----

        The Sketch's current path. If the `where` parameter is used, the result will be
        a subdirectory of the current path.

        Result will be relative to Python's current working directory (`os.getcwd()`)
        unless it was specifically set to something else with the `run_sketch()` call by
        including a `--sketch-path` argument in the `py5_options` parameters."""
        pass

    @overload
    def sketch_path(self, where: str, /) -> Path:
        """The Sketch's current path.

        Underlying Processing method: PApplet.sketchPath

        Methods
        -------

        You can use any of the following signatures:

         * sketch_path() -> Path
         * sketch_path(where: str, /) -> Path

        Parameters
        ----------

        where: str
            subdirectories relative to the sketch path

        Notes
        -----

        The Sketch's current path. If the `where` parameter is used, the result will be
        a subdirectory of the current path.

        Result will be relative to Python's current working directory (`os.getcwd()`)
        unless it was specifically set to something else with the `run_sketch()` call by
        including a `--sketch-path` argument in the `py5_options` parameters."""
        pass

    def sketch_path(self, *args) -> Path:
        """The Sketch's current path.

        Underlying Processing method: PApplet.sketchPath

        Methods
        -------

        You can use any of the following signatures:

         * sketch_path() -> Path
         * sketch_path(where: str, /) -> Path

        Parameters
        ----------

        where: str
            subdirectories relative to the sketch path

        Notes
        -----

        The Sketch's current path. If the `where` parameter is used, the result will be
        a subdirectory of the current path.

        Result will be relative to Python's current working directory (`os.getcwd()`)
        unless it was specifically set to something else with the `run_sketch()` call by
        including a `--sketch-path` argument in the `py5_options` parameters."""
        if not self.is_running:
            msg = (
                "Calling method sketch_path() when Sketch is not running. "
                + "The returned value will not be correct on all platforms. Consider "
                + "calling this after setup() or perhaps using the Python standard "
                + "library methods os.getcwd() or pathlib.Path.cwd()."
            )
            warnings.warn(msg)
        if len(args) <= 1:
            return Path(str(self._instance.sketchPath(*args)))
        else:
            # this exception will be replaced with a more informative one by the custom exception handler
            raise TypeError("The parameters are invalid for method sketch_path()")

    def _get_is_ready(self) -> bool:
        """Boolean value reflecting if the Sketch is in the ready state.

        Notes
        -----

        Boolean value reflecting if the Sketch is in the ready state. This will be
        `True` before `run_sketch()` is called. It will be `False` while the Sketch is
        running and after it has exited."""
        surface = self.get_surface()
        # if there is no surface yet, the sketch can be run.
        return surface._instance is None

    is_ready: bool = property(
        fget=_get_is_ready,
        doc="""Boolean value reflecting if the Sketch is in the ready state.

        Notes
        -----

        Boolean value reflecting if the Sketch is in the ready state. This will be
        `True` before `run_sketch()` is called. It will be `False` while the Sketch is
        running and after it has exited.""",
    )

    def _get_is_running(self) -> bool:
        """Boolean value reflecting if the Sketch is in the running state.

        Notes
        -----

        Boolean value reflecting if the Sketch is in the running state. This will be
        `False` before `run_sketch()` is called and `True` after. It will be `False`
        again after the Sketch has exited."""
        surface = self.get_surface()
        if surface._instance is None:
            # Sketch has not been run yet
            return False
        else:
            return not surface.is_stopped() and not hasattr(self, "_shutdown_initiated")

    is_running: bool = property(
        fget=_get_is_running,
        doc="""Boolean value reflecting if the Sketch is in the running state.

        Notes
        -----

        Boolean value reflecting if the Sketch is in the running state. This will be
        `False` before `run_sketch()` is called and `True` after. It will be `False`
        again after the Sketch has exited.""",
    )

    def _get_is_dead(self) -> bool:
        """Boolean value reflecting if the Sketch has been run and has now stopped.

        Notes
        -----

        Boolean value reflecting if the Sketch has been run and has now stopped. This
        will be `True` after calling `exit_sketch()` or if the Sketch throws an error
        and stops. This will also be `True` after calling `Py5Surface`'s
        `Py5Surface.stop_thread()` method. Once a Sketch reaches the "dead" state, it
        cannot be rerun.

        After an error or a call to `Py5Surface.stop_thread()`, the Sketch window will
        still be open. Call `exit_sketch()` to close the window."""
        surface = self.get_surface()
        if surface._instance is None:
            # Sketch has not been run yet
            return False
        return surface.is_stopped() or hasattr(self, "_shutdown_initiated")

    is_dead: bool = property(
        fget=_get_is_dead,
        doc="""Boolean value reflecting if the Sketch has been run and has now stopped.

        Notes
        -----

        Boolean value reflecting if the Sketch has been run and has now stopped. This
        will be `True` after calling `exit_sketch()` or if the Sketch throws an error
        and stops. This will also be `True` after calling `Py5Surface`'s
        `Py5Surface.stop_thread()` method. Once a Sketch reaches the "dead" state, it
        cannot be rerun.

        After an error or a call to `Py5Surface.stop_thread()`, the Sketch window will
        still be open. Call `exit_sketch()` to close the window.""",
    )

    def _get_is_dead_from_error(self) -> bool:
        """Boolean value reflecting if the Sketch has been run and has now stopped because
        of an error.

        Notes
        -----

        Boolean value reflecting if the Sketch has been run and has now stopped because
        of an error. This will be `True` only when `is_dead` is `True` and the Sketch
        stopped because an exception was thrown."""
        return self.is_dead and not self._instance.getSuccess()

    is_dead_from_error: bool = property(
        fget=_get_is_dead_from_error,
        doc="""Boolean value reflecting if the Sketch has been run and has now stopped because
        of an error.

        Notes
        -----

        Boolean value reflecting if the Sketch has been run and has now stopped because
        of an error. This will be `True` only when `is_dead` is `True` and the Sketch
        stopped because an exception was thrown.""",
    )

    def _get_is_mouse_pressed(self) -> bool:
        """The `is_mouse_pressed` variable stores whether or not a mouse button is
        currently being pressed.

        Notes
        -----

        The `is_mouse_pressed` variable stores whether or not a mouse button is
        currently being pressed. The value is `True` when `any` mouse button is pressed,
        and `False` if no button is pressed. The `mouse_button` variable (see the
        related reference entry) can be used to determine which button has been pressed.
        """
        return self._instance.isMousePressed()

    is_mouse_pressed: bool = property(
        fget=_get_is_mouse_pressed,
        doc="""The `is_mouse_pressed` variable stores whether or not a mouse button is
        currently being pressed.

        Notes
        -----

        The `is_mouse_pressed` variable stores whether or not a mouse button is
        currently being pressed. The value is `True` when `any` mouse button is pressed,
        and `False` if no button is pressed. The `mouse_button` variable (see the
        related reference entry) can be used to determine which button has been pressed.""",
    )

    def _get_is_key_pressed(self) -> bool:
        """The `is_key_pressed` variable stores whether or not a keyboard button is
        currently being pressed.

        Notes
        -----

        The `is_key_pressed` variable stores whether or not a keyboard button is
        currently being pressed. The value is true when `any` keyboard button is
        pressed, and false if no button is pressed. The `key` variable and `key_code`
        variables (see the related reference entries) can be used to determine which
        button has been pressed."""
        return self._instance.isKeyPressed()

    is_key_pressed: bool = property(
        fget=_get_is_key_pressed,
        doc="""The `is_key_pressed` variable stores whether or not a keyboard button is
        currently being pressed.

        Notes
        -----

        The `is_key_pressed` variable stores whether or not a keyboard button is
        currently being pressed. The value is true when `any` keyboard button is
        pressed, and false if no button is pressed. The `key` variable and `key_code`
        variables (see the related reference entries) can be used to determine which
        button has been pressed.""",
    )

    def hot_reload_draw(self, draw: Callable) -> None:
        """Perform a hot reload of the Sketch's draw function.

        Parameters
        ----------

        draw: Callable
            function to replace existing draw function

        Notes
        -----

        Perform a hot reload of the Sketch's draw function. This method allows you to
        replace a running Sketch's draw function with a different one."""
        methods, method_param_counts = _extract_py5_user_function_data(dict(draw=draw))
        if "draw" in methods:
            self._py5_bridge.add_functions(methods, method_param_counts)
        else:
            self.println("The new draw() function must take no parameters")

    def profile_functions(self, function_names: list[str]) -> None:
        """Profile the execution times of the Sketch's functions with a line profiler.

        Parameters
        ----------

        function_names: list[str]
            names of py5 functions to be profiled

        Notes
        -----

        Profile the execution times of the Sketch's functions with a line profiler. This
        uses the Python library lineprofiler to provide line by line performance data.
        The collected stats will include the number of times each line of code was
        executed (Hits) and the total amount of time spent on each line (Time). This
        information can be used to target the performance tuning efforts for a slow
        Sketch.

        This method can be called before or after `run_sketch()`. You are welcome to
        profile multiple functions, but don't initiate profiling on the same function
        multiple times. To profile functions that do not belong to the Sketch, including
        any functions called from `launch_thread()` and the like, use lineprofiler
        directly and not through py5's performance tools.

        To profile just the draw function, you can also use `profile_draw()`. To see the
        results, use `print_line_profiler_stats()`."""
        if self._py5_bridge is None:
            self._methods_to_profile.extend(function_names)
        else:
            self._py5_bridge.profile_functions(function_names)

    def profile_draw(self) -> None:
        """Profile the execution times of the draw function with a line profiler.

        Notes
        -----

        Profile the execution times of the draw function with a line profiler. This uses
        the Python library lineprofiler to provide line by line performance data. The
        collected stats will include the number of times each line of code was executed
        (Hits) and the total amount of time spent on each line (Time). This information
        can be used to target the performance tuning efforts for a slow Sketch.

        This method can be called before or after `run_sketch()`. You are welcome to
        profile multiple functions, but don't initiate profiling on the same function
        multiple times. To profile functions that do not belong to the Sketch, including
        any functions called from `launch_thread()` and the like, use lineprofiler
        directly and not through py5's performance tools.

        To profile a other functions besides draw, use `profile_functions()`. To see the
        results, use `print_line_profiler_stats()`."""
        self.profile_functions(["draw"])

    def print_line_profiler_stats(self) -> None:
        """Print the line profiler stats initiated with `profile_draw()` or
        `profile_functions()`.

        Notes
        -----

        Print the line profiler stats initiated with `profile_draw()` or
        `profile_functions()`. The collected stats will include the number of times each
        line of code was executed (Hits) and the total amount of time spent on each line
        (Time). This information can be used to target the performance tuning efforts
        for a slow Sketch.

        This method can be called multiple times on a running Sketch."""
        self._py5_bridge.dump_stats()

    def _insert_frame(self, what, num=None):
        """Utility function to insert a number into a filename.

        This is just like PApplet's insertFrame method except it allows you to
        override the frameCount with something else.
        """
        if num is None:
            num = self._instance.frameCount
        first = what.find("#")
        last = len(what) - what[::-1].find("#")
        if first != -1 and last - first > 1:
            count = last - first
            numstr = str(num)
            numprefix = "0" * (count - len(numstr))
            what = what[:first] + numprefix + numstr + what[last:]
        return what

    def save_frame(
        self,
        filename: Union[str, Path, BytesIO],
        *,
        format: str = None,
        drop_alpha: bool = True,
        use_thread: bool = False,
        **params,
    ) -> None:
        """Save the current frame as an image.

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

        Save the current frame as an image. This method uses the Python library Pillow
        to write the image, so it can save images in any format that that library
        supports.

        Use the `drop_alpha` parameter to drop the alpha channel from the image. This
        defaults to `True`. Some image formats such as JPG do not support alpha
        channels, and Pillow will throw an error if you try to save an image with the
        alpha channel in that format.

        The `use_thread` parameter will save the image in a separate Python thread. This
        improves performance by returning before the image has actually been written to
        the file.

        This method is the same as `save()` except it will replace a sequence of `#`
        symbols in the `filename` parameter with the frame number. This is useful when
        saving an image sequence for a running animation. The first frame number will be
        1."""
        if not isinstance(filename, BytesIO):
            filename = self._insert_frame(str(filename))
        self.save(
            filename,
            format=format,
            drop_alpha=drop_alpha,
            use_thread=use_thread,
            **params,
        )

    def select_folder(
        self, prompt: str, callback: Callable, default_folder: str = None
    ) -> None:
        """Opens a file chooser dialog to select a folder.

        Underlying Processing method: Sketch.selectFolder

        Parameters
        ----------

        callback: Callable
            callback function after selection is made

        default_folder: str = None
            default folder

        prompt: str
            text prompt for select dialog box

        Notes
        -----

        Opens a file chooser dialog to select a folder. After the selection is made, the
        selection will be passed to the `callback` function. If the dialog is closed or
        canceled, `None` will be sent to the function, so that the program is not
        waiting for additional input. The callback is necessary because of how threading
        works.

        This method has some platform specific quirks. On macOS, this does not work when
        the Sketch is run through a Jupyter notebook. On Windows, Sketches using the
        OpenGL renderers (`P2D` or `P3D`) will be minimized while the select dialog box
        is open. This method only uses native dialog boxes on macOS."""
        if (
            not isinstance(prompt, str)
            or not callable(callback)
            or (default_folder is not None and not isinstance(default_folder, str))
        ):
            raise TypeError(
                "This method's signature is select_folder(prompt: str, callback: Callable, default_folder: str)"
            )
        self._generic_select(
            self._instance.py5SelectFolder,
            "select_folder",
            prompt,
            callback,
            default_folder,
        )

    def select_input(
        self, prompt: str, callback: Callable, default_file: str = None
    ) -> None:
        """Opens a file chooser dialog to select a folder.

        Underlying Processing method: Sketch.selectFolder

        Parameters
        ----------

        callback: Callable
            callback function after selection is made

        default_folder: str = None
            default folder

        prompt: str
            text prompt for select dialog box

        Notes
        -----

        Opens a file chooser dialog to select a folder. After the selection is made, the
        selection will be passed to the `callback` function. If the dialog is closed or
        canceled, `None` will be sent to the function, so that the program is not
        waiting for additional input. The callback is necessary because of how threading
        works.

        This method has some platform specific quirks. On macOS, this does not work when
        the Sketch is run through a Jupyter notebook. On Windows, Sketches using the
        OpenGL renderers (`P2D` or `P3D`) will be minimized while the select dialog box
        is open. This method only uses native dialog boxes on macOS."""
        if (
            not isinstance(prompt, str)
            or not callable(callback)
            or (default_file is not None and not isinstance(default_file, str))
        ):
            raise TypeError(
                "This method's signature is select_input(prompt: str, callback: Callable, default_file: str)"
            )
        self._generic_select(
            self._instance.py5SelectInput,
            "select_input",
            prompt,
            callback,
            default_file,
        )

    def select_output(
        self, prompt: str, callback: Callable, default_file: str = None
    ) -> None:
        """Opens a file chooser dialog to select a folder.

        Underlying Processing method: Sketch.selectFolder

        Parameters
        ----------

        callback: Callable
            callback function after selection is made

        default_folder: str = None
            default folder

        prompt: str
            text prompt for select dialog box

        Notes
        -----

        Opens a file chooser dialog to select a folder. After the selection is made, the
        selection will be passed to the `callback` function. If the dialog is closed or
        canceled, `None` will be sent to the function, so that the program is not
        waiting for additional input. The callback is necessary because of how threading
        works.

        This method has some platform specific quirks. On macOS, this does not work when
        the Sketch is run through a Jupyter notebook. On Windows, Sketches using the
        OpenGL renderers (`P2D` or `P3D`) will be minimized while the select dialog box
        is open. This method only uses native dialog boxes on macOS."""
        if (
            not isinstance(prompt, str)
            or not callable(callback)
            or (default_file is not None and not isinstance(default_file, str))
        ):
            raise TypeError(
                "This method's signature is select_output(prompt: str, callback: Callable, default_file: str)"
            )
        self._generic_select(
            self._instance.py5SelectOutput,
            "select_output",
            prompt,
            callback,
            default_file,
        )

    def _generic_select(
        self,
        py5f: Callable,
        name: str,
        prompt: str,
        callback: Callable,
        default_folder: str = None,
    ) -> None:
        callback_sig = inspect.signature(callback)
        if (
            len(callback_sig.parameters) != 1
            or list(callback_sig.parameters.values())[0].kind
            == inspect.Parameter.KEYWORD_ONLY
        ):
            raise RuntimeError(
                "The callback function must have one and only one positional argument"
            )

        key = "_PY5_SELECT_CALLBACK_" + str(uuid.uuid4())

        def wrapped_callback_py5_no_prune(selection):
            return callback(selection if selection is None else Path(selection))

        py5_tools.config.register_processing_mode_key(
            key, wrapped_callback_py5_no_prune, callback_once=True
        )

        if platform.system() == "Darwin":
            if self._environ.in_ipython_session:
                raise RuntimeError(
                    "Sorry, py5's "
                    + name
                    + "() method doesn't work on macOS when the Sketch is run through Jupyter. However, there are some IPython widgets you can use instead."
                )
            else:

                def _run():
                    py5f(key, prompt, default_folder)

                proxy = jpype.JProxy("java.lang.Runnable", dict(run=_run))
                jpype.JClass("java.lang.Thread")(proxy).start()
        else:
            py5f(key, prompt, default_folder)

    def _set_sync_draw(self, sync_draw):
        self._sync_draw = sync_draw

    def _get_sync_draw(self):
        return self._sync_draw

    # *** Py5Image methods ***

    def create_image_from_numpy(
        self, array: npt.NDArray[np.uint8], bands: str = "ARGB", *, dst: Py5Image = None
    ) -> Py5Image:
        """Convert a numpy array into a Py5Image object.

        Parameters
        ----------

        array: npt.NDArray[np.uint8]
            numpy image array

        bands: str = "ARGB"
            color channels in array

        dst: Py5Image = None
            existing Py5Image object to put the image data into

        Notes
        -----

        Convert a numpy array into a Py5Image object. The numpy array must have 3
        dimensions and the array's `dtype` must be `np.uint8`. The size of `array`'s
        first and second dimensions will be the image's height and width, respectively.
        The third dimension is for the array's color channels.

        The `bands` parameter is used to interpret the `array`'s color channel dimension
        (the array's third dimension). It can be one of `'L'` (single-channel
        grayscale), `'ARGB'`, `'RGB'`, or `'RGBA'`. If there is no alpha channel,
        `array` is assumed to have no transparency. If the `bands` parameter is `'L'`,
        `array`'s third dimension is optional.

        The caller can optionally pass an existing Py5Image object to put the image data
        into using the `dst` parameter. This can have performance benefits in code that
        would otherwise continuously create new Py5Image objects. The array's width and
        height must match that of the recycled Py5Image object."""
        height, width = array.shape[:2]

        if dst:
            if width != dst.pixel_width or height != dst.pixel_height:
                raise RuntimeError("array size does not match size of dst Py5Image")
            py5_img = dst
        else:
            py5_img = self.create_image(width, height, self.ARGB)

        py5_img.set_np_pixels(array, bands)

        return py5_img

    def convert_image(
        self, obj: Any, *, dst: Py5Image = None, **kwargs: dict[str, Any]
    ) -> Py5Image:
        """Convert non-py5 image objects into Py5Image objects.

        Parameters
        ----------

        dst: Py5Image = None
            existing Py5Image object to put the converted image into

        kwargs: dict[str, Any]
            keyword arguments for conversion function

        obj: Any
            object to convert into a Py5Image object

        Notes
        -----

        Convert non-py5 image objects into Py5Image objects. This facilitates py5
        compatability with other commonly used Python libraries.

        This method is comparable to `load_image()`, except instead of reading image
        files from disk, it converts image data from other Python objects.

        Passed image object types must be known to py5's image conversion tools. New
        object types and functions to effect conversions can be registered with
        `register_image_conversion()`.

        The `convert_image()` method has builtin support for the conversion of
        `PIL.Image` objects. This will allow users to use image formats that
        `load_image()` cannot read. Look at the online "Images and Pillow" Python
        Ecosystem Integration tutorial for more information. To convert a numpy array
        into a Py5Image, use `create_image_from_numpy()`.

        The caller can optionally pass an existing Py5Image object to put the converted
        image into using the `dst` parameter. This can have performance benefits in code
        that would otherwise continuously create new Py5Image objects. The converted
        image width and height must match that of the recycled Py5Image object.

        The `convert_image()` method has builtin support for the conversion of
        matplotlib charts and Cairo surfaces. Look at the online "Charts, Plots, and
        Matplotlib" and "SVG Images and Cairo" Python Ecosystem Integration tutorials
        for more information. You can also create your own custom integrations. Look at
        the online "Custom Integrations" Python Ecosystem Integration tutorial to learn
        more."""
        if isinstance(obj, (Py5Image, Py5Graphics)):
            return obj
        result = image_conversion._convert(self, obj, **kwargs)
        if isinstance(result, (Path, str)):
            return self.load_image(result, dst=dst)
        elif isinstance(result, image_conversion.NumpyImageArray):
            return self.create_image_from_numpy(result.array, result.bands, dst=dst)
        else:
            # could be Py5Image or something comparable
            return result

    def convert_cached_image(
        self, obj: Any, force_conversion: bool = False, **kwargs: dict[str, Any]
    ) -> Py5Image:
        """Convert non-py5 image objects into Py5Image objects, but cache the results.

        Parameters
        ----------

        force_conversion: bool = False
            force conversion of object if it is already in the cache

        kwargs: dict[str, Any]
            keyword arguments for conversion function

        obj: Any
            object to convert into a Py5Image object

        Notes
        -----

        Convert non-py5 image objects into Py5Image objects, but cache the results. This
        method is similar to `convert_image()` with the addition of an object cache.
        Both methods facilitate py5 compatibility with other commonly used Python
        libraries.

        See `convert_image()` for method details.

        Converting objects to Py5Image objects can sometimes be slow. Usually you will
        not want to repeatedly convert the same object in your `draw()` function.
        Writing code to convert an object one time in `setup()` (with a `global`
        directive) to be later used in your `draw()` function can be a bit tedious. This
        method lets you write simpler code.

        Your object must be hashable for object caching to work. If your object is not
        hashable, it cannot be cached and you will receive a warning. If you want py5 to
        ignore a previously cached object and force a re-conversion, set the
        `force_conversion` parameter to `True`."""
        try:
            obj_in_cache = obj in self._py5_convert_image_cache
            hashable = True
        except TypeError:
            obj_in_cache = False
            hashable = False
            warnings.warn(
                "cannot cache convert image results for unhashable "
                + str(obj.__class__.__module__)
                + "."
                + str(obj.__class__.__name__)
                + " object"
            )

        if obj_in_cache and not force_conversion:
            return self._py5_convert_image_cache[obj]
        else:
            converted_obj = self.convert_image(obj, **kwargs)

            if hashable:
                self._py5_convert_image_cache[obj] = converted_obj

            return converted_obj

    def convert_shape(self, obj: Any, **kwargs: dict[str, Any]) -> Py5Shape:
        """Convert non-py5 shape objects into Py5Shape objects.

        Parameters
        ----------

        kwargs: dict[str, Any]
            keyword arguments for conversion function

        obj: Any
            object to convert into a Py5Shape object

        Notes
        -----

        Convert non-py5 shape objects into Py5Shape objects. This facilitates py5
        compatability with other commonly used Python libraries.

        This method is comparable to `load_shape()`, except instead of reading shape
        files from disk, it converts shape data from other Python objects.

        Passed shape object types must be known to py5's shape conversion tools. New
        object types and functions to effect conversions can be registered with
        `register_shape_conversion()`.

        The `convert_shape()` method has builtin support for the conversion of shapely
        and trimesh objects. This will allow users to explore the geometry capabilities
        of those libraries. Look at the online "2D Shapes and Shapely" and "3D Shapes
        and Trimesh" Python Ecosystem Integration tutorials for more information. You
        can also create your own custom integrations. Look at the online "Custom
        Integrations" Python Ecosystem Integration tutorial to learn more."""
        if isinstance(obj, Py5Shape):
            return obj
        return shape_conversion._convert(self, obj, **kwargs)

    def convert_cached_shape(
        self, obj: Any, force_conversion: bool = False, **kwargs: dict[str, Any]
    ) -> Py5Shape:
        """Convert non-py5 shape objects into Py5Shape objects, but cache the results.

        Parameters
        ----------

        force_conversion: bool = False
            force conversion of object if it is already in the cache

        kwargs: dict[str, Any]
            keyword arguments for conversion function

        obj: Any
            object to convert into a Py5Shape object

        Notes
        -----

        Convert non-py5 shape objects into Py5Shape objects, but cache the results. This
        method is similar to `convert_shape()` with the addition of an object cache.
        Both methods facilitate py5 compatibility with other commonly used Python
        libraries.

        See `convert_shape()` for method details.

        Converting objects to Py5Shape objects can sometimes be slow. Usually you will
        not want to repeatedly convert the same object in your `draw()` function.
        Writing code to convert an object one time in `setup()` (with a `global`
        directive) to be later used in your `draw()` function can be a bit tedious. This
        method lets you write simpler code.

        Your object must be hashable for object caching to work. If your object is not
        hashable, it cannot be cached and you will receive a warning. If you want py5 to
        ignore a previously cached object and force a re-conversion, set the
        `force_conversion` parameter to `True`."""
        try:
            obj_in_cache = obj in self._py5_convert_shape_cache
            hashable = True
        except TypeError:
            obj_in_cache = False
            hashable = False
            warnings.warn(
                "cannot cache convert shape results for unhashable "
                + str(obj.__class__.__module__)
                + "."
                + str(obj.__class__.__name__)
                + " object"
            )

        if obj_in_cache and not force_conversion:
            return self._py5_convert_shape_cache[obj]
        else:
            converted_obj = self.convert_shape(obj, **kwargs)

            if hashable:
                self._py5_convert_shape_cache[obj] = converted_obj

            return converted_obj

    def load_image(
        self, image_path: Union[str, Path], *, dst: Py5Image = None
    ) -> Py5Image:
        """Load an image into a variable of type `Py5Image`.

        Parameters
        ----------

        dst: Py5Image = None
            existing Py5Image object to load image into

        image_path: Union[str, Path]
            url or file path for image file

        Notes
        -----

        Load an image into a variable of type `Py5Image`. Four types of images (GIF,
        JPG, TGA, PNG) can be loaded. To load images in other formats, consider using
        `convert_image()`.

        The `image_path` parameter can be a file or a URL. When loading a file, the path
        can be in the data directory, relative to the current working directory
        (`sketch_path()`), or an absolute path. When loading from a URL, the
        `image_path` parameter must start with `http://` or `https://`. If the image
        cannot be loaded, a Python `RuntimeError` will be thrown.

        In most cases, load all images in `setup()` to preload them at the start of the
        program. Loading images inside `draw()` will reduce the speed of a program. In
        those situations, consider using `request_image()` instead.

        The `dst` parameter allows users to store the loaded image into an existing
        Py5Image object instead of creating a new object. The size of the existing
        Py5Image object must match the size of the loaded image. Most users will not
        find the `dst` parameter helpful. This feature is needed internally for
        performance reasons."""
        try:
            pimg = self._instance.loadImage(str(image_path))
        except JException as e:
            msg = "cannot load image file " + str(image_path)
            if e.message() == "None":
                msg += ". error message: either the file cannot be found or the file does not contain valid image data."
            else:
                msg += ". error message: " + e.message()
        else:
            if pimg and pimg.width > 0:
                if dst:
                    if (
                        pimg.pixel_width != dst.pixel_width
                        or pimg.pixel_height != dst.pixel_height
                    ):
                        raise RuntimeError(
                            "size of loaded image does not match size of dst Py5Image"
                        )
                    dst._replace_instance(pimg)
                    return dst
                else:
                    return Py5Image(pimg)
            else:
                raise RuntimeError(
                    "cannot load image file "
                    + str(image_path)
                    + ". error message: either the file cannot be found or the file does not contain valid image data."
                )
        raise RuntimeError(msg)

    def request_image(self, image_path: Union[str, Path]) -> Py5Promise:
        """Use a Py5Promise object to load an image into a variable of type `Py5Image`.

        Parameters
        ----------

        image_path: Union[str, Path]
            url or file path for image file

        Notes
        -----

        Use a Py5Promise object to load an image into a variable of type `Py5Image`.
        This method provides a convenient alternative to combining
        `launch_promise_thread()` with `load_image()` to load image data.

        Consider using `request_image()` to load image data from within a Sketch's
        `draw()` function. Using `load_image()` in the `draw()` function would slow down
        the Sketch animation.

        The returned Py5Promise object has an `is_ready` property that will be `True`
        when the `result` property contains the value function `f` returned. Before
        then, the `result` property will be `None`."""
        return self.launch_promise_thread(self.load_image, args=(image_path,))

    @overload
    def color_mode(self, mode: int, /) -> None:
        """Changes the way py5 interprets color data.

        Underlying Processing method: PApplet.colorMode

        Methods
        -------

        You can use any of the following signatures:

         * color_mode(colormap_mode: int, color_map: str, /) -> None
         * color_mode(colormap_mode: int, color_map: str, max_map: float, /) -> None
         * color_mode(colormap_mode: int, color_map: str, max_map: float, max_a: float, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, max_map: float, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, max_map: float, max_a: float, /, ) -> None
         * color_mode(mode: int, /) -> None
         * color_mode(mode: int, max1: float, max2: float, max3: float, /) -> None
         * color_mode(mode: int, max1: float, max2: float, max3: float, max_a: float, /) -> None
         * color_mode(mode: int, max: float, /) -> None

        Parameters
        ----------

        color_map: str
            name of builtin matplotlib Colormap

        color_map_instance: Colormap
            matplotlib.colors.Colormap instance

        colormap_mode: int
            CMAP, activating matplotlib Colormap mode

        max1: float
            range for the red or hue depending on the current color mode

        max2: float
            range for the green or saturation depending on the current color mode

        max3: float
            range for the blue or brightness depending on the current color mode

        max: float
            range for all color elements

        max_a: float
            range for the alpha

        max_map: float
            range for the color map

        mode: int
            Either RGB or HSB, corresponding to Red/Green/Blue and Hue/Saturation/Brightness

        Notes
        -----

        Changes the way py5 interprets color data. By default, the parameters for
        `fill()`, `stroke()`, `background()`, and `color()` are defined by values
        between 0 and 255 using the `RGB` color model. The `color_mode()` function is
        used to change the numerical range used for specifying colors and to switch
        color systems. For example, calling `color_mode(RGB, 1.0)` will specify that
        values are specified between 0 and 1. The limits for defining colors are altered
        by setting the parameters `max`, `max1`, `max2`, `max3`, and `max_a`.

        After changing the range of values for colors with code like `color_mode(HSB,
        360, 100, 100)`, those ranges remain in use until they are explicitly changed
        again. For example, after running `color_mode(HSB, 360, 100, 100)` and then
        changing back to `color_mode(RGB)`, the range for R will be 0 to 360 and the
        range for G and B will be 0 to 100. To avoid this, be explicit about the ranges
        when changing the color mode. For instance, instead of `color_mode(RGB)`, write
        `color_mode(RGB, 255, 255, 255)`."""
        pass

    @overload
    def color_mode(self, mode: int, max1: float, max2: float, max3: float, /) -> None:
        """Changes the way py5 interprets color data.

        Underlying Processing method: PApplet.colorMode

        Methods
        -------

        You can use any of the following signatures:

         * color_mode(colormap_mode: int, color_map: str, /) -> None
         * color_mode(colormap_mode: int, color_map: str, max_map: float, /) -> None
         * color_mode(colormap_mode: int, color_map: str, max_map: float, max_a: float, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, max_map: float, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, max_map: float, max_a: float, /, ) -> None
         * color_mode(mode: int, /) -> None
         * color_mode(mode: int, max1: float, max2: float, max3: float, /) -> None
         * color_mode(mode: int, max1: float, max2: float, max3: float, max_a: float, /) -> None
         * color_mode(mode: int, max: float, /) -> None

        Parameters
        ----------

        color_map: str
            name of builtin matplotlib Colormap

        color_map_instance: Colormap
            matplotlib.colors.Colormap instance

        colormap_mode: int
            CMAP, activating matplotlib Colormap mode

        max1: float
            range for the red or hue depending on the current color mode

        max2: float
            range for the green or saturation depending on the current color mode

        max3: float
            range for the blue or brightness depending on the current color mode

        max: float
            range for all color elements

        max_a: float
            range for the alpha

        max_map: float
            range for the color map

        mode: int
            Either RGB or HSB, corresponding to Red/Green/Blue and Hue/Saturation/Brightness

        Notes
        -----

        Changes the way py5 interprets color data. By default, the parameters for
        `fill()`, `stroke()`, `background()`, and `color()` are defined by values
        between 0 and 255 using the `RGB` color model. The `color_mode()` function is
        used to change the numerical range used for specifying colors and to switch
        color systems. For example, calling `color_mode(RGB, 1.0)` will specify that
        values are specified between 0 and 1. The limits for defining colors are altered
        by setting the parameters `max`, `max1`, `max2`, `max3`, and `max_a`.

        After changing the range of values for colors with code like `color_mode(HSB,
        360, 100, 100)`, those ranges remain in use until they are explicitly changed
        again. For example, after running `color_mode(HSB, 360, 100, 100)` and then
        changing back to `color_mode(RGB)`, the range for R will be 0 to 360 and the
        range for G and B will be 0 to 100. To avoid this, be explicit about the ranges
        when changing the color mode. For instance, instead of `color_mode(RGB)`, write
        `color_mode(RGB, 255, 255, 255)`."""
        pass

    @overload
    def color_mode(
        self, mode: int, max1: float, max2: float, max3: float, max_a: float, /
    ) -> None:
        """Changes the way py5 interprets color data.

        Underlying Processing method: PApplet.colorMode

        Methods
        -------

        You can use any of the following signatures:

         * color_mode(colormap_mode: int, color_map: str, /) -> None
         * color_mode(colormap_mode: int, color_map: str, max_map: float, /) -> None
         * color_mode(colormap_mode: int, color_map: str, max_map: float, max_a: float, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, max_map: float, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, max_map: float, max_a: float, /, ) -> None
         * color_mode(mode: int, /) -> None
         * color_mode(mode: int, max1: float, max2: float, max3: float, /) -> None
         * color_mode(mode: int, max1: float, max2: float, max3: float, max_a: float, /) -> None
         * color_mode(mode: int, max: float, /) -> None

        Parameters
        ----------

        color_map: str
            name of builtin matplotlib Colormap

        color_map_instance: Colormap
            matplotlib.colors.Colormap instance

        colormap_mode: int
            CMAP, activating matplotlib Colormap mode

        max1: float
            range for the red or hue depending on the current color mode

        max2: float
            range for the green or saturation depending on the current color mode

        max3: float
            range for the blue or brightness depending on the current color mode

        max: float
            range for all color elements

        max_a: float
            range for the alpha

        max_map: float
            range for the color map

        mode: int
            Either RGB or HSB, corresponding to Red/Green/Blue and Hue/Saturation/Brightness

        Notes
        -----

        Changes the way py5 interprets color data. By default, the parameters for
        `fill()`, `stroke()`, `background()`, and `color()` are defined by values
        between 0 and 255 using the `RGB` color model. The `color_mode()` function is
        used to change the numerical range used for specifying colors and to switch
        color systems. For example, calling `color_mode(RGB, 1.0)` will specify that
        values are specified between 0 and 1. The limits for defining colors are altered
        by setting the parameters `max`, `max1`, `max2`, `max3`, and `max_a`.

        After changing the range of values for colors with code like `color_mode(HSB,
        360, 100, 100)`, those ranges remain in use until they are explicitly changed
        again. For example, after running `color_mode(HSB, 360, 100, 100)` and then
        changing back to `color_mode(RGB)`, the range for R will be 0 to 360 and the
        range for G and B will be 0 to 100. To avoid this, be explicit about the ranges
        when changing the color mode. For instance, instead of `color_mode(RGB)`, write
        `color_mode(RGB, 255, 255, 255)`."""
        pass

    @overload
    def color_mode(self, mode: int, max: float, /) -> None:
        """Changes the way py5 interprets color data.

        Underlying Processing method: PApplet.colorMode

        Methods
        -------

        You can use any of the following signatures:

         * color_mode(colormap_mode: int, color_map: str, /) -> None
         * color_mode(colormap_mode: int, color_map: str, max_map: float, /) -> None
         * color_mode(colormap_mode: int, color_map: str, max_map: float, max_a: float, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, max_map: float, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, max_map: float, max_a: float, /, ) -> None
         * color_mode(mode: int, /) -> None
         * color_mode(mode: int, max1: float, max2: float, max3: float, /) -> None
         * color_mode(mode: int, max1: float, max2: float, max3: float, max_a: float, /) -> None
         * color_mode(mode: int, max: float, /) -> None

        Parameters
        ----------

        color_map: str
            name of builtin matplotlib Colormap

        color_map_instance: Colormap
            matplotlib.colors.Colormap instance

        colormap_mode: int
            CMAP, activating matplotlib Colormap mode

        max1: float
            range for the red or hue depending on the current color mode

        max2: float
            range for the green or saturation depending on the current color mode

        max3: float
            range for the blue or brightness depending on the current color mode

        max: float
            range for all color elements

        max_a: float
            range for the alpha

        max_map: float
            range for the color map

        mode: int
            Either RGB or HSB, corresponding to Red/Green/Blue and Hue/Saturation/Brightness

        Notes
        -----

        Changes the way py5 interprets color data. By default, the parameters for
        `fill()`, `stroke()`, `background()`, and `color()` are defined by values
        between 0 and 255 using the `RGB` color model. The `color_mode()` function is
        used to change the numerical range used for specifying colors and to switch
        color systems. For example, calling `color_mode(RGB, 1.0)` will specify that
        values are specified between 0 and 1. The limits for defining colors are altered
        by setting the parameters `max`, `max1`, `max2`, `max3`, and `max_a`.

        After changing the range of values for colors with code like `color_mode(HSB,
        360, 100, 100)`, those ranges remain in use until they are explicitly changed
        again. For example, after running `color_mode(HSB, 360, 100, 100)` and then
        changing back to `color_mode(RGB)`, the range for R will be 0 to 360 and the
        range for G and B will be 0 to 100. To avoid this, be explicit about the ranges
        when changing the color mode. For instance, instead of `color_mode(RGB)`, write
        `color_mode(RGB, 255, 255, 255)`."""
        pass

    @overload
    def color_mode(self, colormap_mode: int, color_map: str, /) -> None:
        """Changes the way py5 interprets color data.

        Underlying Processing method: PApplet.colorMode

        Methods
        -------

        You can use any of the following signatures:

         * color_mode(colormap_mode: int, color_map: str, /) -> None
         * color_mode(colormap_mode: int, color_map: str, max_map: float, /) -> None
         * color_mode(colormap_mode: int, color_map: str, max_map: float, max_a: float, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, max_map: float, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, max_map: float, max_a: float, /, ) -> None
         * color_mode(mode: int, /) -> None
         * color_mode(mode: int, max1: float, max2: float, max3: float, /) -> None
         * color_mode(mode: int, max1: float, max2: float, max3: float, max_a: float, /) -> None
         * color_mode(mode: int, max: float, /) -> None

        Parameters
        ----------

        color_map: str
            name of builtin matplotlib Colormap

        color_map_instance: Colormap
            matplotlib.colors.Colormap instance

        colormap_mode: int
            CMAP, activating matplotlib Colormap mode

        max1: float
            range for the red or hue depending on the current color mode

        max2: float
            range for the green or saturation depending on the current color mode

        max3: float
            range for the blue or brightness depending on the current color mode

        max: float
            range for all color elements

        max_a: float
            range for the alpha

        max_map: float
            range for the color map

        mode: int
            Either RGB or HSB, corresponding to Red/Green/Blue and Hue/Saturation/Brightness

        Notes
        -----

        Changes the way py5 interprets color data. By default, the parameters for
        `fill()`, `stroke()`, `background()`, and `color()` are defined by values
        between 0 and 255 using the `RGB` color model. The `color_mode()` function is
        used to change the numerical range used for specifying colors and to switch
        color systems. For example, calling `color_mode(RGB, 1.0)` will specify that
        values are specified between 0 and 1. The limits for defining colors are altered
        by setting the parameters `max`, `max1`, `max2`, `max3`, and `max_a`.

        After changing the range of values for colors with code like `color_mode(HSB,
        360, 100, 100)`, those ranges remain in use until they are explicitly changed
        again. For example, after running `color_mode(HSB, 360, 100, 100)` and then
        changing back to `color_mode(RGB)`, the range for R will be 0 to 360 and the
        range for G and B will be 0 to 100. To avoid this, be explicit about the ranges
        when changing the color mode. For instance, instead of `color_mode(RGB)`, write
        `color_mode(RGB, 255, 255, 255)`."""
        pass

    @overload
    def color_mode(self, colormap_mode: int, color_map_instance: Colormap, /) -> None:
        """Changes the way py5 interprets color data.

        Underlying Processing method: PApplet.colorMode

        Methods
        -------

        You can use any of the following signatures:

         * color_mode(colormap_mode: int, color_map: str, /) -> None
         * color_mode(colormap_mode: int, color_map: str, max_map: float, /) -> None
         * color_mode(colormap_mode: int, color_map: str, max_map: float, max_a: float, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, max_map: float, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, max_map: float, max_a: float, /, ) -> None
         * color_mode(mode: int, /) -> None
         * color_mode(mode: int, max1: float, max2: float, max3: float, /) -> None
         * color_mode(mode: int, max1: float, max2: float, max3: float, max_a: float, /) -> None
         * color_mode(mode: int, max: float, /) -> None

        Parameters
        ----------

        color_map: str
            name of builtin matplotlib Colormap

        color_map_instance: Colormap
            matplotlib.colors.Colormap instance

        colormap_mode: int
            CMAP, activating matplotlib Colormap mode

        max1: float
            range for the red or hue depending on the current color mode

        max2: float
            range for the green or saturation depending on the current color mode

        max3: float
            range for the blue or brightness depending on the current color mode

        max: float
            range for all color elements

        max_a: float
            range for the alpha

        max_map: float
            range for the color map

        mode: int
            Either RGB or HSB, corresponding to Red/Green/Blue and Hue/Saturation/Brightness

        Notes
        -----

        Changes the way py5 interprets color data. By default, the parameters for
        `fill()`, `stroke()`, `background()`, and `color()` are defined by values
        between 0 and 255 using the `RGB` color model. The `color_mode()` function is
        used to change the numerical range used for specifying colors and to switch
        color systems. For example, calling `color_mode(RGB, 1.0)` will specify that
        values are specified between 0 and 1. The limits for defining colors are altered
        by setting the parameters `max`, `max1`, `max2`, `max3`, and `max_a`.

        After changing the range of values for colors with code like `color_mode(HSB,
        360, 100, 100)`, those ranges remain in use until they are explicitly changed
        again. For example, after running `color_mode(HSB, 360, 100, 100)` and then
        changing back to `color_mode(RGB)`, the range for R will be 0 to 360 and the
        range for G and B will be 0 to 100. To avoid this, be explicit about the ranges
        when changing the color mode. For instance, instead of `color_mode(RGB)`, write
        `color_mode(RGB, 255, 255, 255)`."""
        pass

    @overload
    def color_mode(self, colormap_mode: int, color_map: str, max_map: float, /) -> None:
        """Changes the way py5 interprets color data.

        Underlying Processing method: PApplet.colorMode

        Methods
        -------

        You can use any of the following signatures:

         * color_mode(colormap_mode: int, color_map: str, /) -> None
         * color_mode(colormap_mode: int, color_map: str, max_map: float, /) -> None
         * color_mode(colormap_mode: int, color_map: str, max_map: float, max_a: float, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, max_map: float, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, max_map: float, max_a: float, /, ) -> None
         * color_mode(mode: int, /) -> None
         * color_mode(mode: int, max1: float, max2: float, max3: float, /) -> None
         * color_mode(mode: int, max1: float, max2: float, max3: float, max_a: float, /) -> None
         * color_mode(mode: int, max: float, /) -> None

        Parameters
        ----------

        color_map: str
            name of builtin matplotlib Colormap

        color_map_instance: Colormap
            matplotlib.colors.Colormap instance

        colormap_mode: int
            CMAP, activating matplotlib Colormap mode

        max1: float
            range for the red or hue depending on the current color mode

        max2: float
            range for the green or saturation depending on the current color mode

        max3: float
            range for the blue or brightness depending on the current color mode

        max: float
            range for all color elements

        max_a: float
            range for the alpha

        max_map: float
            range for the color map

        mode: int
            Either RGB or HSB, corresponding to Red/Green/Blue and Hue/Saturation/Brightness

        Notes
        -----

        Changes the way py5 interprets color data. By default, the parameters for
        `fill()`, `stroke()`, `background()`, and `color()` are defined by values
        between 0 and 255 using the `RGB` color model. The `color_mode()` function is
        used to change the numerical range used for specifying colors and to switch
        color systems. For example, calling `color_mode(RGB, 1.0)` will specify that
        values are specified between 0 and 1. The limits for defining colors are altered
        by setting the parameters `max`, `max1`, `max2`, `max3`, and `max_a`.

        After changing the range of values for colors with code like `color_mode(HSB,
        360, 100, 100)`, those ranges remain in use until they are explicitly changed
        again. For example, after running `color_mode(HSB, 360, 100, 100)` and then
        changing back to `color_mode(RGB)`, the range for R will be 0 to 360 and the
        range for G and B will be 0 to 100. To avoid this, be explicit about the ranges
        when changing the color mode. For instance, instead of `color_mode(RGB)`, write
        `color_mode(RGB, 255, 255, 255)`."""
        pass

    @overload
    def color_mode(
        self, colormap_mode: int, color_map_instance: Colormap, max_map: float, /
    ) -> None:
        """Changes the way py5 interprets color data.

        Underlying Processing method: PApplet.colorMode

        Methods
        -------

        You can use any of the following signatures:

         * color_mode(colormap_mode: int, color_map: str, /) -> None
         * color_mode(colormap_mode: int, color_map: str, max_map: float, /) -> None
         * color_mode(colormap_mode: int, color_map: str, max_map: float, max_a: float, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, max_map: float, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, max_map: float, max_a: float, /, ) -> None
         * color_mode(mode: int, /) -> None
         * color_mode(mode: int, max1: float, max2: float, max3: float, /) -> None
         * color_mode(mode: int, max1: float, max2: float, max3: float, max_a: float, /) -> None
         * color_mode(mode: int, max: float, /) -> None

        Parameters
        ----------

        color_map: str
            name of builtin matplotlib Colormap

        color_map_instance: Colormap
            matplotlib.colors.Colormap instance

        colormap_mode: int
            CMAP, activating matplotlib Colormap mode

        max1: float
            range for the red or hue depending on the current color mode

        max2: float
            range for the green or saturation depending on the current color mode

        max3: float
            range for the blue or brightness depending on the current color mode

        max: float
            range for all color elements

        max_a: float
            range for the alpha

        max_map: float
            range for the color map

        mode: int
            Either RGB or HSB, corresponding to Red/Green/Blue and Hue/Saturation/Brightness

        Notes
        -----

        Changes the way py5 interprets color data. By default, the parameters for
        `fill()`, `stroke()`, `background()`, and `color()` are defined by values
        between 0 and 255 using the `RGB` color model. The `color_mode()` function is
        used to change the numerical range used for specifying colors and to switch
        color systems. For example, calling `color_mode(RGB, 1.0)` will specify that
        values are specified between 0 and 1. The limits for defining colors are altered
        by setting the parameters `max`, `max1`, `max2`, `max3`, and `max_a`.

        After changing the range of values for colors with code like `color_mode(HSB,
        360, 100, 100)`, those ranges remain in use until they are explicitly changed
        again. For example, after running `color_mode(HSB, 360, 100, 100)` and then
        changing back to `color_mode(RGB)`, the range for R will be 0 to 360 and the
        range for G and B will be 0 to 100. To avoid this, be explicit about the ranges
        when changing the color mode. For instance, instead of `color_mode(RGB)`, write
        `color_mode(RGB, 255, 255, 255)`."""
        pass

    @overload
    def color_mode(
        self, colormap_mode: int, color_map: str, max_map: float, max_a: float, /
    ) -> None:
        """Changes the way py5 interprets color data.

        Underlying Processing method: PApplet.colorMode

        Methods
        -------

        You can use any of the following signatures:

         * color_mode(colormap_mode: int, color_map: str, /) -> None
         * color_mode(colormap_mode: int, color_map: str, max_map: float, /) -> None
         * color_mode(colormap_mode: int, color_map: str, max_map: float, max_a: float, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, max_map: float, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, max_map: float, max_a: float, /, ) -> None
         * color_mode(mode: int, /) -> None
         * color_mode(mode: int, max1: float, max2: float, max3: float, /) -> None
         * color_mode(mode: int, max1: float, max2: float, max3: float, max_a: float, /) -> None
         * color_mode(mode: int, max: float, /) -> None

        Parameters
        ----------

        color_map: str
            name of builtin matplotlib Colormap

        color_map_instance: Colormap
            matplotlib.colors.Colormap instance

        colormap_mode: int
            CMAP, activating matplotlib Colormap mode

        max1: float
            range for the red or hue depending on the current color mode

        max2: float
            range for the green or saturation depending on the current color mode

        max3: float
            range for the blue or brightness depending on the current color mode

        max: float
            range for all color elements

        max_a: float
            range for the alpha

        max_map: float
            range for the color map

        mode: int
            Either RGB or HSB, corresponding to Red/Green/Blue and Hue/Saturation/Brightness

        Notes
        -----

        Changes the way py5 interprets color data. By default, the parameters for
        `fill()`, `stroke()`, `background()`, and `color()` are defined by values
        between 0 and 255 using the `RGB` color model. The `color_mode()` function is
        used to change the numerical range used for specifying colors and to switch
        color systems. For example, calling `color_mode(RGB, 1.0)` will specify that
        values are specified between 0 and 1. The limits for defining colors are altered
        by setting the parameters `max`, `max1`, `max2`, `max3`, and `max_a`.

        After changing the range of values for colors with code like `color_mode(HSB,
        360, 100, 100)`, those ranges remain in use until they are explicitly changed
        again. For example, after running `color_mode(HSB, 360, 100, 100)` and then
        changing back to `color_mode(RGB)`, the range for R will be 0 to 360 and the
        range for G and B will be 0 to 100. To avoid this, be explicit about the ranges
        when changing the color mode. For instance, instead of `color_mode(RGB)`, write
        `color_mode(RGB, 255, 255, 255)`."""
        pass

    @overload
    def color_mode(
        self,
        colormap_mode: int,
        color_map_instance: Colormap,
        max_map: float,
        max_a: float,
        /,
    ) -> None:
        """Changes the way py5 interprets color data.

        Underlying Processing method: PApplet.colorMode

        Methods
        -------

        You can use any of the following signatures:

         * color_mode(colormap_mode: int, color_map: str, /) -> None
         * color_mode(colormap_mode: int, color_map: str, max_map: float, /) -> None
         * color_mode(colormap_mode: int, color_map: str, max_map: float, max_a: float, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, max_map: float, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, max_map: float, max_a: float, /, ) -> None
         * color_mode(mode: int, /) -> None
         * color_mode(mode: int, max1: float, max2: float, max3: float, /) -> None
         * color_mode(mode: int, max1: float, max2: float, max3: float, max_a: float, /) -> None
         * color_mode(mode: int, max: float, /) -> None

        Parameters
        ----------

        color_map: str
            name of builtin matplotlib Colormap

        color_map_instance: Colormap
            matplotlib.colors.Colormap instance

        colormap_mode: int
            CMAP, activating matplotlib Colormap mode

        max1: float
            range for the red or hue depending on the current color mode

        max2: float
            range for the green or saturation depending on the current color mode

        max3: float
            range for the blue or brightness depending on the current color mode

        max: float
            range for all color elements

        max_a: float
            range for the alpha

        max_map: float
            range for the color map

        mode: int
            Either RGB or HSB, corresponding to Red/Green/Blue and Hue/Saturation/Brightness

        Notes
        -----

        Changes the way py5 interprets color data. By default, the parameters for
        `fill()`, `stroke()`, `background()`, and `color()` are defined by values
        between 0 and 255 using the `RGB` color model. The `color_mode()` function is
        used to change the numerical range used for specifying colors and to switch
        color systems. For example, calling `color_mode(RGB, 1.0)` will specify that
        values are specified between 0 and 1. The limits for defining colors are altered
        by setting the parameters `max`, `max1`, `max2`, `max3`, and `max_a`.

        After changing the range of values for colors with code like `color_mode(HSB,
        360, 100, 100)`, those ranges remain in use until they are explicitly changed
        again. For example, after running `color_mode(HSB, 360, 100, 100)` and then
        changing back to `color_mode(RGB)`, the range for R will be 0 to 360 and the
        range for G and B will be 0 to 100. To avoid this, be explicit about the ranges
        when changing the color mode. For instance, instead of `color_mode(RGB)`, write
        `color_mode(RGB, 255, 255, 255)`."""
        pass

    def color_mode(self, mode: int, *args) -> None:
        """Changes the way py5 interprets color data.

        Underlying Processing method: PApplet.colorMode

        Methods
        -------

        You can use any of the following signatures:

         * color_mode(colormap_mode: int, color_map: str, /) -> None
         * color_mode(colormap_mode: int, color_map: str, max_map: float, /) -> None
         * color_mode(colormap_mode: int, color_map: str, max_map: float, max_a: float, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, max_map: float, /) -> None
         * color_mode(colormap_mode: int, color_map_instance: Colormap, max_map: float, max_a: float, /, ) -> None
         * color_mode(mode: int, /) -> None
         * color_mode(mode: int, max1: float, max2: float, max3: float, /) -> None
         * color_mode(mode: int, max1: float, max2: float, max3: float, max_a: float, /) -> None
         * color_mode(mode: int, max: float, /) -> None

        Parameters
        ----------

        color_map: str
            name of builtin matplotlib Colormap

        color_map_instance: Colormap
            matplotlib.colors.Colormap instance

        colormap_mode: int
            CMAP, activating matplotlib Colormap mode

        max1: float
            range for the red or hue depending on the current color mode

        max2: float
            range for the green or saturation depending on the current color mode

        max3: float
            range for the blue or brightness depending on the current color mode

        max: float
            range for all color elements

        max_a: float
            range for the alpha

        max_map: float
            range for the color map

        mode: int
            Either RGB or HSB, corresponding to Red/Green/Blue and Hue/Saturation/Brightness

        Notes
        -----

        Changes the way py5 interprets color data. By default, the parameters for
        `fill()`, `stroke()`, `background()`, and `color()` are defined by values
        between 0 and 255 using the `RGB` color model. The `color_mode()` function is
        used to change the numerical range used for specifying colors and to switch
        color systems. For example, calling `color_mode(RGB, 1.0)` will specify that
        values are specified between 0 and 1. The limits for defining colors are altered
        by setting the parameters `max`, `max1`, `max2`, `max3`, and `max_a`.

        After changing the range of values for colors with code like `color_mode(HSB,
        360, 100, 100)`, those ranges remain in use until they are explicitly changed
        again. For example, after running `color_mode(HSB, 360, 100, 100)` and then
        changing back to `color_mode(RGB)`, the range for R will be 0 to 360 and the
        range for G and B will be 0 to 100. To avoid this, be explicit about the ranges
        when changing the color mode. For instance, instead of `color_mode(RGB)`, write
        `color_mode(RGB, 255, 255, 255)`."""
        # don't allow users to call this before the Sketch starts running
        if not self.is_running:
            raise RuntimeError(
                "color_mode() cannot be called for a Sketch that is not running."
            )

        if mode == self.CMAP:
            if mpl is None:
                raise RuntimeError(
                    "matplotlib must be installed to use CMAP color mode"
                )
            args = list(args)
            if len(args) == 0:
                raise TypeError(
                    "When using the CMAP color mode, the second parameter must be an instance of matplotlib.colors.Colormap or a string representing a matplotlib colormap name"
                )
            if isinstance(args[0], str):
                if args[0] in mpl.colormaps:
                    args[0] = mpl.colormaps[args[0]]
                else:
                    raise RuntimeError(
                        "provided colormap name not available in matplotlib"
                    )
            elif not isinstance(args[0], mpl.colors.Colormap):
                raise RuntimeError(
                    "provided colormap is not an instance of mpl.colors.Colormap"
                )

            if len(args) == 1:
                self._cmap = args[0]
                self._cmap_range = 1.0
                self._cmap_alpha_range = 255
            elif len(args) == 2:
                self._cmap = args[0]
                self._cmap_range = args[1]
                self._cmap_alpha_range = 255
            elif len(args) == 3:
                self._cmap = args[0]
                self._cmap_range = args[1]
                self._cmap_alpha_range = args[2]
            else:
                raise TypeError(
                    "When using the CMAP color mode, the arguments must be one of color_mode(CMAP, cmap), color_mode(CMAP, cmap, range), or color_mode(CMAP, cmap, range, alpha_range)"
                )

            self._instance.colorMode(self.RGB, 255, 255, 255, self._cmap_alpha_range)
        else:
            self._cmap = None
            self._cmap_range = 0
            self._cmap_alpha_range = 0
            self._instance.colorMode(mode, *args)

    @overload
    def color(self, fgray: float, /) -> int:
        """Creates colors for storing in variables of the `color` datatype (a 32 bit
        integer).

        Underlying Processing method: PApplet.color

        Methods
        -------

        You can use any of the following signatures:

         * color(cmap_input: float, /) -> int
         * color(cmap_input: float, alpha: int, /) -> int
         * color(fgray: float, /) -> int
         * color(fgray: float, falpha: float, /) -> int
         * color(gray: int, /) -> int
         * color(gray: int, alpha: int, /) -> int
         * color(hex_code: str, /) -> int
         * color(hex_code: str, alpha: int, /) -> int
         * color(v1: float, v2: float, v3: float, /) -> int
         * color(v1: float, v2: float, v3: float, alpha: float, /) -> int
         * color(v1: int, v2: int, v3: int, /) -> int
         * color(v1: int, v2: int, v3: int, alpha: int, /) -> int

        Parameters
        ----------

        alpha: float
            alpha value relative to current color range

        alpha: int
            alpha value relative to current color range

        cmap_input: float
            input value when using colormap color mode

        falpha: float
            alpha value relative to current color range

        fgray: float
            number specifying value between white and black

        gray: int
            number specifying value between white and black

        hex_code: str
            hex color code

        v1: float
            red or hue values relative to the current color range

        v1: int
            red or hue values relative to the current color range

        v2: float
            green or saturation values relative to the current color range

        v2: int
            green or saturation values relative to the current color range

        v3: float
            blue or brightness values relative to the current color range

        v3: int
            blue or brightness values relative to the current color range

        Notes
        -----

        Creates colors for storing in variables of the `color` datatype (a 32 bit
        integer). The parameters are interpreted as `RGB` or `HSB` values depending on
        the current `color_mode()`. The default mode is `RGB` values from 0 to 255 and,
        therefore, `color(255, 204, 0)` will return a bright yellow color (see the first
        example).

        Note that if only one value is provided to `color()`, it will be interpreted as
        a grayscale value. Add a second value, and it will be used for alpha
        transparency. When three values are specified, they are interpreted as either
        `RGB` or `HSB` values. Adding a fourth value applies alpha transparency.

        Note that you can also use hexadecimal notation and web color notation to
        specify colors, as in `c = 0xFFDDCC33` or `c = "#DDCC33FF"` in place of `c =
        color(221, 204, 51, 255)`. Additionally, the `color()` method can accept both
        color notations as a parameter.

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
        values."""
        pass

    @overload
    def color(self, fgray: float, falpha: float, /) -> int:
        """Creates colors for storing in variables of the `color` datatype (a 32 bit
        integer).

        Underlying Processing method: PApplet.color

        Methods
        -------

        You can use any of the following signatures:

         * color(cmap_input: float, /) -> int
         * color(cmap_input: float, alpha: int, /) -> int
         * color(fgray: float, /) -> int
         * color(fgray: float, falpha: float, /) -> int
         * color(gray: int, /) -> int
         * color(gray: int, alpha: int, /) -> int
         * color(hex_code: str, /) -> int
         * color(hex_code: str, alpha: int, /) -> int
         * color(v1: float, v2: float, v3: float, /) -> int
         * color(v1: float, v2: float, v3: float, alpha: float, /) -> int
         * color(v1: int, v2: int, v3: int, /) -> int
         * color(v1: int, v2: int, v3: int, alpha: int, /) -> int

        Parameters
        ----------

        alpha: float
            alpha value relative to current color range

        alpha: int
            alpha value relative to current color range

        cmap_input: float
            input value when using colormap color mode

        falpha: float
            alpha value relative to current color range

        fgray: float
            number specifying value between white and black

        gray: int
            number specifying value between white and black

        hex_code: str
            hex color code

        v1: float
            red or hue values relative to the current color range

        v1: int
            red or hue values relative to the current color range

        v2: float
            green or saturation values relative to the current color range

        v2: int
            green or saturation values relative to the current color range

        v3: float
            blue or brightness values relative to the current color range

        v3: int
            blue or brightness values relative to the current color range

        Notes
        -----

        Creates colors for storing in variables of the `color` datatype (a 32 bit
        integer). The parameters are interpreted as `RGB` or `HSB` values depending on
        the current `color_mode()`. The default mode is `RGB` values from 0 to 255 and,
        therefore, `color(255, 204, 0)` will return a bright yellow color (see the first
        example).

        Note that if only one value is provided to `color()`, it will be interpreted as
        a grayscale value. Add a second value, and it will be used for alpha
        transparency. When three values are specified, they are interpreted as either
        `RGB` or `HSB` values. Adding a fourth value applies alpha transparency.

        Note that you can also use hexadecimal notation and web color notation to
        specify colors, as in `c = 0xFFDDCC33` or `c = "#DDCC33FF"` in place of `c =
        color(221, 204, 51, 255)`. Additionally, the `color()` method can accept both
        color notations as a parameter.

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
        values."""
        pass

    @overload
    def color(self, gray: int, /) -> int:
        """Creates colors for storing in variables of the `color` datatype (a 32 bit
        integer).

        Underlying Processing method: PApplet.color

        Methods
        -------

        You can use any of the following signatures:

         * color(cmap_input: float, /) -> int
         * color(cmap_input: float, alpha: int, /) -> int
         * color(fgray: float, /) -> int
         * color(fgray: float, falpha: float, /) -> int
         * color(gray: int, /) -> int
         * color(gray: int, alpha: int, /) -> int
         * color(hex_code: str, /) -> int
         * color(hex_code: str, alpha: int, /) -> int
         * color(v1: float, v2: float, v3: float, /) -> int
         * color(v1: float, v2: float, v3: float, alpha: float, /) -> int
         * color(v1: int, v2: int, v3: int, /) -> int
         * color(v1: int, v2: int, v3: int, alpha: int, /) -> int

        Parameters
        ----------

        alpha: float
            alpha value relative to current color range

        alpha: int
            alpha value relative to current color range

        cmap_input: float
            input value when using colormap color mode

        falpha: float
            alpha value relative to current color range

        fgray: float
            number specifying value between white and black

        gray: int
            number specifying value between white and black

        hex_code: str
            hex color code

        v1: float
            red or hue values relative to the current color range

        v1: int
            red or hue values relative to the current color range

        v2: float
            green or saturation values relative to the current color range

        v2: int
            green or saturation values relative to the current color range

        v3: float
            blue or brightness values relative to the current color range

        v3: int
            blue or brightness values relative to the current color range

        Notes
        -----

        Creates colors for storing in variables of the `color` datatype (a 32 bit
        integer). The parameters are interpreted as `RGB` or `HSB` values depending on
        the current `color_mode()`. The default mode is `RGB` values from 0 to 255 and,
        therefore, `color(255, 204, 0)` will return a bright yellow color (see the first
        example).

        Note that if only one value is provided to `color()`, it will be interpreted as
        a grayscale value. Add a second value, and it will be used for alpha
        transparency. When three values are specified, they are interpreted as either
        `RGB` or `HSB` values. Adding a fourth value applies alpha transparency.

        Note that you can also use hexadecimal notation and web color notation to
        specify colors, as in `c = 0xFFDDCC33` or `c = "#DDCC33FF"` in place of `c =
        color(221, 204, 51, 255)`. Additionally, the `color()` method can accept both
        color notations as a parameter.

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
        values."""
        pass

    @overload
    def color(self, gray: int, alpha: int, /) -> int:
        """Creates colors for storing in variables of the `color` datatype (a 32 bit
        integer).

        Underlying Processing method: PApplet.color

        Methods
        -------

        You can use any of the following signatures:

         * color(cmap_input: float, /) -> int
         * color(cmap_input: float, alpha: int, /) -> int
         * color(fgray: float, /) -> int
         * color(fgray: float, falpha: float, /) -> int
         * color(gray: int, /) -> int
         * color(gray: int, alpha: int, /) -> int
         * color(hex_code: str, /) -> int
         * color(hex_code: str, alpha: int, /) -> int
         * color(v1: float, v2: float, v3: float, /) -> int
         * color(v1: float, v2: float, v3: float, alpha: float, /) -> int
         * color(v1: int, v2: int, v3: int, /) -> int
         * color(v1: int, v2: int, v3: int, alpha: int, /) -> int

        Parameters
        ----------

        alpha: float
            alpha value relative to current color range

        alpha: int
            alpha value relative to current color range

        cmap_input: float
            input value when using colormap color mode

        falpha: float
            alpha value relative to current color range

        fgray: float
            number specifying value between white and black

        gray: int
            number specifying value between white and black

        hex_code: str
            hex color code

        v1: float
            red or hue values relative to the current color range

        v1: int
            red or hue values relative to the current color range

        v2: float
            green or saturation values relative to the current color range

        v2: int
            green or saturation values relative to the current color range

        v3: float
            blue or brightness values relative to the current color range

        v3: int
            blue or brightness values relative to the current color range

        Notes
        -----

        Creates colors for storing in variables of the `color` datatype (a 32 bit
        integer). The parameters are interpreted as `RGB` or `HSB` values depending on
        the current `color_mode()`. The default mode is `RGB` values from 0 to 255 and,
        therefore, `color(255, 204, 0)` will return a bright yellow color (see the first
        example).

        Note that if only one value is provided to `color()`, it will be interpreted as
        a grayscale value. Add a second value, and it will be used for alpha
        transparency. When three values are specified, they are interpreted as either
        `RGB` or `HSB` values. Adding a fourth value applies alpha transparency.

        Note that you can also use hexadecimal notation and web color notation to
        specify colors, as in `c = 0xFFDDCC33` or `c = "#DDCC33FF"` in place of `c =
        color(221, 204, 51, 255)`. Additionally, the `color()` method can accept both
        color notations as a parameter.

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
        values."""
        pass

    @overload
    def color(self, v1: float, v2: float, v3: float, /) -> int:
        """Creates colors for storing in variables of the `color` datatype (a 32 bit
        integer).

        Underlying Processing method: PApplet.color

        Methods
        -------

        You can use any of the following signatures:

         * color(cmap_input: float, /) -> int
         * color(cmap_input: float, alpha: int, /) -> int
         * color(fgray: float, /) -> int
         * color(fgray: float, falpha: float, /) -> int
         * color(gray: int, /) -> int
         * color(gray: int, alpha: int, /) -> int
         * color(hex_code: str, /) -> int
         * color(hex_code: str, alpha: int, /) -> int
         * color(v1: float, v2: float, v3: float, /) -> int
         * color(v1: float, v2: float, v3: float, alpha: float, /) -> int
         * color(v1: int, v2: int, v3: int, /) -> int
         * color(v1: int, v2: int, v3: int, alpha: int, /) -> int

        Parameters
        ----------

        alpha: float
            alpha value relative to current color range

        alpha: int
            alpha value relative to current color range

        cmap_input: float
            input value when using colormap color mode

        falpha: float
            alpha value relative to current color range

        fgray: float
            number specifying value between white and black

        gray: int
            number specifying value between white and black

        hex_code: str
            hex color code

        v1: float
            red or hue values relative to the current color range

        v1: int
            red or hue values relative to the current color range

        v2: float
            green or saturation values relative to the current color range

        v2: int
            green or saturation values relative to the current color range

        v3: float
            blue or brightness values relative to the current color range

        v3: int
            blue or brightness values relative to the current color range

        Notes
        -----

        Creates colors for storing in variables of the `color` datatype (a 32 bit
        integer). The parameters are interpreted as `RGB` or `HSB` values depending on
        the current `color_mode()`. The default mode is `RGB` values from 0 to 255 and,
        therefore, `color(255, 204, 0)` will return a bright yellow color (see the first
        example).

        Note that if only one value is provided to `color()`, it will be interpreted as
        a grayscale value. Add a second value, and it will be used for alpha
        transparency. When three values are specified, they are interpreted as either
        `RGB` or `HSB` values. Adding a fourth value applies alpha transparency.

        Note that you can also use hexadecimal notation and web color notation to
        specify colors, as in `c = 0xFFDDCC33` or `c = "#DDCC33FF"` in place of `c =
        color(221, 204, 51, 255)`. Additionally, the `color()` method can accept both
        color notations as a parameter.

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
        values."""
        pass

    @overload
    def color(self, v1: float, v2: float, v3: float, alpha: float, /) -> int:
        """Creates colors for storing in variables of the `color` datatype (a 32 bit
        integer).

        Underlying Processing method: PApplet.color

        Methods
        -------

        You can use any of the following signatures:

         * color(cmap_input: float, /) -> int
         * color(cmap_input: float, alpha: int, /) -> int
         * color(fgray: float, /) -> int
         * color(fgray: float, falpha: float, /) -> int
         * color(gray: int, /) -> int
         * color(gray: int, alpha: int, /) -> int
         * color(hex_code: str, /) -> int
         * color(hex_code: str, alpha: int, /) -> int
         * color(v1: float, v2: float, v3: float, /) -> int
         * color(v1: float, v2: float, v3: float, alpha: float, /) -> int
         * color(v1: int, v2: int, v3: int, /) -> int
         * color(v1: int, v2: int, v3: int, alpha: int, /) -> int

        Parameters
        ----------

        alpha: float
            alpha value relative to current color range

        alpha: int
            alpha value relative to current color range

        cmap_input: float
            input value when using colormap color mode

        falpha: float
            alpha value relative to current color range

        fgray: float
            number specifying value between white and black

        gray: int
            number specifying value between white and black

        hex_code: str
            hex color code

        v1: float
            red or hue values relative to the current color range

        v1: int
            red or hue values relative to the current color range

        v2: float
            green or saturation values relative to the current color range

        v2: int
            green or saturation values relative to the current color range

        v3: float
            blue or brightness values relative to the current color range

        v3: int
            blue or brightness values relative to the current color range

        Notes
        -----

        Creates colors for storing in variables of the `color` datatype (a 32 bit
        integer). The parameters are interpreted as `RGB` or `HSB` values depending on
        the current `color_mode()`. The default mode is `RGB` values from 0 to 255 and,
        therefore, `color(255, 204, 0)` will return a bright yellow color (see the first
        example).

        Note that if only one value is provided to `color()`, it will be interpreted as
        a grayscale value. Add a second value, and it will be used for alpha
        transparency. When three values are specified, they are interpreted as either
        `RGB` or `HSB` values. Adding a fourth value applies alpha transparency.

        Note that you can also use hexadecimal notation and web color notation to
        specify colors, as in `c = 0xFFDDCC33` or `c = "#DDCC33FF"` in place of `c =
        color(221, 204, 51, 255)`. Additionally, the `color()` method can accept both
        color notations as a parameter.

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
        values."""
        pass

    @overload
    def color(self, v1: int, v2: int, v3: int, /) -> int:
        """Creates colors for storing in variables of the `color` datatype (a 32 bit
        integer).

        Underlying Processing method: PApplet.color

        Methods
        -------

        You can use any of the following signatures:

         * color(cmap_input: float, /) -> int
         * color(cmap_input: float, alpha: int, /) -> int
         * color(fgray: float, /) -> int
         * color(fgray: float, falpha: float, /) -> int
         * color(gray: int, /) -> int
         * color(gray: int, alpha: int, /) -> int
         * color(hex_code: str, /) -> int
         * color(hex_code: str, alpha: int, /) -> int
         * color(v1: float, v2: float, v3: float, /) -> int
         * color(v1: float, v2: float, v3: float, alpha: float, /) -> int
         * color(v1: int, v2: int, v3: int, /) -> int
         * color(v1: int, v2: int, v3: int, alpha: int, /) -> int

        Parameters
        ----------

        alpha: float
            alpha value relative to current color range

        alpha: int
            alpha value relative to current color range

        cmap_input: float
            input value when using colormap color mode

        falpha: float
            alpha value relative to current color range

        fgray: float
            number specifying value between white and black

        gray: int
            number specifying value between white and black

        hex_code: str
            hex color code

        v1: float
            red or hue values relative to the current color range

        v1: int
            red or hue values relative to the current color range

        v2: float
            green or saturation values relative to the current color range

        v2: int
            green or saturation values relative to the current color range

        v3: float
            blue or brightness values relative to the current color range

        v3: int
            blue or brightness values relative to the current color range

        Notes
        -----

        Creates colors for storing in variables of the `color` datatype (a 32 bit
        integer). The parameters are interpreted as `RGB` or `HSB` values depending on
        the current `color_mode()`. The default mode is `RGB` values from 0 to 255 and,
        therefore, `color(255, 204, 0)` will return a bright yellow color (see the first
        example).

        Note that if only one value is provided to `color()`, it will be interpreted as
        a grayscale value. Add a second value, and it will be used for alpha
        transparency. When three values are specified, they are interpreted as either
        `RGB` or `HSB` values. Adding a fourth value applies alpha transparency.

        Note that you can also use hexadecimal notation and web color notation to
        specify colors, as in `c = 0xFFDDCC33` or `c = "#DDCC33FF"` in place of `c =
        color(221, 204, 51, 255)`. Additionally, the `color()` method can accept both
        color notations as a parameter.

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
        values."""
        pass

    @overload
    def color(self, v1: int, v2: int, v3: int, alpha: int, /) -> int:
        """Creates colors for storing in variables of the `color` datatype (a 32 bit
        integer).

        Underlying Processing method: PApplet.color

        Methods
        -------

        You can use any of the following signatures:

         * color(cmap_input: float, /) -> int
         * color(cmap_input: float, alpha: int, /) -> int
         * color(fgray: float, /) -> int
         * color(fgray: float, falpha: float, /) -> int
         * color(gray: int, /) -> int
         * color(gray: int, alpha: int, /) -> int
         * color(hex_code: str, /) -> int
         * color(hex_code: str, alpha: int, /) -> int
         * color(v1: float, v2: float, v3: float, /) -> int
         * color(v1: float, v2: float, v3: float, alpha: float, /) -> int
         * color(v1: int, v2: int, v3: int, /) -> int
         * color(v1: int, v2: int, v3: int, alpha: int, /) -> int

        Parameters
        ----------

        alpha: float
            alpha value relative to current color range

        alpha: int
            alpha value relative to current color range

        cmap_input: float
            input value when using colormap color mode

        falpha: float
            alpha value relative to current color range

        fgray: float
            number specifying value between white and black

        gray: int
            number specifying value between white and black

        hex_code: str
            hex color code

        v1: float
            red or hue values relative to the current color range

        v1: int
            red or hue values relative to the current color range

        v2: float
            green or saturation values relative to the current color range

        v2: int
            green or saturation values relative to the current color range

        v3: float
            blue or brightness values relative to the current color range

        v3: int
            blue or brightness values relative to the current color range

        Notes
        -----

        Creates colors for storing in variables of the `color` datatype (a 32 bit
        integer). The parameters are interpreted as `RGB` or `HSB` values depending on
        the current `color_mode()`. The default mode is `RGB` values from 0 to 255 and,
        therefore, `color(255, 204, 0)` will return a bright yellow color (see the first
        example).

        Note that if only one value is provided to `color()`, it will be interpreted as
        a grayscale value. Add a second value, and it will be used for alpha
        transparency. When three values are specified, they are interpreted as either
        `RGB` or `HSB` values. Adding a fourth value applies alpha transparency.

        Note that you can also use hexadecimal notation and web color notation to
        specify colors, as in `c = 0xFFDDCC33` or `c = "#DDCC33FF"` in place of `c =
        color(221, 204, 51, 255)`. Additionally, the `color()` method can accept both
        color notations as a parameter.

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
        values."""
        pass

    @overload
    def color(self, cmap_input: float, /) -> int:
        """Creates colors for storing in variables of the `color` datatype (a 32 bit
        integer).

        Underlying Processing method: PApplet.color

        Methods
        -------

        You can use any of the following signatures:

         * color(cmap_input: float, /) -> int
         * color(cmap_input: float, alpha: int, /) -> int
         * color(fgray: float, /) -> int
         * color(fgray: float, falpha: float, /) -> int
         * color(gray: int, /) -> int
         * color(gray: int, alpha: int, /) -> int
         * color(hex_code: str, /) -> int
         * color(hex_code: str, alpha: int, /) -> int
         * color(v1: float, v2: float, v3: float, /) -> int
         * color(v1: float, v2: float, v3: float, alpha: float, /) -> int
         * color(v1: int, v2: int, v3: int, /) -> int
         * color(v1: int, v2: int, v3: int, alpha: int, /) -> int

        Parameters
        ----------

        alpha: float
            alpha value relative to current color range

        alpha: int
            alpha value relative to current color range

        cmap_input: float
            input value when using colormap color mode

        falpha: float
            alpha value relative to current color range

        fgray: float
            number specifying value between white and black

        gray: int
            number specifying value between white and black

        hex_code: str
            hex color code

        v1: float
            red or hue values relative to the current color range

        v1: int
            red or hue values relative to the current color range

        v2: float
            green or saturation values relative to the current color range

        v2: int
            green or saturation values relative to the current color range

        v3: float
            blue or brightness values relative to the current color range

        v3: int
            blue or brightness values relative to the current color range

        Notes
        -----

        Creates colors for storing in variables of the `color` datatype (a 32 bit
        integer). The parameters are interpreted as `RGB` or `HSB` values depending on
        the current `color_mode()`. The default mode is `RGB` values from 0 to 255 and,
        therefore, `color(255, 204, 0)` will return a bright yellow color (see the first
        example).

        Note that if only one value is provided to `color()`, it will be interpreted as
        a grayscale value. Add a second value, and it will be used for alpha
        transparency. When three values are specified, they are interpreted as either
        `RGB` or `HSB` values. Adding a fourth value applies alpha transparency.

        Note that you can also use hexadecimal notation and web color notation to
        specify colors, as in `c = 0xFFDDCC33` or `c = "#DDCC33FF"` in place of `c =
        color(221, 204, 51, 255)`. Additionally, the `color()` method can accept both
        color notations as a parameter.

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
        values."""
        pass

    @overload
    def color(self, cmap_input: float, alpha: int, /) -> int:
        """Creates colors for storing in variables of the `color` datatype (a 32 bit
        integer).

        Underlying Processing method: PApplet.color

        Methods
        -------

        You can use any of the following signatures:

         * color(cmap_input: float, /) -> int
         * color(cmap_input: float, alpha: int, /) -> int
         * color(fgray: float, /) -> int
         * color(fgray: float, falpha: float, /) -> int
         * color(gray: int, /) -> int
         * color(gray: int, alpha: int, /) -> int
         * color(hex_code: str, /) -> int
         * color(hex_code: str, alpha: int, /) -> int
         * color(v1: float, v2: float, v3: float, /) -> int
         * color(v1: float, v2: float, v3: float, alpha: float, /) -> int
         * color(v1: int, v2: int, v3: int, /) -> int
         * color(v1: int, v2: int, v3: int, alpha: int, /) -> int

        Parameters
        ----------

        alpha: float
            alpha value relative to current color range

        alpha: int
            alpha value relative to current color range

        cmap_input: float
            input value when using colormap color mode

        falpha: float
            alpha value relative to current color range

        fgray: float
            number specifying value between white and black

        gray: int
            number specifying value between white and black

        hex_code: str
            hex color code

        v1: float
            red or hue values relative to the current color range

        v1: int
            red or hue values relative to the current color range

        v2: float
            green or saturation values relative to the current color range

        v2: int
            green or saturation values relative to the current color range

        v3: float
            blue or brightness values relative to the current color range

        v3: int
            blue or brightness values relative to the current color range

        Notes
        -----

        Creates colors for storing in variables of the `color` datatype (a 32 bit
        integer). The parameters are interpreted as `RGB` or `HSB` values depending on
        the current `color_mode()`. The default mode is `RGB` values from 0 to 255 and,
        therefore, `color(255, 204, 0)` will return a bright yellow color (see the first
        example).

        Note that if only one value is provided to `color()`, it will be interpreted as
        a grayscale value. Add a second value, and it will be used for alpha
        transparency. When three values are specified, they are interpreted as either
        `RGB` or `HSB` values. Adding a fourth value applies alpha transparency.

        Note that you can also use hexadecimal notation and web color notation to
        specify colors, as in `c = 0xFFDDCC33` or `c = "#DDCC33FF"` in place of `c =
        color(221, 204, 51, 255)`. Additionally, the `color()` method can accept both
        color notations as a parameter.

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
        values."""
        pass

    @overload
    def color(self, hex_code: str, /) -> int:
        """Creates colors for storing in variables of the `color` datatype (a 32 bit
        integer).

        Underlying Processing method: PApplet.color

        Methods
        -------

        You can use any of the following signatures:

         * color(cmap_input: float, /) -> int
         * color(cmap_input: float, alpha: int, /) -> int
         * color(fgray: float, /) -> int
         * color(fgray: float, falpha: float, /) -> int
         * color(gray: int, /) -> int
         * color(gray: int, alpha: int, /) -> int
         * color(hex_code: str, /) -> int
         * color(hex_code: str, alpha: int, /) -> int
         * color(v1: float, v2: float, v3: float, /) -> int
         * color(v1: float, v2: float, v3: float, alpha: float, /) -> int
         * color(v1: int, v2: int, v3: int, /) -> int
         * color(v1: int, v2: int, v3: int, alpha: int, /) -> int

        Parameters
        ----------

        alpha: float
            alpha value relative to current color range

        alpha: int
            alpha value relative to current color range

        cmap_input: float
            input value when using colormap color mode

        falpha: float
            alpha value relative to current color range

        fgray: float
            number specifying value between white and black

        gray: int
            number specifying value between white and black

        hex_code: str
            hex color code

        v1: float
            red or hue values relative to the current color range

        v1: int
            red or hue values relative to the current color range

        v2: float
            green or saturation values relative to the current color range

        v2: int
            green or saturation values relative to the current color range

        v3: float
            blue or brightness values relative to the current color range

        v3: int
            blue or brightness values relative to the current color range

        Notes
        -----

        Creates colors for storing in variables of the `color` datatype (a 32 bit
        integer). The parameters are interpreted as `RGB` or `HSB` values depending on
        the current `color_mode()`. The default mode is `RGB` values from 0 to 255 and,
        therefore, `color(255, 204, 0)` will return a bright yellow color (see the first
        example).

        Note that if only one value is provided to `color()`, it will be interpreted as
        a grayscale value. Add a second value, and it will be used for alpha
        transparency. When three values are specified, they are interpreted as either
        `RGB` or `HSB` values. Adding a fourth value applies alpha transparency.

        Note that you can also use hexadecimal notation and web color notation to
        specify colors, as in `c = 0xFFDDCC33` or `c = "#DDCC33FF"` in place of `c =
        color(221, 204, 51, 255)`. Additionally, the `color()` method can accept both
        color notations as a parameter.

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
        values."""
        pass

    @overload
    def color(self, hex_code: str, alpha: int, /) -> int:
        """Creates colors for storing in variables of the `color` datatype (a 32 bit
        integer).

        Underlying Processing method: PApplet.color

        Methods
        -------

        You can use any of the following signatures:

         * color(cmap_input: float, /) -> int
         * color(cmap_input: float, alpha: int, /) -> int
         * color(fgray: float, /) -> int
         * color(fgray: float, falpha: float, /) -> int
         * color(gray: int, /) -> int
         * color(gray: int, alpha: int, /) -> int
         * color(hex_code: str, /) -> int
         * color(hex_code: str, alpha: int, /) -> int
         * color(v1: float, v2: float, v3: float, /) -> int
         * color(v1: float, v2: float, v3: float, alpha: float, /) -> int
         * color(v1: int, v2: int, v3: int, /) -> int
         * color(v1: int, v2: int, v3: int, alpha: int, /) -> int

        Parameters
        ----------

        alpha: float
            alpha value relative to current color range

        alpha: int
            alpha value relative to current color range

        cmap_input: float
            input value when using colormap color mode

        falpha: float
            alpha value relative to current color range

        fgray: float
            number specifying value between white and black

        gray: int
            number specifying value between white and black

        hex_code: str
            hex color code

        v1: float
            red or hue values relative to the current color range

        v1: int
            red or hue values relative to the current color range

        v2: float
            green or saturation values relative to the current color range

        v2: int
            green or saturation values relative to the current color range

        v3: float
            blue or brightness values relative to the current color range

        v3: int
            blue or brightness values relative to the current color range

        Notes
        -----

        Creates colors for storing in variables of the `color` datatype (a 32 bit
        integer). The parameters are interpreted as `RGB` or `HSB` values depending on
        the current `color_mode()`. The default mode is `RGB` values from 0 to 255 and,
        therefore, `color(255, 204, 0)` will return a bright yellow color (see the first
        example).

        Note that if only one value is provided to `color()`, it will be interpreted as
        a grayscale value. Add a second value, and it will be used for alpha
        transparency. When three values are specified, they are interpreted as either
        `RGB` or `HSB` values. Adding a fourth value applies alpha transparency.

        Note that you can also use hexadecimal notation and web color notation to
        specify colors, as in `c = 0xFFDDCC33` or `c = "#DDCC33FF"` in place of `c =
        color(221, 204, 51, 255)`. Additionally, the `color()` method can accept both
        color notations as a parameter.

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
        values."""
        pass

    def color(self, *args) -> int:
        """Creates colors for storing in variables of the `color` datatype (a 32 bit
        integer).

        Underlying Processing method: PApplet.color

        Methods
        -------

        You can use any of the following signatures:

         * color(cmap_input: float, /) -> int
         * color(cmap_input: float, alpha: int, /) -> int
         * color(fgray: float, /) -> int
         * color(fgray: float, falpha: float, /) -> int
         * color(gray: int, /) -> int
         * color(gray: int, alpha: int, /) -> int
         * color(hex_code: str, /) -> int
         * color(hex_code: str, alpha: int, /) -> int
         * color(v1: float, v2: float, v3: float, /) -> int
         * color(v1: float, v2: float, v3: float, alpha: float, /) -> int
         * color(v1: int, v2: int, v3: int, /) -> int
         * color(v1: int, v2: int, v3: int, alpha: int, /) -> int

        Parameters
        ----------

        alpha: float
            alpha value relative to current color range

        alpha: int
            alpha value relative to current color range

        cmap_input: float
            input value when using colormap color mode

        falpha: float
            alpha value relative to current color range

        fgray: float
            number specifying value between white and black

        gray: int
            number specifying value between white and black

        hex_code: str
            hex color code

        v1: float
            red or hue values relative to the current color range

        v1: int
            red or hue values relative to the current color range

        v2: float
            green or saturation values relative to the current color range

        v2: int
            green or saturation values relative to the current color range

        v3: float
            blue or brightness values relative to the current color range

        v3: int
            blue or brightness values relative to the current color range

        Notes
        -----

        Creates colors for storing in variables of the `color` datatype (a 32 bit
        integer). The parameters are interpreted as `RGB` or `HSB` values depending on
        the current `color_mode()`. The default mode is `RGB` values from 0 to 255 and,
        therefore, `color(255, 204, 0)` will return a bright yellow color (see the first
        example).

        Note that if only one value is provided to `color()`, it will be interpreted as
        a grayscale value. Add a second value, and it will be used for alpha
        transparency. When three values are specified, they are interpreted as either
        `RGB` or `HSB` values. Adding a fourth value applies alpha transparency.

        Note that you can also use hexadecimal notation and web color notation to
        specify colors, as in `c = 0xFFDDCC33` or `c = "#DDCC33FF"` in place of `c =
        color(221, 204, 51, 255)`. Additionally, the `color()` method can accept both
        color notations as a parameter.

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
        values."""
        args = list(args)

        if not isinstance(args[0], Py5Color):
            if self._cmap is not None and isinstance(
                args[0], (int, np.integer, float, np.floating)
            ):
                new_arg = JInt(
                    int(
                        "0xFF"
                        + mcolors.to_hex(self._cmap(args[0] / self._cmap_range))[1:],
                        base=16,
                    )
                )
                args[0] = Py5Color(new_arg, _creator_instance=self)

            elif (new_arg := _hex_converter(args[0])) is not None:
                args[0] = Py5Color(new_arg, _creator_instance=self)

            if len(args) == 1 and isinstance(args[0], Py5Color):
                return args[0]

        if self.is_running:
            return Py5Color(self._instance.color(*args), _creator_instance=self)
        else:
            if not hasattr(self, "_dummy_pgraphics"):
                self._dummy_pgraphics = JClass("processing.core.PGraphics")()
                self._dummy_pgraphics.colorMode(self.RGB, 255, 255, 255, 255)

            return Py5Color(self._dummy_pgraphics.color(*args), _creator_instance=self)

    ADD = 2
    ALPHA = 4
    ALT = 18
    AMBIENT = 0
    ARC = 32
    ARGB = 2
    ARGS_BGCOLOR = "--bgcolor"
    ARGS_DISABLE_AWT = "--disable-awt"
    ARGS_DISPLAY = "--display"
    ARGS_EDITOR_LOCATION = "--editor-location"
    ARGS_EXTERNAL = "--external"
    ARGS_FULL_SCREEN = "--full-screen"
    ARGS_HIDE_STOP = "--hide-stop"
    ARGS_LOCATION = "--location"
    ARGS_PRESENT = "--present"
    ARGS_SKETCH_FOLDER = "--sketch-path"
    ARGS_STOP_COLOR = "--stop-color"
    ARGS_UI_SCALE = "--ui-scale"
    ARGS_WINDOW_COLOR = "--window-color"
    ARROW = 0
    BACKSPACE = "\b"
    BASELINE = 0
    BEVEL = 32
    BEZIER_VERTEX = 1
    BICUBIC = 2
    BILINEAR = 1
    BLEND = 1
    BLUR = 11
    BOTTOM = 102
    BOX = 41
    BREAK = 4
    BURN = 8192
    CENTER = 3
    CHORD = 2
    CLAMP = 0
    CLOSE = 2
    CODED = "\uffff"
    CONTROL = 17
    CORNER = 0
    CORNERS = 1
    CROSS = 1
    CURVE_VERTEX = 3
    DARKEST = 16
    DELETE = "\u007f"
    DIAMETER = 3
    DIFFERENCE = 32
    DILATE = 18
    DIRECTIONAL = 1
    DISABLE_ASYNC_SAVEFRAME = 12
    DISABLE_BUFFER_READING = -10
    DISABLE_DEPTH_MASK = 5
    DISABLE_DEPTH_SORT = -3
    DISABLE_DEPTH_TEST = 2
    DISABLE_KEY_REPEAT = 11
    DISABLE_NATIVE_FONTS = -1
    DISABLE_OPENGL_ERRORS = 4
    DISABLE_OPTIMIZED_STROKE = 6
    DISABLE_STROKE_PERSPECTIVE = -7
    DISABLE_STROKE_PURE = -9
    DISABLE_TEXTURE_MIPMAPS = 8
    DODGE = 4096
    DOWN = 40
    DXF = "processing.dxf.RawDXF"
    ELLIPSE = 31
    ENABLE_ASYNC_SAVEFRAME = -12
    ENABLE_BUFFER_READING = 10
    ENABLE_DEPTH_MASK = -5
    ENABLE_DEPTH_SORT = 3
    ENABLE_DEPTH_TEST = -2
    ENABLE_KEY_REPEAT = -11
    ENABLE_NATIVE_FONTS = 1
    ENABLE_OPENGL_ERRORS = -4
    ENABLE_OPTIMIZED_STROKE = -6
    ENABLE_STROKE_PERSPECTIVE = 7
    ENABLE_STROKE_PURE = 9
    ENABLE_TEXTURE_MIPMAPS = -8
    ENTER = "\n"
    EPSILON = 1.0e-4
    ERODE = 17
    ESC = "\u001b"
    EXCLUSION = 64
    EXTERNAL_MOVE = "__MOVE__"
    EXTERNAL_STOP = "__STOP__"
    FX2D = "processing.javafx.PGraphicsFX2D"
    GRAY = 12
    GROUP = 0
    HAND = 12
    HARD_LIGHT = 1024
    HIDDEN = "py5.core.graphics.HiddenPy5GraphicsJava2D"
    HSB = 3
    IMAGE = 2
    INVERT = 13
    JAVA2D = "processing.awt.PGraphicsJava2D"
    LEFT = 37
    LIGHTEST = 8
    LINE = 4
    LINES = 5
    LINE_LOOP = 51
    LINE_STRIP = 50
    MAX_FLOAT = 3.4028235e38
    MAX_INT = 2147483647
    MIN_FLOAT = -3.4028235e38
    MIN_INT = -2147483648
    MITER = 8
    MODEL = 4
    MOVE = 13
    MULTIPLY = 128
    NEAREST_NEIGHBOR = 0
    NORMAL = 1
    OPAQUE = 14
    OPEN = 1
    OPENGL = "processing.opengl.PGraphics3D"
    OVERLAY = 512
    P2D = "processing.opengl.PGraphics2D"
    P3D = "processing.opengl.PGraphics3D"
    PATH = 21
    PDF = "processing.pdf.PGraphicsPDF"
    PIE = 3
    POINT = 2
    POINTS = 3
    POLYGON = 20
    POSTERIZE = 15
    PROJECT = 4
    QUAD = 16
    QUADRATIC_VERTEX = 2
    QUADS = 17
    QUAD_BEZIER_VERTEX = 2
    QUAD_STRIP = 18
    RADIUS = 2
    RECT = 30
    REPEAT = 1
    REPLACE = 0
    RETURN = "\r"
    RGB = 1
    RIGHT = 39
    ROUND = 2
    SCREEN = 256
    SHAPE = 5
    SHIFT = 16
    SOFT_LIGHT = 2048
    SPAN = 0
    SPHERE = 40
    SPOT = 3
    SQUARE = 1
    SUBTRACT = 4
    SVG = "processing.svg.PGraphicsSVG"
    TAB = "\t"
    TEXT = 2
    THRESHOLD = 16
    TOP = 101
    TRIANGLE = 8
    TRIANGLES = 9
    TRIANGLE_FAN = 11
    TRIANGLE_STRIP = 10
    UP = 38
    VERTEX = 0
    WAIT = 3
    WHITESPACE = " \t\n\r\f\u00a0"

    @_return_list_str
    def _get_pargs(self) -> JArray(JString):
        """List of strings passed to the Sketch through the call to `run_sketch()`.

        Underlying Processing field: PApplet.args

        Notes
        -----

        List of strings passed to the Sketch through the call to `run_sketch()`. Only
        passing strings is allowed, but you can convert string types to something else
        to make this more useful.
        """
        return self._instance.args

    pargs: JArray(JString) = property(
        fget=_get_pargs,
        doc="""List of strings passed to the Sketch through the call to `run_sketch()`.

        Underlying Processing field: PApplet.args

        Notes
        -----

        List of strings passed to the Sketch through the call to `run_sketch()`. Only
        passing strings is allowed, but you can convert string types to something else
        to make this more useful.""",
    )

    def _get_display_height(self) -> int:
        """Variable that stores the height of the entire screen display.

        Underlying Processing field: PApplet.displayHeight

        Notes
        -----

        Variable that stores the height of the entire screen display. This can be used
        to run a full-screen program on any display size, but calling `full_screen()` is
        usually a better choice.
        """
        return self._instance.displayHeight

    display_height: int = property(
        fget=_get_display_height,
        doc="""Variable that stores the height of the entire screen display.

        Underlying Processing field: PApplet.displayHeight

        Notes
        -----

        Variable that stores the height of the entire screen display. This can be used
        to run a full-screen program on any display size, but calling `full_screen()` is
        usually a better choice.""",
    )

    def _get_display_width(self) -> int:
        """Variable that stores the width of the entire screen display.

        Underlying Processing field: PApplet.displayWidth

        Notes
        -----

        Variable that stores the width of the entire screen display. This can be used to
        run a full-screen program on any display size, but calling `full_screen()` is
        usually a better choice.
        """
        return self._instance.displayWidth

    display_width: int = property(
        fget=_get_display_width,
        doc="""Variable that stores the width of the entire screen display.

        Underlying Processing field: PApplet.displayWidth

        Notes
        -----

        Variable that stores the width of the entire screen display. This can be used to
        run a full-screen program on any display size, but calling `full_screen()` is
        usually a better choice.""",
    )

    def _get_finished(self) -> bool:
        """Boolean variable reflecting if the Sketch has stopped permanently.

        Underlying Processing field: PApplet.finished

        Notes
        -----

        Boolean variable reflecting if the Sketch has stopped permanently.
        """
        return self._instance.finished

    finished: bool = property(
        fget=_get_finished,
        doc="""Boolean variable reflecting if the Sketch has stopped permanently.

        Underlying Processing field: PApplet.finished

        Notes
        -----

        Boolean variable reflecting if the Sketch has stopped permanently.""",
    )

    def _get_focused(self) -> bool:
        """Confirms if a py5 program is "focused," meaning that it is active and will
        accept mouse or keyboard input.

        Underlying Processing field: PApplet.focused

        Notes
        -----

        Confirms if a py5 program is "focused," meaning that it is active and will
        accept mouse or keyboard input. This variable is `True` if it is focused and
        `False` if not.
        """
        return self._instance.focused

    focused: bool = property(
        fget=_get_focused,
        doc="""Confirms if a py5 program is "focused," meaning that it is active and will
        accept mouse or keyboard input.

        Underlying Processing field: PApplet.focused

        Notes
        -----

        Confirms if a py5 program is "focused," meaning that it is active and will
        accept mouse or keyboard input. This variable is `True` if it is focused and
        `False` if not.""",
    )

    def _get_frame_count(self) -> int:
        """The variable `frame_count` contains the number of frames that have been
        displayed since the program started.

        Underlying Processing field: PApplet.frameCount

        Notes
        -----

        The variable `frame_count` contains the number of frames that have been
        displayed since the program started. Inside `setup()` the value is 0. Inside the
        first execution of `draw()` it is 1, and it will increase by 1 for every
        execution of `draw()` after that.
        """
        return self._instance.frameCount

    frame_count: int = property(
        fget=_get_frame_count,
        doc="""The variable `frame_count` contains the number of frames that have been
        displayed since the program started.

        Underlying Processing field: PApplet.frameCount

        Notes
        -----

        The variable `frame_count` contains the number of frames that have been
        displayed since the program started. Inside `setup()` the value is 0. Inside the
        first execution of `draw()` it is 1, and it will increase by 1 for every
        execution of `draw()` after that.""",
    )

    def _get_height(self) -> int:
        """Variable that stores the height of the display window.

        Underlying Processing field: PApplet.height

        Notes
        -----

        Variable that stores the height of the display window. This value is set by the
        second parameter of the `size()` function. For example, the function call
        `size(320, 240)` sets the `height` variable to the value 240. The value of
        `height` defaults to 100 if `size()` is not used in a program.
        """
        return self._instance.height

    height: int = property(
        fget=_get_height,
        doc="""Variable that stores the height of the display window.

        Underlying Processing field: PApplet.height

        Notes
        -----

        Variable that stores the height of the display window. This value is set by the
        second parameter of the `size()` function. For example, the function call
        `size(320, 240)` sets the `height` variable to the value 240. The value of
        `height` defaults to 100 if `size()` is not used in a program.""",
    )

    def _get_java_platform(self) -> int:
        """Version of Java currently being used by py5.

        Underlying Processing field: PApplet.javaPlatform

        Notes
        -----

        Version of Java currently being used by py5. Internally the py5 library is using
        the Processing Java libraries to provide functionality. Those libraries run in a
        Java Virtual Machine. This field provides the Java platform number for that
        Virtual Machine.
        """
        return self._instance.javaPlatform

    java_platform: int = property(
        fget=_get_java_platform,
        doc="""Version of Java currently being used by py5.

        Underlying Processing field: PApplet.javaPlatform

        Notes
        -----

        Version of Java currently being used by py5. Internally the py5 library is using
        the Processing Java libraries to provide functionality. Those libraries run in a
        Java Virtual Machine. This field provides the Java platform number for that
        Virtual Machine.""",
    )

    def _get_java_version_name(self) -> str:
        """Version name of Java currently being used by py5.

        Underlying Processing field: PApplet.javaVersionName

        Notes
        -----

        Version name of Java currently being used by py5. Internally the py5 library is
        using the Processing Java libraries to provide functionality. Those libraries
        run in a Java Virtual Machine. This field provides the Java version name for
        that Virtual Machine.
        """
        return self._instance.javaVersionName

    java_version_name: str = property(
        fget=_get_java_version_name,
        doc="""Version name of Java currently being used by py5.

        Underlying Processing field: PApplet.javaVersionName

        Notes
        -----

        Version name of Java currently being used by py5. Internally the py5 library is
        using the Processing Java libraries to provide functionality. Those libraries
        run in a Java Virtual Machine. This field provides the Java version name for
        that Virtual Machine.""",
    )

    @_convert_jchar_to_chr
    def _get_key(self) -> chr:
        """The variable `key` always contains the value of the most recent key on the
        keyboard that was used (either pressed or released).

        Underlying Processing field: PApplet.key

        Notes
        -----

        The variable `key` always contains the value of the most recent key on the
        keyboard that was used (either pressed or released).

        For non-ASCII keys, use the `key_code` variable. The keys included in the ASCII
        specification (`BACKSPACE`, `TAB`, `ENTER`, `RETURN`, `ESC`, and `DELETE`) do
        not require checking to see if the key is coded, and you should simply use the
        `key` variable instead of `key_code`. If you're making cross-platform projects,
        note that the `ENTER` key is commonly used on PCs and Unix and the `RETURN` key
        is used instead on Macintosh. Check for both `ENTER` and `RETURN` to make sure
        your program will work for all platforms.

        There are issues with how `key_code` behaves across different renderers and
        operating systems. Watch out for unexpected behavior as you switch renderers and
        operating systems.
        """
        return self._instance.key

    key: chr = property(
        fget=_get_key,
        doc="""The variable `key` always contains the value of the most recent key on the
        keyboard that was used (either pressed or released).

        Underlying Processing field: PApplet.key

        Notes
        -----

        The variable `key` always contains the value of the most recent key on the
        keyboard that was used (either pressed or released).

        For non-ASCII keys, use the `key_code` variable. The keys included in the ASCII
        specification (`BACKSPACE`, `TAB`, `ENTER`, `RETURN`, `ESC`, and `DELETE`) do
        not require checking to see if the key is coded, and you should simply use the
        `key` variable instead of `key_code`. If you're making cross-platform projects,
        note that the `ENTER` key is commonly used on PCs and Unix and the `RETURN` key
        is used instead on Macintosh. Check for both `ENTER` and `RETURN` to make sure
        your program will work for all platforms.

        There are issues with how `key_code` behaves across different renderers and
        operating systems. Watch out for unexpected behavior as you switch renderers and
        operating systems.""",
    )

    @_convert_jint_to_int
    def _get_key_code(self) -> int:
        """The variable `key_code` is used to detect special keys such as the arrow keys
        (`UP`, `DOWN`, `LEFT`, and `RIGHT`) as well as `ALT`, `CONTROL`, and `SHIFT`.

        Underlying Processing field: PApplet.keyCode

        Notes
        -----

        The variable `key_code` is used to detect special keys such as the arrow keys
        (`UP`, `DOWN`, `LEFT`, and `RIGHT`) as well as `ALT`, `CONTROL`, and `SHIFT`.

        When checking for these keys, it can be useful to first check if the key is
        coded. This is done with the conditional `if (key == CODED)`, as shown in the
        example.

        The keys included in the ASCII specification (`BACKSPACE`, `TAB`, `ENTER`,
        `RETURN`, `ESC`, and `DELETE`) do not require checking to see if the key is
        coded; for those keys, you should simply use the `key` variable directly (and
        not `key_code`).  If you're making cross-platform projects, note that the
        `ENTER` key is commonly used on PCs and Unix, while the `RETURN` key is used on
        Macs. Make sure your program will work on all platforms by checking for both
        `ENTER` and `RETURN`.

        For those familiar with Java, the values for `UP` and `DOWN` are simply shorter
        versions of Java's `key_event.VK_UP` and `key_event.VK_DOWN`. Other `key_code`
        values can be found in the Java KeyEvent reference.

        There are issues with how `key_code` behaves across different renderers and
        operating systems. Watch out for unexpected behavior as you switch renderers and
        operating systems and you are using keys are aren't mentioned in this reference
        entry.

        If you are using `P2D` or `P3D` as your renderer, use the `NEWT` KeyEvent
        constants.
        """
        return self._instance.keyCode

    key_code: int = property(
        fget=_get_key_code,
        doc="""The variable `key_code` is used to detect special keys such as the arrow keys
        (`UP`, `DOWN`, `LEFT`, and `RIGHT`) as well as `ALT`, `CONTROL`, and `SHIFT`.

        Underlying Processing field: PApplet.keyCode

        Notes
        -----

        The variable `key_code` is used to detect special keys such as the arrow keys
        (`UP`, `DOWN`, `LEFT`, and `RIGHT`) as well as `ALT`, `CONTROL`, and `SHIFT`.

        When checking for these keys, it can be useful to first check if the key is
        coded. This is done with the conditional `if (key == CODED)`, as shown in the
        example.

        The keys included in the ASCII specification (`BACKSPACE`, `TAB`, `ENTER`,
        `RETURN`, `ESC`, and `DELETE`) do not require checking to see if the key is
        coded; for those keys, you should simply use the `key` variable directly (and
        not `key_code`).  If you're making cross-platform projects, note that the
        `ENTER` key is commonly used on PCs and Unix, while the `RETURN` key is used on
        Macs. Make sure your program will work on all platforms by checking for both
        `ENTER` and `RETURN`.

        For those familiar with Java, the values for `UP` and `DOWN` are simply shorter
        versions of Java's `key_event.VK_UP` and `key_event.VK_DOWN`. Other `key_code`
        values can be found in the Java KeyEvent reference.

        There are issues with how `key_code` behaves across different renderers and
        operating systems. Watch out for unexpected behavior as you switch renderers and
        operating systems and you are using keys are aren't mentioned in this reference
        entry.

        If you are using `P2D` or `P3D` as your renderer, use the `NEWT` KeyEvent
        constants.""",
    )

    def _get_mouse_button(self) -> int:
        """When a mouse button is pressed, the variable `mouse_button` is set to either
        `LEFT`, `RIGHT`, or `CENTER`, depending on which button is pressed.

        Underlying Processing field: PApplet.mouseButton

        Notes
        -----

        When a mouse button is pressed, the variable `mouse_button` is set to either
        `LEFT`, `RIGHT`, or `CENTER`, depending on which button is pressed. (If no
        button is pressed, `mouse_button` may be reset to `0`. For that reason, it's
        best to use `mouse_pressed` first to test if any button is being pressed, and
        only then test the value of `mouse_button`, as shown in the examples.)
        """
        return self._instance.mouseButton

    mouse_button: int = property(
        fget=_get_mouse_button,
        doc="""When a mouse button is pressed, the variable `mouse_button` is set to either
        `LEFT`, `RIGHT`, or `CENTER`, depending on which button is pressed.

        Underlying Processing field: PApplet.mouseButton

        Notes
        -----

        When a mouse button is pressed, the variable `mouse_button` is set to either
        `LEFT`, `RIGHT`, or `CENTER`, depending on which button is pressed. (If no
        button is pressed, `mouse_button` may be reset to `0`. For that reason, it's
        best to use `mouse_pressed` first to test if any button is being pressed, and
        only then test the value of `mouse_button`, as shown in the examples.)""",
    )

    def _get_mouse_x(self) -> int:
        """The variable `mouse_x` always contains the current horizontal coordinate of the
        mouse.

        Underlying Processing field: PApplet.mouseX

        Notes
        -----

        The variable `mouse_x` always contains the current horizontal coordinate of the
        mouse.

        Note that py5 can only track the mouse position when the pointer is over the
        current window. The default value of `mouse_x` is `0`, so `0` will be returned
        until the mouse moves in front of the Sketch window. (This typically happens
        when a Sketch is first run.)  Once the mouse moves away from the window,
        `mouse_x` will continue to report its most recent position.
        """
        return self._instance.mouseX

    mouse_x: int = property(
        fget=_get_mouse_x,
        doc="""The variable `mouse_x` always contains the current horizontal coordinate of the
        mouse.

        Underlying Processing field: PApplet.mouseX

        Notes
        -----

        The variable `mouse_x` always contains the current horizontal coordinate of the
        mouse.

        Note that py5 can only track the mouse position when the pointer is over the
        current window. The default value of `mouse_x` is `0`, so `0` will be returned
        until the mouse moves in front of the Sketch window. (This typically happens
        when a Sketch is first run.)  Once the mouse moves away from the window,
        `mouse_x` will continue to report its most recent position.""",
    )

    def _get_mouse_y(self) -> int:
        """The variable `mouse_y` always contains the current vertical coordinate of the
        mouse.

        Underlying Processing field: PApplet.mouseY

        Notes
        -----

        The variable `mouse_y` always contains the current vertical coordinate of the
        mouse.

        Note that py5 can only track the mouse position when the pointer is over the
        current window. The default value of `mouse_y` is `0`, so `0` will be returned
        until the mouse moves in front of the Sketch window. (This typically happens
        when a Sketch is first run.)  Once the mouse moves away from the window,
        `mouse_y` will continue to report its most recent position.
        """
        return self._instance.mouseY

    mouse_y: int = property(
        fget=_get_mouse_y,
        doc="""The variable `mouse_y` always contains the current vertical coordinate of the
        mouse.

        Underlying Processing field: PApplet.mouseY

        Notes
        -----

        The variable `mouse_y` always contains the current vertical coordinate of the
        mouse.

        Note that py5 can only track the mouse position when the pointer is over the
        current window. The default value of `mouse_y` is `0`, so `0` will be returned
        until the mouse moves in front of the Sketch window. (This typically happens
        when a Sketch is first run.)  Once the mouse moves away from the window,
        `mouse_y` will continue to report its most recent position.""",
    )

    def _get_pixel_height(self) -> int:
        """Height of the display window in pixels.

        Underlying Processing field: PApplet.pixelHeight

        Notes
        -----

        Height of the display window in pixels. When `pixel_density(2)` is used to make
        use of a high resolution display (called a Retina display on macOS or high-dpi
        on Windows and Linux), the width and height of the Sketch do not change, but the
        number of pixels is doubled. As a result, all operations that use pixels (like
        `load_pixels()`, `get_pixels()`, etc.) happen in this doubled space. As a
        convenience, the variables `pixel_width` and `pixel_height` hold the actual
        width and height of the Sketch in pixels. This is useful for any Sketch that use
        the `pixels[]` or `np_pixels[]` arrays, for instance, because the number of
        elements in each array will be `pixel_width*pixel_height`, not `width*height`.
        """
        return self._instance.pixelHeight

    pixel_height: int = property(
        fget=_get_pixel_height,
        doc="""Height of the display window in pixels.

        Underlying Processing field: PApplet.pixelHeight

        Notes
        -----

        Height of the display window in pixels. When `pixel_density(2)` is used to make
        use of a high resolution display (called a Retina display on macOS or high-dpi
        on Windows and Linux), the width and height of the Sketch do not change, but the
        number of pixels is doubled. As a result, all operations that use pixels (like
        `load_pixels()`, `get_pixels()`, etc.) happen in this doubled space. As a
        convenience, the variables `pixel_width` and `pixel_height` hold the actual
        width and height of the Sketch in pixels. This is useful for any Sketch that use
        the `pixels[]` or `np_pixels[]` arrays, for instance, because the number of
        elements in each array will be `pixel_width*pixel_height`, not `width*height`.""",
    )

    def _get_pixel_width(self) -> int:
        """Width of the display window in pixels.

        Underlying Processing field: PApplet.pixelWidth

        Notes
        -----

        Width of the display window in pixels. When `pixel_density(2)` is used to make
        use of a high resolution display (called a Retina display on macOS or high-dpi
        on Windows and Linux), the width and height of the Sketch do not change, but the
        number of pixels is doubled. As a result, all operations that use pixels (like
        `load_pixels()`, `get_pixels()`, etc.) happen in this doubled space. As a
        convenience, the variables `pixel_width` and `pixel_height` hold the actual
        width and height of the Sketch in pixels. This is useful for any Sketch that use
        the `pixels[]` or `np_pixels[]` arrays, for instance, because the number of
        elements in each array will be `pixel_width*pixel_height`, not `width*height`.
        """
        return self._instance.pixelWidth

    pixel_width: int = property(
        fget=_get_pixel_width,
        doc="""Width of the display window in pixels.

        Underlying Processing field: PApplet.pixelWidth

        Notes
        -----

        Width of the display window in pixels. When `pixel_density(2)` is used to make
        use of a high resolution display (called a Retina display on macOS or high-dpi
        on Windows and Linux), the width and height of the Sketch do not change, but the
        number of pixels is doubled. As a result, all operations that use pixels (like
        `load_pixels()`, `get_pixels()`, etc.) happen in this doubled space. As a
        convenience, the variables `pixel_width` and `pixel_height` hold the actual
        width and height of the Sketch in pixels. This is useful for any Sketch that use
        the `pixels[]` or `np_pixels[]` arrays, for instance, because the number of
        elements in each array will be `pixel_width*pixel_height`, not `width*height`.""",
    )

    def _get_pmouse_x(self) -> int:
        """The variable `pmouse_x` always contains the horizontal position of the mouse in
        the frame previous to the current frame.

        Underlying Processing field: PApplet.pmouseX

        Notes
        -----

        The variable `pmouse_x` always contains the horizontal position of the mouse in
        the frame previous to the current frame.

        You may find that `pmouse_x` and `pmouse_y` have different values when
        referenced inside of `draw()` and inside of mouse events like `mouse_pressed()`
        and `mouse_moved()`. Inside `draw()`, `pmouse_x` and `pmouse_y` update only once
        per frame (once per trip through the `draw()` loop). But inside mouse events,
        they update each time the event is called. If these values weren't updated
        immediately during mouse events, then the mouse position would be read only once
        per frame, resulting in slight delays and choppy interaction. If the mouse
        variables were always updated multiple times per frame, then something like
        `line(pmouse_x, pmouse_y, mouse_x, mouse_y)` inside `draw()` would have lots of
        gaps, because `pmouse_x` may have changed several times in between the calls to
        `line()`.

        If you want values relative to the previous frame, use `pmouse_x` and `pmouse_y`
        inside `draw()`. If you want continuous response, use `pmouse_x` and `pmouse_y`
        inside the mouse event functions.
        """
        return self._instance.pmouseX

    pmouse_x: int = property(
        fget=_get_pmouse_x,
        doc="""The variable `pmouse_x` always contains the horizontal position of the mouse in
        the frame previous to the current frame.

        Underlying Processing field: PApplet.pmouseX

        Notes
        -----

        The variable `pmouse_x` always contains the horizontal position of the mouse in
        the frame previous to the current frame.

        You may find that `pmouse_x` and `pmouse_y` have different values when
        referenced inside of `draw()` and inside of mouse events like `mouse_pressed()`
        and `mouse_moved()`. Inside `draw()`, `pmouse_x` and `pmouse_y` update only once
        per frame (once per trip through the `draw()` loop). But inside mouse events,
        they update each time the event is called. If these values weren't updated
        immediately during mouse events, then the mouse position would be read only once
        per frame, resulting in slight delays and choppy interaction. If the mouse
        variables were always updated multiple times per frame, then something like
        `line(pmouse_x, pmouse_y, mouse_x, mouse_y)` inside `draw()` would have lots of
        gaps, because `pmouse_x` may have changed several times in between the calls to
        `line()`.

        If you want values relative to the previous frame, use `pmouse_x` and `pmouse_y`
        inside `draw()`. If you want continuous response, use `pmouse_x` and `pmouse_y`
        inside the mouse event functions.""",
    )

    def _get_pmouse_y(self) -> int:
        """The variable `pmouse_y` always contains the vertical position of the mouse in
        the frame previous to the current frame.

        Underlying Processing field: PApplet.pmouseY

        Notes
        -----

        The variable `pmouse_y` always contains the vertical position of the mouse in
        the frame previous to the current frame.

        For more detail on how `pmouse_y` is updated inside of mouse events and
        `draw()`, see the reference for `pmouse_x`.
        """
        return self._instance.pmouseY

    pmouse_y: int = property(
        fget=_get_pmouse_y,
        doc="""The variable `pmouse_y` always contains the vertical position of the mouse in
        the frame previous to the current frame.

        Underlying Processing field: PApplet.pmouseY

        Notes
        -----

        The variable `pmouse_y` always contains the vertical position of the mouse in
        the frame previous to the current frame.

        For more detail on how `pmouse_y` is updated inside of mouse events and
        `draw()`, see the reference for `pmouse_x`.""",
    )

    def _get_ratio_left(self) -> float:
        """Width of the left section of the window that does not fit the desired aspect
        ratio of a scale invariant Sketch.

        Underlying Processing field: Sketch.ratioLeft

        Notes
        -----

        Width of the left section of the window that does not fit the desired aspect
        ratio of a scale invariant Sketch. This will always be greater than or equal to
        zero. Experimenting with the example and seeing how this value changes will
        provide more understanding than what can be explained with words. See
        `window_ratio()` for more information about how to activate scale invariant
        drawing and why it is useful.
        """
        return self._instance.ratioLeft

    ratio_left: float = property(
        fget=_get_ratio_left,
        doc="""Width of the left section of the window that does not fit the desired aspect
        ratio of a scale invariant Sketch.

        Underlying Processing field: Sketch.ratioLeft

        Notes
        -----

        Width of the left section of the window that does not fit the desired aspect
        ratio of a scale invariant Sketch. This will always be greater than or equal to
        zero. Experimenting with the example and seeing how this value changes will
        provide more understanding than what can be explained with words. See
        `window_ratio()` for more information about how to activate scale invariant
        drawing and why it is useful.""",
    )

    def _get_ratio_scale(self) -> float:
        """Scaling factor used to maintain scale invariant drawing.

        Underlying Processing field: Sketch.ratioScale

        Notes
        -----

        Scaling factor used to maintain scale invariant drawing. Experimenting with the
        example and seeing how this value changes will provide more understanding than
        what can be explained with words. See `window_ratio()` for more information
        about how to activate scale invariant drawing and why it is useful.
        """
        return self._instance.ratioScale

    ratio_scale: float = property(
        fget=_get_ratio_scale,
        doc="""Scaling factor used to maintain scale invariant drawing.

        Underlying Processing field: Sketch.ratioScale

        Notes
        -----

        Scaling factor used to maintain scale invariant drawing. Experimenting with the
        example and seeing how this value changes will provide more understanding than
        what can be explained with words. See `window_ratio()` for more information
        about how to activate scale invariant drawing and why it is useful.""",
    )

    def _get_ratio_top(self) -> float:
        """Height of the top section of the window that does not fit the desired aspect
        ratio of a scale invariant Sketch.

        Underlying Processing field: Sketch.ratioTop

        Notes
        -----

        Height of the top section of the window that does not fit the desired aspect
        ratio of a scale invariant Sketch. This will always be greater than or equal to
        zero. Experimenting with the example and seeing how this value changes will
        provide more understanding than what can be explained with words. See
        `window_ratio()` for more information about how to activate scale invariant
        drawing and why it is useful.
        """
        return self._instance.ratioTop

    ratio_top: float = property(
        fget=_get_ratio_top,
        doc="""Height of the top section of the window that does not fit the desired aspect
        ratio of a scale invariant Sketch.

        Underlying Processing field: Sketch.ratioTop

        Notes
        -----

        Height of the top section of the window that does not fit the desired aspect
        ratio of a scale invariant Sketch. This will always be greater than or equal to
        zero. Experimenting with the example and seeing how this value changes will
        provide more understanding than what can be explained with words. See
        `window_ratio()` for more information about how to activate scale invariant
        drawing and why it is useful.""",
    )

    def _get_rheight(self) -> int:
        """The height of the scale invariant display window.

        Underlying Processing field: Sketch.rheight

        Notes
        -----

        The height of the scale invariant display window. This will be the value of the
        `high` parameter used in the call to `window_ratio()` that activates scale
        invariant drawing. This field should only be used in a scale invariant Sketch.
        See `window_ratio()` for more information about how to activate this and why it
        is useful.
        """
        return self._instance.rheight

    rheight: int = property(
        fget=_get_rheight,
        doc="""The height of the scale invariant display window.

        Underlying Processing field: Sketch.rheight

        Notes
        -----

        The height of the scale invariant display window. This will be the value of the
        `high` parameter used in the call to `window_ratio()` that activates scale
        invariant drawing. This field should only be used in a scale invariant Sketch.
        See `window_ratio()` for more information about how to activate this and why it
        is useful.""",
    )

    def _get_rmouse_x(self) -> int:
        """The current horizontal coordinate of the mouse after activating scale invariant
        drawing.

        Underlying Processing field: Sketch.rmouseX

        Notes
        -----

        The current horizontal coordinate of the mouse after activating scale invariant
        drawing. See `window_ratio()` for more information about how to activate this
        and why it is useful.

        Note that py5 can only track the mouse position when the pointer is over the
        current window. The default value of `rmouse_x` is `0`, so `0` will be returned
        until the mouse moves in front of the Sketch window. (This typically happens
        when a Sketch is first run.)  Once the mouse moves away from the window,
        `rmouse_x` will continue to report its most recent position.
        """
        return self._instance.rmouseX

    rmouse_x: int = property(
        fget=_get_rmouse_x,
        doc="""The current horizontal coordinate of the mouse after activating scale invariant
        drawing.

        Underlying Processing field: Sketch.rmouseX

        Notes
        -----

        The current horizontal coordinate of the mouse after activating scale invariant
        drawing. See `window_ratio()` for more information about how to activate this
        and why it is useful.

        Note that py5 can only track the mouse position when the pointer is over the
        current window. The default value of `rmouse_x` is `0`, so `0` will be returned
        until the mouse moves in front of the Sketch window. (This typically happens
        when a Sketch is first run.)  Once the mouse moves away from the window,
        `rmouse_x` will continue to report its most recent position.""",
    )

    def _get_rmouse_y(self) -> int:
        """The current vertical coordinate of the mouse after activating scale invariant
        drawing.

        Underlying Processing field: Sketch.rmouseY

        Notes
        -----

        The current vertical coordinate of the mouse after activating scale invariant
        drawing. See `window_ratio()` for more information about how to activate this
        and why it is useful.

        Note that py5 can only track the mouse position when the pointer is over the
        current window. The default value of `rmouse_y` is `0`, so `0` will be returned
        until the mouse moves in front of the Sketch window. (This typically happens
        when a Sketch is first run.)  Once the mouse moves away from the window,
        `rmouse_y` will continue to report its most recent position.
        """
        return self._instance.rmouseY

    rmouse_y: int = property(
        fget=_get_rmouse_y,
        doc="""The current vertical coordinate of the mouse after activating scale invariant
        drawing.

        Underlying Processing field: Sketch.rmouseY

        Notes
        -----

        The current vertical coordinate of the mouse after activating scale invariant
        drawing. See `window_ratio()` for more information about how to activate this
        and why it is useful.

        Note that py5 can only track the mouse position when the pointer is over the
        current window. The default value of `rmouse_y` is `0`, so `0` will be returned
        until the mouse moves in front of the Sketch window. (This typically happens
        when a Sketch is first run.)  Once the mouse moves away from the window,
        `rmouse_y` will continue to report its most recent position.""",
    )

    def _get_rwidth(self) -> int:
        """The width of the scale invariant display window.

        Underlying Processing field: Sketch.rwidth

        Notes
        -----

        The width of the scale invariant display window. This will be the value of the
        `wide` parameter used in the call to `window_ratio()` that activates scale
        invariant drawing. This field should only be used in a scale invariant Sketch.
        See `window_ratio()` for more information about how to activate this and why it
        is useful.
        """
        return self._instance.rwidth

    rwidth: int = property(
        fget=_get_rwidth,
        doc="""The width of the scale invariant display window.

        Underlying Processing field: Sketch.rwidth

        Notes
        -----

        The width of the scale invariant display window. This will be the value of the
        `wide` parameter used in the call to `window_ratio()` that activates scale
        invariant drawing. This field should only be used in a scale invariant Sketch.
        See `window_ratio()` for more information about how to activate this and why it
        is useful.""",
    )

    def _get_width(self) -> int:
        """Variable that stores the width of the display window.

        Underlying Processing field: PApplet.width

        Notes
        -----

        Variable that stores the width of the display window. This value is set by the
        first parameter of the `size()` function. For example, the function call
        `size(320, 240)` sets the `width` variable to the value 320. The value of
        `width` defaults to 100 if `size()` is not used in a program.
        """
        return self._instance.width

    width: int = property(
        fget=_get_width,
        doc="""Variable that stores the width of the display window.

        Underlying Processing field: PApplet.width

        Notes
        -----

        Variable that stores the width of the display window. This value is set by the
        first parameter of the `size()` function. For example, the function call
        `size(320, 240)` sets the `width` variable to the value 320. The value of
        `width` defaults to 100 if `size()` is not used in a program.""",
    )

    def _get_window_x(self) -> int:
        """The x-coordinate of the current window location.

        Underlying Processing field: Sketch.windowX

        Notes
        -----

        The x-coordinate of the current window location. The location is measured from
        the Sketch window's upper left corner.
        """
        return self._instance.windowX

    window_x: int = property(
        fget=_get_window_x,
        doc="""The x-coordinate of the current window location.

        Underlying Processing field: Sketch.windowX

        Notes
        -----

        The x-coordinate of the current window location. The location is measured from
        the Sketch window's upper left corner.""",
    )

    def _get_window_y(self) -> int:
        """The y-coordinate of the current window location.

        Underlying Processing field: Sketch.windowY

        Notes
        -----

        The y-coordinate of the current window location. The location is measured from
        the Sketch window's upper left corner.
        """
        return self._instance.windowY

    window_y: int = property(
        fget=_get_window_y,
        doc="""The y-coordinate of the current window location.

        Underlying Processing field: Sketch.windowY

        Notes
        -----

        The y-coordinate of the current window location. The location is measured from
        the Sketch window's upper left corner.""",
    )

    @_convert_hex_color()
    def alpha(self, rgb: int, /) -> float:
        """Extracts the alpha value from a color, scaled to match current `color_mode()`.

        Underlying Processing method: PApplet.alpha

        Parameters
        ----------

        rgb: int
            any value of the color datatype

        Notes
        -----

        Extracts the alpha value from a color, scaled to match current `color_mode()`.

        The `alpha()` function is easy to use and understand, but it is slower than a
        technique called bit shifting. When working in `color_mode(RGB, 255)`, you can
        achieve the same results as `alpha()` but with greater speed by using the right
        shift operator (`>>`) with a bit mask. For example, `alpha(c)` and `c >> 24 &
        0xFF` both extract the alpha value from a color variable `c` but the later is
        faster.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        return self._instance.alpha(rgb)

    @overload
    def ambient(self, gray: float, /) -> None:
        """Sets the ambient reflectance for shapes drawn to the screen.

        Underlying Processing method: PApplet.ambient

        Methods
        -------

        You can use any of the following signatures:

         * ambient(gray: float, /) -> None
         * ambient(rgb: int, /) -> None
         * ambient(v1: float, v2: float, v3: float, /) -> None

        Parameters
        ----------

        gray: float
            number specifying value between white and black

        rgb: int
            any value of the color datatype

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the ambient reflectance for shapes drawn to the screen. This is combined
        with the ambient light component of the environment. The color components set
        through the parameters define the reflectance. For example in the default color
        mode, setting `ambient(255, 127, 0)`, would cause all the red light to reflect
        and half of the green light to reflect. Use in combination with `emissive()`,
        `specular()`, and `shininess()` to set the material properties of shapes.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def ambient(self, v1: float, v2: float, v3: float, /) -> None:
        """Sets the ambient reflectance for shapes drawn to the screen.

        Underlying Processing method: PApplet.ambient

        Methods
        -------

        You can use any of the following signatures:

         * ambient(gray: float, /) -> None
         * ambient(rgb: int, /) -> None
         * ambient(v1: float, v2: float, v3: float, /) -> None

        Parameters
        ----------

        gray: float
            number specifying value between white and black

        rgb: int
            any value of the color datatype

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the ambient reflectance for shapes drawn to the screen. This is combined
        with the ambient light component of the environment. The color components set
        through the parameters define the reflectance. For example in the default color
        mode, setting `ambient(255, 127, 0)`, would cause all the red light to reflect
        and half of the green light to reflect. Use in combination with `emissive()`,
        `specular()`, and `shininess()` to set the material properties of shapes.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def ambient(self, rgb: int, /) -> None:
        """Sets the ambient reflectance for shapes drawn to the screen.

        Underlying Processing method: PApplet.ambient

        Methods
        -------

        You can use any of the following signatures:

         * ambient(gray: float, /) -> None
         * ambient(rgb: int, /) -> None
         * ambient(v1: float, v2: float, v3: float, /) -> None

        Parameters
        ----------

        gray: float
            number specifying value between white and black

        rgb: int
            any value of the color datatype

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the ambient reflectance for shapes drawn to the screen. This is combined
        with the ambient light component of the environment. The color components set
        through the parameters define the reflectance. For example in the default color
        mode, setting `ambient(255, 127, 0)`, would cause all the red light to reflect
        and half of the green light to reflect. Use in combination with `emissive()`,
        `specular()`, and `shininess()` to set the material properties of shapes.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @_convert_hex_color()
    def ambient(self, *args):
        """Sets the ambient reflectance for shapes drawn to the screen.

        Underlying Processing method: PApplet.ambient

        Methods
        -------

        You can use any of the following signatures:

         * ambient(gray: float, /) -> None
         * ambient(rgb: int, /) -> None
         * ambient(v1: float, v2: float, v3: float, /) -> None

        Parameters
        ----------

        gray: float
            number specifying value between white and black

        rgb: int
            any value of the color datatype

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the ambient reflectance for shapes drawn to the screen. This is combined
        with the ambient light component of the environment. The color components set
        through the parameters define the reflectance. For example in the default color
        mode, setting `ambient(255, 127, 0)`, would cause all the red light to reflect
        and half of the green light to reflect. Use in combination with `emissive()`,
        `specular()`, and `shininess()` to set the material properties of shapes.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        return self._instance.ambient(*args)

    @overload
    def ambient_light(self, v1: float, v2: float, v3: float, /) -> None:
        """Adds an ambient light.

        Underlying Processing method: PApplet.ambientLight

        Methods
        -------

        You can use any of the following signatures:

         * ambient_light(v1: float, v2: float, v3: float, /) -> None
         * ambient_light(v1: float, v2: float, v3: float, x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        x: float
            x-coordinate of the light

        y: float
            y-coordinate of the light

        z: float
            z-coordinate of the light

        Notes
        -----

        Adds an ambient light. Ambient light doesn't come from a specific direction, the
        rays of light have bounced around so much that objects are evenly lit from all
        sides. Ambient lights are almost always used in combination with other types of
        lights. Lights need to be included in the `draw()` to remain persistent in a
        looping program. Placing them in the `setup()` of a looping program will cause
        them to only have an effect the first time through the loop. The `v1`, `v2`, and
        `v3` parameters are interpreted as either `RGB` or `HSB` values, depending on
        the current color mode.
        """
        pass

    @overload
    def ambient_light(
        self, v1: float, v2: float, v3: float, x: float, y: float, z: float, /
    ) -> None:
        """Adds an ambient light.

        Underlying Processing method: PApplet.ambientLight

        Methods
        -------

        You can use any of the following signatures:

         * ambient_light(v1: float, v2: float, v3: float, /) -> None
         * ambient_light(v1: float, v2: float, v3: float, x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        x: float
            x-coordinate of the light

        y: float
            y-coordinate of the light

        z: float
            z-coordinate of the light

        Notes
        -----

        Adds an ambient light. Ambient light doesn't come from a specific direction, the
        rays of light have bounced around so much that objects are evenly lit from all
        sides. Ambient lights are almost always used in combination with other types of
        lights. Lights need to be included in the `draw()` to remain persistent in a
        looping program. Placing them in the `setup()` of a looping program will cause
        them to only have an effect the first time through the loop. The `v1`, `v2`, and
        `v3` parameters are interpreted as either `RGB` or `HSB` values, depending on
        the current color mode.
        """
        pass

    def ambient_light(self, *args):
        """Adds an ambient light.

        Underlying Processing method: PApplet.ambientLight

        Methods
        -------

        You can use any of the following signatures:

         * ambient_light(v1: float, v2: float, v3: float, /) -> None
         * ambient_light(v1: float, v2: float, v3: float, x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        x: float
            x-coordinate of the light

        y: float
            y-coordinate of the light

        z: float
            z-coordinate of the light

        Notes
        -----

        Adds an ambient light. Ambient light doesn't come from a specific direction, the
        rays of light have bounced around so much that objects are evenly lit from all
        sides. Ambient lights are almost always used in combination with other types of
        lights. Lights need to be included in the `draw()` to remain persistent in a
        looping program. Placing them in the `setup()` of a looping program will cause
        them to only have an effect the first time through the loop. The `v1`, `v2`, and
        `v3` parameters are interpreted as either `RGB` or `HSB` values, depending on
        the current color mode.
        """
        return self._instance.ambientLight(*args)

    @overload
    def apply_matrix(
        self, n00: float, n01: float, n02: float, n10: float, n11: float, n12: float, /
    ) -> None:
        """Multiplies the current matrix by the one specified through the parameters.

        Underlying Processing method: PApplet.applyMatrix

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

        Multiplies the current matrix by the one specified through the parameters. This
        is very slow because it will try to calculate the inverse of the transform, so
        avoid it whenever possible. The equivalent function in OpenGL is
        `gl_mult_matrix()`.
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
        """Multiplies the current matrix by the one specified through the parameters.

        Underlying Processing method: PApplet.applyMatrix

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

        Multiplies the current matrix by the one specified through the parameters. This
        is very slow because it will try to calculate the inverse of the transform, so
        avoid it whenever possible. The equivalent function in OpenGL is
        `gl_mult_matrix()`.
        """
        pass

    @overload
    def apply_matrix(self, source: npt.NDArray[np.floating], /) -> None:
        """Multiplies the current matrix by the one specified through the parameters.

        Underlying Processing method: PApplet.applyMatrix

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

        Multiplies the current matrix by the one specified through the parameters. This
        is very slow because it will try to calculate the inverse of the transform, so
        avoid it whenever possible. The equivalent function in OpenGL is
        `gl_mult_matrix()`.
        """
        pass

    def apply_matrix(self, *args):
        """Multiplies the current matrix by the one specified through the parameters.

        Underlying Processing method: PApplet.applyMatrix

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

        Multiplies the current matrix by the one specified through the parameters. This
        is very slow because it will try to calculate the inverse of the transform, so
        avoid it whenever possible. The equivalent function in OpenGL is
        `gl_mult_matrix()`.
        """
        return self._instance.applyMatrix(*args)

    @overload
    def arc(
        self, a: float, b: float, c: float, d: float, start: float, stop: float, /
    ) -> None:
        """Draws an arc to the screen.

        Underlying Processing method: PApplet.arc

        Methods
        -------

        You can use any of the following signatures:

         * arc(a: float, b: float, c: float, d: float, start: float, stop: float, /) -> None
         * arc(a: float, b: float, c: float, d: float, start: float, stop: float, mode: int, /) -> None

        Parameters
        ----------

        a: float
            x-coordinate of the arc's ellipse

        b: float
            y-coordinate of the arc's ellipse

        c: float
            width of the arc's ellipse by default

        d: float
            height of the arc's ellipse by default

        mode: int
            arc drawing mode

        start: float
            angle to start the arc, specified in radians

        stop: float
            angle to stop the arc, specified in radians

        Notes
        -----

        Draws an arc to the screen. Arcs are drawn along the outer edge of an ellipse
        defined by the `a`, `b`, `c`, and `d` parameters. The origin of the arc's
        ellipse may be changed with the `ellipse_mode()` function. Use the `start` and
        `stop` parameters to specify the angles (in radians) at which to draw the arc.
        The start/stop values must be in clockwise order.

        There are three ways to draw an arc; the rendering technique used is defined by
        the optional seventh parameter. The three options, depicted in the examples, are
        `PIE`, `OPEN`, and `CHORD`. The default mode is the `OPEN` stroke with a `PIE`
        fill.

        In some cases, the `arc()` function isn't accurate enough for smooth drawing.
        For example, the shape may jitter on screen when rotating slowly. If you're
        having an issue with how arcs are rendered, you'll need to draw the arc yourself
        with `begin_shape()` & `end_shape()` or a `Py5Shape`.
        """
        pass

    @overload
    def arc(
        self,
        a: float,
        b: float,
        c: float,
        d: float,
        start: float,
        stop: float,
        mode: int,
        /,
    ) -> None:
        """Draws an arc to the screen.

        Underlying Processing method: PApplet.arc

        Methods
        -------

        You can use any of the following signatures:

         * arc(a: float, b: float, c: float, d: float, start: float, stop: float, /) -> None
         * arc(a: float, b: float, c: float, d: float, start: float, stop: float, mode: int, /) -> None

        Parameters
        ----------

        a: float
            x-coordinate of the arc's ellipse

        b: float
            y-coordinate of the arc's ellipse

        c: float
            width of the arc's ellipse by default

        d: float
            height of the arc's ellipse by default

        mode: int
            arc drawing mode

        start: float
            angle to start the arc, specified in radians

        stop: float
            angle to stop the arc, specified in radians

        Notes
        -----

        Draws an arc to the screen. Arcs are drawn along the outer edge of an ellipse
        defined by the `a`, `b`, `c`, and `d` parameters. The origin of the arc's
        ellipse may be changed with the `ellipse_mode()` function. Use the `start` and
        `stop` parameters to specify the angles (in radians) at which to draw the arc.
        The start/stop values must be in clockwise order.

        There are three ways to draw an arc; the rendering technique used is defined by
        the optional seventh parameter. The three options, depicted in the examples, are
        `PIE`, `OPEN`, and `CHORD`. The default mode is the `OPEN` stroke with a `PIE`
        fill.

        In some cases, the `arc()` function isn't accurate enough for smooth drawing.
        For example, the shape may jitter on screen when rotating slowly. If you're
        having an issue with how arcs are rendered, you'll need to draw the arc yourself
        with `begin_shape()` & `end_shape()` or a `Py5Shape`.
        """
        pass

    def arc(self, *args):
        """Draws an arc to the screen.

        Underlying Processing method: PApplet.arc

        Methods
        -------

        You can use any of the following signatures:

         * arc(a: float, b: float, c: float, d: float, start: float, stop: float, /) -> None
         * arc(a: float, b: float, c: float, d: float, start: float, stop: float, mode: int, /) -> None

        Parameters
        ----------

        a: float
            x-coordinate of the arc's ellipse

        b: float
            y-coordinate of the arc's ellipse

        c: float
            width of the arc's ellipse by default

        d: float
            height of the arc's ellipse by default

        mode: int
            arc drawing mode

        start: float
            angle to start the arc, specified in radians

        stop: float
            angle to stop the arc, specified in radians

        Notes
        -----

        Draws an arc to the screen. Arcs are drawn along the outer edge of an ellipse
        defined by the `a`, `b`, `c`, and `d` parameters. The origin of the arc's
        ellipse may be changed with the `ellipse_mode()` function. Use the `start` and
        `stop` parameters to specify the angles (in radians) at which to draw the arc.
        The start/stop values must be in clockwise order.

        There are three ways to draw an arc; the rendering technique used is defined by
        the optional seventh parameter. The three options, depicted in the examples, are
        `PIE`, `OPEN`, and `CHORD`. The default mode is the `OPEN` stroke with a `PIE`
        fill.

        In some cases, the `arc()` function isn't accurate enough for smooth drawing.
        For example, the shape may jitter on screen when rotating slowly. If you're
        having an issue with how arcs are rendered, you'll need to draw the arc yourself
        with `begin_shape()` & `end_shape()` or a `Py5Shape`.
        """
        return self._instance.arc(*args)

    @overload
    def background(self, gray: float, /) -> None:
        """The `background()` function sets the color used for the background of the py5
        window.

        Underlying Processing method: PApplet.background

        Methods
        -------

        You can use any of the following signatures:

         * background(gray: float, /) -> None
         * background(gray: float, alpha: float, /) -> None
         * background(image: Py5Image, /) -> None
         * background(rgb: int, /) -> None
         * background(rgb: int, alpha: float, /) -> None
         * background(v1: float, v2: float, v3: float, /) -> None
         * background(v1: float, v2: float, v3: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the background

        gray: float
            specifies a value between white and black

        image: Py5Image
            Py5Image to set as background (must be same size as the Sketch window)

        rgb: int
            any value of the color datatype

        v1: float
            red or hue value (depending on the current color mode)

        v2: float
            green or saturation value (depending on the current color mode)

        v3: float
            blue or brightness value (depending on the current color mode)

        Notes
        -----

        The `background()` function sets the color used for the background of the py5
        window. The default background is light gray. This function is typically used
        within `draw()` to clear the display window at the beginning of each frame, but
        it can be used inside `setup()` to set the background on the first frame of
        animation or if the backgound need only be set once.

        An image can also be used as the background for a Sketch, although the image's
        width and height must match that of the Sketch window. Images used with
        `background()` will ignore the current `tint()` setting. To resize an image to
        the size of the Sketch window, use `image.resize(width, height)`.

        It is not possible to use the transparency `alpha` parameter with background
        colors on the main drawing surface. It can only be used along with a
        `Py5Graphics` object and `create_graphics()`.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def background(self, gray: float, alpha: float, /) -> None:
        """The `background()` function sets the color used for the background of the py5
        window.

        Underlying Processing method: PApplet.background

        Methods
        -------

        You can use any of the following signatures:

         * background(gray: float, /) -> None
         * background(gray: float, alpha: float, /) -> None
         * background(image: Py5Image, /) -> None
         * background(rgb: int, /) -> None
         * background(rgb: int, alpha: float, /) -> None
         * background(v1: float, v2: float, v3: float, /) -> None
         * background(v1: float, v2: float, v3: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the background

        gray: float
            specifies a value between white and black

        image: Py5Image
            Py5Image to set as background (must be same size as the Sketch window)

        rgb: int
            any value of the color datatype

        v1: float
            red or hue value (depending on the current color mode)

        v2: float
            green or saturation value (depending on the current color mode)

        v3: float
            blue or brightness value (depending on the current color mode)

        Notes
        -----

        The `background()` function sets the color used for the background of the py5
        window. The default background is light gray. This function is typically used
        within `draw()` to clear the display window at the beginning of each frame, but
        it can be used inside `setup()` to set the background on the first frame of
        animation or if the backgound need only be set once.

        An image can also be used as the background for a Sketch, although the image's
        width and height must match that of the Sketch window. Images used with
        `background()` will ignore the current `tint()` setting. To resize an image to
        the size of the Sketch window, use `image.resize(width, height)`.

        It is not possible to use the transparency `alpha` parameter with background
        colors on the main drawing surface. It can only be used along with a
        `Py5Graphics` object and `create_graphics()`.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def background(self, v1: float, v2: float, v3: float, /) -> None:
        """The `background()` function sets the color used for the background of the py5
        window.

        Underlying Processing method: PApplet.background

        Methods
        -------

        You can use any of the following signatures:

         * background(gray: float, /) -> None
         * background(gray: float, alpha: float, /) -> None
         * background(image: Py5Image, /) -> None
         * background(rgb: int, /) -> None
         * background(rgb: int, alpha: float, /) -> None
         * background(v1: float, v2: float, v3: float, /) -> None
         * background(v1: float, v2: float, v3: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the background

        gray: float
            specifies a value between white and black

        image: Py5Image
            Py5Image to set as background (must be same size as the Sketch window)

        rgb: int
            any value of the color datatype

        v1: float
            red or hue value (depending on the current color mode)

        v2: float
            green or saturation value (depending on the current color mode)

        v3: float
            blue or brightness value (depending on the current color mode)

        Notes
        -----

        The `background()` function sets the color used for the background of the py5
        window. The default background is light gray. This function is typically used
        within `draw()` to clear the display window at the beginning of each frame, but
        it can be used inside `setup()` to set the background on the first frame of
        animation or if the backgound need only be set once.

        An image can also be used as the background for a Sketch, although the image's
        width and height must match that of the Sketch window. Images used with
        `background()` will ignore the current `tint()` setting. To resize an image to
        the size of the Sketch window, use `image.resize(width, height)`.

        It is not possible to use the transparency `alpha` parameter with background
        colors on the main drawing surface. It can only be used along with a
        `Py5Graphics` object and `create_graphics()`.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def background(self, v1: float, v2: float, v3: float, alpha: float, /) -> None:
        """The `background()` function sets the color used for the background of the py5
        window.

        Underlying Processing method: PApplet.background

        Methods
        -------

        You can use any of the following signatures:

         * background(gray: float, /) -> None
         * background(gray: float, alpha: float, /) -> None
         * background(image: Py5Image, /) -> None
         * background(rgb: int, /) -> None
         * background(rgb: int, alpha: float, /) -> None
         * background(v1: float, v2: float, v3: float, /) -> None
         * background(v1: float, v2: float, v3: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the background

        gray: float
            specifies a value between white and black

        image: Py5Image
            Py5Image to set as background (must be same size as the Sketch window)

        rgb: int
            any value of the color datatype

        v1: float
            red or hue value (depending on the current color mode)

        v2: float
            green or saturation value (depending on the current color mode)

        v3: float
            blue or brightness value (depending on the current color mode)

        Notes
        -----

        The `background()` function sets the color used for the background of the py5
        window. The default background is light gray. This function is typically used
        within `draw()` to clear the display window at the beginning of each frame, but
        it can be used inside `setup()` to set the background on the first frame of
        animation or if the backgound need only be set once.

        An image can also be used as the background for a Sketch, although the image's
        width and height must match that of the Sketch window. Images used with
        `background()` will ignore the current `tint()` setting. To resize an image to
        the size of the Sketch window, use `image.resize(width, height)`.

        It is not possible to use the transparency `alpha` parameter with background
        colors on the main drawing surface. It can only be used along with a
        `Py5Graphics` object and `create_graphics()`.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def background(self, rgb: int, /) -> None:
        """The `background()` function sets the color used for the background of the py5
        window.

        Underlying Processing method: PApplet.background

        Methods
        -------

        You can use any of the following signatures:

         * background(gray: float, /) -> None
         * background(gray: float, alpha: float, /) -> None
         * background(image: Py5Image, /) -> None
         * background(rgb: int, /) -> None
         * background(rgb: int, alpha: float, /) -> None
         * background(v1: float, v2: float, v3: float, /) -> None
         * background(v1: float, v2: float, v3: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the background

        gray: float
            specifies a value between white and black

        image: Py5Image
            Py5Image to set as background (must be same size as the Sketch window)

        rgb: int
            any value of the color datatype

        v1: float
            red or hue value (depending on the current color mode)

        v2: float
            green or saturation value (depending on the current color mode)

        v3: float
            blue or brightness value (depending on the current color mode)

        Notes
        -----

        The `background()` function sets the color used for the background of the py5
        window. The default background is light gray. This function is typically used
        within `draw()` to clear the display window at the beginning of each frame, but
        it can be used inside `setup()` to set the background on the first frame of
        animation or if the backgound need only be set once.

        An image can also be used as the background for a Sketch, although the image's
        width and height must match that of the Sketch window. Images used with
        `background()` will ignore the current `tint()` setting. To resize an image to
        the size of the Sketch window, use `image.resize(width, height)`.

        It is not possible to use the transparency `alpha` parameter with background
        colors on the main drawing surface. It can only be used along with a
        `Py5Graphics` object and `create_graphics()`.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def background(self, rgb: int, alpha: float, /) -> None:
        """The `background()` function sets the color used for the background of the py5
        window.

        Underlying Processing method: PApplet.background

        Methods
        -------

        You can use any of the following signatures:

         * background(gray: float, /) -> None
         * background(gray: float, alpha: float, /) -> None
         * background(image: Py5Image, /) -> None
         * background(rgb: int, /) -> None
         * background(rgb: int, alpha: float, /) -> None
         * background(v1: float, v2: float, v3: float, /) -> None
         * background(v1: float, v2: float, v3: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the background

        gray: float
            specifies a value between white and black

        image: Py5Image
            Py5Image to set as background (must be same size as the Sketch window)

        rgb: int
            any value of the color datatype

        v1: float
            red or hue value (depending on the current color mode)

        v2: float
            green or saturation value (depending on the current color mode)

        v3: float
            blue or brightness value (depending on the current color mode)

        Notes
        -----

        The `background()` function sets the color used for the background of the py5
        window. The default background is light gray. This function is typically used
        within `draw()` to clear the display window at the beginning of each frame, but
        it can be used inside `setup()` to set the background on the first frame of
        animation or if the backgound need only be set once.

        An image can also be used as the background for a Sketch, although the image's
        width and height must match that of the Sketch window. Images used with
        `background()` will ignore the current `tint()` setting. To resize an image to
        the size of the Sketch window, use `image.resize(width, height)`.

        It is not possible to use the transparency `alpha` parameter with background
        colors on the main drawing surface. It can only be used along with a
        `Py5Graphics` object and `create_graphics()`.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def background(self, image: Py5Image, /) -> None:
        """The `background()` function sets the color used for the background of the py5
        window.

        Underlying Processing method: PApplet.background

        Methods
        -------

        You can use any of the following signatures:

         * background(gray: float, /) -> None
         * background(gray: float, alpha: float, /) -> None
         * background(image: Py5Image, /) -> None
         * background(rgb: int, /) -> None
         * background(rgb: int, alpha: float, /) -> None
         * background(v1: float, v2: float, v3: float, /) -> None
         * background(v1: float, v2: float, v3: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the background

        gray: float
            specifies a value between white and black

        image: Py5Image
            Py5Image to set as background (must be same size as the Sketch window)

        rgb: int
            any value of the color datatype

        v1: float
            red or hue value (depending on the current color mode)

        v2: float
            green or saturation value (depending on the current color mode)

        v3: float
            blue or brightness value (depending on the current color mode)

        Notes
        -----

        The `background()` function sets the color used for the background of the py5
        window. The default background is light gray. This function is typically used
        within `draw()` to clear the display window at the beginning of each frame, but
        it can be used inside `setup()` to set the background on the first frame of
        animation or if the backgound need only be set once.

        An image can also be used as the background for a Sketch, although the image's
        width and height must match that of the Sketch window. Images used with
        `background()` will ignore the current `tint()` setting. To resize an image to
        the size of the Sketch window, use `image.resize(width, height)`.

        It is not possible to use the transparency `alpha` parameter with background
        colors on the main drawing surface. It can only be used along with a
        `Py5Graphics` object and `create_graphics()`.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @_auto_convert_to_py5image(0)
    @_convert_hex_color()
    def background(self, *args):
        """The `background()` function sets the color used for the background of the py5
        window.

        Underlying Processing method: PApplet.background

        Methods
        -------

        You can use any of the following signatures:

         * background(gray: float, /) -> None
         * background(gray: float, alpha: float, /) -> None
         * background(image: Py5Image, /) -> None
         * background(rgb: int, /) -> None
         * background(rgb: int, alpha: float, /) -> None
         * background(v1: float, v2: float, v3: float, /) -> None
         * background(v1: float, v2: float, v3: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the background

        gray: float
            specifies a value between white and black

        image: Py5Image
            Py5Image to set as background (must be same size as the Sketch window)

        rgb: int
            any value of the color datatype

        v1: float
            red or hue value (depending on the current color mode)

        v2: float
            green or saturation value (depending on the current color mode)

        v3: float
            blue or brightness value (depending on the current color mode)

        Notes
        -----

        The `background()` function sets the color used for the background of the py5
        window. The default background is light gray. This function is typically used
        within `draw()` to clear the display window at the beginning of each frame, but
        it can be used inside `setup()` to set the background on the first frame of
        animation or if the backgound need only be set once.

        An image can also be used as the background for a Sketch, although the image's
        width and height must match that of the Sketch window. Images used with
        `background()` will ignore the current `tint()` setting. To resize an image to
        the size of the Sketch window, use `image.resize(width, height)`.

        It is not possible to use the transparency `alpha` parameter with background
        colors on the main drawing surface. It can only be used along with a
        `Py5Graphics` object and `create_graphics()`.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        return self._instance.background(*args)

    @_context_wrapper("end_camera")
    def begin_camera(self) -> None:
        """The `begin_camera()` and `end_camera()` functions enable advanced customization
        of the camera space.

        Underlying Processing method: PApplet.beginCamera

        Notes
        -----

        The `begin_camera()` and `end_camera()` functions enable advanced customization
        of the camera space. The functions are useful if you want to more control over
        camera movement, however for most users, the `camera()` function will be
        sufficient. The camera functions will replace any transformations (such as
        `rotate()` or `translate()`) that occur before them in `draw()`, but they will
        not automatically replace the camera transform itself. For this reason, camera
        functions should be placed at the beginning of `draw()` (so that transformations
        happen afterwards), and the `camera()` function can be used after
        `begin_camera()` if you want to reset the camera before applying
        transformations.

        This function sets the matrix mode to the camera matrix so calls such as
        `translate()`, `rotate()`, `apply_matrix()` and `reset_matrix()` affect the
        camera. `begin_camera()` should always be used with a following `end_camera()`
        and pairs of `begin_camera()` and `end_camera()` cannot be nested.

        This method can be used as a context manager to ensure that `end_camera()`
        always gets called, as shown in the last example.
        """
        return self._instance.beginCamera()

    @_context_wrapper("end_contour")
    def begin_contour(self) -> None:
        """Use the `begin_contour()` and `end_contour()` methods to create negative shapes
        within shapes such as the center of the letter 'O'.

        Underlying Processing method: PApplet.beginContour

        Notes
        -----

        Use the `begin_contour()` and `end_contour()` methods to create negative shapes
        within shapes such as the center of the letter 'O'. The `begin_contour()` method
        begins recording vertices for the shape and `end_contour()` stops recording. The
        vertices that define a negative shape must "wind" in the opposite direction from
        the exterior shape. First draw vertices for the exterior shape in clockwise
        order, then for internal shapes, draw vertices counterclockwise.

        These methods can only be used within a `begin_shape()` & `end_shape()` pair and
        transformations such as `translate()`, `rotate()`, and `scale()` do not work
        within a `begin_contour()` & `end_contour()` pair. It is also not possible to
        use other shapes, such as `ellipse()` or `rect()` within.

        This method can be used as a context manager to ensure that `end_contour()`
        always gets called, as shown in the second example.
        """
        return self._instance.beginContour()

    @overload
    def begin_raw(self, renderer: str, filename: str, /) -> Py5Graphics:
        """To create vectors from 3D data, use the `begin_raw()` and `end_raw()` commands.

        Underlying Processing method: PApplet.beginRaw

        Methods
        -------

        You can use any of the following signatures:

         * begin_raw(raw_graphics: Py5Graphics, /) -> None
         * begin_raw(renderer: str, filename: str, /) -> Py5Graphics

        Parameters
        ----------

        filename: str
            filename for output

        raw_graphics: Py5Graphics
            Py5Graphics object to apply draw commands to

        renderer: str
            for example, PDF or DXF

        Notes
        -----

        To create vectors from 3D data, use the `begin_raw()` and `end_raw()` commands.
        These commands will grab the shape data just before it is rendered to the
        screen. At this stage, your entire scene is nothing but a long list of
        individual lines and triangles. This means that a shape created with `sphere()`
        function will be made up of hundreds of triangles, rather than a single object.
        Or that a multi-segment line shape (such as a curve) will be rendered as
        individual segments.

        When using `begin_raw()` and `end_raw()`, it's possible to write to either a 2D
        or 3D renderer. For instance, `begin_raw()` with the `PDF` library will write
        the geometry as flattened triangles and lines, even if recording from the `P3D`
        renderer.

        If you want a background to show up in your files, use `rect(0, 0, width,
        height)` after setting the `fill()` to the background color. Otherwise the
        background will not be rendered to the file because the background is not a
        shape.

        This method can be used as a context manager to ensure that `end_raw()` always
        gets called, as shown in the last example.

        Using `hint(ENABLE_DEPTH_SORT)` can improve the appearance of 3D geometry drawn
        to 2D file formats.
        """
        pass

    @overload
    def begin_raw(self, raw_graphics: Py5Graphics, /) -> None:
        """To create vectors from 3D data, use the `begin_raw()` and `end_raw()` commands.

        Underlying Processing method: PApplet.beginRaw

        Methods
        -------

        You can use any of the following signatures:

         * begin_raw(raw_graphics: Py5Graphics, /) -> None
         * begin_raw(renderer: str, filename: str, /) -> Py5Graphics

        Parameters
        ----------

        filename: str
            filename for output

        raw_graphics: Py5Graphics
            Py5Graphics object to apply draw commands to

        renderer: str
            for example, PDF or DXF

        Notes
        -----

        To create vectors from 3D data, use the `begin_raw()` and `end_raw()` commands.
        These commands will grab the shape data just before it is rendered to the
        screen. At this stage, your entire scene is nothing but a long list of
        individual lines and triangles. This means that a shape created with `sphere()`
        function will be made up of hundreds of triangles, rather than a single object.
        Or that a multi-segment line shape (such as a curve) will be rendered as
        individual segments.

        When using `begin_raw()` and `end_raw()`, it's possible to write to either a 2D
        or 3D renderer. For instance, `begin_raw()` with the `PDF` library will write
        the geometry as flattened triangles and lines, even if recording from the `P3D`
        renderer.

        If you want a background to show up in your files, use `rect(0, 0, width,
        height)` after setting the `fill()` to the background color. Otherwise the
        background will not be rendered to the file because the background is not a
        shape.

        This method can be used as a context manager to ensure that `end_raw()` always
        gets called, as shown in the last example.

        Using `hint(ENABLE_DEPTH_SORT)` can improve the appearance of 3D geometry drawn
        to 2D file formats.
        """
        pass

    @_context_wrapper("end_raw")
    @_return_py5graphics
    def begin_raw(self, *args):
        """To create vectors from 3D data, use the `begin_raw()` and `end_raw()` commands.

        Underlying Processing method: PApplet.beginRaw

        Methods
        -------

        You can use any of the following signatures:

         * begin_raw(raw_graphics: Py5Graphics, /) -> None
         * begin_raw(renderer: str, filename: str, /) -> Py5Graphics

        Parameters
        ----------

        filename: str
            filename for output

        raw_graphics: Py5Graphics
            Py5Graphics object to apply draw commands to

        renderer: str
            for example, PDF or DXF

        Notes
        -----

        To create vectors from 3D data, use the `begin_raw()` and `end_raw()` commands.
        These commands will grab the shape data just before it is rendered to the
        screen. At this stage, your entire scene is nothing but a long list of
        individual lines and triangles. This means that a shape created with `sphere()`
        function will be made up of hundreds of triangles, rather than a single object.
        Or that a multi-segment line shape (such as a curve) will be rendered as
        individual segments.

        When using `begin_raw()` and `end_raw()`, it's possible to write to either a 2D
        or 3D renderer. For instance, `begin_raw()` with the `PDF` library will write
        the geometry as flattened triangles and lines, even if recording from the `P3D`
        renderer.

        If you want a background to show up in your files, use `rect(0, 0, width,
        height)` after setting the `fill()` to the background color. Otherwise the
        background will not be rendered to the file because the background is not a
        shape.

        This method can be used as a context manager to ensure that `end_raw()` always
        gets called, as shown in the last example.

        Using `hint(ENABLE_DEPTH_SORT)` can improve the appearance of 3D geometry drawn
        to 2D file formats.
        """
        return self._instance.beginRaw(*args)

    @overload
    def begin_record(self, renderer: str, filename: str, /) -> Py5Graphics:
        """Opens a new file and all subsequent drawing functions are echoed to this file as
        well as the display window.

        Underlying Processing method: PApplet.beginRecord

        Methods
        -------

        You can use any of the following signatures:

         * begin_record(recorder: Py5Graphics, /) -> None
         * begin_record(renderer: str, filename: str, /) -> Py5Graphics

        Parameters
        ----------

        filename: str
            filename for output

        recorder: Py5Graphics
            Py5Graphics object to record drawing commands to

        renderer: str
            PDF or SVG

        Notes
        -----

        Opens a new file and all subsequent drawing functions are echoed to this file as
        well as the display window. The `begin_record()` function requires two
        parameters, the first is the renderer and the second is the file name. This
        function is always used with `end_record()` to stop the recording process and
        close the file.

        Note that `begin_record()` will only pick up any settings that happen after it
        has been called. For instance, if you call `text_font()` before
        `begin_record()`, then that font will not be set for the file that you're
        recording to.

        `begin_record()` works only with the `PDF` and `SVG` renderers.

        This method can be used as a context manager to ensure that `end_record()`
        always gets called, as shown in the last example.
        """
        pass

    @overload
    def begin_record(self, recorder: Py5Graphics, /) -> None:
        """Opens a new file and all subsequent drawing functions are echoed to this file as
        well as the display window.

        Underlying Processing method: PApplet.beginRecord

        Methods
        -------

        You can use any of the following signatures:

         * begin_record(recorder: Py5Graphics, /) -> None
         * begin_record(renderer: str, filename: str, /) -> Py5Graphics

        Parameters
        ----------

        filename: str
            filename for output

        recorder: Py5Graphics
            Py5Graphics object to record drawing commands to

        renderer: str
            PDF or SVG

        Notes
        -----

        Opens a new file and all subsequent drawing functions are echoed to this file as
        well as the display window. The `begin_record()` function requires two
        parameters, the first is the renderer and the second is the file name. This
        function is always used with `end_record()` to stop the recording process and
        close the file.

        Note that `begin_record()` will only pick up any settings that happen after it
        has been called. For instance, if you call `text_font()` before
        `begin_record()`, then that font will not be set for the file that you're
        recording to.

        `begin_record()` works only with the `PDF` and `SVG` renderers.

        This method can be used as a context manager to ensure that `end_record()`
        always gets called, as shown in the last example.
        """
        pass

    @_context_wrapper("end_record")
    @_return_py5graphics
    def begin_record(self, *args):
        """Opens a new file and all subsequent drawing functions are echoed to this file as
        well as the display window.

        Underlying Processing method: PApplet.beginRecord

        Methods
        -------

        You can use any of the following signatures:

         * begin_record(recorder: Py5Graphics, /) -> None
         * begin_record(renderer: str, filename: str, /) -> Py5Graphics

        Parameters
        ----------

        filename: str
            filename for output

        recorder: Py5Graphics
            Py5Graphics object to record drawing commands to

        renderer: str
            PDF or SVG

        Notes
        -----

        Opens a new file and all subsequent drawing functions are echoed to this file as
        well as the display window. The `begin_record()` function requires two
        parameters, the first is the renderer and the second is the file name. This
        function is always used with `end_record()` to stop the recording process and
        close the file.

        Note that `begin_record()` will only pick up any settings that happen after it
        has been called. For instance, if you call `text_font()` before
        `begin_record()`, then that font will not be set for the file that you're
        recording to.

        `begin_record()` works only with the `PDF` and `SVG` renderers.

        This method can be used as a context manager to ensure that `end_record()`
        always gets called, as shown in the last example.
        """
        return self._instance.beginRecord(*args)

    @overload
    def begin_shape(self) -> None:
        """Using the `begin_shape()` and `end_shape()` functions allow creating more
        complex forms.

        Underlying Processing method: PApplet.beginShape

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

        Using the `begin_shape()` and `end_shape()` functions allow creating more
        complex forms. `begin_shape()` begins recording vertices for a shape and
        `end_shape()` stops recording. The value of the `kind` parameter tells it which
        types of shapes to create from the provided vertices. With no mode specified,
        the shape can be any irregular polygon. The parameters available for
        `begin_shape()` are `POINTS`, `LINES`, `TRIANGLES`, `TRIANGLE_FAN`,
        `TRIANGLE_STRIP`, `QUADS`, and `QUAD_STRIP`. After calling the `begin_shape()`
        function, a series of `vertex()` commands must follow. To stop drawing the
        shape, call `end_shape()`. The `vertex()` function with two parameters specifies
        a position in 2D and the `vertex()` function with three parameters specifies a
        position in 3D. Each shape will be outlined with the current stroke color and
        filled with the fill color.

        Transformations such as `translate()`, `rotate()`, and `scale()` do not work
        within `begin_shape()`. It is also not possible to use other shapes, such as
        `ellipse()` or `rect()` within `begin_shape()`.

        The `P2D` and `P3D` renderers allow `stroke()` and `fill()` to be altered on a
        per-vertex basis, but the default renderer does not. Settings such as
        `stroke_weight()`, `stroke_cap()`, and `stroke_join()` cannot be changed while
        inside a `begin_shape()` & `end_shape()` block with any renderer.

        This method can be used as a context manager to ensure that `end_shape()` always
        gets called, as shown in the last example. Use `begin_closed_shape()` to create
        a context manager that will pass the `CLOSE` parameter to `end_shape()`, closing
        the shape.
        """
        pass

    @overload
    def begin_shape(self, kind: int, /) -> None:
        """Using the `begin_shape()` and `end_shape()` functions allow creating more
        complex forms.

        Underlying Processing method: PApplet.beginShape

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

        Using the `begin_shape()` and `end_shape()` functions allow creating more
        complex forms. `begin_shape()` begins recording vertices for a shape and
        `end_shape()` stops recording. The value of the `kind` parameter tells it which
        types of shapes to create from the provided vertices. With no mode specified,
        the shape can be any irregular polygon. The parameters available for
        `begin_shape()` are `POINTS`, `LINES`, `TRIANGLES`, `TRIANGLE_FAN`,
        `TRIANGLE_STRIP`, `QUADS`, and `QUAD_STRIP`. After calling the `begin_shape()`
        function, a series of `vertex()` commands must follow. To stop drawing the
        shape, call `end_shape()`. The `vertex()` function with two parameters specifies
        a position in 2D and the `vertex()` function with three parameters specifies a
        position in 3D. Each shape will be outlined with the current stroke color and
        filled with the fill color.

        Transformations such as `translate()`, `rotate()`, and `scale()` do not work
        within `begin_shape()`. It is also not possible to use other shapes, such as
        `ellipse()` or `rect()` within `begin_shape()`.

        The `P2D` and `P3D` renderers allow `stroke()` and `fill()` to be altered on a
        per-vertex basis, but the default renderer does not. Settings such as
        `stroke_weight()`, `stroke_cap()`, and `stroke_join()` cannot be changed while
        inside a `begin_shape()` & `end_shape()` block with any renderer.

        This method can be used as a context manager to ensure that `end_shape()` always
        gets called, as shown in the last example. Use `begin_closed_shape()` to create
        a context manager that will pass the `CLOSE` parameter to `end_shape()`, closing
        the shape.
        """
        pass

    @_context_wrapper("end_shape")
    def begin_shape(self, *args):
        """Using the `begin_shape()` and `end_shape()` functions allow creating more
        complex forms.

        Underlying Processing method: PApplet.beginShape

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

        Using the `begin_shape()` and `end_shape()` functions allow creating more
        complex forms. `begin_shape()` begins recording vertices for a shape and
        `end_shape()` stops recording. The value of the `kind` parameter tells it which
        types of shapes to create from the provided vertices. With no mode specified,
        the shape can be any irregular polygon. The parameters available for
        `begin_shape()` are `POINTS`, `LINES`, `TRIANGLES`, `TRIANGLE_FAN`,
        `TRIANGLE_STRIP`, `QUADS`, and `QUAD_STRIP`. After calling the `begin_shape()`
        function, a series of `vertex()` commands must follow. To stop drawing the
        shape, call `end_shape()`. The `vertex()` function with two parameters specifies
        a position in 2D and the `vertex()` function with three parameters specifies a
        position in 3D. Each shape will be outlined with the current stroke color and
        filled with the fill color.

        Transformations such as `translate()`, `rotate()`, and `scale()` do not work
        within `begin_shape()`. It is also not possible to use other shapes, such as
        `ellipse()` or `rect()` within `begin_shape()`.

        The `P2D` and `P3D` renderers allow `stroke()` and `fill()` to be altered on a
        per-vertex basis, but the default renderer does not. Settings such as
        `stroke_weight()`, `stroke_cap()`, and `stroke_join()` cannot be changed while
        inside a `begin_shape()` & `end_shape()` block with any renderer.

        This method can be used as a context manager to ensure that `end_shape()` always
        gets called, as shown in the last example. Use `begin_closed_shape()` to create
        a context manager that will pass the `CLOSE` parameter to `end_shape()`, closing
        the shape.
        """
        return self._instance.beginShape(*args)

    @overload
    def begin_closed_shape(self) -> None:
        """This method is used to start a custom closed shape.

        Underlying Processing method: PApplet.beginShape

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

        This method is used to start a custom closed shape. This method should only be
        used as a context manager, as shown in the examples. When used as a context
        manager, this will ensure that `end_shape()` always gets called, just like when
        using `begin_shape()` as a context manager. The difference is that when exiting,
        the parameter `CLOSE` will be passed to `end_shape()`, connecting the last
        vertex to the first. This will close the shape. If this method were to be used
        not as a context manager, it won't be able to close the shape by making the call
        to `end_shape()`.
        """
        pass

    @overload
    def begin_closed_shape(self, kind: int, /) -> None:
        """This method is used to start a custom closed shape.

        Underlying Processing method: PApplet.beginShape

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

        This method is used to start a custom closed shape. This method should only be
        used as a context manager, as shown in the examples. When used as a context
        manager, this will ensure that `end_shape()` always gets called, just like when
        using `begin_shape()` as a context manager. The difference is that when exiting,
        the parameter `CLOSE` will be passed to `end_shape()`, connecting the last
        vertex to the first. This will close the shape. If this method were to be used
        not as a context manager, it won't be able to close the shape by making the call
        to `end_shape()`.
        """
        pass

    @_context_wrapper("end_shape", exit_attr_args=("CLOSE",))
    def begin_closed_shape(self, *args):
        """This method is used to start a custom closed shape.

        Underlying Processing method: PApplet.beginShape

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

        This method is used to start a custom closed shape. This method should only be
        used as a context manager, as shown in the examples. When used as a context
        manager, this will ensure that `end_shape()` always gets called, just like when
        using `begin_shape()` as a context manager. The difference is that when exiting,
        the parameter `CLOSE` will be passed to `end_shape()`, connecting the last
        vertex to the first. This will close the shape. If this method were to be used
        not as a context manager, it won't be able to close the shape by making the call
        to `end_shape()`.
        """
        return self._instance.beginShape(*args)

    @overload
    def bezier(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        x3: float,
        y3: float,
        x4: float,
        y4: float,
        /,
    ) -> None:
        """Draws a Bezier curve on the screen.

        Underlying Processing method: PApplet.bezier

        Methods
        -------

        You can use any of the following signatures:

         * bezier(x1: float, y1: float, x2: float, y2: float, x3: float, y3: float, x4: float, y4: float, /) -> None
         * bezier(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float, x3: float, y3: float, z3: float, x4: float, y4: float, z4: float, /) -> None

        Parameters
        ----------

        x1: float
            coordinates for the first anchor point

        x2: float
            coordinates for the first control point

        x3: float
            coordinates for the second control point

        x4: float
            coordinates for the second anchor point

        y1: float
            coordinates for the first anchor point

        y2: float
            coordinates for the first control point

        y3: float
            coordinates for the second control point

        y4: float
            coordinates for the second anchor point

        z1: float
            coordinates for the first anchor point

        z2: float
            coordinates for the first control point

        z3: float
            coordinates for the second control point

        z4: float
            coordinates for the second anchor point

        Notes
        -----

        Draws a Bezier curve on the screen. These curves are defined by a series of
        anchor and control points. The first two parameters specify the first anchor
        point and the last two parameters specify the other anchor point. The middle
        parameters specify the control points which define the shape of the curve.
        Bezier curves were developed by French engineer Pierre Bezier. Using the 3D
        version requires rendering with `P3D`.
        """
        pass

    @overload
    def bezier(
        self,
        x1: float,
        y1: float,
        z1: float,
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
        """Draws a Bezier curve on the screen.

        Underlying Processing method: PApplet.bezier

        Methods
        -------

        You can use any of the following signatures:

         * bezier(x1: float, y1: float, x2: float, y2: float, x3: float, y3: float, x4: float, y4: float, /) -> None
         * bezier(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float, x3: float, y3: float, z3: float, x4: float, y4: float, z4: float, /) -> None

        Parameters
        ----------

        x1: float
            coordinates for the first anchor point

        x2: float
            coordinates for the first control point

        x3: float
            coordinates for the second control point

        x4: float
            coordinates for the second anchor point

        y1: float
            coordinates for the first anchor point

        y2: float
            coordinates for the first control point

        y3: float
            coordinates for the second control point

        y4: float
            coordinates for the second anchor point

        z1: float
            coordinates for the first anchor point

        z2: float
            coordinates for the first control point

        z3: float
            coordinates for the second control point

        z4: float
            coordinates for the second anchor point

        Notes
        -----

        Draws a Bezier curve on the screen. These curves are defined by a series of
        anchor and control points. The first two parameters specify the first anchor
        point and the last two parameters specify the other anchor point. The middle
        parameters specify the control points which define the shape of the curve.
        Bezier curves were developed by French engineer Pierre Bezier. Using the 3D
        version requires rendering with `P3D`.
        """
        pass

    def bezier(self, *args):
        """Draws a Bezier curve on the screen.

        Underlying Processing method: PApplet.bezier

        Methods
        -------

        You can use any of the following signatures:

         * bezier(x1: float, y1: float, x2: float, y2: float, x3: float, y3: float, x4: float, y4: float, /) -> None
         * bezier(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float, x3: float, y3: float, z3: float, x4: float, y4: float, z4: float, /) -> None

        Parameters
        ----------

        x1: float
            coordinates for the first anchor point

        x2: float
            coordinates for the first control point

        x3: float
            coordinates for the second control point

        x4: float
            coordinates for the second anchor point

        y1: float
            coordinates for the first anchor point

        y2: float
            coordinates for the first control point

        y3: float
            coordinates for the second control point

        y4: float
            coordinates for the second anchor point

        z1: float
            coordinates for the first anchor point

        z2: float
            coordinates for the first control point

        z3: float
            coordinates for the second control point

        z4: float
            coordinates for the second anchor point

        Notes
        -----

        Draws a Bezier curve on the screen. These curves are defined by a series of
        anchor and control points. The first two parameters specify the first anchor
        point and the last two parameters specify the other anchor point. The middle
        parameters specify the control points which define the shape of the curve.
        Bezier curves were developed by French engineer Pierre Bezier. Using the 3D
        version requires rendering with `P3D`.
        """
        return self._instance.bezier(*args)

    def bezier_detail(self, detail: int, /) -> None:
        """Sets the resolution at which Beziers display.

        Underlying Processing method: PApplet.bezierDetail

        Parameters
        ----------

        detail: int
            resolution of the curves

        Notes
        -----

        Sets the resolution at which Beziers display. The default value is 20. This
        function is only useful when using the `P3D` renderer; the default `P2D`
        renderer does not use this information.
        """
        return self._instance.bezierDetail(detail)

    def bezier_point(
        self, a: float, b: float, c: float, d: float, t: float, /
    ) -> float:
        """Evaluates the Bezier at point t for points a, b, c, d.

        Underlying Processing method: PApplet.bezierPoint

        Parameters
        ----------

        a: float
            coordinate of first point on the curve

        b: float
            coordinate of first control point

        c: float
            coordinate of second control point

        d: float
            coordinate of second point on the curve

        t: float
            value between 0 and 1

        Notes
        -----

        Evaluates the Bezier at point t for points a, b, c, d. The parameter t varies
        between 0 and 1, a and d are points on the curve, and b and c are the control
        points. This can be done once with the x coordinates and a second time with the
        y coordinates to get the location of a bezier curve at t.
        """
        return self._instance.bezierPoint(a, b, c, d, t)

    def bezier_tangent(
        self, a: float, b: float, c: float, d: float, t: float, /
    ) -> float:
        """Calculates the tangent of a point on a Bezier curve.

        Underlying Processing method: PApplet.bezierTangent

        Parameters
        ----------

        a: float
            coordinate of first point on the curve

        b: float
            coordinate of first control point

        c: float
            coordinate of second control point

        d: float
            coordinate of second point on the curve

        t: float
            value between 0 and 1

        Notes
        -----

        Calculates the tangent of a point on a Bezier curve. There is a good definition
        of *tangent* on Wikipedia.
        """
        return self._instance.bezierTangent(a, b, c, d, t)

    @overload
    def bezier_vertex(
        self, x2: float, y2: float, x3: float, y3: float, x4: float, y4: float, /
    ) -> None:
        """Specifies vertex coordinates for Bezier curves.

        Underlying Processing method: PApplet.bezierVertex

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

        Specifies vertex coordinates for Bezier curves. Each call to `bezier_vertex()`
        defines the position of two control points and one anchor point of a Bezier
        curve, adding a new segment to a line or shape. The first time `bezier_vertex()`
        is used within a `begin_shape()` call, it must be prefaced with a call to
        `vertex()` to set the first anchor point. This function must be used between
        `begin_shape()` and `end_shape()` and only when there is no `MODE` parameter
        specified to `begin_shape()`. Using the 3D version requires rendering with
        `P3D`.
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
        """Specifies vertex coordinates for Bezier curves.

        Underlying Processing method: PApplet.bezierVertex

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

        Specifies vertex coordinates for Bezier curves. Each call to `bezier_vertex()`
        defines the position of two control points and one anchor point of a Bezier
        curve, adding a new segment to a line or shape. The first time `bezier_vertex()`
        is used within a `begin_shape()` call, it must be prefaced with a call to
        `vertex()` to set the first anchor point. This function must be used between
        `begin_shape()` and `end_shape()` and only when there is no `MODE` parameter
        specified to `begin_shape()`. Using the 3D version requires rendering with
        `P3D`.
        """
        pass

    def bezier_vertex(self, *args):
        """Specifies vertex coordinates for Bezier curves.

        Underlying Processing method: PApplet.bezierVertex

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

        Specifies vertex coordinates for Bezier curves. Each call to `bezier_vertex()`
        defines the position of two control points and one anchor point of a Bezier
        curve, adding a new segment to a line or shape. The first time `bezier_vertex()`
        is used within a `begin_shape()` call, it must be prefaced with a call to
        `vertex()` to set the first anchor point. This function must be used between
        `begin_shape()` and `end_shape()` and only when there is no `MODE` parameter
        specified to `begin_shape()`. Using the 3D version requires rendering with
        `P3D`.
        """
        return self._instance.bezierVertex(*args)

    @_generator_to_list
    def bezier_vertices(self, coordinates: Sequence[Sequence[float]], /) -> None:
        """Create a collection of bezier vertices.

        Parameters
        ----------

        coordinates: Sequence[Sequence[float]]
            2D array of bezier vertex coordinates with 6 or 9 columns for 2D or 3D points, respectively

        Notes
        -----

        Create a collection of bezier vertices. The purpose of this method is to provide
        an alternative to repeatedly calling `bezier_vertex()` in a loop. For a large
        number of bezier vertices, the performance of `bezier_vertices()` will be much
        faster.

        The `coordinates` parameter should be a numpy array with one row for each bezier
        vertex. The first few columns are for the first control point, the next few
        columns are for the second control point, and the final few columns are for the
        anchor point. There should be six or nine columns for 2D or 3D points,
        respectively.
        """
        return self._instance.bezierVertices(coordinates)

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
        """Blends a region of pixels from one image into another (or in itself again) with
        full alpha channel support.

        Underlying Processing method: PApplet.blend

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

        Blends a region of pixels from one image into another (or in itself again) with
        full alpha channel support. There is a choice of the following modes to blend
        the source pixels (A) with the ones of pixels in the destination image (B):

        * BLEND: linear interpolation of colors: `C = A*factor + B`
        * ADD: additive blending with white clip: `C = min(A*factor + B, 255)`
        * SUBTRACT: subtractive blending with black clip: `C = max(B - A*factor, 0)`
        * DARKEST: only the darkest color succeeds: `C = min(A*factor, B)`
        * LIGHTEST: only the lightest color succeeds: `C = max(A*factor, B)`
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
        """Blends a region of pixels from one image into another (or in itself again) with
        full alpha channel support.

        Underlying Processing method: PApplet.blend

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

        Blends a region of pixels from one image into another (or in itself again) with
        full alpha channel support. There is a choice of the following modes to blend
        the source pixels (A) with the ones of pixels in the destination image (B):

        * BLEND: linear interpolation of colors: `C = A*factor + B`
        * ADD: additive blending with white clip: `C = min(A*factor + B, 255)`
        * SUBTRACT: subtractive blending with black clip: `C = max(B - A*factor, 0)`
        * DARKEST: only the darkest color succeeds: `C = min(A*factor, B)`
        * LIGHTEST: only the lightest color succeeds: `C = max(A*factor, B)`
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

    @_auto_convert_to_py5image(0)
    def blend(self, *args):
        """Blends a region of pixels from one image into another (or in itself again) with
        full alpha channel support.

        Underlying Processing method: PApplet.blend

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

        Blends a region of pixels from one image into another (or in itself again) with
        full alpha channel support. There is a choice of the following modes to blend
        the source pixels (A) with the ones of pixels in the destination image (B):

        * BLEND: linear interpolation of colors: `C = A*factor + B`
        * ADD: additive blending with white clip: `C = min(A*factor + B, 255)`
        * SUBTRACT: subtractive blending with black clip: `C = max(B - A*factor, 0)`
        * DARKEST: only the darkest color succeeds: `C = min(A*factor, B)`
        * LIGHTEST: only the lightest color succeeds: `C = max(A*factor, B)`
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

    def blend_mode(self, mode: int, /) -> None:
        """Blends the pixels in the display window according to a defined mode.

        Underlying Processing method: PApplet.blendMode

        Parameters
        ----------

        mode: int
            the blending mode to use

        Notes
        -----

        Blends the pixels in the display window according to a defined mode. There is a
        choice of the following modes to blend the source pixels (A) with the ones of
        pixels already in the display window (B). Each pixel's final color is the result
        of applying one of the blend modes with each channel of (A) and (B)
        independently. The red channel is compared with red, green with green, and blue
        with blue.

        * BLEND: linear interpolation of colors: `C = A*factor + B`. This is the
        default.
        * ADD: additive blending with white clip: `C = min(A*factor + B, 255)`
        * SUBTRACT: subtractive blending with black clip: `C = max(B - A*factor, 0)`
        * DARKEST: only the darkest color succeeds: `C = min(A*factor, B)`
        * LIGHTEST: only the lightest color succeeds: `C = max(A*factor, B)`
        * DIFFERENCE: subtract colors from underlying image.
        * EXCLUSION: similar to DIFFERENCE, but less extreme.
        * MULTIPLY: multiply the colors, result will always be darker.
        * SCREEN: opposite multiply, uses inverse values of the colors.
        * REPLACE: the pixels entirely replace the others and don't utilize alpha
        (transparency) values

        We recommend using `blend_mode()` and not the previous `blend()` function.
        However, unlike `blend()`, the `blend_mode()` function does not support the
        following: `HARD_LIGHT`, `SOFT_LIGHT`, `OVERLAY`, `DODGE`, `BURN`. On older
        hardware, the `LIGHTEST`, `DARKEST`, and `DIFFERENCE` modes might not be
        available as well.
        """
        return self._instance.blendMode(mode)

    @_convert_hex_color()
    def blue(self, rgb: int, /) -> float:
        """Extracts the blue value from a color, scaled to match current `color_mode()`.

        Underlying Processing method: PApplet.blue

        Parameters
        ----------

        rgb: int
            any value of the color datatype

        Notes
        -----

        Extracts the blue value from a color, scaled to match current `color_mode()`.

        The `blue()` function is easy to use and understand, but it is slower than a
        technique called bit masking. When working in `color_mode(RGB, 255)`, you can
        achieve the same results as `blue()` but with greater speed by using a bit mask
        to remove the other color components. For example, `blue(c)` and `c & 0xFF` both
        extract the blue value from a color variable `c` but the later is faster.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        return self._instance.blue(rgb)

    @overload
    def box(self, size: float, /) -> None:
        """A box is an extruded rectangle.

        Underlying Processing method: PApplet.box

        Methods
        -------

        You can use any of the following signatures:

         * box(size: float, /) -> None
         * box(w: float, h: float, d: float, /) -> None

        Parameters
        ----------

        d: float
            dimension of the box in the z-dimension

        h: float
            dimension of the box in the y-dimension

        size: float
            dimension of the box in all dimensions (creates a cube)

        w: float
            dimension of the box in the x-dimension

        Notes
        -----

        A box is an extruded rectangle. A box with equal dimensions on all sides is a
        cube.
        """
        pass

    @overload
    def box(self, w: float, h: float, d: float, /) -> None:
        """A box is an extruded rectangle.

        Underlying Processing method: PApplet.box

        Methods
        -------

        You can use any of the following signatures:

         * box(size: float, /) -> None
         * box(w: float, h: float, d: float, /) -> None

        Parameters
        ----------

        d: float
            dimension of the box in the z-dimension

        h: float
            dimension of the box in the y-dimension

        size: float
            dimension of the box in all dimensions (creates a cube)

        w: float
            dimension of the box in the x-dimension

        Notes
        -----

        A box is an extruded rectangle. A box with equal dimensions on all sides is a
        cube.
        """
        pass

    def box(self, *args):
        """A box is an extruded rectangle.

        Underlying Processing method: PApplet.box

        Methods
        -------

        You can use any of the following signatures:

         * box(size: float, /) -> None
         * box(w: float, h: float, d: float, /) -> None

        Parameters
        ----------

        d: float
            dimension of the box in the z-dimension

        h: float
            dimension of the box in the y-dimension

        size: float
            dimension of the box in all dimensions (creates a cube)

        w: float
            dimension of the box in the x-dimension

        Notes
        -----

        A box is an extruded rectangle. A box with equal dimensions on all sides is a
        cube.
        """
        return self._instance.box(*args)

    @_convert_hex_color()
    def brightness(self, rgb: int, /) -> float:
        """Extracts the brightness value from a color.

        Underlying Processing method: PApplet.brightness

        Parameters
        ----------

        rgb: int
            any value of the color datatype

        Notes
        -----

        Extracts the brightness value from a color.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        return self._instance.brightness(rgb)

    @overload
    def camera(self) -> None:
        """Sets the position of the camera through setting the eye position, the center of
        the scene, and which axis is facing upward.

        Underlying Processing method: PApplet.camera

        Methods
        -------

        You can use any of the following signatures:

         * camera() -> None
         * camera(eye_x: float, eye_y: float, eye_z: float, center_x: float, center_y: float, center_z: float, up_x: float, up_y: float, up_z: float, /) -> None

        Parameters
        ----------

        center_x: float
            x-coordinate for the center of the scene

        center_y: float
            y-coordinate for the center of the scene

        center_z: float
            z-coordinate for the center of the scene

        eye_x: float
            x-coordinate for the eye

        eye_y: float
            y-coordinate for the eye

        eye_z: float
            z-coordinate for the eye

        up_x: float
            usually 0.0, 1.0, or -1.0

        up_y: float
            usually 0.0, 1.0, or -1.0

        up_z: float
            usually 0.0, 1.0, or -1.0

        Notes
        -----

        Sets the position of the camera through setting the eye position, the center of
        the scene, and which axis is facing upward. Moving the eye position and the
        direction it is pointing (the center of the scene) allows the images to be seen
        from different angles. The version without any parameters sets the camera to the
        default position, pointing to the center of the display window with the Y axis
        as up. The default values are `camera(width//2.0, height//2.0, (height//2.0) /
        tan(PI*30.0 / 180.0), width//2.0, height//2.0, 0, 0, 1, 0)`. This function is
        similar to `glu_look_at()` in OpenGL, but it first clears the current camera
        settings.
        """
        pass

    @overload
    def camera(
        self,
        eye_x: float,
        eye_y: float,
        eye_z: float,
        center_x: float,
        center_y: float,
        center_z: float,
        up_x: float,
        up_y: float,
        up_z: float,
        /,
    ) -> None:
        """Sets the position of the camera through setting the eye position, the center of
        the scene, and which axis is facing upward.

        Underlying Processing method: PApplet.camera

        Methods
        -------

        You can use any of the following signatures:

         * camera() -> None
         * camera(eye_x: float, eye_y: float, eye_z: float, center_x: float, center_y: float, center_z: float, up_x: float, up_y: float, up_z: float, /) -> None

        Parameters
        ----------

        center_x: float
            x-coordinate for the center of the scene

        center_y: float
            y-coordinate for the center of the scene

        center_z: float
            z-coordinate for the center of the scene

        eye_x: float
            x-coordinate for the eye

        eye_y: float
            y-coordinate for the eye

        eye_z: float
            z-coordinate for the eye

        up_x: float
            usually 0.0, 1.0, or -1.0

        up_y: float
            usually 0.0, 1.0, or -1.0

        up_z: float
            usually 0.0, 1.0, or -1.0

        Notes
        -----

        Sets the position of the camera through setting the eye position, the center of
        the scene, and which axis is facing upward. Moving the eye position and the
        direction it is pointing (the center of the scene) allows the images to be seen
        from different angles. The version without any parameters sets the camera to the
        default position, pointing to the center of the display window with the Y axis
        as up. The default values are `camera(width//2.0, height//2.0, (height//2.0) /
        tan(PI*30.0 / 180.0), width//2.0, height//2.0, 0, 0, 1, 0)`. This function is
        similar to `glu_look_at()` in OpenGL, but it first clears the current camera
        settings.
        """
        pass

    def camera(self, *args):
        """Sets the position of the camera through setting the eye position, the center of
        the scene, and which axis is facing upward.

        Underlying Processing method: PApplet.camera

        Methods
        -------

        You can use any of the following signatures:

         * camera() -> None
         * camera(eye_x: float, eye_y: float, eye_z: float, center_x: float, center_y: float, center_z: float, up_x: float, up_y: float, up_z: float, /) -> None

        Parameters
        ----------

        center_x: float
            x-coordinate for the center of the scene

        center_y: float
            y-coordinate for the center of the scene

        center_z: float
            z-coordinate for the center of the scene

        eye_x: float
            x-coordinate for the eye

        eye_y: float
            y-coordinate for the eye

        eye_z: float
            z-coordinate for the eye

        up_x: float
            usually 0.0, 1.0, or -1.0

        up_y: float
            usually 0.0, 1.0, or -1.0

        up_z: float
            usually 0.0, 1.0, or -1.0

        Notes
        -----

        Sets the position of the camera through setting the eye position, the center of
        the scene, and which axis is facing upward. Moving the eye position and the
        direction it is pointing (the center of the scene) allows the images to be seen
        from different angles. The version without any parameters sets the camera to the
        default position, pointing to the center of the display window with the Y axis
        as up. The default values are `camera(width//2.0, height//2.0, (height//2.0) /
        tan(PI*30.0 / 180.0), width//2.0, height//2.0, 0, 0, 1, 0)`. This function is
        similar to `glu_look_at()` in OpenGL, but it first clears the current camera
        settings.
        """
        return self._instance.camera(*args)

    def circle(self, x: float, y: float, extent: float, /) -> None:
        """Draws a circle to the screen.

        Underlying Processing method: PApplet.circle

        Parameters
        ----------

        extent: float
            width and height of the ellipse by default

        x: float
            x-coordinate of the ellipse

        y: float
            y-coordinate of the ellipse

        Notes
        -----

        Draws a circle to the screen. By default, the first two parameters set the
        location of the center, and the third sets the shape's width and height. The
        origin may be changed with the `ellipse_mode()` function.
        """
        return self._instance.circle(x, y, extent)

    def clear(self) -> None:
        """Clear the drawing surface by setting every pixel to black.

        Underlying Processing method: Sketch.clear

        Notes
        -----

        Clear the drawing surface by setting every pixel to black. Calling this method
        is the same as passing `0` to the `background()` method, as in `background(0)`.

        This method behaves differently than `Py5Graphics.clear()` because `Py5Graphics`
        objects allow transparent pixels.
        """
        return self._instance.clear()

    def clip(self, a: float, b: float, c: float, d: float, /) -> None:
        """Limits the rendering to the boundaries of a rectangle defined by the parameters.

        Underlying Processing method: PApplet.clip

        Parameters
        ----------

        a: float
            x-coordinate of the rectangle, by default

        b: float
            y-coordinate of the rectangle, by default

        c: float
            width of the rectangle, by default

        d: float
            height of the rectangle, by default

        Notes
        -----

        Limits the rendering to the boundaries of a rectangle defined by the parameters.
        The boundaries are drawn based on the state of the `image_mode()` fuction,
        either `CORNER`, `CORNERS`, or `CENTER`.
        """
        return self._instance.clip(a, b, c, d)

    @overload
    def copy(self) -> Py5Image:
        """Copies a region of pixels from the display window to another area of the display
        window and copies a region of pixels from an image used as the `src_img`
        parameter into the display window.

        Underlying Processing method: PApplet.copy

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

        Copies a region of pixels from the display window to another area of the display
        window and copies a region of pixels from an image used as the `src_img`
        parameter into the display window. If the source and destination regions aren't
        the same size, it will automatically resize the source pixels to fit the
        specified target region. No alpha information is used in the process, however if
        the source image has an alpha channel set, it will be copied as well.

        This function ignores `image_mode()`.

        If you want to create a new image with the contents of a rectangular region of
        the sketch, check out `get_pixels()` where x, y, w, h, are the position and
        dimensions of the area to be copied. It will return a `Py5Image` object.
        """
        pass

    @overload
    def copy(
        self, sx: int, sy: int, sw: int, sh: int, dx: int, dy: int, dw: int, dh: int, /
    ) -> None:
        """Copies a region of pixels from the display window to another area of the display
        window and copies a region of pixels from an image used as the `src_img`
        parameter into the display window.

        Underlying Processing method: PApplet.copy

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

        Copies a region of pixels from the display window to another area of the display
        window and copies a region of pixels from an image used as the `src_img`
        parameter into the display window. If the source and destination regions aren't
        the same size, it will automatically resize the source pixels to fit the
        specified target region. No alpha information is used in the process, however if
        the source image has an alpha channel set, it will be copied as well.

        This function ignores `image_mode()`.

        If you want to create a new image with the contents of a rectangular region of
        the sketch, check out `get_pixels()` where x, y, w, h, are the position and
        dimensions of the area to be copied. It will return a `Py5Image` object.
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
        """Copies a region of pixels from the display window to another area of the display
        window and copies a region of pixels from an image used as the `src_img`
        parameter into the display window.

        Underlying Processing method: PApplet.copy

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

        Copies a region of pixels from the display window to another area of the display
        window and copies a region of pixels from an image used as the `src_img`
        parameter into the display window. If the source and destination regions aren't
        the same size, it will automatically resize the source pixels to fit the
        specified target region. No alpha information is used in the process, however if
        the source image has an alpha channel set, it will be copied as well.

        This function ignores `image_mode()`.

        If you want to create a new image with the contents of a rectangular region of
        the sketch, check out `get_pixels()` where x, y, w, h, are the position and
        dimensions of the area to be copied. It will return a `Py5Image` object.
        """
        pass

    @_auto_convert_to_py5image(0)
    @_return_py5image
    def copy(self, *args):
        """Copies a region of pixels from the display window to another area of the display
        window and copies a region of pixels from an image used as the `src_img`
        parameter into the display window.

        Underlying Processing method: PApplet.copy

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

        Copies a region of pixels from the display window to another area of the display
        window and copies a region of pixels from an image used as the `src_img`
        parameter into the display window. If the source and destination regions aren't
        the same size, it will automatically resize the source pixels to fit the
        specified target region. No alpha information is used in the process, however if
        the source image has an alpha channel set, it will be copied as well.

        This function ignores `image_mode()`.

        If you want to create a new image with the contents of a rectangular region of
        the sketch, check out `get_pixels()` where x, y, w, h, are the position and
        dimensions of the area to be copied. It will return a `Py5Image` object.
        """
        return self._instance.copy(*args)

    @overload
    def create_font(self, name: str, size: float, /) -> Py5Font:
        """Dynamically converts a font to the format used by py5 from a .ttf or .otf file
        inside the Sketch's "data" folder or a font that's installed elsewhere on the
        computer.

        Underlying Processing method: PApplet.createFont

        Methods
        -------

        You can use any of the following signatures:

         * create_font(name: str, size: float, /) -> Py5Font
         * create_font(name: str, size: float, smooth: bool, /) -> Py5Font
         * create_font(name: str, size: float, smooth: bool, charset: Sequence[chr], /) -> Py5Font

        Parameters
        ----------

        charset: Sequence[chr]
            characters to be generated

        name: str
            name of the font to load

        size: float
            point size of the font

        smooth: bool
            true for an antialiased font, false for aliased

        Notes
        -----

        Dynamically converts a font to the format used by py5 from a .ttf or .otf file
        inside the Sketch's "data" folder or a font that's installed elsewhere on the
        computer. If you want to use a font installed on your computer, use the
        `Py5Font.list()` method to first determine the names for the fonts recognized by
        the computer and are compatible with this function. Not all fonts can be used
        and some might work with one operating system and not others. When sharing a
        Sketch with other people or posting it on the web, you may need to include a
        .ttf or .otf version of your font in the data directory of the Sketch because
        other people might not have the font installed on their computer. Only fonts
        that can legally be distributed should be included with a Sketch.

        The `size` parameter states the font size you want to generate. The `smooth`
        parameter specifies if the font should be antialiased or not. The `charset`
        parameter is an array of chars that specifies the characters to generate.

        This function allows py5 to work with the font natively in the default renderer,
        so the letters are defined by vector geometry and are rendered quickly. In the
        `P2D` and `P3D` renderers, the function sets the project to render the font as a
        series of small textures. For instance, when using the default renderer, the
        actual native version of the font will be employed by the Sketch, improving
        drawing quality and performance. With the `P2D` and `P3D` renderers, the
        bitmapped version will be used to improve speed and appearance, but the results
        are poor when exporting if the Sketch does not include the .otf or .ttf file,
        and the requested font is not available on the machine running the Sketch.
        """
        pass

    @overload
    def create_font(self, name: str, size: float, smooth: bool, /) -> Py5Font:
        """Dynamically converts a font to the format used by py5 from a .ttf or .otf file
        inside the Sketch's "data" folder or a font that's installed elsewhere on the
        computer.

        Underlying Processing method: PApplet.createFont

        Methods
        -------

        You can use any of the following signatures:

         * create_font(name: str, size: float, /) -> Py5Font
         * create_font(name: str, size: float, smooth: bool, /) -> Py5Font
         * create_font(name: str, size: float, smooth: bool, charset: Sequence[chr], /) -> Py5Font

        Parameters
        ----------

        charset: Sequence[chr]
            characters to be generated

        name: str
            name of the font to load

        size: float
            point size of the font

        smooth: bool
            true for an antialiased font, false for aliased

        Notes
        -----

        Dynamically converts a font to the format used by py5 from a .ttf or .otf file
        inside the Sketch's "data" folder or a font that's installed elsewhere on the
        computer. If you want to use a font installed on your computer, use the
        `Py5Font.list()` method to first determine the names for the fonts recognized by
        the computer and are compatible with this function. Not all fonts can be used
        and some might work with one operating system and not others. When sharing a
        Sketch with other people or posting it on the web, you may need to include a
        .ttf or .otf version of your font in the data directory of the Sketch because
        other people might not have the font installed on their computer. Only fonts
        that can legally be distributed should be included with a Sketch.

        The `size` parameter states the font size you want to generate. The `smooth`
        parameter specifies if the font should be antialiased or not. The `charset`
        parameter is an array of chars that specifies the characters to generate.

        This function allows py5 to work with the font natively in the default renderer,
        so the letters are defined by vector geometry and are rendered quickly. In the
        `P2D` and `P3D` renderers, the function sets the project to render the font as a
        series of small textures. For instance, when using the default renderer, the
        actual native version of the font will be employed by the Sketch, improving
        drawing quality and performance. With the `P2D` and `P3D` renderers, the
        bitmapped version will be used to improve speed and appearance, but the results
        are poor when exporting if the Sketch does not include the .otf or .ttf file,
        and the requested font is not available on the machine running the Sketch.
        """
        pass

    @overload
    def create_font(
        self, name: str, size: float, smooth: bool, charset: Sequence[chr], /
    ) -> Py5Font:
        """Dynamically converts a font to the format used by py5 from a .ttf or .otf file
        inside the Sketch's "data" folder or a font that's installed elsewhere on the
        computer.

        Underlying Processing method: PApplet.createFont

        Methods
        -------

        You can use any of the following signatures:

         * create_font(name: str, size: float, /) -> Py5Font
         * create_font(name: str, size: float, smooth: bool, /) -> Py5Font
         * create_font(name: str, size: float, smooth: bool, charset: Sequence[chr], /) -> Py5Font

        Parameters
        ----------

        charset: Sequence[chr]
            characters to be generated

        name: str
            name of the font to load

        size: float
            point size of the font

        smooth: bool
            true for an antialiased font, false for aliased

        Notes
        -----

        Dynamically converts a font to the format used by py5 from a .ttf or .otf file
        inside the Sketch's "data" folder or a font that's installed elsewhere on the
        computer. If you want to use a font installed on your computer, use the
        `Py5Font.list()` method to first determine the names for the fonts recognized by
        the computer and are compatible with this function. Not all fonts can be used
        and some might work with one operating system and not others. When sharing a
        Sketch with other people or posting it on the web, you may need to include a
        .ttf or .otf version of your font in the data directory of the Sketch because
        other people might not have the font installed on their computer. Only fonts
        that can legally be distributed should be included with a Sketch.

        The `size` parameter states the font size you want to generate. The `smooth`
        parameter specifies if the font should be antialiased or not. The `charset`
        parameter is an array of chars that specifies the characters to generate.

        This function allows py5 to work with the font natively in the default renderer,
        so the letters are defined by vector geometry and are rendered quickly. In the
        `P2D` and `P3D` renderers, the function sets the project to render the font as a
        series of small textures. For instance, when using the default renderer, the
        actual native version of the font will be employed by the Sketch, improving
        drawing quality and performance. With the `P2D` and `P3D` renderers, the
        bitmapped version will be used to improve speed and appearance, but the results
        are poor when exporting if the Sketch does not include the .otf or .ttf file,
        and the requested font is not available on the machine running the Sketch.
        """
        pass

    @_load_py5font
    def create_font(self, *args):
        """Dynamically converts a font to the format used by py5 from a .ttf or .otf file
        inside the Sketch's "data" folder or a font that's installed elsewhere on the
        computer.

        Underlying Processing method: PApplet.createFont

        Methods
        -------

        You can use any of the following signatures:

         * create_font(name: str, size: float, /) -> Py5Font
         * create_font(name: str, size: float, smooth: bool, /) -> Py5Font
         * create_font(name: str, size: float, smooth: bool, charset: Sequence[chr], /) -> Py5Font

        Parameters
        ----------

        charset: Sequence[chr]
            characters to be generated

        name: str
            name of the font to load

        size: float
            point size of the font

        smooth: bool
            true for an antialiased font, false for aliased

        Notes
        -----

        Dynamically converts a font to the format used by py5 from a .ttf or .otf file
        inside the Sketch's "data" folder or a font that's installed elsewhere on the
        computer. If you want to use a font installed on your computer, use the
        `Py5Font.list()` method to first determine the names for the fonts recognized by
        the computer and are compatible with this function. Not all fonts can be used
        and some might work with one operating system and not others. When sharing a
        Sketch with other people or posting it on the web, you may need to include a
        .ttf or .otf version of your font in the data directory of the Sketch because
        other people might not have the font installed on their computer. Only fonts
        that can legally be distributed should be included with a Sketch.

        The `size` parameter states the font size you want to generate. The `smooth`
        parameter specifies if the font should be antialiased or not. The `charset`
        parameter is an array of chars that specifies the characters to generate.

        This function allows py5 to work with the font natively in the default renderer,
        so the letters are defined by vector geometry and are rendered quickly. In the
        `P2D` and `P3D` renderers, the function sets the project to render the font as a
        series of small textures. For instance, when using the default renderer, the
        actual native version of the font will be employed by the Sketch, improving
        drawing quality and performance. With the `P2D` and `P3D` renderers, the
        bitmapped version will be used to improve speed and appearance, but the results
        are poor when exporting if the Sketch does not include the .otf or .ttf file,
        and the requested font is not available on the machine running the Sketch.
        """
        return self._instance.createFont(*args)

    @overload
    def create_graphics(self, w: int, h: int, /) -> Py5Graphics:
        """Creates and returns a new `Py5Graphics` object.

        Underlying Processing method: PApplet.createGraphics

        Methods
        -------

        You can use any of the following signatures:

         * create_graphics(w: int, h: int, /) -> Py5Graphics
         * create_graphics(w: int, h: int, renderer: str, /) -> Py5Graphics
         * create_graphics(w: int, h: int, renderer: str, path: str, /) -> Py5Graphics

        Parameters
        ----------

        h: int
            height in pixels

        path: str
            the name of the file (can be an absolute or relative path)

        renderer: str
            Either P2D, P3D, or PDF

        w: int
            width in pixels

        Notes
        -----

        Creates and returns a new `Py5Graphics` object. Use this class if you need to
        draw into an off-screen graphics buffer. The first two parameters define the
        width and height in pixels. The third, optional parameter specifies the
        renderer. It can be defined as `P2D`, `P3D`, `PDF`, or `SVG`. If the third
        parameter isn't used, the default renderer is set. The `PDF` and `SVG` renderers
        require the filename parameter.

        It's important to consider the renderer used with `create_graphics()` in
        relation to the main renderer specified in `size()`. For example, it's only
        possible to use `P2D` or `P3D` with `create_graphics()` when one of them is
        defined in `size()`. `P2D` and `P3D` use OpenGL for drawing, and when using an
        OpenGL renderer it's necessary for the main drawing surface to be OpenGL-based.
        If `P2D` or `P3D` are used as the renderer in `size()`, then any of the options
        can be used with `create_graphics()`. If the default renderer is used in
        `size()`, then only the default, `PDF`, or `SVG` can be used with
        `create_graphics()`.

        It's important to run all drawing functions between the
        `Py5Graphics.begin_draw()` and `Py5Graphics.end_draw()`. As the exception to
        this rule, `smooth()` should be run on the Py5Graphics object before
        `Py5Graphics.begin_draw()`. See the reference for `smooth()` for more detail.

        The `create_graphics()` function should almost never be used inside `draw()`
        because of the memory and time needed to set up the graphics. One-time or
        occasional use during `draw()` might be acceptable, but code that calls
        `create_graphics()` at 60 frames per second might run out of memory or freeze
        your Sketch.

        Unlike the main drawing surface which is completely opaque, surfaces created
        with `create_graphics()` can have transparency. This makes it possible to draw
        into a graphics and maintain the alpha channel. By using `save()` to write a
        `PNG` or `TGA` file, the transparency of the graphics object will be honored.
        """
        pass

    @overload
    def create_graphics(self, w: int, h: int, renderer: str, /) -> Py5Graphics:
        """Creates and returns a new `Py5Graphics` object.

        Underlying Processing method: PApplet.createGraphics

        Methods
        -------

        You can use any of the following signatures:

         * create_graphics(w: int, h: int, /) -> Py5Graphics
         * create_graphics(w: int, h: int, renderer: str, /) -> Py5Graphics
         * create_graphics(w: int, h: int, renderer: str, path: str, /) -> Py5Graphics

        Parameters
        ----------

        h: int
            height in pixels

        path: str
            the name of the file (can be an absolute or relative path)

        renderer: str
            Either P2D, P3D, or PDF

        w: int
            width in pixels

        Notes
        -----

        Creates and returns a new `Py5Graphics` object. Use this class if you need to
        draw into an off-screen graphics buffer. The first two parameters define the
        width and height in pixels. The third, optional parameter specifies the
        renderer. It can be defined as `P2D`, `P3D`, `PDF`, or `SVG`. If the third
        parameter isn't used, the default renderer is set. The `PDF` and `SVG` renderers
        require the filename parameter.

        It's important to consider the renderer used with `create_graphics()` in
        relation to the main renderer specified in `size()`. For example, it's only
        possible to use `P2D` or `P3D` with `create_graphics()` when one of them is
        defined in `size()`. `P2D` and `P3D` use OpenGL for drawing, and when using an
        OpenGL renderer it's necessary for the main drawing surface to be OpenGL-based.
        If `P2D` or `P3D` are used as the renderer in `size()`, then any of the options
        can be used with `create_graphics()`. If the default renderer is used in
        `size()`, then only the default, `PDF`, or `SVG` can be used with
        `create_graphics()`.

        It's important to run all drawing functions between the
        `Py5Graphics.begin_draw()` and `Py5Graphics.end_draw()`. As the exception to
        this rule, `smooth()` should be run on the Py5Graphics object before
        `Py5Graphics.begin_draw()`. See the reference for `smooth()` for more detail.

        The `create_graphics()` function should almost never be used inside `draw()`
        because of the memory and time needed to set up the graphics. One-time or
        occasional use during `draw()` might be acceptable, but code that calls
        `create_graphics()` at 60 frames per second might run out of memory or freeze
        your Sketch.

        Unlike the main drawing surface which is completely opaque, surfaces created
        with `create_graphics()` can have transparency. This makes it possible to draw
        into a graphics and maintain the alpha channel. By using `save()` to write a
        `PNG` or `TGA` file, the transparency of the graphics object will be honored.
        """
        pass

    @overload
    def create_graphics(
        self, w: int, h: int, renderer: str, path: str, /
    ) -> Py5Graphics:
        """Creates and returns a new `Py5Graphics` object.

        Underlying Processing method: PApplet.createGraphics

        Methods
        -------

        You can use any of the following signatures:

         * create_graphics(w: int, h: int, /) -> Py5Graphics
         * create_graphics(w: int, h: int, renderer: str, /) -> Py5Graphics
         * create_graphics(w: int, h: int, renderer: str, path: str, /) -> Py5Graphics

        Parameters
        ----------

        h: int
            height in pixels

        path: str
            the name of the file (can be an absolute or relative path)

        renderer: str
            Either P2D, P3D, or PDF

        w: int
            width in pixels

        Notes
        -----

        Creates and returns a new `Py5Graphics` object. Use this class if you need to
        draw into an off-screen graphics buffer. The first two parameters define the
        width and height in pixels. The third, optional parameter specifies the
        renderer. It can be defined as `P2D`, `P3D`, `PDF`, or `SVG`. If the third
        parameter isn't used, the default renderer is set. The `PDF` and `SVG` renderers
        require the filename parameter.

        It's important to consider the renderer used with `create_graphics()` in
        relation to the main renderer specified in `size()`. For example, it's only
        possible to use `P2D` or `P3D` with `create_graphics()` when one of them is
        defined in `size()`. `P2D` and `P3D` use OpenGL for drawing, and when using an
        OpenGL renderer it's necessary for the main drawing surface to be OpenGL-based.
        If `P2D` or `P3D` are used as the renderer in `size()`, then any of the options
        can be used with `create_graphics()`. If the default renderer is used in
        `size()`, then only the default, `PDF`, or `SVG` can be used with
        `create_graphics()`.

        It's important to run all drawing functions between the
        `Py5Graphics.begin_draw()` and `Py5Graphics.end_draw()`. As the exception to
        this rule, `smooth()` should be run on the Py5Graphics object before
        `Py5Graphics.begin_draw()`. See the reference for `smooth()` for more detail.

        The `create_graphics()` function should almost never be used inside `draw()`
        because of the memory and time needed to set up the graphics. One-time or
        occasional use during `draw()` might be acceptable, but code that calls
        `create_graphics()` at 60 frames per second might run out of memory or freeze
        your Sketch.

        Unlike the main drawing surface which is completely opaque, surfaces created
        with `create_graphics()` can have transparency. This makes it possible to draw
        into a graphics and maintain the alpha channel. By using `save()` to write a
        `PNG` or `TGA` file, the transparency of the graphics object will be honored.
        """
        pass

    @_return_py5graphics
    def create_graphics(self, *args):
        """Creates and returns a new `Py5Graphics` object.

        Underlying Processing method: PApplet.createGraphics

        Methods
        -------

        You can use any of the following signatures:

         * create_graphics(w: int, h: int, /) -> Py5Graphics
         * create_graphics(w: int, h: int, renderer: str, /) -> Py5Graphics
         * create_graphics(w: int, h: int, renderer: str, path: str, /) -> Py5Graphics

        Parameters
        ----------

        h: int
            height in pixels

        path: str
            the name of the file (can be an absolute or relative path)

        renderer: str
            Either P2D, P3D, or PDF

        w: int
            width in pixels

        Notes
        -----

        Creates and returns a new `Py5Graphics` object. Use this class if you need to
        draw into an off-screen graphics buffer. The first two parameters define the
        width and height in pixels. The third, optional parameter specifies the
        renderer. It can be defined as `P2D`, `P3D`, `PDF`, or `SVG`. If the third
        parameter isn't used, the default renderer is set. The `PDF` and `SVG` renderers
        require the filename parameter.

        It's important to consider the renderer used with `create_graphics()` in
        relation to the main renderer specified in `size()`. For example, it's only
        possible to use `P2D` or `P3D` with `create_graphics()` when one of them is
        defined in `size()`. `P2D` and `P3D` use OpenGL for drawing, and when using an
        OpenGL renderer it's necessary for the main drawing surface to be OpenGL-based.
        If `P2D` or `P3D` are used as the renderer in `size()`, then any of the options
        can be used with `create_graphics()`. If the default renderer is used in
        `size()`, then only the default, `PDF`, or `SVG` can be used with
        `create_graphics()`.

        It's important to run all drawing functions between the
        `Py5Graphics.begin_draw()` and `Py5Graphics.end_draw()`. As the exception to
        this rule, `smooth()` should be run on the Py5Graphics object before
        `Py5Graphics.begin_draw()`. See the reference for `smooth()` for more detail.

        The `create_graphics()` function should almost never be used inside `draw()`
        because of the memory and time needed to set up the graphics. One-time or
        occasional use during `draw()` might be acceptable, but code that calls
        `create_graphics()` at 60 frames per second might run out of memory or freeze
        your Sketch.

        Unlike the main drawing surface which is completely opaque, surfaces created
        with `create_graphics()` can have transparency. This makes it possible to draw
        into a graphics and maintain the alpha channel. By using `save()` to write a
        `PNG` or `TGA` file, the transparency of the graphics object will be honored.
        """
        return self._instance.createGraphics(*args)

    @_return_py5image
    def create_image(self, w: int, h: int, format: int, /) -> Py5Image:
        """Creates a new Py5Image (the datatype for storing images).

        Underlying Processing method: PApplet.createImage

        Parameters
        ----------

        format: int
            Either RGB, ARGB, ALPHA (grayscale alpha channel)

        h: int
            height in pixels

        w: int
            width in pixels

        Notes
        -----

        Creates a new Py5Image (the datatype for storing images). This provides a fresh
        buffer of pixels to play with. Set the size of the buffer with the `w` and `h`
        parameters. The `format` parameter defines how the pixels are stored. See the
        `Py5Image` reference for more information.

        Be sure to include all three parameters, specifying only the width and height
        (but no format) will produce a strange error.

        Advanced users please note that `create_image()` should be used instead of the
        syntax `Py5Image()`.
        """
        return self._instance.createImage(w, h, format)

    @overload
    def create_shape(self) -> Py5Shape:
        """The `create_shape()` function is used to define a new shape.

        Underlying Processing method: PApplet.createShape

        Methods
        -------

        You can use any of the following signatures:

         * create_shape() -> Py5Shape
         * create_shape(kind: int, /, *p: float) -> Py5Shape
         * create_shape(type: int, /) -> Py5Shape

        Parameters
        ----------

        kind: int
            either POINT, LINE, TRIANGLE, QUAD, RECT, ELLIPSE, ARC, BOX, SPHERE

        p: float
            parameters that match the kind of shape

        type: int
            either GROUP, PATH, or GEOMETRY

        Notes
        -----

        The `create_shape()` function is used to define a new shape. Once created, this
        shape can be drawn with the `shape()` function. The basic way to use the
        function defines new primitive shapes. One of the following parameters are used
        as the first parameter: `ELLIPSE`, `RECT`, `ARC`, `TRIANGLE`, `SPHERE`, `BOX`,
        `QUAD`, or `LINE`. The parameters for each of these different shapes are the
        same as their corresponding functions: `ellipse()`, `rect()`, `arc()`,
        `triangle()`, `sphere()`, `box()`, `quad()`, and `line()`. The first example
        clarifies how this works.

        Custom, unique shapes can be made by using `create_shape()` without a parameter.
        After the shape is started, the drawing attributes and geometry can be set
        directly to the shape within the `begin_shape()` and `end_shape()` methods. See
        the second example for specifics, and the reference for `begin_shape()` for all
        of its options.

        The  `create_shape()` function can also be used to make a complex shape made of
        other shapes. This is called a "group" and it's created by using the parameter
        `GROUP` as the first parameter. See the fourth example to see how it works.

        After using `create_shape()`, stroke and fill color can be set by calling
        methods like `Py5Shape.set_fill()` and `Py5Shape.set_stroke()`, as seen in the
        examples. The complete list of methods and fields for the `Py5Shape` class are
        in the py5 documentation.
        """
        pass

    @overload
    def create_shape(self, type: int, /) -> Py5Shape:
        """The `create_shape()` function is used to define a new shape.

        Underlying Processing method: PApplet.createShape

        Methods
        -------

        You can use any of the following signatures:

         * create_shape() -> Py5Shape
         * create_shape(kind: int, /, *p: float) -> Py5Shape
         * create_shape(type: int, /) -> Py5Shape

        Parameters
        ----------

        kind: int
            either POINT, LINE, TRIANGLE, QUAD, RECT, ELLIPSE, ARC, BOX, SPHERE

        p: float
            parameters that match the kind of shape

        type: int
            either GROUP, PATH, or GEOMETRY

        Notes
        -----

        The `create_shape()` function is used to define a new shape. Once created, this
        shape can be drawn with the `shape()` function. The basic way to use the
        function defines new primitive shapes. One of the following parameters are used
        as the first parameter: `ELLIPSE`, `RECT`, `ARC`, `TRIANGLE`, `SPHERE`, `BOX`,
        `QUAD`, or `LINE`. The parameters for each of these different shapes are the
        same as their corresponding functions: `ellipse()`, `rect()`, `arc()`,
        `triangle()`, `sphere()`, `box()`, `quad()`, and `line()`. The first example
        clarifies how this works.

        Custom, unique shapes can be made by using `create_shape()` without a parameter.
        After the shape is started, the drawing attributes and geometry can be set
        directly to the shape within the `begin_shape()` and `end_shape()` methods. See
        the second example for specifics, and the reference for `begin_shape()` for all
        of its options.

        The  `create_shape()` function can also be used to make a complex shape made of
        other shapes. This is called a "group" and it's created by using the parameter
        `GROUP` as the first parameter. See the fourth example to see how it works.

        After using `create_shape()`, stroke and fill color can be set by calling
        methods like `Py5Shape.set_fill()` and `Py5Shape.set_stroke()`, as seen in the
        examples. The complete list of methods and fields for the `Py5Shape` class are
        in the py5 documentation.
        """
        pass

    @overload
    def create_shape(self, kind: int, /, *p: float) -> Py5Shape:
        """The `create_shape()` function is used to define a new shape.

        Underlying Processing method: PApplet.createShape

        Methods
        -------

        You can use any of the following signatures:

         * create_shape() -> Py5Shape
         * create_shape(kind: int, /, *p: float) -> Py5Shape
         * create_shape(type: int, /) -> Py5Shape

        Parameters
        ----------

        kind: int
            either POINT, LINE, TRIANGLE, QUAD, RECT, ELLIPSE, ARC, BOX, SPHERE

        p: float
            parameters that match the kind of shape

        type: int
            either GROUP, PATH, or GEOMETRY

        Notes
        -----

        The `create_shape()` function is used to define a new shape. Once created, this
        shape can be drawn with the `shape()` function. The basic way to use the
        function defines new primitive shapes. One of the following parameters are used
        as the first parameter: `ELLIPSE`, `RECT`, `ARC`, `TRIANGLE`, `SPHERE`, `BOX`,
        `QUAD`, or `LINE`. The parameters for each of these different shapes are the
        same as their corresponding functions: `ellipse()`, `rect()`, `arc()`,
        `triangle()`, `sphere()`, `box()`, `quad()`, and `line()`. The first example
        clarifies how this works.

        Custom, unique shapes can be made by using `create_shape()` without a parameter.
        After the shape is started, the drawing attributes and geometry can be set
        directly to the shape within the `begin_shape()` and `end_shape()` methods. See
        the second example for specifics, and the reference for `begin_shape()` for all
        of its options.

        The  `create_shape()` function can also be used to make a complex shape made of
        other shapes. This is called a "group" and it's created by using the parameter
        `GROUP` as the first parameter. See the fourth example to see how it works.

        After using `create_shape()`, stroke and fill color can be set by calling
        methods like `Py5Shape.set_fill()` and `Py5Shape.set_stroke()`, as seen in the
        examples. The complete list of methods and fields for the `Py5Shape` class are
        in the py5 documentation.
        """
        pass

    @_return_py5shape
    def create_shape(self, *args):
        """The `create_shape()` function is used to define a new shape.

        Underlying Processing method: PApplet.createShape

        Methods
        -------

        You can use any of the following signatures:

         * create_shape() -> Py5Shape
         * create_shape(kind: int, /, *p: float) -> Py5Shape
         * create_shape(type: int, /) -> Py5Shape

        Parameters
        ----------

        kind: int
            either POINT, LINE, TRIANGLE, QUAD, RECT, ELLIPSE, ARC, BOX, SPHERE

        p: float
            parameters that match the kind of shape

        type: int
            either GROUP, PATH, or GEOMETRY

        Notes
        -----

        The `create_shape()` function is used to define a new shape. Once created, this
        shape can be drawn with the `shape()` function. The basic way to use the
        function defines new primitive shapes. One of the following parameters are used
        as the first parameter: `ELLIPSE`, `RECT`, `ARC`, `TRIANGLE`, `SPHERE`, `BOX`,
        `QUAD`, or `LINE`. The parameters for each of these different shapes are the
        same as their corresponding functions: `ellipse()`, `rect()`, `arc()`,
        `triangle()`, `sphere()`, `box()`, `quad()`, and `line()`. The first example
        clarifies how this works.

        Custom, unique shapes can be made by using `create_shape()` without a parameter.
        After the shape is started, the drawing attributes and geometry can be set
        directly to the shape within the `begin_shape()` and `end_shape()` methods. See
        the second example for specifics, and the reference for `begin_shape()` for all
        of its options.

        The  `create_shape()` function can also be used to make a complex shape made of
        other shapes. This is called a "group" and it's created by using the parameter
        `GROUP` as the first parameter. See the fourth example to see how it works.

        After using `create_shape()`, stroke and fill color can be set by calling
        methods like `Py5Shape.set_fill()` and `Py5Shape.set_stroke()`, as seen in the
        examples. The complete list of methods and fields for the `Py5Shape` class are
        in the py5 documentation.
        """
        return self._instance.createShape(*args)

    @overload
    def cursor(self) -> None:
        """Sets the cursor to a predefined symbol or an image, or makes it visible if
        already hidden.

        Underlying Processing method: PApplet.cursor

        Methods
        -------

        You can use any of the following signatures:

         * cursor() -> None
         * cursor(img: Py5Image, /) -> None
         * cursor(img: Py5Image, x: int, y: int, /) -> None
         * cursor(kind: int, /) -> None

        Parameters
        ----------

        img: Py5Image
            any variable of type Py5Image

        kind: int
            either ARROW, CROSS, HAND, MOVE, TEXT, or WAIT

        x: int
            the horizontal active spot of the cursor

        y: int
            the vertical active spot of the cursor

        Notes
        -----

        Sets the cursor to a predefined symbol or an image, or makes it visible if
        already hidden. If you are trying to set an image as the cursor, the recommended
        size is 16x16 or 32x32 pixels. The values for parameters `x` and `y` must be
        less than the dimensions of the image.

        Setting or hiding the cursor does not generally work with "Present" mode (when
        running full-screen).

        With the `P2D` and `P3D` renderers, a generic set of cursors are used because
        the OpenGL renderer doesn't have access to the default cursor images for each
        platform (Processing Issue 3791).
        """
        pass

    @overload
    def cursor(self, kind: int, /) -> None:
        """Sets the cursor to a predefined symbol or an image, or makes it visible if
        already hidden.

        Underlying Processing method: PApplet.cursor

        Methods
        -------

        You can use any of the following signatures:

         * cursor() -> None
         * cursor(img: Py5Image, /) -> None
         * cursor(img: Py5Image, x: int, y: int, /) -> None
         * cursor(kind: int, /) -> None

        Parameters
        ----------

        img: Py5Image
            any variable of type Py5Image

        kind: int
            either ARROW, CROSS, HAND, MOVE, TEXT, or WAIT

        x: int
            the horizontal active spot of the cursor

        y: int
            the vertical active spot of the cursor

        Notes
        -----

        Sets the cursor to a predefined symbol or an image, or makes it visible if
        already hidden. If you are trying to set an image as the cursor, the recommended
        size is 16x16 or 32x32 pixels. The values for parameters `x` and `y` must be
        less than the dimensions of the image.

        Setting or hiding the cursor does not generally work with "Present" mode (when
        running full-screen).

        With the `P2D` and `P3D` renderers, a generic set of cursors are used because
        the OpenGL renderer doesn't have access to the default cursor images for each
        platform (Processing Issue 3791).
        """
        pass

    @overload
    def cursor(self, img: Py5Image, /) -> None:
        """Sets the cursor to a predefined symbol or an image, or makes it visible if
        already hidden.

        Underlying Processing method: PApplet.cursor

        Methods
        -------

        You can use any of the following signatures:

         * cursor() -> None
         * cursor(img: Py5Image, /) -> None
         * cursor(img: Py5Image, x: int, y: int, /) -> None
         * cursor(kind: int, /) -> None

        Parameters
        ----------

        img: Py5Image
            any variable of type Py5Image

        kind: int
            either ARROW, CROSS, HAND, MOVE, TEXT, or WAIT

        x: int
            the horizontal active spot of the cursor

        y: int
            the vertical active spot of the cursor

        Notes
        -----

        Sets the cursor to a predefined symbol or an image, or makes it visible if
        already hidden. If you are trying to set an image as the cursor, the recommended
        size is 16x16 or 32x32 pixels. The values for parameters `x` and `y` must be
        less than the dimensions of the image.

        Setting or hiding the cursor does not generally work with "Present" mode (when
        running full-screen).

        With the `P2D` and `P3D` renderers, a generic set of cursors are used because
        the OpenGL renderer doesn't have access to the default cursor images for each
        platform (Processing Issue 3791).
        """
        pass

    @overload
    def cursor(self, img: Py5Image, x: int, y: int, /) -> None:
        """Sets the cursor to a predefined symbol or an image, or makes it visible if
        already hidden.

        Underlying Processing method: PApplet.cursor

        Methods
        -------

        You can use any of the following signatures:

         * cursor() -> None
         * cursor(img: Py5Image, /) -> None
         * cursor(img: Py5Image, x: int, y: int, /) -> None
         * cursor(kind: int, /) -> None

        Parameters
        ----------

        img: Py5Image
            any variable of type Py5Image

        kind: int
            either ARROW, CROSS, HAND, MOVE, TEXT, or WAIT

        x: int
            the horizontal active spot of the cursor

        y: int
            the vertical active spot of the cursor

        Notes
        -----

        Sets the cursor to a predefined symbol or an image, or makes it visible if
        already hidden. If you are trying to set an image as the cursor, the recommended
        size is 16x16 or 32x32 pixels. The values for parameters `x` and `y` must be
        less than the dimensions of the image.

        Setting or hiding the cursor does not generally work with "Present" mode (when
        running full-screen).

        With the `P2D` and `P3D` renderers, a generic set of cursors are used because
        the OpenGL renderer doesn't have access to the default cursor images for each
        platform (Processing Issue 3791).
        """
        pass

    @_auto_convert_to_py5image(0)
    def cursor(self, *args):
        """Sets the cursor to a predefined symbol or an image, or makes it visible if
        already hidden.

        Underlying Processing method: PApplet.cursor

        Methods
        -------

        You can use any of the following signatures:

         * cursor() -> None
         * cursor(img: Py5Image, /) -> None
         * cursor(img: Py5Image, x: int, y: int, /) -> None
         * cursor(kind: int, /) -> None

        Parameters
        ----------

        img: Py5Image
            any variable of type Py5Image

        kind: int
            either ARROW, CROSS, HAND, MOVE, TEXT, or WAIT

        x: int
            the horizontal active spot of the cursor

        y: int
            the vertical active spot of the cursor

        Notes
        -----

        Sets the cursor to a predefined symbol or an image, or makes it visible if
        already hidden. If you are trying to set an image as the cursor, the recommended
        size is 16x16 or 32x32 pixels. The values for parameters `x` and `y` must be
        less than the dimensions of the image.

        Setting or hiding the cursor does not generally work with "Present" mode (when
        running full-screen).

        With the `P2D` and `P3D` renderers, a generic set of cursors are used because
        the OpenGL renderer doesn't have access to the default cursor images for each
        platform (Processing Issue 3791).
        """
        return self._instance.cursor(*args)

    @overload
    def curve(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        x3: float,
        y3: float,
        x4: float,
        y4: float,
        /,
    ) -> None:
        """Draws a curved line on the screen.

        Underlying Processing method: PApplet.curve

        Methods
        -------

        You can use any of the following signatures:

         * curve(x1: float, y1: float, x2: float, y2: float, x3: float, y3: float, x4: float, y4: float, /) -> None
         * curve(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float, x3: float, y3: float, z3: float, x4: float, y4: float, z4: float, /) -> None

        Parameters
        ----------

        x1: float
            coordinates for the beginning control point

        x2: float
            coordinates for the first point

        x3: float
            coordinates for the second point

        x4: float
            coordinates for the ending control point

        y1: float
            coordinates for the beginning control point

        y2: float
            coordinates for the first point

        y3: float
            coordinates for the second point

        y4: float
            coordinates for the ending control point

        z1: float
            coordinates for the beginning control point

        z2: float
            coordinates for the first point

        z3: float
            coordinates for the second point

        z4: float
            coordinates for the ending control point

        Notes
        -----

        Draws a curved line on the screen. The first and second parameters specify the
        beginning control point and the last two parameters specify the ending control
        point. The middle parameters specify the start and stop of the curve. Longer
        curves can be created by putting a series of `curve()` functions together or
        using `curve_vertex()`. An additional function called `curve_tightness()`
        provides control for the visual quality of the curve. The `curve()` function is
        an implementation of Catmull-Rom splines. Using the 3D version requires
        rendering with `P3D`.
        """
        pass

    @overload
    def curve(
        self,
        x1: float,
        y1: float,
        z1: float,
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
        """Draws a curved line on the screen.

        Underlying Processing method: PApplet.curve

        Methods
        -------

        You can use any of the following signatures:

         * curve(x1: float, y1: float, x2: float, y2: float, x3: float, y3: float, x4: float, y4: float, /) -> None
         * curve(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float, x3: float, y3: float, z3: float, x4: float, y4: float, z4: float, /) -> None

        Parameters
        ----------

        x1: float
            coordinates for the beginning control point

        x2: float
            coordinates for the first point

        x3: float
            coordinates for the second point

        x4: float
            coordinates for the ending control point

        y1: float
            coordinates for the beginning control point

        y2: float
            coordinates for the first point

        y3: float
            coordinates for the second point

        y4: float
            coordinates for the ending control point

        z1: float
            coordinates for the beginning control point

        z2: float
            coordinates for the first point

        z3: float
            coordinates for the second point

        z4: float
            coordinates for the ending control point

        Notes
        -----

        Draws a curved line on the screen. The first and second parameters specify the
        beginning control point and the last two parameters specify the ending control
        point. The middle parameters specify the start and stop of the curve. Longer
        curves can be created by putting a series of `curve()` functions together or
        using `curve_vertex()`. An additional function called `curve_tightness()`
        provides control for the visual quality of the curve. The `curve()` function is
        an implementation of Catmull-Rom splines. Using the 3D version requires
        rendering with `P3D`.
        """
        pass

    def curve(self, *args):
        """Draws a curved line on the screen.

        Underlying Processing method: PApplet.curve

        Methods
        -------

        You can use any of the following signatures:

         * curve(x1: float, y1: float, x2: float, y2: float, x3: float, y3: float, x4: float, y4: float, /) -> None
         * curve(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float, x3: float, y3: float, z3: float, x4: float, y4: float, z4: float, /) -> None

        Parameters
        ----------

        x1: float
            coordinates for the beginning control point

        x2: float
            coordinates for the first point

        x3: float
            coordinates for the second point

        x4: float
            coordinates for the ending control point

        y1: float
            coordinates for the beginning control point

        y2: float
            coordinates for the first point

        y3: float
            coordinates for the second point

        y4: float
            coordinates for the ending control point

        z1: float
            coordinates for the beginning control point

        z2: float
            coordinates for the first point

        z3: float
            coordinates for the second point

        z4: float
            coordinates for the ending control point

        Notes
        -----

        Draws a curved line on the screen. The first and second parameters specify the
        beginning control point and the last two parameters specify the ending control
        point. The middle parameters specify the start and stop of the curve. Longer
        curves can be created by putting a series of `curve()` functions together or
        using `curve_vertex()`. An additional function called `curve_tightness()`
        provides control for the visual quality of the curve. The `curve()` function is
        an implementation of Catmull-Rom splines. Using the 3D version requires
        rendering with `P3D`.
        """
        return self._instance.curve(*args)

    def curve_detail(self, detail: int, /) -> None:
        """Sets the resolution at which curves display.

        Underlying Processing method: PApplet.curveDetail

        Parameters
        ----------

        detail: int
            resolution of the curves

        Notes
        -----

        Sets the resolution at which curves display. The default value is 20. This
        function is only useful when using the `P3D` renderer as the default `P2D`
        renderer does not use this information.
        """
        return self._instance.curveDetail(detail)

    def curve_point(self, a: float, b: float, c: float, d: float, t: float, /) -> float:
        """Evaluates the curve at point `t` for points `a`, `b`, `c`, `d`.

        Underlying Processing method: PApplet.curvePoint

        Parameters
        ----------

        a: float
            coordinate of first control point

        b: float
            coordinate of first point on the curve

        c: float
            coordinate of second point on the curve

        d: float
            coordinate of second control point

        t: float
            value between 0 and 1

        Notes
        -----

        Evaluates the curve at point `t` for points `a`, `b`, `c`, `d`. The parameter
        `t` may range from 0 (the start of the curve) and 1 (the end of the curve). `a`
        and `d` are the control points, and `b` and `c` are points on the curve. As seen
        in the example, this can be used once with the `x` coordinates and a second time
        with the `y` coordinates to get the location of a curve at `t`.
        """
        return self._instance.curvePoint(a, b, c, d, t)

    def curve_tangent(
        self, a: float, b: float, c: float, d: float, t: float, /
    ) -> float:
        """Calculates the tangent of a point on a curve.

        Underlying Processing method: PApplet.curveTangent

        Parameters
        ----------

        a: float
            coordinate of first point on the curve

        b: float
            coordinate of first control point

        c: float
            coordinate of second control point

        d: float
            coordinate of second point on the curve

        t: float
            value between 0 and 1

        Notes
        -----

        Calculates the tangent of a point on a curve. There's a good definition of
        *tangent* on Wikipedia.
        """
        return self._instance.curveTangent(a, b, c, d, t)

    def curve_tightness(self, tightness: float, /) -> None:
        """Modifies the quality of forms created with `curve()` and `curve_vertex()`.

        Underlying Processing method: PApplet.curveTightness

        Parameters
        ----------

        tightness: float
            amount of deformation from the original vertices

        Notes
        -----

        Modifies the quality of forms created with `curve()` and `curve_vertex()`. The
        parameter `tightness` determines how the curve fits to the vertex points. The
        value 0.0 is the default value for `tightness` (this value defines the curves to
        be Catmull-Rom splines) and the value 1.0 connects all the points with straight
        lines. Values within the range -5.0 and 5.0 will deform the curves but will
        leave them recognizable and as values increase in magnitude, they will continue
        to deform.
        """
        return self._instance.curveTightness(tightness)

    @overload
    def curve_vertex(self, x: float, y: float, /) -> None:
        """Specifies vertex coordinates for curves.

        Underlying Processing method: PApplet.curveVertex

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

        Specifies vertex coordinates for curves. This method may only be used between
        `begin_shape()` and `end_shape()` and only when there is no `MODE` parameter
        specified to `begin_shape()`. The first and last points in a series of
        `curve_vertex()` lines will be used to guide the beginning and end of the curve.
        A minimum of four points is required to draw a tiny curve between the second and
        third points. Adding a fifth point with `curve_vertex()` will draw the curve
        between the second, third, and fourth points. The `curve_vertex()` method is an
        implementation of Catmull-Rom splines. Using the 3D version requires rendering
        with `P3D`.
        """
        pass

    @overload
    def curve_vertex(self, x: float, y: float, z: float, /) -> None:
        """Specifies vertex coordinates for curves.

        Underlying Processing method: PApplet.curveVertex

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

        Specifies vertex coordinates for curves. This method may only be used between
        `begin_shape()` and `end_shape()` and only when there is no `MODE` parameter
        specified to `begin_shape()`. The first and last points in a series of
        `curve_vertex()` lines will be used to guide the beginning and end of the curve.
        A minimum of four points is required to draw a tiny curve between the second and
        third points. Adding a fifth point with `curve_vertex()` will draw the curve
        between the second, third, and fourth points. The `curve_vertex()` method is an
        implementation of Catmull-Rom splines. Using the 3D version requires rendering
        with `P3D`.
        """
        pass

    def curve_vertex(self, *args):
        """Specifies vertex coordinates for curves.

        Underlying Processing method: PApplet.curveVertex

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

        Specifies vertex coordinates for curves. This method may only be used between
        `begin_shape()` and `end_shape()` and only when there is no `MODE` parameter
        specified to `begin_shape()`. The first and last points in a series of
        `curve_vertex()` lines will be used to guide the beginning and end of the curve.
        A minimum of four points is required to draw a tiny curve between the second and
        third points. Adding a fifth point with `curve_vertex()` will draw the curve
        between the second, third, and fourth points. The `curve_vertex()` method is an
        implementation of Catmull-Rom splines. Using the 3D version requires rendering
        with `P3D`.
        """
        return self._instance.curveVertex(*args)

    @_generator_to_list
    def curve_vertices(self, coordinates: Sequence[Sequence[float]], /) -> None:
        """Create a collection of curve vertices.

        Parameters
        ----------

        coordinates: Sequence[Sequence[float]]
            2D array of curve vertex coordinates with 2 or 3 columns for 2D or 3D points, respectively

        Notes
        -----

        Create a collection of curve vertices. The purpose of this method is to provide
        an alternative to repeatedly calling `curve_vertex()` in a loop. For a large
        number of curve vertices, the performance of `curve_vertices()` will be much
        faster.

        The `coordinates` parameter should be a numpy array with one row for each curve
        vertex.  There should be two or three columns for 2D or 3D points, respectively.
        """
        return self._instance.curveVertices(coordinates)

    @classmethod
    def day(cls) -> int:
        """Py5 communicates with the clock on your computer.

        Underlying Processing method: PApplet.day

        Notes
        -----

        Py5 communicates with the clock on your computer. The `day()` function returns
        the current day as a value from 1 - 31.
        """
        return cls._cls.day()

    def directional_light(
        self, v1: float, v2: float, v3: float, nx: float, ny: float, nz: float, /
    ) -> None:
        """Adds a directional light.

        Underlying Processing method: PApplet.directionalLight

        Parameters
        ----------

        nx: float
            direction along the x-axis

        ny: float
            direction along the y-axis

        nz: float
            direction along the z-axis

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Adds a directional light. Directional light comes from one direction: it is
        stronger when hitting a surface squarely, and weaker if it hits at a gentle
        angle. After hitting a surface, directional light scatters in all directions.
        Lights need to be included in the `draw()` to remain persistent in a looping
        program. Placing them in the `setup()` of a looping program will cause them to
        only have an effect the first time through the loop. The `v1`, `v2`, and `v3`
        parameters are interpreted as either `RGB` or `HSB` values, depending on the
        current color mode. The `nx`, `ny`, and `nz` parameters specify the direction
        the light is facing. For example, setting `ny` to -1 will cause the geometry to
        be lit from below (since the light would be facing directly upward).
        """
        return self._instance.directionalLight(v1, v2, v3, nx, ny, nz)

    @overload
    def display_density(self) -> int:
        """This function returns the number "2" if the screen is a high-density screen
        (called a Retina display on macOS or high-dpi on Windows and Linux) and a "1" if
        not.

        Underlying Processing method: PApplet.displayDensity

        Methods
        -------

        You can use any of the following signatures:

         * display_density() -> int
         * display_density(display: int, /) -> int

        Parameters
        ----------

        display: int
            the display number to check (1-indexed to match the Preferences dialog box)

        Notes
        -----

        This function returns the number "2" if the screen is a high-density screen
        (called a Retina display on macOS or high-dpi on Windows and Linux) and a "1" if
        not. This information is useful for a program to adapt to run at double the
        pixel density on a screen that supports it.
        """
        pass

    @overload
    def display_density(self, display: int, /) -> int:
        """This function returns the number "2" if the screen is a high-density screen
        (called a Retina display on macOS or high-dpi on Windows and Linux) and a "1" if
        not.

        Underlying Processing method: PApplet.displayDensity

        Methods
        -------

        You can use any of the following signatures:

         * display_density() -> int
         * display_density(display: int, /) -> int

        Parameters
        ----------

        display: int
            the display number to check (1-indexed to match the Preferences dialog box)

        Notes
        -----

        This function returns the number "2" if the screen is a high-density screen
        (called a Retina display on macOS or high-dpi on Windows and Linux) and a "1" if
        not. This information is useful for a program to adapt to run at double the
        pixel density on a screen that supports it.
        """
        pass

    def display_density(self, *args):
        """This function returns the number "2" if the screen is a high-density screen
        (called a Retina display on macOS or high-dpi on Windows and Linux) and a "1" if
        not.

        Underlying Processing method: PApplet.displayDensity

        Methods
        -------

        You can use any of the following signatures:

         * display_density() -> int
         * display_density(display: int, /) -> int

        Parameters
        ----------

        display: int
            the display number to check (1-indexed to match the Preferences dialog box)

        Notes
        -----

        This function returns the number "2" if the screen is a high-density screen
        (called a Retina display on macOS or high-dpi on Windows and Linux) and a "1" if
        not. This information is useful for a program to adapt to run at double the
        pixel density on a screen that supports it.
        """
        return self._instance.displayDensity(*args)

    def ellipse(self, a: float, b: float, c: float, d: float, /) -> None:
        """Draws an ellipse (oval) to the screen.

        Underlying Processing method: PApplet.ellipse

        Parameters
        ----------

        a: float
            x-coordinate of the ellipse

        b: float
            y-coordinate of the ellipse

        c: float
            width of the ellipse by default

        d: float
            height of the ellipse by default

        Notes
        -----

        Draws an ellipse (oval) to the screen. An ellipse with equal width and height is
        a circle. By default, the first two parameters set the location, and the third
        and fourth parameters set the shape's width and height. The origin may be
        changed with the `ellipse_mode()` function.
        """
        return self._instance.ellipse(a, b, c, d)

    def ellipse_mode(self, mode: int, /) -> None:
        """Modifies the location from which ellipses are drawn by changing the way in which
        parameters given to `ellipse()` are intepreted.

        Underlying Processing method: PApplet.ellipseMode

        Parameters
        ----------

        mode: int
            either CENTER, RADIUS, CORNER, or CORNERS

        Notes
        -----

        Modifies the location from which ellipses are drawn by changing the way in which
        parameters given to `ellipse()` are intepreted.

        The default mode is `ellipse_mode(CENTER)`, which interprets the first two
        parameters of `ellipse()` as the shape's center point, while the third and
        fourth parameters are its width and height.

        `ellipse_mode(RADIUS)` also uses the first two parameters of `ellipse()` as the
        shape's center point, but uses the third and fourth parameters to specify half
        of the shapes's width and height.

        `ellipse_mode(CORNER)` interprets the first two parameters of `ellipse()` as the
        upper-left corner of the shape, while the third and fourth parameters are its
        width and height.

        `ellipse_mode(CORNERS)` interprets the first two parameters of `ellipse()` as
        the location of one corner of the ellipse's bounding box, and the third and
        fourth parameters as the location of the opposite corner.

        The parameter must be written in ALL CAPS because Python is a case-sensitive
        language.
        """
        return self._instance.ellipseMode(mode)

    @overload
    def emissive(self, gray: float, /) -> None:
        """Sets the emissive color of the material used for drawing shapes drawn to the
        screen.

        Underlying Processing method: PApplet.emissive

        Methods
        -------

        You can use any of the following signatures:

         * emissive(gray: float, /) -> None
         * emissive(rgb: int, /) -> None
         * emissive(v1: float, v2: float, v3: float, /) -> None

        Parameters
        ----------

        gray: float
            value between black and white, by default 0 to 255

        rgb: int
            color to set

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the emissive color of the material used for drawing shapes drawn to the
        screen. Use in combination with `ambient()`, `specular()`, and `shininess()` to
        set the material properties of shapes.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def emissive(self, v1: float, v2: float, v3: float, /) -> None:
        """Sets the emissive color of the material used for drawing shapes drawn to the
        screen.

        Underlying Processing method: PApplet.emissive

        Methods
        -------

        You can use any of the following signatures:

         * emissive(gray: float, /) -> None
         * emissive(rgb: int, /) -> None
         * emissive(v1: float, v2: float, v3: float, /) -> None

        Parameters
        ----------

        gray: float
            value between black and white, by default 0 to 255

        rgb: int
            color to set

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the emissive color of the material used for drawing shapes drawn to the
        screen. Use in combination with `ambient()`, `specular()`, and `shininess()` to
        set the material properties of shapes.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def emissive(self, rgb: int, /) -> None:
        """Sets the emissive color of the material used for drawing shapes drawn to the
        screen.

        Underlying Processing method: PApplet.emissive

        Methods
        -------

        You can use any of the following signatures:

         * emissive(gray: float, /) -> None
         * emissive(rgb: int, /) -> None
         * emissive(v1: float, v2: float, v3: float, /) -> None

        Parameters
        ----------

        gray: float
            value between black and white, by default 0 to 255

        rgb: int
            color to set

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the emissive color of the material used for drawing shapes drawn to the
        screen. Use in combination with `ambient()`, `specular()`, and `shininess()` to
        set the material properties of shapes.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @_convert_hex_color()
    def emissive(self, *args):
        """Sets the emissive color of the material used for drawing shapes drawn to the
        screen.

        Underlying Processing method: PApplet.emissive

        Methods
        -------

        You can use any of the following signatures:

         * emissive(gray: float, /) -> None
         * emissive(rgb: int, /) -> None
         * emissive(v1: float, v2: float, v3: float, /) -> None

        Parameters
        ----------

        gray: float
            value between black and white, by default 0 to 255

        rgb: int
            color to set

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the emissive color of the material used for drawing shapes drawn to the
        screen. Use in combination with `ambient()`, `specular()`, and `shininess()` to
        set the material properties of shapes.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        return self._instance.emissive(*args)

    def end_camera(self) -> None:
        """The `begin_camera()` and `end_camera()` methods enable advanced customization of
        the camera space.

        Underlying Processing method: PApplet.endCamera

        Notes
        -----

        The `begin_camera()` and `end_camera()` methods enable advanced customization of
        the camera space. Please see the reference for `begin_camera()` for a
        description of how the methods are used.
        """
        return self._instance.endCamera()

    def end_contour(self) -> None:
        """Use the `begin_contour()` and `end_contour()` methods to create negative shapes
        within shapes such as the center of the letter 'O'.

        Underlying Processing method: PApplet.endContour

        Notes
        -----

        Use the `begin_contour()` and `end_contour()` methods to create negative shapes
        within shapes such as the center of the letter 'O'. The `begin_contour()` method
        begins recording vertices for the shape and `end_contour()` stops recording. The
        vertices that define a negative shape must "wind" in the opposite direction from
        the exterior shape. First draw vertices for the exterior shape in clockwise
        order, then for internal shapes, draw vertices counterclockwise.

        These methods can only be used within a `begin_shape()` & `end_shape()` pair and
        transformations such as `translate()`, `rotate()`, and `scale()` do not work
        within a `begin_contour()` & `end_contour()` pair. It is also not possible to
        use other shapes, such as `ellipse()` or `rect()` within.
        """
        return self._instance.endContour()

    def end_raw(self) -> None:
        """Complement to `begin_raw()`; they must always be used together.

        Underlying Processing method: PApplet.endRaw

        Notes
        -----

        Complement to `begin_raw()`; they must always be used together. See the
        `begin_raw()` reference for details.
        """
        return self._instance.endRaw()

    def end_record(self) -> None:
        """Stops the recording process started by `begin_record()` and closes the file.

        Underlying Processing method: PApplet.endRecord

        Notes
        -----

        Stops the recording process started by `begin_record()` and closes the file.
        """
        return self._instance.endRecord()

    @overload
    def end_shape(self) -> None:
        """The `end_shape()` function is the companion to `begin_shape()` and may only be
        called after `begin_shape()`.

        Underlying Processing method: PApplet.endShape

        Methods
        -------

        You can use any of the following signatures:

         * end_shape() -> None
         * end_shape(mode: int, /) -> None

        Parameters
        ----------

        mode: int
            use CLOSE to close the shape

        Notes
        -----

        The `end_shape()` function is the companion to `begin_shape()` and may only be
        called after `begin_shape()`. When `end_shape()` is called, all of image data
        defined since the previous call to `begin_shape()` is written into the image
        buffer. The constant `CLOSE` as the value for the `MODE` parameter to close the
        shape (to connect the beginning and the end).
        """
        pass

    @overload
    def end_shape(self, mode: int, /) -> None:
        """The `end_shape()` function is the companion to `begin_shape()` and may only be
        called after `begin_shape()`.

        Underlying Processing method: PApplet.endShape

        Methods
        -------

        You can use any of the following signatures:

         * end_shape() -> None
         * end_shape(mode: int, /) -> None

        Parameters
        ----------

        mode: int
            use CLOSE to close the shape

        Notes
        -----

        The `end_shape()` function is the companion to `begin_shape()` and may only be
        called after `begin_shape()`. When `end_shape()` is called, all of image data
        defined since the previous call to `begin_shape()` is written into the image
        buffer. The constant `CLOSE` as the value for the `MODE` parameter to close the
        shape (to connect the beginning and the end).
        """
        pass

    def end_shape(self, *args):
        """The `end_shape()` function is the companion to `begin_shape()` and may only be
        called after `begin_shape()`.

        Underlying Processing method: PApplet.endShape

        Methods
        -------

        You can use any of the following signatures:

         * end_shape() -> None
         * end_shape(mode: int, /) -> None

        Parameters
        ----------

        mode: int
            use CLOSE to close the shape

        Notes
        -----

        The `end_shape()` function is the companion to `begin_shape()` and may only be
        called after `begin_shape()`. When `end_shape()` is called, all of image data
        defined since the previous call to `begin_shape()` is written into the image
        buffer. The constant `CLOSE` as the value for the `MODE` parameter to close the
        shape (to connect the beginning and the end).
        """
        return self._instance.endShape(*args)

    def exit_sketch(self) -> None:
        """Quits/stops/exits the program.

        Underlying Processing method: PApplet.exit

        Notes
        -----

        Quits/stops/exits the program. Programs without a `draw()` function stop
        automatically after the last line has run, but programs with `draw()` run
        continuously until the program is manually stopped or `exit_sketch()` is run.

        Rather than terminating immediately, `exit_sketch()` will cause the Sketch to
        exit after `draw()` has completed (or after `setup()` completes if called during
        the `setup()` function).

        For Python programmers, this is *not* the same as `sys.exit()`. Further,
        `sys.exit()` should not be used because closing out an application while
        `draw()` is running may cause a crash (particularly with `P3D`).
        """
        return self._instance.exit()

    @overload
    def fill(self, gray: float, /) -> None:
        """Sets the color used to fill shapes.

        Underlying Processing method: PApplet.fill

        Methods
        -------

        You can use any of the following signatures:

         * fill(gray: float, /) -> None
         * fill(gray: float, alpha: float, /) -> None
         * fill(rgb: int, /) -> None
         * fill(rgb: int, alpha: float, /) -> None
         * fill(v1: float, v2: float, v3: float, /) -> None
         * fill(v1: float, v2: float, v3: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the fill

        gray: float
            number specifying value between white and black

        rgb: int
            color variable or hex value

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the color used to fill shapes. For example, if you run `fill(204, 102, 0)`,
        all subsequent shapes will be filled with orange. This color is either specified
        in terms of the `RGB` or `HSB` color depending on the current `color_mode()`.
        The default color space is `RGB`, with each value in the range from 0 to 255.

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

        To change the color of an image or a texture, use `tint()`.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def fill(self, gray: float, alpha: float, /) -> None:
        """Sets the color used to fill shapes.

        Underlying Processing method: PApplet.fill

        Methods
        -------

        You can use any of the following signatures:

         * fill(gray: float, /) -> None
         * fill(gray: float, alpha: float, /) -> None
         * fill(rgb: int, /) -> None
         * fill(rgb: int, alpha: float, /) -> None
         * fill(v1: float, v2: float, v3: float, /) -> None
         * fill(v1: float, v2: float, v3: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the fill

        gray: float
            number specifying value between white and black

        rgb: int
            color variable or hex value

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the color used to fill shapes. For example, if you run `fill(204, 102, 0)`,
        all subsequent shapes will be filled with orange. This color is either specified
        in terms of the `RGB` or `HSB` color depending on the current `color_mode()`.
        The default color space is `RGB`, with each value in the range from 0 to 255.

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

        To change the color of an image or a texture, use `tint()`.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def fill(self, v1: float, v2: float, v3: float, /) -> None:
        """Sets the color used to fill shapes.

        Underlying Processing method: PApplet.fill

        Methods
        -------

        You can use any of the following signatures:

         * fill(gray: float, /) -> None
         * fill(gray: float, alpha: float, /) -> None
         * fill(rgb: int, /) -> None
         * fill(rgb: int, alpha: float, /) -> None
         * fill(v1: float, v2: float, v3: float, /) -> None
         * fill(v1: float, v2: float, v3: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the fill

        gray: float
            number specifying value between white and black

        rgb: int
            color variable or hex value

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the color used to fill shapes. For example, if you run `fill(204, 102, 0)`,
        all subsequent shapes will be filled with orange. This color is either specified
        in terms of the `RGB` or `HSB` color depending on the current `color_mode()`.
        The default color space is `RGB`, with each value in the range from 0 to 255.

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

        To change the color of an image or a texture, use `tint()`.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def fill(self, v1: float, v2: float, v3: float, alpha: float, /) -> None:
        """Sets the color used to fill shapes.

        Underlying Processing method: PApplet.fill

        Methods
        -------

        You can use any of the following signatures:

         * fill(gray: float, /) -> None
         * fill(gray: float, alpha: float, /) -> None
         * fill(rgb: int, /) -> None
         * fill(rgb: int, alpha: float, /) -> None
         * fill(v1: float, v2: float, v3: float, /) -> None
         * fill(v1: float, v2: float, v3: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the fill

        gray: float
            number specifying value between white and black

        rgb: int
            color variable or hex value

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the color used to fill shapes. For example, if you run `fill(204, 102, 0)`,
        all subsequent shapes will be filled with orange. This color is either specified
        in terms of the `RGB` or `HSB` color depending on the current `color_mode()`.
        The default color space is `RGB`, with each value in the range from 0 to 255.

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

        To change the color of an image or a texture, use `tint()`.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def fill(self, rgb: int, /) -> None:
        """Sets the color used to fill shapes.

        Underlying Processing method: PApplet.fill

        Methods
        -------

        You can use any of the following signatures:

         * fill(gray: float, /) -> None
         * fill(gray: float, alpha: float, /) -> None
         * fill(rgb: int, /) -> None
         * fill(rgb: int, alpha: float, /) -> None
         * fill(v1: float, v2: float, v3: float, /) -> None
         * fill(v1: float, v2: float, v3: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the fill

        gray: float
            number specifying value between white and black

        rgb: int
            color variable or hex value

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the color used to fill shapes. For example, if you run `fill(204, 102, 0)`,
        all subsequent shapes will be filled with orange. This color is either specified
        in terms of the `RGB` or `HSB` color depending on the current `color_mode()`.
        The default color space is `RGB`, with each value in the range from 0 to 255.

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

        To change the color of an image or a texture, use `tint()`.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def fill(self, rgb: int, alpha: float, /) -> None:
        """Sets the color used to fill shapes.

        Underlying Processing method: PApplet.fill

        Methods
        -------

        You can use any of the following signatures:

         * fill(gray: float, /) -> None
         * fill(gray: float, alpha: float, /) -> None
         * fill(rgb: int, /) -> None
         * fill(rgb: int, alpha: float, /) -> None
         * fill(v1: float, v2: float, v3: float, /) -> None
         * fill(v1: float, v2: float, v3: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the fill

        gray: float
            number specifying value between white and black

        rgb: int
            color variable or hex value

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the color used to fill shapes. For example, if you run `fill(204, 102, 0)`,
        all subsequent shapes will be filled with orange. This color is either specified
        in terms of the `RGB` or `HSB` color depending on the current `color_mode()`.
        The default color space is `RGB`, with each value in the range from 0 to 255.

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

        To change the color of an image or a texture, use `tint()`.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @_convert_hex_color()
    def fill(self, *args):
        """Sets the color used to fill shapes.

        Underlying Processing method: PApplet.fill

        Methods
        -------

        You can use any of the following signatures:

         * fill(gray: float, /) -> None
         * fill(gray: float, alpha: float, /) -> None
         * fill(rgb: int, /) -> None
         * fill(rgb: int, alpha: float, /) -> None
         * fill(v1: float, v2: float, v3: float, /) -> None
         * fill(v1: float, v2: float, v3: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the fill

        gray: float
            number specifying value between white and black

        rgb: int
            color variable or hex value

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the color used to fill shapes. For example, if you run `fill(204, 102, 0)`,
        all subsequent shapes will be filled with orange. This color is either specified
        in terms of the `RGB` or `HSB` color depending on the current `color_mode()`.
        The default color space is `RGB`, with each value in the range from 0 to 255.

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

        To change the color of an image or a texture, use `tint()`.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        return self._instance.fill(*args)

    @overload
    def apply_filter(self, kind: int, /) -> None:
        """Filters the display window using a preset filter or with a custom shader.

        Underlying Processing method: PApplet.filter

        Methods
        -------

        You can use any of the following signatures:

         * apply_filter(kind: int, /) -> None
         * apply_filter(kind: int, param: float, /) -> None
         * apply_filter(shader: Py5Shader, /) -> None

        Parameters
        ----------

        kind: int
            Either THRESHOLD, GRAY, OPAQUE, INVERT, POSTERIZE, BLUR, ERODE, or DILATE

        param: float
            unique for each, see above

        shader: Py5Shader
            the fragment shader to apply

        Notes
        -----

        Filters the display window using a preset filter or with a custom shader. Using
        a shader with `apply_filter()` is much faster than without. Shaders require the
        `P2D` or `P3D` renderer in `size()`.

        The presets options are:

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
        * BLUR: Executes a Guassian blur with the level parameter specifying the extent
        of the blurring. If no parameter is used, the blur is equivalent to Guassian
        blur of radius 1. Larger values increase the blur.
        * ERODE: Reduces the light areas. No parameter is used.
        * DILATE: Increases the light areas. No parameter is used.
        """
        pass

    @overload
    def apply_filter(self, kind: int, param: float, /) -> None:
        """Filters the display window using a preset filter or with a custom shader.

        Underlying Processing method: PApplet.filter

        Methods
        -------

        You can use any of the following signatures:

         * apply_filter(kind: int, /) -> None
         * apply_filter(kind: int, param: float, /) -> None
         * apply_filter(shader: Py5Shader, /) -> None

        Parameters
        ----------

        kind: int
            Either THRESHOLD, GRAY, OPAQUE, INVERT, POSTERIZE, BLUR, ERODE, or DILATE

        param: float
            unique for each, see above

        shader: Py5Shader
            the fragment shader to apply

        Notes
        -----

        Filters the display window using a preset filter or with a custom shader. Using
        a shader with `apply_filter()` is much faster than without. Shaders require the
        `P2D` or `P3D` renderer in `size()`.

        The presets options are:

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
        * BLUR: Executes a Guassian blur with the level parameter specifying the extent
        of the blurring. If no parameter is used, the blur is equivalent to Guassian
        blur of radius 1. Larger values increase the blur.
        * ERODE: Reduces the light areas. No parameter is used.
        * DILATE: Increases the light areas. No parameter is used.
        """
        pass

    @overload
    def apply_filter(self, shader: Py5Shader, /) -> None:
        """Filters the display window using a preset filter or with a custom shader.

        Underlying Processing method: PApplet.filter

        Methods
        -------

        You can use any of the following signatures:

         * apply_filter(kind: int, /) -> None
         * apply_filter(kind: int, param: float, /) -> None
         * apply_filter(shader: Py5Shader, /) -> None

        Parameters
        ----------

        kind: int
            Either THRESHOLD, GRAY, OPAQUE, INVERT, POSTERIZE, BLUR, ERODE, or DILATE

        param: float
            unique for each, see above

        shader: Py5Shader
            the fragment shader to apply

        Notes
        -----

        Filters the display window using a preset filter or with a custom shader. Using
        a shader with `apply_filter()` is much faster than without. Shaders require the
        `P2D` or `P3D` renderer in `size()`.

        The presets options are:

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
        * BLUR: Executes a Guassian blur with the level parameter specifying the extent
        of the blurring. If no parameter is used, the blur is equivalent to Guassian
        blur of radius 1. Larger values increase the blur.
        * ERODE: Reduces the light areas. No parameter is used.
        * DILATE: Increases the light areas. No parameter is used.
        """
        pass

    def apply_filter(self, *args):
        """Filters the display window using a preset filter or with a custom shader.

        Underlying Processing method: PApplet.filter

        Methods
        -------

        You can use any of the following signatures:

         * apply_filter(kind: int, /) -> None
         * apply_filter(kind: int, param: float, /) -> None
         * apply_filter(shader: Py5Shader, /) -> None

        Parameters
        ----------

        kind: int
            Either THRESHOLD, GRAY, OPAQUE, INVERT, POSTERIZE, BLUR, ERODE, or DILATE

        param: float
            unique for each, see above

        shader: Py5Shader
            the fragment shader to apply

        Notes
        -----

        Filters the display window using a preset filter or with a custom shader. Using
        a shader with `apply_filter()` is much faster than without. Shaders require the
        `P2D` or `P3D` renderer in `size()`.

        The presets options are:

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
        * BLUR: Executes a Guassian blur with the level parameter specifying the extent
        of the blurring. If no parameter is used, the blur is equivalent to Guassian
        blur of radius 1. Larger values increase the blur.
        * ERODE: Reduces the light areas. No parameter is used.
        * DILATE: Increases the light areas. No parameter is used.
        """
        return self._instance.filter(*args)

    def flush(self) -> None:
        """Flush drawing commands to the renderer.

        Underlying Processing method: Sketch.flush

        Notes
        -----

        Flush drawing commands to the renderer. For most renderers, this method does
        absolutely nothing. There are not a lot of good reasons to use this method, but
        if you need it, it is available for your use.
        """
        return self._instance.flush()

    def frame_rate(self, fps: float, /) -> None:
        """Specifies the number of frames to be displayed every second.

        Underlying Processing method: PApplet.frameRate

        Parameters
        ----------

        fps: float
            number of desired frames per second

        Notes
        -----

        Specifies the number of frames to be displayed every second. For example, the
        function call `frame_rate(30)` will attempt to refresh 30 times a second. If the
        processor is not fast enough to maintain the specified rate, the frame rate will
        not be achieved. Setting the frame rate within `setup()` is recommended. The
        default rate is 60 frames per second.
        """
        return self._instance.frameRate(fps)

    def frustum(
        self,
        left: float,
        right: float,
        bottom: float,
        top: float,
        near: float,
        far: float,
        /,
    ) -> None:
        """Sets a perspective matrix as defined by the parameters.

        Underlying Processing method: PApplet.frustum

        Parameters
        ----------

        bottom: float
            bottom coordinate of the clipping plane

        far: float
            far component of the clipping plane; must be greater than the near value

        left: float
            left coordinate of the clipping plane

        near: float
            near component of the clipping plane; must be greater than zero

        right: float
            right coordinate of the clipping plane

        top: float
            top coordinate of the clipping plane

        Notes
        -----

        Sets a perspective matrix as defined by the parameters.

        A frustum is a geometric form: a pyramid with its top cut off.  With the
        viewer's eye at the imaginary top of the pyramid, the six planes of the frustum
        act as clipping planes when rendering a 3D view.  Thus, any form inside the
        clipping planes is rendered and visible; anything outside those planes is not
        visible.

        Setting the frustum has the effect of changing the *perspective* with which the
        scene is rendered.  This can be achieved more simply in many cases by using
        `perspective()`.

        Note that the near value must be greater than zero (as the point of the frustum
        "pyramid" cannot converge "behind" the viewer).  Similarly, the far value must
        be greater than the near value (as the "far" plane of the frustum must be
        "farther away" from the viewer than the near plane).

        Works like glFrustum, except it wipes out the current perspective matrix rather
        than multiplying itself with it.
        """
        return self._instance.frustum(left, right, bottom, top, near, far)

    @overload
    def full_screen(self) -> None:
        """Open a Sketch using the full size of the computer's display.

        Underlying Processing method: PApplet.fullScreen

        Methods
        -------

        You can use any of the following signatures:

         * full_screen() -> None
         * full_screen(display: int, /) -> None
         * full_screen(renderer: str, /) -> None
         * full_screen(renderer: str, display: int, /) -> None

        Parameters
        ----------

        display: int
            the screen to run the Sketch on (1, 2, 3, etc. or on multiple screens using SPAN)

        renderer: str
            the renderer to use, e.g. P2D, P3D, JAVA2D (default)

        Notes
        -----

        Open a Sketch using the full size of the computer's display. This is intended to
        be called from the `settings()` function. The `size()` and `full_screen()`
        functions cannot both be used in the same program.

        When programming in module mode and imported mode, py5 will allow calls to
        `full_screen()` from the `setup()` function if it is called at the beginning of
        `setup()`. This allows the user to omit the `settings()` function, much like
        what can be done while programming in the Processing IDE. Py5 does this by
        inspecting the `setup()` function and attempting to split it into synthetic
        `settings()` and `setup()` functions if both were not created by the user and
        the real `setup()` function contains a call to `full_screen()`, or calls to
        `size()`, `smooth()`, `no_smooth()`, or `pixel_density()`. Calls to those
        functions must be at the very beginning of `setup()`, before any other Python
        code (but comments are ok). This feature is not available when programming in
        class mode.

        When `full_screen()` is used without a parameter on a computer with multiple
        monitors, it will (probably) draw the Sketch to the primary display. When it is
        used with a single parameter, this number defines the screen to display to
        program on (e.g. 1, 2, 3...). When used with two parameters, the first defines
        the renderer to use (e.g. P2D) and the second defines the screen. The `SPAN`
        parameter can be used in place of a screen number to draw the Sketch as a full-
        screen window across all of the attached displays if there are more than one.
        """
        pass

    @overload
    def full_screen(self, display: int, /) -> None:
        """Open a Sketch using the full size of the computer's display.

        Underlying Processing method: PApplet.fullScreen

        Methods
        -------

        You can use any of the following signatures:

         * full_screen() -> None
         * full_screen(display: int, /) -> None
         * full_screen(renderer: str, /) -> None
         * full_screen(renderer: str, display: int, /) -> None

        Parameters
        ----------

        display: int
            the screen to run the Sketch on (1, 2, 3, etc. or on multiple screens using SPAN)

        renderer: str
            the renderer to use, e.g. P2D, P3D, JAVA2D (default)

        Notes
        -----

        Open a Sketch using the full size of the computer's display. This is intended to
        be called from the `settings()` function. The `size()` and `full_screen()`
        functions cannot both be used in the same program.

        When programming in module mode and imported mode, py5 will allow calls to
        `full_screen()` from the `setup()` function if it is called at the beginning of
        `setup()`. This allows the user to omit the `settings()` function, much like
        what can be done while programming in the Processing IDE. Py5 does this by
        inspecting the `setup()` function and attempting to split it into synthetic
        `settings()` and `setup()` functions if both were not created by the user and
        the real `setup()` function contains a call to `full_screen()`, or calls to
        `size()`, `smooth()`, `no_smooth()`, or `pixel_density()`. Calls to those
        functions must be at the very beginning of `setup()`, before any other Python
        code (but comments are ok). This feature is not available when programming in
        class mode.

        When `full_screen()` is used without a parameter on a computer with multiple
        monitors, it will (probably) draw the Sketch to the primary display. When it is
        used with a single parameter, this number defines the screen to display to
        program on (e.g. 1, 2, 3...). When used with two parameters, the first defines
        the renderer to use (e.g. P2D) and the second defines the screen. The `SPAN`
        parameter can be used in place of a screen number to draw the Sketch as a full-
        screen window across all of the attached displays if there are more than one.
        """
        pass

    @overload
    def full_screen(self, renderer: str, /) -> None:
        """Open a Sketch using the full size of the computer's display.

        Underlying Processing method: PApplet.fullScreen

        Methods
        -------

        You can use any of the following signatures:

         * full_screen() -> None
         * full_screen(display: int, /) -> None
         * full_screen(renderer: str, /) -> None
         * full_screen(renderer: str, display: int, /) -> None

        Parameters
        ----------

        display: int
            the screen to run the Sketch on (1, 2, 3, etc. or on multiple screens using SPAN)

        renderer: str
            the renderer to use, e.g. P2D, P3D, JAVA2D (default)

        Notes
        -----

        Open a Sketch using the full size of the computer's display. This is intended to
        be called from the `settings()` function. The `size()` and `full_screen()`
        functions cannot both be used in the same program.

        When programming in module mode and imported mode, py5 will allow calls to
        `full_screen()` from the `setup()` function if it is called at the beginning of
        `setup()`. This allows the user to omit the `settings()` function, much like
        what can be done while programming in the Processing IDE. Py5 does this by
        inspecting the `setup()` function and attempting to split it into synthetic
        `settings()` and `setup()` functions if both were not created by the user and
        the real `setup()` function contains a call to `full_screen()`, or calls to
        `size()`, `smooth()`, `no_smooth()`, or `pixel_density()`. Calls to those
        functions must be at the very beginning of `setup()`, before any other Python
        code (but comments are ok). This feature is not available when programming in
        class mode.

        When `full_screen()` is used without a parameter on a computer with multiple
        monitors, it will (probably) draw the Sketch to the primary display. When it is
        used with a single parameter, this number defines the screen to display to
        program on (e.g. 1, 2, 3...). When used with two parameters, the first defines
        the renderer to use (e.g. P2D) and the second defines the screen. The `SPAN`
        parameter can be used in place of a screen number to draw the Sketch as a full-
        screen window across all of the attached displays if there are more than one.
        """
        pass

    @overload
    def full_screen(self, renderer: str, display: int, /) -> None:
        """Open a Sketch using the full size of the computer's display.

        Underlying Processing method: PApplet.fullScreen

        Methods
        -------

        You can use any of the following signatures:

         * full_screen() -> None
         * full_screen(display: int, /) -> None
         * full_screen(renderer: str, /) -> None
         * full_screen(renderer: str, display: int, /) -> None

        Parameters
        ----------

        display: int
            the screen to run the Sketch on (1, 2, 3, etc. or on multiple screens using SPAN)

        renderer: str
            the renderer to use, e.g. P2D, P3D, JAVA2D (default)

        Notes
        -----

        Open a Sketch using the full size of the computer's display. This is intended to
        be called from the `settings()` function. The `size()` and `full_screen()`
        functions cannot both be used in the same program.

        When programming in module mode and imported mode, py5 will allow calls to
        `full_screen()` from the `setup()` function if it is called at the beginning of
        `setup()`. This allows the user to omit the `settings()` function, much like
        what can be done while programming in the Processing IDE. Py5 does this by
        inspecting the `setup()` function and attempting to split it into synthetic
        `settings()` and `setup()` functions if both were not created by the user and
        the real `setup()` function contains a call to `full_screen()`, or calls to
        `size()`, `smooth()`, `no_smooth()`, or `pixel_density()`. Calls to those
        functions must be at the very beginning of `setup()`, before any other Python
        code (but comments are ok). This feature is not available when programming in
        class mode.

        When `full_screen()` is used without a parameter on a computer with multiple
        monitors, it will (probably) draw the Sketch to the primary display. When it is
        used with a single parameter, this number defines the screen to display to
        program on (e.g. 1, 2, 3...). When used with two parameters, the first defines
        the renderer to use (e.g. P2D) and the second defines the screen. The `SPAN`
        parameter can be used in place of a screen number to draw the Sketch as a full-
        screen window across all of the attached displays if there are more than one.
        """
        pass

    @_settings_only("full_screen")
    def full_screen(self, *args):
        """Open a Sketch using the full size of the computer's display.

        Underlying Processing method: PApplet.fullScreen

        Methods
        -------

        You can use any of the following signatures:

         * full_screen() -> None
         * full_screen(display: int, /) -> None
         * full_screen(renderer: str, /) -> None
         * full_screen(renderer: str, display: int, /) -> None

        Parameters
        ----------

        display: int
            the screen to run the Sketch on (1, 2, 3, etc. or on multiple screens using SPAN)

        renderer: str
            the renderer to use, e.g. P2D, P3D, JAVA2D (default)

        Notes
        -----

        Open a Sketch using the full size of the computer's display. This is intended to
        be called from the `settings()` function. The `size()` and `full_screen()`
        functions cannot both be used in the same program.

        When programming in module mode and imported mode, py5 will allow calls to
        `full_screen()` from the `setup()` function if it is called at the beginning of
        `setup()`. This allows the user to omit the `settings()` function, much like
        what can be done while programming in the Processing IDE. Py5 does this by
        inspecting the `setup()` function and attempting to split it into synthetic
        `settings()` and `setup()` functions if both were not created by the user and
        the real `setup()` function contains a call to `full_screen()`, or calls to
        `size()`, `smooth()`, `no_smooth()`, or `pixel_density()`. Calls to those
        functions must be at the very beginning of `setup()`, before any other Python
        code (but comments are ok). This feature is not available when programming in
        class mode.

        When `full_screen()` is used without a parameter on a computer with multiple
        monitors, it will (probably) draw the Sketch to the primary display. When it is
        used with a single parameter, this number defines the screen to display to
        program on (e.g. 1, 2, 3...). When used with two parameters, the first defines
        the renderer to use (e.g. P2D) and the second defines the screen. The `SPAN`
        parameter can be used in place of a screen number to draw the Sketch as a full-
        screen window across all of the attached displays if there are more than one.
        """
        return self._instance.fullScreen(*args)

    @overload
    def get_pixels(self) -> Py5Image:
        """Reads the color of any pixel or grabs a section of the drawing surface.

        Underlying Processing method: PApplet.get

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

        Reads the color of any pixel or grabs a section of the drawing surface. If no
        parameters are specified, the entire drawing surface is returned. Use the `x`
        and `y` parameters to get the value of one pixel. Get a section of the display
        window by specifying additional `w` and `h` parameters. When getting an image,
        the `x` and `y` parameters define the coordinates for the upper-left corner of
        the returned image, regardless of the current `image_mode()`.

        If the pixel requested is outside of the image window, black is returned. The
        numbers returned are scaled according to the current color ranges, but only
        `RGB` values are returned by this function. For example, even though you may
        have drawn a shape with `color_mode(HSB)`, the numbers returned will be in `RGB`
        format.

        If a width and a height are specified, `get_pixels(x, y, w, h)` returns a
        Py5Image corresponding to the part of the original Py5Image where the top left
        pixel is at the `(x, y)` position with a width of `w` a height of `h`.

        Getting the color of a single pixel with `get_pixels(x, y)` is easy, but not as
        fast as grabbing the data directly from `pixels[]` or `np_pixels[]`. The
        equivalent statement to `get_pixels(x, y)` using `pixels[]` is
        `pixels[y*width+x]`. Using `np_pixels[]` it is `np_pixels[y, x]`. See the
        reference for `pixels[]` and `np_pixels[]` for more information.
        """
        pass

    @overload
    def get_pixels(self, x: int, y: int, /) -> int:
        """Reads the color of any pixel or grabs a section of the drawing surface.

        Underlying Processing method: PApplet.get

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

        Reads the color of any pixel or grabs a section of the drawing surface. If no
        parameters are specified, the entire drawing surface is returned. Use the `x`
        and `y` parameters to get the value of one pixel. Get a section of the display
        window by specifying additional `w` and `h` parameters. When getting an image,
        the `x` and `y` parameters define the coordinates for the upper-left corner of
        the returned image, regardless of the current `image_mode()`.

        If the pixel requested is outside of the image window, black is returned. The
        numbers returned are scaled according to the current color ranges, but only
        `RGB` values are returned by this function. For example, even though you may
        have drawn a shape with `color_mode(HSB)`, the numbers returned will be in `RGB`
        format.

        If a width and a height are specified, `get_pixels(x, y, w, h)` returns a
        Py5Image corresponding to the part of the original Py5Image where the top left
        pixel is at the `(x, y)` position with a width of `w` a height of `h`.

        Getting the color of a single pixel with `get_pixels(x, y)` is easy, but not as
        fast as grabbing the data directly from `pixels[]` or `np_pixels[]`. The
        equivalent statement to `get_pixels(x, y)` using `pixels[]` is
        `pixels[y*width+x]`. Using `np_pixels[]` it is `np_pixels[y, x]`. See the
        reference for `pixels[]` and `np_pixels[]` for more information.
        """
        pass

    @overload
    def get_pixels(self, x: int, y: int, w: int, h: int, /) -> Py5Image:
        """Reads the color of any pixel or grabs a section of the drawing surface.

        Underlying Processing method: PApplet.get

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

        Reads the color of any pixel or grabs a section of the drawing surface. If no
        parameters are specified, the entire drawing surface is returned. Use the `x`
        and `y` parameters to get the value of one pixel. Get a section of the display
        window by specifying additional `w` and `h` parameters. When getting an image,
        the `x` and `y` parameters define the coordinates for the upper-left corner of
        the returned image, regardless of the current `image_mode()`.

        If the pixel requested is outside of the image window, black is returned. The
        numbers returned are scaled according to the current color ranges, but only
        `RGB` values are returned by this function. For example, even though you may
        have drawn a shape with `color_mode(HSB)`, the numbers returned will be in `RGB`
        format.

        If a width and a height are specified, `get_pixels(x, y, w, h)` returns a
        Py5Image corresponding to the part of the original Py5Image where the top left
        pixel is at the `(x, y)` position with a width of `w` a height of `h`.

        Getting the color of a single pixel with `get_pixels(x, y)` is easy, but not as
        fast as grabbing the data directly from `pixels[]` or `np_pixels[]`. The
        equivalent statement to `get_pixels(x, y)` using `pixels[]` is
        `pixels[y*width+x]`. Using `np_pixels[]` it is `np_pixels[y, x]`. See the
        reference for `pixels[]` and `np_pixels[]` for more information.
        """
        pass

    @_return_py5image
    def get_pixels(self, *args):
        """Reads the color of any pixel or grabs a section of the drawing surface.

        Underlying Processing method: PApplet.get

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

        Reads the color of any pixel or grabs a section of the drawing surface. If no
        parameters are specified, the entire drawing surface is returned. Use the `x`
        and `y` parameters to get the value of one pixel. Get a section of the display
        window by specifying additional `w` and `h` parameters. When getting an image,
        the `x` and `y` parameters define the coordinates for the upper-left corner of
        the returned image, regardless of the current `image_mode()`.

        If the pixel requested is outside of the image window, black is returned. The
        numbers returned are scaled according to the current color ranges, but only
        `RGB` values are returned by this function. For example, even though you may
        have drawn a shape with `color_mode(HSB)`, the numbers returned will be in `RGB`
        format.

        If a width and a height are specified, `get_pixels(x, y, w, h)` returns a
        Py5Image corresponding to the part of the original Py5Image where the top left
        pixel is at the `(x, y)` position with a width of `w` a height of `h`.

        Getting the color of a single pixel with `get_pixels(x, y)` is easy, but not as
        fast as grabbing the data directly from `pixels[]` or `np_pixels[]`. The
        equivalent statement to `get_pixels(x, y)` using `pixels[]` is
        `pixels[y*width+x]`. Using `np_pixels[]` it is `np_pixels[y, x]`. See the
        reference for `pixels[]` and `np_pixels[]` for more information.
        """
        return self._instance.get(*args)

    def get_frame_rate(self) -> float:
        """Get the running Sketch's current frame rate.

        Notes
        -----

        Get the running Sketch's current frame rate. This is measured in frames per
        second (fps) and uses an exponential moving average. The returned value will not
        be accurate until after the Sketch has run for a few seconds. You can set the
        target frame rate with `frame_rate()`.

        This method provides the same information as Processing's `frameRate` variable.
        Python can't have a variable and a method with the same name, so a new method
        was created to provide access to that variable.
        """
        return self._instance.getFrameRate()

    @_return_py5graphics
    def get_graphics(self) -> Py5Graphics:
        """Get the `Py5Graphics` object used by the Sketch.

        Underlying Processing method: PApplet.getGraphics

        Notes
        -----

        Get the `Py5Graphics` object used by the Sketch. Internally, all of Processing's
        drawing functionality comes from interaction with PGraphics objects, and this
        will provide direct access to the PGraphics object used by the Sketch.
        """
        return self._instance.getGraphics()

    @overload
    def get_matrix(self) -> npt.NDArray[np.floating]:
        """Get the current matrix as a numpy array.

        Underlying Processing method: PApplet.getMatrix

        Methods
        -------

        You can use any of the following signatures:

         * get_matrix() -> npt.NDArray[np.floating]
         * get_matrix(target: npt.NDArray[np.floating], /) -> npt.NDArray[np.floating]

        Parameters
        ----------

        target: npt.NDArray[np.floating]
            transformation matrix with a shape of 2x3 for 2D transforms or 4x4 for 3D transforms

        Notes
        -----

        Get the current matrix as a numpy array. Use the `target` parameter to put the
        matrix data in a properly sized and typed numpy array.
        """
        pass

    @overload
    def get_matrix(
        self, target: npt.NDArray[np.floating], /
    ) -> npt.NDArray[np.floating]:
        """Get the current matrix as a numpy array.

        Underlying Processing method: PApplet.getMatrix

        Methods
        -------

        You can use any of the following signatures:

         * get_matrix() -> npt.NDArray[np.floating]
         * get_matrix(target: npt.NDArray[np.floating], /) -> npt.NDArray[np.floating]

        Parameters
        ----------

        target: npt.NDArray[np.floating]
            transformation matrix with a shape of 2x3 for 2D transforms or 4x4 for 3D transforms

        Notes
        -----

        Get the current matrix as a numpy array. Use the `target` parameter to put the
        matrix data in a properly sized and typed numpy array.
        """
        pass

    @_get_matrix_wrapper
    def get_matrix(self, *args):
        """Get the current matrix as a numpy array.

        Underlying Processing method: PApplet.getMatrix

        Methods
        -------

        You can use any of the following signatures:

         * get_matrix() -> npt.NDArray[np.floating]
         * get_matrix(target: npt.NDArray[np.floating], /) -> npt.NDArray[np.floating]

        Parameters
        ----------

        target: npt.NDArray[np.floating]
            transformation matrix with a shape of 2x3 for 2D transforms or 4x4 for 3D transforms

        Notes
        -----

        Get the current matrix as a numpy array. Use the `target` parameter to put the
        matrix data in a properly sized and typed numpy array.
        """
        return self._instance.getMatrix(*args)

    @_return_py5surface
    def get_surface(self) -> Py5Surface:
        """Get the `Py5Surface` object used for the Sketch.

        Underlying Processing method: PApplet.getSurface

        Notes
        -----

        Get the `Py5Surface` object used for the Sketch.
        """
        return self._instance.getSurface()

    @_convert_hex_color()
    def green(self, rgb: int, /) -> float:
        """Extracts the green value from a color, scaled to match current `color_mode()`.

        Underlying Processing method: PApplet.green

        Parameters
        ----------

        rgb: int
            any value of the color datatype

        Notes
        -----

        Extracts the green value from a color, scaled to match current `color_mode()`.

        The `green()` function is easy to use and understand, but it is slower than a
        technique called bit shifting. When working in `color_mode(RGB, 255)`, you can
        achieve the same results as `green()` but with greater speed by using the right
        shift operator (`>>`) with a bit mask. For example, `green(c)` and `c >> 8 &
        0xFF` both extract the green value from a color variable `c` but the later is
        faster.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        return self._instance.green(rgb)

    def hint(self, which: int, /) -> None:
        """This function is used to enable or disable special features that control how
        graphics are drawn.

        Underlying Processing method: PApplet.hint

        Parameters
        ----------

        which: int
            hint to use when rendering Sketch

        Notes
        -----

        This function is used to enable or disable special features that control how
        graphics are drawn. In the course of developing Processing, the developers had
        to make hard decisions about tradeoffs between performance and visual quality.
        They put significant effort into determining what makes most sense for the
        largest number of users, and then use functions like `hint()` to allow people to
        tune the settings for their particular Sketch. Implementing a `hint()` is a last
        resort that's used when a more elegant solution cannot be found. Some options
        might graduate to standard features instead of hints over time, or be added and
        removed between (major) releases.

        Hints used by the Default Renderer
        ----------------------------------

        * `ENABLE_STROKE_PURE`: Fixes a problem with shapes that have a stroke and are
        rendered using small steps (for instance, using `vertex()` with points that are
        close to one another), or are drawn at small sizes.

        Hints for use with `P2D` and `P3D`
        --------------------------------------

        * `DISABLE_OPENGL_ERRORS`: Speeds up the `P3D` renderer setting by not checking
        for errors while running.
        * `DISABLE_TEXTURE_MIPMAPS`: Disable generation of texture mipmaps in `P2D` or
        `P3D`. This results in lower quality - but faster - rendering of texture images
        when they appear smaller than their native resolutions (the mipmaps are scaled-
        down versions of a texture that make it look better when drawing it at a small
        size). However, the difference in performance is fairly minor on recent desktop
        video cards.


        Hints for use with `P3D` only
        -------------------------------

        * `DISABLE_DEPTH_MASK`: Disables writing into the depth buffer. This means that
        a shape drawn with this hint can be hidden by another shape drawn later,
        irrespective of their distances to the camera. Note that this is different from
        disabling the depth test. The depth test is still applied, as long as the
        `DISABLE_DEPTH_TEST` hint is not called, but the depth values of the objects are
        not recorded. This is useful when drawing a semi-transparent 3D object without
        depth sorting, in order to avoid visual glitches due the faces of the object
        being at different distances from the camera, but still having the object
        properly occluded by the rest of the objects in the scene.
        * `ENABLE_DEPTH_SORT`: Enable primitive z-sorting of triangles and lines in
        `P3D`. This can slow performance considerably, and the algorithm is not yet
        perfect.
        * `DISABLE_DEPTH_TEST`: Disable the zbuffer, allowing you to draw on top of
        everything at will. When depth testing is disabled, items will be drawn to the
        screen sequentially, like a painting. This hint is most often used to draw in
        3D, then draw in 2D on top of it (for instance, to draw GUI controls in 2D on
        top of a 3D interface). When called, this will also clear the depth buffer.
        Restore the default with `hint(ENABLE_DEPTH_TEST)`, but note that with the depth
        buffer cleared, any 3D drawing that happens later in will ignore existing shapes
        on the screen.
        * `DISABLE_OPTIMIZED_STROKE`: Forces the `P3D` renderer to draw each shape
        (including its strokes) separately, instead of batching them into larger groups
        for better performance. One consequence of this is that 2D items drawn with
        `P3D` are correctly stacked on the screen, depending on the order in which they
        were drawn. Otherwise, glitches such as the stroke lines being drawn on top of
        the interior of all the shapes will occur. However, this hint can make rendering
        substantially slower, so it is recommended to use it only when drawing a small
        amount of shapes. For drawing two-dimensional scenes, use the `P2D` renderer
        instead, which doesn't need the hint to properly stack shapes and their strokes.
        * `ENABLE_STROKE_PERSPECTIVE`: Enables stroke geometry (lines and points) to be
        affected by the perspective, meaning that they will look smaller as they move
        away from the camera.
        """
        return self._instance.hint(which)

    @classmethod
    def hour(cls) -> int:
        """Py5 communicates with the clock on your computer.

        Underlying Processing method: PApplet.hour

        Notes
        -----

        Py5 communicates with the clock on your computer. The `hour()` function returns
        the current hour as a value from 0 - 23.
        """
        return cls._cls.hour()

    @_convert_hex_color()
    def hue(self, rgb: int, /) -> float:
        """Extracts the hue value from a color.

        Underlying Processing method: PApplet.hue

        Parameters
        ----------

        rgb: int
            any value of the color datatype

        Notes
        -----

        Extracts the hue value from a color.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        return self._instance.hue(rgb)

    @overload
    def image(self, img: Py5Image, a: float, b: float, /) -> None:
        """The `image()` function draws an image to the display window.

        Underlying Processing method: PApplet.image

        Methods
        -------

        You can use any of the following signatures:

         * image(img: Py5Image, a: float, b: float, /) -> None
         * image(img: Py5Image, a: float, b: float, c: float, d: float, /) -> None
         * image(img: Py5Image, a: float, b: float, c: float, d: float, u1: int, v1: int, u2: int, v2: int, /) -> None

        Parameters
        ----------

        a: float
            x-coordinate of the image by default

        b: float
            y-coordinate of the image by default

        c: float
            width to display the image by default

        d: float
            height to display the image by default

        img: Py5Image
            the image to display

        u1: int
            x-coordinate of the upper left corner of image subset

        u2: int
            x-coordinate of the lower right corner of image subset

        v1: int
            y-coordinate of the upper left corner of image subset

        v2: int
            y-coordinate of the lower right corner of image subset

        Notes
        -----

        The `image()` function draws an image to the display window. Images must be in
        the Sketch's "data" directory to load correctly. Py5 currently works with GIF,
        JPEG, and PNG images.

        The `img` parameter specifies the image to display and by default the `a` and
        `b` parameters define the location of its upper-left corner. The image is
        displayed at its original size unless the `c` and `d` parameters specify a
        different size. The `image_mode()` function can be used to change the way these
        parameters draw the image.

        Use the `u1`, `u2`, `v1`, and `v2` parameters to use only a subset of the image.
        These values are always specified in image space location, regardless of the
        current `texture_mode()` setting.

        The color of an image may be modified with the `tint()` function. This function
        will maintain transparency for GIF and PNG images.
        """
        pass

    @overload
    def image(self, img: Py5Image, a: float, b: float, c: float, d: float, /) -> None:
        """The `image()` function draws an image to the display window.

        Underlying Processing method: PApplet.image

        Methods
        -------

        You can use any of the following signatures:

         * image(img: Py5Image, a: float, b: float, /) -> None
         * image(img: Py5Image, a: float, b: float, c: float, d: float, /) -> None
         * image(img: Py5Image, a: float, b: float, c: float, d: float, u1: int, v1: int, u2: int, v2: int, /) -> None

        Parameters
        ----------

        a: float
            x-coordinate of the image by default

        b: float
            y-coordinate of the image by default

        c: float
            width to display the image by default

        d: float
            height to display the image by default

        img: Py5Image
            the image to display

        u1: int
            x-coordinate of the upper left corner of image subset

        u2: int
            x-coordinate of the lower right corner of image subset

        v1: int
            y-coordinate of the upper left corner of image subset

        v2: int
            y-coordinate of the lower right corner of image subset

        Notes
        -----

        The `image()` function draws an image to the display window. Images must be in
        the Sketch's "data" directory to load correctly. Py5 currently works with GIF,
        JPEG, and PNG images.

        The `img` parameter specifies the image to display and by default the `a` and
        `b` parameters define the location of its upper-left corner. The image is
        displayed at its original size unless the `c` and `d` parameters specify a
        different size. The `image_mode()` function can be used to change the way these
        parameters draw the image.

        Use the `u1`, `u2`, `v1`, and `v2` parameters to use only a subset of the image.
        These values are always specified in image space location, regardless of the
        current `texture_mode()` setting.

        The color of an image may be modified with the `tint()` function. This function
        will maintain transparency for GIF and PNG images.
        """
        pass

    @overload
    def image(
        self,
        img: Py5Image,
        a: float,
        b: float,
        c: float,
        d: float,
        u1: int,
        v1: int,
        u2: int,
        v2: int,
        /,
    ) -> None:
        """The `image()` function draws an image to the display window.

        Underlying Processing method: PApplet.image

        Methods
        -------

        You can use any of the following signatures:

         * image(img: Py5Image, a: float, b: float, /) -> None
         * image(img: Py5Image, a: float, b: float, c: float, d: float, /) -> None
         * image(img: Py5Image, a: float, b: float, c: float, d: float, u1: int, v1: int, u2: int, v2: int, /) -> None

        Parameters
        ----------

        a: float
            x-coordinate of the image by default

        b: float
            y-coordinate of the image by default

        c: float
            width to display the image by default

        d: float
            height to display the image by default

        img: Py5Image
            the image to display

        u1: int
            x-coordinate of the upper left corner of image subset

        u2: int
            x-coordinate of the lower right corner of image subset

        v1: int
            y-coordinate of the upper left corner of image subset

        v2: int
            y-coordinate of the lower right corner of image subset

        Notes
        -----

        The `image()` function draws an image to the display window. Images must be in
        the Sketch's "data" directory to load correctly. Py5 currently works with GIF,
        JPEG, and PNG images.

        The `img` parameter specifies the image to display and by default the `a` and
        `b` parameters define the location of its upper-left corner. The image is
        displayed at its original size unless the `c` and `d` parameters specify a
        different size. The `image_mode()` function can be used to change the way these
        parameters draw the image.

        Use the `u1`, `u2`, `v1`, and `v2` parameters to use only a subset of the image.
        These values are always specified in image space location, regardless of the
        current `texture_mode()` setting.

        The color of an image may be modified with the `tint()` function. This function
        will maintain transparency for GIF and PNG images.
        """
        pass

    @_auto_convert_to_py5image(0)
    def image(self, *args):
        """The `image()` function draws an image to the display window.

        Underlying Processing method: PApplet.image

        Methods
        -------

        You can use any of the following signatures:

         * image(img: Py5Image, a: float, b: float, /) -> None
         * image(img: Py5Image, a: float, b: float, c: float, d: float, /) -> None
         * image(img: Py5Image, a: float, b: float, c: float, d: float, u1: int, v1: int, u2: int, v2: int, /) -> None

        Parameters
        ----------

        a: float
            x-coordinate of the image by default

        b: float
            y-coordinate of the image by default

        c: float
            width to display the image by default

        d: float
            height to display the image by default

        img: Py5Image
            the image to display

        u1: int
            x-coordinate of the upper left corner of image subset

        u2: int
            x-coordinate of the lower right corner of image subset

        v1: int
            y-coordinate of the upper left corner of image subset

        v2: int
            y-coordinate of the lower right corner of image subset

        Notes
        -----

        The `image()` function draws an image to the display window. Images must be in
        the Sketch's "data" directory to load correctly. Py5 currently works with GIF,
        JPEG, and PNG images.

        The `img` parameter specifies the image to display and by default the `a` and
        `b` parameters define the location of its upper-left corner. The image is
        displayed at its original size unless the `c` and `d` parameters specify a
        different size. The `image_mode()` function can be used to change the way these
        parameters draw the image.

        Use the `u1`, `u2`, `v1`, and `v2` parameters to use only a subset of the image.
        These values are always specified in image space location, regardless of the
        current `texture_mode()` setting.

        The color of an image may be modified with the `tint()` function. This function
        will maintain transparency for GIF and PNG images.
        """
        return self._instance.image(*args)

    def image_mode(self, mode: int, /) -> None:
        """Modifies the location from which images are drawn by changing the way in which
        parameters given to `image()` are intepreted.

        Underlying Processing method: PApplet.imageMode

        Parameters
        ----------

        mode: int
            either CORNER, CORNERS, or CENTER

        Notes
        -----

        Modifies the location from which images are drawn by changing the way in which
        parameters given to `image()` are intepreted.

        The default mode is `image_mode(CORNER)`, which interprets the second and third
        parameters of `image()` as the upper-left corner of the image. If two additional
        parameters are specified, they are used to set the image's width and height.

        `image_mode(CORNERS)` interprets the second and third parameters of `image()` as
        the location of one corner, and the fourth and fifth parameters as the opposite
        corner.

        `image_mode(CENTER)` interprets the second and third parameters of `image()` as
        the image's center point. If two additional parameters are specified, they are
        used to set the image's width and height.

        The parameter must be written in ALL CAPS because Python is a case-sensitive
        language.
        """
        return self._instance.imageMode(mode)

    def intercept_escape(self) -> None:
        """Prevent the Escape key from causing the Sketch to exit.

        Notes
        -----

        Prevent the Escape key from causing the Sketch to exit. Normally hitting the
        Escape key (`ESC`) will cause the Sketch to exit. In Processing, one can write
        code to change the Escape key's behavior by changing the `key` value to
        something else, perhaps with code similar to `py5.key = 'x'`. That code won't
        work in py5 because py5 does not allow the user to alter the value of `key` like
        Processing does. The `intercept_escape()` method was created to allow users to
        achieve the same goal of preventing the Escape key from causing the Sketch to
        exit.

        The `intercept_escape()` method will only do something when `key` already equals
        `ESC`. This function should only be called from the user event functions
        `key_pressed()`, `key_typed()`, and `key_released()`.

        This method will not alter the value of `key`. This method cannot prevent a
        Sketch from exiting when the exit is triggered by any other means, such as a
        call to `exit_sketch()` or the user closes the window.
        """
        return self._instance.interceptEscape()

    @overload
    def lerp_color(self, c1: int, c2: int, amt: float, /) -> int:
        """Calculates a color between two colors at a specific increment.

        Underlying Processing method: PApplet.lerpColor

        Methods
        -------

        You can use any of the following signatures:

         * lerp_color(c1: int, c2: int, amt: float, /) -> int
         * lerp_color(c1: int, c2: int, amt: float, mode: int, /) -> int

        Parameters
        ----------

        amt: float
            between 0.0 and 1.0

        c1: int
            interpolate from this color

        c2: int
            interpolate to this color

        mode: int
            either RGB or HSB

        Notes
        -----

        Calculates a color between two colors at a specific increment. The `amt`
        parameter is the amount to interpolate between the two values where 0.0 is equal
        to the first point, 0.1 is very near the first point, 0.5 is halfway in between,
        etc.

        An amount below 0 will be treated as 0. Likewise, amounts above 1 will be capped
        at 1. This is different from the behavior of `lerp()`, but necessary because
        otherwise numbers outside the range will produce strange and unexpected colors.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def lerp_color(self, c1: int, c2: int, amt: float, mode: int, /) -> int:
        """Calculates a color between two colors at a specific increment.

        Underlying Processing method: PApplet.lerpColor

        Methods
        -------

        You can use any of the following signatures:

         * lerp_color(c1: int, c2: int, amt: float, /) -> int
         * lerp_color(c1: int, c2: int, amt: float, mode: int, /) -> int

        Parameters
        ----------

        amt: float
            between 0.0 and 1.0

        c1: int
            interpolate from this color

        c2: int
            interpolate to this color

        mode: int
            either RGB or HSB

        Notes
        -----

        Calculates a color between two colors at a specific increment. The `amt`
        parameter is the amount to interpolate between the two values where 0.0 is equal
        to the first point, 0.1 is very near the first point, 0.5 is halfway in between,
        etc.

        An amount below 0 will be treated as 0. Likewise, amounts above 1 will be capped
        at 1. This is different from the behavior of `lerp()`, but necessary because
        otherwise numbers outside the range will produce strange and unexpected colors.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @_return_color
    @_convert_hex_color(indices=[0, 1])
    def lerp_color(self, *args):
        """Calculates a color between two colors at a specific increment.

        Underlying Processing method: PApplet.lerpColor

        Methods
        -------

        You can use any of the following signatures:

         * lerp_color(c1: int, c2: int, amt: float, /) -> int
         * lerp_color(c1: int, c2: int, amt: float, mode: int, /) -> int

        Parameters
        ----------

        amt: float
            between 0.0 and 1.0

        c1: int
            interpolate from this color

        c2: int
            interpolate to this color

        mode: int
            either RGB or HSB

        Notes
        -----

        Calculates a color between two colors at a specific increment. The `amt`
        parameter is the amount to interpolate between the two values where 0.0 is equal
        to the first point, 0.1 is very near the first point, 0.5 is halfway in between,
        etc.

        An amount below 0 will be treated as 0. Likewise, amounts above 1 will be capped
        at 1. This is different from the behavior of `lerp()`, but necessary because
        otherwise numbers outside the range will produce strange and unexpected colors.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        return self._instance.lerpColor(*args)

    def light_falloff(
        self, constant: float, linear: float, quadratic: float, /
    ) -> None:
        """Sets the falloff rates for point lights, spot lights, and ambient lights.

        Underlying Processing method: PApplet.lightFalloff

        Parameters
        ----------

        constant: float
            constant value or determining falloff

        linear: float
            linear value for determining falloff

        quadratic: float
            quadratic value for determining falloff

        Notes
        -----

        Sets the falloff rates for point lights, spot lights, and ambient lights. Like
        `fill()`, it affects only the elements which are created after it in the code.
        The default value is `light_falloff(1.0, 0.0, 0.0)`, and the parameters are used
        to calculate the falloff with the equation `falloff = 1 / (CONSTANT + d *
        `LINEAR` + (d*d) * QUADRATIC)`, where `d` is the distance from light position to
        vertex position.

        Thinking about an ambient light with a falloff can be tricky. If you want a
        region of your scene to be lit ambiently with one color and another region to be
        lit ambiently with another color, you could use an ambient light with location
        and falloff. You can think of it as a point light that doesn't care which
        direction a surface is facing.
        """
        return self._instance.lightFalloff(constant, linear, quadratic)

    def light_specular(self, v1: float, v2: float, v3: float, /) -> None:
        """Sets the specular color for lights.

        Underlying Processing method: PApplet.lightSpecular

        Parameters
        ----------

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the specular color for lights. Like `fill()`, it affects only the elements
        which are created after it in the code. Specular refers to light which bounces
        off a surface in a preferred direction (rather than bouncing in all directions
        like a diffuse light) and is used for creating highlights. The specular quality
        of a light interacts with the specular material qualities set through the
        `specular()` and `shininess()` functions.
        """
        return self._instance.lightSpecular(v1, v2, v3)

    def lights(self) -> None:
        """Sets the default ambient light, directional light, falloff, and specular values.

        Underlying Processing method: PApplet.lights

        Notes
        -----

        Sets the default ambient light, directional light, falloff, and specular values.
        The defaults are `ambientLight(128, 128, 128)` and `directionalLight(128, 128,
        128, 0, 0, -1)`, `lightFalloff(1, 0, 0)`, and `lightSpecular(0, 0, 0)`. Lights
        need to be included in the `draw()` to remain persistent in a looping program.
        Placing them in the `setup()` of a looping program will cause them to only have
        an effect the first time through the loop.
        """
        return self._instance.lights()

    @overload
    def line(self, x1: float, y1: float, x2: float, y2: float, /) -> None:
        """Draws a line (a direct path between two points) to the screen.

        Underlying Processing method: PApplet.line

        Methods
        -------

        You can use any of the following signatures:

         * line(x1: float, y1: float, x2: float, y2: float, /) -> None
         * line(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float, /) -> None

        Parameters
        ----------

        x1: float
            x-coordinate of the first point

        x2: float
            x-coordinate of the second point

        y1: float
            y-coordinate of the first point

        y2: float
            y-coordinate of the second point

        z1: float
            z-coordinate of the first point

        z2: float
            z-coordinate of the second point

        Notes
        -----

        Draws a line (a direct path between two points) to the screen. The version of
        `line()` with four parameters draws the line in 2D.  To color a line, use the
        `stroke()` function. A line cannot be filled, therefore the `fill()` function
        will not affect the color of a line. 2D lines are drawn with a width of one
        pixel by default, but this can be changed with the `stroke_weight()` function.
        The version with six parameters allows the line to be placed anywhere within XYZ
        space. Drawing this shape in 3D with the `z` parameter requires the `P3D`
        parameter in combination with `size()` as shown in the third example.
        """
        pass

    @overload
    def line(
        self, x1: float, y1: float, z1: float, x2: float, y2: float, z2: float, /
    ) -> None:
        """Draws a line (a direct path between two points) to the screen.

        Underlying Processing method: PApplet.line

        Methods
        -------

        You can use any of the following signatures:

         * line(x1: float, y1: float, x2: float, y2: float, /) -> None
         * line(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float, /) -> None

        Parameters
        ----------

        x1: float
            x-coordinate of the first point

        x2: float
            x-coordinate of the second point

        y1: float
            y-coordinate of the first point

        y2: float
            y-coordinate of the second point

        z1: float
            z-coordinate of the first point

        z2: float
            z-coordinate of the second point

        Notes
        -----

        Draws a line (a direct path between two points) to the screen. The version of
        `line()` with four parameters draws the line in 2D.  To color a line, use the
        `stroke()` function. A line cannot be filled, therefore the `fill()` function
        will not affect the color of a line. 2D lines are drawn with a width of one
        pixel by default, but this can be changed with the `stroke_weight()` function.
        The version with six parameters allows the line to be placed anywhere within XYZ
        space. Drawing this shape in 3D with the `z` parameter requires the `P3D`
        parameter in combination with `size()` as shown in the third example.
        """
        pass

    def line(self, *args):
        """Draws a line (a direct path between two points) to the screen.

        Underlying Processing method: PApplet.line

        Methods
        -------

        You can use any of the following signatures:

         * line(x1: float, y1: float, x2: float, y2: float, /) -> None
         * line(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float, /) -> None

        Parameters
        ----------

        x1: float
            x-coordinate of the first point

        x2: float
            x-coordinate of the second point

        y1: float
            y-coordinate of the first point

        y2: float
            y-coordinate of the second point

        z1: float
            z-coordinate of the first point

        z2: float
            z-coordinate of the second point

        Notes
        -----

        Draws a line (a direct path between two points) to the screen. The version of
        `line()` with four parameters draws the line in 2D.  To color a line, use the
        `stroke()` function. A line cannot be filled, therefore the `fill()` function
        will not affect the color of a line. 2D lines are drawn with a width of one
        pixel by default, but this can be changed with the `stroke_weight()` function.
        The version with six parameters allows the line to be placed anywhere within XYZ
        space. Drawing this shape in 3D with the `z` parameter requires the `P3D`
        parameter in combination with `size()` as shown in the third example.
        """
        return self._instance.line(*args)

    @_generator_to_list
    def lines(self, coordinates: Sequence[Sequence[float]], /) -> None:
        """Draw a collection of lines to the screen.

        Parameters
        ----------

        coordinates: Sequence[Sequence[float]]
            2D array of line coordinates with 4 or 6 columns for 2D or 3D points, respectively

        Notes
        -----

        Draw a collection of lines to the screen. The purpose of this method is to
        provide an alternative to repeatedly calling `line()` in a loop. For a large
        number of lines, the performance of `lines()` will be much faster.

        The `coordinates` parameter should be a numpy array with one row for each line.
        The first few columns are for the first point of each line and the next few
        columns are for the second point of each line. There will be four or six columns
        for 2D or 3D points, respectively.
        """
        return self._instance.lines(coordinates)

    @_load_py5font
    def load_font(self, filename: str, /) -> Py5Font:
        """Loads a .vlw formatted font into a `Py5Font` object.

        Underlying Processing method: PApplet.loadFont

        Parameters
        ----------

        filename: str
            name of the font to load

        Notes
        -----

        Loads a .vlw formatted font into a `Py5Font` object. Create a .vlw font with the
        `create_font_file()` function. This tool creates a texture for each alphanumeric
        character and then adds them as a .vlw file to the current Sketch's data folder.
        Because the letters are defined as textures (and not vector data) the size at
        which the fonts are created must be considered in relation to the size at which
        they are drawn. For example, load a 32pt font if the Sketch displays the font at
        32 pixels or smaller. Conversely, if a 12pt font is loaded and displayed at
        48pts, the letters will be distorted because the program will be stretching a
        small graphic to a large size.

        Like `load_image()` and other functions that load data, the `load_font()`
        function should not be used inside `draw()`, because it will slow down the
        Sketch considerably, as the font will be re-loaded from the disk (or network) on
        each frame. It's recommended to load files inside `setup()`.

        To load correctly, fonts must be located in the "data" folder of the current
        Sketch. Alternatively, the file maybe be loaded from anywhere on the local
        computer using an absolute path (something that starts with / on Unix and Linux,
        or a drive letter on Windows), or the filename parameter can be a URL for a file
        found on a network.

        If the file is not available or an error occurs, `None` will be returned and an
        error message will be printed to the console. The error message does not halt
        the program, however the `None` value may cause an error if your code does not
        check whether the value returned is `None`.

        Use `create_font()` (instead of `load_font()`) to enable vector data to be used
        with the default renderer setting. This can be helpful when many font sizes are
        needed, or when using any renderer based on the default renderer, such as the
        `PDF` renderer.
        """
        return self._instance.loadFont(filename)

    def load_pixels(self) -> None:
        """Loads the pixel data of the current display window into the `pixels[]` array.

        Underlying Processing method: PApplet.loadPixels

        Notes
        -----

        Loads the pixel data of the current display window into the `pixels[]` array.
        This function must always be called before reading from or writing to
        `pixels[]`. Subsequent changes to the display window will not be reflected in
        `pixels[]` until `load_pixels()` is called again.
        """
        return self._instance.loadPixels()

    @overload
    def load_shader(self, frag_filename: str, /) -> Py5Shader:
        """Loads a shader into a `Py5Shader` object.

        Underlying Processing method: PApplet.loadShader

        Methods
        -------

        You can use any of the following signatures:

         * load_shader(frag_filename: str, /) -> Py5Shader
         * load_shader(frag_filename: str, vert_filename: str, /) -> Py5Shader

        Parameters
        ----------

        frag_filename: str
            name of fragment shader file

        vert_filename: str
            name of vertex shader file

        Notes
        -----

        Loads a shader into a `Py5Shader` object. The shader file must be located in the
        Sketch's "data" directory to load correctly. Shaders are compatible with the
        `P2D` and `P3D` renderers, but not with the default renderer.

        Alternatively, the file maybe be loaded from anywhere on the local computer
        using an absolute path (something that starts with / on Unix and Linux, or a
        drive letter on Windows), or the filename parameter can be a URL for a file
        found on a network.

        If the file is not available or an error occurs, `None` will be returned and an
        error message will be printed to the console. The error message does not halt
        the program, however the `None` value may cause an error if your code does not
        check whether the value returned is `None`.
        """
        pass

    @overload
    def load_shader(self, frag_filename: str, vert_filename: str, /) -> Py5Shader:
        """Loads a shader into a `Py5Shader` object.

        Underlying Processing method: PApplet.loadShader

        Methods
        -------

        You can use any of the following signatures:

         * load_shader(frag_filename: str, /) -> Py5Shader
         * load_shader(frag_filename: str, vert_filename: str, /) -> Py5Shader

        Parameters
        ----------

        frag_filename: str
            name of fragment shader file

        vert_filename: str
            name of vertex shader file

        Notes
        -----

        Loads a shader into a `Py5Shader` object. The shader file must be located in the
        Sketch's "data" directory to load correctly. Shaders are compatible with the
        `P2D` and `P3D` renderers, but not with the default renderer.

        Alternatively, the file maybe be loaded from anywhere on the local computer
        using an absolute path (something that starts with / on Unix and Linux, or a
        drive letter on Windows), or the filename parameter can be a URL for a file
        found on a network.

        If the file is not available or an error occurs, `None` will be returned and an
        error message will be printed to the console. The error message does not halt
        the program, however the `None` value may cause an error if your code does not
        check whether the value returned is `None`.
        """
        pass

    @_load_py5shader
    def load_shader(self, *args):
        """Loads a shader into a `Py5Shader` object.

        Underlying Processing method: PApplet.loadShader

        Methods
        -------

        You can use any of the following signatures:

         * load_shader(frag_filename: str, /) -> Py5Shader
         * load_shader(frag_filename: str, vert_filename: str, /) -> Py5Shader

        Parameters
        ----------

        frag_filename: str
            name of fragment shader file

        vert_filename: str
            name of vertex shader file

        Notes
        -----

        Loads a shader into a `Py5Shader` object. The shader file must be located in the
        Sketch's "data" directory to load correctly. Shaders are compatible with the
        `P2D` and `P3D` renderers, but not with the default renderer.

        Alternatively, the file maybe be loaded from anywhere on the local computer
        using an absolute path (something that starts with / on Unix and Linux, or a
        drive letter on Windows), or the filename parameter can be a URL for a file
        found on a network.

        If the file is not available or an error occurs, `None` will be returned and an
        error message will be printed to the console. The error message does not halt
        the program, however the `None` value may cause an error if your code does not
        check whether the value returned is `None`.
        """
        return self._instance.loadShader(*args)

    @overload
    def load_shape(self, filename: str, /) -> Py5Shape:
        """Loads geometry into a variable of type `Py5Shape`.

        Underlying Processing method: PApplet.loadShape

        Methods
        -------

        You can use any of the following signatures:

         * load_shape(filename: str, /) -> Py5Shape
         * load_shape(filename: str, options: str, /) -> Py5Shape

        Parameters
        ----------

        filename: str
            name of file to load, can be .svg or .obj

        options: str
            unused parameter

        Notes
        -----

        Loads geometry into a variable of type `Py5Shape`. SVG and OBJ files may be
        loaded. To load correctly, the file must be located in the data directory of the
        current Sketch. In most cases, `load_shape()` should be used inside `setup()`
        because loading shapes inside `draw()` will reduce the speed of a Sketch.

        Alternatively, the file maybe be loaded from anywhere on the local computer
        using an absolute path (something that starts with / on Unix and Linux, or a
        drive letter on Windows), or the filename parameter can be a URL for a file
        found on a network.

        If the shape file is not available or for whatever reason a shape cannot be
        created, an exception will be thrown.
        """
        pass

    @overload
    def load_shape(self, filename: str, options: str, /) -> Py5Shape:
        """Loads geometry into a variable of type `Py5Shape`.

        Underlying Processing method: PApplet.loadShape

        Methods
        -------

        You can use any of the following signatures:

         * load_shape(filename: str, /) -> Py5Shape
         * load_shape(filename: str, options: str, /) -> Py5Shape

        Parameters
        ----------

        filename: str
            name of file to load, can be .svg or .obj

        options: str
            unused parameter

        Notes
        -----

        Loads geometry into a variable of type `Py5Shape`. SVG and OBJ files may be
        loaded. To load correctly, the file must be located in the data directory of the
        current Sketch. In most cases, `load_shape()` should be used inside `setup()`
        because loading shapes inside `draw()` will reduce the speed of a Sketch.

        Alternatively, the file maybe be loaded from anywhere on the local computer
        using an absolute path (something that starts with / on Unix and Linux, or a
        drive letter on Windows), or the filename parameter can be a URL for a file
        found on a network.

        If the shape file is not available or for whatever reason a shape cannot be
        created, an exception will be thrown.
        """
        pass

    @_load_py5shape
    def load_shape(self, *args):
        """Loads geometry into a variable of type `Py5Shape`.

        Underlying Processing method: PApplet.loadShape

        Methods
        -------

        You can use any of the following signatures:

         * load_shape(filename: str, /) -> Py5Shape
         * load_shape(filename: str, options: str, /) -> Py5Shape

        Parameters
        ----------

        filename: str
            name of file to load, can be .svg or .obj

        options: str
            unused parameter

        Notes
        -----

        Loads geometry into a variable of type `Py5Shape`. SVG and OBJ files may be
        loaded. To load correctly, the file must be located in the data directory of the
        current Sketch. In most cases, `load_shape()` should be used inside `setup()`
        because loading shapes inside `draw()` will reduce the speed of a Sketch.

        Alternatively, the file maybe be loaded from anywhere on the local computer
        using an absolute path (something that starts with / on Unix and Linux, or a
        drive letter on Windows), or the filename parameter can be a URL for a file
        found on a network.

        If the shape file is not available or for whatever reason a shape cannot be
        created, an exception will be thrown.
        """
        return self._instance.loadShape(*args)

    def loop(self) -> None:
        """By default, py5 loops through `draw()` continuously, executing the code within
        it.

        Underlying Processing method: PApplet.loop

        Notes
        -----

        By default, py5 loops through `draw()` continuously, executing the code within
        it. However, the `draw()` loop may be stopped by calling `no_loop()`. In that
        case, the `draw()` loop can be resumed with `loop()`.
        """
        return self._instance.loop()

    def millis(self) -> int:
        """Returns the number of milliseconds (thousandths of a second) since starting the
        program.

        Underlying Processing method: PApplet.millis

        Notes
        -----

        Returns the number of milliseconds (thousandths of a second) since starting the
        program. This information is often used for timing events and animation
        sequences.
        """
        return self._instance.millis()

    @classmethod
    def minute(cls) -> int:
        """Py5 communicates with the clock on your computer.

        Underlying Processing method: PApplet.minute

        Notes
        -----

        Py5 communicates with the clock on your computer. The `minute()` function
        returns the current minute as a value from 0 - 59.
        """
        return cls._cls.minute()

    def model_x(self, x: float, y: float, z: float, /) -> float:
        """Returns the three-dimensional X, Y, Z position in model space.

        Underlying Processing method: PApplet.modelX

        Parameters
        ----------

        x: float
            3D x-coordinate to be mapped

        y: float
            3D y-coordinate to be mapped

        z: float
            3D z-coordinate to be mapped

        Notes
        -----

        Returns the three-dimensional X, Y, Z position in model space. This returns the
        X value for a given coordinate based on the current set of transformations
        (scale, rotate, translate, etc.) The X value can be used to place an object in
        space relative to the location of the original point once the transformations
        are no longer in use.

        In the example, the `model_x()`, `model_y()`, and `model_z()` functions record
        the location of a box in space after being placed using a series of translate
        and rotate commands. After `pop_matrix()` is called, those transformations no
        longer apply, but the (x, y, z) coordinate returned by the model functions is
        used to place another box in the same location.
        """
        return self._instance.modelX(x, y, z)

    def model_y(self, x: float, y: float, z: float, /) -> float:
        """Returns the three-dimensional X, Y, Z position in model space.

        Underlying Processing method: PApplet.modelY

        Parameters
        ----------

        x: float
            3D x-coordinate to be mapped

        y: float
            3D y-coordinate to be mapped

        z: float
            3D z-coordinate to be mapped

        Notes
        -----

        Returns the three-dimensional X, Y, Z position in model space. This returns the
        Y value for a given coordinate based on the current set of transformations
        (scale, rotate, translate, etc.) The Y value can be used to place an object in
        space relative to the location of the original point once the transformations
        are no longer in use.

        In the example, the `model_x()`, `model_y()`, and `model_z()` functions record
        the location of a box in space after being placed using a series of translate
        and rotate commands. After `pop_matrix()` is called, those transformations no
        longer apply, but the (x, y, z) coordinate returned by the model functions is
        used to place another box in the same location.
        """
        return self._instance.modelY(x, y, z)

    def model_z(self, x: float, y: float, z: float, /) -> float:
        """Returns the three-dimensional X, Y, Z position in model space.

        Underlying Processing method: PApplet.modelZ

        Parameters
        ----------

        x: float
            3D x-coordinate to be mapped

        y: float
            3D y-coordinate to be mapped

        z: float
            3D z-coordinate to be mapped

        Notes
        -----

        Returns the three-dimensional X, Y, Z position in model space. This returns the
        Z value for a given coordinate based on the current set of transformations
        (scale, rotate, translate, etc.) The Z value can be used to place an object in
        space relative to the location of the original point once the transformations
        are no longer in use.

        In the example, the `model_x()`, `model_y()`, and `model_z()` functions record
        the location of a box in space after being placed using a series of translate
        and rotate commands. After `pop_matrix()` is called, those transformations no
        longer apply, but the (x, y, z) coordinate returned by the model functions is
        used to place another box in the same location.
        """
        return self._instance.modelZ(x, y, z)

    @classmethod
    def month(cls) -> int:
        """Py5 communicates with the clock on your computer.

        Underlying Processing method: PApplet.month

        Notes
        -----

        Py5 communicates with the clock on your computer. The `month()` function returns
        the current month as a value from 1 - 12.
        """
        return cls._cls.month()

    def no_clip(self) -> None:
        """Disables the clipping previously started by the `clip()` function.

        Underlying Processing method: PApplet.noClip

        Notes
        -----

        Disables the clipping previously started by the `clip()` function.
        """
        return self._instance.noClip()

    def no_cursor(self) -> None:
        """Hides the cursor from view.

        Underlying Processing method: PApplet.noCursor

        Notes
        -----

        Hides the cursor from view. Will not work when running the program in full
        screen (Present) mode.
        """
        return self._instance.noCursor()

    def no_fill(self) -> None:
        """Disables filling geometry.

        Underlying Processing method: PApplet.noFill

        Notes
        -----

        Disables filling geometry. If both `no_stroke()` and `no_fill()` are called,
        nothing will be drawn to the screen.
        """
        return self._instance.noFill()

    def no_lights(self) -> None:
        """Disable all lighting.

        Underlying Processing method: PApplet.noLights

        Notes
        -----

        Disable all lighting. Lighting is turned off by default and enabled with the
        `lights()` function. This function can be used to disable lighting so that 2D
        geometry (which does not require lighting) can be drawn after a set of lighted
        3D geometry.
        """
        return self._instance.noLights()

    def no_loop(self) -> None:
        """Stops py5 from continuously executing the code within `draw()`.

        Underlying Processing method: PApplet.noLoop

        Notes
        -----

        Stops py5 from continuously executing the code within `draw()`. If `loop()` is
        called, the code in `draw()` begins to run continuously again. If using
        `no_loop()` in `setup()`, it should be the last line inside the block.

        When `no_loop()` is used, it's not possible to manipulate or access the screen
        inside event handling functions such as `mouse_pressed()` or `key_pressed()`.
        Instead, use those functions to call `redraw()` or `loop()`, which will run
        `draw()`, which can update the screen properly. This means that when `no_loop()`
        has been called, no drawing can happen, and functions like `save_frame()` or
        `load_pixels()` may not be used.

        Note that if the Sketch is resized, `redraw()` will be called to update the
        Sketch, even after `no_loop()` has been specified. Otherwise, the Sketch would
        enter an odd state until `loop()` was called.
        """
        return self._instance.noLoop()

    @_settings_only("no_smooth")
    def no_smooth(self) -> None:
        """Draws all geometry and fonts with jagged (aliased) edges and images with hard
        edges between the pixels when enlarged rather than interpolating pixels.

        Underlying Processing method: PApplet.noSmooth

        Notes
        -----

        Draws all geometry and fonts with jagged (aliased) edges and images with hard
        edges between the pixels when enlarged rather than interpolating pixels.  Note
        that `smooth()` is active by default, so it is necessary to call `no_smooth()`
        to disable smoothing of geometry, fonts, and images.

        The `no_smooth()` function can only be called once within a Sketch. It is
        intended to be called from the `settings()` function. The `smooth()` function
        follows the same rules.

        When programming in module mode and imported mode, py5 will allow calls to
        `no_smooth()` from the `setup()` function if it is called at the beginning of
        `setup()`. This allows the user to omit the `settings()` function, much like
        what can be done while programming in the Processing IDE. Py5 does this by
        inspecting the `setup()` function and attempting to split it into synthetic
        `settings()` and `setup()` functions if both were not created by the user and
        the real `setup()` function contains a call to `no_smooth()`, or calls to
        `size()`, `full_screen()`, `smooth()`, or `pixel_density()`. Calls to those
        functions must be at the very beginning of `setup()`, before any other Python
        code (but comments are ok). This feature is not available when programming in
        class mode.
        """
        return self._instance.noSmooth()

    def no_stroke(self) -> None:
        """Disables drawing the stroke (outline).

        Underlying Processing method: PApplet.noStroke

        Notes
        -----

        Disables drawing the stroke (outline). If both `no_stroke()` and `no_fill()` are
        called, nothing will be drawn to the screen.
        """
        return self._instance.noStroke()

    def no_tint(self) -> None:
        """Removes the current fill value for displaying images and reverts to displaying
        images with their original hues.

        Underlying Processing method: PApplet.noTint

        Notes
        -----

        Removes the current fill value for displaying images and reverts to displaying
        images with their original hues.
        """
        return self._instance.noTint()

    @overload
    def noise_detail(self, lod: int, /) -> None:
        """Adjusts the character and level of detail of Processing's noise algorithm,
        produced by the `noise()` function.

        Underlying Processing method: PApplet.noiseDetail

        Methods
        -------

        You can use any of the following signatures:

         * noise_detail(lod: int, /) -> None
         * noise_detail(lod: int, falloff: float, /) -> None

        Parameters
        ----------

        falloff: float
            falloff factor for each octave

        lod: int
            number of octaves to be used by the noise

        Notes
        -----

        Adjusts the character and level of detail of Processing's noise algorithm,
        produced by the `noise()` function. Similar to harmonics in physics, Processing
        noise is computed over several octaves. Lower octaves contribute more to the
        output signal and as such define the overall intensity of the noise, whereas
        higher octaves create finer-grained details in the noise sequence.

        By default, noise is computed over 4 octaves with each octave contributing
        exactly half than its predecessor, starting at 50% strength for the first
        octave. This falloff amount can be changed by adding an additional function
        parameter. For example, a `falloff` factor of 0.75 means each octave will now
        have 75% impact (25% less) of the previous lower octave. While any number
        between 0.0 and 1.0 is valid, note that values greater than 0.5 may result in
        noise() returning values greater than 1.0 or less than 0.0.

        By changing these parameters, the signal created by the `noise()` function can
        be adapted to fit very specific needs and characteristics.
        """
        pass

    @overload
    def noise_detail(self, lod: int, falloff: float, /) -> None:
        """Adjusts the character and level of detail of Processing's noise algorithm,
        produced by the `noise()` function.

        Underlying Processing method: PApplet.noiseDetail

        Methods
        -------

        You can use any of the following signatures:

         * noise_detail(lod: int, /) -> None
         * noise_detail(lod: int, falloff: float, /) -> None

        Parameters
        ----------

        falloff: float
            falloff factor for each octave

        lod: int
            number of octaves to be used by the noise

        Notes
        -----

        Adjusts the character and level of detail of Processing's noise algorithm,
        produced by the `noise()` function. Similar to harmonics in physics, Processing
        noise is computed over several octaves. Lower octaves contribute more to the
        output signal and as such define the overall intensity of the noise, whereas
        higher octaves create finer-grained details in the noise sequence.

        By default, noise is computed over 4 octaves with each octave contributing
        exactly half than its predecessor, starting at 50% strength for the first
        octave. This falloff amount can be changed by adding an additional function
        parameter. For example, a `falloff` factor of 0.75 means each octave will now
        have 75% impact (25% less) of the previous lower octave. While any number
        between 0.0 and 1.0 is valid, note that values greater than 0.5 may result in
        noise() returning values greater than 1.0 or less than 0.0.

        By changing these parameters, the signal created by the `noise()` function can
        be adapted to fit very specific needs and characteristics.
        """
        pass

    def noise_detail(self, *args):
        """Adjusts the character and level of detail of Processing's noise algorithm,
        produced by the `noise()` function.

        Underlying Processing method: PApplet.noiseDetail

        Methods
        -------

        You can use any of the following signatures:

         * noise_detail(lod: int, /) -> None
         * noise_detail(lod: int, falloff: float, /) -> None

        Parameters
        ----------

        falloff: float
            falloff factor for each octave

        lod: int
            number of octaves to be used by the noise

        Notes
        -----

        Adjusts the character and level of detail of Processing's noise algorithm,
        produced by the `noise()` function. Similar to harmonics in physics, Processing
        noise is computed over several octaves. Lower octaves contribute more to the
        output signal and as such define the overall intensity of the noise, whereas
        higher octaves create finer-grained details in the noise sequence.

        By default, noise is computed over 4 octaves with each octave contributing
        exactly half than its predecessor, starting at 50% strength for the first
        octave. This falloff amount can be changed by adding an additional function
        parameter. For example, a `falloff` factor of 0.75 means each octave will now
        have 75% impact (25% less) of the previous lower octave. While any number
        between 0.0 and 1.0 is valid, note that values greater than 0.5 may result in
        noise() returning values greater than 1.0 or less than 0.0.

        By changing these parameters, the signal created by the `noise()` function can
        be adapted to fit very specific needs and characteristics.
        """
        return self._instance.noiseDetail(*args)

    def noise_seed(self, seed: int, /) -> None:
        """Sets the seed value for `noise()`.

        Underlying Processing method: PApplet.noiseSeed

        Parameters
        ----------

        seed: int
            seed value

        Notes
        -----

        Sets the seed value for `noise()`. By default, `noise()` produces different
        results each time the program is run. Set the seed parameter to a constant to
        return the same pseudo-random numbers each time the Sketch is run.
        """
        return self._instance.noiseSeed(seed)

    def normal(self, nx: float, ny: float, nz: float, /) -> None:
        """Sets the current normal vector.

        Underlying Processing method: PApplet.normal

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

        Sets the current normal vector. Used for drawing three dimensional shapes and
        surfaces, `normal()` specifies a vector perpendicular to a shape's surface
        which, in turn, determines how lighting affects it. Py5 attempts to
        automatically assign normals to shapes, but since that's imperfect, this is a
        better option when you want more control. This function is identical to
        `gl_normal3f()` in OpenGL.
        """
        return self._instance.normal(nx, ny, nz)

    @overload
    def ortho(self) -> None:
        """Sets an orthographic projection and defines a parallel clipping volume.

        Underlying Processing method: PApplet.ortho

        Methods
        -------

        You can use any of the following signatures:

         * ortho() -> None
         * ortho(left: float, right: float, bottom: float, top: float, /) -> None
         * ortho(left: float, right: float, bottom: float, top: float, near: float, far: float, /) -> None

        Parameters
        ----------

        bottom: float
            bottom plane of the clipping volume

        far: float
            distance from the viewer to the farthest clipping plane

        left: float
            left plane of the clipping volume

        near: float
            distance from the viewer to the nearest clipping plane

        right: float
            right plane of the clipping volume

        top: float
            top plane of the clipping volume

        Notes
        -----

        Sets an orthographic projection and defines a parallel clipping volume. All
        objects with the same dimension appear the same size, regardless of whether they
        are near or far from the camera. The parameters to this function specify the
        clipping volume where left and right are the minimum and maximum x values, top
        and bottom are the minimum and maximum y values, and near and far are the
        minimum and maximum z values. If no parameters are given, the default is used:
        `ortho(-width/2, width/2, -height/2, height/2)`.
        """
        pass

    @overload
    def ortho(self, left: float, right: float, bottom: float, top: float, /) -> None:
        """Sets an orthographic projection and defines a parallel clipping volume.

        Underlying Processing method: PApplet.ortho

        Methods
        -------

        You can use any of the following signatures:

         * ortho() -> None
         * ortho(left: float, right: float, bottom: float, top: float, /) -> None
         * ortho(left: float, right: float, bottom: float, top: float, near: float, far: float, /) -> None

        Parameters
        ----------

        bottom: float
            bottom plane of the clipping volume

        far: float
            distance from the viewer to the farthest clipping plane

        left: float
            left plane of the clipping volume

        near: float
            distance from the viewer to the nearest clipping plane

        right: float
            right plane of the clipping volume

        top: float
            top plane of the clipping volume

        Notes
        -----

        Sets an orthographic projection and defines a parallel clipping volume. All
        objects with the same dimension appear the same size, regardless of whether they
        are near or far from the camera. The parameters to this function specify the
        clipping volume where left and right are the minimum and maximum x values, top
        and bottom are the minimum and maximum y values, and near and far are the
        minimum and maximum z values. If no parameters are given, the default is used:
        `ortho(-width/2, width/2, -height/2, height/2)`.
        """
        pass

    @overload
    def ortho(
        self,
        left: float,
        right: float,
        bottom: float,
        top: float,
        near: float,
        far: float,
        /,
    ) -> None:
        """Sets an orthographic projection and defines a parallel clipping volume.

        Underlying Processing method: PApplet.ortho

        Methods
        -------

        You can use any of the following signatures:

         * ortho() -> None
         * ortho(left: float, right: float, bottom: float, top: float, /) -> None
         * ortho(left: float, right: float, bottom: float, top: float, near: float, far: float, /) -> None

        Parameters
        ----------

        bottom: float
            bottom plane of the clipping volume

        far: float
            distance from the viewer to the farthest clipping plane

        left: float
            left plane of the clipping volume

        near: float
            distance from the viewer to the nearest clipping plane

        right: float
            right plane of the clipping volume

        top: float
            top plane of the clipping volume

        Notes
        -----

        Sets an orthographic projection and defines a parallel clipping volume. All
        objects with the same dimension appear the same size, regardless of whether they
        are near or far from the camera. The parameters to this function specify the
        clipping volume where left and right are the minimum and maximum x values, top
        and bottom are the minimum and maximum y values, and near and far are the
        minimum and maximum z values. If no parameters are given, the default is used:
        `ortho(-width/2, width/2, -height/2, height/2)`.
        """
        pass

    def ortho(self, *args):
        """Sets an orthographic projection and defines a parallel clipping volume.

        Underlying Processing method: PApplet.ortho

        Methods
        -------

        You can use any of the following signatures:

         * ortho() -> None
         * ortho(left: float, right: float, bottom: float, top: float, /) -> None
         * ortho(left: float, right: float, bottom: float, top: float, near: float, far: float, /) -> None

        Parameters
        ----------

        bottom: float
            bottom plane of the clipping volume

        far: float
            distance from the viewer to the farthest clipping plane

        left: float
            left plane of the clipping volume

        near: float
            distance from the viewer to the nearest clipping plane

        right: float
            right plane of the clipping volume

        top: float
            top plane of the clipping volume

        Notes
        -----

        Sets an orthographic projection and defines a parallel clipping volume. All
        objects with the same dimension appear the same size, regardless of whether they
        are near or far from the camera. The parameters to this function specify the
        clipping volume where left and right are the minimum and maximum x values, top
        and bottom are the minimum and maximum y values, and near and far are the
        minimum and maximum z values. If no parameters are given, the default is used:
        `ortho(-width/2, width/2, -height/2, height/2)`.
        """
        return self._instance.ortho(*args)

    def os_noise_seed(self, seed: int, /) -> None:
        """Sets the seed value for `os_noise()`.

        Parameters
        ----------

        seed: int
            seed value

        Notes
        -----

        Sets the seed value for `os_noise()`. By default, `os_noise()` produces
        different results each time the program is run. Set the seed parameter to a
        constant to return the same pseudo-random numbers each time the Sketch is run.
        """
        return self._instance.osNoiseSeed(seed)

    @overload
    def perspective(self) -> None:
        """Sets a perspective projection applying foreshortening, making distant objects
        appear smaller than closer ones.

        Underlying Processing method: PApplet.perspective

        Methods
        -------

        You can use any of the following signatures:

         * perspective() -> None
         * perspective(fovy: float, aspect: float, z_near: float, z_far: float, /) -> None

        Parameters
        ----------

        aspect: float
            ratio of width to height

        fovy: float
            field-of-view angle (in radians) for vertical direction

        z_far: float
            z-position of farthest clipping plane

        z_near: float
            z-position of nearest clipping plane

        Notes
        -----

        Sets a perspective projection applying foreshortening, making distant objects
        appear smaller than closer ones. The parameters define a viewing volume with the
        shape of truncated pyramid. Objects near to the front of the volume appear their
        actual size, while farther objects appear smaller. This projection simulates the
        perspective of the world more accurately than orthographic projection. The
        version of perspective without parameters sets the default perspective and the
        version with four parameters allows the programmer to set the area precisely.
        The default values are: `perspective(PI/3.0, width/height, cameraZ/10.0,
        cameraZ*10.0)` where cameraZ is `((height/2.0) / tan(PI*60.0/360.0))`.
        """
        pass

    @overload
    def perspective(
        self, fovy: float, aspect: float, z_near: float, z_far: float, /
    ) -> None:
        """Sets a perspective projection applying foreshortening, making distant objects
        appear smaller than closer ones.

        Underlying Processing method: PApplet.perspective

        Methods
        -------

        You can use any of the following signatures:

         * perspective() -> None
         * perspective(fovy: float, aspect: float, z_near: float, z_far: float, /) -> None

        Parameters
        ----------

        aspect: float
            ratio of width to height

        fovy: float
            field-of-view angle (in radians) for vertical direction

        z_far: float
            z-position of farthest clipping plane

        z_near: float
            z-position of nearest clipping plane

        Notes
        -----

        Sets a perspective projection applying foreshortening, making distant objects
        appear smaller than closer ones. The parameters define a viewing volume with the
        shape of truncated pyramid. Objects near to the front of the volume appear their
        actual size, while farther objects appear smaller. This projection simulates the
        perspective of the world more accurately than orthographic projection. The
        version of perspective without parameters sets the default perspective and the
        version with four parameters allows the programmer to set the area precisely.
        The default values are: `perspective(PI/3.0, width/height, cameraZ/10.0,
        cameraZ*10.0)` where cameraZ is `((height/2.0) / tan(PI*60.0/360.0))`.
        """
        pass

    def perspective(self, *args):
        """Sets a perspective projection applying foreshortening, making distant objects
        appear smaller than closer ones.

        Underlying Processing method: PApplet.perspective

        Methods
        -------

        You can use any of the following signatures:

         * perspective() -> None
         * perspective(fovy: float, aspect: float, z_near: float, z_far: float, /) -> None

        Parameters
        ----------

        aspect: float
            ratio of width to height

        fovy: float
            field-of-view angle (in radians) for vertical direction

        z_far: float
            z-position of farthest clipping plane

        z_near: float
            z-position of nearest clipping plane

        Notes
        -----

        Sets a perspective projection applying foreshortening, making distant objects
        appear smaller than closer ones. The parameters define a viewing volume with the
        shape of truncated pyramid. Objects near to the front of the volume appear their
        actual size, while farther objects appear smaller. This projection simulates the
        perspective of the world more accurately than orthographic projection. The
        version of perspective without parameters sets the default perspective and the
        version with four parameters allows the programmer to set the area precisely.
        The default values are: `perspective(PI/3.0, width/height, cameraZ/10.0,
        cameraZ*10.0)` where cameraZ is `((height/2.0) / tan(PI*60.0/360.0))`.
        """
        return self._instance.perspective(*args)

    @_settings_only("pixel_density")
    def pixel_density(self, density: int, /) -> None:
        """This function makes it possible for py5 to render using all of the pixels on
        high resolutions screens like Apple Retina displays and Windows High-DPI
        displays.

        Underlying Processing method: PApplet.pixelDensity

        Parameters
        ----------

        density: int
            1 or 2

        Notes
        -----

        This function makes it possible for py5 to render using all of the pixels on
        high resolutions screens like Apple Retina displays and Windows High-DPI
        displays. This function can only be run once within a program. It is intended to
        be called from the `settings()` function.

        When programming in module mode and imported mode, py5 will allow calls to
        `pixel_density()` from the `setup()` function if it is called at the beginning
        of `setup()`. This allows the user to omit the `settings()` function, much like
        what can be done while programming in the Processing IDE. Py5 does this by
        inspecting the `setup()` function and attempting to split it into synthetic
        `settings()` and `setup()` functions if both were not created by the user and
        the real `setup()` function contains a call to `pixel_density()`, or calls to
        `size()`, `full_screen()`, `smooth()`, or `no_smooth()`. Calls to those
        functions must be at the very beginning of `setup()`, before any other Python
        code (but comments are ok). This feature is not available when programming in
        class mode.

        The `pixel_density()` should only be used with hardcoded numbers (in almost all
        cases this number will be 2) or in combination with `display_density()` as in
        the second example.

        When the pixel density is set to more than 1, it changes all of the pixel
        operations including the way `get_pixels()`, `set_pixels()`, `blend()`,
        `copy()`, `update_pixels()`, and `update_np_pixels()` all work. See the
        reference for `pixel_width` and `pixel_height` for more information.
        """
        return self._instance.pixelDensity(density)

    @overload
    def point(self, x: float, y: float, /) -> None:
        """Draws a point, a coordinate in space at the dimension of one pixel.

        Underlying Processing method: PApplet.point

        Methods
        -------

        You can use any of the following signatures:

         * point(x: float, y: float, /) -> None
         * point(x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        x: float
            x-coordinate of the point

        y: float
            y-coordinate of the point

        z: float
            z-coordinate of the point

        Notes
        -----

        Draws a point, a coordinate in space at the dimension of one pixel. The first
        parameter is the horizontal value for the point, the second value is the
        vertical value for the point, and the optional third value is the depth value.
        Drawing this shape in 3D with the `z` parameter requires the `P3D` parameter in
        combination with `size()` as shown in the second example.

        Use `stroke()` to set the color of a `point()`.

        Point appears round with the default `stroke_cap(ROUND)` and square with
        `stroke_cap(PROJECT)`. Points are invisible with `stroke_cap(SQUARE)` (no cap).

        Using `point()` with `strokeWeight(1)` or smaller may draw nothing to the
        screen, depending on the graphics settings of the computer. Workarounds include
        setting the pixel using the `pixels[]` or `np_pixels[]` arrays or drawing the
        point using either `circle()` or `square()`.
        """
        pass

    @overload
    def point(self, x: float, y: float, z: float, /) -> None:
        """Draws a point, a coordinate in space at the dimension of one pixel.

        Underlying Processing method: PApplet.point

        Methods
        -------

        You can use any of the following signatures:

         * point(x: float, y: float, /) -> None
         * point(x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        x: float
            x-coordinate of the point

        y: float
            y-coordinate of the point

        z: float
            z-coordinate of the point

        Notes
        -----

        Draws a point, a coordinate in space at the dimension of one pixel. The first
        parameter is the horizontal value for the point, the second value is the
        vertical value for the point, and the optional third value is the depth value.
        Drawing this shape in 3D with the `z` parameter requires the `P3D` parameter in
        combination with `size()` as shown in the second example.

        Use `stroke()` to set the color of a `point()`.

        Point appears round with the default `stroke_cap(ROUND)` and square with
        `stroke_cap(PROJECT)`. Points are invisible with `stroke_cap(SQUARE)` (no cap).

        Using `point()` with `strokeWeight(1)` or smaller may draw nothing to the
        screen, depending on the graphics settings of the computer. Workarounds include
        setting the pixel using the `pixels[]` or `np_pixels[]` arrays or drawing the
        point using either `circle()` or `square()`.
        """
        pass

    def point(self, *args):
        """Draws a point, a coordinate in space at the dimension of one pixel.

        Underlying Processing method: PApplet.point

        Methods
        -------

        You can use any of the following signatures:

         * point(x: float, y: float, /) -> None
         * point(x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        x: float
            x-coordinate of the point

        y: float
            y-coordinate of the point

        z: float
            z-coordinate of the point

        Notes
        -----

        Draws a point, a coordinate in space at the dimension of one pixel. The first
        parameter is the horizontal value for the point, the second value is the
        vertical value for the point, and the optional third value is the depth value.
        Drawing this shape in 3D with the `z` parameter requires the `P3D` parameter in
        combination with `size()` as shown in the second example.

        Use `stroke()` to set the color of a `point()`.

        Point appears round with the default `stroke_cap(ROUND)` and square with
        `stroke_cap(PROJECT)`. Points are invisible with `stroke_cap(SQUARE)` (no cap).

        Using `point()` with `strokeWeight(1)` or smaller may draw nothing to the
        screen, depending on the graphics settings of the computer. Workarounds include
        setting the pixel using the `pixels[]` or `np_pixels[]` arrays or drawing the
        point using either `circle()` or `square()`.
        """
        return self._instance.point(*args)

    def point_light(
        self, v1: float, v2: float, v3: float, x: float, y: float, z: float, /
    ) -> None:
        """Adds a point light.

        Underlying Processing method: PApplet.pointLight

        Parameters
        ----------

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        x: float
            x-coordinate of the light

        y: float
            y-coordinate of the light

        z: float
            z-coordinate of the light

        Notes
        -----

        Adds a point light. Lights need to be included in the `draw()` to remain
        persistent in a looping program. Placing them in the `setup()` of a looping
        program will cause them to only have an effect the first time through the loop.
        The `v1`, `v2`, and `v3` parameters are interpreted as either RGB or HSB values,
        depending on the current color mode. The `x`, `y`, and `z` parameters set the
        position of the light.
        """
        return self._instance.pointLight(v1, v2, v3, x, y, z)

    @_generator_to_list
    def points(self, coordinates: Sequence[Sequence[float]], /) -> None:
        """Draw a collection of points, each a coordinate in space at the dimension of one
        pixel.

        Parameters
        ----------

        coordinates: Sequence[Sequence[float]]
            2D array of point coordinates with 2 or 3 columns for 2D or 3D points, respectively

        Notes
        -----

        Draw a collection of points, each a coordinate in space at the dimension of one
        pixel. The purpose of this method is to provide an alternative to repeatedly
        calling `point()` in a loop. For a large number of points, the performance of
        `points()` will be much faster.

        The `coordinates` parameter should be a numpy array with one row for each point.
        There should be two or three columns for 2D or 3D points, respectively.
        """
        return self._instance.points(coordinates)

    def pop(self) -> None:
        """The `pop()` function restores the previous drawing style settings and
        transformations after `push()` has changed them.

        Underlying Processing method: PApplet.pop

        Notes
        -----

        The `pop()` function restores the previous drawing style settings and
        transformations after `push()` has changed them. Note that these functions are
        always used together. They allow you to change the style and transformation
        settings and later return to what you had. When a new state is started with
        `push()`, it builds on the current style and transform information.

        `push()` stores information related to the current transformation state and
        style settings controlled by the following functions: `rotate()`, `translate()`,
        `scale()`, `fill()`, `stroke()`, `tint()`, `stroke_weight()`, `stroke_cap()`,
        `stroke_join()`, `image_mode()`, `rect_mode()`, `ellipse_mode()`,
        `color_mode()`, `text_align()`, `text_font()`, `text_mode()`, `text_size()`, and
        `text_leading()`.

        The `push()` and `pop()` functions can be used in place of `push_matrix()`,
        `pop_matrix()`, `push_style()`, and `pop_style()`. The difference is that
        `push()` and `pop()` control both the transformations (rotate, scale, translate)
        and the drawing styles at the same time.
        """
        return self._instance.pop()

    def pop_matrix(self) -> None:
        """Pops the current transformation matrix off the matrix stack.

        Underlying Processing method: PApplet.popMatrix

        Notes
        -----

        Pops the current transformation matrix off the matrix stack. Understanding
        pushing and popping requires understanding the concept of a matrix stack. The
        `push_matrix()` function saves the current coordinate system to the stack and
        `pop_matrix()` restores the prior coordinate system. `push_matrix()` and
        `pop_matrix()` are used in conjuction with the other transformation functions
        and may be embedded to control the scope of the transformations.
        """
        return self._instance.popMatrix()

    def pop_style(self) -> None:
        """The `push_style()` function saves the current style settings and `pop_style()`
        restores the prior settings; these functions are always used together.

        Underlying Processing method: PApplet.popStyle

        Notes
        -----

        The `push_style()` function saves the current style settings and `pop_style()`
        restores the prior settings; these functions are always used together. They
        allow you to change the style settings and later return to what you had. When a
        new style is started with `push_style()`, it builds on the current style
        information. The `push_style()` and `pop_style()` method pairs can be nested to
        provide more control (see the second example for a demonstration.)
        """
        return self._instance.popStyle()

    def print_camera(self) -> None:
        """Prints the current camera matrix to standard output.

        Underlying Processing method: PApplet.printCamera

        Notes
        -----

        Prints the current camera matrix to standard output.
        """
        return self._instance.printCamera()

    def print_matrix(self) -> None:
        """Prints the current matrix to standard output.

        Underlying Processing method: PApplet.printMatrix

        Notes
        -----

        Prints the current matrix to standard output.
        """
        return self._instance.printMatrix()

    def print_projection(self) -> None:
        """Prints the current projection matrix to standard output.

        Underlying Processing method: PApplet.printProjection

        Notes
        -----

        Prints the current projection matrix to standard output.
        """
        return self._instance.printProjection()

    @_context_wrapper("pop")
    def push(self) -> None:
        """The `push()` function saves the current drawing style settings and
        transformations, while `pop()` restores these settings.

        Underlying Processing method: PApplet.push

        Notes
        -----

        The `push()` function saves the current drawing style settings and
        transformations, while `pop()` restores these settings. Note that these
        functions are always used together. They allow you to change the style and
        transformation settings and later return to what you had. When a new state is
        started with `push()`, it builds on the current style and transform information.

        `push()` stores information related to the current transformation state and
        style settings controlled by the following functions: `rotate()`, `translate()`,
        `scale()`, `fill()`, `stroke()`, `tint()`, `stroke_weight()`, `stroke_cap()`,
        `stroke_join()`, `image_mode()`, `rect_mode()`, `ellipse_mode()`,
        `color_mode()`, `text_align()`, `text_font()`, `text_mode()`, `text_size()`, and
        `text_leading()`.

        The `push()` and `pop()` functions can be used in place of `push_matrix()`,
        `pop_matrix()`, `push_style()`, and `pop_style()`. The difference is that
        `push()` and `pop()` control both the transformations (rotate, scale, translate)
        and the drawing styles at the same time.

        This method can be used as a context manager to ensure that `pop()` always gets
        called, as shown in the last example.
        """
        return self._instance.push()

    @_context_wrapper("pop_matrix")
    def push_matrix(self) -> None:
        """Pushes the current transformation matrix onto the matrix stack.

        Underlying Processing method: PApplet.pushMatrix

        Notes
        -----

        Pushes the current transformation matrix onto the matrix stack. Understanding
        `push_matrix()` and `pop_matrix()` requires understanding the concept of a
        matrix stack. The `push_matrix()` function saves the current coordinate system
        to the stack and `pop_matrix()` restores the prior coordinate system.
        `push_matrix()` and `pop_matrix()` are used in conjuction with the other
        transformation functions and may be embedded to control the scope of the
        transformations.

        This method can be used as a context manager to ensure that `pop_matrix()`
        always gets called, as shown in the last example.
        """
        return self._instance.pushMatrix()

    @_context_wrapper("pop_style")
    def push_style(self) -> None:
        """The `push_style()` function saves the current style settings and `pop_style()`
        restores the prior settings.

        Underlying Processing method: PApplet.pushStyle

        Notes
        -----

        The `push_style()` function saves the current style settings and `pop_style()`
        restores the prior settings. Note that these functions are always used together.
        They allow you to change the style settings and later return to what you had.
        When a new style is started with `push_style()`, it builds on the current style
        information. The `push_style()` and `pop_style()` method pairs can be nested to
        provide more control. (See the second example for a demonstration.)

        The style information controlled by the following functions are included in the
        style: `fill()`, `stroke()`, `tint()`, `stroke_weight()`, `stroke_cap()`,
        `stroke_join()`, `image_mode()`, `rect_mode()`, `ellipse_mode()`,
        `shape_mode()`, `color_mode()`, `text_align()`, `text_font()`, `text_mode()`,
        `text_size()`, `text_leading()`, `emissive()`, `specular()`, `shininess()`, and
        `ambient()`.

        This method can be used as a context manager to ensure that `pop_style()` always
        gets called, as shown in the last example.
        """
        return self._instance.pushStyle()

    def quad(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        x3: float,
        y3: float,
        x4: float,
        y4: float,
        /,
    ) -> None:
        """A quad is a quadrilateral, a four sided polygon.

        Underlying Processing method: PApplet.quad

        Parameters
        ----------

        x1: float
            x-coordinate of the first corner

        x2: float
            x-coordinate of the second corner

        x3: float
            x-coordinate of the third corner

        x4: float
            x-coordinate of the fourth corner

        y1: float
            y-coordinate of the first corner

        y2: float
            y-coordinate of the second corner

        y3: float
            y-coordinate of the third corner

        y4: float
            y-coordinate of the fourth corner

        Notes
        -----

        A quad is a quadrilateral, a four sided polygon. It is similar to a rectangle,
        but the angles between its edges are not constrained to ninety degrees. The
        first pair of parameters (x1,y1) sets the first vertex and the subsequent pairs
        should proceed clockwise or counter-clockwise around the defined shape.
        """
        return self._instance.quad(x1, y1, x2, y2, x3, y3, x4, y4)

    @overload
    def quadratic_vertex(self, cx: float, cy: float, x3: float, y3: float, /) -> None:
        """Specifies vertex coordinates for quadratic Bezier curves.

        Underlying Processing method: PApplet.quadraticVertex

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

        Specifies vertex coordinates for quadratic Bezier curves. Each call to
        `quadratic_vertex()` defines the position of one control point and one anchor
        point of a Bezier curve, adding a new segment to a line or shape. The first time
        `quadratic_vertex()` is used within a `begin_shape()` call, it must be prefaced
        with a call to `vertex()` to set the first anchor point. This method must be
        used between `begin_shape()` and `end_shape()` and only when there is no `MODE`
        parameter specified to `begin_shape()`. Using the 3D version requires rendering
        with `P3D`.
        """
        pass

    @overload
    def quadratic_vertex(
        self, cx: float, cy: float, cz: float, x3: float, y3: float, z3: float, /
    ) -> None:
        """Specifies vertex coordinates for quadratic Bezier curves.

        Underlying Processing method: PApplet.quadraticVertex

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

        Specifies vertex coordinates for quadratic Bezier curves. Each call to
        `quadratic_vertex()` defines the position of one control point and one anchor
        point of a Bezier curve, adding a new segment to a line or shape. The first time
        `quadratic_vertex()` is used within a `begin_shape()` call, it must be prefaced
        with a call to `vertex()` to set the first anchor point. This method must be
        used between `begin_shape()` and `end_shape()` and only when there is no `MODE`
        parameter specified to `begin_shape()`. Using the 3D version requires rendering
        with `P3D`.
        """
        pass

    def quadratic_vertex(self, *args):
        """Specifies vertex coordinates for quadratic Bezier curves.

        Underlying Processing method: PApplet.quadraticVertex

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

        Specifies vertex coordinates for quadratic Bezier curves. Each call to
        `quadratic_vertex()` defines the position of one control point and one anchor
        point of a Bezier curve, adding a new segment to a line or shape. The first time
        `quadratic_vertex()` is used within a `begin_shape()` call, it must be prefaced
        with a call to `vertex()` to set the first anchor point. This method must be
        used between `begin_shape()` and `end_shape()` and only when there is no `MODE`
        parameter specified to `begin_shape()`. Using the 3D version requires rendering
        with `P3D`.
        """
        return self._instance.quadraticVertex(*args)

    @_generator_to_list
    def quadratic_vertices(self, coordinates: Sequence[Sequence[float]], /) -> None:
        """Create a collection of quadratic vertices.

        Parameters
        ----------

        coordinates: Sequence[Sequence[float]]
            2D array of quadratic vertex coordinates with 4 or 6 columns for 2D or 3D points, respectively

        Notes
        -----

        Create a collection of quadratic vertices. The purpose of this method is to
        provide an alternative to repeatedly calling `quadratic_vertex()` in a loop. For
        a large number of quadratic vertices, the performance of `quadratic_vertices()`
        will be much faster.

        The `coordinates` parameter should be a numpy array with one row for each
        quadratic vertex. The first few columns are for the control point and the next
        few columns are for the anchor point. There should be four or six columns for 2D
        or 3D points, respectively.
        """
        return self._instance.quadraticVertices(coordinates)

    @overload
    def rect(self, a: float, b: float, c: float, d: float, /) -> None:
        """Draws a rectangle to the screen.

        Underlying Processing method: PApplet.rect

        Methods
        -------

        You can use any of the following signatures:

         * rect(a: float, b: float, c: float, d: float, /) -> None
         * rect(a: float, b: float, c: float, d: float, r: float, /) -> None
         * rect(a: float, b: float, c: float, d: float, tl: float, tr: float, br: float, bl: float, /) -> None

        Parameters
        ----------

        a: float
            x-coordinate of the rectangle by default

        b: float
            y-coordinate of the rectangle by default

        bl: float
            radius for bottom-left corner

        br: float
            radius for bottom-right corner

        c: float
            width of the rectangle by default

        d: float
            height of the rectangle by default

        r: float
            radii for all four corners

        tl: float
            radius for top-left corner

        tr: float
            radius for top-right corner

        Notes
        -----

        Draws a rectangle to the screen. A rectangle is a four-sided shape with every
        angle at ninety degrees. By default, the first two parameters set the location
        of the upper-left corner, the third sets the width, and the fourth sets the
        height. The way these parameters are interpreted, however, may be changed with
        the `rect_mode()` function.

        To draw a rounded rectangle, add a fifth parameter, which is used as the radius
        value for all four corners.

        To use a different radius value for each corner, include eight parameters. When
        using eight parameters, the latter four set the radius of the arc at each corner
        separately, starting with the top-left corner and moving clockwise around the
        rectangle.
        """
        pass

    @overload
    def rect(self, a: float, b: float, c: float, d: float, r: float, /) -> None:
        """Draws a rectangle to the screen.

        Underlying Processing method: PApplet.rect

        Methods
        -------

        You can use any of the following signatures:

         * rect(a: float, b: float, c: float, d: float, /) -> None
         * rect(a: float, b: float, c: float, d: float, r: float, /) -> None
         * rect(a: float, b: float, c: float, d: float, tl: float, tr: float, br: float, bl: float, /) -> None

        Parameters
        ----------

        a: float
            x-coordinate of the rectangle by default

        b: float
            y-coordinate of the rectangle by default

        bl: float
            radius for bottom-left corner

        br: float
            radius for bottom-right corner

        c: float
            width of the rectangle by default

        d: float
            height of the rectangle by default

        r: float
            radii for all four corners

        tl: float
            radius for top-left corner

        tr: float
            radius for top-right corner

        Notes
        -----

        Draws a rectangle to the screen. A rectangle is a four-sided shape with every
        angle at ninety degrees. By default, the first two parameters set the location
        of the upper-left corner, the third sets the width, and the fourth sets the
        height. The way these parameters are interpreted, however, may be changed with
        the `rect_mode()` function.

        To draw a rounded rectangle, add a fifth parameter, which is used as the radius
        value for all four corners.

        To use a different radius value for each corner, include eight parameters. When
        using eight parameters, the latter four set the radius of the arc at each corner
        separately, starting with the top-left corner and moving clockwise around the
        rectangle.
        """
        pass

    @overload
    def rect(
        self,
        a: float,
        b: float,
        c: float,
        d: float,
        tl: float,
        tr: float,
        br: float,
        bl: float,
        /,
    ) -> None:
        """Draws a rectangle to the screen.

        Underlying Processing method: PApplet.rect

        Methods
        -------

        You can use any of the following signatures:

         * rect(a: float, b: float, c: float, d: float, /) -> None
         * rect(a: float, b: float, c: float, d: float, r: float, /) -> None
         * rect(a: float, b: float, c: float, d: float, tl: float, tr: float, br: float, bl: float, /) -> None

        Parameters
        ----------

        a: float
            x-coordinate of the rectangle by default

        b: float
            y-coordinate of the rectangle by default

        bl: float
            radius for bottom-left corner

        br: float
            radius for bottom-right corner

        c: float
            width of the rectangle by default

        d: float
            height of the rectangle by default

        r: float
            radii for all four corners

        tl: float
            radius for top-left corner

        tr: float
            radius for top-right corner

        Notes
        -----

        Draws a rectangle to the screen. A rectangle is a four-sided shape with every
        angle at ninety degrees. By default, the first two parameters set the location
        of the upper-left corner, the third sets the width, and the fourth sets the
        height. The way these parameters are interpreted, however, may be changed with
        the `rect_mode()` function.

        To draw a rounded rectangle, add a fifth parameter, which is used as the radius
        value for all four corners.

        To use a different radius value for each corner, include eight parameters. When
        using eight parameters, the latter four set the radius of the arc at each corner
        separately, starting with the top-left corner and moving clockwise around the
        rectangle.
        """
        pass

    def rect(self, *args):
        """Draws a rectangle to the screen.

        Underlying Processing method: PApplet.rect

        Methods
        -------

        You can use any of the following signatures:

         * rect(a: float, b: float, c: float, d: float, /) -> None
         * rect(a: float, b: float, c: float, d: float, r: float, /) -> None
         * rect(a: float, b: float, c: float, d: float, tl: float, tr: float, br: float, bl: float, /) -> None

        Parameters
        ----------

        a: float
            x-coordinate of the rectangle by default

        b: float
            y-coordinate of the rectangle by default

        bl: float
            radius for bottom-left corner

        br: float
            radius for bottom-right corner

        c: float
            width of the rectangle by default

        d: float
            height of the rectangle by default

        r: float
            radii for all four corners

        tl: float
            radius for top-left corner

        tr: float
            radius for top-right corner

        Notes
        -----

        Draws a rectangle to the screen. A rectangle is a four-sided shape with every
        angle at ninety degrees. By default, the first two parameters set the location
        of the upper-left corner, the third sets the width, and the fourth sets the
        height. The way these parameters are interpreted, however, may be changed with
        the `rect_mode()` function.

        To draw a rounded rectangle, add a fifth parameter, which is used as the radius
        value for all four corners.

        To use a different radius value for each corner, include eight parameters. When
        using eight parameters, the latter four set the radius of the arc at each corner
        separately, starting with the top-left corner and moving clockwise around the
        rectangle.
        """
        return self._instance.rect(*args)

    def rect_mode(self, mode: int, /) -> None:
        """Modifies the location from which rectangles are drawn by changing the way in
        which parameters given to `rect()` are intepreted.

        Underlying Processing method: PApplet.rectMode

        Parameters
        ----------

        mode: int
            either CORNER, CORNERS, CENTER, or RADIUS

        Notes
        -----

        Modifies the location from which rectangles are drawn by changing the way in
        which parameters given to `rect()` are intepreted.

        The default mode is `rect_mode(CORNER)`, which interprets the first two
        parameters of `rect()` as the upper-left corner of the shape, while the third
        and fourth parameters are its width and height.

        `rect_mode(CORNERS)` interprets the first two parameters of `rect()` as the
        location of one corner, and the third and fourth parameters as the location of
        the opposite corner.

        `rect_mode(CENTER)` interprets the first two parameters of `rect()` as the
        shape's center point, while the third and fourth parameters are its width and
        height.

        `rect_mode(RADIUS)` also uses the first two parameters of `rect()` as the
        shape's center point, but uses the third and fourth parameters to specify half
        of the shapes's width and height.

        The parameter must be written in ALL CAPS because Python is a case-sensitive
        language.
        """
        return self._instance.rectMode(mode)

    @_convert_hex_color()
    def red(self, rgb: int, /) -> float:
        """Extracts the red value from a color, scaled to match current `color_mode()`.

        Underlying Processing method: PApplet.red

        Parameters
        ----------

        rgb: int
            any value of the color datatype

        Notes
        -----

        Extracts the red value from a color, scaled to match current `color_mode()`.

        The `red()` function is easy to use and understand, but it is slower than a
        technique called bit shifting. When working in `color_mode(RGB, 255)`, you can
        achieve the same results as `red()` but with greater speed by using the right
        shift operator (`>>`) with a bit mask. For example, `red(c)` and `c >> 16 &
        0xFF` both extract the red value from a color variable `c` but the later is
        faster.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        return self._instance.red(rgb)

    def redraw(self) -> None:
        """Executes the code within `draw()` one time.

        Underlying Processing method: PApplet.redraw

        Notes
        -----

        Executes the code within `draw()` one time. This functions allows the program to
        update the display window only when necessary, for example when an event
        registered by `mouse_pressed()` or `key_pressed()` occurs.

        In structuring a program, it only makes sense to call `redraw()` within events
        such as `mouse_pressed()`. This is because `redraw()` does not run `draw()`
        immediately (it only sets a flag that indicates an update is needed).

        The `redraw()` function does not work properly when called inside `draw()`. To
        enable/disable animations, use `loop()` and `no_loop()`.
        """
        return self._instance.redraw()

    def reset_matrix(self) -> None:
        """Replaces the current matrix with the identity matrix.

        Underlying Processing method: PApplet.resetMatrix

        Notes
        -----

        Replaces the current matrix with the identity matrix. The equivalent function in
        OpenGL is `gl_load_identity()`.
        """
        return self._instance.resetMatrix()

    @overload
    def reset_shader(self) -> None:
        """Restores the default shaders.

        Underlying Processing method: PApplet.resetShader

        Methods
        -------

        You can use any of the following signatures:

         * reset_shader() -> None
         * reset_shader(kind: int, /) -> None

        Parameters
        ----------

        kind: int
            type of shader, either POINTS, LINES, or TRIANGLES

        Notes
        -----

        Restores the default shaders. Code that runs after `reset_shader()` will not be
        affected by previously defined shaders.
        """
        pass

    @overload
    def reset_shader(self, kind: int, /) -> None:
        """Restores the default shaders.

        Underlying Processing method: PApplet.resetShader

        Methods
        -------

        You can use any of the following signatures:

         * reset_shader() -> None
         * reset_shader(kind: int, /) -> None

        Parameters
        ----------

        kind: int
            type of shader, either POINTS, LINES, or TRIANGLES

        Notes
        -----

        Restores the default shaders. Code that runs after `reset_shader()` will not be
        affected by previously defined shaders.
        """
        pass

    def reset_shader(self, *args):
        """Restores the default shaders.

        Underlying Processing method: PApplet.resetShader

        Methods
        -------

        You can use any of the following signatures:

         * reset_shader() -> None
         * reset_shader(kind: int, /) -> None

        Parameters
        ----------

        kind: int
            type of shader, either POINTS, LINES, or TRIANGLES

        Notes
        -----

        Restores the default shaders. Code that runs after `reset_shader()` will not be
        affected by previously defined shaders.
        """
        return self._instance.resetShader(*args)

    @overload
    def rotate(self, angle: float, /) -> None:
        """Rotates the amount specified by the `angle` parameter.

        Underlying Processing method: PApplet.rotate

        Methods
        -------

        You can use any of the following signatures:

         * rotate(angle: float, /) -> None
         * rotate(angle: float, x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        angle: float
            angle of rotation specified in radians

        x: float
            x-coordinate of vector to rotate around

        y: float
            y-coordinate of vector to rotate around

        z: float
            z-coordinate of vector to rotate around

        Notes
        -----

        Rotates the amount specified by the `angle` parameter. Angles must be specified
        in radians (values from `0` to `TWO_PI`), or they can be converted from degrees
        to radians with the `radians()` function.

        The coordinates are always rotated around their relative position to the origin.
        Positive numbers rotate objects in a clockwise direction and negative numbers
        rotate in the couterclockwise direction. Transformations apply to everything
        that happens afterward, and subsequent calls to the function compound the
        effect. For example, calling `rotate(PI/2.0)` once and then calling
        `rotate(PI/2.0)` a second time is the same as a single `rotate(PI)`. All
        tranformations are reset when `draw()` begins again.

        Technically, `rotate()` multiplies the current transformation matrix by a
        rotation matrix. This function can be further controlled by `push_matrix()` and
        `pop_matrix()`.
        """
        pass

    @overload
    def rotate(self, angle: float, x: float, y: float, z: float, /) -> None:
        """Rotates the amount specified by the `angle` parameter.

        Underlying Processing method: PApplet.rotate

        Methods
        -------

        You can use any of the following signatures:

         * rotate(angle: float, /) -> None
         * rotate(angle: float, x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        angle: float
            angle of rotation specified in radians

        x: float
            x-coordinate of vector to rotate around

        y: float
            y-coordinate of vector to rotate around

        z: float
            z-coordinate of vector to rotate around

        Notes
        -----

        Rotates the amount specified by the `angle` parameter. Angles must be specified
        in radians (values from `0` to `TWO_PI`), or they can be converted from degrees
        to radians with the `radians()` function.

        The coordinates are always rotated around their relative position to the origin.
        Positive numbers rotate objects in a clockwise direction and negative numbers
        rotate in the couterclockwise direction. Transformations apply to everything
        that happens afterward, and subsequent calls to the function compound the
        effect. For example, calling `rotate(PI/2.0)` once and then calling
        `rotate(PI/2.0)` a second time is the same as a single `rotate(PI)`. All
        tranformations are reset when `draw()` begins again.

        Technically, `rotate()` multiplies the current transformation matrix by a
        rotation matrix. This function can be further controlled by `push_matrix()` and
        `pop_matrix()`.
        """
        pass

    def rotate(self, *args):
        """Rotates the amount specified by the `angle` parameter.

        Underlying Processing method: PApplet.rotate

        Methods
        -------

        You can use any of the following signatures:

         * rotate(angle: float, /) -> None
         * rotate(angle: float, x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        angle: float
            angle of rotation specified in radians

        x: float
            x-coordinate of vector to rotate around

        y: float
            y-coordinate of vector to rotate around

        z: float
            z-coordinate of vector to rotate around

        Notes
        -----

        Rotates the amount specified by the `angle` parameter. Angles must be specified
        in radians (values from `0` to `TWO_PI`), or they can be converted from degrees
        to radians with the `radians()` function.

        The coordinates are always rotated around their relative position to the origin.
        Positive numbers rotate objects in a clockwise direction and negative numbers
        rotate in the couterclockwise direction. Transformations apply to everything
        that happens afterward, and subsequent calls to the function compound the
        effect. For example, calling `rotate(PI/2.0)` once and then calling
        `rotate(PI/2.0)` a second time is the same as a single `rotate(PI)`. All
        tranformations are reset when `draw()` begins again.

        Technically, `rotate()` multiplies the current transformation matrix by a
        rotation matrix. This function can be further controlled by `push_matrix()` and
        `pop_matrix()`.
        """
        return self._instance.rotate(*args)

    def rotate_x(self, angle: float, /) -> None:
        """Rotates around the x-axis the amount specified by the `angle` parameter.

        Underlying Processing method: PApplet.rotateX

        Parameters
        ----------

        angle: float
            angle of rotation specified in radians

        Notes
        -----

        Rotates around the x-axis the amount specified by the `angle` parameter. Angles
        should be specified in radians (values from `0` to `TWO_PI`) or converted from
        degrees to radians with the `radians()` function. Coordinates are always rotated
        around their relative position to the origin. Positive numbers rotate in a
        clockwise direction and negative numbers rotate in a counterclockwise direction.
        Transformations apply to everything that happens after and subsequent calls to
        the function accumulates the effect. For example, calling `rotate_x(PI/2)` and
        then `rotate_x(PI/2)` is the same as `rotate_x(PI)`. If `rotate_x()` is run
        within the `draw()`, the transformation is reset when the loop begins again.
        This function requires using `P3D` as a third parameter to `size()` as shown in
        the example.
        """
        return self._instance.rotateX(angle)

    def rotate_y(self, angle: float, /) -> None:
        """Rotates around the y-axis the amount specified by the `angle` parameter.

        Underlying Processing method: PApplet.rotateY

        Parameters
        ----------

        angle: float
            angle of rotation specified in radians

        Notes
        -----

        Rotates around the y-axis the amount specified by the `angle` parameter. Angles
        should be specified in radians (values from `0` to `TWO_PI`) or converted from
        degrees to radians with the `radians()` function. Coordinates are always rotated
        around their relative position to the origin. Positive numbers rotate in a
        clockwise direction and negative numbers rotate in a counterclockwise direction.
        Transformations apply to everything that happens after and subsequent calls to
        the function accumulates the effect. For example, calling `rotate_y(PI/2)` and
        then `rotate_y(PI/2)` is the same as `rotate_y(PI)`. If `rotate_y()` is run
        within the `draw()`, the transformation is reset when the loop begins again.
        This function requires using `P3D` as a third parameter to `size()` as shown in
        the example.
        """
        return self._instance.rotateY(angle)

    def rotate_z(self, angle: float, /) -> None:
        """Rotates around the z-axis the amount specified by the `angle` parameter.

        Underlying Processing method: PApplet.rotateZ

        Parameters
        ----------

        angle: float
            angle of rotation specified in radians

        Notes
        -----

        Rotates around the z-axis the amount specified by the `angle` parameter. Angles
        should be specified in radians (values from `0` to `TWO_PI`) or converted from
        degrees to radians with the `radians()` function. Coordinates are always rotated
        around their relative position to the origin. Positive numbers rotate in a
        clockwise direction and negative numbers rotate in a counterclockwise direction.
        Transformations apply to everything that happens after and subsequent calls to
        the function accumulates the effect. For example, calling `rotate_z(PI/2)` and
        then `rotate_z(PI/2)` is the same as `rotate_z(PI)`. If `rotate_z()` is run
        within the `draw()`, the transformation is reset when the loop begins again.
        This function requires using `P3D` as a third parameter to `size()` as shown in
        the example.
        """
        return self._instance.rotateZ(angle)

    @_convert_hex_color()
    def saturation(self, rgb: int, /) -> float:
        """Extracts the saturation value from a color.

        Underlying Processing method: PApplet.saturation

        Parameters
        ----------

        rgb: int
            any value of the color datatype

        Notes
        -----

        Extracts the saturation value from a color.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        return self._instance.saturation(rgb)

    @overload
    def scale(self, s: float, /) -> None:
        """Increases or decreases the size of a shape by expanding and contracting
        vertices.

        Underlying Processing method: PApplet.scale

        Methods
        -------

        You can use any of the following signatures:

         * scale(s: float, /) -> None
         * scale(x: float, y: float, /) -> None
         * scale(x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        s: float
            percentage to scale the object

        x: float
            percentage to scale the object in the x-axis

        y: float
            percentage to scale the object in the y-axis

        z: float
            percentage to scale the object in the z-axis

        Notes
        -----

        Increases or decreases the size of a shape by expanding and contracting
        vertices. Objects always scale from their relative origin to the coordinate
        system. Scale values are specified as decimal percentages. For example, the
        function call `scale(2.0)` increases the dimension of a shape by 200%.

        Transformations apply to everything that happens after and subsequent calls to
        the function multiply the effect. For example, calling `scale(2.0)` and then
        `scale(1.5)` is the same as `scale(3.0)`. If `scale()` is called within
        `draw()`, the transformation is reset when the loop begins again. Using this
        function with the `z` parameter requires using `P3D` as a parameter for
        `size()`, as shown in the third example. This function can be further controlled
        with `push_matrix()` and `pop_matrix()`.
        """
        pass

    @overload
    def scale(self, x: float, y: float, /) -> None:
        """Increases or decreases the size of a shape by expanding and contracting
        vertices.

        Underlying Processing method: PApplet.scale

        Methods
        -------

        You can use any of the following signatures:

         * scale(s: float, /) -> None
         * scale(x: float, y: float, /) -> None
         * scale(x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        s: float
            percentage to scale the object

        x: float
            percentage to scale the object in the x-axis

        y: float
            percentage to scale the object in the y-axis

        z: float
            percentage to scale the object in the z-axis

        Notes
        -----

        Increases or decreases the size of a shape by expanding and contracting
        vertices. Objects always scale from their relative origin to the coordinate
        system. Scale values are specified as decimal percentages. For example, the
        function call `scale(2.0)` increases the dimension of a shape by 200%.

        Transformations apply to everything that happens after and subsequent calls to
        the function multiply the effect. For example, calling `scale(2.0)` and then
        `scale(1.5)` is the same as `scale(3.0)`. If `scale()` is called within
        `draw()`, the transformation is reset when the loop begins again. Using this
        function with the `z` parameter requires using `P3D` as a parameter for
        `size()`, as shown in the third example. This function can be further controlled
        with `push_matrix()` and `pop_matrix()`.
        """
        pass

    @overload
    def scale(self, x: float, y: float, z: float, /) -> None:
        """Increases or decreases the size of a shape by expanding and contracting
        vertices.

        Underlying Processing method: PApplet.scale

        Methods
        -------

        You can use any of the following signatures:

         * scale(s: float, /) -> None
         * scale(x: float, y: float, /) -> None
         * scale(x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        s: float
            percentage to scale the object

        x: float
            percentage to scale the object in the x-axis

        y: float
            percentage to scale the object in the y-axis

        z: float
            percentage to scale the object in the z-axis

        Notes
        -----

        Increases or decreases the size of a shape by expanding and contracting
        vertices. Objects always scale from their relative origin to the coordinate
        system. Scale values are specified as decimal percentages. For example, the
        function call `scale(2.0)` increases the dimension of a shape by 200%.

        Transformations apply to everything that happens after and subsequent calls to
        the function multiply the effect. For example, calling `scale(2.0)` and then
        `scale(1.5)` is the same as `scale(3.0)`. If `scale()` is called within
        `draw()`, the transformation is reset when the loop begins again. Using this
        function with the `z` parameter requires using `P3D` as a parameter for
        `size()`, as shown in the third example. This function can be further controlled
        with `push_matrix()` and `pop_matrix()`.
        """
        pass

    def scale(self, *args):
        """Increases or decreases the size of a shape by expanding and contracting
        vertices.

        Underlying Processing method: PApplet.scale

        Methods
        -------

        You can use any of the following signatures:

         * scale(s: float, /) -> None
         * scale(x: float, y: float, /) -> None
         * scale(x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        s: float
            percentage to scale the object

        x: float
            percentage to scale the object in the x-axis

        y: float
            percentage to scale the object in the y-axis

        z: float
            percentage to scale the object in the z-axis

        Notes
        -----

        Increases or decreases the size of a shape by expanding and contracting
        vertices. Objects always scale from their relative origin to the coordinate
        system. Scale values are specified as decimal percentages. For example, the
        function call `scale(2.0)` increases the dimension of a shape by 200%.

        Transformations apply to everything that happens after and subsequent calls to
        the function multiply the effect. For example, calling `scale(2.0)` and then
        `scale(1.5)` is the same as `scale(3.0)`. If `scale()` is called within
        `draw()`, the transformation is reset when the loop begins again. Using this
        function with the `z` parameter requires using `P3D` as a parameter for
        `size()`, as shown in the third example. This function can be further controlled
        with `push_matrix()` and `pop_matrix()`.
        """
        return self._instance.scale(*args)

    @overload
    def screen_x(self, x: float, y: float, /) -> float:
        """Takes a three-dimensional X, Y, Z position and returns the X value for where it
        will appear on a (two-dimensional) screen.

        Underlying Processing method: PApplet.screenX

        Methods
        -------

        You can use any of the following signatures:

         * screen_x(x: float, y: float, /) -> float
         * screen_x(x: float, y: float, z: float, /) -> float

        Parameters
        ----------

        x: float
            3D x-coordinate to be mapped

        y: float
            3D y-coordinate to be mapped

        z: float
            3D z-coordinate to be mapped

        Notes
        -----

        Takes a three-dimensional X, Y, Z position and returns the X value for where it
        will appear on a (two-dimensional) screen.
        """
        pass

    @overload
    def screen_x(self, x: float, y: float, z: float, /) -> float:
        """Takes a three-dimensional X, Y, Z position and returns the X value for where it
        will appear on a (two-dimensional) screen.

        Underlying Processing method: PApplet.screenX

        Methods
        -------

        You can use any of the following signatures:

         * screen_x(x: float, y: float, /) -> float
         * screen_x(x: float, y: float, z: float, /) -> float

        Parameters
        ----------

        x: float
            3D x-coordinate to be mapped

        y: float
            3D y-coordinate to be mapped

        z: float
            3D z-coordinate to be mapped

        Notes
        -----

        Takes a three-dimensional X, Y, Z position and returns the X value for where it
        will appear on a (two-dimensional) screen.
        """
        pass

    def screen_x(self, *args):
        """Takes a three-dimensional X, Y, Z position and returns the X value for where it
        will appear on a (two-dimensional) screen.

        Underlying Processing method: PApplet.screenX

        Methods
        -------

        You can use any of the following signatures:

         * screen_x(x: float, y: float, /) -> float
         * screen_x(x: float, y: float, z: float, /) -> float

        Parameters
        ----------

        x: float
            3D x-coordinate to be mapped

        y: float
            3D y-coordinate to be mapped

        z: float
            3D z-coordinate to be mapped

        Notes
        -----

        Takes a three-dimensional X, Y, Z position and returns the X value for where it
        will appear on a (two-dimensional) screen.
        """
        return self._instance.screenX(*args)

    @overload
    def screen_y(self, x: float, y: float, /) -> float:
        """Takes a three-dimensional X, Y, Z position and returns the Y value for where it
        will appear on a (two-dimensional) screen.

        Underlying Processing method: PApplet.screenY

        Methods
        -------

        You can use any of the following signatures:

         * screen_y(x: float, y: float, /) -> float
         * screen_y(x: float, y: float, z: float, /) -> float

        Parameters
        ----------

        x: float
            3D x-coordinate to be mapped

        y: float
            3D y-coordinate to be mapped

        z: float
            3D z-coordinate to be mapped

        Notes
        -----

        Takes a three-dimensional X, Y, Z position and returns the Y value for where it
        will appear on a (two-dimensional) screen.
        """
        pass

    @overload
    def screen_y(self, x: float, y: float, z: float, /) -> float:
        """Takes a three-dimensional X, Y, Z position and returns the Y value for where it
        will appear on a (two-dimensional) screen.

        Underlying Processing method: PApplet.screenY

        Methods
        -------

        You can use any of the following signatures:

         * screen_y(x: float, y: float, /) -> float
         * screen_y(x: float, y: float, z: float, /) -> float

        Parameters
        ----------

        x: float
            3D x-coordinate to be mapped

        y: float
            3D y-coordinate to be mapped

        z: float
            3D z-coordinate to be mapped

        Notes
        -----

        Takes a three-dimensional X, Y, Z position and returns the Y value for where it
        will appear on a (two-dimensional) screen.
        """
        pass

    def screen_y(self, *args):
        """Takes a three-dimensional X, Y, Z position and returns the Y value for where it
        will appear on a (two-dimensional) screen.

        Underlying Processing method: PApplet.screenY

        Methods
        -------

        You can use any of the following signatures:

         * screen_y(x: float, y: float, /) -> float
         * screen_y(x: float, y: float, z: float, /) -> float

        Parameters
        ----------

        x: float
            3D x-coordinate to be mapped

        y: float
            3D y-coordinate to be mapped

        z: float
            3D z-coordinate to be mapped

        Notes
        -----

        Takes a three-dimensional X, Y, Z position and returns the Y value for where it
        will appear on a (two-dimensional) screen.
        """
        return self._instance.screenY(*args)

    def screen_z(self, x: float, y: float, z: float, /) -> float:
        """Takes a three-dimensional X, Y, Z position and returns the Z value for where it
        will appear on a (two-dimensional) screen.

        Underlying Processing method: PApplet.screenZ

        Parameters
        ----------

        x: float
            3D x-coordinate to be mapped

        y: float
            3D y-coordinate to be mapped

        z: float
            3D z-coordinate to be mapped

        Notes
        -----

        Takes a three-dimensional X, Y, Z position and returns the Z value for where it
        will appear on a (two-dimensional) screen.
        """
        return self._instance.screenZ(x, y, z)

    @classmethod
    def second(cls) -> int:
        """Py5 communicates with the clock on your computer.

        Underlying Processing method: PApplet.second

        Notes
        -----

        Py5 communicates with the clock on your computer. The `second()` function
        returns the current second as a value from 0 - 59.
        """
        return cls._cls.second()

    @overload
    def set_pixels(self, x: int, y: int, c: int, /) -> None:
        """Changes the color of any pixel or writes an image directly into the drawing
        surface.

        Underlying Processing method: Sketch.set

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
            image to copy into the Sketch window

        x: int
            x-coordinate of the pixel

        y: int
            y-coordinate of the pixel

        Notes
        -----

        Changes the color of any pixel or writes an image directly into the drawing
        surface.

        The `x` and `y` parameters specify the pixel to change and the color parameter
        specifies the color value. The color parameter `c` is affected by the current
        color mode (the default is RGB values from 0 to 255). When setting an image, the
        `x` and `y` parameters define the coordinates for the upper-left corner of the
        image, regardless of the current `image_mode()`.

        Setting the color of a single pixel with `py5.set_pixels(x, y)` is easy, but not
        as fast as putting the data directly into `pixels[]`. The equivalent statement
        to `py5.set_pixels(x, y, 0)` using `pixels[]` is `py5.pixels[y*py5.width+x] =
        0`. See the reference for `pixels[]` for more information.
        """
        pass

    @overload
    def set_pixels(self, x: int, y: int, img: Py5Image, /) -> None:
        """Changes the color of any pixel or writes an image directly into the drawing
        surface.

        Underlying Processing method: Sketch.set

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
            image to copy into the Sketch window

        x: int
            x-coordinate of the pixel

        y: int
            y-coordinate of the pixel

        Notes
        -----

        Changes the color of any pixel or writes an image directly into the drawing
        surface.

        The `x` and `y` parameters specify the pixel to change and the color parameter
        specifies the color value. The color parameter `c` is affected by the current
        color mode (the default is RGB values from 0 to 255). When setting an image, the
        `x` and `y` parameters define the coordinates for the upper-left corner of the
        image, regardless of the current `image_mode()`.

        Setting the color of a single pixel with `py5.set_pixels(x, y)` is easy, but not
        as fast as putting the data directly into `pixels[]`. The equivalent statement
        to `py5.set_pixels(x, y, 0)` using `pixels[]` is `py5.pixels[y*py5.width+x] =
        0`. See the reference for `pixels[]` for more information.
        """
        pass

    @_auto_convert_to_py5image(2)
    def set_pixels(self, *args):
        """Changes the color of any pixel or writes an image directly into the drawing
        surface.

        Underlying Processing method: Sketch.set

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
            image to copy into the Sketch window

        x: int
            x-coordinate of the pixel

        y: int
            y-coordinate of the pixel

        Notes
        -----

        Changes the color of any pixel or writes an image directly into the drawing
        surface.

        The `x` and `y` parameters specify the pixel to change and the color parameter
        specifies the color value. The color parameter `c` is affected by the current
        color mode (the default is RGB values from 0 to 255). When setting an image, the
        `x` and `y` parameters define the coordinates for the upper-left corner of the
        image, regardless of the current `image_mode()`.

        Setting the color of a single pixel with `py5.set_pixels(x, y)` is easy, but not
        as fast as putting the data directly into `pixels[]`. The equivalent statement
        to `py5.set_pixels(x, y, 0)` using `pixels[]` is `py5.pixels[y*py5.width+x] =
        0`. See the reference for `pixels[]` for more information.
        """
        return self._instance.set(*args)

    @overload
    def set_matrix(self, source: npt.NDArray[np.floating], /) -> None:
        """Set the current matrix to the one specified through the parameter `source`.

        Underlying Processing method: PApplet.setMatrix

        Parameters
        ----------

        source: npt.NDArray[np.floating]
            transformation matrix with a shape of 2x3 for 2D transforms or 4x4 for 3D transforms

        Notes
        -----

        Set the current matrix to the one specified through the parameter `source`.
        Inside the Processing code it will call `reset_matrix()` followed by
        `apply_matrix()`. This will be very slow because `apply_matrix()` will try to
        calculate the inverse of the transform, so avoid it whenever possible.
        """
        pass

    def set_matrix(self, *args):
        """Set the current matrix to the one specified through the parameter `source`.

        Underlying Processing method: PApplet.setMatrix

        Parameters
        ----------

        source: npt.NDArray[np.floating]
            transformation matrix with a shape of 2x3 for 2D transforms or 4x4 for 3D transforms

        Notes
        -----

        Set the current matrix to the one specified through the parameter `source`.
        Inside the Processing code it will call `reset_matrix()` followed by
        `apply_matrix()`. This will be very slow because `apply_matrix()` will try to
        calculate the inverse of the transform, so avoid it whenever possible.
        """
        return self._instance.setMatrix(*args)

    @overload
    def shader(self, shader: Py5Shader, /) -> None:
        """Applies the shader specified by the parameters.

        Underlying Processing method: PApplet.shader

        Methods
        -------

        You can use any of the following signatures:

         * shader(shader: Py5Shader, /) -> None
         * shader(shader: Py5Shader, kind: int, /) -> None

        Parameters
        ----------

        kind: int
            type of shader, either POINTS, LINES, or TRIANGLES

        shader: Py5Shader
            name of shader file

        Notes
        -----

        Applies the shader specified by the parameters. It's compatible with the `P2D`
        and `P3D` renderers, but not with the default renderer.
        """
        pass

    @overload
    def shader(self, shader: Py5Shader, kind: int, /) -> None:
        """Applies the shader specified by the parameters.

        Underlying Processing method: PApplet.shader

        Methods
        -------

        You can use any of the following signatures:

         * shader(shader: Py5Shader, /) -> None
         * shader(shader: Py5Shader, kind: int, /) -> None

        Parameters
        ----------

        kind: int
            type of shader, either POINTS, LINES, or TRIANGLES

        shader: Py5Shader
            name of shader file

        Notes
        -----

        Applies the shader specified by the parameters. It's compatible with the `P2D`
        and `P3D` renderers, but not with the default renderer.
        """
        pass

    def shader(self, *args):
        """Applies the shader specified by the parameters.

        Underlying Processing method: PApplet.shader

        Methods
        -------

        You can use any of the following signatures:

         * shader(shader: Py5Shader, /) -> None
         * shader(shader: Py5Shader, kind: int, /) -> None

        Parameters
        ----------

        kind: int
            type of shader, either POINTS, LINES, or TRIANGLES

        shader: Py5Shader
            name of shader file

        Notes
        -----

        Applies the shader specified by the parameters. It's compatible with the `P2D`
        and `P3D` renderers, but not with the default renderer.
        """
        return self._instance.shader(*args)

    @overload
    def shape(self, shape: Py5Shape, /) -> None:
        """Draws shapes to the display window.

        Underlying Processing method: PApplet.shape

        Methods
        -------

        You can use any of the following signatures:

         * shape(shape: Py5Shape, /) -> None
         * shape(shape: Py5Shape, a: float, b: float, c: float, d: float, /) -> None
         * shape(shape: Py5Shape, x: float, y: float, /) -> None

        Parameters
        ----------

        a: float
            x-coordinate of the shape

        b: float
            y-coordinate of the shape

        c: float
            width to display the shape

        d: float
            height to display the shape

        shape: Py5Shape
            the shape to display

        x: float
            x-coordinate of the shape

        y: float
            y-coordinate of the shape

        Notes
        -----

        Draws shapes to the display window. Shapes must be in the Sketch's "data"
        directory to load correctly. Py5 currently works with SVG, OBJ, and custom-
        created shapes. The `shape` parameter specifies the shape to display and the
        coordinate parameters define the location of the shape from its upper-left
        corner. The shape is displayed at its original size unless the `c` and `d`
        parameters specify a different size. The `shape_mode()` function can be used to
        change the way these parameters are interpreted.
        """
        pass

    @overload
    def shape(self, shape: Py5Shape, x: float, y: float, /) -> None:
        """Draws shapes to the display window.

        Underlying Processing method: PApplet.shape

        Methods
        -------

        You can use any of the following signatures:

         * shape(shape: Py5Shape, /) -> None
         * shape(shape: Py5Shape, a: float, b: float, c: float, d: float, /) -> None
         * shape(shape: Py5Shape, x: float, y: float, /) -> None

        Parameters
        ----------

        a: float
            x-coordinate of the shape

        b: float
            y-coordinate of the shape

        c: float
            width to display the shape

        d: float
            height to display the shape

        shape: Py5Shape
            the shape to display

        x: float
            x-coordinate of the shape

        y: float
            y-coordinate of the shape

        Notes
        -----

        Draws shapes to the display window. Shapes must be in the Sketch's "data"
        directory to load correctly. Py5 currently works with SVG, OBJ, and custom-
        created shapes. The `shape` parameter specifies the shape to display and the
        coordinate parameters define the location of the shape from its upper-left
        corner. The shape is displayed at its original size unless the `c` and `d`
        parameters specify a different size. The `shape_mode()` function can be used to
        change the way these parameters are interpreted.
        """
        pass

    @overload
    def shape(self, shape: Py5Shape, a: float, b: float, c: float, d: float, /) -> None:
        """Draws shapes to the display window.

        Underlying Processing method: PApplet.shape

        Methods
        -------

        You can use any of the following signatures:

         * shape(shape: Py5Shape, /) -> None
         * shape(shape: Py5Shape, a: float, b: float, c: float, d: float, /) -> None
         * shape(shape: Py5Shape, x: float, y: float, /) -> None

        Parameters
        ----------

        a: float
            x-coordinate of the shape

        b: float
            y-coordinate of the shape

        c: float
            width to display the shape

        d: float
            height to display the shape

        shape: Py5Shape
            the shape to display

        x: float
            x-coordinate of the shape

        y: float
            y-coordinate of the shape

        Notes
        -----

        Draws shapes to the display window. Shapes must be in the Sketch's "data"
        directory to load correctly. Py5 currently works with SVG, OBJ, and custom-
        created shapes. The `shape` parameter specifies the shape to display and the
        coordinate parameters define the location of the shape from its upper-left
        corner. The shape is displayed at its original size unless the `c` and `d`
        parameters specify a different size. The `shape_mode()` function can be used to
        change the way these parameters are interpreted.
        """
        pass

    @_auto_convert_to_py5shape
    def shape(self, *args):
        """Draws shapes to the display window.

        Underlying Processing method: PApplet.shape

        Methods
        -------

        You can use any of the following signatures:

         * shape(shape: Py5Shape, /) -> None
         * shape(shape: Py5Shape, a: float, b: float, c: float, d: float, /) -> None
         * shape(shape: Py5Shape, x: float, y: float, /) -> None

        Parameters
        ----------

        a: float
            x-coordinate of the shape

        b: float
            y-coordinate of the shape

        c: float
            width to display the shape

        d: float
            height to display the shape

        shape: Py5Shape
            the shape to display

        x: float
            x-coordinate of the shape

        y: float
            y-coordinate of the shape

        Notes
        -----

        Draws shapes to the display window. Shapes must be in the Sketch's "data"
        directory to load correctly. Py5 currently works with SVG, OBJ, and custom-
        created shapes. The `shape` parameter specifies the shape to display and the
        coordinate parameters define the location of the shape from its upper-left
        corner. The shape is displayed at its original size unless the `c` and `d`
        parameters specify a different size. The `shape_mode()` function can be used to
        change the way these parameters are interpreted.
        """
        return self._instance.shape(*args)

    def shape_mode(self, mode: int, /) -> None:
        """Modifies the location from which shapes draw.

        Underlying Processing method: PApplet.shapeMode

        Parameters
        ----------

        mode: int
            either CORNER, CORNERS, CENTER

        Notes
        -----

        Modifies the location from which shapes draw. The default mode is
        `shape_mode(CORNER)`, which specifies the location to be the upper left corner
        of the shape and uses the third and fourth parameters of `shape()` to specify
        the width and height. The syntax `shape_mode(CORNERS)` uses the first and second
        parameters of `shape()` to set the location of one corner and uses the third and
        fourth parameters to set the opposite corner. The syntax `shape_mode(CENTER)`
        draws the shape from its center point and uses the third and forth parameters of
        `shape()` to specify the width and height. The parameter must be written in ALL
        CAPS because Python is a case sensitive language.
        """
        return self._instance.shapeMode(mode)

    def shear_x(self, angle: float, /) -> None:
        """Shears a shape around the x-axis the amount specified by the `angle` parameter.

        Underlying Processing method: PApplet.shearX

        Parameters
        ----------

        angle: float
            angle of shear specified in radians

        Notes
        -----

        Shears a shape around the x-axis the amount specified by the `angle` parameter.
        Angles should be specified in radians (values from `0` to `TWO_PI`) or converted
        to radians with the `radians()` function. Objects are always sheared around
        their relative position to the origin and positive numbers shear objects in a
        clockwise direction. Transformations apply to everything that happens after and
        subsequent calls to the function accumulates the effect. For example, calling
        `shear_x(PI/2)` and then `shear_x(PI/2)` is the same as `shear_x(PI)`. If
        `shear_x()` is called within the `draw()`, the transformation is reset when the
        loop begins again.

        Technically, `shear_x()` multiplies the current transformation matrix by a
        rotation matrix. This function can be further controlled by the `push_matrix()`
        and `pop_matrix()` functions.
        """
        return self._instance.shearX(angle)

    def shear_y(self, angle: float, /) -> None:
        """Shears a shape around the y-axis the amount specified by the `angle` parameter.

        Underlying Processing method: PApplet.shearY

        Parameters
        ----------

        angle: float
            angle of shear specified in radians

        Notes
        -----

        Shears a shape around the y-axis the amount specified by the `angle` parameter.
        Angles should be specified in radians (values from `0` to `TWO_PI`) or converted
        to radians with the `radians()` function. Objects are always sheared around
        their relative position to the origin and positive numbers shear objects in a
        clockwise direction. Transformations apply to everything that happens after and
        subsequent calls to the function accumulates the effect. For example, calling
        `shear_y(PI/2)` and then `shear_y(PI/2)` is the same as `shear_y(PI)`. If
        `shear_y()` is called within the `draw()`, the transformation is reset when the
        loop begins again.

        Technically, `shear_y()` multiplies the current transformation matrix by a
        rotation matrix. This function can be further controlled by the `push_matrix()`
        and `pop_matrix()` functions.
        """
        return self._instance.shearY(angle)

    def shininess(self, shine: float, /) -> None:
        """Sets the amount of gloss in the surface of shapes.

        Underlying Processing method: PApplet.shininess

        Parameters
        ----------

        shine: float
            degree of shininess

        Notes
        -----

        Sets the amount of gloss in the surface of shapes. Use in combination with
        `ambient()`, `specular()`, and `emissive()` to set the material properties of
        shapes.
        """
        return self._instance.shininess(shine)

    @overload
    def size(self, width: int, height: int, /) -> None:
        """Defines the dimension of the display window width and height in units of pixels.

        Underlying Processing method: PApplet.size

        Methods
        -------

        You can use any of the following signatures:

         * size(width: int, height: int, /) -> None
         * size(width: int, height: int, renderer: str, /) -> None
         * size(width: int, height: int, renderer: str, path: str, /) -> None

        Parameters
        ----------

        height: int
            height of the display window in units of pixels

        path: str
            filename to save rendering engine output to

        renderer: str
            rendering engine to use

        width: int
            width of the display window in units of pixels

        Notes
        -----

        Defines the dimension of the display window width and height in units of pixels.
        This is intended to be called from the `settings()` function.

        When programming in module mode and imported mode, py5 will allow calls to
        `size()` from the `setup()` function if it is called at the beginning of
        `setup()`. This allows the user to omit the `settings()` function, much like
        what can be done while programming in the Processing IDE. Py5 does this by
        inspecting the `setup()` function and attempting to split it into synthetic
        `settings()` and `setup()` functions if both were not created by the user and
        the real `setup()` function contains a call to `size()`, or calls to
        `full_screen()`, `smooth()`, `no_smooth()`, or `pixel_density()`. Calls to those
        functions must be at the very beginning of `setup()`, before any other Python
        code (but comments are ok). This feature is not available when programming in
        class mode.

        The built-in variables `width` and `height` are set by the parameters passed to
        this function. For example, running `size(640, 480)` will assign 640 to the
        `width` variable and 480 to the height `variable`. If `size()` is not used, the
        window will be given a default size of 100 x 100 pixels.

        The `size()` function can only be used once inside a Sketch, and it cannot be
        used for resizing.

        To run a Sketch at the full dimensions of a screen, use the `full_screen()`
        function, rather than the older way of using `size(display_width,
        display_height)`.

        The maximum width and height is limited by your operating system, and is usually
        the width and height of your actual screen. On some machines it may simply be
        the number of pixels on your current screen, meaning that a screen of 800 x 600
        could support `size(1600, 300)`, since that is the same number of pixels. This
        varies widely, so you'll have to try different rendering modes and sizes until
        you get what you're looking for. If you need something larger, use
        `create_graphics` to create a non-visible drawing surface.

        The minimum width and height is around 100 pixels in each direction. This is the
        smallest that is supported across Windows, macOS, and Linux. We enforce the
        minimum size so that Sketches will run identically on different machines.

        The `renderer` parameter selects which rendering engine to use. For example, if
        you will be drawing 3D shapes, use `P3D`. In addition to the default renderer,
        other renderers are:

        * `P2D` (Processing 2D): 2D graphics renderer that makes use of OpenGL-
        compatible graphics hardware.
        * `P3D` (Processing 3D): 3D graphics renderer that makes use of OpenGL-
        compatible graphics hardware.
        * `FX2D` (JavaFX 2D): A 2D renderer that uses JavaFX, which may be faster for
        some applications, but has some compatibility quirks.
        * `PDF`: The `PDF` renderer draws 2D graphics directly to an Acrobat PDF file.
        This produces excellent results when you need vector shapes for high-resolution
        output or printing.
        * `SVG`: The `SVG` renderer draws 2D graphics directly to an SVG file. This is
        great for importing into other vector programs or using for digital fabrication.

        When using the `PDF` and `SVG` renderers with the `size()` method, you must use
        the `path` parameter to specify the file to write the output to. No window will
        open while the Sketch is running. You must also call `exit_sketch()` to exit the
        Sketch and write the completed output to the file. Without this call, the Sketch
        will not exit and the output file will be empty. If you would like to draw 3D
        objects to a PDF or SVG file, use the `P3D` renderer and the strategy described
        in `begin_raw()`.
        """
        pass

    @overload
    def size(self, width: int, height: int, renderer: str, /) -> None:
        """Defines the dimension of the display window width and height in units of pixels.

        Underlying Processing method: PApplet.size

        Methods
        -------

        You can use any of the following signatures:

         * size(width: int, height: int, /) -> None
         * size(width: int, height: int, renderer: str, /) -> None
         * size(width: int, height: int, renderer: str, path: str, /) -> None

        Parameters
        ----------

        height: int
            height of the display window in units of pixels

        path: str
            filename to save rendering engine output to

        renderer: str
            rendering engine to use

        width: int
            width of the display window in units of pixels

        Notes
        -----

        Defines the dimension of the display window width and height in units of pixels.
        This is intended to be called from the `settings()` function.

        When programming in module mode and imported mode, py5 will allow calls to
        `size()` from the `setup()` function if it is called at the beginning of
        `setup()`. This allows the user to omit the `settings()` function, much like
        what can be done while programming in the Processing IDE. Py5 does this by
        inspecting the `setup()` function and attempting to split it into synthetic
        `settings()` and `setup()` functions if both were not created by the user and
        the real `setup()` function contains a call to `size()`, or calls to
        `full_screen()`, `smooth()`, `no_smooth()`, or `pixel_density()`. Calls to those
        functions must be at the very beginning of `setup()`, before any other Python
        code (but comments are ok). This feature is not available when programming in
        class mode.

        The built-in variables `width` and `height` are set by the parameters passed to
        this function. For example, running `size(640, 480)` will assign 640 to the
        `width` variable and 480 to the height `variable`. If `size()` is not used, the
        window will be given a default size of 100 x 100 pixels.

        The `size()` function can only be used once inside a Sketch, and it cannot be
        used for resizing.

        To run a Sketch at the full dimensions of a screen, use the `full_screen()`
        function, rather than the older way of using `size(display_width,
        display_height)`.

        The maximum width and height is limited by your operating system, and is usually
        the width and height of your actual screen. On some machines it may simply be
        the number of pixels on your current screen, meaning that a screen of 800 x 600
        could support `size(1600, 300)`, since that is the same number of pixels. This
        varies widely, so you'll have to try different rendering modes and sizes until
        you get what you're looking for. If you need something larger, use
        `create_graphics` to create a non-visible drawing surface.

        The minimum width and height is around 100 pixels in each direction. This is the
        smallest that is supported across Windows, macOS, and Linux. We enforce the
        minimum size so that Sketches will run identically on different machines.

        The `renderer` parameter selects which rendering engine to use. For example, if
        you will be drawing 3D shapes, use `P3D`. In addition to the default renderer,
        other renderers are:

        * `P2D` (Processing 2D): 2D graphics renderer that makes use of OpenGL-
        compatible graphics hardware.
        * `P3D` (Processing 3D): 3D graphics renderer that makes use of OpenGL-
        compatible graphics hardware.
        * `FX2D` (JavaFX 2D): A 2D renderer that uses JavaFX, which may be faster for
        some applications, but has some compatibility quirks.
        * `PDF`: The `PDF` renderer draws 2D graphics directly to an Acrobat PDF file.
        This produces excellent results when you need vector shapes for high-resolution
        output or printing.
        * `SVG`: The `SVG` renderer draws 2D graphics directly to an SVG file. This is
        great for importing into other vector programs or using for digital fabrication.

        When using the `PDF` and `SVG` renderers with the `size()` method, you must use
        the `path` parameter to specify the file to write the output to. No window will
        open while the Sketch is running. You must also call `exit_sketch()` to exit the
        Sketch and write the completed output to the file. Without this call, the Sketch
        will not exit and the output file will be empty. If you would like to draw 3D
        objects to a PDF or SVG file, use the `P3D` renderer and the strategy described
        in `begin_raw()`.
        """
        pass

    @overload
    def size(self, width: int, height: int, renderer: str, path: str, /) -> None:
        """Defines the dimension of the display window width and height in units of pixels.

        Underlying Processing method: PApplet.size

        Methods
        -------

        You can use any of the following signatures:

         * size(width: int, height: int, /) -> None
         * size(width: int, height: int, renderer: str, /) -> None
         * size(width: int, height: int, renderer: str, path: str, /) -> None

        Parameters
        ----------

        height: int
            height of the display window in units of pixels

        path: str
            filename to save rendering engine output to

        renderer: str
            rendering engine to use

        width: int
            width of the display window in units of pixels

        Notes
        -----

        Defines the dimension of the display window width and height in units of pixels.
        This is intended to be called from the `settings()` function.

        When programming in module mode and imported mode, py5 will allow calls to
        `size()` from the `setup()` function if it is called at the beginning of
        `setup()`. This allows the user to omit the `settings()` function, much like
        what can be done while programming in the Processing IDE. Py5 does this by
        inspecting the `setup()` function and attempting to split it into synthetic
        `settings()` and `setup()` functions if both were not created by the user and
        the real `setup()` function contains a call to `size()`, or calls to
        `full_screen()`, `smooth()`, `no_smooth()`, or `pixel_density()`. Calls to those
        functions must be at the very beginning of `setup()`, before any other Python
        code (but comments are ok). This feature is not available when programming in
        class mode.

        The built-in variables `width` and `height` are set by the parameters passed to
        this function. For example, running `size(640, 480)` will assign 640 to the
        `width` variable and 480 to the height `variable`. If `size()` is not used, the
        window will be given a default size of 100 x 100 pixels.

        The `size()` function can only be used once inside a Sketch, and it cannot be
        used for resizing.

        To run a Sketch at the full dimensions of a screen, use the `full_screen()`
        function, rather than the older way of using `size(display_width,
        display_height)`.

        The maximum width and height is limited by your operating system, and is usually
        the width and height of your actual screen. On some machines it may simply be
        the number of pixels on your current screen, meaning that a screen of 800 x 600
        could support `size(1600, 300)`, since that is the same number of pixels. This
        varies widely, so you'll have to try different rendering modes and sizes until
        you get what you're looking for. If you need something larger, use
        `create_graphics` to create a non-visible drawing surface.

        The minimum width and height is around 100 pixels in each direction. This is the
        smallest that is supported across Windows, macOS, and Linux. We enforce the
        minimum size so that Sketches will run identically on different machines.

        The `renderer` parameter selects which rendering engine to use. For example, if
        you will be drawing 3D shapes, use `P3D`. In addition to the default renderer,
        other renderers are:

        * `P2D` (Processing 2D): 2D graphics renderer that makes use of OpenGL-
        compatible graphics hardware.
        * `P3D` (Processing 3D): 3D graphics renderer that makes use of OpenGL-
        compatible graphics hardware.
        * `FX2D` (JavaFX 2D): A 2D renderer that uses JavaFX, which may be faster for
        some applications, but has some compatibility quirks.
        * `PDF`: The `PDF` renderer draws 2D graphics directly to an Acrobat PDF file.
        This produces excellent results when you need vector shapes for high-resolution
        output or printing.
        * `SVG`: The `SVG` renderer draws 2D graphics directly to an SVG file. This is
        great for importing into other vector programs or using for digital fabrication.

        When using the `PDF` and `SVG` renderers with the `size()` method, you must use
        the `path` parameter to specify the file to write the output to. No window will
        open while the Sketch is running. You must also call `exit_sketch()` to exit the
        Sketch and write the completed output to the file. Without this call, the Sketch
        will not exit and the output file will be empty. If you would like to draw 3D
        objects to a PDF or SVG file, use the `P3D` renderer and the strategy described
        in `begin_raw()`.
        """
        pass

    @_settings_only("size")
    def size(self, *args):
        """Defines the dimension of the display window width and height in units of pixels.

        Underlying Processing method: PApplet.size

        Methods
        -------

        You can use any of the following signatures:

         * size(width: int, height: int, /) -> None
         * size(width: int, height: int, renderer: str, /) -> None
         * size(width: int, height: int, renderer: str, path: str, /) -> None

        Parameters
        ----------

        height: int
            height of the display window in units of pixels

        path: str
            filename to save rendering engine output to

        renderer: str
            rendering engine to use

        width: int
            width of the display window in units of pixels

        Notes
        -----

        Defines the dimension of the display window width and height in units of pixels.
        This is intended to be called from the `settings()` function.

        When programming in module mode and imported mode, py5 will allow calls to
        `size()` from the `setup()` function if it is called at the beginning of
        `setup()`. This allows the user to omit the `settings()` function, much like
        what can be done while programming in the Processing IDE. Py5 does this by
        inspecting the `setup()` function and attempting to split it into synthetic
        `settings()` and `setup()` functions if both were not created by the user and
        the real `setup()` function contains a call to `size()`, or calls to
        `full_screen()`, `smooth()`, `no_smooth()`, or `pixel_density()`. Calls to those
        functions must be at the very beginning of `setup()`, before any other Python
        code (but comments are ok). This feature is not available when programming in
        class mode.

        The built-in variables `width` and `height` are set by the parameters passed to
        this function. For example, running `size(640, 480)` will assign 640 to the
        `width` variable and 480 to the height `variable`. If `size()` is not used, the
        window will be given a default size of 100 x 100 pixels.

        The `size()` function can only be used once inside a Sketch, and it cannot be
        used for resizing.

        To run a Sketch at the full dimensions of a screen, use the `full_screen()`
        function, rather than the older way of using `size(display_width,
        display_height)`.

        The maximum width and height is limited by your operating system, and is usually
        the width and height of your actual screen. On some machines it may simply be
        the number of pixels on your current screen, meaning that a screen of 800 x 600
        could support `size(1600, 300)`, since that is the same number of pixels. This
        varies widely, so you'll have to try different rendering modes and sizes until
        you get what you're looking for. If you need something larger, use
        `create_graphics` to create a non-visible drawing surface.

        The minimum width and height is around 100 pixels in each direction. This is the
        smallest that is supported across Windows, macOS, and Linux. We enforce the
        minimum size so that Sketches will run identically on different machines.

        The `renderer` parameter selects which rendering engine to use. For example, if
        you will be drawing 3D shapes, use `P3D`. In addition to the default renderer,
        other renderers are:

        * `P2D` (Processing 2D): 2D graphics renderer that makes use of OpenGL-
        compatible graphics hardware.
        * `P3D` (Processing 3D): 3D graphics renderer that makes use of OpenGL-
        compatible graphics hardware.
        * `FX2D` (JavaFX 2D): A 2D renderer that uses JavaFX, which may be faster for
        some applications, but has some compatibility quirks.
        * `PDF`: The `PDF` renderer draws 2D graphics directly to an Acrobat PDF file.
        This produces excellent results when you need vector shapes for high-resolution
        output or printing.
        * `SVG`: The `SVG` renderer draws 2D graphics directly to an SVG file. This is
        great for importing into other vector programs or using for digital fabrication.

        When using the `PDF` and `SVG` renderers with the `size()` method, you must use
        the `path` parameter to specify the file to write the output to. No window will
        open while the Sketch is running. You must also call `exit_sketch()` to exit the
        Sketch and write the completed output to the file. Without this call, the Sketch
        will not exit and the output file will be empty. If you would like to draw 3D
        objects to a PDF or SVG file, use the `P3D` renderer and the strategy described
        in `begin_raw()`.
        """
        return self._instance.size(*args)

    @overload
    def smooth(self) -> None:
        """Draws all geometry with smooth (anti-aliased) edges.

        Underlying Processing method: PApplet.smooth

        Methods
        -------

        You can use any of the following signatures:

         * smooth() -> None
         * smooth(level: int, /) -> None

        Parameters
        ----------

        level: int
            either 2, 3, 4, or 8 depending on the renderer

        Notes
        -----

        Draws all geometry with smooth (anti-aliased) edges. This behavior is the
        default, so `smooth()` only needs to be used when a program needs to set the
        smoothing in a different way. The `level` parameter increases the amount of
        smoothness. This is the level of over sampling applied to the graphics buffer.

        With the `P2D` and `P3D` renderers, `smooth(2)` is the default, this is called
        "2x anti-aliasing." The code `smooth(4)` is used for 4x anti-aliasing and
        `smooth(8)` is specified for "8x anti-aliasing." The maximum anti-aliasing level
        is determined by the hardware of the machine that is running the software, so
        `smooth(4)` and `smooth(8)` will not work with every computer.

        The default renderer uses `smooth(3)` by default. This is bicubic smoothing. The
        other option for the default renderer is `smooth(2)`, which is bilinear
        smoothing.

        The `smooth()` function can only be set once within a Sketch. It is intended to
        be called from the `settings()` function. The `no_smooth()` function follows the
        same rules.

        When programming in module mode and imported mode, py5 will allow calls to
        `smooth()` from the `setup()` function if it is called at the beginning of
        `setup()`. This allows the user to omit the `settings()` function, much like
        what can be done while programming in the Processing IDE. Py5 does this by
        inspecting the `setup()` function and attempting to split it into synthetic
        `settings()` and `setup()` functions if both were not created by the user and
        the real `setup()` function contains a call to `smooth()`, or calls to `size()`,
        `full_screen()`, `no_smooth()`, or `pixel_density()`. Calls to those functions
        must be at the very beginning of `setup()`, before any other Python code (but
        comments are ok). This feature is not available when programming in class mode.
        """
        pass

    @overload
    def smooth(self, level: int, /) -> None:
        """Draws all geometry with smooth (anti-aliased) edges.

        Underlying Processing method: PApplet.smooth

        Methods
        -------

        You can use any of the following signatures:

         * smooth() -> None
         * smooth(level: int, /) -> None

        Parameters
        ----------

        level: int
            either 2, 3, 4, or 8 depending on the renderer

        Notes
        -----

        Draws all geometry with smooth (anti-aliased) edges. This behavior is the
        default, so `smooth()` only needs to be used when a program needs to set the
        smoothing in a different way. The `level` parameter increases the amount of
        smoothness. This is the level of over sampling applied to the graphics buffer.

        With the `P2D` and `P3D` renderers, `smooth(2)` is the default, this is called
        "2x anti-aliasing." The code `smooth(4)` is used for 4x anti-aliasing and
        `smooth(8)` is specified for "8x anti-aliasing." The maximum anti-aliasing level
        is determined by the hardware of the machine that is running the software, so
        `smooth(4)` and `smooth(8)` will not work with every computer.

        The default renderer uses `smooth(3)` by default. This is bicubic smoothing. The
        other option for the default renderer is `smooth(2)`, which is bilinear
        smoothing.

        The `smooth()` function can only be set once within a Sketch. It is intended to
        be called from the `settings()` function. The `no_smooth()` function follows the
        same rules.

        When programming in module mode and imported mode, py5 will allow calls to
        `smooth()` from the `setup()` function if it is called at the beginning of
        `setup()`. This allows the user to omit the `settings()` function, much like
        what can be done while programming in the Processing IDE. Py5 does this by
        inspecting the `setup()` function and attempting to split it into synthetic
        `settings()` and `setup()` functions if both were not created by the user and
        the real `setup()` function contains a call to `smooth()`, or calls to `size()`,
        `full_screen()`, `no_smooth()`, or `pixel_density()`. Calls to those functions
        must be at the very beginning of `setup()`, before any other Python code (but
        comments are ok). This feature is not available when programming in class mode.
        """
        pass

    @_settings_only("smooth")
    def smooth(self, *args):
        """Draws all geometry with smooth (anti-aliased) edges.

        Underlying Processing method: PApplet.smooth

        Methods
        -------

        You can use any of the following signatures:

         * smooth() -> None
         * smooth(level: int, /) -> None

        Parameters
        ----------

        level: int
            either 2, 3, 4, or 8 depending on the renderer

        Notes
        -----

        Draws all geometry with smooth (anti-aliased) edges. This behavior is the
        default, so `smooth()` only needs to be used when a program needs to set the
        smoothing in a different way. The `level` parameter increases the amount of
        smoothness. This is the level of over sampling applied to the graphics buffer.

        With the `P2D` and `P3D` renderers, `smooth(2)` is the default, this is called
        "2x anti-aliasing." The code `smooth(4)` is used for 4x anti-aliasing and
        `smooth(8)` is specified for "8x anti-aliasing." The maximum anti-aliasing level
        is determined by the hardware of the machine that is running the software, so
        `smooth(4)` and `smooth(8)` will not work with every computer.

        The default renderer uses `smooth(3)` by default. This is bicubic smoothing. The
        other option for the default renderer is `smooth(2)`, which is bilinear
        smoothing.

        The `smooth()` function can only be set once within a Sketch. It is intended to
        be called from the `settings()` function. The `no_smooth()` function follows the
        same rules.

        When programming in module mode and imported mode, py5 will allow calls to
        `smooth()` from the `setup()` function if it is called at the beginning of
        `setup()`. This allows the user to omit the `settings()` function, much like
        what can be done while programming in the Processing IDE. Py5 does this by
        inspecting the `setup()` function and attempting to split it into synthetic
        `settings()` and `setup()` functions if both were not created by the user and
        the real `setup()` function contains a call to `smooth()`, or calls to `size()`,
        `full_screen()`, `no_smooth()`, or `pixel_density()`. Calls to those functions
        must be at the very beginning of `setup()`, before any other Python code (but
        comments are ok). This feature is not available when programming in class mode.
        """
        return self._instance.smooth(*args)

    @overload
    def specular(self, gray: float, /) -> None:
        """Sets the specular color of the materials used for shapes drawn to the screen,
        which sets the color of highlights.

        Underlying Processing method: PApplet.specular

        Methods
        -------

        You can use any of the following signatures:

         * specular(gray: float, /) -> None
         * specular(rgb: int, /) -> None
         * specular(v1: float, v2: float, v3: float, /) -> None

        Parameters
        ----------

        gray: float
            value between black and white, by default 0 to 255

        rgb: int
            color to set

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the specular color of the materials used for shapes drawn to the screen,
        which sets the color of highlights. Specular refers to light which bounces off a
        surface in a preferred direction (rather than bouncing in all directions like a
        diffuse light). Use in combination with `emissive()`, `ambient()`, and
        `shininess()` to set the material properties of shapes.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def specular(self, v1: float, v2: float, v3: float, /) -> None:
        """Sets the specular color of the materials used for shapes drawn to the screen,
        which sets the color of highlights.

        Underlying Processing method: PApplet.specular

        Methods
        -------

        You can use any of the following signatures:

         * specular(gray: float, /) -> None
         * specular(rgb: int, /) -> None
         * specular(v1: float, v2: float, v3: float, /) -> None

        Parameters
        ----------

        gray: float
            value between black and white, by default 0 to 255

        rgb: int
            color to set

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the specular color of the materials used for shapes drawn to the screen,
        which sets the color of highlights. Specular refers to light which bounces off a
        surface in a preferred direction (rather than bouncing in all directions like a
        diffuse light). Use in combination with `emissive()`, `ambient()`, and
        `shininess()` to set the material properties of shapes.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @overload
    def specular(self, rgb: int, /) -> None:
        """Sets the specular color of the materials used for shapes drawn to the screen,
        which sets the color of highlights.

        Underlying Processing method: PApplet.specular

        Methods
        -------

        You can use any of the following signatures:

         * specular(gray: float, /) -> None
         * specular(rgb: int, /) -> None
         * specular(v1: float, v2: float, v3: float, /) -> None

        Parameters
        ----------

        gray: float
            value between black and white, by default 0 to 255

        rgb: int
            color to set

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the specular color of the materials used for shapes drawn to the screen,
        which sets the color of highlights. Specular refers to light which bounces off a
        surface in a preferred direction (rather than bouncing in all directions like a
        diffuse light). Use in combination with `emissive()`, `ambient()`, and
        `shininess()` to set the material properties of shapes.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        pass

    @_convert_hex_color()
    def specular(self, *args):
        """Sets the specular color of the materials used for shapes drawn to the screen,
        which sets the color of highlights.

        Underlying Processing method: PApplet.specular

        Methods
        -------

        You can use any of the following signatures:

         * specular(gray: float, /) -> None
         * specular(rgb: int, /) -> None
         * specular(v1: float, v2: float, v3: float, /) -> None

        Parameters
        ----------

        gray: float
            value between black and white, by default 0 to 255

        rgb: int
            color to set

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the specular color of the materials used for shapes drawn to the screen,
        which sets the color of highlights. Specular refers to light which bounces off a
        surface in a preferred direction (rather than bouncing in all directions like a
        diffuse light). Use in combination with `emissive()`, `ambient()`, and
        `shininess()` to set the material properties of shapes.

        This method has additional color functionality that is not reflected in the
        method's signatures. For example, you can pass the name of a color (e.g.
        "green", "mediumpurple", etc). Look at the online "All About Colors" Python
        Ecosystem Integration tutorial for more information.
        """
        return self._instance.specular(*args)

    def sphere(self, r: float, /) -> None:
        """A sphere is a hollow ball made from tessellated triangles.

        Underlying Processing method: PApplet.sphere

        Parameters
        ----------

        r: float
            the radius of the sphere

        Notes
        -----

        A sphere is a hollow ball made from tessellated triangles.
        """
        return self._instance.sphere(r)

    @overload
    def sphere_detail(self, res: int, /) -> None:
        """Controls the detail used to render a sphere by adjusting the number of vertices
        of the sphere mesh.

        Underlying Processing method: PApplet.sphereDetail

        Methods
        -------

        You can use any of the following signatures:

         * sphere_detail(res: int, /) -> None
         * sphere_detail(ures: int, vres: int, /) -> None

        Parameters
        ----------

        res: int
            number of segments (minimum 3) used per full circle revolution

        ures: int
            number of segments used longitudinally per full circle revolutoin

        vres: int
            number of segments used latitudinally from top to bottom

        Notes
        -----

        Controls the detail used to render a sphere by adjusting the number of vertices
        of the sphere mesh. The default resolution is 30, which creates a fairly
        detailed sphere definition with vertices every `360/30 = 12` degrees. If you're
        going to render a great number of spheres per frame, it is advised to reduce the
        level of detail using this function. The setting stays active until
        `sphere_detail()` is called again with a new parameter and so should *not* be
        called prior to every `sphere()` statement, unless you wish to render spheres
        with different settings, e.g. using less detail for smaller spheres or ones
        further away from the camera. To control the detail of the horizontal and
        vertical resolution independently, use the version of the functions with two
        parameters.
        """
        pass

    @overload
    def sphere_detail(self, ures: int, vres: int, /) -> None:
        """Controls the detail used to render a sphere by adjusting the number of vertices
        of the sphere mesh.

        Underlying Processing method: PApplet.sphereDetail

        Methods
        -------

        You can use any of the following signatures:

         * sphere_detail(res: int, /) -> None
         * sphere_detail(ures: int, vres: int, /) -> None

        Parameters
        ----------

        res: int
            number of segments (minimum 3) used per full circle revolution

        ures: int
            number of segments used longitudinally per full circle revolutoin

        vres: int
            number of segments used latitudinally from top to bottom

        Notes
        -----

        Controls the detail used to render a sphere by adjusting the number of vertices
        of the sphere mesh. The default resolution is 30, which creates a fairly
        detailed sphere definition with vertices every `360/30 = 12` degrees. If you're
        going to render a great number of spheres per frame, it is advised to reduce the
        level of detail using this function. The setting stays active until
        `sphere_detail()` is called again with a new parameter and so should *not* be
        called prior to every `sphere()` statement, unless you wish to render spheres
        with different settings, e.g. using less detail for smaller spheres or ones
        further away from the camera. To control the detail of the horizontal and
        vertical resolution independently, use the version of the functions with two
        parameters.
        """
        pass

    def sphere_detail(self, *args):
        """Controls the detail used to render a sphere by adjusting the number of vertices
        of the sphere mesh.

        Underlying Processing method: PApplet.sphereDetail

        Methods
        -------

        You can use any of the following signatures:

         * sphere_detail(res: int, /) -> None
         * sphere_detail(ures: int, vres: int, /) -> None

        Parameters
        ----------

        res: int
            number of segments (minimum 3) used per full circle revolution

        ures: int
            number of segments used longitudinally per full circle revolutoin

        vres: int
            number of segments used latitudinally from top to bottom

        Notes
        -----

        Controls the detail used to render a sphere by adjusting the number of vertices
        of the sphere mesh. The default resolution is 30, which creates a fairly
        detailed sphere definition with vertices every `360/30 = 12` degrees. If you're
        going to render a great number of spheres per frame, it is advised to reduce the
        level of detail using this function. The setting stays active until
        `sphere_detail()` is called again with a new parameter and so should *not* be
        called prior to every `sphere()` statement, unless you wish to render spheres
        with different settings, e.g. using less detail for smaller spheres or ones
        further away from the camera. To control the detail of the horizontal and
        vertical resolution independently, use the version of the functions with two
        parameters.
        """
        return self._instance.sphereDetail(*args)

    def spot_light(
        self,
        v1: float,
        v2: float,
        v3: float,
        x: float,
        y: float,
        z: float,
        nx: float,
        ny: float,
        nz: float,
        angle: float,
        concentration: float,
        /,
    ) -> None:
        """Adds a spot light.

        Underlying Processing method: PApplet.spotLight

        Parameters
        ----------

        angle: float
            angle of the spotlight cone

        concentration: float
            exponent determining the center bias of the cone

        nx: float
            direction along the x axis

        ny: float
            direction along the y axis

        nz: float
            direction along the z axis

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        x: float
            x-coordinate of the light

        y: float
            y-coordinate of the light

        z: float
            z-coordinate of the light

        Notes
        -----

        Adds a spot light. Lights need to be included in the `draw()` to remain
        persistent in a looping program. Placing them in the `setup()` of a looping
        program will cause them to only have an effect the first time through the loop.
        The `v1`, `v2`, and `v3` parameters are interpreted as either RGB or HSB values,
        depending on the current color mode. The `x`, `y`, and `z` parameters specify
        the position of the light and `nx`, `ny`, `nz` specify the direction of light.
        The `angle` parameter affects angle of the spotlight cone, while `concentration`
        sets the bias of light focusing toward the center of that cone.
        """
        return self._instance.spotLight(
            v1, v2, v3, x, y, z, nx, ny, nz, angle, concentration
        )

    def square(self, x: float, y: float, extent: float, /) -> None:
        """Draws a square to the screen.

        Underlying Processing method: PApplet.square

        Parameters
        ----------

        extent: float
            width and height of the rectangle by default

        x: float
            x-coordinate of the rectangle by default

        y: float
            y-coordinate of the rectangle by default

        Notes
        -----

        Draws a square to the screen. A square is a four-sided shape with every angle at
        ninety degrees and each side is the same length. By default, the first two
        parameters set the location of the upper-left corner, the third sets the width
        and height. The way these parameters are interpreted, however, may be changed
        with the `rect_mode()` function.
        """
        return self._instance.square(x, y, extent)

    @overload
    def stroke(self, gray: float, /) -> None:
        """Sets the color used to draw lines and borders around shapes.

        Underlying Processing method: PApplet.stroke

        Methods
        -------

        You can use any of the following signatures:

         * stroke(gray: float, /) -> None
         * stroke(gray: float, alpha: float, /) -> None
         * stroke(rgb: int, /) -> None
         * stroke(rgb: int, alpha: float, /) -> None
         * stroke(v1: float, v2: float, v3: float, /) -> None
         * stroke(v1: float, v2: float, v3: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the stroke

        gray: float
            specifies a value between white and black

        rgb: int
            color value in hexadecimal notation

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the color used to draw lines and borders around shapes. This color is
        either specified in terms of the RGB or HSB color depending on the current
        `color_mode()`. The default color space is RGB, with each value in the range
        from 0 to 255.

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
        """Sets the color used to draw lines and borders around shapes.

        Underlying Processing method: PApplet.stroke

        Methods
        -------

        You can use any of the following signatures:

         * stroke(gray: float, /) -> None
         * stroke(gray: float, alpha: float, /) -> None
         * stroke(rgb: int, /) -> None
         * stroke(rgb: int, alpha: float, /) -> None
         * stroke(v1: float, v2: float, v3: float, /) -> None
         * stroke(v1: float, v2: float, v3: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the stroke

        gray: float
            specifies a value between white and black

        rgb: int
            color value in hexadecimal notation

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the color used to draw lines and borders around shapes. This color is
        either specified in terms of the RGB or HSB color depending on the current
        `color_mode()`. The default color space is RGB, with each value in the range
        from 0 to 255.

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
    def stroke(self, v1: float, v2: float, v3: float, /) -> None:
        """Sets the color used to draw lines and borders around shapes.

        Underlying Processing method: PApplet.stroke

        Methods
        -------

        You can use any of the following signatures:

         * stroke(gray: float, /) -> None
         * stroke(gray: float, alpha: float, /) -> None
         * stroke(rgb: int, /) -> None
         * stroke(rgb: int, alpha: float, /) -> None
         * stroke(v1: float, v2: float, v3: float, /) -> None
         * stroke(v1: float, v2: float, v3: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the stroke

        gray: float
            specifies a value between white and black

        rgb: int
            color value in hexadecimal notation

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the color used to draw lines and borders around shapes. This color is
        either specified in terms of the RGB or HSB color depending on the current
        `color_mode()`. The default color space is RGB, with each value in the range
        from 0 to 255.

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
    def stroke(self, v1: float, v2: float, v3: float, alpha: float, /) -> None:
        """Sets the color used to draw lines and borders around shapes.

        Underlying Processing method: PApplet.stroke

        Methods
        -------

        You can use any of the following signatures:

         * stroke(gray: float, /) -> None
         * stroke(gray: float, alpha: float, /) -> None
         * stroke(rgb: int, /) -> None
         * stroke(rgb: int, alpha: float, /) -> None
         * stroke(v1: float, v2: float, v3: float, /) -> None
         * stroke(v1: float, v2: float, v3: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the stroke

        gray: float
            specifies a value between white and black

        rgb: int
            color value in hexadecimal notation

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the color used to draw lines and borders around shapes. This color is
        either specified in terms of the RGB or HSB color depending on the current
        `color_mode()`. The default color space is RGB, with each value in the range
        from 0 to 255.

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
        """Sets the color used to draw lines and borders around shapes.

        Underlying Processing method: PApplet.stroke

        Methods
        -------

        You can use any of the following signatures:

         * stroke(gray: float, /) -> None
         * stroke(gray: float, alpha: float, /) -> None
         * stroke(rgb: int, /) -> None
         * stroke(rgb: int, alpha: float, /) -> None
         * stroke(v1: float, v2: float, v3: float, /) -> None
         * stroke(v1: float, v2: float, v3: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the stroke

        gray: float
            specifies a value between white and black

        rgb: int
            color value in hexadecimal notation

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the color used to draw lines and borders around shapes. This color is
        either specified in terms of the RGB or HSB color depending on the current
        `color_mode()`. The default color space is RGB, with each value in the range
        from 0 to 255.

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
        """Sets the color used to draw lines and borders around shapes.

        Underlying Processing method: PApplet.stroke

        Methods
        -------

        You can use any of the following signatures:

         * stroke(gray: float, /) -> None
         * stroke(gray: float, alpha: float, /) -> None
         * stroke(rgb: int, /) -> None
         * stroke(rgb: int, alpha: float, /) -> None
         * stroke(v1: float, v2: float, v3: float, /) -> None
         * stroke(v1: float, v2: float, v3: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the stroke

        gray: float
            specifies a value between white and black

        rgb: int
            color value in hexadecimal notation

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the color used to draw lines and borders around shapes. This color is
        either specified in terms of the RGB or HSB color depending on the current
        `color_mode()`. The default color space is RGB, with each value in the range
        from 0 to 255.

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
        """Sets the color used to draw lines and borders around shapes.

        Underlying Processing method: PApplet.stroke

        Methods
        -------

        You can use any of the following signatures:

         * stroke(gray: float, /) -> None
         * stroke(gray: float, alpha: float, /) -> None
         * stroke(rgb: int, /) -> None
         * stroke(rgb: int, alpha: float, /) -> None
         * stroke(v1: float, v2: float, v3: float, /) -> None
         * stroke(v1: float, v2: float, v3: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the stroke

        gray: float
            specifies a value between white and black

        rgb: int
            color value in hexadecimal notation

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the color used to draw lines and borders around shapes. This color is
        either specified in terms of the RGB or HSB color depending on the current
        `color_mode()`. The default color space is RGB, with each value in the range
        from 0 to 255.

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
        """Sets the style for rendering line endings.

        Underlying Processing method: PApplet.strokeCap

        Parameters
        ----------

        cap: int
            either SQUARE, PROJECT, or ROUND

        Notes
        -----

        Sets the style for rendering line endings. These ends are either squared,
        extended, or rounded, each of which specified with the corresponding parameters:
        `SQUARE`, `PROJECT`, and `ROUND`. The default cap is `ROUND`.

        To make `point()` appear square, use `stroke_cap(PROJECT)`. Using
        `stroke_cap(SQUARE)` (no cap) causes points to become invisible.
        """
        return self._instance.strokeCap(cap)

    def stroke_join(self, join: int, /) -> None:
        """Sets the style of the joints which connect line segments.

        Underlying Processing method: PApplet.strokeJoin

        Parameters
        ----------

        join: int
            either MITER, BEVEL, ROUND

        Notes
        -----

        Sets the style of the joints which connect line segments. These joints are
        either mitered, beveled, or rounded and specified with the corresponding
        parameters `MITER`, `BEVEL`, and `ROUND`. The default joint is `MITER`.
        """
        return self._instance.strokeJoin(join)

    def stroke_weight(self, weight: float, /) -> None:
        """Sets the width of the stroke used for lines, points, and the border around
        shapes.

        Underlying Processing method: PApplet.strokeWeight

        Parameters
        ----------

        weight: float
            the weight (in pixels) of the stroke

        Notes
        -----

        Sets the width of the stroke used for lines, points, and the border around
        shapes. All widths are set in units of pixels.

        Using `point()` with `strokeWeight(1)` or smaller may draw nothing to the
        screen, depending on the graphics settings of the computer. Workarounds include
        setting the pixel using the `pixels[]` or `np_pixels[]` arrays or drawing the
        point using either `circle()` or `square()`.
        """
        return self._instance.strokeWeight(weight)

    @overload
    def text(self, c: chr, x: float, y: float, /) -> None:
        """Draws text to the screen.

        Underlying Processing method: PApplet.text

        Methods
        -------

        You can use any of the following signatures:

         * text(c: chr, x: float, y: float, /) -> None
         * text(c: chr, x: float, y: float, z: float, /) -> None
         * text(chars: Sequence[chr], start: int, stop: int, x: float, y: float, /) -> None
         * text(chars: Sequence[chr], start: int, stop: int, x: float, y: float, z: float, /) -> None
         * text(num: float, x: float, y: float, /) -> None
         * text(num: float, x: float, y: float, z: float, /) -> None
         * text(num: int, x: float, y: float, /) -> None
         * text(num: int, x: float, y: float, z: float, /) -> None
         * text(str: str, x1: float, y1: float, x2: float, y2: float, /) -> None
         * text(str: str, x: float, y: float, /) -> None
         * text(str: str, x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        c: chr
            the alphanumeric character to be displayed

        chars: Sequence[chr]
            the alphanumberic symbols to be displayed

        num: float
            the numeric value to be displayed

        num: int
            the numeric value to be displayed

        start: int
            array index at which to start writing characters

        stop: int
            array index at which to stop writing characters

        str: str
            string to be displayed

        x1: float
            by default, the x-coordinate of text, see rectMode() for more info

        x2: float
            by default, the width of the text box, see rectMode() for more info

        x: float
            x-coordinate of text

        y1: float
            by default, the y-coordinate of text, see rectMode() for more info

        y2: float
            by default, the height of the text box, see rectMode() for more info

        y: float
            y-coordinate of text

        z: float
            z-coordinate of text

        Notes
        -----

        Draws text to the screen. Displays the information specified in the first
        parameter on the screen in the position specified by the additional parameters.
        A default font will be used unless a font is set with the `text_font()` function
        and a default size will be used unless a font is set with `text_size()`. Change
        the color of the text with the `fill()` function. The text displays in relation
        to the `text_align()` function, which gives the option to draw to the left,
        right, and center of the coordinates.

        The `x2` and `y2` parameters define a rectangular area to display within and may
        only be used with string data. When these parameters are specified, they are
        interpreted based on the current `rect_mode()` setting. Text that does not fit
        completely within the rectangle specified will not be drawn to the screen.

        Note that py5 lets you call `text()` without first specifying a Py5Font with
        `text_font()`. In that case, a generic sans-serif font will be used instead.
        (See the third example.)
        """
        pass

    @overload
    def text(self, c: chr, x: float, y: float, z: float, /) -> None:
        """Draws text to the screen.

        Underlying Processing method: PApplet.text

        Methods
        -------

        You can use any of the following signatures:

         * text(c: chr, x: float, y: float, /) -> None
         * text(c: chr, x: float, y: float, z: float, /) -> None
         * text(chars: Sequence[chr], start: int, stop: int, x: float, y: float, /) -> None
         * text(chars: Sequence[chr], start: int, stop: int, x: float, y: float, z: float, /) -> None
         * text(num: float, x: float, y: float, /) -> None
         * text(num: float, x: float, y: float, z: float, /) -> None
         * text(num: int, x: float, y: float, /) -> None
         * text(num: int, x: float, y: float, z: float, /) -> None
         * text(str: str, x1: float, y1: float, x2: float, y2: float, /) -> None
         * text(str: str, x: float, y: float, /) -> None
         * text(str: str, x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        c: chr
            the alphanumeric character to be displayed

        chars: Sequence[chr]
            the alphanumberic symbols to be displayed

        num: float
            the numeric value to be displayed

        num: int
            the numeric value to be displayed

        start: int
            array index at which to start writing characters

        stop: int
            array index at which to stop writing characters

        str: str
            string to be displayed

        x1: float
            by default, the x-coordinate of text, see rectMode() for more info

        x2: float
            by default, the width of the text box, see rectMode() for more info

        x: float
            x-coordinate of text

        y1: float
            by default, the y-coordinate of text, see rectMode() for more info

        y2: float
            by default, the height of the text box, see rectMode() for more info

        y: float
            y-coordinate of text

        z: float
            z-coordinate of text

        Notes
        -----

        Draws text to the screen. Displays the information specified in the first
        parameter on the screen in the position specified by the additional parameters.
        A default font will be used unless a font is set with the `text_font()` function
        and a default size will be used unless a font is set with `text_size()`. Change
        the color of the text with the `fill()` function. The text displays in relation
        to the `text_align()` function, which gives the option to draw to the left,
        right, and center of the coordinates.

        The `x2` and `y2` parameters define a rectangular area to display within and may
        only be used with string data. When these parameters are specified, they are
        interpreted based on the current `rect_mode()` setting. Text that does not fit
        completely within the rectangle specified will not be drawn to the screen.

        Note that py5 lets you call `text()` without first specifying a Py5Font with
        `text_font()`. In that case, a generic sans-serif font will be used instead.
        (See the third example.)
        """
        pass

    @overload
    def text(
        self, chars: Sequence[chr], start: int, stop: int, x: float, y: float, /
    ) -> None:
        """Draws text to the screen.

        Underlying Processing method: PApplet.text

        Methods
        -------

        You can use any of the following signatures:

         * text(c: chr, x: float, y: float, /) -> None
         * text(c: chr, x: float, y: float, z: float, /) -> None
         * text(chars: Sequence[chr], start: int, stop: int, x: float, y: float, /) -> None
         * text(chars: Sequence[chr], start: int, stop: int, x: float, y: float, z: float, /) -> None
         * text(num: float, x: float, y: float, /) -> None
         * text(num: float, x: float, y: float, z: float, /) -> None
         * text(num: int, x: float, y: float, /) -> None
         * text(num: int, x: float, y: float, z: float, /) -> None
         * text(str: str, x1: float, y1: float, x2: float, y2: float, /) -> None
         * text(str: str, x: float, y: float, /) -> None
         * text(str: str, x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        c: chr
            the alphanumeric character to be displayed

        chars: Sequence[chr]
            the alphanumberic symbols to be displayed

        num: float
            the numeric value to be displayed

        num: int
            the numeric value to be displayed

        start: int
            array index at which to start writing characters

        stop: int
            array index at which to stop writing characters

        str: str
            string to be displayed

        x1: float
            by default, the x-coordinate of text, see rectMode() for more info

        x2: float
            by default, the width of the text box, see rectMode() for more info

        x: float
            x-coordinate of text

        y1: float
            by default, the y-coordinate of text, see rectMode() for more info

        y2: float
            by default, the height of the text box, see rectMode() for more info

        y: float
            y-coordinate of text

        z: float
            z-coordinate of text

        Notes
        -----

        Draws text to the screen. Displays the information specified in the first
        parameter on the screen in the position specified by the additional parameters.
        A default font will be used unless a font is set with the `text_font()` function
        and a default size will be used unless a font is set with `text_size()`. Change
        the color of the text with the `fill()` function. The text displays in relation
        to the `text_align()` function, which gives the option to draw to the left,
        right, and center of the coordinates.

        The `x2` and `y2` parameters define a rectangular area to display within and may
        only be used with string data. When these parameters are specified, they are
        interpreted based on the current `rect_mode()` setting. Text that does not fit
        completely within the rectangle specified will not be drawn to the screen.

        Note that py5 lets you call `text()` without first specifying a Py5Font with
        `text_font()`. In that case, a generic sans-serif font will be used instead.
        (See the third example.)
        """
        pass

    @overload
    def text(
        self,
        chars: Sequence[chr],
        start: int,
        stop: int,
        x: float,
        y: float,
        z: float,
        /,
    ) -> None:
        """Draws text to the screen.

        Underlying Processing method: PApplet.text

        Methods
        -------

        You can use any of the following signatures:

         * text(c: chr, x: float, y: float, /) -> None
         * text(c: chr, x: float, y: float, z: float, /) -> None
         * text(chars: Sequence[chr], start: int, stop: int, x: float, y: float, /) -> None
         * text(chars: Sequence[chr], start: int, stop: int, x: float, y: float, z: float, /) -> None
         * text(num: float, x: float, y: float, /) -> None
         * text(num: float, x: float, y: float, z: float, /) -> None
         * text(num: int, x: float, y: float, /) -> None
         * text(num: int, x: float, y: float, z: float, /) -> None
         * text(str: str, x1: float, y1: float, x2: float, y2: float, /) -> None
         * text(str: str, x: float, y: float, /) -> None
         * text(str: str, x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        c: chr
            the alphanumeric character to be displayed

        chars: Sequence[chr]
            the alphanumberic symbols to be displayed

        num: float
            the numeric value to be displayed

        num: int
            the numeric value to be displayed

        start: int
            array index at which to start writing characters

        stop: int
            array index at which to stop writing characters

        str: str
            string to be displayed

        x1: float
            by default, the x-coordinate of text, see rectMode() for more info

        x2: float
            by default, the width of the text box, see rectMode() for more info

        x: float
            x-coordinate of text

        y1: float
            by default, the y-coordinate of text, see rectMode() for more info

        y2: float
            by default, the height of the text box, see rectMode() for more info

        y: float
            y-coordinate of text

        z: float
            z-coordinate of text

        Notes
        -----

        Draws text to the screen. Displays the information specified in the first
        parameter on the screen in the position specified by the additional parameters.
        A default font will be used unless a font is set with the `text_font()` function
        and a default size will be used unless a font is set with `text_size()`. Change
        the color of the text with the `fill()` function. The text displays in relation
        to the `text_align()` function, which gives the option to draw to the left,
        right, and center of the coordinates.

        The `x2` and `y2` parameters define a rectangular area to display within and may
        only be used with string data. When these parameters are specified, they are
        interpreted based on the current `rect_mode()` setting. Text that does not fit
        completely within the rectangle specified will not be drawn to the screen.

        Note that py5 lets you call `text()` without first specifying a Py5Font with
        `text_font()`. In that case, a generic sans-serif font will be used instead.
        (See the third example.)
        """
        pass

    @overload
    def text(self, num: float, x: float, y: float, /) -> None:
        """Draws text to the screen.

        Underlying Processing method: PApplet.text

        Methods
        -------

        You can use any of the following signatures:

         * text(c: chr, x: float, y: float, /) -> None
         * text(c: chr, x: float, y: float, z: float, /) -> None
         * text(chars: Sequence[chr], start: int, stop: int, x: float, y: float, /) -> None
         * text(chars: Sequence[chr], start: int, stop: int, x: float, y: float, z: float, /) -> None
         * text(num: float, x: float, y: float, /) -> None
         * text(num: float, x: float, y: float, z: float, /) -> None
         * text(num: int, x: float, y: float, /) -> None
         * text(num: int, x: float, y: float, z: float, /) -> None
         * text(str: str, x1: float, y1: float, x2: float, y2: float, /) -> None
         * text(str: str, x: float, y: float, /) -> None
         * text(str: str, x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        c: chr
            the alphanumeric character to be displayed

        chars: Sequence[chr]
            the alphanumberic symbols to be displayed

        num: float
            the numeric value to be displayed

        num: int
            the numeric value to be displayed

        start: int
            array index at which to start writing characters

        stop: int
            array index at which to stop writing characters

        str: str
            string to be displayed

        x1: float
            by default, the x-coordinate of text, see rectMode() for more info

        x2: float
            by default, the width of the text box, see rectMode() for more info

        x: float
            x-coordinate of text

        y1: float
            by default, the y-coordinate of text, see rectMode() for more info

        y2: float
            by default, the height of the text box, see rectMode() for more info

        y: float
            y-coordinate of text

        z: float
            z-coordinate of text

        Notes
        -----

        Draws text to the screen. Displays the information specified in the first
        parameter on the screen in the position specified by the additional parameters.
        A default font will be used unless a font is set with the `text_font()` function
        and a default size will be used unless a font is set with `text_size()`. Change
        the color of the text with the `fill()` function. The text displays in relation
        to the `text_align()` function, which gives the option to draw to the left,
        right, and center of the coordinates.

        The `x2` and `y2` parameters define a rectangular area to display within and may
        only be used with string data. When these parameters are specified, they are
        interpreted based on the current `rect_mode()` setting. Text that does not fit
        completely within the rectangle specified will not be drawn to the screen.

        Note that py5 lets you call `text()` without first specifying a Py5Font with
        `text_font()`. In that case, a generic sans-serif font will be used instead.
        (See the third example.)
        """
        pass

    @overload
    def text(self, num: float, x: float, y: float, z: float, /) -> None:
        """Draws text to the screen.

        Underlying Processing method: PApplet.text

        Methods
        -------

        You can use any of the following signatures:

         * text(c: chr, x: float, y: float, /) -> None
         * text(c: chr, x: float, y: float, z: float, /) -> None
         * text(chars: Sequence[chr], start: int, stop: int, x: float, y: float, /) -> None
         * text(chars: Sequence[chr], start: int, stop: int, x: float, y: float, z: float, /) -> None
         * text(num: float, x: float, y: float, /) -> None
         * text(num: float, x: float, y: float, z: float, /) -> None
         * text(num: int, x: float, y: float, /) -> None
         * text(num: int, x: float, y: float, z: float, /) -> None
         * text(str: str, x1: float, y1: float, x2: float, y2: float, /) -> None
         * text(str: str, x: float, y: float, /) -> None
         * text(str: str, x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        c: chr
            the alphanumeric character to be displayed

        chars: Sequence[chr]
            the alphanumberic symbols to be displayed

        num: float
            the numeric value to be displayed

        num: int
            the numeric value to be displayed

        start: int
            array index at which to start writing characters

        stop: int
            array index at which to stop writing characters

        str: str
            string to be displayed

        x1: float
            by default, the x-coordinate of text, see rectMode() for more info

        x2: float
            by default, the width of the text box, see rectMode() for more info

        x: float
            x-coordinate of text

        y1: float
            by default, the y-coordinate of text, see rectMode() for more info

        y2: float
            by default, the height of the text box, see rectMode() for more info

        y: float
            y-coordinate of text

        z: float
            z-coordinate of text

        Notes
        -----

        Draws text to the screen. Displays the information specified in the first
        parameter on the screen in the position specified by the additional parameters.
        A default font will be used unless a font is set with the `text_font()` function
        and a default size will be used unless a font is set with `text_size()`. Change
        the color of the text with the `fill()` function. The text displays in relation
        to the `text_align()` function, which gives the option to draw to the left,
        right, and center of the coordinates.

        The `x2` and `y2` parameters define a rectangular area to display within and may
        only be used with string data. When these parameters are specified, they are
        interpreted based on the current `rect_mode()` setting. Text that does not fit
        completely within the rectangle specified will not be drawn to the screen.

        Note that py5 lets you call `text()` without first specifying a Py5Font with
        `text_font()`. In that case, a generic sans-serif font will be used instead.
        (See the third example.)
        """
        pass

    @overload
    def text(self, num: int, x: float, y: float, /) -> None:
        """Draws text to the screen.

        Underlying Processing method: PApplet.text

        Methods
        -------

        You can use any of the following signatures:

         * text(c: chr, x: float, y: float, /) -> None
         * text(c: chr, x: float, y: float, z: float, /) -> None
         * text(chars: Sequence[chr], start: int, stop: int, x: float, y: float, /) -> None
         * text(chars: Sequence[chr], start: int, stop: int, x: float, y: float, z: float, /) -> None
         * text(num: float, x: float, y: float, /) -> None
         * text(num: float, x: float, y: float, z: float, /) -> None
         * text(num: int, x: float, y: float, /) -> None
         * text(num: int, x: float, y: float, z: float, /) -> None
         * text(str: str, x1: float, y1: float, x2: float, y2: float, /) -> None
         * text(str: str, x: float, y: float, /) -> None
         * text(str: str, x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        c: chr
            the alphanumeric character to be displayed

        chars: Sequence[chr]
            the alphanumberic symbols to be displayed

        num: float
            the numeric value to be displayed

        num: int
            the numeric value to be displayed

        start: int
            array index at which to start writing characters

        stop: int
            array index at which to stop writing characters

        str: str
            string to be displayed

        x1: float
            by default, the x-coordinate of text, see rectMode() for more info

        x2: float
            by default, the width of the text box, see rectMode() for more info

        x: float
            x-coordinate of text

        y1: float
            by default, the y-coordinate of text, see rectMode() for more info

        y2: float
            by default, the height of the text box, see rectMode() for more info

        y: float
            y-coordinate of text

        z: float
            z-coordinate of text

        Notes
        -----

        Draws text to the screen. Displays the information specified in the first
        parameter on the screen in the position specified by the additional parameters.
        A default font will be used unless a font is set with the `text_font()` function
        and a default size will be used unless a font is set with `text_size()`. Change
        the color of the text with the `fill()` function. The text displays in relation
        to the `text_align()` function, which gives the option to draw to the left,
        right, and center of the coordinates.

        The `x2` and `y2` parameters define a rectangular area to display within and may
        only be used with string data. When these parameters are specified, they are
        interpreted based on the current `rect_mode()` setting. Text that does not fit
        completely within the rectangle specified will not be drawn to the screen.

        Note that py5 lets you call `text()` without first specifying a Py5Font with
        `text_font()`. In that case, a generic sans-serif font will be used instead.
        (See the third example.)
        """
        pass

    @overload
    def text(self, num: int, x: float, y: float, z: float, /) -> None:
        """Draws text to the screen.

        Underlying Processing method: PApplet.text

        Methods
        -------

        You can use any of the following signatures:

         * text(c: chr, x: float, y: float, /) -> None
         * text(c: chr, x: float, y: float, z: float, /) -> None
         * text(chars: Sequence[chr], start: int, stop: int, x: float, y: float, /) -> None
         * text(chars: Sequence[chr], start: int, stop: int, x: float, y: float, z: float, /) -> None
         * text(num: float, x: float, y: float, /) -> None
         * text(num: float, x: float, y: float, z: float, /) -> None
         * text(num: int, x: float, y: float, /) -> None
         * text(num: int, x: float, y: float, z: float, /) -> None
         * text(str: str, x1: float, y1: float, x2: float, y2: float, /) -> None
         * text(str: str, x: float, y: float, /) -> None
         * text(str: str, x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        c: chr
            the alphanumeric character to be displayed

        chars: Sequence[chr]
            the alphanumberic symbols to be displayed

        num: float
            the numeric value to be displayed

        num: int
            the numeric value to be displayed

        start: int
            array index at which to start writing characters

        stop: int
            array index at which to stop writing characters

        str: str
            string to be displayed

        x1: float
            by default, the x-coordinate of text, see rectMode() for more info

        x2: float
            by default, the width of the text box, see rectMode() for more info

        x: float
            x-coordinate of text

        y1: float
            by default, the y-coordinate of text, see rectMode() for more info

        y2: float
            by default, the height of the text box, see rectMode() for more info

        y: float
            y-coordinate of text

        z: float
            z-coordinate of text

        Notes
        -----

        Draws text to the screen. Displays the information specified in the first
        parameter on the screen in the position specified by the additional parameters.
        A default font will be used unless a font is set with the `text_font()` function
        and a default size will be used unless a font is set with `text_size()`. Change
        the color of the text with the `fill()` function. The text displays in relation
        to the `text_align()` function, which gives the option to draw to the left,
        right, and center of the coordinates.

        The `x2` and `y2` parameters define a rectangular area to display within and may
        only be used with string data. When these parameters are specified, they are
        interpreted based on the current `rect_mode()` setting. Text that does not fit
        completely within the rectangle specified will not be drawn to the screen.

        Note that py5 lets you call `text()` without first specifying a Py5Font with
        `text_font()`. In that case, a generic sans-serif font will be used instead.
        (See the third example.)
        """
        pass

    @overload
    def text(self, str: str, x: float, y: float, /) -> None:
        """Draws text to the screen.

        Underlying Processing method: PApplet.text

        Methods
        -------

        You can use any of the following signatures:

         * text(c: chr, x: float, y: float, /) -> None
         * text(c: chr, x: float, y: float, z: float, /) -> None
         * text(chars: Sequence[chr], start: int, stop: int, x: float, y: float, /) -> None
         * text(chars: Sequence[chr], start: int, stop: int, x: float, y: float, z: float, /) -> None
         * text(num: float, x: float, y: float, /) -> None
         * text(num: float, x: float, y: float, z: float, /) -> None
         * text(num: int, x: float, y: float, /) -> None
         * text(num: int, x: float, y: float, z: float, /) -> None
         * text(str: str, x1: float, y1: float, x2: float, y2: float, /) -> None
         * text(str: str, x: float, y: float, /) -> None
         * text(str: str, x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        c: chr
            the alphanumeric character to be displayed

        chars: Sequence[chr]
            the alphanumberic symbols to be displayed

        num: float
            the numeric value to be displayed

        num: int
            the numeric value to be displayed

        start: int
            array index at which to start writing characters

        stop: int
            array index at which to stop writing characters

        str: str
            string to be displayed

        x1: float
            by default, the x-coordinate of text, see rectMode() for more info

        x2: float
            by default, the width of the text box, see rectMode() for more info

        x: float
            x-coordinate of text

        y1: float
            by default, the y-coordinate of text, see rectMode() for more info

        y2: float
            by default, the height of the text box, see rectMode() for more info

        y: float
            y-coordinate of text

        z: float
            z-coordinate of text

        Notes
        -----

        Draws text to the screen. Displays the information specified in the first
        parameter on the screen in the position specified by the additional parameters.
        A default font will be used unless a font is set with the `text_font()` function
        and a default size will be used unless a font is set with `text_size()`. Change
        the color of the text with the `fill()` function. The text displays in relation
        to the `text_align()` function, which gives the option to draw to the left,
        right, and center of the coordinates.

        The `x2` and `y2` parameters define a rectangular area to display within and may
        only be used with string data. When these parameters are specified, they are
        interpreted based on the current `rect_mode()` setting. Text that does not fit
        completely within the rectangle specified will not be drawn to the screen.

        Note that py5 lets you call `text()` without first specifying a Py5Font with
        `text_font()`. In that case, a generic sans-serif font will be used instead.
        (See the third example.)
        """
        pass

    @overload
    def text(self, str: str, x: float, y: float, z: float, /) -> None:
        """Draws text to the screen.

        Underlying Processing method: PApplet.text

        Methods
        -------

        You can use any of the following signatures:

         * text(c: chr, x: float, y: float, /) -> None
         * text(c: chr, x: float, y: float, z: float, /) -> None
         * text(chars: Sequence[chr], start: int, stop: int, x: float, y: float, /) -> None
         * text(chars: Sequence[chr], start: int, stop: int, x: float, y: float, z: float, /) -> None
         * text(num: float, x: float, y: float, /) -> None
         * text(num: float, x: float, y: float, z: float, /) -> None
         * text(num: int, x: float, y: float, /) -> None
         * text(num: int, x: float, y: float, z: float, /) -> None
         * text(str: str, x1: float, y1: float, x2: float, y2: float, /) -> None
         * text(str: str, x: float, y: float, /) -> None
         * text(str: str, x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        c: chr
            the alphanumeric character to be displayed

        chars: Sequence[chr]
            the alphanumberic symbols to be displayed

        num: float
            the numeric value to be displayed

        num: int
            the numeric value to be displayed

        start: int
            array index at which to start writing characters

        stop: int
            array index at which to stop writing characters

        str: str
            string to be displayed

        x1: float
            by default, the x-coordinate of text, see rectMode() for more info

        x2: float
            by default, the width of the text box, see rectMode() for more info

        x: float
            x-coordinate of text

        y1: float
            by default, the y-coordinate of text, see rectMode() for more info

        y2: float
            by default, the height of the text box, see rectMode() for more info

        y: float
            y-coordinate of text

        z: float
            z-coordinate of text

        Notes
        -----

        Draws text to the screen. Displays the information specified in the first
        parameter on the screen in the position specified by the additional parameters.
        A default font will be used unless a font is set with the `text_font()` function
        and a default size will be used unless a font is set with `text_size()`. Change
        the color of the text with the `fill()` function. The text displays in relation
        to the `text_align()` function, which gives the option to draw to the left,
        right, and center of the coordinates.

        The `x2` and `y2` parameters define a rectangular area to display within and may
        only be used with string data. When these parameters are specified, they are
        interpreted based on the current `rect_mode()` setting. Text that does not fit
        completely within the rectangle specified will not be drawn to the screen.

        Note that py5 lets you call `text()` without first specifying a Py5Font with
        `text_font()`. In that case, a generic sans-serif font will be used instead.
        (See the third example.)
        """
        pass

    @overload
    def text(self, str: str, x1: float, y1: float, x2: float, y2: float, /) -> None:
        """Draws text to the screen.

        Underlying Processing method: PApplet.text

        Methods
        -------

        You can use any of the following signatures:

         * text(c: chr, x: float, y: float, /) -> None
         * text(c: chr, x: float, y: float, z: float, /) -> None
         * text(chars: Sequence[chr], start: int, stop: int, x: float, y: float, /) -> None
         * text(chars: Sequence[chr], start: int, stop: int, x: float, y: float, z: float, /) -> None
         * text(num: float, x: float, y: float, /) -> None
         * text(num: float, x: float, y: float, z: float, /) -> None
         * text(num: int, x: float, y: float, /) -> None
         * text(num: int, x: float, y: float, z: float, /) -> None
         * text(str: str, x1: float, y1: float, x2: float, y2: float, /) -> None
         * text(str: str, x: float, y: float, /) -> None
         * text(str: str, x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        c: chr
            the alphanumeric character to be displayed

        chars: Sequence[chr]
            the alphanumberic symbols to be displayed

        num: float
            the numeric value to be displayed

        num: int
            the numeric value to be displayed

        start: int
            array index at which to start writing characters

        stop: int
            array index at which to stop writing characters

        str: str
            string to be displayed

        x1: float
            by default, the x-coordinate of text, see rectMode() for more info

        x2: float
            by default, the width of the text box, see rectMode() for more info

        x: float
            x-coordinate of text

        y1: float
            by default, the y-coordinate of text, see rectMode() for more info

        y2: float
            by default, the height of the text box, see rectMode() for more info

        y: float
            y-coordinate of text

        z: float
            z-coordinate of text

        Notes
        -----

        Draws text to the screen. Displays the information specified in the first
        parameter on the screen in the position specified by the additional parameters.
        A default font will be used unless a font is set with the `text_font()` function
        and a default size will be used unless a font is set with `text_size()`. Change
        the color of the text with the `fill()` function. The text displays in relation
        to the `text_align()` function, which gives the option to draw to the left,
        right, and center of the coordinates.

        The `x2` and `y2` parameters define a rectangular area to display within and may
        only be used with string data. When these parameters are specified, they are
        interpreted based on the current `rect_mode()` setting. Text that does not fit
        completely within the rectangle specified will not be drawn to the screen.

        Note that py5 lets you call `text()` without first specifying a Py5Font with
        `text_font()`. In that case, a generic sans-serif font will be used instead.
        (See the third example.)
        """
        pass

    @_text_fix_str
    def text(self, *args):
        """Draws text to the screen.

        Underlying Processing method: PApplet.text

        Methods
        -------

        You can use any of the following signatures:

         * text(c: chr, x: float, y: float, /) -> None
         * text(c: chr, x: float, y: float, z: float, /) -> None
         * text(chars: Sequence[chr], start: int, stop: int, x: float, y: float, /) -> None
         * text(chars: Sequence[chr], start: int, stop: int, x: float, y: float, z: float, /) -> None
         * text(num: float, x: float, y: float, /) -> None
         * text(num: float, x: float, y: float, z: float, /) -> None
         * text(num: int, x: float, y: float, /) -> None
         * text(num: int, x: float, y: float, z: float, /) -> None
         * text(str: str, x1: float, y1: float, x2: float, y2: float, /) -> None
         * text(str: str, x: float, y: float, /) -> None
         * text(str: str, x: float, y: float, z: float, /) -> None

        Parameters
        ----------

        c: chr
            the alphanumeric character to be displayed

        chars: Sequence[chr]
            the alphanumberic symbols to be displayed

        num: float
            the numeric value to be displayed

        num: int
            the numeric value to be displayed

        start: int
            array index at which to start writing characters

        stop: int
            array index at which to stop writing characters

        str: str
            string to be displayed

        x1: float
            by default, the x-coordinate of text, see rectMode() for more info

        x2: float
            by default, the width of the text box, see rectMode() for more info

        x: float
            x-coordinate of text

        y1: float
            by default, the y-coordinate of text, see rectMode() for more info

        y2: float
            by default, the height of the text box, see rectMode() for more info

        y: float
            y-coordinate of text

        z: float
            z-coordinate of text

        Notes
        -----

        Draws text to the screen. Displays the information specified in the first
        parameter on the screen in the position specified by the additional parameters.
        A default font will be used unless a font is set with the `text_font()` function
        and a default size will be used unless a font is set with `text_size()`. Change
        the color of the text with the `fill()` function. The text displays in relation
        to the `text_align()` function, which gives the option to draw to the left,
        right, and center of the coordinates.

        The `x2` and `y2` parameters define a rectangular area to display within and may
        only be used with string data. When these parameters are specified, they are
        interpreted based on the current `rect_mode()` setting. Text that does not fit
        completely within the rectangle specified will not be drawn to the screen.

        Note that py5 lets you call `text()` without first specifying a Py5Font with
        `text_font()`. In that case, a generic sans-serif font will be used instead.
        (See the third example.)
        """
        return self._instance.text(*args)

    @overload
    def text_align(self, align_x: int, /) -> None:
        """Sets the current alignment for drawing text.

        Underlying Processing method: PApplet.textAlign

        Methods
        -------

        You can use any of the following signatures:

         * text_align(align_x: int, /) -> None
         * text_align(align_x: int, align_y: int, /) -> None

        Parameters
        ----------

        align_x: int
            horizontal alignment, either LEFT, CENTER, or RIGHT

        align_y: int
            vertical alignment, either TOP, BOTTOM, CENTER, or BASELINE

        Notes
        -----

        Sets the current alignment for drawing text. The parameters `LEFT`, `CENTER`,
        and `RIGHT` set the display characteristics of the letters in relation to the
        values for the `x` and `y` parameters of the `text()` function.

        An optional second parameter can be used to vertically align the text.
        `BASELINE` is the default, and the vertical alignment will be reset to
        `BASELINE` if the second parameter is not used. The `TOP` and `CENTER`
        parameters are straightforward. The `BOTTOM` parameter offsets the line based on
        the current `text_descent()`. For multiple lines, the final line will be aligned
        to the bottom, with the previous lines appearing above it.

        When using `text()` with width and height parameters, `BASELINE` is ignored, and
        treated as `TOP`. (Otherwise, text would by default draw outside the box, since
        `BASELINE` is the default setting. `BASELINE` is not a useful drawing mode for
        text drawn in a rectangle.)

        The vertical alignment is based on the value of `text_ascent()`, which many
        fonts do not specify correctly. It may be necessary to use a hack and offset by
        a few pixels by hand so that the offset looks correct. To do this as less of a
        hack, use some percentage of `text_ascent()` or `text_descent()` so that the
        hack works even if you change the size of the font.
        """
        pass

    @overload
    def text_align(self, align_x: int, align_y: int, /) -> None:
        """Sets the current alignment for drawing text.

        Underlying Processing method: PApplet.textAlign

        Methods
        -------

        You can use any of the following signatures:

         * text_align(align_x: int, /) -> None
         * text_align(align_x: int, align_y: int, /) -> None

        Parameters
        ----------

        align_x: int
            horizontal alignment, either LEFT, CENTER, or RIGHT

        align_y: int
            vertical alignment, either TOP, BOTTOM, CENTER, or BASELINE

        Notes
        -----

        Sets the current alignment for drawing text. The parameters `LEFT`, `CENTER`,
        and `RIGHT` set the display characteristics of the letters in relation to the
        values for the `x` and `y` parameters of the `text()` function.

        An optional second parameter can be used to vertically align the text.
        `BASELINE` is the default, and the vertical alignment will be reset to
        `BASELINE` if the second parameter is not used. The `TOP` and `CENTER`
        parameters are straightforward. The `BOTTOM` parameter offsets the line based on
        the current `text_descent()`. For multiple lines, the final line will be aligned
        to the bottom, with the previous lines appearing above it.

        When using `text()` with width and height parameters, `BASELINE` is ignored, and
        treated as `TOP`. (Otherwise, text would by default draw outside the box, since
        `BASELINE` is the default setting. `BASELINE` is not a useful drawing mode for
        text drawn in a rectangle.)

        The vertical alignment is based on the value of `text_ascent()`, which many
        fonts do not specify correctly. It may be necessary to use a hack and offset by
        a few pixels by hand so that the offset looks correct. To do this as less of a
        hack, use some percentage of `text_ascent()` or `text_descent()` so that the
        hack works even if you change the size of the font.
        """
        pass

    def text_align(self, *args):
        """Sets the current alignment for drawing text.

        Underlying Processing method: PApplet.textAlign

        Methods
        -------

        You can use any of the following signatures:

         * text_align(align_x: int, /) -> None
         * text_align(align_x: int, align_y: int, /) -> None

        Parameters
        ----------

        align_x: int
            horizontal alignment, either LEFT, CENTER, or RIGHT

        align_y: int
            vertical alignment, either TOP, BOTTOM, CENTER, or BASELINE

        Notes
        -----

        Sets the current alignment for drawing text. The parameters `LEFT`, `CENTER`,
        and `RIGHT` set the display characteristics of the letters in relation to the
        values for the `x` and `y` parameters of the `text()` function.

        An optional second parameter can be used to vertically align the text.
        `BASELINE` is the default, and the vertical alignment will be reset to
        `BASELINE` if the second parameter is not used. The `TOP` and `CENTER`
        parameters are straightforward. The `BOTTOM` parameter offsets the line based on
        the current `text_descent()`. For multiple lines, the final line will be aligned
        to the bottom, with the previous lines appearing above it.

        When using `text()` with width and height parameters, `BASELINE` is ignored, and
        treated as `TOP`. (Otherwise, text would by default draw outside the box, since
        `BASELINE` is the default setting. `BASELINE` is not a useful drawing mode for
        text drawn in a rectangle.)

        The vertical alignment is based on the value of `text_ascent()`, which many
        fonts do not specify correctly. It may be necessary to use a hack and offset by
        a few pixels by hand so that the offset looks correct. To do this as less of a
        hack, use some percentage of `text_ascent()` or `text_descent()` so that the
        hack works even if you change the size of the font.
        """
        return self._instance.textAlign(*args)

    def text_ascent(self) -> float:
        """Returns ascent of the current font at its current size.

        Underlying Processing method: PApplet.textAscent

        Notes
        -----

        Returns ascent of the current font at its current size. This information is
        useful for determining the height of the font above the baseline.
        """
        return self._instance.textAscent()

    def text_descent(self) -> float:
        """Returns descent of the current font at its current size.

        Underlying Processing method: PApplet.textDescent

        Notes
        -----

        Returns descent of the current font at its current size. This information is
        useful for determining the height of the font below the baseline.
        """
        return self._instance.textDescent()

    @overload
    def text_font(self, which: Py5Font, /) -> None:
        """Sets the current font that will be drawn with the `text()` function.

        Underlying Processing method: PApplet.textFont

        Methods
        -------

        You can use any of the following signatures:

         * text_font(which: Py5Font, /) -> None
         * text_font(which: Py5Font, size: float, /) -> None

        Parameters
        ----------

        size: float
            the size of the letters in units of pixels

        which: Py5Font
            any variable of the type Py5Font

        Notes
        -----

        Sets the current font that will be drawn with the `text()` function. Fonts must
        be created for py5 with `create_font()` or loaded with `load_font()` before they
        can be used. The font set through `text_font()` will be used in all subsequent
        calls to the `text()` function. If no `size` parameter is specified, the font
        size defaults to the original size (the size in which it was created with
        `create_font_file()`) overriding any previous calls to `text_font()` or
        `text_size()`.

        When fonts are rendered as an image texture (as is the case with the `P2D` and
        `P3D` renderers as well as with `load_font()` and vlw files), you should create
        fonts at the sizes that will be used most commonly. Using `text_font()` without
        the size parameter will result in the cleanest type.
        """
        pass

    @overload
    def text_font(self, which: Py5Font, size: float, /) -> None:
        """Sets the current font that will be drawn with the `text()` function.

        Underlying Processing method: PApplet.textFont

        Methods
        -------

        You can use any of the following signatures:

         * text_font(which: Py5Font, /) -> None
         * text_font(which: Py5Font, size: float, /) -> None

        Parameters
        ----------

        size: float
            the size of the letters in units of pixels

        which: Py5Font
            any variable of the type Py5Font

        Notes
        -----

        Sets the current font that will be drawn with the `text()` function. Fonts must
        be created for py5 with `create_font()` or loaded with `load_font()` before they
        can be used. The font set through `text_font()` will be used in all subsequent
        calls to the `text()` function. If no `size` parameter is specified, the font
        size defaults to the original size (the size in which it was created with
        `create_font_file()`) overriding any previous calls to `text_font()` or
        `text_size()`.

        When fonts are rendered as an image texture (as is the case with the `P2D` and
        `P3D` renderers as well as with `load_font()` and vlw files), you should create
        fonts at the sizes that will be used most commonly. Using `text_font()` without
        the size parameter will result in the cleanest type.
        """
        pass

    def text_font(self, *args):
        """Sets the current font that will be drawn with the `text()` function.

        Underlying Processing method: PApplet.textFont

        Methods
        -------

        You can use any of the following signatures:

         * text_font(which: Py5Font, /) -> None
         * text_font(which: Py5Font, size: float, /) -> None

        Parameters
        ----------

        size: float
            the size of the letters in units of pixels

        which: Py5Font
            any variable of the type Py5Font

        Notes
        -----

        Sets the current font that will be drawn with the `text()` function. Fonts must
        be created for py5 with `create_font()` or loaded with `load_font()` before they
        can be used. The font set through `text_font()` will be used in all subsequent
        calls to the `text()` function. If no `size` parameter is specified, the font
        size defaults to the original size (the size in which it was created with
        `create_font_file()`) overriding any previous calls to `text_font()` or
        `text_size()`.

        When fonts are rendered as an image texture (as is the case with the `P2D` and
        `P3D` renderers as well as with `load_font()` and vlw files), you should create
        fonts at the sizes that will be used most commonly. Using `text_font()` without
        the size parameter will result in the cleanest type.
        """
        return self._instance.textFont(*args)

    def text_leading(self, leading: float, /) -> None:
        """Sets the spacing between lines of text in units of pixels.

        Underlying Processing method: PApplet.textLeading

        Parameters
        ----------

        leading: float
            the size in pixels for spacing between lines

        Notes
        -----

        Sets the spacing between lines of text in units of pixels. This setting will be
        used in all subsequent calls to the `text()` function.  Note, however, that the
        leading is reset by `text_size()`. For example, if the leading is set to 20 with
        `text_leading(20)`, then if `text_size(48)` is run at a later point, the leading
        will be reset to the default for the text size of 48.
        """
        return self._instance.textLeading(leading)

    def text_mode(self, mode: int, /) -> None:
        """Sets the way text draws to the screen, either as texture maps or as vector
        geometry.

        Underlying Processing method: PApplet.textMode

        Parameters
        ----------

        mode: int
            either MODEL or SHAPE

        Notes
        -----

        Sets the way text draws to the screen, either as texture maps or as vector
        geometry. The default `text_mode(MODEL)`, uses textures to render the fonts. The
        `text_mode(SHAPE)` mode draws text using the glyph outlines of individual
        characters rather than as textures. This mode is only supported with the `PDF`
        and `P3D` renderer settings. With the `PDF` renderer, you must call
        `text_mode(SHAPE)` before any other drawing occurs. If the outlines are not
        available, then `text_mode(SHAPE)` will be ignored and `text_mode(MODEL)` will
        be used instead.

        The `text_mode(SHAPE)` option in `P3D` can be combined with `begin_raw()` to
        write vector-accurate text to 2D and 3D output files, for instance `DXF` or
        `PDF`. The `SHAPE` mode is not currently optimized for `P3D`, so if recording
        shape data, use `text_mode(MODEL)` until you're ready to capture the geometry
        with `begin_raw()`.
        """
        return self._instance.textMode(mode)

    def text_size(self, size: float, /) -> None:
        """Sets the current font size.

        Underlying Processing method: PApplet.textSize

        Parameters
        ----------

        size: float
            the size of the letters in units of pixels

        Notes
        -----

        Sets the current font size. This size will be used in all subsequent calls to
        the `text()` function. Font size is measured in units of pixels.
        """
        return self._instance.textSize(size)

    @overload
    def text_width(self, c: chr, /) -> float:
        """Calculates and returns the width of any character or text string.

        Underlying Processing method: PApplet.textWidth

        Methods
        -------

        You can use any of the following signatures:

         * text_width(c: chr, /) -> float
         * text_width(chars: Sequence[chr], start: int, length: int, /) -> float
         * text_width(str: str, /) -> float

        Parameters
        ----------

        c: chr
            the character to measure

        chars: Sequence[chr]
            the characters to measure

        length: int
            number of characters to measure

        start: int
            first character to measure

        str: str
            the String of characters to measure

        Notes
        -----

        Calculates and returns the width of any character or text string.
        """
        pass

    @overload
    def text_width(self, chars: Sequence[chr], start: int, length: int, /) -> float:
        """Calculates and returns the width of any character or text string.

        Underlying Processing method: PApplet.textWidth

        Methods
        -------

        You can use any of the following signatures:

         * text_width(c: chr, /) -> float
         * text_width(chars: Sequence[chr], start: int, length: int, /) -> float
         * text_width(str: str, /) -> float

        Parameters
        ----------

        c: chr
            the character to measure

        chars: Sequence[chr]
            the characters to measure

        length: int
            number of characters to measure

        start: int
            first character to measure

        str: str
            the String of characters to measure

        Notes
        -----

        Calculates and returns the width of any character or text string.
        """
        pass

    @overload
    def text_width(self, str: str, /) -> float:
        """Calculates and returns the width of any character or text string.

        Underlying Processing method: PApplet.textWidth

        Methods
        -------

        You can use any of the following signatures:

         * text_width(c: chr, /) -> float
         * text_width(chars: Sequence[chr], start: int, length: int, /) -> float
         * text_width(str: str, /) -> float

        Parameters
        ----------

        c: chr
            the character to measure

        chars: Sequence[chr]
            the characters to measure

        length: int
            number of characters to measure

        start: int
            first character to measure

        str: str
            the String of characters to measure

        Notes
        -----

        Calculates and returns the width of any character or text string.
        """
        pass

    @_text_fix_str
    def text_width(self, *args):
        """Calculates and returns the width of any character or text string.

        Underlying Processing method: PApplet.textWidth

        Methods
        -------

        You can use any of the following signatures:

         * text_width(c: chr, /) -> float
         * text_width(chars: Sequence[chr], start: int, length: int, /) -> float
         * text_width(str: str, /) -> float

        Parameters
        ----------

        c: chr
            the character to measure

        chars: Sequence[chr]
            the characters to measure

        length: int
            number of characters to measure

        start: int
            first character to measure

        str: str
            the String of characters to measure

        Notes
        -----

        Calculates and returns the width of any character or text string.
        """
        return self._instance.textWidth(*args)

    @_auto_convert_to_py5image(0)
    def texture(self, image: Py5Image, /) -> None:
        """Sets a texture to be applied to vertex points.

        Underlying Processing method: PApplet.texture

        Parameters
        ----------

        image: Py5Image
            reference to a Py5Image object

        Notes
        -----

        Sets a texture to be applied to vertex points. The `texture()` method must be
        called between `begin_shape()` and `end_shape()` and before any calls to
        `vertex()`. This method only works with the `P2D` and `P3D` renderers.

        When textures are in use, the fill color is ignored. Instead, use `tint()` to
        specify the color of the texture as it is applied to the shape.
        """
        return self._instance.texture(image)

    def texture_mode(self, mode: int, /) -> None:
        """Sets the coordinate space for texture mapping.

        Underlying Processing method: PApplet.textureMode

        Parameters
        ----------

        mode: int
            either IMAGE or NORMAL

        Notes
        -----

        Sets the coordinate space for texture mapping. The default mode is `IMAGE`,
        which refers to the actual pixel coordinates of the image. `NORMAL` refers to a
        normalized space of values ranging from 0 to 1. This function only works with
        the `P2D` and `P3D` renderers.

        With `IMAGE`, if an image is 100 x 200 pixels, mapping the image onto the entire
        size of a quad would require the points (0,0) (100,0) (100,200) (0,200). The
        same mapping in `NORMAL` is (0,0) (1,0) (1,1) (0,1).
        """
        return self._instance.textureMode(mode)

    def texture_wrap(self, wrap: int, /) -> None:
        """Defines if textures repeat or draw once within a texture map.

        Underlying Processing method: PApplet.textureWrap

        Parameters
        ----------

        wrap: int
            Either CLAMP (default) or REPEAT

        Notes
        -----

        Defines if textures repeat or draw once within a texture map. The two parameters
        are `CLAMP` (the default behavior) and `REPEAT`. This function only works with
        the `P2D` and `P3D` renderers.
        """
        return self._instance.textureWrap(wrap)

    @overload
    def tint(self, gray: float, /) -> None:
        """Sets the fill value for displaying images.

        Underlying Processing method: PApplet.tint

        Methods
        -------

        You can use any of the following signatures:

         * tint(gray: float, /) -> None
         * tint(gray: float, alpha: float, /) -> None
         * tint(rgb: int, /) -> None
         * tint(rgb: int, alpha: float, /) -> None
         * tint(v1: float, v2: float, v3: float, /) -> None
         * tint(v1: float, v2: float, v3: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the image

        gray: float
            specifies a value between white and black

        rgb: int
            color value in hexadecimal notation

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the fill value for displaying images. Images can be tinted to specified
        colors or made transparent by including an alpha value.

        To apply transparency to an image without affecting its color, use white as the
        tint color and specify an alpha value. For instance, `tint(255, 128)` will make
        an image 50% transparent (assuming the default alpha range of 0-255, which can
        be changed with `color_mode()`).

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
        """Sets the fill value for displaying images.

        Underlying Processing method: PApplet.tint

        Methods
        -------

        You can use any of the following signatures:

         * tint(gray: float, /) -> None
         * tint(gray: float, alpha: float, /) -> None
         * tint(rgb: int, /) -> None
         * tint(rgb: int, alpha: float, /) -> None
         * tint(v1: float, v2: float, v3: float, /) -> None
         * tint(v1: float, v2: float, v3: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the image

        gray: float
            specifies a value between white and black

        rgb: int
            color value in hexadecimal notation

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the fill value for displaying images. Images can be tinted to specified
        colors or made transparent by including an alpha value.

        To apply transparency to an image without affecting its color, use white as the
        tint color and specify an alpha value. For instance, `tint(255, 128)` will make
        an image 50% transparent (assuming the default alpha range of 0-255, which can
        be changed with `color_mode()`).

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
    def tint(self, v1: float, v2: float, v3: float, /) -> None:
        """Sets the fill value for displaying images.

        Underlying Processing method: PApplet.tint

        Methods
        -------

        You can use any of the following signatures:

         * tint(gray: float, /) -> None
         * tint(gray: float, alpha: float, /) -> None
         * tint(rgb: int, /) -> None
         * tint(rgb: int, alpha: float, /) -> None
         * tint(v1: float, v2: float, v3: float, /) -> None
         * tint(v1: float, v2: float, v3: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the image

        gray: float
            specifies a value between white and black

        rgb: int
            color value in hexadecimal notation

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the fill value for displaying images. Images can be tinted to specified
        colors or made transparent by including an alpha value.

        To apply transparency to an image without affecting its color, use white as the
        tint color and specify an alpha value. For instance, `tint(255, 128)` will make
        an image 50% transparent (assuming the default alpha range of 0-255, which can
        be changed with `color_mode()`).

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
    def tint(self, v1: float, v2: float, v3: float, alpha: float, /) -> None:
        """Sets the fill value for displaying images.

        Underlying Processing method: PApplet.tint

        Methods
        -------

        You can use any of the following signatures:

         * tint(gray: float, /) -> None
         * tint(gray: float, alpha: float, /) -> None
         * tint(rgb: int, /) -> None
         * tint(rgb: int, alpha: float, /) -> None
         * tint(v1: float, v2: float, v3: float, /) -> None
         * tint(v1: float, v2: float, v3: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the image

        gray: float
            specifies a value between white and black

        rgb: int
            color value in hexadecimal notation

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the fill value for displaying images. Images can be tinted to specified
        colors or made transparent by including an alpha value.

        To apply transparency to an image without affecting its color, use white as the
        tint color and specify an alpha value. For instance, `tint(255, 128)` will make
        an image 50% transparent (assuming the default alpha range of 0-255, which can
        be changed with `color_mode()`).

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
        """Sets the fill value for displaying images.

        Underlying Processing method: PApplet.tint

        Methods
        -------

        You can use any of the following signatures:

         * tint(gray: float, /) -> None
         * tint(gray: float, alpha: float, /) -> None
         * tint(rgb: int, /) -> None
         * tint(rgb: int, alpha: float, /) -> None
         * tint(v1: float, v2: float, v3: float, /) -> None
         * tint(v1: float, v2: float, v3: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the image

        gray: float
            specifies a value between white and black

        rgb: int
            color value in hexadecimal notation

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the fill value for displaying images. Images can be tinted to specified
        colors or made transparent by including an alpha value.

        To apply transparency to an image without affecting its color, use white as the
        tint color and specify an alpha value. For instance, `tint(255, 128)` will make
        an image 50% transparent (assuming the default alpha range of 0-255, which can
        be changed with `color_mode()`).

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
        """Sets the fill value for displaying images.

        Underlying Processing method: PApplet.tint

        Methods
        -------

        You can use any of the following signatures:

         * tint(gray: float, /) -> None
         * tint(gray: float, alpha: float, /) -> None
         * tint(rgb: int, /) -> None
         * tint(rgb: int, alpha: float, /) -> None
         * tint(v1: float, v2: float, v3: float, /) -> None
         * tint(v1: float, v2: float, v3: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the image

        gray: float
            specifies a value between white and black

        rgb: int
            color value in hexadecimal notation

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the fill value for displaying images. Images can be tinted to specified
        colors or made transparent by including an alpha value.

        To apply transparency to an image without affecting its color, use white as the
        tint color and specify an alpha value. For instance, `tint(255, 128)` will make
        an image 50% transparent (assuming the default alpha range of 0-255, which can
        be changed with `color_mode()`).

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
        """Sets the fill value for displaying images.

        Underlying Processing method: PApplet.tint

        Methods
        -------

        You can use any of the following signatures:

         * tint(gray: float, /) -> None
         * tint(gray: float, alpha: float, /) -> None
         * tint(rgb: int, /) -> None
         * tint(rgb: int, alpha: float, /) -> None
         * tint(v1: float, v2: float, v3: float, /) -> None
         * tint(v1: float, v2: float, v3: float, alpha: float, /) -> None

        Parameters
        ----------

        alpha: float
            opacity of the image

        gray: float
            specifies a value between white and black

        rgb: int
            color value in hexadecimal notation

        v1: float
            red or hue value (depending on current color mode)

        v2: float
            green or saturation value (depending on current color mode)

        v3: float
            blue or brightness value (depending on current color mode)

        Notes
        -----

        Sets the fill value for displaying images. Images can be tinted to specified
        colors or made transparent by including an alpha value.

        To apply transparency to an image without affecting its color, use white as the
        tint color and specify an alpha value. For instance, `tint(255, 128)` will make
        an image 50% transparent (assuming the default alpha range of 0-255, which can
        be changed with `color_mode()`).

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
        """Specifies an amount to displace objects within the display window.

        Underlying Processing method: PApplet.translate

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
            forward/backward translation

        Notes
        -----

        Specifies an amount to displace objects within the display window. The `x`
        parameter specifies left/right translation, the `y` parameter specifies up/down
        translation, and the `z` parameter specifies translations toward/away from the
        screen. Using this function with the `z` parameter requires using `P3D` as a
        parameter in combination with size as shown in the second example.

        Transformations are cumulative and apply to everything that happens after and
        subsequent calls to the function accumulates the effect. For example, calling
        `translate(50, 0)` and then `translate(20, 0)` is the same as `translate(70,
        0)`. If `translate()` is called within `draw()`, the transformation is reset
        when the loop begins again. This function can be further controlled by using
        `push_matrix()` and `pop_matrix()`.
        """
        pass

    @overload
    def translate(self, x: float, y: float, z: float, /) -> None:
        """Specifies an amount to displace objects within the display window.

        Underlying Processing method: PApplet.translate

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
            forward/backward translation

        Notes
        -----

        Specifies an amount to displace objects within the display window. The `x`
        parameter specifies left/right translation, the `y` parameter specifies up/down
        translation, and the `z` parameter specifies translations toward/away from the
        screen. Using this function with the `z` parameter requires using `P3D` as a
        parameter in combination with size as shown in the second example.

        Transformations are cumulative and apply to everything that happens after and
        subsequent calls to the function accumulates the effect. For example, calling
        `translate(50, 0)` and then `translate(20, 0)` is the same as `translate(70,
        0)`. If `translate()` is called within `draw()`, the transformation is reset
        when the loop begins again. This function can be further controlled by using
        `push_matrix()` and `pop_matrix()`.
        """
        pass

    def translate(self, *args):
        """Specifies an amount to displace objects within the display window.

        Underlying Processing method: PApplet.translate

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
            forward/backward translation

        Notes
        -----

        Specifies an amount to displace objects within the display window. The `x`
        parameter specifies left/right translation, the `y` parameter specifies up/down
        translation, and the `z` parameter specifies translations toward/away from the
        screen. Using this function with the `z` parameter requires using `P3D` as a
        parameter in combination with size as shown in the second example.

        Transformations are cumulative and apply to everything that happens after and
        subsequent calls to the function accumulates the effect. For example, calling
        `translate(50, 0)` and then `translate(20, 0)` is the same as `translate(70,
        0)`. If `translate()` is called within `draw()`, the transformation is reset
        when the loop begins again. This function can be further controlled by using
        `push_matrix()` and `pop_matrix()`.
        """
        return self._instance.translate(*args)

    def triangle(
        self, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float, /
    ) -> None:
        """A triangle is a plane created by connecting three points.

        Underlying Processing method: PApplet.triangle

        Parameters
        ----------

        x1: float
            x-coordinate of the first point

        x2: float
            x-coordinate of the second point

        x3: float
            x-coordinate of the third point

        y1: float
            y-coordinate of the first point

        y2: float
            y-coordinate of the second point

        y3: float
            y-coordinate of the third point

        Notes
        -----

        A triangle is a plane created by connecting three points. The first two
        arguments specify the first point, the middle two arguments specify the second
        point, and the last two arguments specify the third point.
        """
        return self._instance.triangle(x1, y1, x2, y2, x3, y3)

    @overload
    def update_pixels(self) -> None:
        """Updates the display window with the data in the `pixels[]` array.

        Underlying Processing method: PApplet.updatePixels

        Methods
        -------

        You can use any of the following signatures:

         * update_pixels() -> None
         * update_pixels(x1: int, y1: int, x2: int, y2: int, /) -> None

        Parameters
        ----------

        x1: int
            x-coordinate of the upper-left corner

        x2: int
            width of the region

        y1: int
            y-coordinate of the upper-left corner

        y2: int
            height of the region

        Notes
        -----

        Updates the display window with the data in the `pixels[]` array. Use in
        conjunction with `load_pixels()`. If you're only reading pixels from the array,
        there's no need to call `update_pixels()` — updating is only necessary to apply
        changes.
        """
        pass

    @overload
    def update_pixels(self, x1: int, y1: int, x2: int, y2: int, /) -> None:
        """Updates the display window with the data in the `pixels[]` array.

        Underlying Processing method: PApplet.updatePixels

        Methods
        -------

        You can use any of the following signatures:

         * update_pixels() -> None
         * update_pixels(x1: int, y1: int, x2: int, y2: int, /) -> None

        Parameters
        ----------

        x1: int
            x-coordinate of the upper-left corner

        x2: int
            width of the region

        y1: int
            y-coordinate of the upper-left corner

        y2: int
            height of the region

        Notes
        -----

        Updates the display window with the data in the `pixels[]` array. Use in
        conjunction with `load_pixels()`. If you're only reading pixels from the array,
        there's no need to call `update_pixels()` — updating is only necessary to apply
        changes.
        """
        pass

    def update_pixels(self, *args):
        """Updates the display window with the data in the `pixels[]` array.

        Underlying Processing method: PApplet.updatePixels

        Methods
        -------

        You can use any of the following signatures:

         * update_pixels() -> None
         * update_pixels(x1: int, y1: int, x2: int, y2: int, /) -> None

        Parameters
        ----------

        x1: int
            x-coordinate of the upper-left corner

        x2: int
            width of the region

        y1: int
            y-coordinate of the upper-left corner

        y2: int
            height of the region

        Notes
        -----

        Updates the display window with the data in the `pixels[]` array. Use in
        conjunction with `load_pixels()`. If you're only reading pixels from the array,
        there's no need to call `update_pixels()` — updating is only necessary to apply
        changes.
        """
        return self._instance.updatePixels(*args)

    @overload
    def vertex(self, x: float, y: float, /) -> None:
        """Add a new vertex to a shape.

        Underlying Processing method: PApplet.vertex

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

        Add a new vertex to a shape. All shapes are constructed by connecting a series
        of vertices. The `vertex()` method is used to specify the vertex coordinates for
        points, lines, triangles, quads, and polygons. It is used exclusively within the
        `begin_shape()` and `end_shape()` functions.

        Drawing a vertex in 3D using the `z` parameter requires the `P3D` renderer, as
        shown in the second example.

        This method is also used to map a texture onto geometry. The `texture()`
        function declares the texture to apply to the geometry and the `u` and `v`
        coordinates define the mapping of this texture to the form. By default, the
        coordinates used for `u` and `v` are specified in relation to the image's size
        in pixels, but this relation can be changed with the Sketch's `texture_mode()`
        method.
        """
        pass

    @overload
    def vertex(self, x: float, y: float, z: float, /) -> None:
        """Add a new vertex to a shape.

        Underlying Processing method: PApplet.vertex

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

        Add a new vertex to a shape. All shapes are constructed by connecting a series
        of vertices. The `vertex()` method is used to specify the vertex coordinates for
        points, lines, triangles, quads, and polygons. It is used exclusively within the
        `begin_shape()` and `end_shape()` functions.

        Drawing a vertex in 3D using the `z` parameter requires the `P3D` renderer, as
        shown in the second example.

        This method is also used to map a texture onto geometry. The `texture()`
        function declares the texture to apply to the geometry and the `u` and `v`
        coordinates define the mapping of this texture to the form. By default, the
        coordinates used for `u` and `v` are specified in relation to the image's size
        in pixels, but this relation can be changed with the Sketch's `texture_mode()`
        method.
        """
        pass

    @overload
    def vertex(self, x: float, y: float, u: float, v: float, /) -> None:
        """Add a new vertex to a shape.

        Underlying Processing method: PApplet.vertex

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

        Add a new vertex to a shape. All shapes are constructed by connecting a series
        of vertices. The `vertex()` method is used to specify the vertex coordinates for
        points, lines, triangles, quads, and polygons. It is used exclusively within the
        `begin_shape()` and `end_shape()` functions.

        Drawing a vertex in 3D using the `z` parameter requires the `P3D` renderer, as
        shown in the second example.

        This method is also used to map a texture onto geometry. The `texture()`
        function declares the texture to apply to the geometry and the `u` and `v`
        coordinates define the mapping of this texture to the form. By default, the
        coordinates used for `u` and `v` are specified in relation to the image's size
        in pixels, but this relation can be changed with the Sketch's `texture_mode()`
        method.
        """
        pass

    @overload
    def vertex(self, x: float, y: float, z: float, u: float, v: float, /) -> None:
        """Add a new vertex to a shape.

        Underlying Processing method: PApplet.vertex

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

        Add a new vertex to a shape. All shapes are constructed by connecting a series
        of vertices. The `vertex()` method is used to specify the vertex coordinates for
        points, lines, triangles, quads, and polygons. It is used exclusively within the
        `begin_shape()` and `end_shape()` functions.

        Drawing a vertex in 3D using the `z` parameter requires the `P3D` renderer, as
        shown in the second example.

        This method is also used to map a texture onto geometry. The `texture()`
        function declares the texture to apply to the geometry and the `u` and `v`
        coordinates define the mapping of this texture to the form. By default, the
        coordinates used for `u` and `v` are specified in relation to the image's size
        in pixels, but this relation can be changed with the Sketch's `texture_mode()`
        method.
        """
        pass

    def vertex(self, *args):
        """Add a new vertex to a shape.

        Underlying Processing method: PApplet.vertex

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

        Add a new vertex to a shape. All shapes are constructed by connecting a series
        of vertices. The `vertex()` method is used to specify the vertex coordinates for
        points, lines, triangles, quads, and polygons. It is used exclusively within the
        `begin_shape()` and `end_shape()` functions.

        Drawing a vertex in 3D using the `z` parameter requires the `P3D` renderer, as
        shown in the second example.

        This method is also used to map a texture onto geometry. The `texture()`
        function declares the texture to apply to the geometry and the `u` and `v`
        coordinates define the mapping of this texture to the form. By default, the
        coordinates used for `u` and `v` are specified in relation to the image's size
        in pixels, but this relation can be changed with the Sketch's `texture_mode()`
        method.
        """
        return self._instance.vertex(*args)

    @_generator_to_list
    def vertices(self, coordinates: Sequence[Sequence[float]], /) -> None:
        """Create a collection of vertices.

        Parameters
        ----------

        coordinates: Sequence[Sequence[float]]
            2D array of vertex coordinates and optional UV texture mapping values

        Notes
        -----

        Create a collection of vertices. The purpose of this method is to provide an
        alternative to repeatedly calling `vertex()` in a loop. For a large number of
        vertices, the performance of `vertices()` will be much faster.

        The `coordinates` parameter should be a numpy array with one row for each
        vertex. There should be two or three columns for 2D or 3D points, respectively.
        There may also be an additional two columns for UV texture mapping values.
        """
        return self._instance.vertices(coordinates)

    def window_move(self, x: int, y: int, /) -> None:
        """Set the Sketch's window location.

        Underlying Processing method: Sketch.windowMove

        Parameters
        ----------

        x: int
            x-coordinate for window location

        y: int
            y-coordinate for window location

        Notes
        -----

        Set the Sketch's window location. Calling this repeatedly from the `draw()`
        function may result in a sluggish Sketch. Negative or invalid coordinates are
        ignored. To hide a Sketch window, use `Py5Surface.set_visible()`.

        This method provides the same functionality as `Py5Surface.set_location()` but
        without the need to interact directly with the `Py5Surface` object.
        """
        return self._instance.windowMove(x, y)

    def window_ratio(self, wide: int, high: int, /) -> None:
        """Set a window ratio to enable scale invariant drawing.

        Underlying Processing method: Sketch.windowRatio

        Parameters
        ----------

        high: int
            height of scale invariant display window

        wide: int
            width of scale invariant display window

        Notes
        -----

        Set a window ratio to enable scale invariant drawing. If the Sketch window is
        resizable, drawing in a consistent way can be challenging as the window changes
        size. This method activates some transformations to let the user draw to the
        window in a way that will be consistent for all window sizes.

        The usefulness of this feature is demonstrated in the example code. The size of
        the text will change as the window changes size. Observe the example makes two
        calls to `text_size()` with fixed values of `200` and `100`. Without this
        feature, calculating the appropriate text size for all window sizes would be
        difficult. Similarly, positioning the text in the same relative location would
        also involve several calculations. Using `window_ratio()` makes resizable
        Sketches that resize well easier to create.

        When using this feature, use `rmouse_x` and `rmouse_y` to get the cursor
        coordinates. The transformations involve calls to `translate()` and `scale()`,
        and the parameters to those methods can be accessed with `ratio_top`,
        `ratio_left`, and `ratio_scale`. The transformed coordinates enabled with this
        feature can be negative for the top and left areas of the window that do not fit
        the desired aspect ratio. Experimenting with the example and seeing how the
        numbers change will provide more understanding than what can be explained with
        words.

        When calling this method, it is better to do so with values like
        `window_ratio(1280, 720)` and not `window_ratio(16, 9)`. The aspect ratio is the
        same for both but the latter might result in floating point accuracy issues.
        """
        return self._instance.windowRatio(wide, high)

    def window_resizable(self, resizable: bool, /) -> None:
        """Set the Sketch window as resizable by the user.

        Underlying Processing method: Sketch.windowResizable

        Parameters
        ----------

        resizable: bool
            should the Sketch window be resizable

        Notes
        -----

        Set the Sketch window as resizable by the user. The user will be able to resize
        the window in the same way as they do for many other windows on their computer.
        By default, the Sketch window is not resizable.

        Changing the window size will clear the drawing canvas. If you do this, the
        `width` and `height` variables will change.

        This method provides the same functionality as `Py5Surface.set_resizable()` but
        without the need to interact directly with the `Py5Surface` object.
        """
        return self._instance.windowResizable(resizable)

    def window_resize(self, new_width: int, new_height: int, /) -> None:
        """Set a new width and height for the Sketch window.

        Underlying Processing method: Sketch.windowResize

        Parameters
        ----------

        new_height: int
            new window height

        new_width: int
            new window width

        Notes
        -----

        Set a new width and height for the Sketch window. You do not need to call
        `window_resizable()` before calling this.

        Changing the window size will clear the drawing canvas. If you do this, the
        `width` and `height` variables will change.

        This method provides the same functionality as `Py5Surface.set_size()` but
        without the need to interact directly with the `Py5Surface` object.
        """
        return self._instance.windowResize(new_width, new_height)

    def window_title(self, title: str, /) -> None:
        """Set the Sketch window's title.

        Underlying Processing method: Sketch.windowTitle

        Parameters
        ----------

        title: str
            new window title

        Notes
        -----

        Set the Sketch window's title. This will typically appear at the window's title
        bar. The default window title is "Sketch".

        This method provides the same functionality as `Py5Surface.set_title()` but
        without the need to interact directly with the `Py5Surface` object.
        """
        return self._instance.windowTitle(title)

    @classmethod
    def year(cls) -> int:
        """Py5 communicates with the clock on your computer.

        Underlying Processing method: PApplet.year

        Notes
        -----

        Py5 communicates with the clock on your computer. The `year()` function returns
        the current year as an integer (2003, 2004, 2005, etc).
        """
        return cls._cls.year()
