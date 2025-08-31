"""


Curves Operators
****************

:func:`add_bezier`

:func:`add_circle`

:func:`attribute_set`

:func:`convert_from_particle_system`

:func:`convert_to_particle_system`

:func:`curve_type_set`

:func:`cyclic_toggle`

:func:`delete`

:func:`draw`

:func:`duplicate`

:func:`duplicate_move`

:func:`extrude`

:func:`extrude_move`

:func:`handle_type_set`

:func:`sculptmode_toggle`

:func:`select_all`

:func:`select_ends`

:func:`select_less`

:func:`select_linked`

:func:`select_linked_pick`

:func:`select_more`

:func:`select_random`

:func:`separate`

:func:`set_selection_domain`

:func:`snap_curves_to_surface`

:func:`split`

:func:`subdivide`

:func:`surface_set`

:func:`switch_direction`

:func:`tilt_clear`

"""

import typing

import mathutils

def add_bezier(*args, radius: float = 1.0, enter_editmode: bool = False, align: str = 'WORLD', location: mathutils.Vector = (0.0, 0.0, 0.0), rotation: mathutils.Euler = (0.0, 0.0, 0.0), scale: mathutils.Vector = (0.0, 0.0, 0.0)) -> None:

  """

  Add new bezier curve

  """

  ...

def add_circle(*args, radius: float = 1.0, enter_editmode: bool = False, align: str = 'WORLD', location: mathutils.Vector = (0.0, 0.0, 0.0), rotation: mathutils.Euler = (0.0, 0.0, 0.0), scale: mathutils.Vector = (0.0, 0.0, 0.0)) -> None:

  """

  Add new circle curve

  """

  ...

def attribute_set(*args, value_float: float = 0.0, value_float_vector_2d: typing.Tuple[float, float] = (0.0, 0.0), value_float_vector_3d: typing.Tuple[float, float, float] = (0.0, 0.0, 0.0), value_int: int = 0, value_int_vector_2d: typing.Tuple[int, int] = (0, 0), value_color: typing.Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0), value_bool: bool = False) -> None:

  """

  Set values of the active attribute for selected elements

  """

  ...

def convert_from_particle_system() -> None:

  """

  Add a new curves object based on the current state of the particle system

  """

  ...

def convert_to_particle_system() -> None:

  """

  Add a new or update an existing hair particle system on the surface object

  """

  ...

def curve_type_set(*args, type: str = 'POLY', use_handles: bool = False) -> None:

  """

  Set type of selected curves

  """

  ...

def cyclic_toggle() -> None:

  """

  Make active curve closed/opened loop

  """

  ...

def delete() -> None:

  """

  Remove selected control points or curves

  """

  ...

def draw(*args, error_threshold: float = 0.0, fit_method: str = 'REFIT', corner_angle: float = 1.22173, use_cyclic: bool = True, stroke: typing.Union[typing.Sequence[OperatorStrokeElement], typing.Mapping[str, OperatorStrokeElement], bpy.types.bpy_prop_collection] = None, wait_for_input: bool = True, is_curve_2d: bool = False, bezier_as_nurbs: bool = False) -> None:

  """

  Draw a freehand curve

  """

  ...

def duplicate() -> None:

  """

  Copy selected points or curves

  """

  ...

def duplicate_move(*args, CURVES_OT_duplicate: CURVES_OT_duplicate = None, TRANSFORM_OT_translate: TRANSFORM_OT_translate = None) -> None:

  """

  Make copies of selected elements and move them

  """

  ...

def extrude() -> None:

  """

  Extrude selected control point(s)

  """

  ...

def extrude_move(*args, CURVES_OT_extrude: CURVES_OT_extrude = None, TRANSFORM_OT_translate: TRANSFORM_OT_translate = None) -> None:

  """

  Extrude curve and move result

  """

  ...

def handle_type_set(*args, type: str = 'AUTO') -> None:

  """

  Set the handle type for bezier curves

  """

  ...

def sculptmode_toggle() -> None:

  """

  Enter/Exit sculpt mode for curves

  """

  ...

def select_all(*args, action: str = 'TOGGLE') -> None:

  """

  (De)select all control points

  """

  ...

def select_ends(*args, amount_start: int = 0, amount_end: int = 1) -> None:

  """

  Select end points of curves

  """

  ...

def select_less() -> None:

  """

  Shrink the selection by one point

  """

  ...

def select_linked() -> None:

  """

  Select all points in curves with any point selection

  """

  ...

def select_linked_pick(*args, deselect: bool = False) -> None:

  """

  Select all points in the curve under the cursor

  """

  ...

def select_more() -> None:

  """

  Grow the selection by one point

  """

  ...

def select_random(*args, seed: int = 0, probability: float = 0.5) -> None:

  """

  Randomizes existing selection or create new random selection

  """

  ...

def separate() -> None:

  """

  Separate selected geometry into a new object

  """

  ...

def set_selection_domain(*args, domain: str = 'POINT') -> None:

  """

  Change the mode used for selection masking in curves sculpt mode

  """

  ...

def snap_curves_to_surface(*args, attach_mode: str = 'NEAREST') -> None:

  """

  Move curves so that the first point is exactly on the surface mesh

  """

  ...

def split() -> None:

  """

  Split selected points

  """

  ...

def subdivide(*args, number_cuts: int = 1) -> None:

  """

  Subdivide selected curve segments

  """

  ...

def surface_set() -> None:

  """

  Use the active object as surface for selected curves objects and set it as the parent

  """

  ...

def switch_direction() -> None:

  """

  Reverse the direction of the selected curves

  """

  ...

def tilt_clear() -> None:

  """

  Clear the tilt of selected control points

  """

  ...
