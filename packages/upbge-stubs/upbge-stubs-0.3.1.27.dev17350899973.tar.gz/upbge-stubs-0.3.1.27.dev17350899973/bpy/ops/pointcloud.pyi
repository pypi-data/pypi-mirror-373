"""


Pointcloud Operators
********************

:func:`attribute_set`

:func:`delete`

:func:`duplicate`

:func:`duplicate_move`

:func:`select_all`

:func:`select_random`

:func:`separate`

"""

import typing

def attribute_set(*args, value_float: float = 0.0, value_float_vector_2d: typing.Tuple[float, float] = (0.0, 0.0), value_float_vector_3d: typing.Tuple[float, float, float] = (0.0, 0.0, 0.0), value_int: int = 0, value_int_vector_2d: typing.Tuple[int, int] = (0, 0), value_color: typing.Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0), value_bool: bool = False) -> None:

  """

  Set values of the active attribute for selected elements

  """

  ...

def delete() -> None:

  """

  Remove selected points

  """

  ...

def duplicate() -> None:

  """

  Copy selected points

  """

  ...

def duplicate_move(*args, POINTCLOUD_OT_duplicate: POINTCLOUD_OT_duplicate = None, TRANSFORM_OT_translate: TRANSFORM_OT_translate = None) -> None:

  """

  Make copies of selected elements and move them

  """

  ...

def select_all(*args, action: str = 'TOGGLE') -> None:

  """

  (De)select all point cloud

  """

  ...

def select_random(*args, seed: int = 0, probability: float = 0.5) -> None:

  """

  Randomizes existing selection or create new random selection

  """

  ...

def separate() -> None:

  """

  Separate selected geometry into a new point cloud

  """

  ...
