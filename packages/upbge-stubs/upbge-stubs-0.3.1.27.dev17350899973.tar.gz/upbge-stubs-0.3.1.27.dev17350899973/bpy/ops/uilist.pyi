"""


Uilist Operators
****************

:func:`entry_add`

:func:`entry_move`

:func:`entry_remove`

"""

import typing

def entry_add(*args, list_path: str = '', active_index_path: str = '') -> None:

  """

  Add an entry to the list after the current active item

  """

  ...

def entry_move(*args, list_path: str = '', active_index_path: str = '', direction: str = 'UP') -> None:

  """

  Move an entry in the list up or down

  """

  ...

def entry_remove(*args, list_path: str = '', active_index_path: str = '') -> None:

  """

  Remove the selected entry from the list

  """

  ...
