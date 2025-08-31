"""


Node Operators
**************

:func:`activate_viewer`

:func:`add_closure_zone`

:func:`add_collection`

:func:`add_color`

:func:`add_empty_group`

:func:`add_foreach_geometry_element_zone`

:func:`add_group`

:func:`add_group_asset`

:func:`add_group_input_node`

:func:`add_image`

:func:`add_import_node`

:func:`add_mask`

:func:`add_material`

:func:`add_node`

:func:`add_object`

:func:`add_repeat_zone`

:func:`add_reroute`

:func:`add_simulation_zone`

:func:`attach`

:func:`backimage_fit`

:func:`backimage_move`

:func:`backimage_sample`

:func:`backimage_zoom`

:func:`bake_node_item_add`

:func:`bake_node_item_move`

:func:`bake_node_item_remove`

:func:`capture_attribute_item_add`

:func:`capture_attribute_item_move`

:func:`capture_attribute_item_remove`

:func:`clear_viewer_border`

:func:`clipboard_copy`

:func:`clipboard_paste`

:func:`closure_input_item_add`

:func:`closure_input_item_move`

:func:`closure_input_item_remove`

:func:`closure_output_item_add`

:func:`closure_output_item_move`

:func:`closure_output_item_remove`

:func:`collapse_hide_unused_toggle`

:func:`combine_bundle_item_add`

:func:`combine_bundle_item_move`

:func:`combine_bundle_item_remove`

:func:`connect_to_output`

:func:`cryptomatte_layer_add`

:func:`cryptomatte_layer_remove`

:func:`deactivate_viewer`

:func:`default_group_width_set`

:func:`delete`

:func:`delete_reconnect`

:func:`detach`

:func:`detach_translate_attach`

:func:`duplicate`

:func:`duplicate_move`

:func:`duplicate_move_keep_inputs`

:func:`duplicate_move_linked`

:func:`enum_definition_item_add`

:func:`enum_definition_item_move`

:func:`enum_definition_item_remove`

:func:`evaluate_closure_input_item_add`

:func:`evaluate_closure_input_item_move`

:func:`evaluate_closure_input_item_remove`

:func:`evaluate_closure_output_item_add`

:func:`evaluate_closure_output_item_move`

:func:`evaluate_closure_output_item_remove`

:func:`file_output_item_add`

:func:`file_output_item_move`

:func:`file_output_item_remove`

:func:`find_node`

:func:`foreach_geometry_element_zone_generation_item_add`

:func:`foreach_geometry_element_zone_generation_item_move`

:func:`foreach_geometry_element_zone_generation_item_remove`

:func:`foreach_geometry_element_zone_input_item_add`

:func:`foreach_geometry_element_zone_input_item_move`

:func:`foreach_geometry_element_zone_input_item_remove`

:func:`foreach_geometry_element_zone_main_item_add`

:func:`foreach_geometry_element_zone_main_item_move`

:func:`foreach_geometry_element_zone_main_item_remove`

:func:`format_string_item_add`

:func:`format_string_item_move`

:func:`format_string_item_remove`

:func:`gltf_settings_node_operator`

:func:`group_edit`

:func:`group_insert`

:func:`group_make`

:func:`group_separate`

:func:`group_ungroup`

:func:`hide_socket_toggle`

:func:`hide_toggle`

:func:`index_switch_item_add`

:func:`index_switch_item_remove`

:func:`insert_offset`

:func:`interface_item_duplicate`

:func:`interface_item_make_panel_toggle`

:func:`interface_item_new`

:func:`interface_item_remove`

:func:`interface_item_unlink_panel_toggle`

:func:`join`

:func:`join_named`

:func:`link`

:func:`link_make`

:func:`link_viewer`

:func:`links_cut`

:func:`links_detach`

:func:`links_mute`

:func:`move_detach_links`

:func:`move_detach_links_release`

:func:`mute_toggle`

:func:`new_compositing_node_group`

:func:`new_geometry_node_group_assign`

:func:`new_geometry_node_group_tool`

:func:`new_geometry_nodes_modifier`

:func:`new_node_tree`

:func:`node_color_preset_add`

:func:`node_copy_color`

:func:`options_toggle`

:func:`parent_set`

:func:`preview_toggle`

:func:`read_viewlayers`

:func:`render_changed`

:func:`repeat_zone_item_add`

:func:`repeat_zone_item_move`

:func:`repeat_zone_item_remove`

:func:`resize`

:func:`select`

:func:`select_all`

:func:`select_box`

:func:`select_circle`

:func:`select_grouped`

:func:`select_lasso`

:func:`select_link_viewer`

:func:`select_linked_from`

:func:`select_linked_to`

:func:`select_same_type_step`

:func:`separate_bundle_item_add`

:func:`separate_bundle_item_move`

:func:`separate_bundle_item_remove`

:func:`shader_script_update`

:func:`simulation_zone_item_add`

:func:`simulation_zone_item_move`

:func:`simulation_zone_item_remove`

:func:`sockets_sync`

:func:`translate_attach`

:func:`translate_attach_remove_on_cancel`

:func:`tree_path_parent`

:func:`view_all`

:func:`view_selected`

:func:`viewer_border`

:func:`viewer_shortcut_get`

:func:`viewer_shortcut_set`

"""

import typing

def activate_viewer() -> None:

  """

  Activate selected viewer node in compositor and geometry nodes

  """

  ...

def add_closure_zone(*args, use_transform: bool = False, settings: typing.Union[typing.Sequence[NodeSetting], typing.Mapping[str, NodeSetting], bpy.types.bpy_prop_collection] = None, offset: typing.Tuple[float, float] = (150.0, 0.0)) -> None:

  """

  Add a Closure zone

  """

  ...

def add_collection(*args, name: str = '', session_uid: int = 0) -> None:

  """

  Add a collection info node to the current node editor

  """

  ...

def add_color(*args, color: typing.Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0), gamma: bool = False, has_alpha: bool = False) -> None:

  """

  Add a color node to the current node editor

  """

  ...

def add_empty_group(*args, use_transform: bool = False, settings: typing.Union[typing.Sequence[NodeSetting], typing.Mapping[str, NodeSetting], bpy.types.bpy_prop_collection] = None) -> None:

  """

  Add a group node with an empty group

  """

  ...

def add_foreach_geometry_element_zone(*args, use_transform: bool = False, settings: typing.Union[typing.Sequence[NodeSetting], typing.Mapping[str, NodeSetting], bpy.types.bpy_prop_collection] = None, offset: typing.Tuple[float, float] = (150.0, 0.0)) -> None:

  """

  Add a For Each Geometry Element zone that allows executing nodes e.g. for each vertex separately

  """

  ...

def add_group(*args, name: str = '', session_uid: int = 0, show_datablock_in_node: bool = True) -> None:

  """

  Add an existing node group to the current node editor

  """

  ...

def add_group_asset(*args, asset_library_type: str = 'LOCAL', asset_library_identifier: str = '', relative_asset_identifier: str = '') -> None:

  """

  Add a node group asset to the active node tree

  """

  ...

def add_group_input_node(*args, socket_identifier: str = '', panel_identifier: int = 0) -> None:

  """

  Add a Group Input node with selected sockets to the current node editor

  """

  ...

def add_image(*args, filepath: str = '', directory: str = '', files: typing.Union[typing.Sequence[OperatorFileListElement], typing.Mapping[str, OperatorFileListElement], bpy.types.bpy_prop_collection] = None, hide_props_region: bool = True, check_existing: bool = False, filter_blender: bool = False, filter_backup: bool = False, filter_image: bool = True, filter_movie: bool = True, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 9, relative_path: bool = True, show_multiview: bool = False, use_multiview: bool = False, display_type: str = 'DEFAULT', sort_method: str = '', name: str = '', session_uid: int = 0) -> None:

  """

  Add a image/movie file as node to the current node editor

  """

  ...

def add_import_node(*args, directory: str = '', files: typing.Union[typing.Sequence[OperatorFileListElement], typing.Mapping[str, OperatorFileListElement], bpy.types.bpy_prop_collection] = None) -> None:

  """

  Add an import node to the node tree

  """

  ...

def add_mask(*args, name: str = '', session_uid: int = 0) -> None:

  """

  Add a mask node to the current node editor

  """

  ...

def add_material(*args, name: str = '', session_uid: int = 0) -> None:

  """

  Add a material node to the current node editor

  """

  ...

def add_node(*args, use_transform: bool = False, settings: typing.Union[typing.Sequence[NodeSetting], typing.Mapping[str, NodeSetting], bpy.types.bpy_prop_collection] = None, type: str = '', visible_output: str = '') -> None:

  """

  Add a node to the active tree

  """

  ...

def add_object(*args, name: str = '', session_uid: int = 0) -> None:

  """

  Add an object info node to the current node editor

  """

  ...

def add_repeat_zone(*args, use_transform: bool = False, settings: typing.Union[typing.Sequence[NodeSetting], typing.Mapping[str, NodeSetting], bpy.types.bpy_prop_collection] = None, offset: typing.Tuple[float, float] = (150.0, 0.0)) -> None:

  """

  Add a repeat zone that allows executing nodes a dynamic number of times

  """

  ...

def add_reroute(*args, path: typing.Union[typing.Sequence[OperatorMousePath], typing.Mapping[str, OperatorMousePath], bpy.types.bpy_prop_collection] = None, cursor: int = 11) -> None:

  """

  Add a reroute node

  """

  ...

def add_simulation_zone(*args, use_transform: bool = False, settings: typing.Union[typing.Sequence[NodeSetting], typing.Mapping[str, NodeSetting], bpy.types.bpy_prop_collection] = None, offset: typing.Tuple[float, float] = (150.0, 0.0)) -> None:

  """

  Add simulation zone input and output nodes to the active tree

  """

  ...

def attach() -> None:

  """

  Attach active node to a frame

  """

  ...

def backimage_fit() -> None:

  """

  Fit the background image to the view

  """

  ...

def backimage_move() -> None:

  """

  Move node backdrop

  """

  ...

def backimage_sample() -> None:

  """

  Use mouse to sample background image

  """

  ...

def backimage_zoom(*args, factor: float = 1.2) -> None:

  """

  Zoom in/out the background image

  """

  ...

def bake_node_item_add() -> None:

  """

  Add item below active item

  """

  ...

def bake_node_item_move(*args, direction: str = 'UP') -> None:

  """

  Move active item

  """

  ...

def bake_node_item_remove() -> None:

  """

  Remove active item

  """

  ...

def capture_attribute_item_add() -> None:

  """

  Add item below active item

  """

  ...

def capture_attribute_item_move(*args, direction: str = 'UP') -> None:

  """

  Move active item

  """

  ...

def capture_attribute_item_remove() -> None:

  """

  Remove active item

  """

  ...

def clear_viewer_border() -> None:

  """

  Clear the boundaries for viewer operations

  """

  ...

def clipboard_copy() -> None:

  """

  Copy the selected nodes to the internal clipboard

  """

  ...

def clipboard_paste(*args, offset: typing.Tuple[float, float] = (0.0, 0.0)) -> None:

  """

  Paste nodes from the internal clipboard to the active node tree

  """

  ...

def closure_input_item_add() -> None:

  """

  Add item below active item

  """

  ...

def closure_input_item_move(*args, direction: str = 'UP') -> None:

  """

  Move active item

  """

  ...

def closure_input_item_remove() -> None:

  """

  Remove active item

  """

  ...

def closure_output_item_add() -> None:

  """

  Add item below active item

  """

  ...

def closure_output_item_move(*args, direction: str = 'UP') -> None:

  """

  Move active item

  """

  ...

def closure_output_item_remove() -> None:

  """

  Remove active item

  """

  ...

def collapse_hide_unused_toggle() -> None:

  """

  Toggle collapsed nodes and hide unused sockets

  """

  ...

def combine_bundle_item_add() -> None:

  """

  Add item below active item

  """

  ...

def combine_bundle_item_move(*args, direction: str = 'UP') -> None:

  """

  Move active item

  """

  ...

def combine_bundle_item_remove() -> None:

  """

  Remove active item

  """

  ...

def connect_to_output(*args, run_in_geometry_nodes: bool = True) -> None:

  """

  Connect active node to the active output node of the node tree

  """

  ...

def cryptomatte_layer_add() -> None:

  """

  Add a new input layer to a Cryptomatte node

  """

  ...

def cryptomatte_layer_remove() -> None:

  """

  Remove layer from a Cryptomatte node

  """

  ...

def deactivate_viewer() -> None:

  """

  Deactivate selected viewer node in geometry nodes

  """

  ...

def default_group_width_set() -> None:

  """

  Set the width based on the parent group node in the current context

  """

  ...

def delete() -> None:

  """

  Remove selected nodes

  """

  ...

def delete_reconnect() -> None:

  """

  Remove nodes and reconnect nodes as if deletion was muted

  """

  ...

def detach() -> None:

  """

  Detach selected nodes from parents

  """

  ...

def detach_translate_attach(*args, NODE_OT_detach: NODE_OT_detach = None, TRANSFORM_OT_translate: TRANSFORM_OT_translate = None, NODE_OT_attach: NODE_OT_attach = None) -> None:

  """

  Detach nodes, move and attach to frame

  """

  ...

def duplicate(*args, keep_inputs: bool = False, linked: bool = True) -> None:

  """

  Duplicate selected nodes

  """

  ...

def duplicate_move(*args, NODE_OT_duplicate: NODE_OT_duplicate = None, NODE_OT_translate_attach: NODE_OT_translate_attach = None) -> None:

  """

  Duplicate selected nodes and move them

  """

  ...

def duplicate_move_keep_inputs(*args, NODE_OT_duplicate: NODE_OT_duplicate = None, NODE_OT_translate_attach: NODE_OT_translate_attach = None) -> None:

  """

  Duplicate selected nodes keeping input links and move them

  """

  ...

def duplicate_move_linked(*args, NODE_OT_duplicate: NODE_OT_duplicate = None, NODE_OT_translate_attach: NODE_OT_translate_attach = None) -> None:

  """

  Duplicate selected nodes, but not their node trees, and move them

  """

  ...

def enum_definition_item_add() -> None:

  """

  Add item below active item

  """

  ...

def enum_definition_item_move(*args, direction: str = 'UP') -> None:

  """

  Move active item

  """

  ...

def enum_definition_item_remove() -> None:

  """

  Remove active item

  """

  ...

def evaluate_closure_input_item_add() -> None:

  """

  Add item below active item

  """

  ...

def evaluate_closure_input_item_move(*args, direction: str = 'UP') -> None:

  """

  Move active item

  """

  ...

def evaluate_closure_input_item_remove() -> None:

  """

  Remove active item

  """

  ...

def evaluate_closure_output_item_add() -> None:

  """

  Add item below active item

  """

  ...

def evaluate_closure_output_item_move(*args, direction: str = 'UP') -> None:

  """

  Move active item

  """

  ...

def evaluate_closure_output_item_remove() -> None:

  """

  Remove active item

  """

  ...

def file_output_item_add() -> None:

  """

  Add item below active item

  """

  ...

def file_output_item_move(*args, direction: str = 'UP') -> None:

  """

  Move active item

  """

  ...

def file_output_item_remove() -> None:

  """

  Remove active item

  """

  ...

def find_node() -> None:

  """

  Search for a node by name and focus and select it

  """

  ...

def foreach_geometry_element_zone_generation_item_add() -> None:

  """

  Add item below active item

  """

  ...

def foreach_geometry_element_zone_generation_item_move(*args, direction: str = 'UP') -> None:

  """

  Move active item

  """

  ...

def foreach_geometry_element_zone_generation_item_remove() -> None:

  """

  Remove active item

  """

  ...

def foreach_geometry_element_zone_input_item_add() -> None:

  """

  Add item below active item

  """

  ...

def foreach_geometry_element_zone_input_item_move(*args, direction: str = 'UP') -> None:

  """

  Move active item

  """

  ...

def foreach_geometry_element_zone_input_item_remove() -> None:

  """

  Remove active item

  """

  ...

def foreach_geometry_element_zone_main_item_add() -> None:

  """

  Add item below active item

  """

  ...

def foreach_geometry_element_zone_main_item_move(*args, direction: str = 'UP') -> None:

  """

  Move active item

  """

  ...

def foreach_geometry_element_zone_main_item_remove() -> None:

  """

  Remove active item

  """

  ...

def format_string_item_add() -> None:

  """

  Add item below active item

  """

  ...

def format_string_item_move(*args, direction: str = 'UP') -> None:

  """

  Move active item

  """

  ...

def format_string_item_remove() -> None:

  """

  Remove active item

  """

  ...

def gltf_settings_node_operator() -> None:

  """

  Add a node to the active tree for glTF export

  """

  ...

def group_edit(*args, exit: bool = False) -> None:

  """

  Edit node group

  """

  ...

def group_insert() -> None:

  """

  Insert selected nodes into a node group

  """

  ...

def group_make() -> None:

  """

  Make group from selected nodes

  """

  ...

def group_separate(*args, type: str = 'COPY') -> None:

  """

  Separate selected nodes from the node group

  """

  ...

def group_ungroup() -> None:

  """

  Ungroup selected nodes

  """

  ...

def hide_socket_toggle() -> None:

  """

  Toggle unused node socket display

  """

  ...

def hide_toggle() -> None:

  """

  Toggle collapsing of selected nodes

  """

  ...

def index_switch_item_add() -> None:

  """

  Add bake item

  """

  ...

def index_switch_item_remove(*args, index: int = 0) -> None:

  """

  Remove an item from the index switch

  """

  ...

def insert_offset() -> None:

  """

  Automatically offset nodes on insertion

  """

  ...

def interface_item_duplicate() -> None:

  """

  Add a copy of the active item to the interface

  """

  ...

def interface_item_make_panel_toggle() -> None:

  """

  Make the active boolean socket a toggle for its parent panel

  """

  ...

def interface_item_new(*args, item_type: str = '') -> None:

  """

  Add a new item to the interface

  """

  ...

def interface_item_remove() -> None:

  """

  Remove active item from the interface

  """

  ...

def interface_item_unlink_panel_toggle() -> None:

  """

  Make the panel toggle a stand-alone socket

  """

  ...

def join() -> None:

  """

  Attach selected nodes to a new common frame

  """

  ...

def join_named(*args, NODE_OT_join: NODE_OT_join = None, WM_OT_call_panel: WM_OT_call_panel = None) -> None:

  """

  Create a new frame node around the selected nodes and name it immediately

  """

  ...

def link(*args, detach: bool = False, drag_start: typing.Tuple[float, float] = (0.0, 0.0), inside_padding: float = 2.0, outside_padding: float = 0.0, speed_ramp: float = 1.0, max_speed: float = 26.0, delay: float = 0.5, zoom_influence: float = 0.5) -> None:

  """

  Use the mouse to create a link between two nodes

  """

  ...

def link_make(*args, replace: bool = False) -> None:

  """

  Make a link between selected output and input sockets

  """

  ...

def link_viewer() -> None:

  """

  Link to viewer node

  """

  ...

def links_cut(*args, path: typing.Union[typing.Sequence[OperatorMousePath], typing.Mapping[str, OperatorMousePath], bpy.types.bpy_prop_collection] = None, cursor: int = 15) -> None:

  """

  Use the mouse to cut (remove) some links

  """

  ...

def links_detach() -> None:

  """

  Remove all links to selected nodes, and try to connect neighbor nodes together

  """

  ...

def links_mute(*args, path: typing.Union[typing.Sequence[OperatorMousePath], typing.Mapping[str, OperatorMousePath], bpy.types.bpy_prop_collection] = None, cursor: int = 39) -> None:

  """

  Use the mouse to mute links

  """

  ...

def move_detach_links(*args, NODE_OT_links_detach: NODE_OT_links_detach = None, TRANSFORM_OT_translate: TRANSFORM_OT_translate = None) -> None:

  """

  Move a node to detach links

  """

  ...

def move_detach_links_release(*args, NODE_OT_links_detach: NODE_OT_links_detach = None, NODE_OT_translate_attach: NODE_OT_translate_attach = None) -> None:

  """

  Move a node to detach links

  """

  ...

def mute_toggle() -> None:

  """

  Toggle muting of selected nodes

  """

  ...

def new_compositing_node_group(*args, name: str = 'Compositor Nodes') -> None:

  """

  Create a new compositing node group and initialize it with default nodes

  """

  ...

def new_geometry_node_group_assign() -> None:

  """

  Create a new geometry node group and assign it to the active modifier

  """

  ...

def new_geometry_node_group_tool() -> None:

  """

  Create a new geometry node group for a tool

  """

  ...

def new_geometry_nodes_modifier() -> None:

  """

  Create a new modifier with a new geometry node group

  """

  ...

def new_node_tree(*args, type: str = '', name: str = 'NodeTree') -> None:

  """

  Create a new node tree

  """

  ...

def node_color_preset_add(*args, name: str = '', remove_name: bool = False, remove_active: bool = False) -> None:

  """

  Add or remove a Node Color Preset

  """

  ...

def node_copy_color() -> None:

  """

  Copy color to all selected nodes

  """

  ...

def options_toggle() -> None:

  """

  Toggle option buttons display for selected nodes

  """

  ...

def parent_set() -> None:

  """

  Attach selected nodes

  """

  ...

def preview_toggle() -> None:

  """

  Toggle preview display for selected nodes

  """

  ...

def read_viewlayers() -> None:

  """

  Read all render layers of all used scenes

  """

  ...

def render_changed() -> None:

  """

  Render current scene, when input node's layer has been changed

  """

  ...

def repeat_zone_item_add() -> None:

  """

  Add item below active item

  """

  ...

def repeat_zone_item_move(*args, direction: str = 'UP') -> None:

  """

  Move active item

  """

  ...

def repeat_zone_item_remove() -> None:

  """

  Remove active item

  """

  ...

def resize() -> None:

  """

  Resize a node

  """

  ...

def select(*args, extend: bool = False, deselect: bool = False, toggle: bool = False, deselect_all: bool = False, select_passthrough: bool = False, location: typing.Tuple[int, int] = (0, 0), socket_select: bool = False, clear_viewer: bool = False) -> None:

  """

  Select the node under the cursor

  """

  ...

def select_all(*args, action: str = 'TOGGLE') -> None:

  """

  (De)select all nodes

  """

  ...

def select_box(*args, tweak: bool = False, xmin: int = 0, xmax: int = 0, ymin: int = 0, ymax: int = 0, wait_for_input: bool = True, mode: str = 'SET') -> None:

  """

  Use box selection to select nodes

  """

  ...

def select_circle(*args, x: int = 0, y: int = 0, radius: int = 25, wait_for_input: bool = True, mode: str = 'SET') -> None:

  """

  Use circle selection to select nodes

  """

  ...

def select_grouped(*args, extend: bool = False, type: str = 'TYPE') -> None:

  """

  Select nodes with similar properties

  """

  ...

def select_lasso(*args, tweak: bool = False, path: typing.Union[typing.Sequence[OperatorMousePath], typing.Mapping[str, OperatorMousePath], bpy.types.bpy_prop_collection] = None, use_smooth_stroke: bool = False, smooth_stroke_factor: float = 0.75, smooth_stroke_radius: int = 35, mode: str = 'SET') -> None:

  """

  Select nodes using lasso selection

  """

  ...

def select_link_viewer(*args, NODE_OT_select: NODE_OT_select = None, NODE_OT_link_viewer: NODE_OT_link_viewer = None) -> None:

  """

  Select node and link it to a viewer node

  """

  ...

def select_linked_from() -> None:

  """

  Select nodes linked from the selected ones

  """

  ...

def select_linked_to() -> None:

  """

  Select nodes linked to the selected ones

  """

  ...

def select_same_type_step(*args, prev: bool = False) -> None:

  """

  Activate and view same node type, step by step

  """

  ...

def separate_bundle_item_add() -> None:

  """

  Add item below active item

  """

  ...

def separate_bundle_item_move(*args, direction: str = 'UP') -> None:

  """

  Move active item

  """

  ...

def separate_bundle_item_remove() -> None:

  """

  Remove active item

  """

  ...

def shader_script_update() -> None:

  """

  Update shader script node with new sockets and options from the script

  """

  ...

def simulation_zone_item_add() -> None:

  """

  Add item below active item

  """

  ...

def simulation_zone_item_move(*args, direction: str = 'UP') -> None:

  """

  Move active item

  """

  ...

def simulation_zone_item_remove() -> None:

  """

  Remove active item

  """

  ...

def sockets_sync(*args, node_name: str = '') -> None:

  """

  Update sockets to match what is actually used

  """

  ...

def translate_attach(*args, TRANSFORM_OT_translate: TRANSFORM_OT_translate = None, NODE_OT_attach: NODE_OT_attach = None) -> None:

  """

  Move nodes and attach to frame

  """

  ...

def translate_attach_remove_on_cancel(*args, TRANSFORM_OT_translate: TRANSFORM_OT_translate = None, NODE_OT_attach: NODE_OT_attach = None) -> None:

  """

  Move nodes and attach to frame

  """

  ...

def tree_path_parent(*args, parent_tree_index: int = 0) -> None:

  """

  Go to parent node tree

  """

  ...

def view_all() -> None:

  """

  Resize view so you can see all nodes

  """

  ...

def view_selected() -> None:

  """

  Resize view so you can see selected nodes

  """

  ...

def viewer_border(*args, xmin: int = 0, xmax: int = 0, ymin: int = 0, ymax: int = 0, wait_for_input: bool = True) -> None:

  """

  Set the boundaries for viewer operations

  """

  ...

def viewer_shortcut_get(*args, viewer_index: int = 0) -> None:

  """

  Activate a specific compositor viewer node using 1,2,..,9 keys

  """

  ...

def viewer_shortcut_set(*args, viewer_index: int = 0) -> None:

  """

  Create a compositor viewer shortcut for the selected node by pressing ctrl+1,2,..9

  """

  ...
