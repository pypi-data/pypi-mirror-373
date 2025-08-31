"""


bpy_extras submodule (bpy_extras.id_map_utils)
**********************************************

:func:`get_id_reference_map`

:func:`get_all_referenced_ids`

"""

import typing

def get_id_reference_map() -> None:

  """

  Return a dictionary of direct data-block references for every data-block in the blend file.

  """

  ...

def get_all_referenced_ids(id: typing.Any, ref_map: typing.Any) -> None:

  """

  Return a set of IDs directly or indirectly referenced by id.

  """

  ...
