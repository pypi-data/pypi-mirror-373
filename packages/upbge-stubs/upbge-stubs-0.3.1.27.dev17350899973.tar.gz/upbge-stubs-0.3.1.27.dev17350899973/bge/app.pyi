"""


Application Data (bge.app)
**************************

Module to access application values that remain unchanged during runtime.

:data:`version`

:data:`version_string`

:data:`version_char`

:data:`upbge_version`

:data:`upbge_version_string`

:data:`has_texture_ffmpeg`

:data:`has_joystick`

:data:`has_physics`

"""

import typing

version: typing.Tuple[typing.Any, ...] = ...

"""

The Blender/BGE version as a tuple of 3 ints, eg. (2, 75, 1).

Note: Version tuples can be compared simply with (in)equality symbols;
for example, ``(2, 74, 5) <= (2, 75, 0)`` returns True (lexical order).

"""

version_string: str = ...

"""

The Blender/BGE version formatted as a string, eg. "2.75 (sub 1)".

"""

version_char: str = ...

"""

The Blender/BGE version character (for minor releases).

"""

upbge_version: typing.Tuple[typing.Any, ...] = ...

"""

The UPBGE version as a tuple of 3 ints, eg. (0, 0, 3).

Note: Version tuples can be compared simply with (in)equality symbols;
for example, ``(0, 0, 2) <= (0, 0, 3)`` returns True (lexical order).

"""

upbge_version_string: str = ...

"""

The UPBGE version formatted as a string, eg. "0.0 (sub 3)".

"""

has_texture_ffmpeg: bool = ...

"""

True if the BGE has been built with FFmpeg support,
enabling use of :class:`~bge.texture.ImageFFmpeg` and :class:`~bge.texture.VideoFFmpeg`.

"""

has_joystick: bool = ...

"""

True if the BGE has been built with joystick support.

"""

has_physics: bool = ...

"""

True if the BGE has been built with physics support.

"""
