"""


Gpencil Operators
*****************

:func:`annotate`

:func:`annotation_active_frame_delete`

:func:`annotation_add`

:func:`data_unlink`

:func:`layer_annotation_add`

:func:`layer_annotation_move`

:func:`layer_annotation_remove`

:func:`tint_flip`

"""

import typing

def annotate(*args, mode: str = 'DRAW', arrowstyle_start: str = 'NONE', arrowstyle_end: str = 'NONE', use_stabilizer: bool = False, stabilizer_factor: float = 0.75, stabilizer_radius: int = 35, stroke: typing.Union[typing.Sequence[OperatorStrokeElement], typing.Mapping[str, OperatorStrokeElement], bpy.types.bpy_prop_collection] = None, wait_for_input: bool = True) -> None:

  """

  Make annotations on the active data

  """

  ...

def annotation_active_frame_delete() -> None:

  """

  Delete the active frame for the active Annotation Layer

  """

  ...

def annotation_add() -> None:

  """

  Add new Annotation data-block

  """

  ...

def data_unlink() -> None:

  """

  Unlink active Annotation data-block

  """

  ...

def layer_annotation_add() -> None:

  """

  Add new Annotation layer or note for the active data-block

  """

  ...

def layer_annotation_move(*args, type: str = 'UP') -> None:

  """

  Move the active Annotation layer up/down in the list

  """

  ...

def layer_annotation_remove() -> None:

  """

  Remove active Annotation layer

  """

  ...

def tint_flip() -> None:

  """

  Switch tint colors

  """

  ...
