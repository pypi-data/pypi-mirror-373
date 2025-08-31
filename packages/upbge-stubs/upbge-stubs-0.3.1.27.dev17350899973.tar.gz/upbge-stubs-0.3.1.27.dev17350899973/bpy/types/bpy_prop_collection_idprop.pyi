"""


bpy_prop_collection_idprop
^^^^^^^^^^^^^^^^^^^^^^^^^^

base classes --- :class:`bpy_prop_collection`

class bpy_prop_collection_idprop:

  """

  built-in class used for user defined collections.

  Note: Note that :class:`bpy.types.bpy_prop_collection_idprop` is not actually available from within Blender,
it only exists for the purpose of documentation.

  """

  def add(self) -> typing.Any:

    """

    This is a function to add a new item to a collection.

    """

    ...

  def clear(self) -> None:

    """

    This is a function to remove all items from a collection.

    """

    ...

  def move(self, src_index: int, dst_index: int) -> None:

    """

    This is a function to move an item in a collection.

    """

    ...

  def remove(self, index: int) -> None:

    """

    This is a function to remove an item from a collection.

    """

    ...

"""

import typing
