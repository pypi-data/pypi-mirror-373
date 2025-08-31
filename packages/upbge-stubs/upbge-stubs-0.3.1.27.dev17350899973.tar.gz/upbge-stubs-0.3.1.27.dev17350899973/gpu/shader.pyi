"""


GPU Shader Utilities (gpu.shader)
*********************************

This module provides access to GPUShader internal functions.

.. _built-in-shaders:

-[ Built-in shaders ]-

All built-in shaders have the ``mat4 ModelViewProjectionMatrix`` uniform.

Its value must be modified using the :class:`gpu.matrix` module.

``FLAT_COLOR``
  :Attributes:      
    vec3 pos, vec4 color

  :Uniforms:        
    none

``IMAGE``
  :Attributes:      
    vec3 pos, vec2 texCoord

  :Uniforms:        
    sampler2D image

``IMAGE_COLOR``
  :Attributes:      
    vec3 pos, vec2 texCoord

  :Uniforms:        
    sampler2D image, vec4 color

``SMOOTH_COLOR``
  :Attributes:      
    vec3 pos, vec4 color

  :Uniforms:        
    none

``UNIFORM_COLOR``
  :Attributes:      
    vec3 pos

  :Uniforms:        
    vec4 color

``POLYLINE_FLAT_COLOR``
  :Attributes:      
    vec3 pos, vec4 color

  :Uniforms:        
    vec2 viewportSize, float lineWidth

``POLYLINE_SMOOTH_COLOR``
  :Attributes:      
    vec3 pos, vec4 color

  :Uniforms:        
    vec2 viewportSize, float lineWidth

``POLYLINE_UNIFORM_COLOR``
  :Attributes:      
    vec3 pos

  :Uniforms:        
    vec2 viewportSize, float lineWidth, vec4 color

``POINT_FLAT_COLOR``
  :Attributes:      
    vec3 pos, vec4 color

  :Uniforms:        
    float size

``POINT_UNIFORM_COLOR``
  :Attributes:      
    vec3 pos

  :Uniforms:        
    vec4 color, float size

:func:`create_from_info`

:func:`from_builtin`

:func:`unbind`

"""

import typing

import gpu

def create_from_info(shader_info: gpu.types.GPUShaderCreateInfo) -> gpu.types.GPUShader:

  """

  Create shader from a GPUShaderCreateInfo.

  """

  ...

def from_builtin(shader_name: str, *args, config: str = 'DEFAULT') -> gpu.types.GPUShader:

  """

  Shaders that are embedded in the blender internal code (see ::`built-in-shaders`).
They all read the uniform ``mat4 ModelViewProjectionMatrix``,
which can be edited by the :mod:`gpu.matrix` module.

  You can also choose a shader configuration that uses clip_planes by setting the ``CLIPPED`` value to the config parameter. Note that in this case you also need to manually set the value of ``mat4 ModelMatrix``.

  """

  ...

def unbind() -> None:

  """

  Unbind the bound shader object.

  """

  ...
