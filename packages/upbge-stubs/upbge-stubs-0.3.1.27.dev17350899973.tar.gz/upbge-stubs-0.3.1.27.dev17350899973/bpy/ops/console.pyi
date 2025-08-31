"""


Console Operators
*****************

:func:`autocomplete`

:func:`banner`

:func:`clear`

:func:`clear_line`

:func:`copy`

:func:`copy_as_script`

:func:`delete`

:func:`execute`

:func:`history_append`

:func:`history_cycle`

:func:`indent`

:func:`indent_or_autocomplete`

:func:`insert`

:func:`language`

:func:`move`

:func:`paste`

:func:`scrollback_append`

:func:`select_all`

:func:`select_set`

:func:`select_word`

:func:`unindent`

"""

import typing

def autocomplete() -> None:

  """

  Evaluate the namespace up until the cursor and give a list of options or complete the name if there is only one

  """

  ...

def banner() -> None:

  """

  Print a message when the terminal initializes

  """

  ...

def clear(*args, scrollback: bool = True, history: bool = False) -> None:

  """

  Clear text by type

  """

  ...

def clear_line() -> None:

  """

  Clear the line and store in history

  """

  ...

def copy(*args, delete: bool = False) -> None:

  """

  Copy selected text to clipboard

  """

  ...

def copy_as_script() -> None:

  """

  Copy the console contents for use in a script

  """

  ...

def delete(*args, type: str = 'NEXT_CHARACTER') -> None:

  """

  Delete text by cursor position

  """

  ...

def execute(*args, interactive: bool = False) -> None:

  """

  Execute the current console line as a Python expression

  """

  ...

def history_append(*args, text: str = '', current_character: int = 0, remove_duplicates: bool = False) -> None:

  """

  Append history at cursor position

  """

  ...

def history_cycle(*args, reverse: bool = False) -> None:

  """

  Cycle through history

  """

  ...

def indent() -> None:

  """

  Add 4 spaces at line beginning

  """

  ...

def indent_or_autocomplete() -> None:

  """

  Indent selected text or autocomplete

  """

  ...

def insert(*args, text: str = '') -> None:

  """

  Insert text at cursor position

  """

  ...

def language(*args, language: str = '') -> None:

  """

  Set the current language for this console

  """

  ...

def move(*args, type: str = 'LINE_BEGIN', select: bool = False) -> None:

  """

  Move cursor position

  """

  ...

def paste(*args, selection: bool = False) -> None:

  """

  Paste text from clipboard

  """

  ...

def scrollback_append(*args, text: str = '', type: str = 'OUTPUT') -> None:

  """

  Append scrollback text by type

  """

  ...

def select_all() -> None:

  """

  Select all the text

  """

  ...

def select_set() -> None:

  """

  Set the console selection

  """

  ...

def select_word() -> None:

  """

  Select word at cursor position

  """

  ...

def unindent() -> None:

  """

  Delete 4 spaces from line beginning

  """

  ...
