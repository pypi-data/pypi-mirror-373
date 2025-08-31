"""


Rasterizer (bge.render)
***********************


Intro
=====

Example of using a :class:`bge.types.SCA_MouseSensor`,
and two :class:`bge.types.SCA_ObjectActuator` to implement MouseLook:

Note: This can also be achieved with the :class:`bge.types.SCA_MouseActuator`.

.. code:: python

  # To use a mouse movement sensor "Mouse" and a
  # motion actuator to mouse look:
  import bge

  # scale sets the speed of motion
  scale = 1.0, 0.5

  co = bge.logic.getCurrentController()
  obj = co.owner
  mouse = co.sensors["Mouse"]
  lmotion = co.actuators["LMove"]
  wmotion = co.actuators["WMove"]

  # Transform the mouse coordinates to see how far the mouse has moved.
  def mousePos():
     x = (bge.render.getWindowWidth() / 2 - mouse.position[0]) * scale[0]
     y = (bge.render.getWindowHeight() / 2 - mouse.position[1]) * scale[1]
     return (x, y)

  pos = mousePos()

  # Set the amount of motion: X is applied in world coordinates...
  wmotion.useLocalTorque = False
  wmotion.torque = ((0.0, 0.0, pos[0]))

  # ...Y is applied in local coordinates
  lmotion.useLocalTorque = True
  lmotion.torque = ((-pos[1], 0.0, 0.0))

  # Activate both actuators
  co.activate(lmotion)
  co.activate(wmotion)

  # Centre the mouse
  bge.render.setMousePosition(int(bge.render.getWindowWidth() / 2), int(bge.render.getWindowHeight() / 2))


Constants
=========

:data:`KX_TEXFACE_MATERIAL`

:data:`KX_BLENDER_MULTITEX_MATERIAL`

:data:`KX_BLENDER_GLSL_MATERIAL`

:data:`VSYNC_OFF`

:data:`VSYNC_ON`

:data:`VSYNC_ADAPTIVE`

:data:`LEFT_EYE`

:data:`RIGHT_EYE`

:data:`RAS_MIPMAP_NONE`

:data:`RAS_MIPMAP_NEAREST`

:data:`RAS_MIPMAP_LINEAR`


Functions
=========

:func:`getWindowWidth`

:func:`getWindowHeight`

:func:`setWindowSize`

:func:`setFullScreen`

:func:`getFullScreen`

:func:`getDisplayDimensions`

:func:`makeScreenshot`

:func:`enableVisibility`

:func:`showMouse`

:func:`setMousePosition`

:func:`setBackgroundColor`

:func:`setEyeSeparation`

:func:`getEyeSeparation`

:func:`setFocalLength`

:func:`getFocalLength`

:func:`getStereoEye`

:func:`setMaterialMode`

:func:`getMaterialMode`

:func:`setGLSLMaterialSetting`

:func:`getGLSLMaterialSetting`

:func:`setAnisotropicFiltering`

:func:`getAnisotropicFiltering`

:func:`setMipmapping`

:func:`getMipmapping`

:func:`drawLine`

:func:`enableMotionBlur`

:func:`disableMotionBlur`

:func:`showFramerate`

:func:`showProfile`

:func:`showProperties`

:func:`autoDebugList`

:func:`clearDebugList`

:func:`setVsync`

:func:`getVsync`

"""

import typing

KX_TEXFACE_MATERIAL: int = ...

"""

Deprecated since version 0.2.2.

"""

KX_BLENDER_MULTITEX_MATERIAL: int = ...

"""

Deprecated since version 0.2.2.

"""

KX_BLENDER_GLSL_MATERIAL: int = ...

"""

Deprecated since version 0.2.2.

"""

VSYNC_OFF: int = ...

"""

Disables vsync

"""

VSYNC_ON: int = ...

"""

Enables vsync

"""

VSYNC_ADAPTIVE: int = ...

"""

Enables adaptive vsync if supported.
Adaptive vsync enables vsync if the framerate is above the monitors refresh rate.
Otherwise, vsync is disabled if the framerate is too low.

"""

LEFT_EYE: int = ...

"""

Deprecated since version 0.3.0.

Left eye being used during stereoscopic rendering.

"""

RIGHT_EYE: int = ...

"""

Deprecated since version 0.3.0.

Right eye being used during stereoscopic rendering.

"""

RAS_MIPMAP_NONE: int = ...

"""

Deprecated since version 0.3.0.

Disables Mipmap filtering.

"""

RAS_MIPMAP_NEAREST: int = ...

"""

Deprecated since version 0.3.0.

Applies mipmap filtering with nearest neighbour interpolation.

"""

RAS_MIPMAP_LINEAR: int = ...

"""

Deprecated since version 0.3.0.

Applies mipmap filtering with nearest linear interpolation.

"""

def getWindowWidth() -> int:

  """

  Gets the width of the window (in pixels)

  """

  ...

def getWindowHeight() -> int:

  """

  Gets the height of the window (in pixels)

  """

  ...

def setWindowSize(width: int, height: int) -> None:

  """

  Set the width and height of the window (in pixels). This also works for fullscreen applications.

  Note: Only works in the standalone player, not the Blender-embedded player.

  """

  ...

def setFullScreen(enable: bool) -> None:

  """

  Set whether or not the window should be fullscreen.

  Note: Only works in the standalone player, not the Blender-embedded player.

  """

  ...

def getFullScreen() -> bool:

  """

  Returns whether or not the window is fullscreen.

  Note: Only works in the standalone player, not the Blender-embedded player; there it always returns False.

  """

  ...

def getDisplayDimensions() -> typing.Tuple[typing.Any, ...]:

  """

  Get the display dimensions, in pixels, of the display (e.g., the
monitor). Can return the size of the entire view, so the
combination of all monitors; for example, ``(3840, 1080)`` for two
side-by-side 1080p monitors.

  """

  ...

def makeScreenshot(filename: str) -> None:

  """

  Writes an image file with the displayed image at the frame end.

  The image is written to *'filename'*.
The path may be absolute (eg. ``/home/foo/image``) or relative when started with
``//`` (eg. ``//image``). Note that absolute paths are not portable between platforms.
If the filename contains a ``#``,
it will be replaced by an incremental index so that screenshots can be taken multiple
times without overwriting the previous ones (eg. ``image-#``).

  Settings for the image are taken from the render settings (file format and respective settings,
gamma and colospace conversion, etc).
The image resolution matches the framebuffer, meaning, the window size and aspect ratio.
When running from the standalone player, instead of the embedded player, only PNG files are supported.
Additional color conversions are also not supported.

  """

  ...

def enableVisibility(visible: typing.Any) -> None:

  """

  Deprecated since version 0.0.1: Doesn't do anything.

  """

  ...

def showMouse(visible: bool) -> None:

  """

  Enables or disables the operating system mouse cursor.

  """

  ...

def setMousePosition(x: int, y: int) -> None:

  """

  Sets the mouse cursor position.

  """

  ...

def setBackgroundColor(rgba: typing.Any) -> None:

  """

  Deprecated since version 0.2.2: Use :attr:`bge.texture.ImageRender.horizon` or :attr:`bge.texture.ImageRender.zenith` instead.

  """

  ...

def setEyeSeparation(eyesep: float) -> None:

  """

  Deprecated since version 0.3.0.

  Sets the eye separation for stereo mode. Usually Focal Length/30 provides a comfortable value.

  """

  ...

def getEyeSeparation() -> float:

  """

  Deprecated since version 0.3.0.

  Gets the current eye separation for stereo mode.

  """

  ...

def setFocalLength(focallength: float) -> None:

  """

  Deprecated since version 0.3.0.

  Sets the focal length for stereo mode. It uses the current camera focal length as initial value.

  """

  ...

def getFocalLength() -> float:

  """

  Deprecated since version 0.3.0.

  Gets the current focal length for stereo mode.

  """

  ...

def getStereoEye() -> typing.Any:

  """

  Deprecated since version 0.3.0.

  Gets the current stereoscopy eye being rendered.
This function is mainly used in a :attr:`bge.types.KX_Scene.pre_draw` callback
function to customize the camera projection matrices for each
stereoscopic eye.

  """

  ...

def setMaterialMode(mode: typing.Any) -> None:

  """

  Deprecated since version 0.2.2.

  """

  ...

def getMaterialMode(mode: typing.Any) -> None:

  """

  Deprecated since version 0.2.2.

  """

  ...

def setGLSLMaterialSetting(setting: typing.Any, enable: typing.Any) -> None:

  """

  Deprecated since version 0.3.0.

  """

  ...

def getGLSLMaterialSetting(setting: typing.Any) -> None:

  """

  Deprecated since version 0.3.0.

  """

  ...

def setAnisotropicFiltering(level: int) -> None:

  """

  Deprecated since version 0.3.0.

  Set the anisotropic filtering level for textures.

  Note: Changing this value can cause all textures to be recreated, which can be slow.

  """

  ...

def getAnisotropicFiltering() -> int:

  """

  Deprecated since version 0.3.0.

  Get the anisotropic filtering level used for textures.

  """

  ...

def setMipmapping(value: int) -> None:

  """

  Deprecated since version 0.3.0.

  Change how to use mipmapping.

  Note: Changing this value can cause all textures to be recreated, which can be slow.

  """

  ...

def getMipmapping() -> int:

  """

  Deprecated since version 0.3.0.

  Get the current mipmapping setting.

  """

  ...

def drawLine(fromVec: typing.List[typing.Any], toVec: typing.List[typing.Any], color: typing.List[typing.Any]) -> None:

  """

  Draw a line in the 3D scene.

  """

  ...

def enableMotionBlur(factor: float) -> None:

  """

  Deprecated since version 0.3.0.

  Enable the motion blur effect.

  """

  ...

def disableMotionBlur() -> None:

  """

  Deprecated since version 0.3.0.

  Disable the motion blur effect.

  """

  ...

def showFramerate(enable: bool) -> None:

  """

  Show or hide the framerate.

  """

  ...

def showProfile(enable: bool) -> None:

  """

  Show or hide the profile.

  """

  ...

def showProperties(enable: bool) -> None:

  """

  Show or hide the debug properties.

  """

  ...

def autoDebugList(enable: bool) -> None:

  """

  Enable or disable auto adding debug properties to the debug list.

  """

  ...

def clearDebugList() -> None:

  """

  Clears the debug property list.

  """

  ...

def setVsync(value: int) -> None:

  """

  Set the vsync value

  """

  ...

def getVsync() -> int:

  """

  Get the current vsync value

  """

  ...
