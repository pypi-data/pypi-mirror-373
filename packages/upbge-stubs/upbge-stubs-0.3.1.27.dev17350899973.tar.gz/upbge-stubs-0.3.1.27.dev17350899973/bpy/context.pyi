"""


Context Access (bpy.context)
****************************

The context members available depend on the area of Blender which is currently being accessed.

Note that all context values are read-only,
but may be modified through the data API or by running operators.


Global Context
==============

These properties are available in any contexts.

:data:`area`

:data:`asset`

:data:`blend_data`

:data:`collection`

:data:`engine`

:data:`gizmo_group`

:data:`layer_collection`

:data:`mode`

:data:`preferences`

:data:`region`

:data:`region_data`

:data:`region_popup`

:data:`scene`

:data:`screen`

:data:`space_data`

:data:`tool_settings`

:data:`view_layer`

:data:`window`

:data:`window_manager`

:data:`workspace`


Buttons Context
===============

:data:`texture_slot`

:data:`world`

:data:`object`

:data:`mesh`

:data:`armature`

:data:`lattice`

:data:`curve`

:data:`meta_ball`

:data:`light`

:data:`speaker`

:data:`lightprobe`

:data:`camera`

:data:`material`

:data:`material_slot`

:data:`texture`

:data:`texture_user`

:data:`texture_user_property`

:data:`texture_node`

:data:`bone`

:data:`edit_bone`

:data:`pose_bone`

:data:`particle_system`

:data:`particle_system_editable`

:data:`particle_settings`

:data:`cloth`

:data:`soft_body`

:data:`fluid`

:data:`collision`

:data:`brush`

:data:`dynamic_paint`

:data:`line_style`

:data:`gpencil`

:data:`grease_pencil`

:data:`curves`

:data:`pointcloud`

:data:`volume`


Clip Context
============

:data:`edit_movieclip`

:data:`edit_mask`


File Context
============

:data:`active_file`

:data:`selected_files`

:data:`asset_library_reference`

:data:`selected_assets`

:data:`id`

:data:`selected_ids`


Image Context
=============

:data:`edit_image`


Node Context
============

:data:`selected_nodes`

:data:`active_node`


Screen Context
==============

:data:`visible_objects`

:data:`selectable_objects`

:data:`selected_objects`

:data:`editable_objects`

:data:`selected_editable_objects`

:data:`objects_in_mode`

:data:`objects_in_mode_unique_data`

:data:`visible_bones`

:data:`editable_bones`

:data:`selected_bones`

:data:`selected_editable_bones`

:data:`visible_pose_bones`

:data:`selected_pose_bones`

:data:`selected_pose_bones_from_active_object`

:data:`active_bone`

:data:`active_pose_bone`

:data:`active_object`

:data:`edit_object`

:data:`sculpt_object`

:data:`vertex_paint_object`

:data:`weight_paint_object`

:data:`image_paint_object`

:data:`particle_edit_object`

:data:`pose_object`

:data:`active_sequence_strip`

:data:`sequences`

:data:`selected_sequences`

:data:`selected_editable_sequences`

:data:`active_nla_track`

:data:`active_nla_strip`

:data:`selected_nla_strips`

:data:`selected_movieclip_tracks`

:data:`annotation_data`

:data:`annotation_data_owner`

:data:`active_annotation_layer`

:data:`active_operator`

:data:`active_action`

:data:`selected_visible_actions`

:data:`selected_editable_actions`

:data:`visible_fcurves`

:data:`editable_fcurves`

:data:`selected_visible_fcurves`

:data:`selected_editable_fcurves`

:data:`active_editable_fcurve`

:data:`selected_editable_keyframes`

:data:`ui_list`

:data:`property`

:data:`active_strip`

:data:`strips`

:data:`selected_strips`

:data:`selected_editable_strips`

:data:`sequencer_scene`


Sequencer Context
=================


Text Context
============

:data:`edit_text`


View3D Context
==============

"""

import typing

import bpy

area: bpy.types.Area = ...

asset: bpy.types.AssetRepresentation = ...

blend_data: bpy.types.BlendData = ...

collection: bpy.types.Collection = ...

engine: str = ...

gizmo_group: bpy.types.GizmoGroup = ...

layer_collection: bpy.types.LayerCollection = ...

mode: str = ...

preferences: bpy.types.Preferences = ...

region: bpy.types.Region = ...

region_data: bpy.types.RegionView3D = ...

region_popup: bpy.types.Region = ...

"""

The temporary region for pop-ups (including menus and pop-overs)

"""

scene: bpy.types.Scene = ...

screen: bpy.types.Screen = ...

space_data: bpy.types.Space = ...

"""

The current space, may be None in background-mode, when the cursor is outside the window or when using menu-search

"""

tool_settings: bpy.types.ToolSettings = ...

view_layer: bpy.types.ViewLayer = ...

window: bpy.types.Window = ...

window_manager: bpy.types.WindowManager = ...

workspace: bpy.types.WorkSpace = ...

texture_slot: bpy.types.TextureSlot = ...

world: bpy.types.World = ...

object: bpy.types.Object = ...

mesh: bpy.types.Mesh = ...

armature: bpy.types.Armature = ...

lattice: bpy.types.Lattice = ...

curve: bpy.types.Curve = ...

meta_ball: bpy.types.MetaBall = ...

light: bpy.types.Light = ...

speaker: bpy.types.Speaker = ...

lightprobe: bpy.types.LightProbe = ...

camera: bpy.types.Camera = ...

material: bpy.types.Material = ...

material_slot: bpy.types.MaterialSlot = ...

texture: bpy.types.Texture = ...

texture_user: bpy.types.ID = ...

texture_user_property: bpy.types.Property = ...

texture_node: bpy.types.Node = ...

bone: bpy.types.Bone = ...

edit_bone: bpy.types.EditBone = ...

pose_bone: bpy.types.PoseBone = ...

particle_system: bpy.types.ParticleSystem = ...

particle_system_editable: bpy.types.ParticleSystem = ...

particle_settings: bpy.types.ParticleSettings = ...

cloth: bpy.types.ClothModifier = ...

soft_body: bpy.types.SoftBodyModifier = ...

fluid: bpy.types.FluidSimulationModifier = ...

collision: bpy.types.CollisionModifier = ...

brush: bpy.types.Brush = ...

dynamic_paint: bpy.types.DynamicPaintModifier = ...

line_style: bpy.types.FreestyleLineStyle = ...

gpencil: bpy.types.GreasePencil = ...

grease_pencil: bpy.types.GreasePencilv3 = ...

curves: typing.Any = ...

pointcloud: bpy.types.PointCloud = ...

volume: bpy.types.Volume = ...

edit_movieclip: bpy.types.MovieClip = ...

edit_mask: bpy.types.Mask = ...

active_file: bpy.types.FileSelectEntry = ...

selected_files: typing.Sequence[bpy.types.FileSelectEntry] = ...

asset_library_reference: bpy.types.AssetLibraryReference = ...

selected_assets: typing.Sequence[bpy.types.AssetRepresentation] = ...

id: bpy.types.ID = ...

selected_ids: typing.Sequence[bpy.types.ID] = ...

edit_image: bpy.types.Image = ...

selected_nodes: typing.Sequence[bpy.types.Node] = ...

active_node: bpy.types.Node = ...

visible_objects: typing.Sequence[bpy.types.Object] = ...

selectable_objects: typing.Sequence[bpy.types.Object] = ...

selected_objects: typing.Sequence[bpy.types.Object] = ...

editable_objects: typing.Sequence[bpy.types.Object] = ...

selected_editable_objects: typing.Sequence[bpy.types.Object] = ...

objects_in_mode: typing.Sequence[bpy.types.Object] = ...

objects_in_mode_unique_data: typing.Sequence[bpy.types.Object] = ...

visible_bones: typing.Sequence[bpy.types.EditBone] = ...

editable_bones: typing.Sequence[bpy.types.EditBone] = ...

selected_bones: typing.Sequence[bpy.types.EditBone] = ...

selected_editable_bones: typing.Sequence[bpy.types.EditBone] = ...

visible_pose_bones: typing.Sequence[bpy.types.PoseBone] = ...

selected_pose_bones: typing.Sequence[bpy.types.PoseBone] = ...

selected_pose_bones_from_active_object: typing.Sequence[bpy.types.PoseBone] = ...

active_bone: typing.Union[bpy.types.EditBone, bpy.types.Bone] = ...

active_pose_bone: bpy.types.PoseBone = ...

active_object: bpy.types.Object = ...

edit_object: bpy.types.Object = ...

sculpt_object: bpy.types.Object = ...

vertex_paint_object: bpy.types.Object = ...

weight_paint_object: bpy.types.Object = ...

image_paint_object: bpy.types.Object = ...

particle_edit_object: bpy.types.Object = ...

pose_object: bpy.types.Object = ...

active_sequence_strip: bpy.types.Strip = ...

sequences: typing.Sequence[bpy.types.Strip] = ...

selected_sequences: typing.Sequence[bpy.types.Strip] = ...

selected_editable_sequences: typing.Sequence[bpy.types.Strip] = ...

active_nla_track: bpy.types.NlaTrack = ...

active_nla_strip: bpy.types.NlaStrip = ...

selected_nla_strips: typing.Sequence[bpy.types.NlaStrip] = ...

selected_movieclip_tracks: typing.Sequence[bpy.types.MovieTrackingTrack] = ...

annotation_data: bpy.types.GreasePencil = ...

annotation_data_owner: bpy.types.ID = ...

active_annotation_layer: bpy.types.GPencilLayer = ...

active_operator: bpy.types.Operator = ...

active_action: bpy.types.Action = ...

selected_visible_actions: typing.Sequence[bpy.types.Action] = ...

selected_editable_actions: typing.Sequence[bpy.types.Action] = ...

visible_fcurves: typing.Sequence[bpy.types.FCurve] = ...

editable_fcurves: typing.Sequence[bpy.types.FCurve] = ...

selected_visible_fcurves: typing.Sequence[bpy.types.FCurve] = ...

selected_editable_fcurves: typing.Sequence[bpy.types.FCurve] = ...

active_editable_fcurve: bpy.types.FCurve = ...

selected_editable_keyframes: typing.Sequence[bpy.types.Keyframe] = ...

ui_list: bpy.types.UIList = ...

property: typing.Union[bpy.types.AnyType, str, int] = ...

"""

Get the property associated with a hovered button.
Returns a tuple of the data-block, data path to the property, and array index.

Note: When the property doesn't have an associated :class:`bpy.types.ID` non-ID data may be returned.
This may occur when accessing windowing data, for example, operator properties.

.. code::

  # Example inserting keyframe for the hovered property.
  active_property = bpy.context.property
  if active_property:
      datablock, data_path, index = active_property
      datablock.keyframe_insert(data_path=data_path, index=index, frame=1)

"""

active_strip: bpy.types.Strip = ...

strips: typing.Sequence[bpy.types.Strip] = ...

selected_strips: typing.Sequence[bpy.types.Strip] = ...

selected_editable_strips: typing.Sequence[bpy.types.Strip] = ...

sequencer_scene: bpy.types.Scene = ...

edit_text: bpy.types.Text = ...
