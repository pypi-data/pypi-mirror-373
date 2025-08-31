"""


Import Scene Operators
**********************

:func:`fbx`

:func:`gltf`

"""

import typing

def fbx(*args, filepath: str = '', directory: str = '', filter_glob: str = '*args.fbx', files: typing.Union[typing.Sequence[OperatorFileListElement], typing.Mapping[str, OperatorFileListElement], bpy.types.bpy_prop_collection] = None, ui_tab: str = 'MAIN', use_manual_orientation: bool = False, global_scale: float = 1.0, bake_space_transform: bool = False, use_custom_normals: bool = True, colors_type: str = 'SRGB', use_image_search: bool = True, use_alpha_decals: bool = False, decal_offset: float = 0.0, use_anim: bool = True, anim_offset: float = 1.0, use_subsurf: bool = False, use_custom_props: bool = True, use_custom_props_enum_as_string: bool = True, ignore_leaf_bones: bool = False, force_connect_children: bool = False, automatic_bone_orientation: bool = False, primary_bone_axis: str = 'Y', secondary_bone_axis: str = 'X', use_prepost_rot: bool = True, mtl_name_collision_mode: str = 'MAKE_UNIQUE', axis_forward: str = '-Z', axis_up: str = 'Y') -> None:

  """

  Load a FBX file

  """

  ...

def gltf(*args, filepath: str = '', export_import_convert_lighting_mode: str = 'SPEC', filter_glob: str = '*args.glb;*args.gltf', directory: str = '', files: typing.Union[typing.Sequence[OperatorFileListElement], typing.Mapping[str, OperatorFileListElement], bpy.types.bpy_prop_collection] = None, loglevel: int = 0, import_pack_images: bool = True, merge_vertices: bool = False, import_shading: str = 'NORMALS', bone_heuristic: str = 'BLENDER', disable_bone_shape: bool = False, bone_shape_scale_factor: float = 1.0, guess_original_bind_pose: bool = True, import_webp_texture: bool = False, import_unused_materials: bool = False, import_select_created_objects: bool = True, import_scene_extras: bool = True, import_scene_as_collection: bool = True, import_merge_material_slots: bool = True) -> None:

  """

  Load a glTF 2.0 file

  """

  ...
