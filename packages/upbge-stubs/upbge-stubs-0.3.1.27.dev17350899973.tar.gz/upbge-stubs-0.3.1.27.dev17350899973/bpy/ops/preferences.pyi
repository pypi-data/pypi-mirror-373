"""


Preferences Operators
*********************

:func:`addon_disable`

:func:`addon_enable`

:func:`addon_expand`

:func:`addon_install`

:func:`addon_refresh`

:func:`addon_remove`

:func:`addon_show`

:func:`app_template_install`

:func:`asset_library_add`

:func:`asset_library_remove`

:func:`associate_blend`

:func:`autoexec_path_add`

:func:`autoexec_path_remove`

:func:`copy_prev`

:func:`extension_repo_add`

:func:`extension_repo_remove`

:func:`extension_url_drop`

:func:`keyconfig_activate`

:func:`keyconfig_export`

:func:`keyconfig_import`

:func:`keyconfig_remove`

:func:`keyconfig_test`

:func:`keyitem_add`

:func:`keyitem_remove`

:func:`keyitem_restore`

:func:`keymap_restore`

:func:`reset_default_theme`

:func:`script_directory_add`

:func:`script_directory_remove`

:func:`studiolight_copy_settings`

:func:`studiolight_install`

:func:`studiolight_new`

:func:`studiolight_uninstall`

:func:`theme_install`

:func:`unassociate_blend`

"""

import typing

def addon_disable(*args, module: str = '') -> None:

  """

  Turn off this add-on

  """

  ...

def addon_enable(*args, module: str = '') -> None:

  """

  Turn on this add-on

  """

  ...

def addon_expand(*args, module: str = '') -> None:

  """

  Display information and preferences for this add-on

  """

  ...

def addon_install(*args, overwrite: bool = True, enable_on_install: bool = False, target: str = '', filepath: str = '', filter_folder: bool = True, filter_python: bool = True, filter_glob: str = '*args.py;*args.zip') -> None:

  """

  Install an add-on

  """

  ...

def addon_refresh() -> None:

  """

  Scan add-on directories for new modules

  """

  ...

def addon_remove(*args, module: str = '') -> None:

  """

  Delete the add-on from the file system

  """

  ...

def addon_show(*args, module: str = '') -> None:

  """

  Show add-on preferences

  """

  ...

def app_template_install(*args, overwrite: bool = True, filepath: str = '', filter_folder: bool = True, filter_glob: str = '*args.zip') -> None:

  """

  Install an application template

  """

  ...

def asset_library_add(*args, directory: str = '', hide_props_region: bool = True, check_existing: bool = False, filter_blender: bool = False, filter_backup: bool = False, filter_image: bool = False, filter_movie: bool = False, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 9, display_type: str = 'DEFAULT', sort_method: str = '') -> None:

  """

  Add a directory to be used by the Asset Browser as source of assets

  """

  ...

def asset_library_remove(*args, index: int = 0) -> None:

  """

  Remove a path to a .blend file, so the Asset Browser will not attempt to show it anymore

  """

  ...

def associate_blend() -> None:

  """

  Use this installation for .blend files and to display thumbnails

  """

  ...

def autoexec_path_add() -> None:

  """

  Add path to exclude from auto-execution

  """

  ...

def autoexec_path_remove(*args, index: int = 0) -> None:

  """

  Remove path to exclude from auto-execution

  """

  ...

def copy_prev() -> None:

  """

  Copy settings from previous version

  """

  ...

def extension_repo_add(*args, name: str = '', remote_url: str = '', use_access_token: bool = False, access_token: str = '', use_sync_on_startup: bool = False, use_custom_directory: bool = False, custom_directory: str = '', type: str = 'REMOTE') -> None:

  """

  Add a new repository used to store extensions

  """

  ...

def extension_repo_remove(*args, index: int = 0, remove_files: bool = False) -> None:

  """

  Remove an extension repository

  """

  ...

def extension_url_drop(*args, url: str = '') -> None:

  """

  Handle dropping an extension URL

  """

  ...

def keyconfig_activate(*args, filepath: str = '') -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def keyconfig_export(*args, all: bool = False, filepath: str = '', filter_folder: bool = True, filter_text: bool = True, filter_python: bool = True) -> None:

  """

  Export key configuration to a Python script

  """

  ...

def keyconfig_import(*args, filepath: str = 'keymap.py', filter_folder: bool = True, filter_text: bool = True, filter_python: bool = True, keep_original: bool = True) -> None:

  """

  Import key configuration from a Python script

  """

  ...

def keyconfig_remove() -> None:

  """

  Remove key config

  """

  ...

def keyconfig_test() -> None:

  """

  Test key configuration for conflicts

  """

  ...

def keyitem_add() -> None:

  """

  Add key map item

  """

  ...

def keyitem_remove(*args, item_id: int = 0) -> None:

  """

  Remove key map item

  """

  ...

def keyitem_restore(*args, item_id: int = 0) -> None:

  """

  Restore key map item

  """

  ...

def keymap_restore(*args, all: bool = False) -> None:

  """

  Restore key map(s)

  """

  ...

def reset_default_theme() -> None:

  """

  Reset to the default theme colors

  """

  ...

def script_directory_add(*args, directory: str = '', filter_folder: bool = True) -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def script_directory_remove(*args, index: int = 0) -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def studiolight_copy_settings(*args, index: int = 0) -> None:

  """

  Copy Studio Light settings to the Studio Light editor

  """

  ...

def studiolight_install(*args, files: typing.Union[typing.Sequence[OperatorFileListElement], typing.Mapping[str, OperatorFileListElement], bpy.types.bpy_prop_collection] = None, directory: str = '', filter_folder: bool = True, filter_glob: str = '*args.png;*args.jpg;*args.hdr;*args.exr', type: str = 'MATCAP') -> None:

  """

  Install a user defined light

  """

  ...

def studiolight_new(*args, filename: str = 'StudioLight') -> None:

  """

  Save custom studio light from the studio light editor settings

  """

  ...

def studiolight_uninstall(*args, index: int = 0) -> None:

  """

  Delete Studio Light

  """

  ...

def theme_install(*args, overwrite: bool = True, filepath: str = '', filter_folder: bool = True, filter_glob: str = '*args.xml') -> None:

  """

  Load and apply a Blender XML theme file

  """

  ...

def unassociate_blend() -> None:

  """

  Remove this installation's associations with .blend files

  """

  ...
