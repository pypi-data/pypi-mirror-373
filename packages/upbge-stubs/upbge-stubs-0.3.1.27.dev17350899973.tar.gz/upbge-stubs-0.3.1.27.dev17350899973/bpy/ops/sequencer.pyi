"""


Sequencer Operators
*******************

:func:`add_scene_strip_from_scene_asset`

:func:`change_effect_type`

:func:`change_path`

:func:`change_scene`

:func:`connect`

:func:`copy`

:func:`crossfade_sounds`

:func:`cursor_set`

:func:`deinterlace_selected_movies`

:func:`delete`

:func:`disconnect`

:func:`duplicate`

:func:`duplicate_move`

:func:`duplicate_move_linked`

:func:`effect_strip_add`

:func:`enable_proxies`

:func:`export_subtitles`

:func:`fades_add`

:func:`fades_clear`

:func:`gap_insert`

:func:`gap_remove`

:func:`image_strip_add`

:func:`images_separate`

:func:`lock`

:func:`mask_strip_add`

:func:`meta_make`

:func:`meta_separate`

:func:`meta_toggle`

:func:`movie_strip_add`

:func:`movieclip_strip_add`

:func:`mute`

:func:`offset_clear`

:func:`paste`

:func:`preview_duplicate_move`

:func:`preview_duplicate_move_linked`

:func:`reassign_inputs`

:func:`rebuild_proxy`

:func:`refresh_all`

:func:`reload`

:func:`rename_channel`

:func:`rendersize`

:func:`retiming_add_freeze_frame_slide`

:func:`retiming_add_transition_slide`

:func:`retiming_freeze_frame_add`

:func:`retiming_key_add`

:func:`retiming_key_delete`

:func:`retiming_reset`

:func:`retiming_segment_speed_set`

:func:`retiming_show`

:func:`retiming_transition_add`

:func:`sample`

:func:`scene_frame_range_update`

:func:`scene_strip_add`

:func:`scene_strip_add_new`

:func:`select`

:func:`select_all`

:func:`select_box`

:func:`select_grouped`

:func:`select_handle`

:func:`select_handles`

:func:`select_less`

:func:`select_linked`

:func:`select_linked_pick`

:func:`select_more`

:func:`select_side`

:func:`select_side_of_frame`

:func:`set_range_to_strips`

:func:`slip`

:func:`snap`

:func:`sound_strip_add`

:func:`split`

:func:`split_multicam`

:func:`strip_color_tag_set`

:func:`strip_jump`

:func:`strip_modifier_add`

:func:`strip_modifier_copy`

:func:`strip_modifier_equalizer_redefine`

:func:`strip_modifier_move`

:func:`strip_modifier_remove`

:func:`strip_transform_clear`

:func:`strip_transform_fit`

:func:`swap`

:func:`swap_data`

:func:`swap_inputs`

:func:`text_cursor_move`

:func:`text_cursor_set`

:func:`text_delete`

:func:`text_deselect_all`

:func:`text_edit_copy`

:func:`text_edit_cut`

:func:`text_edit_mode_toggle`

:func:`text_edit_paste`

:func:`text_insert`

:func:`text_line_break`

:func:`text_select_all`

:func:`unlock`

:func:`unmute`

:func:`view_all`

:func:`view_all_preview`

:func:`view_frame`

:func:`view_ghost_border`

:func:`view_selected`

:func:`view_zoom_ratio`

"""

import typing

import mathutils

def add_scene_strip_from_scene_asset(*args, move_strips: bool = True, frame_start: int = 0, channel: int = 1, replace_sel: bool = True, overlap: bool = False, overlap_shuffle_override: bool = False, skip_locked_or_muted_channels: bool = True, asset_library_type: str = 'LOCAL', asset_library_identifier: str = '', relative_asset_identifier: str = '') -> None:

  """

  Add a scene strip from a scene asset

  """

  ...

def change_effect_type(*args, type: str = 'CROSS') -> None:

  """

  Replace effect strip with another that takes the same number of inputs

  """

  ...

def change_path(*args, filepath: str = '', directory: str = '', files: typing.Union[typing.Sequence[OperatorFileListElement], typing.Mapping[str, OperatorFileListElement], bpy.types.bpy_prop_collection] = None, hide_props_region: bool = True, check_existing: bool = False, filter_blender: bool = False, filter_backup: bool = False, filter_image: bool = False, filter_movie: bool = False, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 9, relative_path: bool = True, display_type: str = 'DEFAULT', sort_method: str = '', use_placeholders: bool = False) -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def change_scene(*args, scene: str = '') -> None:

  """

  Change Scene assigned to Strip

  """

  ...

def connect(*args, toggle: bool = True) -> None:

  """

  Link selected strips together for simplified group selection

  """

  ...

def copy() -> None:

  """

  Copy the selected strips to the internal clipboard

  """

  ...

def crossfade_sounds() -> None:

  """

  Do cross-fading volume animation of two selected sound strips

  """

  ...

def cursor_set(*args, location: mathutils.Vector = (0.0, 0.0)) -> None:

  """

  Set 2D cursor location

  """

  ...

def deinterlace_selected_movies() -> None:

  """

  Deinterlace all selected movie sources

  """

  ...

def delete(*args, delete_data: bool = False) -> None:

  """

  Delete selected strips from the sequencer

  """

  ...

def disconnect() -> None:

  """

  Unlink selected strips so that they can be selected individually

  """

  ...

def duplicate(*args, linked: bool = False) -> None:

  """

  Duplicate the selected strips

  """

  ...

def duplicate_move(*args, SEQUENCER_OT_duplicate: SEQUENCER_OT_duplicate = None, TRANSFORM_OT_seq_slide: TRANSFORM_OT_seq_slide = None) -> None:

  """

  Duplicate selected strips and move them

  """

  ...

def duplicate_move_linked(*args, SEQUENCER_OT_duplicate: SEQUENCER_OT_duplicate = None, TRANSFORM_OT_seq_slide: TRANSFORM_OT_seq_slide = None) -> None:

  """

  Duplicate selected strips, but not their data, and move them

  """

  ...

def effect_strip_add(*args, type: str = 'CROSS', move_strips: bool = True, frame_start: int = 0, length: int = 0, channel: int = 1, replace_sel: bool = True, overlap: bool = False, overlap_shuffle_override: bool = False, skip_locked_or_muted_channels: bool = True, color: mathutils.Color = (0.0, 0.0, 0.0)) -> None:

  """

  Add an effect to the sequencer, most are applied on top of existing strips

  """

  ...

def enable_proxies(*args, proxy_25: bool = False, proxy_50: bool = False, proxy_75: bool = False, proxy_100: bool = False, overwrite: bool = False) -> None:

  """

  Enable selected proxies on all selected Movie and Image strips

  """

  ...

def export_subtitles(*args, filepath: str = '', hide_props_region: bool = True, check_existing: bool = True, filter_blender: bool = False, filter_backup: bool = False, filter_image: bool = False, filter_movie: bool = False, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 8, display_type: str = 'DEFAULT', sort_method: str = '') -> None:

  """

  Export .srt file containing text strips

  """

  ...

def fades_add(*args, duration_seconds: float = 1.0, type: str = 'IN_OUT') -> None:

  """

  Adds or updates a fade animation for either visual or audio strips

  """

  ...

def fades_clear() -> None:

  """

  Removes fade animation from selected strips

  """

  ...

def gap_insert(*args, frames: int = 10) -> None:

  """

  Insert gap at current frame to first strips at the right, independent of selection or locked state of strips

  """

  ...

def gap_remove(*args, all: bool = False) -> None:

  """

  Remove gap at current frame to first strip at the right, independent of selection or locked state of strips

  """

  ...

def image_strip_add(*args, directory: str = '', files: typing.Union[typing.Sequence[OperatorFileListElement], typing.Mapping[str, OperatorFileListElement], bpy.types.bpy_prop_collection] = None, check_existing: bool = False, filter_blender: bool = False, filter_backup: bool = False, filter_image: bool = True, filter_movie: bool = False, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 9, relative_path: bool = True, show_multiview: bool = False, use_multiview: bool = False, display_type: str = 'DEFAULT', sort_method: str = '', move_strips: bool = True, frame_start: int = 0, length: int = 0, channel: int = 1, replace_sel: bool = True, overlap: bool = False, overlap_shuffle_override: bool = False, skip_locked_or_muted_channels: bool = True, fit_method: str = 'FIT', set_view_transform: bool = True, use_placeholders: bool = False, use_sequence_detection: bool = True) -> None:

  """

  Add an image or image sequence to the sequencer

  """

  ...

def images_separate(*args, length: int = 1) -> None:

  """

  On image sequence strips, it returns a strip for each image

  """

  ...

def lock() -> None:

  """

  Lock strips so they cannot be transformed

  """

  ...

def mask_strip_add(*args, move_strips: bool = True, frame_start: int = 0, channel: int = 1, replace_sel: bool = True, overlap: bool = False, overlap_shuffle_override: bool = False, skip_locked_or_muted_channels: bool = True, mask: str = '') -> None:

  """

  Add a mask strip to the sequencer

  """

  ...

def meta_make() -> None:

  """

  Group selected strips into a meta-strip

  """

  ...

def meta_separate() -> None:

  """

  Put the contents of a meta-strip back in the sequencer

  """

  ...

def meta_toggle() -> None:

  """

  Toggle a meta-strip (to edit enclosed strips)

  """

  ...

def movie_strip_add(*args, filepath: str = '', directory: str = '', files: typing.Union[typing.Sequence[OperatorFileListElement], typing.Mapping[str, OperatorFileListElement], bpy.types.bpy_prop_collection] = None, check_existing: bool = False, filter_blender: bool = False, filter_backup: bool = False, filter_image: bool = False, filter_movie: bool = True, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 9, relative_path: bool = True, show_multiview: bool = False, use_multiview: bool = False, display_type: str = 'DEFAULT', sort_method: str = '', move_strips: bool = True, frame_start: int = 0, channel: int = 1, replace_sel: bool = True, overlap: bool = False, overlap_shuffle_override: bool = False, skip_locked_or_muted_channels: bool = True, fit_method: str = 'FIT', set_view_transform: bool = True, adjust_playback_rate: bool = True, sound: bool = True, use_framerate: bool = True) -> None:

  """

  Add a movie strip to the sequencer

  """

  ...

def movieclip_strip_add(*args, move_strips: bool = True, frame_start: int = 0, channel: int = 1, replace_sel: bool = True, overlap: bool = False, overlap_shuffle_override: bool = False, skip_locked_or_muted_channels: bool = True, clip: str = '') -> None:

  """

  Add a movieclip strip to the sequencer

  """

  ...

def mute(*args, unselected: bool = False) -> None:

  """

  Mute (un)selected strips

  """

  ...

def offset_clear() -> None:

  """

  Clear strip in/out offsets from the start and end of content

  """

  ...

def paste(*args, keep_offset: bool = False) -> None:

  """

  Paste strips from the internal clipboard

  """

  ...

def preview_duplicate_move(*args, SEQUENCER_OT_duplicate: SEQUENCER_OT_duplicate = None, TRANSFORM_OT_translate: TRANSFORM_OT_translate = None) -> None:

  """

  Duplicate selected strips and move them

  """

  ...

def preview_duplicate_move_linked(*args, SEQUENCER_OT_duplicate: SEQUENCER_OT_duplicate = None, TRANSFORM_OT_translate: TRANSFORM_OT_translate = None) -> None:

  """

  Duplicate selected strips, but not their data, and move them

  """

  ...

def reassign_inputs() -> None:

  """

  Reassign the inputs for the effect strip

  """

  ...

def rebuild_proxy() -> None:

  """

  Rebuild all selected proxies and timecode indices

  """

  ...

def refresh_all() -> None:

  """

  Refresh the sequencer editor

  """

  ...

def reload(*args, adjust_length: bool = False) -> None:

  """

  Reload strips in the sequencer

  """

  ...

def rename_channel() -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def rendersize() -> None:

  """

  Set render size and aspect from active strip

  """

  ...

def retiming_add_freeze_frame_slide(*args, SEQUENCER_OT_retiming_freeze_frame_add: SEQUENCER_OT_retiming_freeze_frame_add = None, TRANSFORM_OT_seq_slide: TRANSFORM_OT_seq_slide = None) -> None:

  """

  Add freeze frame and move it

  """

  ...

def retiming_add_transition_slide(*args, SEQUENCER_OT_retiming_transition_add: SEQUENCER_OT_retiming_transition_add = None, TRANSFORM_OT_seq_slide: TRANSFORM_OT_seq_slide = None) -> None:

  """

  Add smooth transition between 2 retimed segments and change its duration

  """

  ...

def retiming_freeze_frame_add(*args, duration: int = 0) -> None:

  """

  Add freeze frame

  """

  ...

def retiming_key_add(*args, timeline_frame: int = 0) -> None:

  """

  Add retiming Key

  """

  ...

def retiming_key_delete() -> None:

  """

  Delete selected retiming keys from the sequencer

  """

  ...

def retiming_reset() -> None:

  """

  Reset strip retiming

  """

  ...

def retiming_segment_speed_set(*args, speed: float = 100.0, keep_retiming: bool = True) -> None:

  """

  Set speed of retimed segment

  """

  ...

def retiming_show() -> None:

  """

  Show retiming keys in selected strips

  """

  ...

def retiming_transition_add(*args, duration: int = 0) -> None:

  """

  Add smooth transition between 2 retimed segments

  """

  ...

def sample(*args, size: int = 1) -> None:

  """

  Use mouse to sample color in current frame

  """

  ...

def scene_frame_range_update() -> None:

  """

  Update frame range of scene strip

  """

  ...

def scene_strip_add(*args, move_strips: bool = True, frame_start: int = 0, channel: int = 1, replace_sel: bool = True, overlap: bool = False, overlap_shuffle_override: bool = False, skip_locked_or_muted_channels: bool = True, scene: str = '') -> None:

  """

  Add a strip to the sequencer using a Blender scene as a source

  """

  ...

def scene_strip_add_new(*args, move_strips: bool = True, frame_start: int = 0, channel: int = 1, replace_sel: bool = True, overlap: bool = False, overlap_shuffle_override: bool = False, skip_locked_or_muted_channels: bool = True, type: str = 'NEW') -> None:

  """

  Create a new Strip and assign a new Scene as source

  """

  ...

def select(*args, wait_to_deselect_others: bool = False, mouse_x: int = 0, mouse_y: int = 0, extend: bool = False, deselect: bool = False, toggle: bool = False, deselect_all: bool = False, select_passthrough: bool = False, center: bool = False, linked_handle: bool = False, linked_time: bool = False, side_of_frame: bool = False, ignore_connections: bool = False) -> None:

  """

  Select a strip (last selected becomes the "active strip")

  """

  ...

def select_all(*args, action: str = 'TOGGLE') -> None:

  """

  Select or deselect all strips

  """

  ...

def select_box(*args, xmin: int = 0, xmax: int = 0, ymin: int = 0, ymax: int = 0, wait_for_input: bool = True, mode: str = 'SET', tweak: bool = False, include_handles: bool = False, ignore_connections: bool = False) -> None:

  """

  Select strips using box selection

  """

  ...

def select_grouped(*args, type: str = 'TYPE', extend: bool = False, use_active_channel: bool = False) -> None:

  """

  Select all strips grouped by various properties

  """

  ...

def select_handle(*args, wait_to_deselect_others: bool = False, mouse_x: int = 0, mouse_y: int = 0, ignore_connections: bool = False) -> None:

  """

  Select strip handle

  """

  ...

def select_handles(*args, side: str = 'BOTH') -> None:

  """

  Select gizmo handles on the sides of the selected strip

  """

  ...

def select_less() -> None:

  """

  Shrink the current selection of adjacent selected strips

  """

  ...

def select_linked() -> None:

  """

  Select all strips adjacent to the current selection

  """

  ...

def select_linked_pick(*args, extend: bool = False) -> None:

  """

  Select a chain of linked strips nearest to the mouse pointer

  """

  ...

def select_more() -> None:

  """

  Select more strips adjacent to the current selection

  """

  ...

def select_side(*args, side: str = 'BOTH') -> None:

  """

  Select strips on the nominated side of the selected strips

  """

  ...

def select_side_of_frame(*args, extend: bool = False, side: str = 'LEFT') -> None:

  """

  Select strips relative to the current frame

  """

  ...

def set_range_to_strips(*args, preview: bool = False) -> None:

  """

  Set the frame range to the selected strips start and end

  """

  ...

def slip(*args, offset: float = 0.0, slip_keyframes: bool = False, use_cursor_position: bool = False, ignore_connections: bool = False) -> None:

  """

  Slip the contents of selected strips

  """

  ...

def snap(*args, frame: int = 0) -> None:

  """

  Frame where selected strips will be snapped

  """

  ...

def sound_strip_add(*args, filepath: str = '', directory: str = '', files: typing.Union[typing.Sequence[OperatorFileListElement], typing.Mapping[str, OperatorFileListElement], bpy.types.bpy_prop_collection] = None, check_existing: bool = False, filter_blender: bool = False, filter_backup: bool = False, filter_image: bool = False, filter_movie: bool = False, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = True, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 9, relative_path: bool = True, display_type: str = 'DEFAULT', sort_method: str = '', move_strips: bool = True, frame_start: int = 0, channel: int = 1, replace_sel: bool = True, overlap: bool = False, overlap_shuffle_override: bool = False, skip_locked_or_muted_channels: bool = True, cache: bool = False, mono: bool = False) -> None:

  """

  Add a sound strip to the sequencer

  """

  ...

def split(*args, frame: int = 0, channel: int = 0, type: str = 'SOFT', use_cursor_position: bool = False, side: str = 'MOUSE', ignore_selection: bool = False) -> None:

  """

  Split the selected strips in two

  """

  ...

def split_multicam(*args, camera: int = 1) -> None:

  """

  Split multicam strip and select camera

  """

  ...

def strip_color_tag_set(*args, color: str = 'NONE') -> None:

  """

  Set a color tag for the selected strips

  """

  ...

def strip_jump(*args, next: bool = True, center: bool = True) -> None:

  """

  Move frame to previous edit point

  """

  ...

def strip_modifier_add(*args, type: str = '') -> None:

  """

  Add a modifier to the strip

  """

  ...

def strip_modifier_copy(*args, type: str = 'REPLACE') -> None:

  """

  Copy modifiers of the active strip to all selected strips

  """

  ...

def strip_modifier_equalizer_redefine(*args, graphs: str = 'SIMPLE', name: str = 'Name') -> None:

  """

  Redefine equalizer graphs

  """

  ...

def strip_modifier_move(*args, name: str = 'Name', direction: str = 'UP') -> None:

  """

  Move modifier up and down in the stack

  """

  ...

def strip_modifier_remove(*args, name: str = 'Name') -> None:

  """

  Remove a modifier from the strip

  """

  ...

def strip_transform_clear(*args, property: str = 'ALL') -> None:

  """

  Reset image transformation to default value

  """

  ...

def strip_transform_fit(*args, fit_method: str = 'FIT') -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def swap(*args, side: str = 'RIGHT') -> None:

  """

  Swap active strip with strip to the right or left

  """

  ...

def swap_data() -> None:

  """

  Swap 2 sequencer strips

  """

  ...

def swap_inputs() -> None:

  """

  Swap the two inputs of the effect strip

  """

  ...

def text_cursor_move(*args, type: str = 'LINE_BEGIN', select_text: bool = False) -> None:

  """

  Move cursor in text

  """

  ...

def text_cursor_set(*args, select_text: bool = False) -> None:

  """

  Set cursor position in text

  """

  ...

def text_delete(*args, type: str = 'NEXT_OR_SELECTION') -> None:

  """

  Delete text at cursor position

  """

  ...

def text_deselect_all() -> None:

  """

  Deselect all characters

  """

  ...

def text_edit_copy() -> None:

  """

  Copy text to clipboard

  """

  ...

def text_edit_cut() -> None:

  """

  Cut text to clipboard

  """

  ...

def text_edit_mode_toggle() -> None:

  """

  Toggle text editing

  """

  ...

def text_edit_paste() -> None:

  """

  Paste text from clipboard

  """

  ...

def text_insert(*args, string: str = '') -> None:

  """

  Insert text at cursor position

  """

  ...

def text_line_break() -> None:

  """

  Insert line break at cursor position

  """

  ...

def text_select_all() -> None:

  """

  Select all characters

  """

  ...

def unlock() -> None:

  """

  Unlock strips so they can be transformed

  """

  ...

def unmute(*args, unselected: bool = False) -> None:

  """

  Unmute (un)selected strips

  """

  ...

def view_all() -> None:

  """

  View all the strips in the sequencer

  """

  ...

def view_all_preview() -> None:

  """

  Zoom preview to fit in the area

  """

  ...

def view_frame() -> None:

  """

  Move the view to the current frame

  """

  ...

def view_ghost_border(*args, xmin: int = 0, xmax: int = 0, ymin: int = 0, ymax: int = 0, wait_for_input: bool = True) -> None:

  """

  Set the boundaries of the border used for offset view

  """

  ...

def view_selected() -> None:

  """

  Zoom the sequencer on the selected strips

  """

  ...

def view_zoom_ratio(*args, ratio: float = 1.0) -> None:

  """

  Change zoom ratio of sequencer preview

  """

  ...
