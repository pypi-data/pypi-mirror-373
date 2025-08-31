"""


GPU Capabilities Utilities (gpu.capabilities)
*********************************************

This module provides access to the GPU capabilities.

:func:`compute_shader_support_get`

:func:`extensions_get`

:func:`hdr_support_get`

:func:`max_batch_indices_get`

:func:`max_batch_vertices_get`

:func:`max_images_get`

:func:`max_texture_layers_get`

:func:`max_texture_size_get`

:func:`max_textures_frag_get`

:func:`max_textures_geom_get`

:func:`max_textures_get`

:func:`max_textures_vert_get`

:func:`max_uniforms_frag_get`

:func:`max_uniforms_vert_get`

:func:`max_varying_floats_get`

:func:`max_vertex_attribs_get`

:func:`max_work_group_count_get`

:func:`max_work_group_size_get`

:func:`shader_image_load_store_support_get`

"""

import typing

def compute_shader_support_get() -> bool:

  """

  Are compute shaders supported.

  """

  ...

def extensions_get() -> typing.Any:

  """

  Get supported extensions in the current context.

  """

  ...

def hdr_support_get() -> bool:

  """

  Return whether GPU backend supports High Dynamic range for viewport.

  """

  ...

def max_batch_indices_get() -> int:

  """

  Get maximum number of vertex array indices.

  """

  ...

def max_batch_vertices_get() -> int:

  """

  Get maximum number of vertex array vertices.

  """

  ...

def max_images_get() -> int:

  """

  Get maximum supported number of image units.

  """

  ...

def max_texture_layers_get() -> int:

  """

  Get maximum number of layers in texture.

  """

  ...

def max_texture_size_get() -> int:

  """

  Get estimated maximum texture size to be able to handle.

  """

  ...

def max_textures_frag_get() -> int:

  """

  Get maximum supported texture image units used for
accessing texture maps from the fragment shader.

  """

  ...

def max_textures_geom_get() -> int:

  """

  Get maximum supported texture image units used for
accessing texture maps from the geometry shader.

  """

  ...

def max_textures_get() -> int:

  """

  Get maximum supported texture image units used for
accessing texture maps from the vertex shader and the
fragment processor.

  """

  ...

def max_textures_vert_get() -> int:

  """

  Get maximum supported texture image units used for
accessing texture maps from the vertex shader.

  """

  ...

def max_uniforms_frag_get() -> int:

  """

  Get maximum number of values held in uniform variable
storage for a fragment shader.

  """

  ...

def max_uniforms_vert_get() -> int:

  """

  Get maximum number of values held in uniform variable
storage for a vertex shader.

  """

  ...

def max_varying_floats_get() -> int:

  """

  Get maximum number of varying variables used by
vertex and fragment shaders.

  """

  ...

def max_vertex_attribs_get() -> int:

  """

  Get maximum number of vertex attributes accessible to
a vertex shader.

  """

  ...

def max_work_group_count_get(index: int) -> int:

  """

  Get maximum number of work groups that may be dispatched to a compute shader.

  """

  ...

def max_work_group_size_get(index: int) -> int:

  """

  Get maximum size of a work group that may be dispatched to a compute shader.

  """

  ...

def shader_image_load_store_support_get() -> bool:

  """

  Is image load/store supported.

  """

  ...
