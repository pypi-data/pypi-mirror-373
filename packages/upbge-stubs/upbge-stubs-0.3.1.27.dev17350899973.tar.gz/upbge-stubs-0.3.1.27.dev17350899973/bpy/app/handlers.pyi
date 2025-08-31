"""


Application Handlers (bpy.app.handlers)
***************************************

This module contains callback lists


Basic Handler Example
=====================

This script shows the most simple example of adding a handler.

.. code::

  import bpy


  def my_handler(scene):
      print("Frame Change", scene.frame_current)


  bpy.app.handlers.frame_change_pre.append(my_handler)


Persistent Handler Example
==========================

By default handlers are freed when loading new files, in some cases you may
want the handler stay running across multiple files (when the handler is
part of an add-on for example).

For this the :data:`bpy.app.handlers.persistent` decorator needs to be used.

.. code::

  import bpy
  from bpy.app.handlers import persistent


  @persistent
  def load_handler(dummy):
      print("Load Handler:", bpy.data.filepath)


  bpy.app.handlers.load_post.append(load_handler)


Note on Altering Data
=====================

Altering data from handlers should be done carefully. While rendering the
``frame_change_pre`` and ``frame_change_post`` handlers are called from one
thread and the viewport updates from a different thread. If the handler changes
data that is accessed by the viewport, this can cause a crash of Blender. In
such cases, lock the interface (Render → Lock Interface or
:data:`bpy.types.RenderSettings.use_lock_interface`) before starting a render.

Below is an example of a mesh that is altered from a handler:

.. code::

  def frame_change_pre(scene):
      # A triangle that shifts in the z direction.
      zshift = scene.frame_current * 0.1
      vertices = [(-1, -1, zshift), (1, -1, zshift), (0, 1, zshift)]
      triangles = [(0, 1, 2)]

      object = bpy.data.objects["The Object"]
      object.data.clear_geometry()
      object.data.from_pydata(vertices, [], triangles)

:data:`animation_playback_post`

:data:`animation_playback_pre`

:data:`annotation_post`

:data:`annotation_pre`

:data:`blend_import_post`

:data:`blend_import_pre`

:data:`composite_cancel`

:data:`composite_post`

:data:`composite_pre`

:data:`depsgraph_update_post`

:data:`depsgraph_update_pre`

:data:`frame_change_post`

:data:`frame_change_pre`

:data:`game_post`

:data:`game_pre`

:data:`load_factory_preferences_post`

:data:`load_factory_startup_post`

:data:`load_post`

:data:`load_post_fail`

:data:`load_pre`

:data:`object_bake_cancel`

:data:`object_bake_complete`

:data:`object_bake_pre`

:data:`redo_post`

:data:`redo_pre`

:data:`render_cancel`

:data:`render_complete`

:data:`render_init`

:data:`render_post`

:data:`render_pre`

:data:`render_stats`

:data:`render_write`

:data:`save_post`

:data:`save_post_fail`

:data:`save_pre`

:data:`translation_update_post`

:data:`undo_post`

:data:`undo_pre`

:data:`version_update`

:data:`xr_session_start_pre`

:data:`persistent`

"""

import typing

animation_playback_post: typing.Any = ...

"""

on ending animation playback. Accepts two arguments: The scene data-block and the dependency graph being updated

"""

animation_playback_pre: typing.Any = ...

"""

on starting animation playback. Accepts two arguments: The scene data-block and the dependency graph being updated

"""

annotation_post: typing.Any = ...

"""

on drawing an annotation (after). Accepts two arguments: the annotation data-block and dependency graph

"""

annotation_pre: typing.Any = ...

"""

on drawing an annotation (before). Accepts two arguments: the annotation data-block and dependency graph

"""

blend_import_post: typing.Any = ...

"""

on linking or appending data (after). Accepts one argument: a BlendImportContext

"""

blend_import_pre: typing.Any = ...

"""

on linking or appending data (before). Accepts one argument: a BlendImportContext

"""

composite_cancel: typing.Any = ...

"""

on a compositing background job (cancel). Accepts one argument: the scene data-block

"""

composite_post: typing.Any = ...

"""

on a compositing background job (after). Accepts one argument: the scene data-block

"""

composite_pre: typing.Any = ...

"""

on a compositing background job (before). Accepts one argument: the scene data-block

"""

depsgraph_update_post: typing.Any = ...

"""

on depsgraph update (post). Accepts two arguments: The scene data-block and the dependency graph being updated

"""

depsgraph_update_pre: typing.Any = ...

"""

on depsgraph update (pre). Accepts two arguments: The scene data-block and the dependency graph being updated

"""

frame_change_post: typing.Any = ...

"""

Called after frame change for playback and rendering, after the data has been evaluated for the new frame. Accepts two arguments: The scene data-block and the dependency graph being updated

"""

frame_change_pre: typing.Any = ...

"""

Called after frame change for playback and rendering, before any data is evaluated for the new frame. This makes it possible to change data and relations (for example swap an object to another mesh) for the new frame. Note that this handler is **not** to be used as 'before the frame changes' event. The dependency graph is not available in this handler, as data and relations may have been altered and the dependency graph has not yet been updated for that. Accepts two arguments: The scene data-block and the dependency graph being updated

"""

game_post: typing.Any = ...

"""

on ending the game engine

"""

game_pre: typing.Any = ...

"""

on starting the game engine

"""

load_factory_preferences_post: typing.Any = ...

"""

on loading factory preferences (after)

"""

load_factory_startup_post: typing.Any = ...

"""

on loading factory startup (after)

"""

load_post: typing.Any = ...

"""

on loading a new blend file (after). Accepts one argument: the file being loaded, an empty string for the startup-file.

"""

load_post_fail: typing.Any = ...

"""

on failure to load a new blend file (after). Accepts one argument: the file being loaded, an empty string for the startup-file.

"""

load_pre: typing.Any = ...

"""

on loading a new blend file (before).Accepts one argument: the file being loaded, an empty string for the startup-file.

"""

object_bake_cancel: typing.Any = ...

"""

on canceling a bake job; will be called in the main thread. Accepts one argument: the object data-block being baked

"""

object_bake_complete: typing.Any = ...

"""

on completing a bake job; will be called in the main thread. Accepts one argument: the object data-block being baked

"""

object_bake_pre: typing.Any = ...

"""

before starting a bake job. Accepts one argument: the object data-block being baked

"""

redo_post: typing.Any = ...

"""

on loading a redo step (after)

"""

redo_pre: typing.Any = ...

"""

on loading a redo step (before)

"""

render_cancel: typing.Any = ...

"""

on canceling a render job. Accepts one argument: the scene data-block being rendered

"""

render_complete: typing.Any = ...

"""

on completion of render job. Accepts one argument: the scene data-block being rendered

"""

render_init: typing.Any = ...

"""

on initialization of a render job. Accepts one argument: the scene data-block being rendered

"""

render_post: typing.Any = ...

"""

on render (after)

"""

render_pre: typing.Any = ...

"""

on render (before)

"""

render_stats: typing.Any = ...

"""

on printing render statistics. Accepts one argument: the render stats (render/saving time plus in background mode frame/used [peak] memory).

"""

render_write: typing.Any = ...

"""

on writing a render frame (directly after the frame is written)

"""

save_post: typing.Any = ...

"""

on saving a blend file (after). Accepts one argument: the file being saved, an empty string for the startup-file.

"""

save_post_fail: typing.Any = ...

"""

on failure to save a blend file (after). Accepts one argument: the file being saved, an empty string for the startup-file.

"""

save_pre: typing.Any = ...

"""

on saving a blend file (before). Accepts one argument: the file being saved, an empty string for the startup-file.

"""

translation_update_post: typing.Any = ...

"""

on translation settings update

"""

undo_post: typing.Any = ...

"""

on loading an undo step (after)

"""

undo_pre: typing.Any = ...

"""

on loading an undo step (before)

"""

version_update: typing.Any = ...

"""

on ending the versioning code

"""

xr_session_start_pre: typing.Any = ...

"""

on starting an xr session (before)

"""

persistent: typing.Any = ...

"""

Function decorator for callback functions not to be removed when loading new files

"""
