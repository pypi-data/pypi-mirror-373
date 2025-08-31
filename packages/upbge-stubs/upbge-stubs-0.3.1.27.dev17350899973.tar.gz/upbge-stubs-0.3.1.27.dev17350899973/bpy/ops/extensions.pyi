"""


Extensions Operators
********************

:func:`package_disable`

:func:`package_install`

:func:`package_install_files`

:func:`package_install_marked`

:func:`package_mark_clear`

:func:`package_mark_clear_all`

:func:`package_mark_set`

:func:`package_mark_set_all`

:func:`package_obsolete_marked`

:func:`package_show_clear`

:func:`package_show_set`

:func:`package_show_settings`

:func:`package_theme_disable`

:func:`package_theme_enable`

:func:`package_uninstall`

:func:`package_uninstall_marked`

:func:`package_uninstall_system`

:func:`package_upgrade_all`

:func:`repo_enable_from_drop`

:func:`repo_lock_all`

:func:`repo_refresh_all`

:func:`repo_sync`

:func:`repo_sync_all`

:func:`repo_unlock`

:func:`repo_unlock_all`

:func:`status_clear`

:func:`status_clear_errors`

:func:`userpref_allow_online`

:func:`userpref_allow_online_popup`

:func:`userpref_show_for_update`

:func:`userpref_show_online`

:func:`userpref_tags_set`

"""

import typing

def package_disable() -> None:

  """

  Turn off this extension

  """

  ...

def package_install(*args, repo_directory: str = '', repo_index: int = -1, pkg_id: str = '', enable_on_install: bool = True, url: str = '', do_legacy_replace: bool = False) -> None:

  """

  Download and install the extension

  """

  ...

def package_install_files(*args, filter_glob: str = '*args.zip;*args.py', directory: str = '', files: typing.Union[typing.Sequence[OperatorFileListElement], typing.Mapping[str, OperatorFileListElement], bpy.types.bpy_prop_collection] = None, filepath: str = '', repo: str = '', enable_on_install: bool = True, target: str = '', overwrite: bool = True, url: str = '') -> None:

  """

  Install extensions from files into a locally managed repository

  """

  ...

def package_install_marked(*args, enable_on_install: bool = True) -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def package_mark_clear(*args, pkg_id: str = '', repo_index: int = -1) -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def package_mark_clear_all() -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def package_mark_set(*args, pkg_id: str = '', repo_index: int = -1) -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def package_mark_set_all() -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def package_obsolete_marked() -> None:

  """

  Zeroes package versions, useful for development - to test upgrading

  """

  ...

def package_show_clear(*args, pkg_id: str = '', repo_index: int = -1) -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def package_show_set(*args, pkg_id: str = '', repo_index: int = -1) -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def package_show_settings(*args, pkg_id: str = '', repo_index: int = -1) -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def package_theme_disable(*args, pkg_id: str = '', repo_index: int = -1) -> None:

  """

  Turn off this theme

  """

  ...

def package_theme_enable(*args, pkg_id: str = '', repo_index: int = -1) -> None:

  """

  Turn off this theme

  """

  ...

def package_uninstall(*args, repo_directory: str = '', repo_index: int = -1, pkg_id: str = '') -> None:

  """

  Disable and uninstall the extension

  """

  ...

def package_uninstall_marked() -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def package_uninstall_system() -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def package_upgrade_all(*args, use_active_only: bool = False) -> None:

  """

  Upgrade all the extensions to their latest version for all the remote repositories

  """

  ...

def repo_enable_from_drop(*args, repo_index: int = -1) -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def repo_lock_all() -> None:

  """

  Lock repositories - to test locking

  """

  ...

def repo_refresh_all(*args, use_active_only: bool = False) -> None:

  """

  Scan extension & legacy add-ons for changes to modules & meta-data (similar to restarting). Any issues are reported as warnings

  """

  ...

def repo_sync(*args, repo_directory: str = '', repo_index: int = -1) -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def repo_sync_all(*args, use_active_only: bool = False) -> None:

  """

  Refresh the list of extensions for all the remote repositories

  """

  ...

def repo_unlock() -> None:

  """

  Remove the repository file-system lock

  """

  ...

def repo_unlock_all() -> None:

  """

  Unlock repositories - to test unlocking

  """

  ...

def status_clear() -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def status_clear_errors() -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def userpref_allow_online() -> None:

  """

  Allow internet access. Blender may access configured online extension repositories. Installed third party add-ons may access the internet for their own functionality

  """

  ...

def userpref_allow_online_popup() -> None:

  """

  Allow internet access. Blender may access configured online extension repositories. Installed third party add-ons may access the internet for their own functionality

  """

  ...

def userpref_show_for_update() -> None:

  """

  Open extensions preferences

  """

  ...

def userpref_show_online() -> None:

  """

  Show system preferences "Network" panel to allow online access

  """

  ...

def userpref_tags_set(*args, value: bool = False, data_path: str = '') -> None:

  """

  Set the value of all tags

  """

  ...
