"""


Video Texture (bge.texture)
***************************


Introduction
============

The ``bge.texture`` module allows you to manipulate textures during the game.
Several sources for texture are possible: video files, image files, video capture,
memory buffer, camera render or a mix of that.
The video and image files can be loaded from the Internet using a URL instead of a file name.
In addition, you can apply filters on the images before sending them to the GPU,
allowing video effect: blue screen, color band, gray, normal map.
``bge.texture`` uses FFmpeg to load images and videos.
All the formats and codecs that FFmpeg supports are supported by ``bge.texture``,
including but not limited to:

* AVI

* Ogg

* Xvid

* Theora

* dv1394 camera

* video4linux capture card (this includes many webcams)

* videoForWindows capture card (this includes many webcams)

* JPG


How it works
------------

The principle is simple: first you identify a texture on an existing object using the
:func:`~bge.texture.materialID` function, then you create a new texture with dynamic content
and swap the two textures in the GPU.

The game engine is not aware of the substitution and continues to display the object as always,
except that you are now in control of the texture.

When the texture object is deleted, the new texture is deleted and the old texture restored.


Game Preparation
----------------

Before you can use the :mod:`bge.texture` module,
you must have objects with textures applied appropriately.

Imagine you want to have a television showing live broadcast programs in the game.
You will create a television object and UV-apply a different texture at the place of the screen,
for example ``tv.png``. What this texture looks like is not important;
probably you want to make it dark gray to simulate power-off state.
When the television must be turned on, you create a dynamic texture from a video capture card
and use it instead of ``tv.png``: the TV screen will come to life.

You have two ways to define textures that ``bge.texture`` can grab:

* Simple UV texture.

* Blender material with image texture channel.

Because ``bge.texture`` works at texture level, it is compatible with all
the Blender Game Engine's fancy texturing features: GLSL, multi-texture, custom shaders, etc.


Examples
========


Basic Video Playback
--------------------

Example of how to replace a texture in game with a video.
It needs to run everyframe.
To avoid any confusion with the location of the file,
we will use :meth:`bge.logic.expandPath` to build an absolute file name,
assuming the video file is in the same directory as the blend-file.

.. code::

  import bge
  from bge import texture
  from bge import logic

  cont = logic.getCurrentController()
  obj = cont.owner

  # the creation of the texture must be done once: save the
  # texture object in an attribute of bge.logic module makes it persistent
  if not hasattr(logic, 'video'):

      # identify a static texture by name
      matID = texture.materialID(obj, 'IMvideo.png')

      # create a dynamic texture that will replace the static texture
      logic.video = texture.Texture(obj, matID)

      # define a source of image for the texture, here a movie
      movie = logic.expandPath('//trailer_400p.ogg')
      logic.video.source = texture.VideoFFmpeg(movie)
      logic.video.source.scale = True

      # Note that we can change the ``Texture`` source at any time.
      # Suppose we want to switch between two movies during the game:
      logic.mySources[0] = texture.VideoFFmpeg('movie1.avi')
      logic.mySources[1] = texture.VideoFFmpeg('movie2.avi')

      #And then assign (and reassign) the source during the game
      logic.video.source = logic.mySources[movieSel]

      # quick off the movie, but it wont play in the background
      logic.video.source.play()


  # Video playback is not a background process: it happens only when we refresh the texture.
  # So you need to call this function every frame to ensure update of the texture.
  logic.video.refresh(True)


Texture Replacement
-------------------

Example of how to replace a texture in game with an external image.
``createTexture()`` and ``removeTexture()`` are to be called from a
module Python Controller.

.. code::

  from bge import logic
  from bge import texture


  def createTexture(cont):
      \"\"\"Create a new Dynamic Texture\"\"\"
      obj = cont.owner

      # get the reference pointer (ID) of the internal texture
      ID = texture.materialID(obj, 'IMoriginal.png')

      # create a texture object
      object_texture = texture.Texture(obj, ID)

      # create a new source with an external image
      url = logic.expandPath("//newtexture.jpg")
      new_source = texture.ImageFFmpeg(url)

      # the texture has to be stored in a permanent Python object
      logic.texture = object_texture

      # update/replace the texture
      logic.texture.source = new_source
      logic.texture.refresh(False)


  def removeTexture(cont):
      \"\"\"Delete the Dynamic Texture, reversing back the final to its original state.\"\"\"
      try:
          del logic.texture
      except:
          pass


Video Capture with DeckLink
---------------------------

Video frames captured with DeckLink cards have pixel formats that are generally not directly
usable by OpenGL, they must be processed by a shader. The three shaders presented here should
cover all common video capture cases.

This file reflects the current video transfer method implemented in the Decklink module:
whenever possible the video images are transferred as float texture because this is more
compatible with GPUs. Of course, only the pixel formats that have a correspondent GL format
can be transferred as float. Look for fg_shaders in this file for an exhaustive list.

Other pixel formats will be transferred as 32 bits integer red-channel texture but this
won't work with certain GPU (Intel GMA); the corresponding shaders are not shown here.
However, it should not be necessary to use any of them as the list below covers all practical
cases of video capture with all types of Decklink product.

In other words, only use one of the pixel format below and you will be fine. Note that depending
on the video stream, only certain pixel formats will be allowed (others will throw an exception).
For example, to capture a PAL video stream, you must use one of the YUV formats.

To find which pixel format is suitable for a particular video stream, use the 'Media Express'
utility that comes with the Decklink software : if you see the video in the 'Log and Capture'
Window, you have selected the right pixel format and you can use the same in Blender.

Note: These shaders only decode the RGB channel and set the alpha channel to a fixed
value (look for color.a = ). It's up to you to add postprocessing to the color.

Note: These shaders are compatible with 2D and 3D video stream.

.. code::

  import bge
  from bge import logic
  from bge import texture as vt

  # The default vertex shader, because we need one
  #
  VertexShader = \"\"\"
  #version 130
     void main()
     {
        gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
        gl_TexCoord[0] = gl_MultiTexCoord0;
     }

  \"\"\"

  # For use with RGB video stream: the pixel is directly usable
  #
  FragmentShader_R10l = \"\"\"
      #version 130
      uniform sampler2D tex;
      // stereo = 1.0 if 2D image, =0.5 if 3D (left eye below, right eye above)
      uniform float stereo;
      // eye = 0.0 for the left eye, 0.5 for the right eye
      uniform float eye;

      void main(void)
      {
          vec4 color;
          float tx, ty;
          tx = gl_TexCoord[0].x;
          ty = eye+gl_TexCoord[0].y*stereo;
          color = texture(tex, vec2(tx,ty));
          color.a = 0.7;
          gl_FragColor = color;
      }
  \"\"\"

  # For use with YUV video stream
  #
  FragmentShader_2vuy = \"\"\"
      #version 130
      uniform sampler2D tex;
      // stereo = 1.0 if 2D image, =0.5 if 3D (left eye below, right eye above)
      uniform float stereo;
      // eye = 0.0 for the left eye, 0.5 for the right eye
      uniform float eye;

      void main(void)
      {
          vec4 color;
          float tx, ty, width, Y, Cb, Cr;
          int px;
          tx = gl_TexCoord[0].x;
          ty = eye+gl_TexCoord[0].y*stereo;
          width = float(textureSize(tex, 0).x);
          color = texture(tex, vec2(tx, ty));
          px = int(floor(fract(tx*width)*2.0));
          switch (px) {
          case 0:
              Y = color.g;
              break;
          case 1:
              Y = color.a;
              break;
          }
          Y = (Y - 0.0625) * 1.168949772;
          Cb = (color.b - 0.0625) * 1.142857143 - 0.5;
          Cr = (color.r - 0.0625) * 1.142857143 - 0.5;
          color.r = Y + 1.5748 * Cr;
          color.g = Y - 0.1873 * Cb - 0.4681 * Cr;
          color.b = Y + 1.8556 * Cb;
          color.a = 0.7;
          gl_FragColor = color;
      }
  \"\"\"

  # For use with high resolution YUV
  #
  FragmentShader_v210 = \"\"\"
      #version 130
      uniform sampler2D tex;
      // stereo = 1.0 if 2D image, =0.5 if 3D (left eye below, right eye above)
      uniform float stereo;
      // eye = 0.0 for the left eye, 0.5 for the right eye
      uniform float eye;

      void main(void)
      {
          vec4 color, color1, color2, color3;
          int px;
          float tx, ty, width, sx, dx, bx, Y, Cb, Cr;
          tx = gl_TexCoord[0].x;
          ty = eye+gl_TexCoord[0].y*stereo;
          width = float(textureSize(tex, 0).x);
          // to sample macro pixels (6 pixels in 4 words)
          sx = tx*width*0.25+0.01;
          // index of display pixel in the macro pixel 0..5
          px = int(floor(fract(sx)*6.0));
          // increment as we sample the macro pixel
          dx = 1.0/width;
          // base x coord of macro pixel
          bx = (floor(sx)+0.01)*dx*4.0;
          color = texture(tex, vec2(bx, ty));
          color1 = texture(tex, vec2(bx+dx, ty));
          color2 = texture(tex, vec2(bx+dx*2.0, ty));
          color3 = texture(tex, vec2(bx+dx*3.0, ty));
          switch (px) {
          case 0:
          case 1:
              Cb = color.b;
              Cr = color.r;
              break;
          case 2:
          case 3:
              Cb = color1.g;
              Cr = color2.b;
              break;
          default:
              Cb = color2.r;
              Cr = color3.g;
              break;
          }
          switch (px) {
          case 0:
              Y = color.g;
              break;
          case 1:
              Y = color1.b;
              break;
          case 2:
              Y = color1.r;
              break;
          case 3:
              Y = color2.g;
              break;
          case 4:
              Y = color3.b;
              break;
          default:
              Y = color3.r;
              break;
          }
          Y = (Y - 0.0625) * 1.168949772;
          Cb = (Cb - 0.0625) * 1.142857143 - 0.5;
          Cr = (Cr - 0.0625) * 1.142857143 - 0.5;
          color.r = Y + 1.5748 * Cr;
          color.g = Y - 0.1873 * Cb - 0.4681 * Cr;
          color.b = Y + 1.8556 * Cb;
          color.a = 0.7;
          gl_FragColor = color;
      }
  \"\"\"

  # The exhausitve list of pixel formats that are transferred as float texture
  # Only use those for greater efficiency and compatibility.
  #
  fg_shaders = {
      '2vuy'       :FragmentShader_2vuy,
      '8BitYUV'    :FragmentShader_2vuy,
      'v210'       :FragmentShader_v210,
      '10BitYUV'   :FragmentShader_v210,
      '8BitBGRA'   :FragmentShader_R10l,
      'BGRA'       :FragmentShader_R10l,
      '8BitARGB'   :FragmentShader_R10l,
      '10BitRGBXLE':FragmentShader_R10l,
      'R10l'       :FragmentShader_R10l
      }


  #
  # Helper function to attach a pixel shader to the material that receives the video frame.
  #

  def config_video(obj, format, pixel, is3D=False, mat=0, card=0):
      if pixel not in fg_shaders:
          raise('Unsuported shader')
      shader = obj.meshes[0].materials[mat].getShader()
      if shader is not None and not shader.isValid():
          shader.setSource(VertexShader, fg_shaders[pixel], True)
          shader.setSampler('tex', 0)
          shader.setUniformEyef("eye")
          shader.setUniform1f("stereo", 0.5 if is3D else 1.0)
      tex = vt.Texture(obj, mat)
      tex.source = vt.VideoDeckLink(format + "/" + pixel + ("/3D" if is3D else ""), card)
      print("frame rate: ", tex.source.framerate)
      tex.source.play()
      obj["video"] = tex

  #
  # Attach this function to an object that has a material with texture
  # and call it once to initialize the object
  #
  def init(cont):
      # config_video(cont.owner, 'HD720p5994', '8BitBGRA')
      # config_video(cont.owner, 'HD720p5994', '8BitYUV')
      # config_video(cont.owner, 'pal ', '10BitYUV')
      config_video(cont.owner, 'pal ', '8BitYUV')


  #
  # To be called on every frame
  #
  def play(cont):
      obj = cont.owner
      video = obj.get("video")
      if video is not None:
          video.refresh(True)


Video classes
=============

:class:`VideoFFmpeg`


Image classes
=============

:class:`ImageFFmpeg`

:class:`ImageBuff`

:class:`ImageMirror`

:class:`ImageMix`

:class:`ImageRender`

:class:`ImageViewport`

:class:`VideoDeckLink`


Texture classes
===============

:class:`Texture`

:class:`DeckLink`


Filter classes
==============

:class:`FilterBGR24`

:class:`FilterBlueScreen`

:class:`FilterColor`

:class:`FilterGray`

:class:`FilterLevel`

:class:`FilterNormal`

:class:`FilterRGB24`

:class:`FilterRGBA32`


Functions
=========

:func:`getLastError`

:func:`imageToArray`

:func:`materialID`

:func:`setLogFile`


Constants
=========


FFmpeg Video and Image Status
*****************************

:data:`SOURCE_ERROR`

:data:`SOURCE_EMPTY`

:data:`SOURCE_READY`

:data:`SOURCE_PLAYING`

:data:`SOURCE_STOPPED`


Image Blending Modes
********************

See Wikipedia's `Blend Modes <https://en.wikipedia.org/wiki/Blend_modes>`_ for reference.

:data:`IMB_BLEND_MIX`

:data:`IMB_BLEND_ADD`

:data:`IMB_BLEND_SUB`

:data:`IMB_BLEND_MUL`

:data:`IMB_BLEND_LIGHTEN`

:data:`IMB_BLEND_DARKEN`

:data:`IMB_BLEND_ERASE_ALPHA`

:data:`IMB_BLEND_ADD_ALPHA`

:data:`IMB_BLEND_OVERLAY`

:data:`IMB_BLEND_HARDLIGHT`

:data:`IMB_BLEND_COLORBURN`

:data:`IMB_BLEND_LINEARBURN`

:data:`IMB_BLEND_COLORDODGE`

:data:`IMB_BLEND_SCREEN`

:data:`IMB_BLEND_SOFTLIGHT`

:data:`IMB_BLEND_PINLIGHT`

:data:`IMB_BLEND_VIVIDLIGHT`

:data:`IMB_BLEND_LINEARLIGHT`

:data:`IMB_BLEND_DIFFERENCE`

:data:`IMB_BLEND_EXCLUSION`

:data:`IMB_BLEND_HUE`

:data:`IMB_BLEND_SATURATION`

:data:`IMB_BLEND_LUMINOSITY`

:data:`IMB_BLEND_COLOR`

:data:`IMB_BLEND_COPY`

:data:`IMB_BLEND_COPY_RGB`

:data:`IMB_BLEND_COPY_ALPHA`

"""

import typing

import bpy

import bgl

import bge

class VideoFFmpeg:

  """

  FFmpeg video source, used for video files, video captures, or video streams.

  """

  def __init__(self, file: str, capture: int = -1, rate: float = 25.0, width: int = 0, height: int = 0) -> None:

    """

    :arg file:        
      Path to the video to load; if capture >= 0 on Windows, this parameter will not be used.

    :type file:       
      str

    :arg capture:     
      Capture device number; if >= 0, the corresponding webcam will be used. (optional)

    :type capture:    
      int

    :arg rate:        
      Capture rate. (optional, used only if capture >= 0)

    :type rate:       
      float

    :arg width:       
      Capture width. (optional, used only if capture >= 0)

    :type width:      
      int

    :arg height:      
      Capture height. (optional, used only if capture >= 0)

    :type height:     
      int

    """

    ...

  status: int = ...

  """

  Video status. (readonly)

  """

  range: typing.Sequence[typing.Any] = ...

  """

  The start and stop time of the video playback, expressed in seconds from beginning.
By default the entire video.

  """

  repeat: int = ...

  """

  Number of times to replay the video, -1 for infinite repeat.

  """

  framerate: float = ...

  """

  Relative frame rate, <1.0 for slow, >1.0 for fast.

  """

  valid: bool = ...

  """

  Tells if an image is available. (readonly)

  """

  image: bgl.Buffer = ...

  """

  Image data. (readonly)

  """

  size: typing.Tuple[typing.Any, ...] = ...

  """

  Image size. (readonly)

  """

  scale: bool = ...

  """

  Set to True to activate fast nearest neighbor scaling algorithm.
Texture width and height must be a power of 2.
If the video picture size is not a power of 2, rescaling is required.
By default ``bge.texture`` uses the precise but slow ``gluScaleImage()`` function.
Best is to rescale the video offline so that no scaling is necessary at runtime!

  """

  flip: bool = ...

  """

  If True the imaged will be flipped vertically.
FFmpeg always delivers the image upside down, so this attribute is set to True by default.

  """

  filter: typing.Union[FilterBGR24, FilterBlueScreen, FilterColor, FilterGray, FilterLevel, FilterNormal, FilterRGB24, FilterRGBA32] = ...

  """

  An additional filter that is applied on the video before sending it to the GPU.

  """

  preseek: int = ...

  """

  Number of frames of preseek.

  """

  deinterlace: bool = ...

  """

  Deinterlace image.

  """

  def play(self) -> bool:

    """

    Play (restart) video.

    """

    ...

  def pause(self) -> bool:

    """

    Pause video.

    """

    ...

  def stop(self) -> bool:

    """

    Stop video (play will replay it from start).

    """

    ...

  def refresh(self, buffer: typing.Any = None, format: str = 'RGBA', timestamp: float = -1.0) -> int:

    """

    Refresh video - get its status and optionally copy the frame to an external buffer.

    """

    ...

class ImageFFmpeg:

  """

  FFmpeg image source, used for image files and web based images.

  """

  def __init__(self, file: str) -> None:

    """

    :arg file:        
      Path to the image to load.

    :type file:       
      str

    """

    ...

  status: int = ...

  """

  Image status. (readonly)

  """

  valid: bool = ...

  """

  Tells if an image is available. (readonly)

  """

  image: bgl.Buffer = ...

  """

  Image data. (readonly)

  """

  size: typing.Tuple[typing.Any, ...] = ...

  """

  Image size. (readonly)

  """

  scale: bool = ...

  """

  Fast scale of image (near neighbour).

  """

  flip: bool = ...

  """

  Flip image vertically.

  """

  filter: typing.Union[FilterBGR24, FilterBlueScreen, FilterColor, FilterGray, FilterLevel, FilterNormal, FilterRGB24, FilterRGBA32] = ...

  """

  Pixel filter.

  """

  def refresh(self, buffer: typing.Any = None, format: str = 'RGBA') -> int:

    """

    Refresh image, get its status and optionally copy the frame to an external buffer.

    """

    ...

  def reload(self, newname: str = None) -> None:

    """

    Reload image, i.e. reopen it.

    """

    ...

class ImageBuff:

  """

  Image from application memory.
For computer generated images, drawing applications.

  """

  def __init__(self, width: int, height: int, color: int = 0, scale: bool = False) -> None:

    """

    :arg width:       
      Width of the image.

    :type width:      
      int

    :arg height:      
      Height of the image.

    :type height:     
      int

    :arg color:       
      Value to initialize RGB channels with. The initialized buffer will have
all pixels set to (color, color, color, 255). (optional)

    :type color:      
      int in [0, 255]

    :arg scale:       
      Image uses scaling. (optional)

    :type scale:      
      bool

    """

    ...

  filter: typing.Union[FilterBGR24, FilterBlueScreen, FilterColor, FilterGray, FilterLevel, FilterNormal, FilterRGB24, FilterRGBA32] = ...

  """

  Pixel filter.

  """

  flip: bool = ...

  """

  Flip image vertically.

  """

  image: bgl.Buffer = ...

  """

  Image data. (readonly)

  """

  def load(self, imageBuffer: bgl.Buffer, width: int, height: int) -> None:

    """

    Load image from buffer.

    """

    ...

  def plot(self, imageBuffer: typing.Any, width: int, height: int, positionX: int, positionY: int, mode: int = IMB_BLEND_COPY) -> None:

    """

    Update image buffer.

    """

    ...

  scale: bool = ...

  """

  Fast scale of image (near neighbour).

  """

  size: typing.Tuple[typing.Any, ...] = ...

  """

  Image size. (readonly)

  """

  valid: bool = ...

  """

  Tells if an image is available. (readonly)

  """

class ImageMirror:

  """

  Image source from mirror.

  """

  def __init__(self, scene: bge.types.KX_Scene, observer: bge.types.KX_GameObject, mirror: bge.types.KX_GameObject, material: int = 0, width: int = None, height: int = None, samples: int = 1) -> None:

    """

    :arg scene:       
      Scene in which the image has to be taken.

    :type scene:      
      :class:`~bge.types.KX_Scene`

    :arg observer:    
      Reference object for the mirror
(the object from which the mirror has to be looked at, for example a camera).

    :type observer:   
      :class:`~bge.types.KX_GameObject`

    :arg mirror:      
      Object holding the mirror.

    :type mirror:     
      :class:`~bge.types.KX_GameObject`

    :arg material:    
      ID of the mirror's material to be used for mirroring. (optional)

    :type material:   
      int

    :arg width:       
      Off-screen render buffer width (optional) (unused since 0.3.0).

    :type width:      
      integer

    :arg height:      
      Off-screen render buffer height (optional) (unused since 0.3.0).

    :type height:     
      integer

    :arg samples:     
      Number of times eevee render loop is called to have a fully antialiased pass or soft shadows support (optional).

    :type samples:    
      integer

    """

    ...

  alpha: bool = ...

  """

  Deprecated since version 0.3.0.

  Use alpha in texture.

  """

  horizon: float = ...

  """

  Deprecated since version 0.3.0.

  Horizon color.

  """

  zenith: float = ...

  """

  Deprecated since version 0.3.0.

  Zenith color.

  """

  background: typing.Any = ...

  """

  Deprecated since version 0.3.0.

  """

  updateShadow: bool = ...

  """

  Deprecated since version 0.3.0.

  Choose to force shadow buffer update if there is a gap between image rendered and shadows.

  """

  colorBindCode: int = ...

  """

  Off-screen color texture bind code.

  """

  capsize: typing.Sequence[typing.Any] = ...

  """

  Size of render area.

  """

  clip: float = ...

  """

  Clipping distance.

  """

  filter: typing.Union[FilterBGR24, FilterBlueScreen, FilterColor, FilterGray, FilterLevel, FilterNormal, FilterRGB24, FilterRGBA32] = ...

  """

  Pixel filter.

  """

  flip: bool = ...

  """

  Flip image vertically.

  """

  image: bgl.Buffer = ...

  """

  Image data. (readonly)

  """

  def refresh(self, buffer: typing.Any = None, format: str = 'RGBA') -> None:

    """

    Refresh image - render and copy the image to an external buffer (optional)
then invalidate its current content.

    """

    ...

  scale: bool = ...

  """

  Fast scale of image (near neighbour).

  """

  size: typing.Tuple[typing.Any, ...] = ...

  """

  Image size (readonly).

  """

  valid: bool = ...

  """

  Tells if an image is available. (readonly)

  """

  whole: bool = ...

  """

  Use whole viewport to render.

  """

class ImageMix:

  """

  Image mixer used to mix multiple image sources together.

  """

  filter: typing.Union[FilterBGR24, FilterBlueScreen, FilterColor, FilterGray, FilterLevel, FilterNormal, FilterRGB24, FilterRGBA32] = ...

  """

  Pixel filter.

  """

  flip: bool = ...

  """

  Flip image vertically.

  """

  def getSource(self, id: str) -> typing.Union[VideoFFmpeg, ImageFFmpeg, ImageBuff, ImageMirror, ImageMix, ImageRender, ImageViewport]:

    """

    Get image source.

    """

    ...

  def getWeight(self, id: str) -> int:

    """

    Get image source weight.

    """

    ...

  image: bgl.Buffer = ...

  """

  Image data. (readonly)

  """

  def refresh(self, buffer: typing.Any = None, format: str = 'RGBA') -> None:

    """

    Refresh image - calculate and copy the image to an external buffer (optional)
then invalidate its current content.

    """

    ...

  scale: bool = ...

  """

  Fast scale of image (near neighbour).

  """

  size: typing.Tuple[typing.Any, ...] = ...

  """

  Image size. (readonly)

  """

  def setSource(self, id: str, image: typing.Any) -> None:

    """

    Set image source - all sources must have the same size.

    """

    ...

  def setWeight(self, id: str, weight: int) -> None:

    """

    Set image source weight - the sum of the weights should be 256 to get full color intensity in the output.

    """

    ...

  valid: bool = ...

  """

  Tells if an image is available. (readonly)

  """

class ImageRender:

  """

  Image source from a render of a non active camera.
The render is done on a custom framebuffer object if fbo is specified,
otherwise on the default framebuffer.

  .. code:: python

    import bpy, bge
    from bge import texture

    cont = bge.logic.getCurrentController() # on main camera
    scene = bge.logic.getCurrentScene()
    rendercam = scene.objects["rendercam"]
    renderplane = scene.objects["renderplane"]

    bge.overlayTex = texture.Texture(renderplane, 0, 0)
    bge.overlayTex.source = texture.ImageRender(scene, rendercam)
    bge.overlayTex.source.capsize = [512, 512]

    filter = scene.filterManager.addFilter(0, bge.logic.RAS_2DFILTER_CUSTOMFILTER, cont.actuators["overlay"].shaderText)

    def preDraw():

        depsgraph = bpy.context.evaluated_depsgraph_get()
        scene_eval = bpy.context.scene.evaluated_get(depsgraph)

        # Make background transparent before rendering overlay texture
        scene_eval.render.film_transparent = True

        # Disable not wanted effects before rendering overlay texture
        scene_eval.eevee.bloom_intensity = 0

    def renderOverlay():

        # Append preDraw to bge.overlayTex.source pre-draw callbacks
        bge.overlayTex.source.pre_draw.append(preDraw)

        # Render Overlay Camera to renderplane texture
        bge.overlayTex.refresh(True)

    def sendUniformsTo2DFilters():

        # Render overlay texture
        renderOverlay()

        # send uniforms to 2D filter to do the compositing between main render and overlay
        if filter is not None:
            filter.setTexture(0, bge.overlayTex.bindId, "overlayTex")

  """

  def __init__(self, scene: bge.types.KX_Scene, camera: bge.types.KX_Camera, width: int = None, height: int = None, samples: int = 1) -> None:

    """

    :arg scene:       
      Scene in which the image has to be taken.

    :type scene:      
      :class:`~bge.types.KX_Scene`

    :arg camera:      
      Camera from which the image has to be taken.

    :type camera:     
      :class:`~bge.types.KX_Camera`

    :arg width:       
      Off-screen render buffer width (optional) (unused since 0.3.0).

    :type width:      
      integer

    :arg height:      
      Off-screen render buffer height (optional) (unused since 0.3.0).

    :type height:     
      integer

    :arg samples:     
      Number of times eevee render loop is called to have a fully antialiased pass or soft shadows support (optional).

    :type samples:    
      integer

    """

    ...

  alpha: bool = ...

  """

  Deprecated since version 0.3.0.

  Use alpha in texture.

  """

  horizon: float = ...

  """

  Deprecated since version 0.3.0.

  Horizon color.

  """

  zenith: float = ...

  """

  Deprecated since version 0.3.0.

  Zenith color.

  """

  background: typing.Any = ...

  """

  Deprecated since version 0.3.0.

  Background color.

  """

  updateShadow: bool = ...

  """

  Deprecated since version 0.3.0.

  Choose to force shadow buffer update if there is a gap between image rendered and shadows.

  """

  colorBindCode: int = ...

  """

  Off-screen color texture bind code.

  """

  capsize: typing.Sequence[typing.Any] = ...

  """

  Size of render area.

  """

  filter: typing.Union[FilterBGR24, FilterBlueScreen, FilterColor, FilterGray, FilterLevel, FilterNormal, FilterRGB24, FilterRGBA32] = ...

  """

  Pixel filter.

  """

  flip: bool = ...

  """

  Flip image vertically.

  """

  image: bgl.Buffer = ...

  """

  Image data. (readonly)

  """

  scale: bool = ...

  """

  Fast scale of image (near neighbour).

  """

  size: typing.Tuple[typing.Any, ...] = ...

  """

  Image size. (readonly)

  """

  valid: bool = ...

  """

  Tells if an image is available. (readonly)

  """

  whole: bool = ...

  """

  Use whole viewport to render.

  """

  depth: bool = ...

  """

  Use depth component of render as array of float - not suitable for texture source,
should only be used with bge.texture.imageToArray(mode='F').

  """

  zbuff: bool = ...

  """

  Use depth component of render as grayscale color - suitable for texture source.

  """

  pre_draw: typing.List[typing.Any] = ...

  """

  A list of callables to be run before the render step.
These callbacks can be used to make background transparent
or disable post processing effects of evaluated scene.
Evaluated scene has to be used for performance reasons.

  """

  post_draw: typing.List[typing.Any] = ...

  """

  A list of callables to be run after the render step.

  """

  def render(self) -> bool:

    """

    Render the scene but do not extract the pixels yet.
The function returns as soon as the render commands have been send to the GPU.
The render will proceed asynchronously in the GPU while the host can perform other tasks.
To complete the render, you can either call :func:`refresh`
directly of refresh the texture of which this object is the source.
This method is useful to implement asynchronous render for optimal performance: call render()
on frame n and refresh() on frame n+1 to give as much as time as possible to the GPU
to render the frame while the game engine can perform other tasks.

    """

    ...

  def refresh(self) -> None:

    ...

  def refresh(self, buffer: typing.Any, format: str = 'RGBA') -> bool:

    """

    Refresh video - render and optionally copy the image to an external buffer then invalidate its current content.
The render may have been started earlier with the :func:`render` method,
in which case this function simply waits for the render operations to complete.
When called without argument, the pixels are not extracted but the render is guaranteed
to be completed when the function returns.
This only makes sense with offscreen render on texture target (see :func:`~bge.render.offScreenCreate`).

    """

    ...

class ImageViewport:

  """

  Image source from viewport rendered by the active camera.
To render from a non active camera see :class:`~bge.texture.ImageRender`.

  """

  alpha: bool = ...

  """

  Deprecated since version 0.3.0.

  Use alpha in texture.

  """

  capsize: typing.Sequence[typing.Any] = ...

  """

  Size of viewport area being captured.

  """

  filter: typing.Union[FilterBGR24, FilterBlueScreen, FilterColor, FilterGray, FilterLevel, FilterNormal, FilterRGB24, FilterRGBA32] = ...

  """

  Pixel filter.

  """

  flip: bool = ...

  """

  Flip image vertically.

  """

  image: bgl.Buffer = ...

  """

  Image data. (readonly)

  """

  position: typing.Sequence[typing.Any] = ...

  """

  Upper left corner of the captured area.

  """

  def refresh(self, buffer: typing.Any = None, format: str = 'RGBA') -> None:

    """

    Refresh video - copy the viewport to an external buffer (optional) then invalidate its current content.

    """

    ...

  scale: bool = ...

  """

  Fast scale of image (near neighbour).

  """

  size: typing.Tuple[typing.Any, ...] = ...

  """

  Image size. (readonly)

  """

  valid: bool = ...

  """

  Tells if an image is available. (readonly)

  """

  whole: bool = ...

  """

  Use whole viewport to capture.

  """

  depth: bool = ...

  """

  Use depth component of viewport as array of float - not suitable for texture source,
should only be used with ``bge.texture.imageToArray(mode='F')``.

  """

  zbuff: bool = ...

  """

  Use depth component of viewport as grayscale color - suitable for texture source.

  """

class VideoDeckLink:

  """

  Image source from an external video stream captured with a DeckLink video card from
Black Magic Design.
Before this source can be used, a DeckLink hardware device must be installed, it can be a PCIe card
or a USB device, and the 'Desktop Video' software package (version 10.4 or above must be installed)
on the host as described in the DeckLink documentation.
If in addition you have a recent nVideo Quadro card, you can benefit from the 'GPUDirect' technology
to push the captured video frame very efficiently to the GPU. For this you need to install the
'DeckLink SDK' version 10.4 or above and copy the 'dvp.dll' runtime library to Blender's
installation directory or to any other place where Blender can load a DLL from.

  The format argument must be written as ``<displayMode>/<pixelFormat>[/3D][:<cacheSize>]``
where ``<displayMode>`` describes the frame size and rate and <pixelFormat> the encoding of the pixels.
The optional ``/3D`` suffix is to be used if the video stream is stereo with a left and right eye feed.
The optional ``:<cacheSize>`` suffix determines the number of the video frames kept in cache, by default 8.
Some DeckLink cards won't work below a certain cache size. The default value 8 should be sufficient for all cards.
You may try to reduce the cache size to reduce the memory footprint. For example the The 4K Extreme is known
to work with 3 frames only, the Extreme 2 needs 4 frames and the Intensity Shuttle needs 6 frames, etc.
Reducing the cache size may be useful when Decklink is used in conjunction with GPUDirect:
all frames must be locked in memory in that case and that puts a lot of pressure on memory.
If you reduce the cache size too much, you'll get no error but no video feed either.

  The valid ``<displayMode>`` values are copied from the ``BMDDisplayMode`` enum in the DeckLink API
without the 'bmdMode' prefix. In case a mode that is not in this list is added in a later version
of the SDK, it is also possible to specify the 4 letters of the internal code for that mode.
You will find the internal code in the ``DeckLinkAPIModes.h`` file that is part of the SDK.
Here is for reference the full list of supported display modes with their equivalent internal code:

  Internal Codes
    * NTSC 'ntsc'

    * NTSC2398        'nt23'

    * PAL             'pal '

    * NTSCp           'ntsp'

    * PALp            'palp'

  HD 1080 Modes
    * HD1080p2398     '23ps'

    * HD1080p24       '24ps'

    * HD1080p25       'Hp25'

    * HD1080p2997     'Hp29'

    * HD1080p30       'Hp30'

    * HD1080i50       'Hi50'

    * HD1080i5994     'Hi59'

    * HD1080i6000     'Hi60'

    * HD1080p50       'Hp50'

    * HD1080p5994     'Hp59'

    * HD1080p6000     'Hp60'

  HD 720 Modes
    * HD720p50        'hp50'

    * HD720p5994      'hp59'

    * HD720p60        'hp60'

  2k Modes
    * 2k2398  '2k23'

    * 2k24            '2k24'

    * 2k25            '2k25'

  4k Modes
    * 4K2160p2398     '4k23'

    * 4K2160p24       '4k24'

    * 4K2160p25       '4k25'

    * 4K2160p2997     '4k29'

    * 4K2160p30       '4k30'

    * 4K2160p50       '4k50'

    * 4K2160p5994     '4k59'

    * 4K2160p60       '4k60'

  Most of names are self explanatory. If necessary refer to the DeckLink API documentation for more information.

  Similarly, <pixelFormat> is copied from the BMDPixelFormat enum.

  Here is for reference the full list of supported pixel format and their equivalent internal code:

  Pixel Formats
    * 8BitYUV '2vuy'

    * 10BitYUV        'v210'

    * 8BitARGB        * no equivalent code *

    * 8BitBGRA        'BGRA'

    * 10BitRGB        'r210'

    * 12BitRGB        'R12B'

    * 12BitRGBLE      'R12L'

    * 10BitRGBXLE     'R10l'

    * 10BitRGBX       'R10b'

  Refer to the DeckLink SDK documentation for a full description of these pixel format.
It is important to understand them as the decoding of the pixels is NOT done in VideoTexture
for performance reason. Instead a specific shader must be used to decode the pixel in the GPU.
Only the '8BitARGB', '8BitBGRA' and '10BitRGBXLE' pixel formats are mapped directly to OpenGL RGB float textures.
The '8BitYUV' and '10BitYUV' pixel formats are mapped to openGL RGB float texture but require a shader to decode.
The other pixel formats are sent as a ``GL_RED_INTEGER`` texture (i.e. a texture with only the
red channel coded as an unsigned 32 bit integer) and are not recommended for use.

  Example: ``HD1080p24/10BitYUV/3D:4`` is equivalent to ``24ps/v210/3D:4``
and represents a full HD stereo feed at 24 frame per second and 4 frames cache size.

  Although video format auto detection is possible with certain DeckLink devices, the corresponding
API is NOT implemented in the BGE. Therefore it is important to specify the format string that
matches exactly the video feed. If the format is wrong, no frame will be captured.
It should be noted that the pixel format that you need to specify is not necessarily the actual
format in the video feed. For example, the 4K Extreme card delivers 8bit RGBs pixels in the
'10BitRGBXLE' format. Use the 'Media Express' application included in 'Desktop Video' to discover
which pixel format works for a particular video stream.

  """

  def __init__(self, format: str, capture: int = 0) -> None:

    """

    :arg format:      
      string describing the video format to be captured.

    :type format:     
      str

    :arg capture:     
      Card number from which the input video must be captured.

    :type capture:    
      int

    """

    ...

  status: int = ...

  """

  Status of the capture: 1=ready to use, 2=capturing, 3=stopped

  """

  framerate: float = ...

  """

  Capture frame rate as computed from the video format.

  """

  valid: bool = ...

  """

  Tells if the image attribute can be used to retrieve the image.
Always False in this implementation (the image is not available at python level)

  """

  image: bgl.Buffer = ...

  """

  The image data. Always None in this implementation.

  """

  size: typing.Any = ...

  """

  The size of the frame in pixel.
Stereo frames have double the height of the video frame, i.e. 3D is delivered to the GPU
as a single image in top-bottom order, left eye on top.

  """

  scale: bool = ...

  """

  Not used in this object.

  """

  flip: bool = ...

  """

  Not used in this object.

  """

  filter: typing.Any = ...

  """

  Not used in this object.

  """

  def play(self) -> bool:

    """

    Kick-off the capture after creation of the object.

    """

    ...

  def pause(self) -> bool:

    """

    Temporary stops the capture. Use play() to restart it.

    """

    ...

  def stop(self) -> bool:

    """

    Stops the capture.

    """

    ...

class Texture:

  """

  Class that creates the ``Texture`` object that loads the dynamic texture on the GPU.

  """

  def __init__(self, gameObj: bge.types.KX_GameObject, materialID: int = 0, textureID: int = 0, textureObj: Texture = None) -> None:

    """

    :arg gameObj:     
      Game object to be created a video texture on.

    :type gameObj:    
      :class:`~bge.types.KX_GameObject`

    :arg materialID:  
      Material ID default, 0 is the first material. (optional)

    :type materialID: 
      int

    :arg textureID:   
      Texture index in case of multi-texture channel, 0 = first channel by default.
In case of UV texture, this parameter should always be 0. (optional)

    :type textureID:  
      int

    :arg textureObj:  
      Reference to another ``Texture`` object with shared bindId
which he user might want to reuse the texture.
If this argument is used, you should not create any source on this texture
and there is no need to refresh it either: the other ``Texture`` object will
provide the texture for both materials/textures.(optional)

    :type textureObj: 
      :class:`~bge.texture.Texture`

    """

    ...

  gpuTexture: bpy.types.GPUTexture = ...

  """

  GPUTexture. (readonly)

  """

  def close(self) -> None:

    """

    Close dynamic texture and restore original.

    """

    ...

  mipmap: bool = ...

  """

  Mipmap texture.

  """

  def refresh(self, refresh_source: bool, timestamp: float = -1.0) -> None:

    """

    Refresh texture from source.

    """

    ...

  source: typing.Union[VideoFFmpeg, VideoDeckLink, ImageFFmpeg, ImageBuff, ImageMirror, ImageMix, ImageRender, ImageViewport] = ...

  """

  Source of texture.

  """

class DeckLink:

  """

  Certain DeckLink devices can be used to playback video: the host sends video frames regularly
for immediate or scheduled playback. The video feed is outputted on HDMI or SDI interfaces.
This class supports the immediate playback mode: it has a source attribute that is assigned
one of the source object in the bge.texture module. Refreshing the DeckLink object causes
the image source to be computed and sent to the DeckLink device for immediate transmission
on the output interfaces.  Keying is supported: it allows to composite the frame with an
input video feed that transits through the DeckLink card.

  The default value of the format argument is reserved for auto detection but it is currently
not supported (it will generate a runtime error) and thus the video format must be explicitly
specified. If keying is the goal (see keying attributes), the format must match exactly the
input video feed, otherwise it can be any format supported by the device (there will be a
runtime error if not).
The format of the string is ``<displayMode>[/3D]``.

  Refer to :class:`~bge.texture.VideoDeckLink` to get the list of acceptable ``<displayMode>``.
The optional ``/3D`` suffix is used to create a stereo 3D feed.
In that case the 'right' attribute must also be set to specify the image source for the right eye.

  Note: The pixel format is not specified here because it is always BGRA. The alpha channel is
used in keying to mix the source with the input video feed, otherwise it is not used.
If a conversion is needed to match the native video format, it is done inside the DeckLink driver
or device.

  """

  def __init__(self, cardIdx: int = 0, format: str = '') -> None:

    """

    :arg cardIdx:     
      Number of the card to be used for output (0=first card).
It should be noted that DeckLink devices are usually half duplex:
they can either be used for capture or playback but not both at the same time.

    :type cardIdx:    
      int

    :arg format:      
      String representing the display mode of the output feed.

    :type format:     
      str

    """

    ...

  source: typing.Union[VideoFFmpeg, VideoDeckLink, ImageFFmpeg, ImageBuff, ImageMirror, ImageMix, ImageRender, ImageViewport] = ...

  """

  This attribute must be set to one of the image sources. If the image size does not fit exactly
the frame size, the extend attribute determines what to do.

  For best performance, the source image should match exactly the size of the output frame.
A further optimization is achieved if the image source object is ImageViewport or ImageRender
set for whole viewport, flip disabled and no filter: the GL frame buffer is copied directly
to the image buffer and directly from there to the DeckLink card (hence no buffer to buffer
copy inside VideoTexture).

  """

  right: typing.Union[VideoFFmpeg, VideoDeckLink, ImageFFmpeg, ImageBuff, ImageMirror, ImageMix, ImageRender, ImageViewport] = ...

  """

  If the video format is stereo 3D, this attribute should be set to an image source object
that will produce the right eye images.  If the goal is to render the BGE scene in 3D,
it can be achieved with 2 cameras, one for each eye, used by 2 ImageRender with an offscreen
render buffer that is just the size of the video frame.

  """

  keying: bool = ...

  """

  Specify if keying is enabled. False (default): the output frame is sent unmodified on
the output interface (in that case no input video is required). True: the output frame
is mixed with the input video, using the alpha channel to blend the two images and the
combination is sent on the output interface.

  """

  level: int = ...

  """

  If keying is enabled, sets the keying level from 0 to 255. This value is a global alpha value
that multiplies the alpha channel of the image source. Use 255 (the default) to keep the alpha
channel unmodified, 0 to make the output frame totally transparent.

  """

  extend: bool = ...

  """

  Determines how the image source should be mapped if the size does not fit the video frame size.
* False (the default): map the image pixel by pixel.
If the image size is smaller than the frame size, extra space around the image is filled with
0-alpha black. If it is larger, the image is cropped to fit the frame size.
* True: the image is scaled by the nearest neighbor algorithm to fit the frame size.
The scaling is fast but poor quality. For best results, always adjust the image source to
match the size of the output video.

  """

  def close(self) -> None:

    """

    Close the DeckLink device and release all resources. After calling this method,
the object cannot be reactivated, it must be destroyed and a new DeckLink object
created from fresh to restart the output.

    """

    ...

  def refresh(self, refresh_source: bool, ts: float) -> None:

    """

    This method must be called frequently to update the output frame in the DeckLink device.

    """

    ...

class FilterBGR24:

  """

  Source filter BGR24.

  """

  ...

class FilterBlueScreen:

  """

  Filter for Blue Screen.
The RGB channels of the color are left unchanged, while the output alpha is obtained as follows:

  * if the square of the euclidean distance between the RGB color
and the filter's reference color is smaller than the filter's lower limit,
the output alpha is set to 0;

  * if that square is bigger than the filter's upper limit, the output alpha is set to 255;

  * otherwise the output alpha is linearly extrapolated between 0 and 255 in the interval of the limits.

  """

  color: typing.Sequence[typing.Any] = ...

  """

  Reference color.

  """

  limits: typing.Sequence[typing.Any] = ...

  """

  Reference color limits.

  """

  previous: typing.Union[FilterBGR24, FilterBlueScreen, FilterColor, FilterGray, FilterLevel, FilterNormal, FilterRGB24, FilterRGBA32] = ...

  """

  Previous pixel filter.

  """

class FilterColor:

  """

  Filter for color calculations.
The output color is obtained by multiplying the reduced 4x4 matrix with the input color
and adding the remaining column to the result.

  """

  matrix: typing.Sequence[typing.Any] = ...

  """

  Matrix [4][5] for color calculation.

  """

  previous: typing.Union[FilterBGR24, FilterBlueScreen, FilterColor, FilterGray, FilterLevel, FilterNormal, FilterRGB24, FilterRGBA32] = ...

  """

  Previous pixel filter.

  """

class FilterGray:

  """

  Filter for grayscale effect.
Proportions of R, G and B contributions in the output grayscale are 28:151:77.

  """

  previous: typing.Union[FilterBGR24, FilterBlueScreen, FilterColor, FilterGray, FilterLevel, FilterNormal, FilterRGB24, FilterRGBA32] = ...

  """

  Previous pixel filter.

  """

class FilterLevel:

  """

  Filter for levels calculations. Each output color component is obtained as follows:

  * if it is smaller than its corresponding min value, it is set to 0;

  * if it is bigger than its corresponding max value, it is set to 255;

  * Otherwise it is linearly extrapolated between 0 and 255 in the (min, max) interval.

  """

  levels: typing.Sequence[typing.Any] = ...

  """

  Levels matrix [4] (min, max).

  """

  previous: typing.Union[FilterBGR24, FilterBlueScreen, FilterColor, FilterGray, FilterLevel, FilterNormal, FilterRGB24, FilterRGBA32] = ...

  """

  Previous pixel filter.

  """

class FilterNormal:

  """

  Normal map filter.

  """

  colorIdx: int = ...

  """

  Index of color used to calculate normal (0 - red, 1 - green, 2 - blue, 3 - alpha).

  """

  depth: float = ...

  """

  Depth of relief.

  """

  previous: typing.Union[FilterBGR24, FilterBlueScreen, FilterColor, FilterGray, FilterLevel, FilterNormal, FilterRGB24, FilterRGBA32] = ...

  """

  Previous pixel filter.

  """

class FilterRGB24:

  """

  Returns a new input filter object to be used with :class:`~bge.texture.ImageBuff` object when the image passed
to the :meth:`~bge.texture.ImageBuff.load` function has the 3-bytes pixel format BGR.

  """

  ...

class FilterRGBA32:

  """

  Source filter RGBA32.

  """

  ...

def getLastError() -> str:

  """

  Last error that occurred in a bge.texture function.

  """

  ...

def imageToArray(image: typing.Any, mode: str) -> bgl.Buffer:

  """

  Returns a :class:`~bgl.Buffer` corresponding to the current image stored in a texture source object.

  """

  ...

def materialID(object: bge.types.KX_GameObject, name: str) -> int:

  """

  Returns a numeric value that can be used in :class:`~bge.texture.Texture` to create a dynamic texture.

  The value corresponds to an internal material number that uses the texture identified
by name. name is a string representing a texture name with ``IM`` prefix if you want to
identify the texture directly. This method works for basic tex face and for material,
provided the material has a texture channel using that particular texture in first
position of the texture stack. name can also have ``MA`` prefix if you want to identify
the texture by material. In that case the material must have a texture channel in first
position.

  If the object has no material that matches name, it generates a runtime error.
Use try/except to catch the exception.

  Ex: ``bge.texture.materialID(obj, 'IMvideo.png')``

  """

  ...

def setLogFile(filename: str) -> int:

  """

  Sets the name of a text file in which runtime error messages will be written,
in addition to the printing of the messages on the Python console.
Only the runtime errors specific to the VideoTexture module are written in that file,
ordinary runtime time errors are not written.

  """

  ...

SOURCE_ERROR: typing.Any = ...

SOURCE_EMPTY: typing.Any = ...

SOURCE_READY: typing.Any = ...

SOURCE_PLAYING: typing.Any = ...

SOURCE_STOPPED: typing.Any = ...

IMB_BLEND_MIX: typing.Any = ...

IMB_BLEND_ADD: typing.Any = ...

IMB_BLEND_SUB: typing.Any = ...

IMB_BLEND_MUL: typing.Any = ...

IMB_BLEND_LIGHTEN: typing.Any = ...

IMB_BLEND_DARKEN: typing.Any = ...

IMB_BLEND_ERASE_ALPHA: typing.Any = ...

IMB_BLEND_ADD_ALPHA: typing.Any = ...

IMB_BLEND_OVERLAY: typing.Any = ...

IMB_BLEND_HARDLIGHT: typing.Any = ...

IMB_BLEND_COLORBURN: typing.Any = ...

IMB_BLEND_LINEARBURN: typing.Any = ...

IMB_BLEND_COLORDODGE: typing.Any = ...

IMB_BLEND_SCREEN: typing.Any = ...

IMB_BLEND_SOFTLIGHT: typing.Any = ...

IMB_BLEND_PINLIGHT: typing.Any = ...

IMB_BLEND_VIVIDLIGHT: typing.Any = ...

IMB_BLEND_LINEARLIGHT: typing.Any = ...

IMB_BLEND_DIFFERENCE: typing.Any = ...

IMB_BLEND_EXCLUSION: typing.Any = ...

IMB_BLEND_HUE: typing.Any = ...

IMB_BLEND_SATURATION: typing.Any = ...

IMB_BLEND_LUMINOSITY: typing.Any = ...

IMB_BLEND_COLOR: typing.Any = ...

IMB_BLEND_COPY: typing.Any = ...

IMB_BLEND_COPY_RGB: typing.Any = ...

IMB_BLEND_COPY_ALPHA: typing.Any = ...
