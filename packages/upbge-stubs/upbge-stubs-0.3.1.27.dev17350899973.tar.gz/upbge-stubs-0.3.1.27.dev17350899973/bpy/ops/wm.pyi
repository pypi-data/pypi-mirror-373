"""


Wm Operators
************

:func:`alembic_export`

:func:`alembic_import`

:func:`append`

:func:`batch_rename`

:func:`blend_strings_utf8_validate`

:func:`blenderplayer_start`

:func:`call_asset_shelf_popover`

:func:`call_menu`

:func:`call_menu_pie`

:func:`call_panel`

:func:`clear_recent_files`

:func:`collection_export_all`

:func:`context_collection_boolean_set`

:func:`context_cycle_array`

:func:`context_cycle_enum`

:func:`context_cycle_int`

:func:`context_menu_enum`

:func:`context_modal_mouse`

:func:`context_pie_enum`

:func:`context_scale_float`

:func:`context_scale_int`

:func:`context_set_boolean`

:func:`context_set_enum`

:func:`context_set_float`

:func:`context_set_id`

:func:`context_set_int`

:func:`context_set_string`

:func:`context_set_value`

:func:`context_toggle`

:func:`context_toggle_enum`

:func:`debug_menu`

:func:`doc_view`

:func:`doc_view_manual`

:func:`doc_view_manual_ui_context`

:func:`drop_blend_file`

:func:`drop_import_file`

:func:`fbx_import`

:func:`grease_pencil_export_pdf`

:func:`grease_pencil_export_svg`

:func:`grease_pencil_import_svg`

:func:`id_linked_relocate`

:func:`interface_theme_preset_add`

:func:`interface_theme_preset_remove`

:func:`interface_theme_preset_save`

:func:`keyconfig_preset_add`

:func:`keyconfig_preset_remove`

:func:`lib_reload`

:func:`lib_relocate`

:func:`link`

:func:`memory_statistics`

:func:`obj_export`

:func:`obj_import`

:func:`open_mainfile`

:func:`operator_cheat_sheet`

:func:`operator_defaults`

:func:`operator_pie_enum`

:func:`operator_preset_add`

:func:`operator_presets_cleanup`

:func:`owner_disable`

:func:`owner_enable`

:func:`path_open`

:func:`ply_export`

:func:`ply_import`

:func:`previews_batch_clear`

:func:`previews_batch_generate`

:func:`previews_clear`

:func:`previews_ensure`

:func:`properties_add`

:func:`properties_context_change`

:func:`properties_edit`

:func:`properties_edit_value`

:func:`properties_remove`

:func:`quit_blender`

:func:`radial_control`

:func:`read_factory_settings`

:func:`read_factory_userpref`

:func:`read_history`

:func:`read_homefile`

:func:`read_userpref`

:func:`recover_auto_save`

:func:`recover_last_session`

:func:`redraw_timer`

:func:`revert_mainfile`

:func:`save_as_mainfile`

:func:`save_as_runtime`

:func:`save_homefile`

:func:`save_mainfile`

:func:`save_userpref`

:func:`search_menu`

:func:`search_operator`

:func:`search_single_menu`

:func:`set_stereo_3d`

:func:`splash`

:func:`splash_about`

:func:`stl_export`

:func:`stl_import`

:func:`sysinfo`

:func:`tool_set_by_brush_type`

:func:`tool_set_by_id`

:func:`tool_set_by_index`

:func:`toolbar`

:func:`toolbar_fallback_pie`

:func:`toolbar_prompt`

:func:`url_open`

:func:`url_open_preset`

:func:`usd_export`

:func:`usd_import`

:func:`window_close`

:func:`window_fullscreen_toggle`

:func:`window_new`

:func:`window_new_main`

:func:`xr_navigation_fly`

:func:`xr_navigation_grab`

:func:`xr_navigation_reset`

:func:`xr_navigation_teleport`

:func:`xr_session_toggle`

"""

import typing

import mathutils

def alembic_export(*args, filepath: str = '', check_existing: bool = True, filter_blender: bool = False, filter_backup: bool = False, filter_image: bool = False, filter_movie: bool = False, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = True, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 8, display_type: str = 'DEFAULT', sort_method: str = '', filter_glob: str = '*args.abc', start: int = -2147483648, end: int = -2147483648, xsamples: int = 1, gsamples: int = 1, sh_open: float = 0.0, sh_close: float = 1.0, selected: bool = False, visible_objects_only: bool = False, flatten: bool = False, collection: str = '', uvs: bool = True, packuv: bool = True, normals: bool = True, vcolors: bool = False, orcos: bool = True, face_sets: bool = False, subdiv_schema: bool = False, apply_subdiv: bool = False, curves_as_mesh: bool = False, use_instancing: bool = True, global_scale: float = 1.0, triangulate: bool = False, quad_method: str = 'SHORTEST_DIAGONAL', ngon_method: str = 'BEAUTY', export_hair: bool = True, export_particles: bool = True, export_custom_properties: bool = True, as_background_job: bool = False, evaluation_mode: str = 'RENDER', init_scene_frame_range: bool = True) -> None:

  """

  Export current scene in an Alembic archive

  """

  ...

def alembic_import(*args, filepath: str = '', directory: str = '', files: typing.Union[typing.Sequence[OperatorFileListElement], typing.Mapping[str, OperatorFileListElement], bpy.types.bpy_prop_collection] = None, check_existing: bool = False, filter_blender: bool = False, filter_backup: bool = False, filter_image: bool = False, filter_movie: bool = False, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = True, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 8, relative_path: bool = True, display_type: str = 'DEFAULT', sort_method: str = '', filter_glob: str = '*args.abc', scale: float = 1.0, set_frame_range: bool = True, validate_meshes: bool = False, always_add_cache_reader: bool = False, is_sequence: bool = False, as_background_job: bool = False) -> None:

  """

  Load an Alembic archive

  """

  ...

def append(*args, filepath: str = '', directory: str = '', filename: str = '', files: typing.Union[typing.Sequence[OperatorFileListElement], typing.Mapping[str, OperatorFileListElement], bpy.types.bpy_prop_collection] = None, check_existing: bool = False, filter_blender: bool = True, filter_backup: bool = False, filter_image: bool = False, filter_movie: bool = False, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = True, filemode: int = 1, display_type: str = 'DEFAULT', sort_method: str = '', link: bool = False, do_reuse_local_id: bool = False, clear_asset_data: bool = False, autoselect: bool = True, active_collection: bool = True, instance_collections: bool = False, instance_object_data: bool = True, set_fake: bool = False, use_recursive: bool = True) -> None:

  """

  Append from a Library .blend file

  """

  ...

def batch_rename(*args, data_type: str = 'OBJECT', data_source: str = 'SELECT', actions: typing.Union[typing.Sequence[BatchRenameAction], typing.Mapping[str, BatchRenameAction], bpy.types.bpy_prop_collection] = None) -> None:

  """

  Rename multiple items at once

  """

  ...

def blend_strings_utf8_validate() -> None:

  """

  Check and fix all strings in current .blend file to be valid UTF-8 Unicode (needed for some old, 2.4x area files)

  """

  ...

def blenderplayer_start() -> None:

  """

  Launch the blender-player with the current blend-file

  """

  ...

def call_asset_shelf_popover(*args, name: str = '') -> None:

  """

  Open a predefined asset shelf in a popup

  """

  ...

def call_menu(*args, name: str = '') -> None:

  """

  Open a predefined menu

  """

  ...

def call_menu_pie(*args, name: str = '') -> None:

  """

  Open a predefined pie menu

  """

  ...

def call_panel(*args, name: str = '', keep_open: bool = True) -> None:

  """

  Open a predefined panel

  """

  ...

def clear_recent_files(*args, remove: str = 'ALL') -> None:

  """

  Clear the recent files list

  """

  ...

def collection_export_all() -> None:

  """

  Invoke all configured exporters for all collections

  """

  ...

def context_collection_boolean_set(*args, data_path_iter: str = '', data_path_item: str = '', type: str = 'TOGGLE') -> None:

  """

  Set boolean values for a collection of items

  """

  ...

def context_cycle_array(*args, data_path: str = '', reverse: bool = False) -> None:

  """

  Set a context array value (useful for cycling the active mesh edit mode)

  """

  ...

def context_cycle_enum(*args, data_path: str = '', reverse: bool = False, wrap: bool = False) -> None:

  """

  Toggle a context value

  """

  ...

def context_cycle_int(*args, data_path: str = '', reverse: bool = False, wrap: bool = False) -> None:

  """

  Set a context value (useful for cycling active material, shape keys, groups, etc.)

  """

  ...

def context_menu_enum(*args, data_path: str = '') -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def context_modal_mouse(*args, data_path_iter: str = '', data_path_item: str = '', header_text: str = '', input_scale: float = 0.01, invert: bool = False, initial_x: int = 0) -> None:

  """

  Adjust arbitrary values with mouse input

  """

  ...

def context_pie_enum(*args, data_path: str = '') -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def context_scale_float(*args, data_path: str = '', value: float = 1.0) -> None:

  """

  Scale a float context value

  """

  ...

def context_scale_int(*args, data_path: str = '', value: float = 1.0, always_step: bool = True) -> None:

  """

  Scale an int context value

  """

  ...

def context_set_boolean(*args, data_path: str = '', value: bool = True) -> None:

  """

  Set a context value

  """

  ...

def context_set_enum(*args, data_path: str = '', value: str = '') -> None:

  """

  Set a context value

  """

  ...

def context_set_float(*args, data_path: str = '', value: float = 0.0, relative: bool = False) -> None:

  """

  Set a context value

  """

  ...

def context_set_id(*args, data_path: str = '', value: str = '') -> None:

  """

  Set a context value to an ID data-block

  """

  ...

def context_set_int(*args, data_path: str = '', value: int = 0, relative: bool = False) -> None:

  """

  Set a context value

  """

  ...

def context_set_string(*args, data_path: str = '', value: str = '') -> None:

  """

  Set a context value

  """

  ...

def context_set_value(*args, data_path: str = '', value: str = '') -> None:

  """

  Set a context value

  """

  ...

def context_toggle(*args, data_path: str = '', module: str = '') -> None:

  """

  Toggle a context value

  """

  ...

def context_toggle_enum(*args, data_path: str = '', value_1: str = '', value_2: str = '') -> None:

  """

  Toggle a context value

  """

  ...

def debug_menu(*args, debug_value: int = 0) -> None:

  """

  Open a popup to set the debug level

  """

  ...

def doc_view(*args, doc_id: str = '') -> None:

  """

  Open online reference docs in a web browser

  """

  ...

def doc_view_manual(*args, doc_id: str = '') -> None:

  """

  Load online manual

  """

  ...

def doc_view_manual_ui_context() -> None:

  """

  View a context based online manual in a web browser

  """

  ...

def drop_blend_file(*args, filepath: str = '') -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def drop_import_file(*args, directory: str = '', files: typing.Union[typing.Sequence[OperatorFileListElement], typing.Mapping[str, OperatorFileListElement], bpy.types.bpy_prop_collection] = None) -> None:

  """

  Operator that allows file handlers to receive file drops

  """

  ...

def fbx_import(*args, filepath: str = '', directory: str = '', files: typing.Union[typing.Sequence[OperatorFileListElement], typing.Mapping[str, OperatorFileListElement], bpy.types.bpy_prop_collection] = None, check_existing: bool = False, filter_blender: bool = False, filter_backup: bool = False, filter_image: bool = False, filter_movie: bool = False, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 8, display_type: str = 'DEFAULT', sort_method: str = '', global_scale: float = 1.0, mtl_name_collision_mode: str = 'MAKE_UNIQUE', import_colors: str = 'SRGB', use_custom_normals: bool = True, use_custom_props: bool = True, use_custom_props_enum_as_string: bool = True, import_subdivision: bool = False, ignore_leaf_bones: bool = False, validate_meshes: bool = True, use_anim: bool = True, anim_offset: float = 1.0, filter_glob: str = '*args.fbx') -> None:

  """

  Import FBX file into current scene

  """

  ...

def grease_pencil_export_pdf(*args, filepath: str = '', check_existing: bool = True, filter_blender: bool = False, filter_backup: bool = False, filter_image: bool = False, filter_movie: bool = False, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = True, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 8, display_type: str = 'DEFAULT', sort_method: str = '', use_fill: bool = True, selected_object_type: str = 'ACTIVE', frame_mode: str = 'ACTIVE', stroke_sample: float = 0.0, use_uniform_width: bool = False) -> None:

  """

  Export Grease Pencil to PDF

  """

  ...

def grease_pencil_export_svg(*args, filepath: str = '', check_existing: bool = True, filter_blender: bool = False, filter_backup: bool = False, filter_image: bool = False, filter_movie: bool = False, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = True, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 8, display_type: str = 'DEFAULT', sort_method: str = '', use_fill: bool = True, selected_object_type: str = 'ACTIVE', frame_mode: str = 'ACTIVE', stroke_sample: float = 0.0, use_uniform_width: bool = False, use_clip_camera: bool = False) -> None:

  """

  Export Grease Pencil to SVG

  """

  ...

def grease_pencil_import_svg(*args, filepath: str = '', directory: str = '', files: typing.Union[typing.Sequence[OperatorFileListElement], typing.Mapping[str, OperatorFileListElement], bpy.types.bpy_prop_collection] = None, check_existing: bool = False, filter_blender: bool = False, filter_backup: bool = False, filter_image: bool = False, filter_movie: bool = False, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = True, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 8, relative_path: bool = True, display_type: str = 'DEFAULT', sort_method: str = '', resolution: int = 10, scale: float = 10.0, use_scene_unit: bool = False) -> None:

  """

  Import SVG into Grease Pencil

  """

  ...

def id_linked_relocate(*args, id_session_uid: int = 0, filepath: str = '', directory: str = '', filename: str = '', check_existing: bool = False, filter_blender: bool = True, filter_backup: bool = False, filter_image: bool = False, filter_movie: bool = False, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = True, filemode: int = 1, relative_path: bool = True, display_type: str = 'DEFAULT', sort_method: str = '', link: bool = True, do_reuse_local_id: bool = False, clear_asset_data: bool = False, autoselect: bool = True, active_collection: bool = False, instance_collections: bool = False, instance_object_data: bool = False) -> None:

  """

  Relocate a linked ID, i.e. select another ID to link, and remap its local usages to that newly linked data-block). Currently only designed as an internal operator, not directly exposed to the user

  """

  ...

def interface_theme_preset_add(*args, name: str = '', remove_name: bool = False, remove_active: bool = False) -> None:

  """

  Add a custom theme to the preset list

  """

  ...

def interface_theme_preset_remove(*args, name: str = '', remove_name: bool = False, remove_active: bool = True) -> None:

  """

  Remove a custom theme from the preset list

  """

  ...

def interface_theme_preset_save(*args, name: str = '', remove_name: bool = False, remove_active: bool = True) -> None:

  """

  Save a custom theme in the preset list

  """

  ...

def keyconfig_preset_add(*args, name: str = '', remove_name: bool = False, remove_active: bool = False) -> None:

  """

  Add a custom keymap configuration to the preset list

  """

  ...

def keyconfig_preset_remove(*args, name: str = '', remove_name: bool = False, remove_active: bool = True) -> None:

  """

  Remove a custom keymap configuration from the preset list

  """

  ...

def lib_reload(*args, library: str = '', filepath: str = '', directory: str = '', filename: str = '', hide_props_region: bool = True, check_existing: bool = False, filter_blender: bool = True, filter_backup: bool = False, filter_image: bool = False, filter_movie: bool = False, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 8, relative_path: bool = True, display_type: str = 'DEFAULT', sort_method: str = '') -> None:

  """

  Reload the given library

  """

  ...

def lib_relocate(*args, library: str = '', filepath: str = '', directory: str = '', filename: str = '', files: typing.Union[typing.Sequence[OperatorFileListElement], typing.Mapping[str, OperatorFileListElement], bpy.types.bpy_prop_collection] = None, hide_props_region: bool = True, check_existing: bool = False, filter_blender: bool = True, filter_backup: bool = False, filter_image: bool = False, filter_movie: bool = False, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 8, relative_path: bool = True, display_type: str = 'DEFAULT', sort_method: str = '') -> None:

  """

  Relocate the given library to one or several others

  """

  ...

def link(*args, filepath: str = '', directory: str = '', filename: str = '', files: typing.Union[typing.Sequence[OperatorFileListElement], typing.Mapping[str, OperatorFileListElement], bpy.types.bpy_prop_collection] = None, check_existing: bool = False, filter_blender: bool = True, filter_backup: bool = False, filter_image: bool = False, filter_movie: bool = False, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = True, filemode: int = 1, relative_path: bool = True, display_type: str = 'DEFAULT', sort_method: str = '', link: bool = True, do_reuse_local_id: bool = False, clear_asset_data: bool = False, autoselect: bool = True, active_collection: bool = True, instance_collections: bool = True, instance_object_data: bool = True) -> None:

  """

  Link from a Library .blend file

  """

  ...

def memory_statistics() -> None:

  """

  Print memory statistics to the console

  """

  ...

def obj_export(*args, filepath: str = '', check_existing: bool = True, filter_blender: bool = False, filter_backup: bool = False, filter_image: bool = False, filter_movie: bool = False, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 8, display_type: str = 'DEFAULT', sort_method: str = '', export_animation: bool = False, start_frame: int = -2147483648, end_frame: int = 2147483647, forward_axis: str = 'NEGATIVE_Z', up_axis: str = 'Y', global_scale: float = 1.0, apply_modifiers: bool = True, apply_transform: bool = True, export_eval_mode: str = 'DAG_EVAL_VIEWPORT', export_selected_objects: bool = False, export_uv: bool = True, export_normals: bool = True, export_colors: bool = False, export_materials: bool = True, export_pbr_extensions: bool = False, path_mode: str = 'AUTO', export_triangulated_mesh: bool = False, export_curves_as_nurbs: bool = False, export_object_groups: bool = False, export_material_groups: bool = False, export_vertex_groups: bool = False, export_smooth_groups: bool = False, smooth_group_bitflags: bool = False, filter_glob: str = '*args.obj;*args.mtl', collection: str = '') -> None:

  """

  Save the scene to a Wavefront OBJ file

  """

  ...

def obj_import(*args, filepath: str = '', directory: str = '', files: typing.Union[typing.Sequence[OperatorFileListElement], typing.Mapping[str, OperatorFileListElement], bpy.types.bpy_prop_collection] = None, check_existing: bool = False, filter_blender: bool = False, filter_backup: bool = False, filter_image: bool = False, filter_movie: bool = False, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 8, display_type: str = 'DEFAULT', sort_method: str = '', global_scale: float = 1.0, clamp_size: float = 0.0, forward_axis: str = 'NEGATIVE_Z', up_axis: str = 'Y', use_split_objects: bool = True, use_split_groups: bool = False, import_vertex_groups: bool = False, validate_meshes: bool = True, close_spline_loops: bool = True, collection_separator: str = '', mtl_name_collision_mode: str = 'MAKE_UNIQUE', filter_glob: str = '*args.obj;*args.mtl') -> None:

  """

  Load a Wavefront OBJ scene

  """

  ...

def open_mainfile(*args, filepath: str = '', hide_props_region: bool = True, check_existing: bool = False, filter_blender: bool = True, filter_backup: bool = False, filter_image: bool = False, filter_movie: bool = False, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 8, display_type: str = 'DEFAULT', sort_method: str = '', load_ui: bool = True, use_scripts: bool = False, display_file_selector: bool = True, state: int = 0) -> None:

  """

  Open a Blender file

  """

  ...

def operator_cheat_sheet() -> None:

  """

  List all the operators in a text-block, useful for scripting

  """

  ...

def operator_defaults() -> None:

  """

  Set the active operator to its default values

  """

  ...

def operator_pie_enum(*args, data_path: str = '', prop_string: str = '') -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def operator_preset_add(*args, name: str = '', remove_name: bool = False, remove_active: bool = False, operator: str = '') -> None:

  """

  Add or remove an Operator Preset

  """

  ...

def operator_presets_cleanup(*args, operator: str = '', properties: typing.Union[typing.Sequence[OperatorFileListElement], typing.Mapping[str, OperatorFileListElement], bpy.types.bpy_prop_collection] = None) -> None:

  """

  Remove outdated operator properties from presets that may cause problems

  """

  ...

def owner_disable(*args, owner_id: str = '') -> None:

  """

  Disable add-on for workspace

  """

  ...

def owner_enable(*args, owner_id: str = '') -> None:

  """

  Enable add-on for workspace

  """

  ...

def path_open(*args, filepath: str = '') -> None:

  """

  Open a path in a file browser

  """

  ...

def ply_export(*args, filepath: str = '', check_existing: bool = True, filter_blender: bool = False, filter_backup: bool = False, filter_image: bool = False, filter_movie: bool = False, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 8, display_type: str = 'DEFAULT', sort_method: str = '', forward_axis: str = 'Y', up_axis: str = 'Z', global_scale: float = 1.0, apply_modifiers: bool = True, export_selected_objects: bool = False, collection: str = '', export_uv: bool = True, export_normals: bool = False, export_colors: str = 'SRGB', export_attributes: bool = True, export_triangulated_mesh: bool = False, ascii_format: bool = False, filter_glob: str = '*args.ply') -> None:

  """

  Save the scene to a PLY file

  """

  ...

def ply_import(*args, filepath: str = '', directory: str = '', files: typing.Union[typing.Sequence[OperatorFileListElement], typing.Mapping[str, OperatorFileListElement], bpy.types.bpy_prop_collection] = None, check_existing: bool = False, filter_blender: bool = False, filter_backup: bool = False, filter_image: bool = False, filter_movie: bool = False, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 8, display_type: str = 'DEFAULT', sort_method: str = '', global_scale: float = 1.0, use_scene_unit: bool = False, forward_axis: str = 'Y', up_axis: str = 'Z', merge_verts: bool = False, import_colors: str = 'SRGB', import_attributes: bool = True, filter_glob: str = '*args.ply') -> None:

  """

  Import an PLY file as an object

  """

  ...

def previews_batch_clear(*args, files: typing.Union[typing.Sequence[OperatorFileListElement], typing.Mapping[str, OperatorFileListElement], bpy.types.bpy_prop_collection] = None, directory: str = '', filter_blender: bool = True, filter_folder: bool = True, use_scenes: bool = True, use_collections: bool = True, use_objects: bool = True, use_intern_data: bool = True, use_trusted: bool = False, use_backups: bool = True) -> None:

  """

  Clear selected .blend file's previews

  """

  ...

def previews_batch_generate(*args, files: typing.Union[typing.Sequence[OperatorFileListElement], typing.Mapping[str, OperatorFileListElement], bpy.types.bpy_prop_collection] = None, directory: str = '', filter_blender: bool = True, filter_folder: bool = True, use_scenes: bool = True, use_collections: bool = True, use_objects: bool = True, use_intern_data: bool = True, use_trusted: bool = False, use_backups: bool = True) -> None:

  """

  Generate selected .blend file's previews

  """

  ...

def previews_clear(*args, id_type: typing.Set[str] = {}) -> None:

  """

  Clear data-block previews (only for some types like objects, materials, textures, etc.)

  """

  ...

def previews_ensure() -> None:

  """

  Ensure data-block previews are available and up-to-date (to be saved in .blend file, only for some types like materials, textures, etc.)

  """

  ...

def properties_add(*args, data_path: str = '') -> None:

  """

  Add your own property to the data-block

  """

  ...

def properties_context_change(*args, context: str = '') -> None:

  """

  Jump to a different tab inside the properties editor

  """

  ...

def properties_edit(*args, data_path: str = '', property_name: str = '', property_type: str = 'FLOAT', is_overridable_library: bool = False, description: str = '', use_soft_limits: bool = False, array_length: int = 3, default_int: typing.Tuple[int, ...] = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), min_int: int = -10000, max_int: int = 10000, soft_min_int: int = -10000, soft_max_int: int = 10000, step_int: int = 1, default_bool: typing.Tuple[bool, ...] = (False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False), default_float: typing.Tuple[float, ...] = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), min_float: float = -10000.0, max_float: float = -10000.0, soft_min_float: float = -10000.0, soft_max_float: float = -10000.0, precision: int = 3, step_float: float = 0.1, subtype: str = '', default_string: str = '', id_type: str = 'OBJECT', eval_string: str = '') -> None:

  """

  Change a custom property's type, or adjust how it is displayed in the interface

  """

  ...

def properties_edit_value(*args, data_path: str = '', property_name: str = '', eval_string: str = '') -> None:

  """

  Edit the value of a custom property

  """

  ...

def properties_remove(*args, data_path: str = '', property_name: str = '') -> None:

  """

  Internal use (edit a property data_path)

  """

  ...

def quit_blender() -> None:

  """

  Quit Blender

  """

  ...

def radial_control(*args, data_path_primary: str = '', data_path_secondary: str = '', use_secondary: str = '', rotation_path: str = '', color_path: str = '', fill_color_path: str = '', fill_color_override_path: str = '', fill_color_override_test_path: str = '', zoom_path: str = '', image_id: str = '', secondary_tex: bool = False, release_confirm: bool = False) -> None:

  """

  Set some size property (e.g. brush size) with mouse wheel

  """

  ...

def read_factory_settings(*args, use_factory_startup_app_template_only: bool = False, app_template: str = 'Template', use_empty: bool = False) -> None:

  """

  Load factory default startup file and preferences. To make changes permanent, use "Save Startup File" and "Save Preferences"

  """

  ...

def read_factory_userpref(*args, use_factory_startup_app_template_only: bool = False) -> None:

  """

  Load factory default preferences. To make changes to preferences permanent, use "Save Preferences"

  """

  ...

def read_history() -> None:

  """

  Reloads history and bookmarks

  """

  ...

def read_homefile(*args, filepath: str = '', load_ui: bool = True, use_splash: bool = False, use_factory_startup: bool = False, use_factory_startup_app_template_only: bool = False, app_template: str = 'Template', use_empty: bool = False) -> None:

  """

  Open the default file

  """

  ...

def read_userpref() -> None:

  """

  Load last saved preferences

  """

  ...

def recover_auto_save(*args, filepath: str = '', hide_props_region: bool = True, check_existing: bool = False, filter_blender: bool = True, filter_backup: bool = False, filter_image: bool = False, filter_movie: bool = False, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = False, filter_blenlib: bool = False, filemode: int = 8, display_type: str = 'LIST_VERTICAL', sort_method: str = '', use_scripts: bool = False) -> None:

  """

  Open an automatically saved file to recover it

  """

  ...

def recover_last_session(*args, use_scripts: bool = False) -> None:

  """

  Open the last closed file ("quit.blend")

  """

  ...

def redraw_timer(*args, type: str = 'DRAW', iterations: int = 10, time_limit: float = 0.0) -> None:

  """

  Simple redraw timer to test the speed of updating the interface

  """

  ...

def revert_mainfile(*args, use_scripts: bool = False) -> None:

  """

  Reload the saved file

  """

  ...

def save_as_mainfile(*args, filepath: str = '', hide_props_region: bool = True, check_existing: bool = True, filter_blender: bool = True, filter_backup: bool = False, filter_image: bool = False, filter_movie: bool = False, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 8, display_type: str = 'DEFAULT', sort_method: str = '', compress: bool = False, relative_remap: bool = True, copy: bool = False) -> None:

  """

  Save the current file in the desired location

  """

  ...

def save_as_runtime(*args, player_path: str = '/home/runner/work/upbge/upbge/build/bin/blenderplayer', filepath: str = '', copy_python: bool = True, overwrite_lib: bool = False, copy_scripts: bool = False, copy_datafiles: bool = True, copy_modules: bool = True, copy_logic_nodes: bool = True, copy_libs: bool = True) -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def save_homefile() -> None:

  """

  Make the current file the default startup file

  """

  ...

def save_mainfile(*args, filepath: str = '', hide_props_region: bool = True, check_existing: bool = True, filter_blender: bool = True, filter_backup: bool = False, filter_image: bool = False, filter_movie: bool = False, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 8, display_type: str = 'DEFAULT', sort_method: str = '', compress: bool = False, relative_remap: bool = False, exit: bool = False, incremental: bool = False) -> None:

  """

  Save the current Blender file

  """

  ...

def save_userpref() -> None:

  """

  Make the current preferences default

  """

  ...

def search_menu() -> None:

  """

  Pop-up a search over all menus in the current context

  """

  ...

def search_operator() -> None:

  """

  Pop-up a search over all available operators in current context

  """

  ...

def search_single_menu(*args, menu_idname: str = '', initial_query: str = '') -> None:

  """

  Pop-up a search for a menu in current context

  """

  ...

def set_stereo_3d(*args, display_mode: str = 'ANAGLYPH', anaglyph_type: str = 'RED_CYAN', interlace_type: str = 'ROW_INTERLEAVED', use_interlace_swap: bool = False, use_sidebyside_crosseyed: bool = False) -> None:

  """

  Toggle 3D stereo support for current window (or change the display mode)

  """

  ...

def splash() -> None:

  """

  Open the splash screen with release info

  """

  ...

def splash_about() -> None:

  """

  Open a window with information about UPBGE

  """

  ...

def stl_export(*args, filepath: str = '', check_existing: bool = True, filter_blender: bool = False, filter_backup: bool = False, filter_image: bool = False, filter_movie: bool = False, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 8, display_type: str = 'DEFAULT', sort_method: str = '', ascii_format: bool = False, use_batch: bool = False, export_selected_objects: bool = False, collection: str = '', global_scale: float = 1.0, use_scene_unit: bool = False, forward_axis: str = 'Y', up_axis: str = 'Z', apply_modifiers: bool = True, filter_glob: str = '*args.stl') -> None:

  """

  Save the scene to an STL file

  """

  ...

def stl_import(*args, filepath: str = '', directory: str = '', files: typing.Union[typing.Sequence[OperatorFileListElement], typing.Mapping[str, OperatorFileListElement], bpy.types.bpy_prop_collection] = None, check_existing: bool = False, filter_blender: bool = False, filter_backup: bool = False, filter_image: bool = False, filter_movie: bool = False, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 8, display_type: str = 'DEFAULT', sort_method: str = '', global_scale: float = 1.0, use_scene_unit: bool = False, use_facet_normal: bool = False, forward_axis: str = 'Y', up_axis: str = 'Z', use_mesh_validate: bool = True, filter_glob: str = '*args.stl') -> None:

  """

  Import an STL file as an object

  """

  ...

def sysinfo(*args, filepath: str = '') -> None:

  """

  Generate system information, saved into a text file

  """

  ...

def tool_set_by_brush_type(*args, brush_type: str = '', space_type: str = 'EMPTY') -> None:

  """

  Look up the most appropriate tool for the given brush type and activate that

  """

  ...

def tool_set_by_id(*args, name: str = '', cycle: bool = False, as_fallback: bool = False, space_type: str = 'EMPTY') -> None:

  """

  Set the tool by name (for key-maps)

  """

  ...

def tool_set_by_index(*args, index: int = 0, cycle: bool = False, expand: bool = True, as_fallback: bool = False, space_type: str = 'EMPTY') -> None:

  """

  Set the tool by index (for key-maps)

  """

  ...

def toolbar() -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def toolbar_fallback_pie() -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def toolbar_prompt() -> None:

  """

  Leader key like functionality for accessing tools

  """

  ...

def url_open(*args, url: str = '') -> None:

  """

  Open a website in the web browser

  """

  ...

def url_open_preset(*args, type: str = '') -> None:

  """

  Open a preset website in the web browser

  """

  ...

def usd_export(*args, filepath: str = '', check_existing: bool = True, filter_blender: bool = False, filter_backup: bool = False, filter_image: bool = False, filter_movie: bool = False, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = True, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 8, display_type: str = 'DEFAULT', sort_method: str = '', filter_glob: str = '*args.usd', selected_objects_only: bool = False, visible_objects_only: bool = True, collection: str = '', export_animation: bool = False, export_hair: bool = False, export_uvmaps: bool = True, rename_uvmaps: bool = True, export_mesh_colors: bool = True, export_normals: bool = True, export_materials: bool = True, export_subdivision: str = 'BEST_MATCH', export_armatures: bool = True, only_deform_bones: bool = False, export_shapekeys: bool = True, use_instancing: bool = False, evaluation_mode: str = 'RENDER', generate_preview_surface: bool = True, generate_materialx_network: bool = False, convert_orientation: bool = False, export_global_forward_selection: str = 'NEGATIVE_Z', export_global_up_selection: str = 'Y', export_textures_mode: str = 'NEW', overwrite_textures: bool = False, relative_paths: bool = True, xform_op_mode: str = 'TRS', root_prim_path: str = '/root', export_custom_properties: bool = True, custom_properties_namespace: str = 'userProperties', author_blender_name: bool = True, convert_world_material: bool = True, allow_unicode: bool = True, export_meshes: bool = True, export_lights: bool = True, export_cameras: bool = True, export_curves: bool = True, export_points: bool = True, export_volumes: bool = True, triangulate_meshes: bool = False, quad_method: str = 'SHORTEST_DIAGONAL', ngon_method: str = 'BEAUTY', usdz_downscale_size: str = 'KEEP', usdz_downscale_custom_size: int = 128, merge_parent_xform: bool = False, convert_scene_units: str = 'METERS', meters_per_unit: float = 1.0) -> None:

  """

  Export current scene in a USD archive

  """

  ...

def usd_import(*args, filepath: str = '', check_existing: bool = False, filter_blender: bool = False, filter_backup: bool = False, filter_image: bool = False, filter_movie: bool = False, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = True, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 8, relative_path: bool = True, display_type: str = 'DEFAULT', sort_method: str = '', filter_glob: str = '*args.usd', scale: float = 1.0, set_frame_range: bool = True, import_cameras: bool = True, import_curves: bool = True, import_lights: bool = True, import_materials: bool = True, import_meshes: bool = True, import_volumes: bool = True, import_shapes: bool = True, import_skeletons: bool = True, import_blendshapes: bool = True, import_points: bool = True, import_subdivision: bool = False, support_scene_instancing: bool = True, import_visible_only: bool = True, create_collection: bool = False, read_mesh_uvs: bool = True, read_mesh_colors: bool = True, read_mesh_attributes: bool = True, prim_path_mask: str = '', import_guide: bool = False, import_proxy: bool = False, import_render: bool = True, import_all_materials: bool = False, import_usd_preview: bool = True, set_material_blend: bool = True, light_intensity_scale: float = 1.0, mtl_purpose: str = 'MTL_FULL', mtl_name_collision_mode: str = 'MAKE_UNIQUE', import_textures_mode: str = 'IMPORT_PACK', import_textures_dir: str = '//textures/', tex_name_collision_mode: str = 'USE_EXISTING', property_import_mode: str = 'ALL', validate_meshes: bool = False, create_world_material: bool = True, import_defined_only: bool = True, merge_parent_xform: bool = True, apply_unit_conversion_scale: bool = True) -> None:

  """

  Import USD stage into current scene

  """

  ...

def window_close() -> None:

  """

  Close the current window

  """

  ...

def window_fullscreen_toggle() -> None:

  """

  Toggle the current window full-screen

  """

  ...

def window_new() -> None:

  """

  Create a new window

  """

  ...

def window_new_main() -> None:

  """

  Create a new main window with its own workspace and scene selection

  """

  ...

def xr_navigation_fly(*args, mode: str = 'VIEWER_FORWARD', lock_location_z: bool = False, lock_direction: bool = False, speed_frame_based: bool = True, speed_min: float = 0.018, speed_max: float = 0.054, speed_interpolation0: mathutils.Vector = (0.0, 0.0), speed_interpolation1: mathutils.Vector = (1.0, 1.0)) -> None:

  """

  Move/turn relative to the VR viewer or controller

  """

  ...

def xr_navigation_grab(*args, lock_location: bool = False, lock_location_z: bool = False, lock_rotation: bool = False, lock_rotation_z: bool = False, lock_scale: bool = False) -> None:

  """

  Navigate the VR scene by grabbing with controllers

  """

  ...

def xr_navigation_reset(*args, location: bool = True, rotation: bool = True, scale: bool = True) -> None:

  """

  Reset VR navigation deltas relative to session base pose

  """

  ...

def xr_navigation_teleport(*args, teleport_axes: typing.Tuple[bool, bool, bool] = (True, True, True), interpolation: float = 1.0, offset: float = 0.0, selectable_only: bool = True, distance: float = 1.70141e+38, from_viewer: bool = False, axis: mathutils.Vector = (0.0, 0.0, -1.0), color: typing.Tuple[float, float, float, float] = (0.35, 0.35, 1.0, 1.0)) -> None:

  """

  Set VR viewer location to controller raycast hit location

  """

  ...

def xr_session_toggle() -> None:

  """

  Open a view for use with virtual reality headsets, or close it if already opened

  """

  ...
