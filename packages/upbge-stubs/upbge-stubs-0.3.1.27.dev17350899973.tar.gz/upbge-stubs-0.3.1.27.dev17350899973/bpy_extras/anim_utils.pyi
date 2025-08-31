"""


bpy_extras submodule (bpy_extras.anim_utils)
********************************************

:func:`bake_action`

:func:`bake_action_objects`

:func:`bake_action_iter`

:func:`bake_action_objects_iter`

:class:`bpy_extras.anim_utils.BakeOptions`

"""

import typing

import bpy

import anim_utils

def bake_action(obj: bpy.types.Object, *args, action: bpy.types.Action, frames: int, bake_options: anim_utils.BakeOptions) -> bpy.types.Action:

  ...

def bake_action_objects(object_action_pairs: typing.Any, *args, frames: typing.Iterable[int], bake_options: anim_utils.BakeOptions) -> typing.Any:

  """

  A version of :func:`bake_action_objects_iter` that takes frames and returns the output.

  """

  ...

def bake_action_iter(obj: bpy.types.Object, *args, action: bpy.types.Action, bake_options: anim_utils.BakeOptions) -> bpy.types.Action:

  """

  An coroutine that bakes action for a single object.

  """

  ...

def bake_action_objects_iter(object_action_pairs: typing.Sequence[typing.Any], bake_options: anim_utils.BakeOptions) -> None:

  """

  An coroutine that bakes actions for multiple objects.

  """

  ...

class bpy_extras.anim_utils.BakeOptions:

  """

  BakeOptions(only_selected: bool, do_pose: bool, do_object: bool, do_visual_keying: bool, do_constraint_clear: bool, do_parents_clear: bool, do_clean: bool, do_location: bool, do_rotation: bool, do_scale: bool, do_bbone: bool, do_custom_props: bool)

  """

  ...
