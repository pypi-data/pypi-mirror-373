"""


View3D Operators
****************

:func:`bone_select_menu`

:func:`camera_background_image_add`

:func:`camera_background_image_remove`

:func:`camera_to_view`

:func:`camera_to_view_selected`

:func:`clear_render_border`

:func:`clip_border`

:func:`copybuffer`

:func:`cursor3d`

:func:`dolly`

:func:`drop_world`

:func:`edit_mesh_extrude_individual_move`

:func:`edit_mesh_extrude_manifold_normal`

:func:`edit_mesh_extrude_move_normal`

:func:`edit_mesh_extrude_move_shrink_fatten`

:func:`fly`

:func:`game_start`

:func:`interactive_add`

:func:`localview`

:func:`localview_remove_from`

:func:`move`

:func:`navigate`

:func:`ndof_all`

:func:`ndof_orbit`

:func:`ndof_orbit_zoom`

:func:`ndof_pan`

:func:`object_as_camera`

:func:`object_mode_pie_or_toggle`

:func:`pastebuffer`

:func:`render_border`

:func:`rotate`

:func:`ruler_add`

:func:`ruler_remove`

:func:`select`

:func:`select_box`

:func:`select_circle`

:func:`select_lasso`

:func:`select_menu`

:func:`smoothview`

:func:`snap_cursor_to_active`

:func:`snap_cursor_to_center`

:func:`snap_cursor_to_grid`

:func:`snap_cursor_to_selected`

:func:`snap_selected_to_active`

:func:`snap_selected_to_cursor`

:func:`snap_selected_to_grid`

:func:`toggle_matcap_flip`

:func:`toggle_shading`

:func:`toggle_xray`

:func:`transform_gizmo_set`

:func:`view_all`

:func:`view_axis`

:func:`view_camera`

:func:`view_center_camera`

:func:`view_center_cursor`

:func:`view_center_lock`

:func:`view_center_pick`

:func:`view_lock_clear`

:func:`view_lock_to_active`

:func:`view_orbit`

:func:`view_pan`

:func:`view_persportho`

:func:`view_roll`

:func:`view_selected`

:func:`walk`

:func:`zoom`

:func:`zoom_border`

:func:`zoom_camera_1_to_1`

"""

import typing

def bone_select_menu(*args, name: str = '', extend: bool = False, deselect: bool = False, toggle: bool = False) -> None:

  """

  Menu bone selection

  """

  ...

def camera_background_image_add(*args, filepath: str = '', relative_path: bool = True, name: str = '', session_uid: int = 0) -> None:

  """

  Add a new background image to the active camera

  """

  ...

def camera_background_image_remove(*args, index: int = 0) -> None:

  """

  Remove a background image from the camera

  """

  ...

def camera_to_view() -> None:

  """

  Set camera view to active view

  """

  ...

def camera_to_view_selected() -> None:

  """

  Move the camera so selected objects are framed

  """

  ...

def clear_render_border() -> None:

  """

  Clear the boundaries of the border render and disable border render

  """

  ...

def clip_border(*args, xmin: int = 0, xmax: int = 0, ymin: int = 0, ymax: int = 0, wait_for_input: bool = True) -> None:

  """

  Set the view clipping region

  """

  ...

def copybuffer() -> None:

  """

  Copy the selected objects to the internal clipboard

  """

  ...

def cursor3d(*args, use_depth: bool = True, orientation: str = 'VIEW') -> None:

  """

  Set the location of the 3D cursor

  """

  ...

def dolly(*args, mx: int = 0, my: int = 0, delta: int = 0, use_cursor_init: bool = True) -> None:

  """

  Dolly in/out in the view

  """

  ...

def drop_world(*args, name: str = '', session_uid: int = 0) -> None:

  """

  Drop a world into the scene

  """

  ...

def edit_mesh_extrude_individual_move() -> None:

  """

  Extrude each individual face separately along local normals

  """

  ...

def edit_mesh_extrude_manifold_normal() -> None:

  """

  Extrude manifold region along normals

  """

  ...

def edit_mesh_extrude_move_normal(*args, dissolve_and_intersect: bool = False) -> None:

  """

  Extrude region together along the average normal

  """

  ...

def edit_mesh_extrude_move_shrink_fatten() -> None:

  """

  Extrude region together along local normals

  """

  ...

def fly() -> None:

  """

  Interactively fly around the scene

  """

  ...

def game_start() -> None:

  """

  Start game engine

  """

  ...

def interactive_add(*args, primitive_type: str = 'CUBE', plane_origin_base: str = 'EDGE', plane_origin_depth: str = 'EDGE', plane_aspect_base: str = 'FREE', plane_aspect_depth: str = 'FREE', wait_for_input: bool = True) -> None:

  """

  Interactively add an object

  """

  ...

def localview(*args, frame_selected: bool = True) -> None:

  """

  Toggle display of selected object(s) separately and centered in view

  """

  ...

def localview_remove_from() -> None:

  """

  Move selected objects out of local view

  """

  ...

def move(*args, use_cursor_init: bool = True) -> None:

  """

  Move the view

  """

  ...

def navigate() -> None:

  """

  Interactively navigate around the scene (uses the mode (walk/fly) preference)

  """

  ...

def ndof_all() -> None:

  """

  Pan and rotate the view with the 3D mouse

  """

  ...

def ndof_orbit() -> None:

  """

  Orbit the view using the 3D mouse

  """

  ...

def ndof_orbit_zoom() -> None:

  """

  Orbit and zoom the view using the 3D mouse

  """

  ...

def ndof_pan() -> None:

  """

  Pan the view with the 3D mouse

  """

  ...

def object_as_camera() -> None:

  """

  Set the active object as the active camera for this view or scene

  """

  ...

def object_mode_pie_or_toggle() -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def pastebuffer(*args, autoselect: bool = True, active_collection: bool = True) -> None:

  """

  Paste objects from the internal clipboard

  """

  ...

def render_border(*args, xmin: int = 0, xmax: int = 0, ymin: int = 0, ymax: int = 0, wait_for_input: bool = True) -> None:

  """

  Set the boundaries of the border render and enable border render

  """

  ...

def rotate(*args, use_cursor_init: bool = True) -> None:

  """

  Rotate the view

  """

  ...

def ruler_add() -> None:

  """

  Add ruler

  """

  ...

def ruler_remove() -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def select(*args, extend: bool = False, deselect: bool = False, toggle: bool = False, deselect_all: bool = False, select_passthrough: bool = False, center: bool = False, enumerate: bool = False, object: bool = False, location: typing.Tuple[int, int] = (0, 0)) -> None:

  """

  Select and activate item(s)

  """

  ...

def select_box(*args, xmin: int = 0, xmax: int = 0, ymin: int = 0, ymax: int = 0, wait_for_input: bool = True, mode: str = 'SET') -> None:

  """

  Select items using box selection

  """

  ...

def select_circle(*args, x: int = 0, y: int = 0, radius: int = 25, wait_for_input: bool = True, mode: str = 'SET') -> None:

  """

  Select items using circle selection

  """

  ...

def select_lasso(*args, path: typing.Union[typing.Sequence[OperatorMousePath], typing.Mapping[str, OperatorMousePath], bpy.types.bpy_prop_collection] = None, use_smooth_stroke: bool = False, smooth_stroke_factor: float = 0.75, smooth_stroke_radius: int = 35, mode: str = 'SET') -> None:

  """

  Select items using lasso selection

  """

  ...

def select_menu(*args, name: str = '', extend: bool = False, deselect: bool = False, toggle: bool = False) -> None:

  """

  Menu object selection

  """

  ...

def smoothview() -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def snap_cursor_to_active() -> None:

  """

  Snap 3D cursor to the active item

  """

  ...

def snap_cursor_to_center() -> None:

  """

  Snap 3D cursor to the world origin

  """

  ...

def snap_cursor_to_grid() -> None:

  """

  Snap 3D cursor to the nearest grid division

  """

  ...

def snap_cursor_to_selected() -> None:

  """

  Snap 3D cursor to the middle of the selected item(s)

  """

  ...

def snap_selected_to_active() -> None:

  """

  Snap selected item(s) to the active item

  """

  ...

def snap_selected_to_cursor(*args, use_offset: bool = True, use_rotation: bool = False) -> None:

  """

  Snap selected item(s) to the 3D cursor

  """

  ...

def snap_selected_to_grid() -> None:

  """

  Snap selected item(s) to their nearest grid division

  """

  ...

def toggle_matcap_flip() -> None:

  """

  Flip MatCap

  """

  ...

def toggle_shading(*args, type: str = 'WIREFRAME') -> None:

  """

  Toggle shading type in 3D viewport

  """

  ...

def toggle_xray() -> None:

  """

  Transparent scene display. Allow selecting through items

  """

  ...

def transform_gizmo_set(*args, extend: bool = False, type: typing.Set[str] = {}) -> None:

  """

  Set the current transform gizmo

  """

  ...

def view_all(*args, use_all_regions: bool = False, center: bool = False) -> None:

  """

  View all objects in scene

  """

  ...

def view_axis(*args, type: str = 'LEFT', align_active: bool = False, relative: bool = False) -> None:

  """

  Use a preset viewpoint

  """

  ...

def view_camera() -> None:

  """

  Toggle the camera view

  """

  ...

def view_center_camera() -> None:

  """

  Center the camera view, resizing the view to fit its bounds

  """

  ...

def view_center_cursor() -> None:

  """

  Center the view so that the cursor is in the middle of the view

  """

  ...

def view_center_lock() -> None:

  """

  Center the view lock offset

  """

  ...

def view_center_pick() -> None:

  """

  Center the view to the Z-depth position under the mouse cursor

  """

  ...

def view_lock_clear() -> None:

  """

  Clear all view locking

  """

  ...

def view_lock_to_active() -> None:

  """

  Lock the view to the active object/bone

  """

  ...

def view_orbit(*args, angle: float = 0.0, type: str = 'ORBITLEFT') -> None:

  """

  Orbit the view

  """

  ...

def view_pan(*args, type: str = 'PANLEFT') -> None:

  """

  Pan the view in a given direction

  """

  ...

def view_persportho() -> None:

  """

  Switch the current view from perspective/orthographic projection

  """

  ...

def view_roll(*args, angle: float = 0.0, type: str = 'ANGLE') -> None:

  """

  Roll the view

  """

  ...

def view_selected(*args, use_all_regions: bool = False) -> None:

  """

  Move the view to the selection center

  """

  ...

def walk() -> None:

  """

  Interactively walk around the scene

  """

  ...

def zoom(*args, mx: int = 0, my: int = 0, delta: int = 0, use_cursor_init: bool = True) -> None:

  """

  Zoom in/out in the view

  """

  ...

def zoom_border(*args, xmin: int = 0, xmax: int = 0, ymin: int = 0, ymax: int = 0, wait_for_input: bool = True, zoom_out: bool = False) -> None:

  """

  Zoom in the view to the nearest object contained in the border

  """

  ...

def zoom_camera_1_to_1() -> None:

  """

  Match the camera to 1:1 to the render output

  """

  ...
