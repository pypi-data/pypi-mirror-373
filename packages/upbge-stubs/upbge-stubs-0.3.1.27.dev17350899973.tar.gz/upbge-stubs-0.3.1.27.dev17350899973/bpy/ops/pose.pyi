"""


Pose Operators
**************

:func:`armature_apply`

:func:`autoside_names`

:func:`blend_to_neighbor`

:func:`blend_with_rest`

:func:`breakdown`

:func:`constraint_add`

:func:`constraint_add_with_targets`

:func:`constraints_clear`

:func:`constraints_copy`

:func:`copy`

:func:`flip_names`

:func:`hide`

:func:`ik_add`

:func:`ik_clear`

:func:`loc_clear`

:func:`paste`

:func:`paths_calculate`

:func:`paths_clear`

:func:`paths_range_update`

:func:`paths_update`

:func:`propagate`

:func:`push`

:func:`quaternions_flip`

:func:`relax`

:func:`reveal`

:func:`rot_clear`

:func:`rotation_mode_set`

:func:`scale_clear`

:func:`select_all`

:func:`select_constraint_target`

:func:`select_grouped`

:func:`select_hierarchy`

:func:`select_linked`

:func:`select_linked_pick`

:func:`select_mirror`

:func:`select_parent`

:func:`selection_set_add`

:func:`selection_set_add_and_assign`

:func:`selection_set_assign`

:func:`selection_set_copy`

:func:`selection_set_delete_all`

:func:`selection_set_deselect`

:func:`selection_set_move`

:func:`selection_set_paste`

:func:`selection_set_remove`

:func:`selection_set_remove_bones`

:func:`selection_set_select`

:func:`selection_set_unassign`

:func:`transforms_clear`

:func:`user_transforms_clear`

:func:`visual_transform_apply`

"""

import typing

def armature_apply(*args, selected: bool = False) -> None:

  """

  Apply the current pose as the new rest pose

  """

  ...

def autoside_names(*args, axis: str = 'XAXIS') -> None:

  """

  Automatically renames the selected bones according to which side of the target axis they fall on

  """

  ...

def blend_to_neighbor(*args, factor: float = 0.5, prev_frame: int = 0, next_frame: int = 0, channels: str = 'ALL', axis_lock: str = 'FREE') -> None:

  """

  Blend from current position to previous or next keyframe

  """

  ...

def blend_with_rest(*args, factor: float = 0.5, prev_frame: int = 0, next_frame: int = 0, channels: str = 'ALL', axis_lock: str = 'FREE') -> None:

  """

  Make the current pose more similar to, or further away from, the rest pose

  """

  ...

def breakdown(*args, factor: float = 0.5, prev_frame: int = 0, next_frame: int = 0, channels: str = 'ALL', axis_lock: str = 'FREE') -> None:

  """

  Create a suitable breakdown pose on the current frame

  """

  ...

def constraint_add(*args, type: str = '') -> None:

  """

  Add a constraint to the active bone

  """

  ...

def constraint_add_with_targets(*args, type: str = '') -> None:

  """

  Add a constraint to the active bone, with target (where applicable) set to the selected Objects/Bones

  """

  ...

def constraints_clear() -> None:

  """

  Clear all constraints from the selected bones

  """

  ...

def constraints_copy() -> None:

  """

  Copy constraints to other selected bones

  """

  ...

def copy() -> None:

  """

  Copy the current pose of the selected bones to the internal clipboard

  """

  ...

def flip_names(*args, do_strip_numbers: bool = False) -> None:

  """

  Flips (and corrects) the axis suffixes of the names of selected bones

  """

  ...

def hide(*args, unselected: bool = False) -> None:

  """

  Tag selected bones to not be visible in Pose Mode

  """

  ...

def ik_add(*args, with_targets: bool = True) -> None:

  """

  Add IK Constraint to the active Bone

  """

  ...

def ik_clear() -> None:

  """

  Remove all IK Constraints from selected bones

  """

  ...

def loc_clear() -> None:

  """

  Reset locations of selected bones to their default values

  """

  ...

def paste(*args, flipped: bool = False, selected_mask: bool = False) -> None:

  """

  Paste the stored pose on to the current pose

  """

  ...

def paths_calculate(*args, display_type: str = 'RANGE', range: str = 'SCENE', bake_location: str = 'HEADS') -> None:

  """

  Calculate paths for the selected bones

  """

  ...

def paths_clear(*args, only_selected: bool = False) -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def paths_range_update() -> None:

  """

  Update frame range for motion paths from the Scene's current frame range

  """

  ...

def paths_update() -> None:

  """

  Recalculate paths for bones that already have them

  """

  ...

def propagate(*args, mode: str = 'NEXT_KEY', end_frame: float = 250.0) -> None:

  """

  Copy selected aspects of the current pose to subsequent poses already keyframed

  """

  ...

def push(*args, factor: float = 0.5, prev_frame: int = 0, next_frame: int = 0, channels: str = 'ALL', axis_lock: str = 'FREE') -> None:

  """

  Exaggerate the current pose in regards to the breakdown pose

  """

  ...

def quaternions_flip() -> None:

  """

  Flip quaternion values to achieve desired rotations, while maintaining the same orientations

  """

  ...

def relax(*args, factor: float = 0.5, prev_frame: int = 0, next_frame: int = 0, channels: str = 'ALL', axis_lock: str = 'FREE') -> None:

  """

  Make the current pose more similar to its breakdown pose

  """

  ...

def reveal(*args, select: bool = True) -> None:

  """

  Reveal all bones hidden in Pose Mode

  """

  ...

def rot_clear() -> None:

  """

  Reset rotations of selected bones to their default values

  """

  ...

def rotation_mode_set(*args, type: str = 'QUATERNION') -> None:

  """

  Set the rotation representation used by selected bones

  """

  ...

def scale_clear() -> None:

  """

  Reset scaling of selected bones to their default values

  """

  ...

def select_all(*args, action: str = 'TOGGLE') -> None:

  """

  Toggle selection status of all bones

  """

  ...

def select_constraint_target() -> None:

  """

  Select bones used as targets for the currently selected bones

  """

  ...

def select_grouped(*args, extend: bool = False, type: str = 'COLLECTION') -> None:

  """

  Select all visible bones grouped by similar properties

  """

  ...

def select_hierarchy(*args, direction: str = 'PARENT', extend: bool = False) -> None:

  """

  Select immediate parent/children of selected bones

  """

  ...

def select_linked() -> None:

  """

  Select all bones linked by parent/child connections to the current selection

  """

  ...

def select_linked_pick(*args, extend: bool = False) -> None:

  """

  Select bones linked by parent/child connections under the mouse cursor

  """

  ...

def select_mirror(*args, only_active: bool = False, extend: bool = False) -> None:

  """

  Mirror the bone selection

  """

  ...

def select_parent() -> None:

  """

  Select bones that are parents of the currently selected bones

  """

  ...

def selection_set_add() -> None:

  """

  Create a new empty Selection Set

  """

  ...

def selection_set_add_and_assign() -> None:

  """

  Create a new Selection Set with the currently selected bones

  """

  ...

def selection_set_assign() -> None:

  """

  Add selected bones to Selection Set

  """

  ...

def selection_set_copy() -> None:

  """

  Copy the selected Selection Set(s) to the clipboard

  """

  ...

def selection_set_delete_all() -> None:

  """

  Remove all Selection Sets from this Armature

  """

  ...

def selection_set_deselect() -> None:

  """

  Remove Selection Set bones from current selection

  """

  ...

def selection_set_move(*args, direction: str = 'UP') -> None:

  """

  Move the active Selection Set up/down the list of sets

  """

  ...

def selection_set_paste() -> None:

  """

  Add new Selection Set(s) from the clipboard

  """

  ...

def selection_set_remove() -> None:

  """

  Remove a Selection Set from this Armature

  """

  ...

def selection_set_remove_bones() -> None:

  """

  Remove the selected bones from all Selection Sets

  """

  ...

def selection_set_select(*args, selection_set_index: int = -1) -> None:

  """

  Select the bones from this Selection Set

  """

  ...

def selection_set_unassign() -> None:

  """

  Remove selected bones from Selection Set

  """

  ...

def transforms_clear() -> None:

  """

  Reset location, rotation, and scaling of selected bones to their default values

  """

  ...

def user_transforms_clear(*args, only_selected: bool = True) -> None:

  """

  Reset pose bone transforms to keyframed state

  """

  ...

def visual_transform_apply() -> None:

  """

  Apply final constrained position of pose bones to their transform

  """

  ...
