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

import sys
import tempfile
import time
from pathlib import Path
from typing import Callable, Iterable

import numpy as np
import numpy.typing as npt
import PIL
from jpype import JClass
from PIL.Image import Image as PIL_Image

from .. import environ as _environ
from .. import imported as _imported
from .hooks import (
    GrabFramesHook,
    QueuedBatchProcessingHook,
    SaveFramesHook,
    ScreenshotHook,
)

Sketch = "Sketch"


def screenshot(*, sketch: Sketch = None, hook_post_draw: bool = False) -> PIL_Image:
    """Take a screenshot of a running Sketch.

    Parameters
    ----------

    hook_post_draw: bool = False
        attach hook to Sketch's post_draw method instead of draw

    sketch: Sketch = None
        running Sketch

    Notes
    -----

    Take a screenshot of a running Sketch.

    The returned image is a `PIL.Image` object. It can be assigned to a variable or
    embedded in the notebook.

    By default the Sketch will be the currently running Sketch, as returned by
    `get_current_sketch()`. Use the `sketch` parameter to specify a different
    running Sketch, such as a Sketch created using class mode.

    This function will not work on a Sketch with no `draw()` function that uses an
    OpenGL renderer such as `P2D` or `P3D`. Either add a token `draw()` function or
    switch to the default `JAVA2D` renderer.

    If your Sketch has a `post_draw()` method, use the `hook_post_draw` parameter to
    make this function run after `post_draw()` instead of `draw()`. This is
    important when using Processing libraries that support `post_draw()` such as
    Camera3D or ColorBlindness."""
    import py5

    if sketch is None:
        sketch = py5.get_current_sketch()
        using_current_sketch = True
    else:
        using_current_sketch = False

    if sketch.is_dead:
        msg = f'The {"current " if using_current_sketch else ""}Sketch is dead. The py5_tools.screenshot() function cannot be used on a Sketch in the dead state.'
        if using_current_sketch:
            msg += f' Call {"" if _imported.get_imported_mode() else "py5."}reset_py5() to reset py5 to the ready state.'
        raise RuntimeError(msg)

    if py5.bridge.check_run_method_callstack():
        msg = "Calling py5_tools.screenshot() from within a py5 user function is not allowed. Please move this code to outside the Sketch or consider using save_frame() instead."
        raise RuntimeError(msg)

    if sketch._py5_bridge.has_function("draw"):
        hook = ScreenshotHook()
        sketch._add_post_hook(
            "post_draw" if hook_post_draw else "draw", hook.hook_name, hook
        )

        while not hook.is_ready and not hook.is_terminated:
            time.sleep(0.005)
            if hook.is_ready:
                return PIL.Image.fromarray(hook.pixels, mode="RGB")
            elif hook.is_terminated and hook.exception:
                raise RuntimeError("error running magic: " + str(hook.exception))
    else:
        # this works because Processing sees a dummy draw() in Sketch.java
        # method and keeps looping
        while sketch.frame_count < 1:
            time.sleep(0.005)

        if isinstance(
            sketch.get_graphics()._instance, JClass("processing.opengl.PGraphicsOpenGL")
        ):
            msg = "The py5_tools.screenshot() function cannot be used on an OpenGL Sketch with no draw() function."
            raise RuntimeError(msg)
        else:
            sketch.load_np_pixels()
            return PIL.Image.fromarray(sketch.np_pixels[:, :, 1:], mode="RGB")


def save_frames(
    dirname: str,
    *,
    filename: str = "frame_####.png",
    period: float = 0.0,
    start: int = None,
    limit: int = 0,
    sketch: Sketch = None,
    hook_post_draw: bool = False,
    block: bool = False,
    display_progress: bool = True,
) -> None:
    """Save a running Sketch's frames to a directory.

    Parameters
    ----------

    block: bool = False
        method returns immediately (False) or blocks until function returns (True)

    dirname: str
        directory to save the frames

    display_progress: bool = True
        display progress as frames are saved

    filename: str = "frame_####.png"
        filename template to use for saved frames

    hook_post_draw: bool = False
        attach hook to Sketch's post_draw method instead of draw

    limit: int = 0
        limit the number of frames to save (default 0 means no limit)

    period: float = 0.0
        time in seconds between Sketch snapshots (default 0 means no delay)

    sketch: Sketch = None
        running Sketch

    start: int = None
        frame starting number instead of Sketch frame_count

    Notes
    -----

    Save a running Sketch's frames to a directory.

    By default this function will return right away and save frames in the
    background while the Sketch is running. The frames will be saved in the
    directory specified by the `dirname` parameter. Set the `block` parameter to
    `True` to instruct the method to not return until the number of frames saved
    reaches the number specified by the `limit` parameter. This blocking feature is
    not available on macOS when the Sketch is executed through an IPython kernel.

    By default the Sketch will be the currently running Sketch, as returned by
    `get_current_sketch()`. Use the `sketch` parameter to specify a different
    running Sketch, such as a Sketch created using class mode.

    If the `limit` parameter is used, this function will wait to return a list of
    the filenames. If not, it will return right away as the frames are saved in the
    background. It will keep doing so as long as the Sketch continues to run.

    By default this function will report its progress as frames are saved. If you
    are using a Jupyter Notebook and happen to be saving tens of thousands of
    frames, this might cause Jupyter to crash. To avoid that fate, set the
    `display_progress` parameter to `False`.

    If your Sketch has a `post_draw()` method, use the `hook_post_draw` parameter to
    make this function run after `post_draw()` instead of `draw()`. This is
    important when using Processing libraries that support `post_draw()` such as
    Camera3D or ColorBlindness."""
    import py5

    if sketch is None:
        sketch = py5.get_current_sketch()
        using_current_sketch = True
    else:
        using_current_sketch = False

    if sketch.is_dead:
        msg = f'The {"current " if using_current_sketch else ""}Sketch is dead. The py5_tools.save_frames() function cannot be used on a Sketch in the dead state.'
        if using_current_sketch:
            msg += f' Call {"" if _imported.get_imported_mode() else "py5."}reset_py5() to reset py5 to the ready state.'
        raise RuntimeError(msg)

    if block and sys.platform == "darwin" and _environ.Environment().in_ipython_session:
        raise RuntimeError("Blocking is not allowed on macOS when run from IPython")

    if block and py5.bridge.check_run_method_callstack():
        msg = "Calling py5_tools.save_frames() from within a py5 user function with `block=True` is not allowed. Please move this code to outside the Sketch or set `block=False`."
        raise RuntimeError(msg)

    dirname = Path(dirname)
    if not dirname.exists():
        dirname.mkdir(parents=True)

    hook = SaveFramesHook(dirname, filename, period, start, limit, display_progress)
    sketch._add_post_hook(
        "post_draw" if hook_post_draw else "draw", hook.hook_name, hook
    )

    if block:
        while not hook.is_ready and not hook.is_terminated:
            time.sleep(0.1)


def offline_frame_processing(
    func: Callable[[npt.NDArray[np.uint8]], None],
    *,
    limit: int = 0,
    period: float = 0.0,
    batch_size: int = 1,
    complete_func: Callable[[], None] = None,
    stop_processing_func: Callable[[], bool] = None,
    sketch: Sketch = None,
    hook_post_draw: bool = False,
    queue_limit: int = None,
    block: bool = None,
    display_progress: bool = True,
) -> None:
    """Process Sketch frames in a separate thread that will minimize the performance
    impact on the Sketch's main animation thread.

    Parameters
    ----------

    batch_size: int = 1
        number of frames to include in each batch passed to the frame processing function

    block: bool = False
        method returns immediately (False) or blocks until function returns (True)

    complete_func: Callable[[], None] = None
        function to call when frame processing is complete

    display_progress: bool = True
        display progress as frames are processed

    func: Callable[[npt.NDArray[np.uint8]], None]
        function to process the Sketch's pixels, one batch at a time

    hook_post_draw: bool = False
        attach hook to Sketch's post_draw method instead of draw

    limit: int = 0
        total number of frames to pass to the frame processing function

    period: float = 0.0
        time in seconds between frames collected to be passed to the frame processing function (default 0 means no delay)

    queue_limit: int = None
        maximum number of frames that can be on the queue waiting to be processed

    sketch: Sketch = None
        running Sketch

    stop_processing_func: Callable[[], bool] = None
        optional predicate function that determines if frame processing should terminate

    Notes
    -----

    Process Sketch frames in a separate thread that will minimize the performance
    impact on the Sketch's main animation thread. As the Sketch runs it will place a
    numpy array of the frame's pixels in a queue that will be later passed to the
    user provided processing function (the `func` parameter). That function should
    not call any Sketch methods. The `offline_frame_processing()` functionality is
    well suited for goals such as live-streaming to YouTube or encoding a video
    file, both of which might otherwise impact the Sketch's frame rate
    significantly.

    The user provided processing function must take a single numpy array as a
    parameter. That numpy array will have a shape of `(batch size, height, width,
    3)` and have a dtype of `np.uint8`. The `batch_size` parameter defaults to 1 but
    can be set to other values to stack frames together into a larger array.
    Therefore a "batch" will consist of one or more frames.

    Use the `limit` parameter to stop frame processing after a set number of frames.
    You can also use the `stop_processing_func` parameter to provide a callable that
    returns `True` when processing should complete (which will stop right away and
    ignore unprocessed frames in the queue). Use the `complete_func` parameter to
    pass a function that will be called once after frame processing has stopped.

    The `queue_limit` parameter specifies a maximum queue size. If frames are added
    to the queue faster than they can be processed, the queue size will grow
    unbounded. Setting a queue limit will cause the oldest frames on the queue to be
    dropped, one batch at a time. You can use the `period` parameter to pause
    between frames that are collected for processing, throttling the workload.

    By default this function will return right away and will process frames in the
    background while the Sketch is running. Set the `block` parameter to `True` to
    instruct the method to not return until the processing is complete or the Sketch
    terminates. This blocking feature is not available on macOS when the Sketch is
    executed through an IPython kernel.

    By default this function will report its progress as frames are processed. If
    you are using a Jupyter Notebook and happen to be processing tens of thousands
    of frames, this might cause Jupyter to crash. To avoid that fate, set the
    `display_progress` parameter to `False`.

    Use the `sketch` parameter to specify a different running Sketch, such as a
    Sketch created using class mode. If your Sketch has a `post_draw()` method, use
    the `hook_post_draw` parameter to make this function run after `post_draw()`
    instead of `draw()`. This is important when using Processing libraries that
    support `post_draw()` such as Camera3D or ColorBlindness."""
    import py5

    if sketch is None:
        sketch = py5.get_current_sketch()
        using_current_sketch = True
    else:
        using_current_sketch = False

    if sketch.is_dead:
        msg = f'The {"current " if using_current_sketch else ""}Sketch is dead. The py5_tools.offline_frame_processing() function cannot be used on a Sketch in the dead state.'
        if using_current_sketch:
            msg += f' Call {"" if _imported.get_imported_mode() else "py5."}reset_py5() to reset py5 to the ready state.'
        raise RuntimeError(msg)

    if block and py5.bridge.check_run_method_callstack():
        msg = "Calling py5_tools.offline_frame_processing() from within a py5 user function with `block=True` is not allowed. Please move this code to outside the Sketch or set `block=False`."
        raise RuntimeError(msg)

    hook = QueuedBatchProcessingHook(
        period,
        limit,
        batch_size,
        func,
        complete_func=complete_func,
        stop_processing_func=stop_processing_func,
        queue_limit=queue_limit,
        display_progress=display_progress,
    )
    sketch._add_post_hook(
        "post_draw" if hook_post_draw else "draw", hook.hook_name, hook
    )

    if block:
        while not hook.is_ready and not hook.is_terminated:
            time.sleep(0.1)


def animated_gif(
    filename: str,
    *,
    count: int = 0,
    period: float = 0.0,
    frame_numbers: Iterable = None,
    duration: float = 0.0,
    loop: int = 0,
    optimize: bool = True,
    sketch: Sketch = None,
    hook_post_draw: bool = False,
    block: bool = False,
) -> None:
    """Create an animated GIF using a running Sketch.

    Parameters
    ----------

    block: bool = False
        function returns immediately (False) or blocks until function returns (True)

    count: int = 0
        number of Sketch snapshots to create

    duration: float = 0.0
        time in seconds between frames in the GIF

    filename: str
        filename of GIF to create

    frame_numbers: Iterable = None
        list of frame numbers to include in animated GIF

    hook_post_draw: bool = False
        attach hook to Sketch's post_draw method instead of draw

    loop: int = 0
        number of times for the GIF to loop (default of 0 loops indefinitely)

    optimize: bool = True
        optimize GIF palette

    period: float = 0.0
        time in seconds between Sketch snapshots

    sketch: Sketch = None
        running Sketch

    Notes
    -----

    Create an animated GIF using a running Sketch.

    You have two choices for how to specify which frames should be included in the
    animated GIF. The first choice is to use the `count` keyword argument to include
    a specific number of frames. Optionally, the `period` keyword argument can also
    be used with `count` to introduce a fixed time delay between captured frames.
    The second choice is to use the `frame_numbers` keyword argument to pass a list
    of frame numbers. A frame will be included when the `frame_count` value is in
    the list passed to `frame_numbers`. For this feature, frame number 0 is after
    `setup()` is complete and frame number 1 is after the first call to `draw()`.

    Bottom line, you must use either the `count` parameter or the `frame_numbers`
    parameter but not both. The `period` parameter can only be used in conjunction
    with the `count` parameter. The duration parameter must always be used.

    By default this function will return right away and construct the animated gif
    in the background while the Sketch is running. The completed gif will be saved
    to the location specified by the `filename` parameter when it is ready. Set the
    `block` parameter to `True` to instruct the function to not return until the gif
    construction is complete. This blocking feature is not available on macOS when
    the Sketch is executed through an IPython kernel. If the Sketch terminates
    prematurely, no gif will be created.

    By default the Sketch will be the currently running Sketch, as returned by
    `get_current_sketch()`. Use the `sketch` parameter to specify a different
    running Sketch, such as a Sketch created using class mode.

    If your Sketch has a `post_draw()` method, use the `hook_post_draw` parameter to
    make this function run after `post_draw()` instead of `draw()`. This is
    important when using Processing libraries that support `post_draw()` such as
    Camera3D or ColorBlindness."""
    import py5

    if count > 0 and frame_numbers is None:
        # ok
        pass
    elif (
        count == 0 and frame_numbers is not None and isinstance(frame_numbers, Iterable)
    ):
        # ok, but check period is still 0.0
        if period != 0.0:
            raise RuntimeError(
                "Must not pass period parameter when using the frame_numbers parameter"
            )
    else:
        # not ok
        raise RuntimeError(
            "Must either pass count > 0 or pass frame_numbers an iterable, but not both"
        )

    if duration <= 0.0:
        raise RuntimeError(
            "Must pass a duration > 0.0 to specify the time delay between frames in the animated gif"
        )

    if sketch is None:
        sketch = py5.get_current_sketch()
        using_current_sketch = True
    else:
        using_current_sketch = False

    if sketch.is_dead:
        msg = f'The {"current " if using_current_sketch else ""}Sketch is dead. The py5_tools.animated_gif() function cannot be used on a Sketch in the dead state.'
        if using_current_sketch:
            msg += f' Call {"" if _imported.get_imported_mode() else "py5."}reset_py5() to reset py5 to the ready state.'
        raise RuntimeError(msg)

    if block and sys.platform == "darwin" and _environ.Environment().in_ipython_session:
        raise RuntimeError("Blocking is not allowed on macOS when run from IPython")

    if block and py5.bridge.check_run_method_callstack():
        msg = "Calling py5_tools.animated_gif() from within a py5 user function with `block=True` is not allowed. Please move this code to outside the Sketch or set `block=False`."
        raise RuntimeError(msg)

    filename = Path(filename)

    def complete_func(hook):
        if not filename.parent.exists():
            filename.parent.mkdir(parents=True)

        img1 = PIL.Image.fromarray(hook.frames[0], mode="RGB")
        imgs = [PIL.Image.fromarray(arr, mode="RGB") for arr in hook.frames[1:]]
        img1.save(
            filename,
            save_all=True,
            duration=1000 * duration,
            loop=loop,
            optimize=optimize,
            append_images=imgs,
        )

        hook.status_msg("animated gif written to " + str(filename))

    hook_setup = bool(frame_numbers and 0 in frame_numbers)
    hook = GrabFramesHook(
        frame_numbers, period, count, complete_func, hooked_setup=hook_setup
    )
    sketch._add_post_hook(
        "post_draw" if hook_post_draw else "draw", hook.hook_name, hook
    )
    if hook_setup:
        sketch._add_post_hook("setup", hook.hook_name, hook)

    if block:
        while not hook.is_ready and not hook.is_terminated:
            time.sleep(0.1)


def capture_frames(
    *,
    count: float = 0,
    period: float = 0.0,
    frame_numbers: Iterable = None,
    sketch: Sketch = None,
    hook_post_draw: bool = False,
    block: bool = False,
) -> list[PIL_Image]:
    """Capture frames from a running Sketch.

    Parameters
    ----------

    block: bool = False
        function returns immediately (False) or blocks until function returns (True)

    count: float = 0
        number of Sketch snapshots to capture

    frame_numbers: Iterable = None
        list of frame numbers to capture

    hook_post_draw: bool = False
        attach hook to Sketch's post_draw method instead of draw

    period: float = 0.0
        time in seconds between Sketch snapshots (default 0 means no delay)

    sketch: Sketch = None
        running Sketch

    Notes
    -----

    Capture frames from a running Sketch.

    You have two choices for how to specify which frames should be captured. The
    first choice is to use the `count` keyword argument to capture a specific number
    of frames. Optionally, the `period` keyword argument can also be used with
    `count` to introduce a fixed time delay between captured frames. The second
    choice is to use the `frame_numbers` keyword argument to pass a list of frame
    numbers. A frame will be captured when the `frame_count` value is in the list
    passed to `frame_numbers`. For this feature, frame number 0 is after `setup()`
    is complete and frame number 1 is after the first call to `draw()`.

    Bottom line, you must use either the `count` parameter or the `frame_numbers`
    parameter but not both. The `period` parameter can only be used in conjunction
    with the `count` parameter.

    By default this function will return right away and will capture frames in the
    background while the Sketch is running. The returned list of PIL Image objects
    (`list[PIL.Image]`) will initially be empty, and will be populated all at once
    when the complete set of frames has been captured. Set the `block` parameter to
    `True` to instruct this function to capture the frames in the foreground and to
    not return until the complete list of frames is ready to be returned. To get
    access to the captured frames as they become available, use the
    `py5_tools.offline_frame_processing()` function instead. If the Sketch is
    terminated prematurely, the returned list will be empty.

    By default the Sketch will be the currently running Sketch, as returned by
    `get_current_sketch()`. Use the `sketch` parameter to specify a different
    running Sketch, such as a Sketch created using class mode.

    If your Sketch has a `post_draw()` method, use the `hook_post_draw` parameter to
    make this function run after `post_draw()` instead of `draw()`. This is
    important when using Processing libraries that support `post_draw()` such as
    Camera3D or ColorBlindness."""
    import py5

    if count > 0 and frame_numbers is None:
        # ok
        pass
    elif (
        count == 0 and frame_numbers is not None and isinstance(frame_numbers, Iterable)
    ):
        # ok, but check period is still 0.0
        if period != 0.0:
            raise RuntimeError(
                "Must not pass period parameter when using the frame_numbers parameter"
            )
    else:
        # not ok
        raise RuntimeError(
            "Must either pass count > 0 or pass frame_numbers an iterable, but not both"
        )

    if sketch is None:
        sketch = py5.get_current_sketch()
        using_current_sketch = True
    else:
        using_current_sketch = False

    if sketch.is_dead:
        msg = f'The {"current " if using_current_sketch else ""}Sketch is dead. The py5_tools.capture_frames() function cannot be used on a Sketch in the dead state.'
        if using_current_sketch:
            msg += f' Call {"" if _imported.get_imported_mode() else "py5."}reset_py5() to reset py5 to the ready state.'
        raise RuntimeError(msg)

    if block and sys.platform == "darwin" and _environ.Environment().in_ipython_session:
        raise RuntimeError("Blocking is not allowed on macOS when run from IPython")

    if block and py5.bridge.check_run_method_callstack():
        msg = "Calling py5_tools.capture_frames() from within a py5 user function with `block=True` is not allowed. Please move this code to outside the Sketch or set `block=False`."
        raise RuntimeError(msg)

    results = []

    def complete_func(hook):
        results.extend([PIL.Image.fromarray(arr, mode="RGB") for arr in hook.frames])
        hook.status_msg(f"captured {len(hook.frames)} frames")

    hook_setup = bool(frame_numbers and 0 in frame_numbers)
    hook = GrabFramesHook(
        frame_numbers, period, count, complete_func, hooked_setup=hook_setup
    )
    sketch._add_post_hook(
        "post_draw" if hook_post_draw else "draw", hook.hook_name, hook
    )
    if hook_setup:
        sketch._add_post_hook("setup", hook.hook_name, hook)

    if block:
        while not hook.is_ready and not hook.is_terminated:
            time.sleep(0.1)

    return results


__all__ = [
    "screenshot",
    "save_frames",
    "offline_frame_processing",
    "animated_gif",
    "capture_frames",
]
