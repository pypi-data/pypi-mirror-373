"""


Workspace Operators
*******************

:func:`add`

:func:`append_activate`

:func:`delete`

:func:`delete_all_others`

:func:`duplicate`

:func:`reorder_to_back`

:func:`reorder_to_front`

:func:`scene_pin_toggle`

"""

import typing

def add() -> None:

  """

  Add a new workspace by duplicating the current one or appending one from the user configuration

  """

  ...

def append_activate(*args, idname: str = '', filepath: str = '') -> None:

  """

  Append a workspace and make it the active one in the current window

  """

  ...

def delete() -> None:

  """

  Delete the active workspace

  """

  ...

def delete_all_others() -> None:

  """

  Delete all workspaces except this one

  """

  ...

def duplicate() -> None:

  """

  Add a new workspace

  """

  ...

def reorder_to_back() -> None:

  """

  Reorder workspace to be last in the list

  """

  ...

def reorder_to_front() -> None:

  """

  Reorder workspace to be first in the list

  """

  ...

def scene_pin_toggle() -> None:

  """

  Remember the last used scene for the current workspace and switch to it whenever this workspace is activated again

  """

  ...
