"""


Sculpt Operators
****************

:func:`brush_stroke`

:func:`cloth_filter`

:func:`color_filter`

:func:`detail_flood_fill`

:func:`dynamic_topology_toggle`

:func:`dyntopo_detail_size_edit`

:func:`expand`

:func:`face_set_box_gesture`

:func:`face_set_change_visibility`

:func:`face_set_edit`

:func:`face_set_extract`

:func:`face_set_lasso_gesture`

:func:`face_set_line_gesture`

:func:`face_set_polyline_gesture`

:func:`face_sets_create`

:func:`face_sets_init`

:func:`face_sets_randomize_colors`

:func:`mask_by_color`

:func:`mask_filter`

:func:`mask_from_boundary`

:func:`mask_from_cavity`

:func:`mask_init`

:func:`mesh_filter`

:func:`optimize`

:func:`paint_mask_extract`

:func:`paint_mask_slice`

:func:`project_line_gesture`

:func:`sample_color`

:func:`sample_detail_size`

:func:`sculptmode_toggle`

:func:`set_persistent_base`

:func:`set_pivot_position`

:func:`symmetrize`

:func:`trim_box_gesture`

:func:`trim_lasso_gesture`

:func:`trim_line_gesture`

:func:`trim_polyline_gesture`

:func:`uv_sculpt_grab`

:func:`uv_sculpt_pinch`

:func:`uv_sculpt_relax`

"""

import typing

import mathutils

def brush_stroke(*args, stroke: typing.Union[typing.Sequence[OperatorStrokeElement], typing.Mapping[str, OperatorStrokeElement], bpy.types.bpy_prop_collection] = None, mode: str = 'NORMAL', pen_flip: bool = False, override_location: bool = False, ignore_background_click: bool = False) -> None:

  """

  Sculpt a stroke into the geometry

  """

  ...

def cloth_filter(*args, start_mouse: typing.Tuple[int, int] = (0, 0), area_normal_radius: float = 0.25, strength: float = 1.0, iteration_count: int = 1, event_history: typing.Union[typing.Sequence[OperatorStrokeElement], typing.Mapping[str, OperatorStrokeElement], bpy.types.bpy_prop_collection] = None, type: str = 'GRAVITY', force_axis: typing.Set[str] = {'X', 'Y', 'Z'}, orientation: str = 'LOCAL', cloth_mass: float = 1.0, cloth_damping: float = 0.0, use_face_sets: bool = False, use_collisions: bool = False) -> None:

  """

  Applies a cloth simulation deformation to the entire mesh

  """

  ...

def color_filter(*args, start_mouse: typing.Tuple[int, int] = (0, 0), area_normal_radius: float = 0.25, strength: float = 1.0, iteration_count: int = 1, event_history: typing.Union[typing.Sequence[OperatorStrokeElement], typing.Mapping[str, OperatorStrokeElement], bpy.types.bpy_prop_collection] = None, type: str = 'FILL', fill_color: mathutils.Color = (1.0, 1.0, 1.0)) -> None:

  """

  Applies a filter to modify the active color attribute

  """

  ...

def detail_flood_fill() -> None:

  """

  Flood fill the mesh with the selected detail setting

  """

  ...

def dynamic_topology_toggle() -> None:

  """

  Dynamic topology alters the mesh topology while sculpting

  """

  ...

def dyntopo_detail_size_edit() -> None:

  """

  Modify the detail size of dyntopo interactively

  """

  ...

def expand(*args, target: str = 'MASK', falloff_type: str = 'GEODESIC', invert: bool = False, use_mask_preserve: bool = False, use_falloff_gradient: bool = False, use_modify_active: bool = False, use_reposition_pivot: bool = True, max_geodesic_move_preview: int = 10000, use_auto_mask: bool = False, normal_falloff_smooth: int = 2) -> None:

  """

  Generic sculpt expand operator

  """

  ...

def face_set_box_gesture(*args, xmin: int = 0, xmax: int = 0, ymin: int = 0, ymax: int = 0, wait_for_input: bool = True, use_front_faces_only: bool = False) -> None:

  """

  Add a face set in a rectangle defined by the cursor

  """

  ...

def face_set_change_visibility(*args, mode: str = 'TOGGLE') -> None:

  """

  Change the visibility of the Face Sets of the sculpt

  """

  ...

def face_set_edit(*args, active_face_set: int = 1, mode: str = 'GROW', strength: float = 1.0, modify_hidden: bool = False) -> None:

  """

  Edits the current active Face Set

  """

  ...

def face_set_extract(*args, add_boundary_loop: bool = True, smooth_iterations: int = 4, apply_shrinkwrap: bool = True, add_solidify: bool = True) -> None:

  """

  Create a new mesh object from the selected Face Set

  """

  ...

def face_set_lasso_gesture(*args, path: typing.Union[typing.Sequence[OperatorMousePath], typing.Mapping[str, OperatorMousePath], bpy.types.bpy_prop_collection] = None, use_smooth_stroke: bool = False, smooth_stroke_factor: float = 0.75, smooth_stroke_radius: int = 35, use_front_faces_only: bool = False) -> None:

  """

  Add a face set in a shape defined by the cursor

  """

  ...

def face_set_line_gesture(*args, xstart: int = 0, xend: int = 0, ystart: int = 0, yend: int = 0, flip: bool = False, cursor: int = 5, use_front_faces_only: bool = False, use_limit_to_segment: bool = False) -> None:

  """

  Add a face set to one side of a line defined by the cursor

  """

  ...

def face_set_polyline_gesture(*args, path: typing.Union[typing.Sequence[OperatorMousePath], typing.Mapping[str, OperatorMousePath], bpy.types.bpy_prop_collection] = None, use_front_faces_only: bool = False) -> None:

  """

  Add a face set in a shape defined by the cursor

  """

  ...

def face_sets_create(*args, mode: str = 'MASKED') -> None:

  """

  Create a new Face Set

  """

  ...

def face_sets_init(*args, mode: str = 'LOOSE_PARTS', threshold: float = 0.5) -> None:

  """

  Initializes all Face Sets in the mesh

  """

  ...

def face_sets_randomize_colors() -> None:

  """

  Generates a new set of random colors to render the Face Sets in the viewport

  """

  ...

def mask_by_color(*args, contiguous: bool = False, invert: bool = False, preserve_previous_mask: bool = False, threshold: float = 0.35, location: typing.Tuple[int, int] = (0, 0)) -> None:

  """

  Creates a mask based on the active color attribute

  """

  ...

def mask_filter(*args, filter_type: str = 'SMOOTH', iterations: int = 1, auto_iteration_count: bool = True) -> None:

  """

  Applies a filter to modify the current mask

  """

  ...

def mask_from_boundary(*args, mix_mode: str = 'MIX', mix_factor: float = 1.0, settings_source: str = 'OPERATOR', boundary_mode: str = 'MESH', propagation_steps: int = 1) -> None:

  """

  Creates a mask based on the boundaries of the surface

  """

  ...

def mask_from_cavity(*args, mix_mode: str = 'MIX', mix_factor: float = 1.0, settings_source: str = 'OPERATOR', factor: float = 0.5, blur_steps: int = 2, use_curve: bool = False, invert: bool = False) -> None:

  """

  Creates a mask based on the curvature of the surface

  """

  ...

def mask_init(*args, mode: str = 'RANDOM_PER_VERTEX') -> None:

  """

  Creates a new mask for the entire mesh

  """

  ...

def mesh_filter(*args, start_mouse: typing.Tuple[int, int] = (0, 0), area_normal_radius: float = 0.25, strength: float = 1.0, iteration_count: int = 1, event_history: typing.Union[typing.Sequence[OperatorStrokeElement], typing.Mapping[str, OperatorStrokeElement], bpy.types.bpy_prop_collection] = None, type: str = 'INFLATE', deform_axis: typing.Set[str] = {'X', 'Y', 'Z'}, orientation: str = 'LOCAL', surface_smooth_shape_preservation: float = 0.5, surface_smooth_current_vertex: float = 0.5, sharpen_smooth_ratio: float = 0.35, sharpen_intensify_detail_strength: float = 0.0, sharpen_curvature_smooth_iterations: int = 0) -> None:

  """

  Applies a filter to modify the current mesh

  """

  ...

def optimize() -> None:

  """

  Recalculate the sculpt BVH to improve performance

  """

  ...

def paint_mask_extract(*args, mask_threshold: float = 0.5, add_boundary_loop: bool = True, smooth_iterations: int = 4, apply_shrinkwrap: bool = True, add_solidify: bool = True) -> None:

  """

  Create a new mesh object from the current paint mask

  """

  ...

def paint_mask_slice(*args, mask_threshold: float = 0.5, fill_holes: bool = True, new_object: bool = True) -> None:

  """

  Slices the paint mask from the mesh

  """

  ...

def project_line_gesture(*args, xstart: int = 0, xend: int = 0, ystart: int = 0, yend: int = 0, flip: bool = False, cursor: int = 5, use_front_faces_only: bool = False, use_limit_to_segment: bool = False) -> None:

  """

  Project the geometry onto a plane defined by a line

  """

  ...

def sample_color() -> None:

  """

  Sample the vertex color of the active vertex

  """

  ...

def sample_detail_size(*args, location: typing.Tuple[int, int] = (0, 0), mode: str = 'DYNTOPO') -> None:

  """

  Sample the mesh detail on clicked point

  """

  ...

def sculptmode_toggle() -> None:

  """

  Toggle sculpt mode in 3D view

  """

  ...

def set_persistent_base() -> None:

  """

  Reset the copy of the mesh that is being sculpted on

  """

  ...

def set_pivot_position(*args, mode: str = 'UNMASKED', mouse_x: float = 0.0, mouse_y: float = 0.0) -> None:

  """

  Sets the sculpt transform pivot position

  """

  ...

def symmetrize(*args, merge_tolerance: float = 0.0005) -> None:

  """

  Symmetrize the topology modifications

  """

  ...

def trim_box_gesture(*args, xmin: int = 0, xmax: int = 0, ymin: int = 0, ymax: int = 0, wait_for_input: bool = True, use_front_faces_only: bool = False, location: typing.Tuple[int, int] = (0, 0), trim_mode: str = 'DIFFERENCE', use_cursor_depth: bool = False, trim_orientation: str = 'VIEW', trim_extrude_mode: str = 'FIXED', trim_solver: str = 'MANIFOLD') -> None:

  """

  Execute a boolean operation on the mesh and a rectangle defined by the cursor

  """

  ...

def trim_lasso_gesture(*args, path: typing.Union[typing.Sequence[OperatorMousePath], typing.Mapping[str, OperatorMousePath], bpy.types.bpy_prop_collection] = None, use_smooth_stroke: bool = False, smooth_stroke_factor: float = 0.75, smooth_stroke_radius: int = 35, use_front_faces_only: bool = False, location: typing.Tuple[int, int] = (0, 0), trim_mode: str = 'DIFFERENCE', use_cursor_depth: bool = False, trim_orientation: str = 'VIEW', trim_extrude_mode: str = 'FIXED', trim_solver: str = 'MANIFOLD') -> None:

  """

  Execute a boolean operation on the mesh and a shape defined by the cursor

  """

  ...

def trim_line_gesture(*args, xstart: int = 0, xend: int = 0, ystart: int = 0, yend: int = 0, flip: bool = False, cursor: int = 5, use_front_faces_only: bool = False, use_limit_to_segment: bool = False, location: typing.Tuple[int, int] = (0, 0), trim_mode: str = 'DIFFERENCE', use_cursor_depth: bool = False, trim_orientation: str = 'VIEW', trim_extrude_mode: str = 'FIXED', trim_solver: str = 'MANIFOLD') -> None:

  """

  Remove a portion of the mesh on one side of a line

  """

  ...

def trim_polyline_gesture(*args, path: typing.Union[typing.Sequence[OperatorMousePath], typing.Mapping[str, OperatorMousePath], bpy.types.bpy_prop_collection] = None, use_front_faces_only: bool = False, location: typing.Tuple[int, int] = (0, 0), trim_mode: str = 'DIFFERENCE', use_cursor_depth: bool = False, trim_orientation: str = 'VIEW', trim_extrude_mode: str = 'FIXED', trim_solver: str = 'MANIFOLD') -> None:

  """

  Execute a boolean operation on the mesh and a polygonal shape defined by the cursor

  """

  ...

def uv_sculpt_grab(*args, use_invert: bool = False) -> None:

  """

  Grab UVs

  """

  ...

def uv_sculpt_pinch(*args, use_invert: bool = False) -> None:

  """

  Pinch UVs

  """

  ...

def uv_sculpt_relax(*args, use_invert: bool = False, relax_method: str = 'COTAN') -> None:

  """

  Relax UVs

  """

  ...
