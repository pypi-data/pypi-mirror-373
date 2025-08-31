"""


Paint Operators
***************

:func:`add_simple_uvs`

:func:`add_texture_paint_slot`

:func:`brush_colors_flip`

:func:`face_select_all`

:func:`face_select_hide`

:func:`face_select_less`

:func:`face_select_linked`

:func:`face_select_linked_pick`

:func:`face_select_loop`

:func:`face_select_more`

:func:`face_vert_reveal`

:func:`grab_clone`

:func:`hide_show`

:func:`hide_show_all`

:func:`hide_show_lasso_gesture`

:func:`hide_show_line_gesture`

:func:`hide_show_masked`

:func:`hide_show_polyline_gesture`

:func:`image_from_view`

:func:`image_paint`

:func:`mask_box_gesture`

:func:`mask_flood_fill`

:func:`mask_lasso_gesture`

:func:`mask_line_gesture`

:func:`mask_polyline_gesture`

:func:`project_image`

:func:`sample_color`

:func:`texture_paint_toggle`

:func:`vert_select_all`

:func:`vert_select_hide`

:func:`vert_select_less`

:func:`vert_select_linked`

:func:`vert_select_linked_pick`

:func:`vert_select_more`

:func:`vert_select_ungrouped`

:func:`vertex_color_brightness_contrast`

:func:`vertex_color_dirt`

:func:`vertex_color_from_weight`

:func:`vertex_color_hsv`

:func:`vertex_color_invert`

:func:`vertex_color_levels`

:func:`vertex_color_set`

:func:`vertex_color_smooth`

:func:`vertex_paint`

:func:`vertex_paint_toggle`

:func:`visibility_filter`

:func:`visibility_invert`

:func:`weight_from_bones`

:func:`weight_gradient`

:func:`weight_paint`

:func:`weight_paint_toggle`

:func:`weight_sample`

:func:`weight_sample_group`

:func:`weight_set`

"""

import typing

import mathutils

def add_simple_uvs() -> None:

  """

  Add cube map UVs on mesh

  """

  ...

def add_texture_paint_slot(*args, type: str = 'BASE_COLOR', slot_type: str = 'IMAGE', name: str = 'Untitled', color: typing.Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0), width: int = 1024, height: int = 1024, alpha: bool = True, generated_type: str = 'BLANK', float: bool = False, domain: str = 'POINT', data_type: str = 'FLOAT_COLOR') -> None:

  """

  Add a paint slot

  """

  ...

def brush_colors_flip() -> None:

  """

  Swap primary and secondary brush colors

  """

  ...

def face_select_all(*args, action: str = 'TOGGLE') -> None:

  """

  Change selection for all faces

  """

  ...

def face_select_hide(*args, unselected: bool = False) -> None:

  """

  Hide selected faces

  """

  ...

def face_select_less(*args, face_step: bool = True) -> None:

  """

  Deselect Faces connected to existing selection

  """

  ...

def face_select_linked() -> None:

  """

  Select linked faces

  """

  ...

def face_select_linked_pick(*args, deselect: bool = False) -> None:

  """

  Select linked faces under the cursor

  """

  ...

def face_select_loop(*args, select: bool = True, extend: bool = False) -> None:

  """

  Select face loop under the cursor

  """

  ...

def face_select_more(*args, face_step: bool = True) -> None:

  """

  Select Faces connected to existing selection

  """

  ...

def face_vert_reveal(*args, select: bool = True) -> None:

  """

  Reveal hidden faces and vertices

  """

  ...

def grab_clone(*args, delta: mathutils.Vector = (0.0, 0.0)) -> None:

  """

  Move the clone source image

  """

  ...

def hide_show(*args, xmin: int = 0, xmax: int = 0, ymin: int = 0, ymax: int = 0, wait_for_input: bool = True, action: str = 'HIDE', area: str = 'Inside', use_front_faces_only: bool = False) -> None:

  """

  Hide/show some vertices

  """

  ...

def hide_show_all(*args, action: str = 'HIDE') -> None:

  """

  Hide/show all vertices

  """

  ...

def hide_show_lasso_gesture(*args, path: typing.Union[typing.Sequence[OperatorMousePath], typing.Mapping[str, OperatorMousePath], bpy.types.bpy_prop_collection] = None, use_smooth_stroke: bool = False, smooth_stroke_factor: float = 0.75, smooth_stroke_radius: int = 35, action: str = 'HIDE', area: str = 'Inside', use_front_faces_only: bool = False) -> None:

  """

  Hide/show some vertices

  """

  ...

def hide_show_line_gesture(*args, xstart: int = 0, xend: int = 0, ystart: int = 0, yend: int = 0, flip: bool = False, cursor: int = 5, action: str = 'HIDE', area: str = 'Inside', use_front_faces_only: bool = False, use_limit_to_segment: bool = False) -> None:

  """

  Hide/show some vertices

  """

  ...

def hide_show_masked(*args, action: str = 'HIDE') -> None:

  """

  Hide/show all masked vertices above a threshold

  """

  ...

def hide_show_polyline_gesture(*args, path: typing.Union[typing.Sequence[OperatorMousePath], typing.Mapping[str, OperatorMousePath], bpy.types.bpy_prop_collection] = None, action: str = 'HIDE', area: str = 'Inside', use_front_faces_only: bool = False) -> None:

  """

  Hide/show some vertices

  """

  ...

def image_from_view(*args, filepath: str = '') -> None:

  """

  Make an image from biggest 3D view for reprojection

  """

  ...

def image_paint(*args, stroke: typing.Union[typing.Sequence[OperatorStrokeElement], typing.Mapping[str, OperatorStrokeElement], bpy.types.bpy_prop_collection] = None, mode: str = 'NORMAL', pen_flip: bool = False) -> None:

  """

  Paint a stroke into the image

  """

  ...

def mask_box_gesture(*args, xmin: int = 0, xmax: int = 0, ymin: int = 0, ymax: int = 0, wait_for_input: bool = True, use_front_faces_only: bool = False, mode: str = 'VALUE', value: float = 1.0) -> None:

  """

  Mask within a rectangle defined by the cursor

  """

  ...

def mask_flood_fill(*args, mode: str = 'VALUE', value: float = 0.0) -> None:

  """

  Fill the whole mask with a given value, or invert its values

  """

  ...

def mask_lasso_gesture(*args, path: typing.Union[typing.Sequence[OperatorMousePath], typing.Mapping[str, OperatorMousePath], bpy.types.bpy_prop_collection] = None, use_smooth_stroke: bool = False, smooth_stroke_factor: float = 0.75, smooth_stroke_radius: int = 35, use_front_faces_only: bool = False, mode: str = 'VALUE', value: float = 1.0) -> None:

  """

  Mask within a shape defined by the cursor

  """

  ...

def mask_line_gesture(*args, xstart: int = 0, xend: int = 0, ystart: int = 0, yend: int = 0, flip: bool = False, cursor: int = 5, use_front_faces_only: bool = False, use_limit_to_segment: bool = False, mode: str = 'VALUE', value: float = 1.0) -> None:

  """

  Mask to one side of a line defined by the cursor

  """

  ...

def mask_polyline_gesture(*args, path: typing.Union[typing.Sequence[OperatorMousePath], typing.Mapping[str, OperatorMousePath], bpy.types.bpy_prop_collection] = None, use_front_faces_only: bool = False, mode: str = 'VALUE', value: float = 1.0) -> None:

  """

  Mask within a shape defined by the cursor

  """

  ...

def project_image(*args, image: str = '') -> None:

  """

  Project an edited render from the active camera back onto the object

  """

  ...

def sample_color(*args, location: typing.Tuple[int, int] = (0, 0), merged: bool = False, palette: bool = False) -> None:

  """

  Use the mouse to sample a color in the image

  """

  ...

def texture_paint_toggle() -> None:

  """

  Toggle texture paint mode in 3D view

  """

  ...

def vert_select_all(*args, action: str = 'TOGGLE') -> None:

  """

  Change selection for all vertices

  """

  ...

def vert_select_hide(*args, unselected: bool = False) -> None:

  """

  Hide selected vertices

  """

  ...

def vert_select_less(*args, face_step: bool = True) -> None:

  """

  Deselect Vertices connected to existing selection

  """

  ...

def vert_select_linked() -> None:

  """

  Select linked vertices

  """

  ...

def vert_select_linked_pick(*args, select: bool = True) -> None:

  """

  Select linked vertices under the cursor

  """

  ...

def vert_select_more(*args, face_step: bool = True) -> None:

  """

  Select Vertices connected to existing selection

  """

  ...

def vert_select_ungrouped(*args, extend: bool = False) -> None:

  """

  Select vertices without a group

  """

  ...

def vertex_color_brightness_contrast(*args, brightness: float = 0.0, contrast: float = 0.0) -> None:

  """

  Adjust vertex color brightness/contrast

  """

  ...

def vertex_color_dirt(*args, blur_strength: float = 1.0, blur_iterations: int = 1, clean_angle: float = 3.14159, dirt_angle: float = 0.0, dirt_only: bool = False, normalize: bool = True) -> None:

  """

  Generate a dirt map gradient based on cavity

  """

  ...

def vertex_color_from_weight() -> None:

  """

  Convert active weight into gray scale vertex colors

  """

  ...

def vertex_color_hsv(*args, h: float = 0.5, s: float = 1.0, v: float = 1.0) -> None:

  """

  Adjust vertex color Hue/Saturation/Value

  """

  ...

def vertex_color_invert() -> None:

  """

  Invert RGB values

  """

  ...

def vertex_color_levels(*args, offset: float = 0.0, gain: float = 1.0) -> None:

  """

  Adjust levels of vertex colors

  """

  ...

def vertex_color_set(*args, use_alpha: bool = True) -> None:

  """

  Fill the active vertex color layer with the current paint color

  """

  ...

def vertex_color_smooth() -> None:

  """

  Smooth colors across vertices

  """

  ...

def vertex_paint(*args, stroke: typing.Union[typing.Sequence[OperatorStrokeElement], typing.Mapping[str, OperatorStrokeElement], bpy.types.bpy_prop_collection] = None, mode: str = 'NORMAL', pen_flip: bool = False, override_location: bool = False) -> None:

  """

  Paint a stroke in the active color attribute layer

  """

  ...

def vertex_paint_toggle() -> None:

  """

  Toggle the vertex paint mode in 3D view

  """

  ...

def visibility_filter(*args, action: str = 'GROW', iterations: int = 1, auto_iteration_count: bool = True) -> None:

  """

  Edit the visibility of the current mesh

  """

  ...

def visibility_invert() -> None:

  """

  Invert the visibility of all vertices

  """

  ...

def weight_from_bones(*args, type: str = 'AUTOMATIC') -> None:

  """

  Set the weights of the groups matching the attached armature's selected bones, using the distance between the vertices and the bones

  """

  ...

def weight_gradient(*args, type: str = 'LINEAR', xstart: int = 0, xend: int = 0, ystart: int = 0, yend: int = 0, flip: bool = False, cursor: int = 5) -> None:

  """

  Draw a line to apply a weight gradient to selected vertices

  """

  ...

def weight_paint(*args, stroke: typing.Union[typing.Sequence[OperatorStrokeElement], typing.Mapping[str, OperatorStrokeElement], bpy.types.bpy_prop_collection] = None, mode: str = 'NORMAL', pen_flip: bool = False, override_location: bool = False) -> None:

  """

  Paint a stroke in the current vertex group's weights

  """

  ...

def weight_paint_toggle() -> None:

  """

  Toggle weight paint mode in 3D view

  """

  ...

def weight_sample() -> None:

  """

  Use the mouse to sample a weight in the 3D view

  """

  ...

def weight_sample_group() -> None:

  """

  Select one of the vertex groups available under current mouse position

  """

  ...

def weight_set() -> None:

  """

  Fill the active vertex group with the current paint weight

  """

  ...
