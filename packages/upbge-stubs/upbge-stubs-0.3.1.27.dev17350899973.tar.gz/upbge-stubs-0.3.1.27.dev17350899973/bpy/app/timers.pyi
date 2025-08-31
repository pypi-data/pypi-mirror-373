"""


Application Timers (bpy.app.timers)
***********************************


Run a Function in x Seconds
===========================

.. code::

  import bpy


  def in_5_seconds():
      print("Hello World")


  bpy.app.timers.register(in_5_seconds, first_interval=5)


Run a Function every x Seconds
==============================

.. code::

  import bpy


  def every_2_seconds():
      print("Hello World")
      return 2.0


  bpy.app.timers.register(every_2_seconds)


Run a Function n times every x seconds
======================================

.. code::

  import bpy

  counter = 0


  def run_10_times():
      global counter
      counter += 1
      print(counter)
      if counter == 10:
          return None
      return 0.1


  bpy.app.timers.register(run_10_times)


Assign parameters to functions
==============================

.. code::

  import bpy
  import functools


  def print_message(message):
      print("Message:", message)


  bpy.app.timers.register(functools.partial(print_message, "Hello"), first_interval=2.0)
  bpy.app.timers.register(functools.partial(print_message, "World"), first_interval=3.0)

:func:`is_registered`

:func:`register`

:func:`unregister`

"""

import typing

def is_registered(function: typing.Any) -> bool:

  """

  Check if this function is registered as a timer.

  """

  ...

def register(function: typing.Any, *args, first_interval: float = 0, persistent: bool = False) -> None:

  """

  Add a new function that will be called after the specified amount of seconds.
The function gets no arguments and is expected to return either None or a float.
If ``None`` is returned, the timer will be unregistered.
A returned number specifies the delay until the function is called again.
``functools.partial`` can be used to assign some parameters.

  """

  ...

def unregister(function: typing.Any) -> None:

  """

  Unregister timer.

  """

  ...
