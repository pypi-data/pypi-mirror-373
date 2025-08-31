"""


Image Buffer (imbuf)
********************

This module provides access to Blender's image manipulation API.

It provides access to image buffers outside of Blender's
:class:`bpy.types.Image` data-block context.

:func:`load`

:func:`load_from_buffer`

:func:`new`

:func:`write`

"""

from . import types

import typing

def load(filepath: str) -> ImBuf:

  """

  Load an image from a file.

  """

  ...

def load_from_buffer(buffer: typing.Any) -> ImBuf:

  """

  Load an image from a buffer.

  """

  ...

def new(size: typing.Any) -> ImBuf:

  """

  Load a new image.

  """

  ...

def write(image: ImBuf, *args, filepath: str = image.filepath) -> None:

  """

  Write an image.

  """

  ...
