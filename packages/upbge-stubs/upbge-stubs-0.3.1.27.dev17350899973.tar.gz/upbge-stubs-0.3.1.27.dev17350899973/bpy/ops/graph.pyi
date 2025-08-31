"""


Graph Operators
***************

:func:`bake_keys`

:func:`blend_offset`

:func:`blend_to_default`

:func:`blend_to_ease`

:func:`blend_to_neighbor`

:func:`breakdown`

:func:`butterworth_smooth`

:func:`clean`

:func:`click_insert`

:func:`clickselect`

:func:`copy`

:func:`cursor_set`

:func:`decimate`

:func:`delete`

:func:`driver_delete_invalid`

:func:`driver_variables_copy`

:func:`driver_variables_paste`

:func:`duplicate`

:func:`duplicate_move`

:func:`ease`

:func:`easing_type`

:func:`equalize_handles`

:func:`euler_filter`

:func:`extrapolation_type`

:func:`fmodifier_add`

:func:`fmodifier_copy`

:func:`fmodifier_paste`

:func:`frame_jump`

:func:`gaussian_smooth`

:func:`ghost_curves_clear`

:func:`ghost_curves_create`

:func:`handle_type`

:func:`hide`

:func:`interpolation_type`

:func:`keyframe_insert`

:func:`keyframe_jump`

:func:`keys_to_samples`

:func:`match_slope`

:func:`mirror`

:func:`paste`

:func:`previewrange_set`

:func:`push_pull`

:func:`reveal`

:func:`samples_to_keys`

:func:`scale_average`

:func:`scale_from_neighbor`

:func:`select_all`

:func:`select_box`

:func:`select_circle`

:func:`select_column`

:func:`select_key_handles`

:func:`select_lasso`

:func:`select_leftright`

:func:`select_less`

:func:`select_linked`

:func:`select_more`

:func:`shear`

:func:`smooth`

:func:`snap`

:func:`snap_cursor_value`

:func:`sound_to_samples`

:func:`time_offset`

:func:`view_all`

:func:`view_frame`

:func:`view_selected`

"""

import typing

def bake_keys() -> None:

  """

  Add keyframes on every frame between the selected keyframes

  """

  ...

def blend_offset(*args, factor: float = 0.0) -> None:

  """

  Shift selected keys to the value of the neighboring keys as a block

  """

  ...

def blend_to_default(*args, factor: float = 0.0) -> None:

  """

  Blend selected keys to their default value from their current position

  """

  ...

def blend_to_ease(*args, factor: float = 0.0) -> None:

  """

  Blends keyframes from current state to an ease-in or ease-out curve

  """

  ...

def blend_to_neighbor(*args, factor: float = 0.0) -> None:

  """

  Blend selected keyframes to their left or right neighbor

  """

  ...

def breakdown(*args, factor: float = 0.0) -> None:

  """

  Move selected keyframes to an inbetween position relative to adjacent keys

  """

  ...

def butterworth_smooth(*args, cutoff_frequency: float = 3.0, filter_order: int = 4, samples_per_frame: int = 1, blend: float = 1.0, blend_in_out: int = 1) -> None:

  """

  Smooth an F-Curve while maintaining the general shape of the curve

  """

  ...

def clean(*args, threshold: float = 0.001, channels: bool = False) -> None:

  """

  Simplify F-Curves by removing closely spaced keyframes

  """

  ...

def click_insert(*args, frame: float = 1.0, value: float = 1.0, extend: bool = False) -> None:

  """

  Insert new keyframe at the cursor position for the active F-Curve

  """

  ...

def clickselect(*args, wait_to_deselect_others: bool = False, mouse_x: int = 0, mouse_y: int = 0, extend: bool = False, deselect_all: bool = False, column: bool = False, curves: bool = False) -> None:

  """

  Select keyframes by clicking on them

  """

  ...

def copy() -> None:

  """

  Copy selected keyframes to the internal clipboard

  """

  ...

def cursor_set(*args, frame: float = 0.0, value: float = 0.0) -> None:

  """

  Interactively set the current frame and value cursor

  """

  ...

def decimate(*args, mode: str = 'RATIO', factor: float = 0.333333, remove_error_margin: float = 0.0) -> None:

  """

  Decimate F-Curves by removing keyframes that influence the curve shape the least

  """

  ...

def delete(*args, confirm: bool = True) -> None:

  """

  Remove all selected keyframes

  """

  ...

def driver_delete_invalid() -> None:

  """

  Delete all visible drivers considered invalid

  """

  ...

def driver_variables_copy() -> None:

  """

  Copy the driver variables of the active driver

  """

  ...

def driver_variables_paste(*args, replace: bool = False) -> None:

  """

  Add copied driver variables to the active driver

  """

  ...

def duplicate(*args, mode: str = 'TRANSLATION') -> None:

  """

  Make a copy of all selected keyframes

  """

  ...

def duplicate_move(*args, GRAPH_OT_duplicate: GRAPH_OT_duplicate = None, TRANSFORM_OT_translate: TRANSFORM_OT_translate = None) -> None:

  """

  Make a copy of all selected keyframes and move them

  """

  ...

def ease(*args, factor: float = 0.0, sharpness: float = 2.0) -> None:

  """

  Align keyframes on a ease-in or ease-out curve

  """

  ...

def easing_type(*args, type: str = 'AUTO') -> None:

  """

  Set easing type for the F-Curve segments starting from the selected keyframes

  """

  ...

def equalize_handles(*args, side: str = 'LEFT', handle_length: float = 5.0, flatten: bool = False) -> None:

  """

  Ensure selected keyframes' handles have equal length, optionally making them horizontal. Automatic, Automatic Clamped, or Vector handle types will be converted to Aligned

  """

  ...

def euler_filter() -> None:

  """

  Fix large jumps and flips in the selected Euler Rotation F-Curves arising from rotation values being clipped when baking physics

  """

  ...

def extrapolation_type(*args, type: str = 'CONSTANT') -> None:

  """

  Set extrapolation mode for selected F-Curves

  """

  ...

def fmodifier_add(*args, type: str = 'NULL', only_active: bool = False) -> None:

  """

  Add F-Modifier to the active/selected F-Curves

  """

  ...

def fmodifier_copy() -> None:

  """

  Copy the F-Modifier(s) of the active F-Curve

  """

  ...

def fmodifier_paste(*args, only_active: bool = False, replace: bool = False) -> None:

  """

  Add copied F-Modifiers to the selected F-Curves

  """

  ...

def frame_jump() -> None:

  """

  Place the cursor on the midpoint of selected keyframes

  """

  ...

def gaussian_smooth(*args, factor: float = 1.0, sigma: float = 0.33, filter_width: int = 6) -> None:

  """

  Smooth the curve using a Gaussian filter

  """

  ...

def ghost_curves_clear() -> None:

  """

  Clear F-Curve snapshots (Ghosts) for active Graph Editor

  """

  ...

def ghost_curves_create() -> None:

  """

  Create snapshot (Ghosts) of selected F-Curves as background aid for active Graph Editor

  """

  ...

def handle_type(*args, type: str = 'FREE') -> None:

  """

  Set type of handle for selected keyframes

  """

  ...

def hide(*args, unselected: bool = False) -> None:

  """

  Hide selected curves from Graph Editor view

  """

  ...

def interpolation_type(*args, type: str = 'CONSTANT') -> None:

  """

  Set interpolation mode for the F-Curve segments starting from the selected keyframes

  """

  ...

def keyframe_insert(*args, type: str = 'ALL') -> None:

  """

  Insert keyframes for the specified channels

  """

  ...

def keyframe_jump(*args, next: bool = True) -> None:

  """

  Jump to previous/next keyframe

  """

  ...

def keys_to_samples() -> None:

  """

  Convert selected channels to an uneditable set of samples to save storage space

  """

  ...

def match_slope(*args, factor: float = 0.0) -> None:

  """

  Blend selected keys to the slope of neighboring ones

  """

  ...

def mirror(*args, type: str = 'CFRA') -> None:

  """

  Flip selected keyframes over the selected mirror line

  """

  ...

def paste(*args, offset: str = 'START', value_offset: str = 'NONE', merge: str = 'MIX', flipped: bool = False) -> None:

  """

  Paste keyframes from the internal clipboard for the selected channels, starting on the current frame

  """

  ...

def previewrange_set() -> None:

  """

  Set Preview Range based on range of selected keyframes

  """

  ...

def push_pull(*args, factor: float = 1.0) -> None:

  """

  Exaggerate or minimize the value of the selected keys

  """

  ...

def reveal(*args, select: bool = True) -> None:

  """

  Make previously hidden curves visible again in Graph Editor view

  """

  ...

def samples_to_keys() -> None:

  """

  Convert selected channels from samples to keyframes

  """

  ...

def scale_average(*args, factor: float = 1.0) -> None:

  """

  Scale selected key values by their combined average

  """

  ...

def scale_from_neighbor(*args, factor: float = 0.0, anchor: str = 'LEFT') -> None:

  """

  Increase or decrease the value of selected keys in relationship to the neighboring one

  """

  ...

def select_all(*args, action: str = 'TOGGLE') -> None:

  """

  Toggle selection of all keyframes

  """

  ...

def select_box(*args, axis_range: bool = False, include_handles: bool = True, tweak: bool = False, use_curve_selection: bool = True, xmin: int = 0, xmax: int = 0, ymin: int = 0, ymax: int = 0, wait_for_input: bool = True, mode: str = 'SET') -> None:

  """

  Select all keyframes within the specified region

  """

  ...

def select_circle(*args, x: int = 0, y: int = 0, radius: int = 25, wait_for_input: bool = True, mode: str = 'SET', include_handles: bool = True, use_curve_selection: bool = True) -> None:

  """

  Select keyframe points using circle selection

  """

  ...

def select_column(*args, mode: str = 'KEYS') -> None:

  """

  Select all keyframes on the specified frame(s)

  """

  ...

def select_key_handles(*args, left_handle_action: str = 'SELECT', right_handle_action: str = 'SELECT', key_action: str = 'KEEP') -> None:

  """

  For selected keyframes, select/deselect any combination of the key itself and its handles

  """

  ...

def select_lasso(*args, path: typing.Union[typing.Sequence[OperatorMousePath], typing.Mapping[str, OperatorMousePath], bpy.types.bpy_prop_collection] = None, use_smooth_stroke: bool = False, smooth_stroke_factor: float = 0.75, smooth_stroke_radius: int = 35, mode: str = 'SET', include_handles: bool = True, use_curve_selection: bool = True) -> None:

  """

  Select keyframe points using lasso selection

  """

  ...

def select_leftright(*args, mode: str = 'CHECK', extend: bool = False) -> None:

  """

  Select keyframes to the left or the right of the current frame

  """

  ...

def select_less() -> None:

  """

  Deselect keyframes on ends of selection islands

  """

  ...

def select_linked() -> None:

  """

  Select keyframes occurring in the same F-Curves as selected ones

  """

  ...

def select_more() -> None:

  """

  Select keyframes beside already selected ones

  """

  ...

def shear(*args, factor: float = 0.0, direction: str = 'FROM_LEFT') -> None:

  """

  Affect the value of the keys linearly, keeping the same relationship between them using either the left or the right key as reference

  """

  ...

def smooth() -> None:

  """

  Apply weighted moving means to make selected F-Curves less bumpy

  """

  ...

def snap(*args, type: str = 'CFRA') -> None:

  """

  Snap selected keyframes to the chosen times/values

  """

  ...

def snap_cursor_value() -> None:

  """

  Place the cursor value on the average value of selected keyframes

  """

  ...

def sound_to_samples(*args, filepath: str = '', check_existing: bool = False, filter_blender: bool = False, filter_backup: bool = False, filter_image: bool = False, filter_movie: bool = True, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = True, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 9, show_multiview: bool = False, use_multiview: bool = False, display_type: str = 'DEFAULT', sort_method: str = '', low: float = 0.0, high: float = 100000.0, attack: float = 0.005, release: float = 0.2, threshold: float = 0.0, use_accumulate: bool = False, use_additive: bool = False, use_square: bool = False, sthreshold: float = 0.1) -> None:

  """

  Bakes a sound wave to samples on selected channels

  """

  ...

def time_offset(*args, frame_offset: float = 0.0) -> None:

  """

  Shifts the value of selected keys in time

  """

  ...

def view_all(*args, include_handles: bool = True) -> None:

  """

  Reset viewable area to show full keyframe range

  """

  ...

def view_frame() -> None:

  """

  Move the view to the current frame

  """

  ...

def view_selected(*args, include_handles: bool = True) -> None:

  """

  Reset viewable area to show selected keyframe range

  """

  ...
