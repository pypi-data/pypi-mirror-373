"""


Application Data (bpy.app)
**************************

This module contains application values that remain unchanged during runtime.

:data:`autoexec_fail`

:data:`autoexec_fail_message`

:data:`autoexec_fail_quiet`

:data:`binary_path`

:data:`debug`

:data:`debug_depsgraph`

:data:`debug_depsgraph_build`

:data:`debug_depsgraph_eval`

:data:`debug_depsgraph_pretty`

:data:`debug_depsgraph_tag`

:data:`debug_depsgraph_time`

:data:`debug_events`

:data:`debug_freestyle`

:data:`debug_handlers`

:data:`debug_io`

:data:`debug_python`

:data:`debug_simdata`

:data:`debug_value`

:data:`debug_wm`

:data:`driver_namespace`

:data:`online_access`

:data:`online_access_override`

:data:`python_args`

:data:`render_icon_size`

:data:`render_preview_size`

:data:`tempdir`

:data:`use_event_simulate`

:data:`use_userpref_skip_save_on_exit`

:data:`background`

:data:`factory_startup`

:data:`module`

:data:`portable`

:data:`build_branch`

:data:`build_cflags`

:data:`build_commit_date`

:data:`build_commit_time`

:data:`build_cxxflags`

:data:`build_date`

:data:`build_hash`

:data:`build_linkflags`

:data:`build_platform`

:data:`build_system`

:data:`build_time`

:data:`build_type`

:data:`build_commit_timestamp`

:data:`version_cycle`

:data:`version_string`

:data:`version`

:data:`version_file`

:data:`alembic`

:data:`build_options`

:data:`ffmpeg`

:data:`ocio`

:data:`oiio`

:data:`opensubdiv`

:data:`openvdb`

:data:`sdl`

:data:`usd`

:func:`help_text`

:func:`is_job_running`

"""

from . import translations

from . import timers

from . import icons

from . import handlers

import typing

autoexec_fail: typing.Any = ...

"""

Undocumented, consider `contributing <https://developer.blender.org/>`_.

"""

autoexec_fail_message: typing.Any = ...

"""

Undocumented, consider `contributing <https://developer.blender.org/>`_.

"""

autoexec_fail_quiet: typing.Any = ...

"""

Undocumented, consider `contributing <https://developer.blender.org/>`_.

"""

binary_path: typing.Any = ...

"""

The location of Blender's executable, useful for utilities that open new instances. Read-only unless Blender is built as a Python module - in this case the value is an empty string which script authors may point to a Blender binary.

"""

debug: typing.Any = ...

"""

Boolean, for debug info (started with ``--debug`` / ``--debug-*`` matching this attribute name).

"""

debug_depsgraph: typing.Any = ...

"""

Boolean, for debug info (started with ``--debug`` / ``--debug-*`` matching this attribute name).

"""

debug_depsgraph_build: typing.Any = ...

"""

Boolean, for debug info (started with ``--debug`` / ``--debug-*`` matching this attribute name).

"""

debug_depsgraph_eval: typing.Any = ...

"""

Boolean, for debug info (started with ``--debug`` / ``--debug-*`` matching this attribute name).

"""

debug_depsgraph_pretty: typing.Any = ...

"""

Boolean, for debug info (started with ``--debug`` / ``--debug-*`` matching this attribute name).

"""

debug_depsgraph_tag: typing.Any = ...

"""

Boolean, for debug info (started with ``--debug`` / ``--debug-*`` matching this attribute name).

"""

debug_depsgraph_time: typing.Any = ...

"""

Boolean, for debug info (started with ``--debug`` / ``--debug-*`` matching this attribute name).

"""

debug_events: typing.Any = ...

"""

Boolean, for debug info (started with ``--debug`` / ``--debug-*`` matching this attribute name).

"""

debug_freestyle: typing.Any = ...

"""

Boolean, for debug info (started with ``--debug`` / ``--debug-*`` matching this attribute name).

"""

debug_handlers: typing.Any = ...

"""

Boolean, for debug info (started with ``--debug`` / ``--debug-*`` matching this attribute name).

"""

debug_io: typing.Any = ...

"""

Boolean, for debug info (started with ``--debug`` / ``--debug-*`` matching this attribute name).

"""

debug_python: typing.Any = ...

"""

Boolean, for debug info (started with ``--debug`` / ``--debug-*`` matching this attribute name).

"""

debug_simdata: typing.Any = ...

"""

Boolean, for debug info (started with ``--debug`` / ``--debug-*`` matching this attribute name).

"""

debug_value: typing.Any = ...

"""

Short, number which can be set to non-zero values for testing purposes.

"""

debug_wm: typing.Any = ...

"""

Boolean, for debug info (started with ``--debug`` / ``--debug-*`` matching this attribute name).

"""

driver_namespace: typing.Any = ...

"""

Dictionary for drivers namespace, editable in-place, reset on file load (read-only).

File Loading & Order of Initialization
  Since drivers may be evaluated immediately after loading a blend-file it is necessary
to ensure the driver name-space is initialized beforehand.

  This can be done by registering text data-blocks to execute on startup,
which executes the scripts before drivers are evaluated.
See *Text -> Register* from Blender's text editor.

  Hint: You may prefer to use external files instead of Blender's text-blocks.
This can be done using a text-block which executes an external file.This example runs ``driver_namespace.py`` located in the same directory as the text-blocks blend-file:

    .. code::

      import os
      import bpy
      blend_dir = os.path.normalize(os.path.join(__file__, "..", ".."))
      bpy.utils.execfile(os.path.join(blend_dir, "driver_namespace.py"))

    Using ``__file__`` ensures the text resolves to the expected path even when library-linked from another file.

  Other methods of populating the drivers name-space can be made to work but tend to be error prone:

  Using The ``--python`` command line argument to populate name-space often fails to achieve the desired goal
because the initial evaluation will lookup a function that doesn't exist yet,
marking the driver as invalid - preventing further evaluation.

  Populating the driver name-space before the blend-file loads also doesn't work
since opening a file clears the name-space.

  It is possible to run a script via the ``--python`` command line argument, before the blend file.
This can register a load-post handler (:mod:`bpy.app.handlers.load_post`) that initialized the name-space.
While this works for background tasks it has the downside that opening the file from the file selector
won't setup the name-space.

"""

online_access: typing.Any = ...

"""

Boolean, true when internet access is allowed by Blender & 3rd party scripts (read-only).

"""

online_access_override: typing.Any = ...

"""

Boolean, true when internet access preference is overridden by the command line (read-only).

"""

python_args: typing.Any = ...

"""

Leading arguments to use when calling Python directly (via ``sys.executable``). These arguments match settings Blender uses to ensure Python runs with a compatible environment (read-only).

"""

render_icon_size: typing.Any = ...

"""

Reference size for icon/preview renders (read-only).

"""

render_preview_size: typing.Any = ...

"""

Reference size for icon/preview renders (read-only).

"""

tempdir: typing.Any = ...

"""

String, the temp directory used by blender (read-only).

"""

use_event_simulate: typing.Any = ...

"""

Boolean, for application behavior (started with ``--enable-*`` matching this attribute name)

"""

use_userpref_skip_save_on_exit: typing.Any = ...

"""

Boolean, for application behavior (started with ``--enable-*`` matching this attribute name)

"""

background: typing.Any = ...

"""

Boolean, True when blender is running without a user interface (started with -b)

"""

factory_startup: typing.Any = ...

"""

Boolean, True when blender is running with --factory-startup)

"""

module: typing.Any = ...

"""

Boolean, True when running Blender as a python module

"""

portable: typing.Any = ...

"""

Boolean, True unless blender was built to reference absolute paths (on UNIX).

"""

build_branch: typing.Any = ...

"""

The branch this blender instance was built from

"""

build_cflags: typing.Any = ...

"""

C compiler flags

"""

build_commit_date: typing.Any = ...

"""

The date of commit this blender instance was built

"""

build_commit_time: typing.Any = ...

"""

The time of commit this blender instance was built

"""

build_cxxflags: typing.Any = ...

"""

C++ compiler flags

"""

build_date: typing.Any = ...

"""

The date this blender instance was built

"""

build_hash: typing.Any = ...

"""

The commit hash this blender instance was built with

"""

build_linkflags: typing.Any = ...

"""

Binary linking flags

"""

build_platform: typing.Any = ...

"""

The platform this blender instance was built for

"""

build_system: typing.Any = ...

"""

Build system used

"""

build_time: typing.Any = ...

"""

The time this blender instance was built

"""

build_type: typing.Any = ...

"""

The type of build (Release, Debug)

"""

build_commit_timestamp: typing.Any = ...

"""

The unix timestamp of commit this blender instance was built

"""

version_cycle: typing.Any = ...

"""

The release status of this build alpha/beta/rc/release

"""

version_string: typing.Any = ...

"""

The Blender version formatted as a string

"""

version: typing.Any = ...

"""

The Blender version as a tuple of 3 numbers (major, minor, micro). eg. (4, 3, 1)

"""

version_file: typing.Any = ...

"""

The Blender File version, as a tuple of 3 numbers (major, minor, file sub-version), that will be used to save a .blend file. The last item in this tuple indicates the file sub-version, which is different from the release micro version (the last item of the ``bpy.app.version`` tuple). The file sub-version can be incremented multiple times while a Blender version is under development. This value is, and should be, used for handling compatibility changes between Blender versions

"""

alembic: typing.Any = ...

"""

Constant value bpy.app.alembic(supported=True, version=(1, 8, 3), version_string=' 1,  8,  3')

"""

build_options: typing.Any = ...

"""

Constant value bpy.app.build_options(bullet=True, codec_avi=False, codec_ffmpeg=True, codec_sndfile=True, compositor_cpu=True, cycles=False, cycles_osl=False, freestyle=True, gameengine=True, image_cineon=True, image_dds=True, image_hdr=True, image_openexr=True, image_openjpeg=True, image_tiff=True, image_webp=True, input_ndof=True, audaspace=True, international=True, openal=True, opensubdiv=True, sdl=True, coreaudio=False, jack=False, pulseaudio=False, wasapi=False, libmv=False, mod_oceansim=False, mod_remesh=True, player=True, io_wavefront_obj=True, io_ply=True, io_stl=True, io_fbx=True, io_gpencil=True, opencolorio=False, openmp=False, openvdb=True, alembic=True, usd=True, fluid=True, xr_openxr=True, potrace=True, pugixml=True, haru=True, experimental_features=True)

"""

ffmpeg: typing.Any = ...

"""

Constant value bpy.app.ffmpeg(supported=True, avcodec_version=(61, 19, 101), avcodec_version_string='61, 19, 101', avdevice_version=(61, 3, 100), avdevice_version_string='61,  3, 100', avformat_version=(61, 7, 100), avformat_version_string='61,  7, 100', avutil_version=(59, 39, 100), avutil_version_string='59, 39, 100', swscale_version=(8, 3, 100), swscale_version_string=' 8,  3, 100')

"""

ocio: typing.Any = ...

"""

Constant value bpy.app.ocio(supported=True, version=(2, 4, 1), version_string=' 2,  4,  1')

"""

oiio: typing.Any = ...

"""

Constant value bpy.app.oiio(supported=True, version=(3, 0, 6), version_string=' 3,  0,  6')

"""

opensubdiv: typing.Any = ...

"""

Constant value bpy.app.opensubdiv(supported=True, version=(3, 6, 0), version_string=' 3,  6,  0')

"""

openvdb: typing.Any = ...

"""

Constant value bpy.app.openvdb(supported=True, version=(12, 0, 0), version_string='12,  0,  0')

"""

sdl: typing.Any = ...

"""

Constant value bpy.app.sdl(supported=True, version=(2, 28, 2), version_string='2.28.2')

"""

usd: typing.Any = ...

"""

Constant value bpy.app.usd(supported=True, version=(0, 25, 2), version_string=' 0, 25,  2')

"""

@staticmethod

def help_text(*args, all: bool = False) -> None:

  """

  Return the help text as a string.

  """

  ...

@staticmethod

def is_job_running(job_type: str) -> bool:

  """

  Check whether a job of the given type is running.

  """

  ...
