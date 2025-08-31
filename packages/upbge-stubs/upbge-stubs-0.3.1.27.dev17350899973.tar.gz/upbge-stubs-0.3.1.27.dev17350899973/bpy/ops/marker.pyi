"""


Marker Operators
****************

:func:`add`

:func:`camera_bind`

:func:`delete`

:func:`duplicate`

:func:`make_links_scene`

:func:`move`

:func:`rename`

:func:`select`

:func:`select_all`

:func:`select_box`

:func:`select_leftright`

"""

import typing

def add() -> None:

  """

  Add a new time marker

  """

  ...

def camera_bind() -> None:

  """

  Bind the selected camera to a marker on the current frame

  """

  ...

def delete(*args, confirm: bool = True) -> None:

  """

  Delete selected time marker(s)

  """

  ...

def duplicate(*args, frames: int = 0) -> None:

  """

  Duplicate selected time marker(s)

  """

  ...

def make_links_scene(*args, scene: str = '') -> None:

  """

  Copy selected markers to another scene

  """

  ...

def move(*args, frames: int = 0, tweak: bool = False) -> None:

  """

  Move selected time marker(s)

  """

  ...

def rename(*args, name: str = 'RenamedMarker') -> None:

  """

  Rename first selected time marker

  """

  ...

def select(*args, wait_to_deselect_others: bool = False, mouse_x: int = 0, mouse_y: int = 0, extend: bool = False, camera: bool = False) -> None:

  """

  Select time marker(s)

  """

  ...

def select_all(*args, action: str = 'TOGGLE') -> None:

  """

  Change selection of all time markers

  """

  ...

def select_box(*args, xmin: int = 0, xmax: int = 0, ymin: int = 0, ymax: int = 0, wait_for_input: bool = True, mode: str = 'SET', tweak: bool = False) -> None:

  """

  Select all time markers using box selection

  """

  ...

def select_leftright(*args, mode: str = 'LEFT', extend: bool = False) -> None:

  """

  Select markers on and left/right of the current frame

  """

  ...
