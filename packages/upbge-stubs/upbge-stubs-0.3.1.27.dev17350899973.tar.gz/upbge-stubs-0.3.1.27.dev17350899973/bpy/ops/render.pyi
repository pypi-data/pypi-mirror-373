"""


Render Operators
****************

:func:`color_management_white_balance_preset_add`

:func:`eevee_raytracing_preset_add`

:func:`opengl`

:func:`play_rendered_anim`

:func:`preset_add`

:func:`render`

:func:`shutter_curve_preset`

:func:`view_cancel`

:func:`view_show`

"""

import typing

def color_management_white_balance_preset_add(*args, name: str = '', remove_name: bool = False, remove_active: bool = False) -> None:

  """

  Add or remove a white balance preset

  """

  ...

def eevee_raytracing_preset_add(*args, name: str = '', remove_name: bool = False, remove_active: bool = False) -> None:

  """

  Add or remove an EEVEE ray-tracing preset

  """

  ...

def opengl(*args, animation: bool = False, render_keyed_only: bool = False, sequencer: bool = False, write_still: bool = False, view_context: bool = True) -> None:

  """

  Take a snapshot of the active viewport

  """

  ...

def play_rendered_anim() -> None:

  """

  Play back rendered frames/movies using an external player

  """

  ...

def preset_add(*args, name: str = '', remove_name: bool = False, remove_active: bool = False) -> None:

  """

  Add or remove a Render Preset

  """

  ...

def render(*args, animation: bool = False, write_still: bool = False, use_viewport: bool = False, layer: str = '', scene: str = '') -> None:

  """

  Render active scene

  """

  ...

def shutter_curve_preset(*args, shape: str = 'SMOOTH') -> None:

  """

  Set shutter curve

  """

  ...

def view_cancel() -> None:

  """

  Cancel show render view

  """

  ...

def view_show() -> None:

  """

  Toggle show render view

  """

  ...
