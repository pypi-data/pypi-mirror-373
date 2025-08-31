"""


Game Keys (bge.events)
**********************


Intro
=====

This module holds key constants for the SCA_KeyboardSensor.

.. code:: python

  # Set a connected keyboard sensor to accept F1
  import bge

  co = bge.logic.getCurrentController()
  # 'Keyboard' is a keyboard sensor
  sensor = co.sensors["Keyboard"]
  sensor.key = bge.events.F1KEY

.. code:: python

  # Do the all keys thing
  import bge

  co = bge.logic.getCurrentController()
  # 'Keyboard' is a keyboard sensor
  sensor = co.sensors["Keyboard"]

  for key, input in sensor.inputs:
       # key[0] == bge.events.keycode = event.type, key[1] = input
       if bge.logic.KX_INPUT_JUST_ACTIVATED in input.queue:
               if key == bge.events.WKEY:
                       # Activate Forward!
               if key == bge.events.SKEY:
                       # Activate Backward!
               if key == bge.events.AKEY:
                       # Activate Left!
               if key == bge.events.DKEY:
                       # Activate Right!

.. code:: python

  # The all keys thing without a keyboard sensor (but you will
  # need an always sensor with pulse mode on)
  import bge

  # Just shortening names here
  keyboard = bge.logic.keyboard
  JUST_ACTIVATED = bge.logic.KX_INPUT_JUST_ACTIVATED

  if JUST_ACTIVATED in keyboard.inputs[bge.events.WKEY].queue:
       print("Activate Forward!")
  if JUST_ACTIVATED in keyboard.inputs[bge.events.SKEY].queue:
       print("Activate Backward!")
  if JUST_ACTIVATED in keyboard.inputs[bge.events.AKEY].queue:
       print("Activate Left!")
  if JUST_ACTIVATED in keyboard.inputs[bge.events.DKEY].queue:
       print("Activate Right!")


Functions
=========

:func:`EventToString`

:func:`EventToCharacter`


Keys (Constants)
================

.. _mouse-keys:


Mouse Keys
----------

:data:`LEFTMOUSE`

:data:`MIDDLEMOUSE`

:data:`RIGHTMOUSE`

:data:`BUTTON4MOUSE`

:data:`BUTTON5MOUSE`

:data:`BUTTON6MOUSE`

:data:`BUTTON7MOUSE`

:data:`WHEELUPMOUSE`

:data:`WHEELDOWNMOUSE`

:data:`MOUSEX`

:data:`MOUSEY`

.. _keyboard-keys:


Keyboard Keys
-------------


Alphabet keys
~~~~~~~~~~~~~

:data:`AKEY`

:data:`BKEY`

:data:`CKEY`

:data:`DKEY`

:data:`EKEY`

:data:`FKEY`

:data:`GKEY`

:data:`HKEY`

:data:`IKEY`

:data:`JKEY`

:data:`KKEY`

:data:`LKEY`

:data:`MKEY`

:data:`NKEY`

:data:`OKEY`

:data:`PKEY`

:data:`QKEY`

:data:`RKEY`

:data:`SKEY`

:data:`TKEY`

:data:`UKEY`

:data:`VKEY`

:data:`WKEY`

:data:`XKEY`

:data:`YKEY`

:data:`ZKEY`


Number keys
~~~~~~~~~~~

:data:`ZEROKEY`

:data:`ONEKEY`

:data:`TWOKEY`

:data:`THREEKEY`

:data:`FOURKEY`

:data:`FIVEKEY`

:data:`SIXKEY`

:data:`SEVENKEY`

:data:`EIGHTKEY`

:data:`NINEKEY`


Modifiers Keys
~~~~~~~~~~~~~~

:data:`CAPSLOCKKEY`

:data:`LEFTCTRLKEY`

:data:`LEFTALTKEY`

:data:`RIGHTALTKEY`

:data:`RIGHTCTRLKEY`

:data:`RIGHTSHIFTKEY`

:data:`LEFTSHIFTKEY`


Arrow Keys
~~~~~~~~~~

:data:`LEFTARROWKEY`

:data:`DOWNARROWKEY`

:data:`RIGHTARROWKEY`

:data:`UPARROWKEY`


Numberpad Keys
~~~~~~~~~~~~~~

:data:`PAD0`

:data:`PAD1`

:data:`PAD2`

:data:`PAD3`

:data:`PAD4`

:data:`PAD5`

:data:`PAD6`

:data:`PAD7`

:data:`PAD8`

:data:`PAD9`

:data:`PADPERIOD`

:data:`PADSLASHKEY`

:data:`PADASTERKEY`

:data:`PADMINUS`

:data:`PADENTER`

:data:`PADPLUSKEY`


Function Keys
~~~~~~~~~~~~~

:data:`F1KEY`

:data:`F2KEY`

:data:`F3KEY`

:data:`F4KEY`

:data:`F5KEY`

:data:`F6KEY`

:data:`F7KEY`

:data:`F8KEY`

:data:`F9KEY`

:data:`F10KEY`

:data:`F11KEY`

:data:`F12KEY`

:data:`F13KEY`

:data:`F14KEY`

:data:`F15KEY`

:data:`F16KEY`

:data:`F17KEY`

:data:`F18KEY`

:data:`F19KEY`


Other Keys
~~~~~~~~~~

:data:`ACCENTGRAVEKEY`

:data:`BACKSLASHKEY`

:data:`BACKSPACEKEY`

:data:`COMMAKEY`

:data:`DELKEY`

:data:`ENDKEY`

:data:`EQUALKEY`

:data:`ESCKEY`

:data:`HOMEKEY`

:data:`INSERTKEY`

:data:`LEFTBRACKETKEY`

:data:`LINEFEEDKEY`

:data:`MINUSKEY`

:data:`PAGEDOWNKEY`

:data:`PAGEUPKEY`

:data:`PAUSEKEY`

:data:`PERIODKEY`

:data:`QUOTEKEY`

:data:`RIGHTBRACKETKEY`

:data:`RETKEY`

:data:`ENTERKEY`

:data:`SEMICOLONKEY`

:data:`SLASHKEY`

:data:`SPACEKEY`

:data:`TABKEY`

"""

import typing

def EventToString(event: int) -> str:

  """

  Return the string name of a key event. Will raise a ValueError error if its invalid.

  """

  ...

def EventToCharacter(event: int, shift: bool) -> str:

  """

  Return the string name of a key event. Returns an empty string if the event cant be represented as a character.

  """

  ...

LEFTMOUSE: typing.Any = ...

MIDDLEMOUSE: typing.Any = ...

RIGHTMOUSE: typing.Any = ...

BUTTON4MOUSE: typing.Any = ...

BUTTON5MOUSE: typing.Any = ...

BUTTON6MOUSE: typing.Any = ...

BUTTON7MOUSE: typing.Any = ...

WHEELUPMOUSE: typing.Any = ...

WHEELDOWNMOUSE: typing.Any = ...

MOUSEX: typing.Any = ...

MOUSEY: typing.Any = ...

AKEY: typing.Any = ...

BKEY: typing.Any = ...

CKEY: typing.Any = ...

DKEY: typing.Any = ...

EKEY: typing.Any = ...

FKEY: typing.Any = ...

GKEY: typing.Any = ...

HKEY: typing.Any = ...

IKEY: typing.Any = ...

JKEY: typing.Any = ...

KKEY: typing.Any = ...

LKEY: typing.Any = ...

MKEY: typing.Any = ...

NKEY: typing.Any = ...

OKEY: typing.Any = ...

PKEY: typing.Any = ...

QKEY: typing.Any = ...

RKEY: typing.Any = ...

SKEY: typing.Any = ...

TKEY: typing.Any = ...

UKEY: typing.Any = ...

VKEY: typing.Any = ...

WKEY: typing.Any = ...

XKEY: typing.Any = ...

YKEY: typing.Any = ...

ZKEY: typing.Any = ...

ZEROKEY: typing.Any = ...

ONEKEY: typing.Any = ...

TWOKEY: typing.Any = ...

THREEKEY: typing.Any = ...

FOURKEY: typing.Any = ...

FIVEKEY: typing.Any = ...

SIXKEY: typing.Any = ...

SEVENKEY: typing.Any = ...

EIGHTKEY: typing.Any = ...

NINEKEY: typing.Any = ...

CAPSLOCKKEY: typing.Any = ...

LEFTCTRLKEY: typing.Any = ...

LEFTALTKEY: typing.Any = ...

RIGHTALTKEY: typing.Any = ...

RIGHTCTRLKEY: typing.Any = ...

RIGHTSHIFTKEY: typing.Any = ...

LEFTSHIFTKEY: typing.Any = ...

LEFTARROWKEY: typing.Any = ...

DOWNARROWKEY: typing.Any = ...

RIGHTARROWKEY: typing.Any = ...

UPARROWKEY: typing.Any = ...

PAD0: typing.Any = ...

PAD1: typing.Any = ...

PAD2: typing.Any = ...

PAD3: typing.Any = ...

PAD4: typing.Any = ...

PAD5: typing.Any = ...

PAD6: typing.Any = ...

PAD7: typing.Any = ...

PAD8: typing.Any = ...

PAD9: typing.Any = ...

PADPERIOD: typing.Any = ...

PADSLASHKEY: typing.Any = ...

PADASTERKEY: typing.Any = ...

PADMINUS: typing.Any = ...

PADENTER: typing.Any = ...

PADPLUSKEY: typing.Any = ...

F1KEY: typing.Any = ...

F2KEY: typing.Any = ...

F3KEY: typing.Any = ...

F4KEY: typing.Any = ...

F5KEY: typing.Any = ...

F6KEY: typing.Any = ...

F7KEY: typing.Any = ...

F8KEY: typing.Any = ...

F9KEY: typing.Any = ...

F10KEY: typing.Any = ...

F11KEY: typing.Any = ...

F12KEY: typing.Any = ...

F13KEY: typing.Any = ...

F14KEY: typing.Any = ...

F15KEY: typing.Any = ...

F16KEY: typing.Any = ...

F17KEY: typing.Any = ...

F18KEY: typing.Any = ...

F19KEY: typing.Any = ...

ACCENTGRAVEKEY: typing.Any = ...

BACKSLASHKEY: typing.Any = ...

BACKSPACEKEY: typing.Any = ...

COMMAKEY: typing.Any = ...

DELKEY: typing.Any = ...

ENDKEY: typing.Any = ...

EQUALKEY: typing.Any = ...

ESCKEY: typing.Any = ...

HOMEKEY: typing.Any = ...

INSERTKEY: typing.Any = ...

LEFTBRACKETKEY: typing.Any = ...

LINEFEEDKEY: typing.Any = ...

MINUSKEY: typing.Any = ...

PAGEDOWNKEY: typing.Any = ...

PAGEUPKEY: typing.Any = ...

PAUSEKEY: typing.Any = ...

PERIODKEY: typing.Any = ...

QUOTEKEY: typing.Any = ...

RIGHTBRACKETKEY: typing.Any = ...

RETKEY: typing.Any = ...

"""

Deprecated since version 0.0.1: Use :data:`~bge.events.ENTERKEY`.

"""

ENTERKEY: typing.Any = ...

SEMICOLONKEY: typing.Any = ...

SLASHKEY: typing.Any = ...

SPACEKEY: typing.Any = ...

TABKEY: typing.Any = ...
