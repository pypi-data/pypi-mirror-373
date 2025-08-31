"""


widget
^^^^^^

This module defines the following constants:

Widget options:
* BGUI_DEFAULT = 0
* BGUI_CENTERX = 1
* BGUI_CENTERY = 2
* BGUI_NO_NORMALIZE = 4
* BGUI_NO_THEME = 8
* BGUI_NO_FOCUS = 16
* BGUI_CACHE = 32
* BGUI_CENTERED = BGUI_CENTERX | BGUI_CENTERY

Widget overflow:
* BGUI_OVERFLOW_NONE = 0
* BGUI_OVERFLOW_HIDDEN = 1
* BGUI_OVERFLOW_REPLACE = 2
* BGUI_OVERFLOW_CALLBACK = 3

Mouse event states:
* BGUI_MOUSE_NONE = 0
* BGUI_MOUSE_CLICK = 1
* BGUI_MOUSE_RELEASE = 2
* BGUI_MOUSE_ACTIVE = 4

Note: The Widget class should not be used directly in a gui, but should instead be subclassed to create other widgets.

"""

import typing
