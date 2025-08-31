"""


bpy_extras submodule (bpy_extras.io_utils)
******************************************

:func:`orientation_helper`

:func:`axis_conversion`

:func:`axis_conversion_ensure`

:func:`create_derived_objects`

:func:`poll_file_object_drop`

:func:`unpack_list`

:func:`unpack_face_list`

:func:`path_reference`

:func:`unique_name`

:class:`bpy_extras.io_utils.ExportHelper`

:class:`bpy_extras.io_utils.ImportHelper`

"""

import typing

import bpy

def orientation_helper(axis_forward: typing.Any = 'Y', axis_up: typing.Any = 'Z') -> None:

  """

  A decorator for import/export classes, generating properties needed by the axis conversion system and IO helpers,
with specified default values (axes).

  """

  ...

def axis_conversion(from_forward: typing.Any = 'Y', from_up: typing.Any = 'Z', to_forward: typing.Any = 'Y', to_up: typing.Any = 'Z') -> None:

  """

  Each argument us an axis in ['X', 'Y', 'Z', '-X', '-Y', '-Z']
where the first 2 are a source and the second 2 are the target.

  """

  ...

def axis_conversion_ensure(operator: bpy.types.Operator, forward_attr: str, up_attr: str) -> bool:

  """

  Function to ensure an operator has valid axis conversion settings, intended
to be used from :class:`bpy.types.Operator.check`.

  """

  ...

def create_derived_objects(depsgraph: bpy.types.Depsgraph, objects: typing.Any) -> typing.Dict[bpy.types.Object, typing.Any]:

  """

  This function takes a sequence of objects, returning their instances.

  """

  ...

def poll_file_object_drop(context: typing.Any) -> None:

  """

  A default implementation for FileHandler poll_drop methods. Allows for both the 3D Viewport and
the Outliner (in ViewLayer display mode) to be targets for file drag and drop.

  """

  ...

def unpack_list(list_of_tuples: typing.Any) -> None:

  ...

def unpack_face_list(list_of_tuples: typing.Any) -> None:

  ...

def path_reference(filepath: str, base_src: str, base_dst: str, mode: str = 'AUTO', copy_subdir: str = '', copy_set: typing.Any = None, library: bpy.types.Library = None) -> str:

  """

  Return a filepath relative to a destination directory, for use with
exporters.

  """

  ...

def unique_name(key: typing.Any, name: str, name_dict: typing.Dict[str, typing.Any], name_max: typing.Any = -1, clean_func: typing.Callable = None, sep: str = '.') -> None:

  """

  Helper function for storing unique names which may have special characters
stripped and restricted to a maximum length.

  """

  ...

class bpy_extras.io_utils.ExportHelper:

  def check(self, _context: typing.Any) -> None:

    ...

  def invoke(self, context: typing.Any, _event: typing.Any) -> None:

    ...

class bpy_extras.io_utils.ImportHelper:

  def check(self, _context: typing.Any) -> None:

    ...

  def invoke(self, context: typing.Any, _event: typing.Any) -> None:

    ...

  def invoke_popup(self, context: typing.Any, confirm_text: typing.Any = '') -> None:

    ...
