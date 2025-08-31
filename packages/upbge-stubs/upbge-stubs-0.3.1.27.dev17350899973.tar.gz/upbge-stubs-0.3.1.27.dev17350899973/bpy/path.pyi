"""


Path Utilities (bpy.path)
*************************

This module has a similar scope to os.path, containing utility
functions for dealing with paths in Blender.

:func:`abspath`

:func:`basename`

:func:`clean_name`

:func:`display_name`

:func:`display_name_to_filepath`

:func:`display_name_from_filepath`

:func:`ensure_ext`

:func:`is_subdir`

:func:`module_names`

:func:`native_pathsep`

:func:`reduce_dirs`

:func:`relpath`

:func:`resolve_ncase`

"""

import typing

import bpy

def abspath(path: typing.Any, *args, start: str = None, library: bpy.types.Library = None) -> str:

  """

  Returns the absolute path relative to the current blend file
using the "//" prefix.

  """

  ...

def basename(path: typing.Any) -> str:

  """

  Equivalent to ``os.path.basename``, but skips a "//" prefix.

  Use for Windows compatibility.

  """

  ...

def clean_name(name: str, *args, replace: str = '_') -> str:

  """

  Returns a name with characters replaced that
may cause problems under various circumstances,
such as writing to a file.

  All characters besides A-Z/a-z, 0-9 are replaced with "_"
or the *replace* argument if defined.

  """

  ...

def display_name(name: str, *args, has_ext: bool = True, title_case: bool = True) -> str:

  """

  Creates a display string from name to be used menus and the user interface.
Intended for use with filenames and module names.

  """

  ...

def display_name_to_filepath(name: str) -> str:

  """

  Performs the reverse of display_name using literal versions of characters
which aren't supported in a filepath.

  """

  ...

def display_name_from_filepath(name: str) -> str:

  """

  Returns the path stripped of directory and extension,
ensured to be utf8 compatible.

  """

  ...

def ensure_ext(filepath: str, ext: str, *args, case_sensitive: bool = False) -> str:

  """

  Return the path with the extension added if it is not already set.

  """

  ...

def is_subdir(path: str, directory: typing.Any) -> bool:

  """

  Returns true if *path* in a subdirectory of *directory*.
Both paths must be absolute.

  """

  ...

def module_names(path: str, *args, recursive: bool = False, package: str = '') -> typing.Any:

  """

  Return a list of modules which can be imported from *path*.

  """

  ...

def native_pathsep(path: str) -> str:

  """

  Replace the path separator with the systems native ``os.sep``.

  """

  ...

def reduce_dirs(dirs: typing.Any) -> typing.List[str]:

  """

  Given a sequence of directories, remove duplicates and
any directories nested in one of the other paths.
(Useful for recursive path searching).

  """

  ...

def relpath(path: str, *args, start: str = None) -> str:

  """

  Returns the path relative to the current blend file using the "//" prefix.

  """

  ...

def resolve_ncase(path: str) -> str:

  """

  Resolve a case insensitive path on a case sensitive system,
returning a string with the path if found else return the original path.

  """

  ...
