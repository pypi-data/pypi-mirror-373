"""


ID Property Access (idprop.types)
*********************************

:class:`idprop.types.IDPropertyArray`

:class:`idprop.types.IDPropertyGroup`

:class:`idprop.types.IDPropertyGroupIterItems`

:class:`idprop.types.IDPropertyGroupIterKeys`

:class:`idprop.types.IDPropertyGroupIterValues`

:class:`idprop.types.IDPropertyGroupViewItems`

:class:`idprop.types.IDPropertyGroupViewKeys`

:class:`idprop.types.IDPropertyGroupViewValues`

"""

import typing

class idprop.types.IDPropertyArray:

  def to_list(self) -> None:

    """

    Return the array as a list.

    """

    ...

  typecode: typing.Any = ...

  """

  The type of the data in the array {'f': float, 'd': double, 'i': int, 'b': bool}.

  """

class idprop.types.IDPropertyGroup:

  def clear(self) -> None:

    """

    Clear all members from this group.

    """

    ...

  def get(self, key: typing.Any, default: typing.Any = None) -> None:

    """

    Return the value for key, if it exists, else default.

    """

    ...

  def items(self) -> None:

    """

    Iterate through the items in the dict; behaves like dictionary method items.

    """

    ...

  def keys(self) -> None:

    """

    Return the keys associated with this group as a list of strings.

    """

    ...

  def pop(self, key: str, default: typing.Any) -> None:

    """

    Remove an item from the group, returning a Python representation.

    """

    ...

  def to_dict(self) -> None:

    """

    Return a purely Python version of the group.

    """

    ...

  def update(self, other: IDPropertyGroup) -> None:

    """

    Update key, values.

    """

    ...

  def values(self) -> None:

    """

    Return the values associated with this group.

    """

    ...

  name: typing.Any = ...

  """

  The name of this Group.

  """

class idprop.types.IDPropertyGroupIterItems:

  ...

class idprop.types.IDPropertyGroupIterKeys:

  ...

class idprop.types.IDPropertyGroupIterValues:

  ...

class idprop.types.IDPropertyGroupViewItems:

  ...

class idprop.types.IDPropertyGroupViewKeys:

  ...

class idprop.types.IDPropertyGroupViewValues:

  ...
