"""


Spreadsheet Operators
*********************

:func:`add_row_filter_rule`

:func:`change_spreadsheet_data_source`

:func:`fit_column`

:func:`remove_row_filter_rule`

:func:`reorder_columns`

:func:`resize_column`

:func:`toggle_pin`

"""

import typing

def add_row_filter_rule() -> None:

  """

  Add a filter to remove rows from the displayed data

  """

  ...

def change_spreadsheet_data_source(*args, component_type: int = 0, attribute_domain_type: int = 0) -> None:

  """

  Change visible data source in the spreadsheet

  """

  ...

def fit_column() -> None:

  """

  Resize a spreadsheet column to the width of the data

  """

  ...

def remove_row_filter_rule(*args, index: int = 0) -> None:

  """

  Remove a row filter from the rules

  """

  ...

def reorder_columns() -> None:

  """

  Change the order of columns

  """

  ...

def resize_column() -> None:

  """

  Resize a spreadsheet column

  """

  ...

def toggle_pin() -> None:

  """

  Turn on or off pinning

  """

  ...
