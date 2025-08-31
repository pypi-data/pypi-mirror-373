"""


Font Drawing (blf)
******************

This module provides access to Blender's text drawing functions.


Hello World Text Example
========================

Example of using the blf module. For this module to work we
need to use the GPU module :mod:`gpu` as well.

.. code::

  # Import stand alone modules.
  import blf
  import bpy

  font_info = {
      "font_id": 0,
      "handler": None,
  }


  def init():
      \"\"\"init function - runs once\"\"\"
      import os
      # Create a new font object, use external TTF file.
      font_path = bpy.path.abspath('//Zeyada.ttf')
      # Store the font index - to use later.
      if os.path.exists(font_path):
          font_info["font_id"] = blf.load(font_path)
      else:
          # Default font.
          font_info["font_id"] = 0

      # Set the font drawing routine to run every frame.
      font_info["handler"] = bpy.types.SpaceView3D.draw_handler_add(
          draw_callback_px, (None, None), 'WINDOW', 'POST_PIXEL')


  def draw_callback_px(self, context):
      \"\"\"Draw on the viewports\"\"\"
      # BLF drawing routine.
      font_id = font_info["font_id"]
      blf.position(font_id, 2, 80, 0)
      blf.size(font_id, 50.0)
      blf.draw(font_id, "Hello World")


  if __name__ == '__main__':
      init()


Drawing Text to an Image
========================

Example showing how text can be draw into an image.
This can be done by binding an image buffer (:mod:`imbuf`) to the font's ID.

.. code::

  import blf
  import imbuf

  image_size = 512, 512
  font_size = 20

  ibuf = imbuf.new(image_size)

  font_id = blf.load("/path/to/font.ttf")

  blf.color(font_id, 1.0, 1.0, 1.0, 1.0)
  blf.size(font_id, font_size)
  blf.position(font_id, 0, image_size[0] - font_size, 0)

  blf.enable(font_id, blf.WORD_WRAP)
  blf.word_wrap(font_id, image_size[0])

  with blf.bind_imbuf(font_id, ibuf, display_name="sRGB"):
      blf.draw_buffer(font_id, "Lots of wrapped text. " * 50)

  imbuf.write(ibuf, filepath="/path/to/image.png")

:func:`aspect`

:func:`bind_imbuf`

:func:`clipping`

:func:`color`

:func:`dimensions`

:func:`disable`

:func:`draw`

:func:`draw_buffer`

:func:`enable`

:func:`load`

:func:`position`

:func:`rotation`

:func:`shadow`

:func:`shadow_offset`

:func:`size`

:func:`unload`

:func:`word_wrap`

:data:`CLIPPING`

:data:`MONOCHROME`

:data:`ROTATION`

:data:`SHADOW`

:data:`WORD_WRAP`

"""

import typing

def aspect(fontid: int, aspect: float) -> None:

  """

  Set the aspect for drawing text.

  """

  ...

def bind_imbuf(self, fontid: int, image: typing.Any) -> typing.Any:

  """

  Context manager to draw text into an image buffer instead of the GPU's context.

  """

  ...

def clipping(fontid: int, xmin: float, ymin: float, xmax: float, ymax: float) -> None:

  """

  Set the clipping, enable/disable using CLIPPING.

  """

  ...

def color(fontid: int, r: float, g: float, b: float, a: float) -> None:

  """

  Set the color for drawing text.

  """

  ...

def dimensions(fontid: int, text: str) -> typing.Any:

  """

  Return the width and height of the text.

  """

  ...

def disable(fontid: int, option: int) -> None:

  """

  Disable option.

  """

  ...

def draw(fontid: int, text: str) -> None:

  """

  Draw text in the current context.

  """

  ...

def draw_buffer(fontid: int, text: str) -> None:

  """

  Draw text into the buffer bound to the fontid.

  """

  ...

def enable(fontid: int, option: int) -> None:

  """

  Enable option.

  """

  ...

def load(filepath: str) -> int:

  """

  Load a new font.

  """

  ...

def position(fontid: int, x: float, y: float, z: float) -> None:

  """

  Set the position for drawing text.

  """

  ...

def rotation(fontid: int, angle: float) -> None:

  """

  Set the text rotation angle, enable/disable using ROTATION.

  """

  ...

def shadow(fontid: int, level: int, r: float, g: float, b: float, a: float) -> None:

  """

  Shadow options, enable/disable using SHADOW .

  """

  ...

def shadow_offset(fontid: int, x: float, y: float) -> None:

  """

  Set the offset for shadow text.

  """

  ...

def size(fontid: int, size: float) -> None:

  """

  Set the size for drawing text.

  """

  ...

def unload(filepath: str) -> None:

  """

  Unload an existing font.

  """

  ...

def word_wrap(fontid: int, wrap_width: int) -> None:

  """

  Set the wrap width, enable/disable using WORD_WRAP.

  """

  ...

CLIPPING: typing.Any = ...

"""

Constant value 2

"""

MONOCHROME: typing.Any = ...

"""

Constant value 128

"""

ROTATION: typing.Any = ...

"""

Constant value 1

"""

SHADOW: typing.Any = ...

"""

Constant value 4

"""

WORD_WRAP: typing.Any = ...

"""

Constant value 64

"""
