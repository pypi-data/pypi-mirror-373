"""


Armature Operators
******************

:func:`align`

:func:`assign_to_collection`

:func:`autoside_names`

:func:`bone_primitive_add`

:func:`calculate_roll`

:func:`click_extrude`

:func:`collection_add`

:func:`collection_assign`

:func:`collection_create_and_assign`

:func:`collection_deselect`

:func:`collection_move`

:func:`collection_remove`

:func:`collection_remove_unused`

:func:`collection_select`

:func:`collection_show_all`

:func:`collection_unassign`

:func:`collection_unassign_named`

:func:`collection_unsolo_all`

:func:`copy_bone_color_to_selected`

:func:`delete`

:func:`dissolve`

:func:`duplicate`

:func:`duplicate_move`

:func:`extrude`

:func:`extrude_forked`

:func:`extrude_move`

:func:`fill`

:func:`flip_names`

:func:`hide`

:func:`move_to_collection`

:func:`parent_clear`

:func:`parent_set`

:func:`reveal`

:func:`roll_clear`

:func:`select_all`

:func:`select_hierarchy`

:func:`select_less`

:func:`select_linked`

:func:`select_linked_pick`

:func:`select_mirror`

:func:`select_more`

:func:`select_similar`

:func:`separate`

:func:`shortest_path_pick`

:func:`split`

:func:`subdivide`

:func:`switch_direction`

:func:`symmetrize`

"""

import typing

def align() -> None:

  """

  Align selected bones to the active bone (or to their parent)

  """

  ...

def assign_to_collection(*args, collection_index: int = -1, new_collection_name: str = '') -> None:

  """

  Assign all selected bones to a collection, or unassign them, depending on whether the active bone is already assigned or not

  """

  ...

def autoside_names(*args, type: str = 'XAXIS') -> None:

  """

  Automatically renames the selected bones according to which side of the target axis they fall on

  """

  ...

def bone_primitive_add(*args, name: str = '') -> None:

  """

  Add a new bone located at the 3D cursor

  """

  ...

def calculate_roll(*args, type: str = 'POS_X', axis_flip: bool = False, axis_only: bool = False) -> None:

  """

  Automatically fix alignment of select bones' axes

  """

  ...

def click_extrude() -> None:

  """

  Create a new bone going from the last selected joint to the mouse position

  """

  ...

def collection_add() -> None:

  """

  Add a new bone collection

  """

  ...

def collection_assign(*args, name: str = '') -> None:

  """

  Add selected bones to the chosen bone collection

  """

  ...

def collection_create_and_assign(*args, name: str = '') -> None:

  """

  Create a new bone collection and assign all selected bones

  """

  ...

def collection_deselect() -> None:

  """

  Deselect bones of active Bone Collection

  """

  ...

def collection_move(*args, direction: str = 'UP') -> None:

  """

  Change position of active Bone Collection in list of Bone collections

  """

  ...

def collection_remove() -> None:

  """

  Remove the active bone collection

  """

  ...

def collection_remove_unused() -> None:

  """

  Remove all bone collections that have neither bones nor children. This is done recursively, so bone collections that only have unused children are also removed

  """

  ...

def collection_select() -> None:

  """

  Select bones in active Bone Collection

  """

  ...

def collection_show_all() -> None:

  """

  Show all bone collections

  """

  ...

def collection_unassign(*args, name: str = '') -> None:

  """

  Remove selected bones from the active bone collection

  """

  ...

def collection_unassign_named(*args, name: str = '', bone_name: str = '') -> None:

  """

  Unassign the named bone from this bone collection

  """

  ...

def collection_unsolo_all() -> None:

  """

  Clear the 'solo' setting on all bone collections

  """

  ...

def copy_bone_color_to_selected(*args, bone_type: str = 'EDIT') -> None:

  """

  Copy the bone color of the active bone to all selected bones

  """

  ...

def delete(*args, confirm: bool = True) -> None:

  """

  Remove selected bones from the armature

  """

  ...

def dissolve() -> None:

  """

  Dissolve selected bones from the armature

  """

  ...

def duplicate(*args, do_flip_names: bool = False) -> None:

  """

  Make copies of the selected bones within the same armature

  """

  ...

def duplicate_move(*args, ARMATURE_OT_duplicate: ARMATURE_OT_duplicate = None, TRANSFORM_OT_translate: TRANSFORM_OT_translate = None) -> None:

  """

  Make copies of the selected bones within the same armature and move them

  """

  ...

def extrude(*args, forked: bool = False) -> None:

  """

  Create new bones from the selected joints

  """

  ...

def extrude_forked(*args, ARMATURE_OT_extrude: ARMATURE_OT_extrude = None, TRANSFORM_OT_translate: TRANSFORM_OT_translate = None) -> None:

  """

  Create new bones from the selected joints and move them

  """

  ...

def extrude_move(*args, ARMATURE_OT_extrude: ARMATURE_OT_extrude = None, TRANSFORM_OT_translate: TRANSFORM_OT_translate = None) -> None:

  """

  Create new bones from the selected joints and move them

  """

  ...

def fill() -> None:

  """

  Add bone between selected joint(s) and/or 3D cursor

  """

  ...

def flip_names(*args, do_strip_numbers: bool = False) -> None:

  """

  Flips (and corrects) the axis suffixes of the names of selected bones

  """

  ...

def hide(*args, unselected: bool = False) -> None:

  """

  Tag selected bones to not be visible in Edit Mode

  """

  ...

def move_to_collection(*args, collection_index: int = -1, new_collection_name: str = '') -> None:

  """

  Move bones to a collection

  """

  ...

def parent_clear(*args, type: str = 'CLEAR') -> None:

  """

  Remove the parent-child relationship between selected bones and their parents

  """

  ...

def parent_set(*args, type: str = 'CONNECTED') -> None:

  """

  Set the active bone as the parent of the selected bones

  """

  ...

def reveal(*args, select: bool = True) -> None:

  """

  Reveal all bones hidden in Edit Mode

  """

  ...

def roll_clear(*args, roll: float = 0.0) -> None:

  """

  Clear roll for selected bones

  """

  ...

def select_all(*args, action: str = 'TOGGLE') -> None:

  """

  Toggle selection status of all bones

  """

  ...

def select_hierarchy(*args, direction: str = 'PARENT', extend: bool = False) -> None:

  """

  Select immediate parent/children of selected bones

  """

  ...

def select_less() -> None:

  """

  Deselect those bones at the boundary of each selection region

  """

  ...

def select_linked(*args, all_forks: bool = False) -> None:

  """

  Select all bones linked by parent/child connections to the current selection

  """

  ...

def select_linked_pick(*args, deselect: bool = False, all_forks: bool = False) -> None:

  """

  (De)select bones linked by parent/child connections under the mouse cursor

  """

  ...

def select_mirror(*args, only_active: bool = False, extend: bool = False) -> None:

  """

  Mirror the bone selection

  """

  ...

def select_more() -> None:

  """

  Select those bones connected to the initial selection

  """

  ...

def select_similar(*args, type: str = 'LENGTH', threshold: float = 0.1) -> None:

  """

  Select similar bones by property types

  """

  ...

def separate() -> None:

  """

  Isolate selected bones into a separate armature

  """

  ...

def shortest_path_pick() -> None:

  """

  Select shortest path between two bones

  """

  ...

def split() -> None:

  """

  Split off selected bones from connected unselected bones

  """

  ...

def subdivide(*args, number_cuts: int = 1) -> None:

  """

  Break selected bones into chains of smaller bones

  """

  ...

def switch_direction() -> None:

  """

  Change the direction that a chain of bones points in (head and tail swap)

  """

  ...

def symmetrize(*args, direction: str = 'NEGATIVE_X') -> None:

  """

  Enforce symmetry, make copies of the selection or use existing

  """

  ...
