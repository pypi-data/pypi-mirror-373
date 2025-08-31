"""


Font Operators
**************

:func:`case_set`

:func:`case_toggle`

:func:`change_character`

:func:`change_spacing`

:func:`delete`

:func:`line_break`

:func:`move`

:func:`move_select`

:func:`open`

:func:`select_all`

:func:`select_word`

:func:`selection_set`

:func:`style_set`

:func:`style_toggle`

:func:`text_copy`

:func:`text_cut`

:func:`text_insert`

:func:`text_insert_unicode`

:func:`text_paste`

:func:`text_paste_from_file`

:func:`textbox_add`

:func:`textbox_remove`

:func:`unlink`

"""

import typing

def case_set(*args, case: str = 'LOWER') -> None:

  """

  Set font case

  """

  ...

def case_toggle() -> None:

  """

  Toggle font case

  """

  ...

def change_character(*args, delta: int = 1) -> None:

  """

  Change font character code

  """

  ...

def change_spacing(*args, delta: float = 1.0) -> None:

  """

  Change font spacing

  """

  ...

def delete(*args, type: str = 'PREVIOUS_CHARACTER') -> None:

  """

  Delete text by cursor position

  """

  ...

def line_break() -> None:

  """

  Insert line break at cursor position

  """

  ...

def move(*args, type: str = 'LINE_BEGIN') -> None:

  """

  Move cursor to position type

  """

  ...

def move_select(*args, type: str = 'LINE_BEGIN') -> None:

  """

  Move the cursor while selecting

  """

  ...

def open(*args, filepath: str = '', hide_props_region: bool = True, check_existing: bool = False, filter_blender: bool = False, filter_backup: bool = False, filter_image: bool = False, filter_movie: bool = False, filter_python: bool = False, filter_font: bool = True, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 9, relative_path: bool = True, display_type: str = 'THUMBNAIL', sort_method: str = '') -> None:

  """

  Load a new font from a file

  """

  ...

def select_all() -> None:

  """

  Select all text

  """

  ...

def select_word() -> None:

  """

  Select word under cursor

  """

  ...

def selection_set() -> None:

  """

  Set cursor selection

  """

  ...

def style_set(*args, style: str = 'BOLD', clear: bool = False) -> None:

  """

  Set font style

  """

  ...

def style_toggle(*args, style: str = 'BOLD') -> None:

  """

  Toggle font style

  """

  ...

def text_copy() -> None:

  """

  Copy selected text to clipboard

  """

  ...

def text_cut() -> None:

  """

  Cut selected text to clipboard

  """

  ...

def text_insert(*args, text: str = '', accent: bool = False) -> None:

  """

  Insert text at cursor position

  """

  ...

def text_insert_unicode() -> None:

  """

  Insert Unicode Character

  """

  ...

def text_paste(*args, selection: bool = False) -> None:

  """

  Paste text from clipboard

  """

  ...

def text_paste_from_file(*args, filepath: str = '', hide_props_region: bool = True, check_existing: bool = False, filter_blender: bool = False, filter_backup: bool = False, filter_image: bool = False, filter_movie: bool = False, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = True, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 9, display_type: str = 'DEFAULT', sort_method: str = '') -> None:

  """

  Paste contents from file

  """

  ...

def textbox_add() -> None:

  """

  Add a new text box

  """

  ...

def textbox_remove(*args, index: int = 0) -> None:

  """

  Remove the text box

  """

  ...

def unlink() -> None:

  """

  Unlink active font data-block

  """

  ...
