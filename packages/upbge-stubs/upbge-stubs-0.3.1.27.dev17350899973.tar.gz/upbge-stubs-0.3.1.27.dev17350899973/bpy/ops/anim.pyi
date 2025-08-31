"""


Anim Operators
**************

:func:`change_frame`

:func:`channel_select_keys`

:func:`channel_view_pick`

:func:`channels_bake`

:func:`channels_clean_empty`

:func:`channels_click`

:func:`channels_collapse`

:func:`channels_delete`

:func:`channels_editable_toggle`

:func:`channels_expand`

:func:`channels_fcurves_enable`

:func:`channels_group`

:func:`channels_move`

:func:`channels_rename`

:func:`channels_select_all`

:func:`channels_select_box`

:func:`channels_select_filter`

:func:`channels_setting_disable`

:func:`channels_setting_enable`

:func:`channels_setting_toggle`

:func:`channels_ungroup`

:func:`channels_view_selected`

:func:`clear_useless_actions`

:func:`convert_legacy_action`

:func:`copy_driver_button`

:func:`driver_button_add`

:func:`driver_button_edit`

:func:`driver_button_remove`

:func:`end_frame_set`

:func:`keyframe_clear_button`

:func:`keyframe_clear_v3d`

:func:`keyframe_clear_vse`

:func:`keyframe_delete`

:func:`keyframe_delete_button`

:func:`keyframe_delete_by_name`

:func:`keyframe_delete_v3d`

:func:`keyframe_delete_vse`

:func:`keyframe_insert`

:func:`keyframe_insert_button`

:func:`keyframe_insert_by_name`

:func:`keyframe_insert_menu`

:func:`keying_set_active_set`

:func:`keying_set_add`

:func:`keying_set_export`

:func:`keying_set_path_add`

:func:`keying_set_path_remove`

:func:`keying_set_remove`

:func:`keyingset_button_add`

:func:`keyingset_button_remove`

:func:`merge_animation`

:func:`paste_driver_button`

:func:`previewrange_clear`

:func:`previewrange_set`

:func:`scene_range_frame`

:func:`separate_slots`

:func:`slot_channels_move_to_new_action`

:func:`slot_new_for_id`

:func:`slot_unassign_from_constraint`

:func:`slot_unassign_from_id`

:func:`slot_unassign_from_nla_strip`

:func:`start_frame_set`

:func:`update_animated_transform_constraints`

:func:`view_curve_in_graph_editor`

"""

import typing

def change_frame(*args, frame: float = 0.0, snap: bool = False, seq_solo_preview: bool = False) -> None:

  """

  Interactively change the current frame number

  """

  ...

def channel_select_keys(*args, extend: bool = False) -> None:

  """

  Select all keyframes of channel under mouse

  """

  ...

def channel_view_pick(*args, include_handles: bool = True, use_preview_range: bool = True) -> None:

  """

  Reset viewable area to show the channel under the cursor

  """

  ...

def channels_bake(*args, range: typing.Tuple[int, int] = (0, 0), step: float = 1.0, remove_outside_range: bool = False, interpolation_type: str = 'BEZIER', bake_modifiers: bool = True) -> None:

  """

  Create keyframes following the current shape of F-Curves of selected channels

  """

  ...

def channels_clean_empty() -> None:

  """

  Delete all empty animation data containers from visible data-blocks

  """

  ...

def channels_click(*args, extend: bool = False, extend_range: bool = False, children_only: bool = False) -> None:

  """

  Handle mouse clicks over animation channels

  """

  ...

def channels_collapse(*args, all: bool = True) -> None:

  """

  Collapse (close) all selected expandable animation channels

  """

  ...

def channels_delete() -> None:

  """

  Delete all selected animation channels

  """

  ...

def channels_editable_toggle(*args, mode: str = 'TOGGLE', type: str = 'PROTECT') -> None:

  """

  Toggle editability of selected channels

  """

  ...

def channels_expand(*args, all: bool = True) -> None:

  """

  Expand (open) all selected expandable animation channels

  """

  ...

def channels_fcurves_enable() -> None:

  """

  Clear 'disabled' tag from all F-Curves to get broken F-Curves working again

  """

  ...

def channels_group(*args, name: str = 'New Group') -> None:

  """

  Add selected F-Curves to a new group

  """

  ...

def channels_move(*args, direction: str = 'DOWN') -> None:

  """

  Rearrange selected animation channels

  """

  ...

def channels_rename() -> None:

  """

  Rename animation channel under mouse

  """

  ...

def channels_select_all(*args, action: str = 'TOGGLE') -> None:

  """

  Toggle selection of all animation channels

  """

  ...

def channels_select_box(*args, xmin: int = 0, xmax: int = 0, ymin: int = 0, ymax: int = 0, wait_for_input: bool = True, deselect: bool = False, extend: bool = True) -> None:

  """

  Select all animation channels within the specified region

  """

  ...

def channels_select_filter() -> None:

  """

  Start entering text which filters the set of channels shown to only include those with matching names

  """

  ...

def channels_setting_disable(*args, mode: str = 'DISABLE', type: str = 'PROTECT') -> None:

  """

  Disable specified setting on all selected animation channels

  """

  ...

def channels_setting_enable(*args, mode: str = 'ENABLE', type: str = 'PROTECT') -> None:

  """

  Enable specified setting on all selected animation channels

  """

  ...

def channels_setting_toggle(*args, mode: str = 'TOGGLE', type: str = 'PROTECT') -> None:

  """

  Toggle specified setting on all selected animation channels

  """

  ...

def channels_ungroup() -> None:

  """

  Remove selected F-Curves from their current groups

  """

  ...

def channels_view_selected(*args, include_handles: bool = True, use_preview_range: bool = True) -> None:

  """

  Reset viewable area to show the selected channels

  """

  ...

def clear_useless_actions(*args, only_unused: bool = True) -> None:

  """

  Mark actions with no F-Curves for deletion after save and reload of file preserving "action libraries"

  """

  ...

def convert_legacy_action() -> None:

  """

  Convert a legacy Action to a layered Action on the active object

  """

  ...

def copy_driver_button() -> None:

  """

  Copy the driver for the highlighted button

  """

  ...

def driver_button_add() -> None:

  """

  Add driver for the property under the cursor

  """

  ...

def driver_button_edit() -> None:

  """

  Edit the drivers for the connected property represented by the highlighted button

  """

  ...

def driver_button_remove(*args, all: bool = True) -> None:

  """

  Remove the driver(s) for the connected property(s) represented by the highlighted button

  """

  ...

def end_frame_set() -> None:

  """

  Set the current frame as the preview or scene end frame

  """

  ...

def keyframe_clear_button(*args, all: bool = True) -> None:

  """

  Clear all keyframes on the currently active property

  """

  ...

def keyframe_clear_v3d(*args, confirm: bool = True) -> None:

  """

  Remove all keyframe animation for selected objects

  """

  ...

def keyframe_clear_vse(*args, confirm: bool = True) -> None:

  """

  Remove all keyframe animation for selected strips

  """

  ...

def keyframe_delete(*args, type: str = 'DEFAULT') -> None:

  """

  Delete keyframes on the current frame for all properties in the specified Keying Set

  """

  ...

def keyframe_delete_button(*args, all: bool = True) -> None:

  """

  Delete current keyframe of current UI-active property

  """

  ...

def keyframe_delete_by_name(*args, type: str = '') -> None:

  """

  Alternate access to 'Delete Keyframe' for keymaps to use

  """

  ...

def keyframe_delete_v3d(*args, confirm: bool = True) -> None:

  """

  Remove keyframes on current frame for selected objects and bones

  """

  ...

def keyframe_delete_vse(*args, confirm: bool = True) -> None:

  """

  Remove keyframes on current frame for selected strips

  """

  ...

def keyframe_insert(*args, type: str = 'DEFAULT') -> None:

  """

  Insert keyframes on the current frame using either the active keying set, or the user preferences if no keying set is active

  """

  ...

def keyframe_insert_button(*args, all: bool = True) -> None:

  """

  Insert a keyframe for current UI-active property

  """

  ...

def keyframe_insert_by_name(*args, type: str = '') -> None:

  """

  Alternate access to 'Insert Keyframe' for keymaps to use

  """

  ...

def keyframe_insert_menu(*args, type: str = 'DEFAULT', always_prompt: bool = False) -> None:

  """

  Insert Keyframes for specified Keying Set, with menu of available Keying Sets if undefined

  """

  ...

def keying_set_active_set(*args, type: str = 'DEFAULT') -> None:

  """

  Set a new active keying set

  """

  ...

def keying_set_add() -> None:

  """

  Add a new (empty) keying set to the active Scene

  """

  ...

def keying_set_export(*args, filepath: str = '', filter_folder: bool = True, filter_text: bool = True, filter_python: bool = True) -> None:

  """

  Export Keying Set to a Python script

  """

  ...

def keying_set_path_add() -> None:

  """

  Add empty path to active keying set

  """

  ...

def keying_set_path_remove() -> None:

  """

  Remove active Path from active keying set

  """

  ...

def keying_set_remove() -> None:

  """

  Remove the active keying set

  """

  ...

def keyingset_button_add(*args, all: bool = True) -> None:

  """

  Add current UI-active property to current keying set

  """

  ...

def keyingset_button_remove() -> None:

  """

  Remove current UI-active property from current keying set

  """

  ...

def merge_animation() -> None:

  """

  Merge the animation of the selected objects into the action of the active object. Actions are not deleted by this, but might end up with zero users

  """

  ...

def paste_driver_button() -> None:

  """

  Paste the driver in the internal clipboard to the highlighted button

  """

  ...

def previewrange_clear() -> None:

  """

  Clear preview range

  """

  ...

def previewrange_set(*args, xmin: int = 0, xmax: int = 0, ymin: int = 0, ymax: int = 0, wait_for_input: bool = True) -> None:

  """

  Interactively define frame range used for playback

  """

  ...

def scene_range_frame() -> None:

  """

  Reset the horizontal view to the current scene frame range, taking the preview range into account if it is active

  """

  ...

def separate_slots() -> None:

  """

  Move all slots of the action on the active object into newly created, separate actions. All users of those slots will be reassigned to the new actions. The current action won't be deleted but will be empty and might end up having zero users

  """

  ...

def slot_channels_move_to_new_action() -> None:

  """

  Move the selected slots into a newly created action

  """

  ...

def slot_new_for_id() -> None:

  """

  Create a new action slot for this data-block, to hold its animation

  """

  ...

def slot_unassign_from_constraint() -> None:

  """

  Un-assign the action slot from this constraint

  """

  ...

def slot_unassign_from_id() -> None:

  """

  Un-assign the action slot, effectively making this data-block non-animated

  """

  ...

def slot_unassign_from_nla_strip() -> None:

  """

  Un-assign the action slot from this NLA strip, effectively making it non-animated

  """

  ...

def start_frame_set() -> None:

  """

  Set the current frame as the preview or scene start frame

  """

  ...

def update_animated_transform_constraints(*args, use_convert_to_radians: bool = True) -> None:

  """

  Update f-curves/drivers affecting Transform constraints (use it with files from 2.70 and earlier)

  """

  ...

def view_curve_in_graph_editor(*args, all: bool = False, isolate: bool = False) -> None:

  """

  Frame the property under the cursor in the Graph Editor

  """

  ...
