"""


Brush Operators
***************

:func:`asset_activate`

:func:`asset_delete`

:func:`asset_edit_metadata`

:func:`asset_load_preview`

:func:`asset_revert`

:func:`asset_save`

:func:`asset_save_as`

:func:`curve_preset`

:func:`scale_size`

:func:`sculpt_curves_falloff_preset`

:func:`stencil_control`

:func:`stencil_fit_image_aspect`

:func:`stencil_reset_transform`

"""

import typing

def asset_activate(*args, asset_library_type: str = 'LOCAL', asset_library_identifier: str = '', relative_asset_identifier: str = '', use_toggle: bool = False) -> None:

  """

  Activate a brush asset as current sculpt and paint tool

  """

  ...

def asset_delete() -> None:

  """

  Delete the active brush asset

  """

  ...

def asset_edit_metadata(*args, catalog_path: str = '', author: str = '', description: str = '') -> None:

  """

  Edit asset information like the catalog, preview image, tags, or author

  """

  ...

def asset_load_preview(*args, filepath: str = '', hide_props_region: bool = True, check_existing: bool = False, filter_blender: bool = False, filter_backup: bool = False, filter_image: bool = True, filter_movie: bool = False, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 9, show_multiview: bool = False, use_multiview: bool = False, display_type: str = 'DEFAULT', sort_method: str = '') -> None:

  """

  Choose a preview image for the brush

  """

  ...

def asset_revert() -> None:

  """

  Revert the active brush settings to the default values from the asset library

  """

  ...

def asset_save() -> None:

  """

  Update the active brush asset in the asset library with current settings

  """

  ...

def asset_save_as(*args, name: str = '', asset_library_reference: str = '', catalog_path: str = '') -> None:

  """

  Save a copy of the active brush asset into the default asset library, and make it the active brush

  """

  ...

def curve_preset(*args, shape: str = 'SMOOTH') -> None:

  """

  Set brush shape

  """

  ...

def scale_size(*args, scalar: float = 1.0) -> None:

  """

  Change brush size by a scalar

  """

  ...

def sculpt_curves_falloff_preset(*args, shape: str = 'SMOOTH') -> None:

  """

  Set Curve Falloff Preset

  """

  ...

def stencil_control(*args, mode: str = 'TRANSLATION', texmode: str = 'PRIMARY') -> None:

  """

  Control the stencil brush

  """

  ...

def stencil_fit_image_aspect(*args, use_repeat: bool = True, use_scale: bool = True, mask: bool = False) -> None:

  """

  When using an image texture, adjust the stencil size to fit the image aspect ratio

  """

  ...

def stencil_reset_transform(*args, mask: bool = False) -> None:

  """

  Reset the stencil transformation to the default

  """

  ...
