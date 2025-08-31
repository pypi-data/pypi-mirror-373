"""


Bge Bricknodes Operators
************************

:func:`convert_bricks`

:func:`duplicate_brick`

:func:`remove_actuator`

:func:`remove_controller`

:func:`remove_sensor`

:func:`update_all`

"""

import typing

def convert_bricks() -> None:

  """

  Convert Bricks to Nodes

  """

  ...

def duplicate_brick() -> None:

  """

  Duplicate this brick

  """

  ...

def remove_actuator(*args, target_brick: str = '') -> None:

  """

  Remove the selected actuator from the selected object

  """

  ...

def remove_controller(*args, target_brick: str = '') -> None:

  """

  Remove the selected controller from the selected object

  """

  ...

def remove_sensor(*args, target_brick: str = '') -> None:

  """

  Remove the selected sensor from the selected object

  """

  ...

def update_all() -> None:

  """

  Synchronize logic bricks with the node setup. This should normally happen automatically

  """

  ...
