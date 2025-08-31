"""


Export Scene Operators
**********************

:func:`fbx`

:func:`gltf`

"""

import typing

def fbx(*args, filepath: str = '', check_existing: bool = True, filter_glob: str = '*args.fbx', use_selection: bool = False, use_visible: bool = False, use_active_collection: bool = False, collection: str = '', global_scale: float = 1.0, apply_unit_scale: bool = True, apply_scale_options: str = 'FBX_SCALE_NONE', use_space_transform: bool = True, bake_space_transform: bool = False, object_types: typing.Set[str] = {'ARMATURE', 'CAMERA', 'EMPTY', 'LIGHT', 'MESH', 'OTHER'}, use_mesh_modifiers: bool = True, use_mesh_modifiers_render: bool = True, mesh_smooth_type: str = 'OFF', colors_type: str = 'SRGB', prioritize_active_color: bool = False, use_subsurf: bool = False, use_mesh_edges: bool = False, use_tspace: bool = False, use_triangles: bool = False, use_custom_props: bool = False, add_leaf_bones: bool = True, primary_bone_axis: str = 'Y', secondary_bone_axis: str = 'X', use_armature_deform_only: bool = False, armature_nodetype: str = 'NULL', bake_anim: bool = True, bake_anim_use_all_bones: bool = True, bake_anim_use_nla_strips: bool = True, bake_anim_use_all_actions: bool = True, bake_anim_force_startend_keying: bool = True, bake_anim_step: float = 1.0, bake_anim_simplify_factor: float = 1.0, path_mode: str = 'AUTO', embed_textures: bool = False, batch_mode: str = 'OFF', use_batch_own_dir: bool = True, use_metadata: bool = True, axis_forward: str = '-Z', axis_up: str = 'Y') -> None:

  """

  Write a FBX file

  """

  ...

def gltf(*args, filepath: str = '', check_existing: bool = True, export_import_convert_lighting_mode: str = 'SPEC', gltf_export_id: str = '', export_use_gltfpack: bool = False, export_gltfpack_tc: bool = True, export_gltfpack_tq: int = 8, export_gltfpack_si: float = 1.0, export_gltfpack_sa: bool = False, export_gltfpack_slb: bool = False, export_gltfpack_vp: int = 14, export_gltfpack_vt: int = 12, export_gltfpack_vn: int = 8, export_gltfpack_vc: int = 8, export_gltfpack_vpi: str = 'Integer', export_gltfpack_noq: bool = True, export_gltfpack_kn: bool = False, export_format: str = '', ui_tab: str = 'GENERAL', export_copyright: str = '', export_image_format: str = 'AUTO', export_image_add_webp: bool = False, export_image_webp_fallback: bool = False, export_texture_dir: str = '', export_jpeg_quality: int = 75, export_image_quality: int = 75, export_keep_originals: bool = False, export_texcoords: bool = True, export_normals: bool = True, export_gn_mesh: bool = False, export_draco_mesh_compression_enable: bool = False, export_draco_mesh_compression_level: int = 6, export_draco_position_quantization: int = 14, export_draco_normal_quantization: int = 10, export_draco_texcoord_quantization: int = 12, export_draco_color_quantization: int = 10, export_draco_generic_quantization: int = 12, export_tangents: bool = False, export_materials: str = 'EXPORT', export_unused_images: bool = False, export_unused_textures: bool = False, export_vertex_color: str = 'MATERIAL', export_vertex_color_name: str = 'Color', export_all_vertex_colors: bool = True, export_active_vertex_color_when_no_material: bool = True, export_attributes: bool = False, use_mesh_edges: bool = False, use_mesh_vertices: bool = False, export_cameras: bool = False, use_selection: bool = False, use_visible: bool = False, use_renderable: bool = False, use_active_collection_with_nested: bool = True, use_active_collection: bool = False, use_active_scene: bool = False, collection: str = '', at_collection_center: bool = False, export_extras: bool = False, export_yup: bool = True, export_apply: bool = False, export_shared_accessors: bool = False, export_animations: bool = True, export_frame_range: bool = False, export_frame_step: int = 1, export_force_sampling: bool = True, export_sampling_interpolation_fallback: str = 'LINEAR', export_pointer_animation: bool = False, export_animation_mode: str = 'ACTIONS', export_nla_strips_merged_animation_name: str = 'Animation', export_def_bones: bool = False, export_hierarchy_flatten_bones: bool = False, export_hierarchy_flatten_objs: bool = False, export_armature_object_remove: bool = False, export_leaf_bone: bool = False, export_optimize_animation_size: bool = True, export_optimize_animation_keep_anim_armature: bool = True, export_optimize_animation_keep_anim_object: bool = False, export_optimize_disable_viewport: bool = False, export_negative_frame: str = 'SLIDE', export_anim_slide_to_zero: bool = False, export_bake_animation: bool = False, export_merge_animation: str = 'ACTION', export_anim_single_armature: bool = True, export_reset_pose_bones: bool = True, export_current_frame: bool = False, export_rest_position_armature: bool = True, export_anim_scene_split_object: bool = True, export_skins: bool = True, export_influence_nb: int = 4, export_all_influences: bool = False, export_morph: bool = True, export_morph_normal: bool = True, export_morph_tangent: bool = False, export_morph_animation: bool = True, export_morph_reset_sk_data: bool = True, export_lights: bool = False, export_try_sparse_sk: bool = True, export_try_omit_sparse_sk: bool = False, export_gpu_instances: bool = False, export_action_filter: bool = False, export_convert_animation_pointer: bool = False, export_nla_strips: bool = True, export_original_specular: bool = False, will_save_settings: bool = False, export_hierarchy_full_collections: bool = False, export_extra_animations: bool = False, export_loglevel: int = -1, filter_glob: str = '*args.glb') -> None:

  """

  Export scene as glTF 2.0 file

  """

  ...
