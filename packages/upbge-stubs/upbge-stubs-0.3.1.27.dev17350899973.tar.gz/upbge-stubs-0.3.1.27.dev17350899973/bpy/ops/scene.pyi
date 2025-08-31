"""


Scene Operators
***************

:func:`delete`

:func:`drop_scene_asset`

:func:`freestyle_add_edge_marks_to_keying_set`

:func:`freestyle_add_face_marks_to_keying_set`

:func:`freestyle_alpha_modifier_add`

:func:`freestyle_color_modifier_add`

:func:`freestyle_fill_range_by_selection`

:func:`freestyle_geometry_modifier_add`

:func:`freestyle_lineset_add`

:func:`freestyle_lineset_copy`

:func:`freestyle_lineset_move`

:func:`freestyle_lineset_paste`

:func:`freestyle_lineset_remove`

:func:`freestyle_linestyle_new`

:func:`freestyle_modifier_copy`

:func:`freestyle_modifier_move`

:func:`freestyle_modifier_remove`

:func:`freestyle_module_add`

:func:`freestyle_module_move`

:func:`freestyle_module_open`

:func:`freestyle_module_remove`

:func:`freestyle_stroke_material_create`

:func:`freestyle_thickness_modifier_add`

:func:`gltf2_action_filter_refresh`

:func:`gpencil_brush_preset_add`

:func:`gpencil_material_preset_add`

:func:`new`

:func:`new_sequencer`

:func:`new_sequencer_scene`

:func:`render_view_add`

:func:`render_view_remove`

:func:`view_layer_add`

:func:`view_layer_add_aov`

:func:`view_layer_add_lightgroup`

:func:`view_layer_add_used_lightgroups`

:func:`view_layer_remove`

:func:`view_layer_remove_aov`

:func:`view_layer_remove_lightgroup`

:func:`view_layer_remove_unused_lightgroups`

"""

import typing

def delete() -> None:

  """

  Delete active scene

  """

  ...

def drop_scene_asset(*args, session_uid: int = 0) -> None:

  """

  Import scene and set it as the active one in the window

  """

  ...

def freestyle_add_edge_marks_to_keying_set() -> None:

  """

  Add the data paths to the Freestyle Edge Mark property of selected edges to the active keying set

  """

  ...

def freestyle_add_face_marks_to_keying_set() -> None:

  """

  Add the data paths to the Freestyle Face Mark property of selected polygons to the active keying set

  """

  ...

def freestyle_alpha_modifier_add(*args, type: str = 'ALONG_STROKE') -> None:

  """

  Add an alpha transparency modifier to the line style associated with the active lineset

  """

  ...

def freestyle_color_modifier_add(*args, type: str = 'ALONG_STROKE') -> None:

  """

  Add a line color modifier to the line style associated with the active lineset

  """

  ...

def freestyle_fill_range_by_selection(*args, type: str = 'COLOR', name: str = '') -> None:

  """

  Fill the Range Min/Max entries by the min/max distance between selected mesh objects and the source object (either a user-specified object or the active camera)

  """

  ...

def freestyle_geometry_modifier_add(*args, type: str = '2D_OFFSET') -> None:

  """

  Add a stroke geometry modifier to the line style associated with the active lineset

  """

  ...

def freestyle_lineset_add() -> None:

  """

  Add a line set into the list of line sets

  """

  ...

def freestyle_lineset_copy() -> None:

  """

  Copy the active line set to the internal clipboard

  """

  ...

def freestyle_lineset_move(*args, direction: str = 'UP') -> None:

  """

  Change the position of the active line set within the list of line sets

  """

  ...

def freestyle_lineset_paste() -> None:

  """

  Paste the internal clipboard content to the active line set

  """

  ...

def freestyle_lineset_remove() -> None:

  """

  Remove the active line set from the list of line sets

  """

  ...

def freestyle_linestyle_new() -> None:

  """

  Create a new line style, reusable by multiple line sets

  """

  ...

def freestyle_modifier_copy() -> None:

  """

  Duplicate the modifier within the list of modifiers

  """

  ...

def freestyle_modifier_move(*args, direction: str = 'UP') -> None:

  """

  Move the modifier within the list of modifiers

  """

  ...

def freestyle_modifier_remove() -> None:

  """

  Remove the modifier from the list of modifiers

  """

  ...

def freestyle_module_add() -> None:

  """

  Add a style module into the list of modules

  """

  ...

def freestyle_module_move(*args, direction: str = 'UP') -> None:

  """

  Change the position of the style module within in the list of style modules

  """

  ...

def freestyle_module_open(*args, filepath: str = '', make_internal: bool = True) -> None:

  """

  Open a style module file

  """

  ...

def freestyle_module_remove() -> None:

  """

  Remove the style module from the stack

  """

  ...

def freestyle_stroke_material_create() -> None:

  """

  Create Freestyle stroke material for testing

  """

  ...

def freestyle_thickness_modifier_add(*args, type: str = 'ALONG_STROKE') -> None:

  """

  Add a line thickness modifier to the line style associated with the active lineset

  """

  ...

def gltf2_action_filter_refresh() -> None:

  """

  Refresh list of actions

  """

  ...

def gpencil_brush_preset_add(*args, name: str = '', remove_name: bool = False, remove_active: bool = False) -> None:

  """

  Add or remove grease pencil brush preset

  """

  ...

def gpencil_material_preset_add(*args, name: str = '', remove_name: bool = False, remove_active: bool = False) -> None:

  """

  Add or remove Grease Pencil material preset

  """

  ...

def new(*args, type: str = 'NEW') -> None:

  """

  Add new scene by type

  """

  ...

def new_sequencer(*args, type: str = 'NEW') -> None:

  """

  Add new scene by type in the sequence editor and assign to active strip

  """

  ...

def new_sequencer_scene(*args, type: str = 'NEW') -> None:

  """

  Add new scene to be used by the sequencer

  """

  ...

def render_view_add() -> None:

  """

  Add a render view

  """

  ...

def render_view_remove() -> None:

  """

  Remove the selected render view

  """

  ...

def view_layer_add(*args, type: str = 'NEW') -> None:

  """

  Add a view layer

  """

  ...

def view_layer_add_aov() -> None:

  """

  Add a Shader AOV

  """

  ...

def view_layer_add_lightgroup(*args, name: str = '') -> None:

  """

  Add a Light Group

  """

  ...

def view_layer_add_used_lightgroups() -> None:

  """

  Add all used Light Groups

  """

  ...

def view_layer_remove() -> None:

  """

  Remove the selected view layer

  """

  ...

def view_layer_remove_aov() -> None:

  """

  Remove Active AOV

  """

  ...

def view_layer_remove_lightgroup() -> None:

  """

  Remove Active Lightgroup

  """

  ...

def view_layer_remove_unused_lightgroups() -> None:

  """

  Remove all unused Light Groups

  """

  ...
