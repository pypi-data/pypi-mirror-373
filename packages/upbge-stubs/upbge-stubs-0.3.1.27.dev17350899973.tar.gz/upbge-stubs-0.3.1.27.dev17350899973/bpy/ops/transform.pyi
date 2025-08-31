"""


Transform Operators
*******************

:func:`bbone_resize`

:func:`bend`

:func:`create_orientation`

:func:`delete_orientation`

:func:`edge_bevelweight`

:func:`edge_crease`

:func:`edge_slide`

:func:`from_gizmo`

:func:`mirror`

:func:`push_pull`

:func:`resize`

:func:`rotate`

:func:`rotate_normal`

:func:`select_orientation`

:func:`seq_slide`

:func:`shear`

:func:`shrink_fatten`

:func:`skin_resize`

:func:`tilt`

:func:`tosphere`

:func:`trackball`

:func:`transform`

:func:`translate`

:func:`vert_crease`

:func:`vert_slide`

:func:`vertex_random`

:func:`vertex_warp`

"""

import typing

import mathutils

def bbone_resize(*args, value: mathutils.Vector = (1.0, 1.0, 1.0), orient_type: str = 'GLOBAL', orient_matrix: mathutils.Matrix = ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)), orient_matrix_type: str = 'GLOBAL', constraint_axis: typing.Tuple[bool, bool, bool] = (False, False, False), mirror: bool = False, release_confirm: bool = False, use_accurate: bool = False) -> None:

  """

  Scale selected bendy bones display size

  """

  ...

def bend(*args, value: typing.Tuple[float] = 0.0, mirror: bool = False, use_proportional_edit: bool = False, proportional_edit_falloff: str = 'SMOOTH', proportional_size: float = 1.0, use_proportional_connected: bool = False, use_proportional_projected: bool = False, snap: bool = False, gpencil_strokes: bool = False, center_override: mathutils.Vector = (0.0, 0.0, 0.0), release_confirm: bool = False, use_accurate: bool = False) -> None:

  """

  Bend selected items between the 3D cursor and the mouse

  """

  ...

def create_orientation(*args, name: str = '', use_view: bool = False, use: bool = False, overwrite: bool = False) -> None:

  """

  Create transformation orientation from selection

  """

  ...

def delete_orientation() -> None:

  """

  Delete transformation orientation

  """

  ...

def edge_bevelweight(*args, value: float = 0.0, snap: bool = False, release_confirm: bool = False, use_accurate: bool = False) -> None:

  """

  Change the bevel weight of edges

  """

  ...

def edge_crease(*args, value: float = 0.0, snap: bool = False, release_confirm: bool = False, use_accurate: bool = False) -> None:

  """

  Change the crease of edges

  """

  ...

def edge_slide(*args, value: float = 0.0, single_side: bool = False, use_even: bool = False, flipped: bool = False, use_clamp: bool = True, mirror: bool = False, snap: bool = False, snap_elements: typing.Set[str] = {'INCREMENT'}, use_snap_project: bool = False, snap_target: str = 'CLOSEST', use_snap_self: bool = True, use_snap_edit: bool = True, use_snap_nonedit: bool = True, use_snap_selectable: bool = False, snap_point: mathutils.Vector = (0.0, 0.0, 0.0), correct_uv: bool = True, release_confirm: bool = False, use_accurate: bool = False) -> None:

  """

  Slide an edge loop along a mesh

  """

  ...

def from_gizmo() -> None:

  """

  Transform selected items by mode type

  """

  ...

def mirror(*args, orient_type: str = 'GLOBAL', orient_matrix: mathutils.Matrix = ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)), orient_matrix_type: str = 'GLOBAL', constraint_axis: typing.Tuple[bool, bool, bool] = (False, False, False), gpencil_strokes: bool = False, center_override: mathutils.Vector = (0.0, 0.0, 0.0), release_confirm: bool = False, use_accurate: bool = False) -> None:

  """

  Mirror selected items around one or more axes

  """

  ...

def push_pull(*args, value: float = 0.0, mirror: bool = False, use_proportional_edit: bool = False, proportional_edit_falloff: str = 'SMOOTH', proportional_size: float = 1.0, use_proportional_connected: bool = False, use_proportional_projected: bool = False, snap: bool = False, center_override: mathutils.Vector = (0.0, 0.0, 0.0), release_confirm: bool = False, use_accurate: bool = False) -> None:

  """

  Push/Pull selected items

  """

  ...

def resize(*args, value: mathutils.Vector = (1.0, 1.0, 1.0), mouse_dir_constraint: mathutils.Vector = (0.0, 0.0, 0.0), orient_type: str = 'GLOBAL', orient_matrix: mathutils.Matrix = ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)), orient_matrix_type: str = 'GLOBAL', constraint_axis: typing.Tuple[bool, bool, bool] = (False, False, False), mirror: bool = False, use_proportional_edit: bool = False, proportional_edit_falloff: str = 'SMOOTH', proportional_size: float = 1.0, use_proportional_connected: bool = False, use_proportional_projected: bool = False, snap: bool = False, snap_elements: typing.Set[str] = {'INCREMENT'}, use_snap_project: bool = False, snap_target: str = 'CLOSEST', use_snap_self: bool = True, use_snap_edit: bool = True, use_snap_nonedit: bool = True, use_snap_selectable: bool = False, snap_point: mathutils.Vector = (0.0, 0.0, 0.0), gpencil_strokes: bool = False, texture_space: bool = False, remove_on_cancel: bool = False, use_duplicated_keyframes: bool = False, center_override: mathutils.Vector = (0.0, 0.0, 0.0), release_confirm: bool = False, use_accurate: bool = False) -> None:

  """

  Scale (resize) selected items

  """

  ...

def rotate(*args, value: float = 0.0, orient_axis: str = 'Z', orient_type: str = 'GLOBAL', orient_matrix: mathutils.Matrix = ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)), orient_matrix_type: str = 'GLOBAL', constraint_axis: typing.Tuple[bool, bool, bool] = (False, False, False), mirror: bool = False, use_proportional_edit: bool = False, proportional_edit_falloff: str = 'SMOOTH', proportional_size: float = 1.0, use_proportional_connected: bool = False, use_proportional_projected: bool = False, snap: bool = False, snap_elements: typing.Set[str] = {'INCREMENT'}, use_snap_project: bool = False, snap_target: str = 'CLOSEST', use_snap_self: bool = True, use_snap_edit: bool = True, use_snap_nonedit: bool = True, use_snap_selectable: bool = False, snap_point: mathutils.Vector = (0.0, 0.0, 0.0), gpencil_strokes: bool = False, center_override: mathutils.Vector = (0.0, 0.0, 0.0), release_confirm: bool = False, use_accurate: bool = False) -> None:

  """

  Rotate selected items

  """

  ...

def rotate_normal(*args, value: float = 0.0, orient_axis: str = 'Z', orient_type: str = 'GLOBAL', orient_matrix: mathutils.Matrix = ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)), orient_matrix_type: str = 'GLOBAL', constraint_axis: typing.Tuple[bool, bool, bool] = (False, False, False), mirror: bool = False, release_confirm: bool = False, use_accurate: bool = False) -> None:

  """

  Rotate custom normal of selected items

  """

  ...

def select_orientation(*args, orientation: str = 'GLOBAL') -> None:

  """

  Select transformation orientation

  """

  ...

def seq_slide(*args, value: mathutils.Vector = (0.0, 0.0), use_restore_handle_selection: bool = False, snap: bool = False, texture_space: bool = False, remove_on_cancel: bool = False, use_duplicated_keyframes: bool = False, view2d_edge_pan: bool = False, release_confirm: bool = False, use_accurate: bool = False) -> None:

  """

  Slide a sequence strip in time

  """

  ...

def shear(*args, value: float = 0.0, orient_axis: str = 'Z', orient_axis_ortho: str = 'X', orient_type: str = 'GLOBAL', orient_matrix: mathutils.Matrix = ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)), orient_matrix_type: str = 'GLOBAL', mirror: bool = False, use_proportional_edit: bool = False, proportional_edit_falloff: str = 'SMOOTH', proportional_size: float = 1.0, use_proportional_connected: bool = False, use_proportional_projected: bool = False, snap: bool = False, gpencil_strokes: bool = False, release_confirm: bool = False, use_accurate: bool = False) -> None:

  """

  Shear selected items along the given axis

  """

  ...

def shrink_fatten(*args, value: float = 0.0, use_even_offset: bool = False, mirror: bool = False, use_proportional_edit: bool = False, proportional_edit_falloff: str = 'SMOOTH', proportional_size: float = 1.0, use_proportional_connected: bool = False, use_proportional_projected: bool = False, snap: bool = False, release_confirm: bool = False, use_accurate: bool = False) -> None:

  """

  Shrink/fatten selected vertices along normals

  """

  ...

def skin_resize(*args, value: mathutils.Vector = (1.0, 1.0, 1.0), orient_type: str = 'GLOBAL', orient_matrix: mathutils.Matrix = ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)), orient_matrix_type: str = 'GLOBAL', constraint_axis: typing.Tuple[bool, bool, bool] = (False, False, False), mirror: bool = False, use_proportional_edit: bool = False, proportional_edit_falloff: str = 'SMOOTH', proportional_size: float = 1.0, use_proportional_connected: bool = False, use_proportional_projected: bool = False, snap: bool = False, snap_elements: typing.Set[str] = {'INCREMENT'}, use_snap_project: bool = False, snap_target: str = 'CLOSEST', use_snap_self: bool = True, use_snap_edit: bool = True, use_snap_nonedit: bool = True, use_snap_selectable: bool = False, snap_point: mathutils.Vector = (0.0, 0.0, 0.0), release_confirm: bool = False, use_accurate: bool = False) -> None:

  """

  Scale selected vertices' skin radii

  """

  ...

def tilt(*args, value: float = 0.0, mirror: bool = False, use_proportional_edit: bool = False, proportional_edit_falloff: str = 'SMOOTH', proportional_size: float = 1.0, use_proportional_connected: bool = False, use_proportional_projected: bool = False, snap: bool = False, release_confirm: bool = False, use_accurate: bool = False) -> None:

  """

  Tilt selected control vertices of 3D curve

  """

  ...

def tosphere(*args, value: float = 0.0, mirror: bool = False, use_proportional_edit: bool = False, proportional_edit_falloff: str = 'SMOOTH', proportional_size: float = 1.0, use_proportional_connected: bool = False, use_proportional_projected: bool = False, snap: bool = False, gpencil_strokes: bool = False, center_override: mathutils.Vector = (0.0, 0.0, 0.0), release_confirm: bool = False, use_accurate: bool = False) -> None:

  """

  Move selected items outward in a spherical shape around geometric center

  """

  ...

def trackball(*args, value: typing.Tuple[float, float] = (0.0, 0.0), mirror: bool = False, use_proportional_edit: bool = False, proportional_edit_falloff: str = 'SMOOTH', proportional_size: float = 1.0, use_proportional_connected: bool = False, use_proportional_projected: bool = False, snap: bool = False, gpencil_strokes: bool = False, center_override: mathutils.Vector = (0.0, 0.0, 0.0), release_confirm: bool = False, use_accurate: bool = False) -> None:

  """

  Trackball style rotation of selected items

  """

  ...

def transform(*args, mode: str = 'TRANSLATION', value: mathutils.Vector = (0.0, 0.0, 0.0, 0.0), orient_axis: str = 'Z', orient_type: str = 'GLOBAL', orient_matrix: mathutils.Matrix = ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)), orient_matrix_type: str = 'GLOBAL', constraint_axis: typing.Tuple[bool, bool, bool] = (False, False, False), mirror: bool = False, use_proportional_edit: bool = False, proportional_edit_falloff: str = 'SMOOTH', proportional_size: float = 1.0, use_proportional_connected: bool = False, use_proportional_projected: bool = False, snap: bool = False, snap_elements: typing.Set[str] = {'INCREMENT'}, use_snap_project: bool = False, snap_target: str = 'CLOSEST', use_snap_self: bool = True, use_snap_edit: bool = True, use_snap_nonedit: bool = True, use_snap_selectable: bool = False, snap_point: mathutils.Vector = (0.0, 0.0, 0.0), snap_align: bool = False, snap_normal: mathutils.Vector = (0.0, 0.0, 0.0), gpencil_strokes: bool = False, texture_space: bool = False, remove_on_cancel: bool = False, use_duplicated_keyframes: bool = False, center_override: mathutils.Vector = (0.0, 0.0, 0.0), release_confirm: bool = False, use_accurate: bool = False, use_automerge_and_split: bool = False) -> None:

  """

  Transform selected items by mode type

  """

  ...

def translate(*args, value: mathutils.Vector = (0.0, 0.0, 0.0), orient_type: str = 'GLOBAL', orient_matrix: mathutils.Matrix = ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)), orient_matrix_type: str = 'GLOBAL', constraint_axis: typing.Tuple[bool, bool, bool] = (False, False, False), mirror: bool = False, use_proportional_edit: bool = False, proportional_edit_falloff: str = 'SMOOTH', proportional_size: float = 1.0, use_proportional_connected: bool = False, use_proportional_projected: bool = False, snap: bool = False, snap_elements: typing.Set[str] = {'INCREMENT'}, use_snap_project: bool = False, snap_target: str = 'CLOSEST', use_snap_self: bool = True, use_snap_edit: bool = True, use_snap_nonedit: bool = True, use_snap_selectable: bool = False, snap_point: mathutils.Vector = (0.0, 0.0, 0.0), snap_align: bool = False, snap_normal: mathutils.Vector = (0.0, 0.0, 0.0), gpencil_strokes: bool = False, cursor_transform: bool = False, texture_space: bool = False, remove_on_cancel: bool = False, use_duplicated_keyframes: bool = False, view2d_edge_pan: bool = False, release_confirm: bool = False, use_accurate: bool = False, use_automerge_and_split: bool = False, translate_origin: bool = False) -> None:

  """

  Move selected items

  """

  ...

def vert_crease(*args, value: float = 0.0, snap: bool = False, release_confirm: bool = False, use_accurate: bool = False) -> None:

  """

  Change the crease of vertices

  """

  ...

def vert_slide(*args, value: float = 0.0, use_even: bool = False, flipped: bool = False, use_clamp: bool = True, mirror: bool = False, snap: bool = False, snap_elements: typing.Set[str] = {'INCREMENT'}, use_snap_project: bool = False, snap_target: str = 'CLOSEST', use_snap_self: bool = True, use_snap_edit: bool = True, use_snap_nonedit: bool = True, use_snap_selectable: bool = False, snap_point: mathutils.Vector = (0.0, 0.0, 0.0), correct_uv: bool = True, release_confirm: bool = False, use_accurate: bool = False) -> None:

  """

  Slide a vertex along a mesh

  """

  ...

def vertex_random(*args, offset: float = 0.0, uniform: float = 0.0, normal: float = 0.0, seed: int = 0, wait_for_input: bool = True) -> None:

  """

  Randomize vertices

  """

  ...

def vertex_warp(*args, warp_angle: float = 6.28319, offset_angle: float = 0.0, min: float = -1.0, max: float = 1.0, viewmat: mathutils.Matrix = ((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)), center: mathutils.Vector = (0.0, 0.0, 0.0)) -> None:

  """

  Warp vertices around the cursor

  """

  ...
