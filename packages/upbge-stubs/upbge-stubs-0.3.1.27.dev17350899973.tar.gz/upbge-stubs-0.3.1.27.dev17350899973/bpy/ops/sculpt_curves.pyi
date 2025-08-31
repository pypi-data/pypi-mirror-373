"""


Sculpt Curves Operators
***********************

:func:`brush_stroke`

:func:`min_distance_edit`

:func:`select_grow`

:func:`select_random`

"""

import typing

def brush_stroke(*args, stroke: typing.Union[typing.Sequence[OperatorStrokeElement], typing.Mapping[str, OperatorStrokeElement], bpy.types.bpy_prop_collection] = None, mode: str = 'NORMAL', pen_flip: bool = False) -> None:

  """

  Sculpt curves using a brush

  """

  ...

def min_distance_edit() -> None:

  """

  Change the minimum distance used by the density brush

  """

  ...

def select_grow(*args, distance: float = 0.1) -> None:

  """

  Select curves which are close to curves that are selected already

  """

  ...

def select_random(*args, seed: int = 0, partial: bool = False, probability: float = 0.5, min: float = 0.0, constant_per_curve: bool = True) -> None:

  """

  Randomizes existing selection or create new random selection

  """

  ...
