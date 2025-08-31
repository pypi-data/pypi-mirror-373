"""


Mask Operators
**************

:func:`add_feather_vertex`

:func:`add_feather_vertex_slide`

:func:`add_vertex`

:func:`add_vertex_slide`

:func:`copy_splines`

:func:`cyclic_toggle`

:func:`delete`

:func:`duplicate`

:func:`duplicate_move`

:func:`feather_weight_clear`

:func:`handle_type_set`

:func:`hide_view_clear`

:func:`hide_view_set`

:func:`layer_move`

:func:`layer_new`

:func:`layer_remove`

:func:`new`

:func:`normals_make_consistent`

:func:`parent_clear`

:func:`parent_set`

:func:`paste_splines`

:func:`primitive_circle_add`

:func:`primitive_square_add`

:func:`select`

:func:`select_all`

:func:`select_box`

:func:`select_circle`

:func:`select_lasso`

:func:`select_less`

:func:`select_linked`

:func:`select_linked_pick`

:func:`select_more`

:func:`shape_key_clear`

:func:`shape_key_feather_reset`

:func:`shape_key_insert`

:func:`shape_key_rekey`

:func:`slide_point`

:func:`slide_spline_curvature`

:func:`switch_direction`

"""

import typing

import mathutils

def add_feather_vertex(*args, location: mathutils.Vector = (0.0, 0.0)) -> None:

  """

  Add vertex to feather

  """

  ...

def add_feather_vertex_slide(*args, MASK_OT_add_feather_vertex: MASK_OT_add_feather_vertex = None, MASK_OT_slide_point: MASK_OT_slide_point = None) -> None:

  """

  Add new vertex to feather and slide it

  """

  ...

def add_vertex(*args, location: mathutils.Vector = (0.0, 0.0)) -> None:

  """

  Add vertex to active spline

  """

  ...

def add_vertex_slide(*args, MASK_OT_add_vertex: MASK_OT_add_vertex = None, MASK_OT_slide_point: MASK_OT_slide_point = None) -> None:

  """

  Add new vertex and slide it

  """

  ...

def copy_splines() -> None:

  """

  Copy the selected splines to the internal clipboard

  """

  ...

def cyclic_toggle() -> None:

  """

  Toggle cyclic for selected splines

  """

  ...

def delete(*args, confirm: bool = True) -> None:

  """

  Delete selected control points or splines

  """

  ...

def duplicate() -> None:

  """

  Duplicate selected control points and segments between them

  """

  ...

def duplicate_move(*args, MASK_OT_duplicate: MASK_OT_duplicate = None, TRANSFORM_OT_translate: TRANSFORM_OT_translate = None) -> None:

  """

  Duplicate mask and move

  """

  ...

def feather_weight_clear() -> None:

  """

  Reset the feather weight to zero

  """

  ...

def handle_type_set(*args, type: str = 'AUTO') -> None:

  """

  Set type of handles for selected control points

  """

  ...

def hide_view_clear(*args, select: bool = True) -> None:

  """

  Reveal temporarily hidden mask layers

  """

  ...

def hide_view_set(*args, unselected: bool = False) -> None:

  """

  Temporarily hide mask layers

  """

  ...

def layer_move(*args, direction: str = 'UP') -> None:

  """

  Move the active layer up/down in the list

  """

  ...

def layer_new(*args, name: str = '') -> None:

  """

  Add new mask layer for masking

  """

  ...

def layer_remove() -> None:

  """

  Remove mask layer

  """

  ...

def new(*args, name: str = '') -> None:

  """

  Create new mask

  """

  ...

def normals_make_consistent() -> None:

  """

  Recalculate the direction of selected handles

  """

  ...

def parent_clear() -> None:

  """

  Clear the mask's parenting

  """

  ...

def parent_set() -> None:

  """

  Set the mask's parenting

  """

  ...

def paste_splines() -> None:

  """

  Paste splines from the internal clipboard

  """

  ...

def primitive_circle_add(*args, size: float = 100.0, location: mathutils.Vector = (0.0, 0.0)) -> None:

  """

  Add new circle-shaped spline

  """

  ...

def primitive_square_add(*args, size: float = 100.0, location: mathutils.Vector = (0.0, 0.0)) -> None:

  """

  Add new square-shaped spline

  """

  ...

def select(*args, extend: bool = False, deselect: bool = False, toggle: bool = False, deselect_all: bool = False, select_passthrough: bool = False, location: mathutils.Vector = (0.0, 0.0)) -> None:

  """

  Select spline points

  """

  ...

def select_all(*args, action: str = 'TOGGLE') -> None:

  """

  Change selection of all curve points

  """

  ...

def select_box(*args, xmin: int = 0, xmax: int = 0, ymin: int = 0, ymax: int = 0, wait_for_input: bool = True, mode: str = 'SET') -> None:

  """

  Select curve points using box selection

  """

  ...

def select_circle(*args, x: int = 0, y: int = 0, radius: int = 25, wait_for_input: bool = True, mode: str = 'SET') -> None:

  """

  Select curve points using circle selection

  """

  ...

def select_lasso(*args, path: typing.Union[typing.Sequence[OperatorMousePath], typing.Mapping[str, OperatorMousePath], bpy.types.bpy_prop_collection] = None, use_smooth_stroke: bool = False, smooth_stroke_factor: float = 0.75, smooth_stroke_radius: int = 35, mode: str = 'SET') -> None:

  """

  Select curve points using lasso selection

  """

  ...

def select_less() -> None:

  """

  Deselect spline points at the boundary of each selection region

  """

  ...

def select_linked() -> None:

  """

  Select all curve points linked to already selected ones

  """

  ...

def select_linked_pick(*args, deselect: bool = False) -> None:

  """

  (De)select all points linked to the curve under the mouse cursor

  """

  ...

def select_more() -> None:

  """

  Select more spline points connected to initial selection

  """

  ...

def shape_key_clear() -> None:

  """

  Remove mask shape keyframe for active mask layer at the current frame

  """

  ...

def shape_key_feather_reset() -> None:

  """

  Reset feather weights on all selected points animation values

  """

  ...

def shape_key_insert() -> None:

  """

  Insert mask shape keyframe for active mask layer at the current frame

  """

  ...

def shape_key_rekey(*args, location: bool = True, feather: bool = True) -> None:

  """

  Recalculate animation data on selected points for frames selected in the dopesheet

  """

  ...

def slide_point(*args, slide_feather: bool = False, is_new_point: bool = False) -> None:

  """

  Slide control points

  """

  ...

def slide_spline_curvature() -> None:

  """

  Slide a point on the spline to define its curvature

  """

  ...

def switch_direction() -> None:

  """

  Switch direction of selected splines

  """

  ...
