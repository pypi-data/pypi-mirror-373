"""


Math Types & Utilities (mathutils)
**********************************

This module provides access to math operations.

Note: Classes, methods and attributes that accept vectors also accept other numeric sequences,
such as tuples, lists.

The :mod:`mathutils` module provides the following classes:

* :class:`Color`,

* :class:`Euler`,

* :class:`Matrix`,

* :class:`Quaternion`,

* :class:`Vector`,

.. code::

  import mathutils
  from math import radians

  vec = mathutils.Vector((1.0, 2.0, 3.0))

  mat_rot = mathutils.Matrix.Rotation(radians(90.0), 4, 'X')
  mat_trans = mathutils.Matrix.Translation(vec)

  mat = mat_trans @ mat_rot
  mat.invert()

  mat3 = mat.to_3x3()
  quat1 = mat.to_quaternion()
  quat2 = mat3.to_quaternion()

  quat_diff = quat1.rotation_difference(quat2)

  print(quat_diff.angle)

:class:`Color`

:class:`Euler`

:class:`Matrix`

:class:`Quaternion`

:class:`Vector`

"""

from . import noise

from . import kdtree

from . import interpolate

from . import geometry

from . import bvhtree

import typing

class Color:

  """

  This object gives access to Colors in Blender.

  Most colors returned by Blender APIs are in scene linear color space, as defined by    the OpenColorIO configuration. The notable exception is user interface theming colors,    which are in sRGB color space.

  .. code::

    import mathutils

    # Color values are represented as RGB values from 0 - 1, this is blue.
    col = mathutils.Color((0.0, 0.0, 1.0))

    # As well as r/g/b attribute access you can adjust them by h/s/v.
    col.s *= 0.5

    # You can access its components by attribute or index.
    print("Color R:", col.r)
    print("Color G:", col[1])
    print("Color B:", col[-1])
    print("Color HSV: {:.2f}, {:.2f}, {:.2f}".format(*col))


    # Components of an existing color can be set.
    col[:] = 0.0, 0.5, 1.0

    # Components of an existing color can use slice notation to get a tuple.
    print("Values: {:f}, {:f}, {:f}".format(*col))

    # Colors can be added and subtracted.
    col += mathutils.Color((0.25, 0.0, 0.0))

    # Color can be multiplied, in this example color is scaled to 0-255
    # can printed as integers.
    print("Color: {:d}, {:d}, {:d}".format(*(int(c) for c in (col * 255.0))))

    # This example prints the color as hexadecimal.
    print("Hexadecimal: {:02x}{:02x}{:02x}".format(int(col.r * 255), int(col.g * 255), int(col.b * 255)))

    # Direct buffer access is supported.
    print(memoryview(col).tobytes())

  """

  def __init__(self) -> None:

    """

    :arg rgb:         
      (red, green, blue) color values where (0, 0, 0) is black & (1, 1, 1) is white.

    :type rgb:        
      Sequence[float]

    """

    ...

  def copy(self) -> Color:

    """

    Returns a copy of this color.

    Note: use this to get a copy of a wrapped color with
no reference to the original data.

    """

    ...

  def freeze(self) -> None:

    """

    Make this object immutable.

    After this the object can be hashed, used in dictionaries & sets.

    """

    ...

  def from_aces_to_scene_linear(self) -> Color:

    """

    Convert from ACES2065-1 linear to scene linear color space.

    """

    ...

  def from_rec709_linear_to_scene_linear(self) -> Color:

    """

    Convert from Rec.709 linear color space to scene linear color space.

    """

    ...

  def from_scene_linear_to_aces(self) -> Color:

    """

    Convert from scene linear to ACES2065-1 linear color space.

    """

    ...

  def from_scene_linear_to_rec709_linear(self) -> Color:

    """

    Convert from scene linear to Rec.709 linear color space.

    """

    ...

  def from_scene_linear_to_srgb(self) -> Color:

    """

    Convert from scene linear to sRGB color space.

    """

    ...

  def from_scene_linear_to_xyz_d65(self) -> Color:

    """

    Convert from scene linear to CIE XYZ (Illuminant D65) color space.

    """

    ...

  def from_srgb_to_scene_linear(self) -> Color:

    """

    Convert from sRGB to scene linear color space.

    """

    ...

  def from_xyz_d65_to_scene_linear(self) -> Color:

    """

    Convert from CIE XYZ (Illuminant D65) to scene linear color space.

    """

    ...

  b: float = ...

  """

  Blue color channel.

  """

  g: float = ...

  """

  Green color channel.

  """

  h: float = ...

  """

  HSV Hue component in [0, 1].

  """

  hsv: typing.Any = ...

  """

  HSV Values in [0, 1].

  """

  is_frozen: bool = ...

  """

  True when this object has been frozen (read-only).

  """

  is_valid: bool = ...

  """

  True when the owner of this data is valid.

  """

  is_wrapped: bool = ...

  """

  True when this object wraps external data (read-only).

  """

  owner: typing.Any = ...

  """

  The item this is wrapping or None  (read-only).

  """

  r: float = ...

  """

  Red color channel.

  """

  s: float = ...

  """

  HSV Saturation component in [0, 1].

  """

  v: float = ...

  """

  HSV Value component in [0, 1].

  """

class Euler:

  """

  This object gives access to Eulers in Blender.

  `Euler angles <https://en.wikipedia.org/wiki/Euler_angles>`_ on Wikipedia.

  .. code::

    import mathutils
    import math

    # Create a new euler with default axis rotation order.
    eul = mathutils.Euler((0.0, math.radians(45.0), 0.0), 'XYZ')

    # Rotate the euler.
    eul.rotate_axis('Z', math.radians(10.0))

    # You can access its components by attribute or index.
    print("Euler X", eul.x)
    print("Euler Y", eul[1])
    print("Euler Z", eul[-1])

    # Components of an existing euler can be set.
    eul[:] = 1.0, 2.0, 3.0

    # Components of an existing euler can use slice notation to get a tuple.
    print("Values: {:f}, {:f}, {:f}".format(*eul))

    # The order can be set at any time too.
    eul.order = 'ZYX'

    # Eulers can be used to rotate vectors.
    vec = mathutils.Vector((0.0, 0.0, 1.0))
    vec.rotate(eul)

    # Often its useful to convert the euler into a matrix so it can be used as
    # transformations with more flexibility.
    mat_rot = eul.to_matrix()
    mat_loc = mathutils.Matrix.Translation((2.0, 3.0, 4.0))
    mat = mat_loc @ mat_rot.to_4x4()

    # Direct buffer access is supported.
    print(memoryview(eul).tobytes())

  """

  def __init__(self) -> None:

    """

    :arg angles:      
      (X, Y, Z) angles in radians.

    :type angles:     
      Sequence[float]

    :arg order:       
      Euler rotation order.

    :type order:      
      Literal['XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX']

    """

    ...

  def copy(self) -> Euler:

    """

    Returns a copy of this euler.

    Note: use this to get a copy of a wrapped euler with
no reference to the original data.

    """

    ...

  def freeze(self) -> None:

    """

    Make this object immutable.

    After this the object can be hashed, used in dictionaries & sets.

    """

    ...

  def make_compatible(self) -> None:

    """

    Make this euler compatible with another,
so interpolating between them works as intended.

    Note: the rotation order is not taken into account for this function.

    """

    ...

  def rotate(self) -> None:

    """

    Rotates the euler by another mathutils value.

    """

    ...

  def rotate_axis(self) -> None:

    """

    Rotates the euler a certain amount and returning a unique euler rotation
(no 720 degree pitches).

    """

    ...

  def to_matrix(self) -> Matrix:

    """

    Return a matrix representation of the euler.

    """

    ...

  def to_quaternion(self) -> Quaternion:

    """

    Return a quaternion representation of the euler.

    """

    ...

  def zero(self) -> None:

    """

    Set all values to zero.

    """

    ...

  is_frozen: bool = ...

  """

  True when this object has been frozen (read-only).

  """

  is_valid: bool = ...

  """

  True when the owner of this data is valid.

  """

  is_wrapped: bool = ...

  """

  True when this object wraps external data (read-only).

  """

  order: typing.Any = ...

  """

  Euler rotation order.

  """

  owner: typing.Any = ...

  """

  The item this is wrapping or None  (read-only).

  """

  x: float = ...

  """

  Euler axis angle in radians.

  """

  y: float = ...

  """

  Euler axis angle in radians.

  """

  z: float = ...

  """

  Euler axis angle in radians.

  """

  def __getitem__(self, index: int) -> float:

    """

    Get the angle component at index.

    """

    ...

  def __setitem__(self, index: int, value: float) -> None:

    """

    Set the angle component at index.

    """

    ...

class Matrix:

  """

  This object gives access to Matrices in Blender, supporting square and rectangular
matrices from 2x2 up to 4x4.

  .. code::

    import mathutils
    import math

    # Create a location matrix.
    mat_loc = mathutils.Matrix.Translation((2.0, 3.0, 4.0))

    # Create an identity matrix.
    mat_sca = mathutils.Matrix.Scale(0.5, 4, (0.0, 0.0, 1.0))

    # Create a rotation matrix.
    mat_rot = mathutils.Matrix.Rotation(math.radians(45.0), 4, 'X')

    # Combine transformations.
    mat_out = mat_loc @ mat_rot @ mat_sca
    print(mat_out)

    # Extract components back out of the matrix as two vectors and a quaternion.
    loc, rot, sca = mat_out.decompose()
    print(loc, rot, sca)

    # Recombine extracted components.
    mat_out2 = mathutils.Matrix.LocRotScale(loc, rot, sca)
    print(mat_out2)

    # It can also be useful to access components of a matrix directly.
    mat = mathutils.Matrix()
    mat[0][0], mat[1][0], mat[2][0] = 0.0, 1.0, 2.0

    mat[0][0:3] = 0.0, 1.0, 2.0

    # Each item in a matrix is a vector so vector utility functions can be used.
    mat[0].xyz = 0.0, 1.0, 2.0

    # Direct buffer access is supported.
    print(memoryview(mat).tobytes())

  """

  def __init__(self) -> None:

    """

    :arg rows:        
      Sequence of rows.

    :type rows:       
      Sequence[Sequence[float]]

    """

    ...

  @classmethod

  def Diagonal(cls) -> Matrix:

    """

    Create a diagonal (scaling) matrix using the values from the vector.

    """

    ...

  @classmethod

  def Identity(cls) -> Matrix:

    """

    Create an identity matrix.

    """

    ...

  @classmethod

  def LocRotScale(cls) -> Matrix:

    """

    Create a matrix combining translation, rotation and scale,
acting as the inverse of the decompose() method.

    Any of the inputs may be replaced with None if not needed.

    .. code::

      # Compute local object transformation matrix:
      if obj.rotation_mode == 'QUATERNION':
          matrix = mathutils.Matrix.LocRotScale(obj.location, obj.rotation_quaternion, obj.scale)
      else:
          matrix = mathutils.Matrix.LocRotScale(obj.location, obj.rotation_euler, obj.scale)

    """

    ...

  @classmethod

  def OrthoProjection(cls) -> Matrix:

    """

    Create a matrix to represent an orthographic projection.

    """

    ...

  @classmethod

  def Rotation(cls) -> Matrix:

    """

    Create a matrix representing a rotation.

    """

    ...

  @classmethod

  def Scale(cls) -> Matrix:

    """

    Create a matrix representing a scaling.

    """

    ...

  @classmethod

  def Shear(cls) -> Matrix:

    """

    Create a matrix to represent a shear transformation.

    """

    ...

  @classmethod

  def Translation(cls) -> Matrix:

    """

    Create a matrix representing a translation.

    """

    ...

  def adjugate(self) -> None:

    """

    Set the matrix to its adjugate.

    `Adjugate matrix <https://en.wikipedia.org/wiki/Adjugate_matrix>`_ on Wikipedia.

    """

    ...

  def adjugated(self) -> Matrix:

    """

    Return an adjugated copy of the matrix.

    """

    ...

  def copy(self) -> Matrix:

    """

    Returns a copy of this matrix.

    """

    ...

  def decompose(self) -> typing.Any:

    """

    Return the translation, rotation, and scale components of this matrix.

    """

    ...

  def determinant(self) -> float:

    """

    Return the determinant of a matrix.

    `Determinant <https://en.wikipedia.org/wiki/Determinant>`_ on Wikipedia.

    """

    ...

  def freeze(self) -> None:

    """

    Make this object immutable.

    After this the object can be hashed, used in dictionaries & sets.

    """

    ...

  def identity(self) -> None:

    """

    Set the matrix to the identity matrix.

    Note: An object with a location and rotation of zero, and a scale of one
will have an identity matrix.

    `Identity matrix <https://en.wikipedia.org/wiki/Identity_matrix>`_ on Wikipedia.

    """

    ...

  def invert(self) -> None:

    """

    Set the matrix to its inverse.

    `Inverse matrix <https://en.wikipedia.org/wiki/Inverse_matrix>`_ on Wikipedia.

    """

    ...

  def invert_safe(self) -> None:

    """

    Set the matrix to its inverse, will never error.
If degenerated (e.g. zero scale on an axis), add some epsilon to its diagonal, to get an invertible one.
If tweaked matrix is still degenerated, set to the identity matrix instead.

    `Inverse Matrix <https://en.wikipedia.org/wiki/Inverse_matrix>`_ on Wikipedia.

    """

    ...

  def inverted(self) -> Matrix:

    """

    Return an inverted copy of the matrix.

    """

    ...

  def inverted_safe(self) -> Matrix:

    """

    Return an inverted copy of the matrix, will never error.
If degenerated (e.g. zero scale on an axis), add some epsilon to its diagonal, to get an invertible one.
If tweaked matrix is still degenerated, return the identity matrix instead.

    """

    ...

  def lerp(self) -> Matrix:

    """

    Returns the interpolation of two matrices. Uses polar decomposition, see   "Matrix Animation and Polar Decomposition", Shoemake and Duff, 1992.

    """

    ...

  def normalize(self) -> None:

    """

    Normalize each of the matrix columns.

    Note: for 4x4 matrices, the 4th column (translation) is left untouched.

    """

    ...

  def normalized(self) -> Matrix:

    """

    Return a column normalized matrix

    Note: for 4x4 matrices, the 4th column (translation) is left untouched.

    """

    ...

  def resize_4x4(self) -> None:

    """

    Resize the matrix to 4x4.

    """

    ...

  def rotate(self) -> None:

    """

    Rotates the matrix by another mathutils value.

    Note: If any of the columns are not unit length this may not have desired results.

    """

    ...

  def to_2x2(self) -> Matrix:

    """

    Return a 2x2 copy of this matrix.

    """

    ...

  def to_3x3(self) -> Matrix:

    """

    Return a 3x3 copy of this matrix.

    """

    ...

  def to_4x4(self) -> Matrix:

    """

    Return a 4x4 copy of this matrix.

    """

    ...

  def to_euler(self) -> Euler:

    """

    Return an Euler representation of the rotation matrix
(3x3 or 4x4 matrix only).

    """

    ...

  def to_quaternion(self) -> Quaternion:

    """

    Return a quaternion representation of the rotation matrix.

    """

    ...

  def to_scale(self) -> Vector:

    """

    Return the scale part of a 3x3 or 4x4 matrix.

    Note: This method does not return a negative scale on any axis because it is not possible to obtain this data from the matrix alone.

    """

    ...

  def to_translation(self) -> Vector:

    """

    Return the translation part of a 4 row matrix.

    """

    ...

  def transpose(self) -> None:

    """

    Set the matrix to its transpose.

    `Transpose <https://en.wikipedia.org/wiki/Transpose>`_ on Wikipedia.

    """

    ...

  def transposed(self) -> Matrix:

    """

    Return a new, transposed matrix.

    """

    ...

  def zero(self) -> None:

    """

    Set all the matrix values to zero.

    """

    ...

  col: Matrix = ...

  """

  Access the matrix by columns, 3x3 and 4x4 only, (read-only).

  """

  is_frozen: bool = ...

  """

  True when this object has been frozen (read-only).

  """

  is_identity: bool = ...

  """

  True if this is an identity matrix (read-only).

  """

  is_negative: bool = ...

  """

  True if this matrix results in a negative scale, 3x3 and 4x4 only, (read-only).

  """

  is_orthogonal: bool = ...

  """

  True if this matrix is orthogonal, 3x3 and 4x4 only, (read-only).

  """

  is_orthogonal_axis_vectors: bool = ...

  """

  True if this matrix has got orthogonal axis vectors, 3x3 and 4x4 only, (read-only).

  """

  is_valid: bool = ...

  """

  True when the owner of this data is valid.

  """

  is_wrapped: bool = ...

  """

  True when this object wraps external data (read-only).

  """

  median_scale: float = ...

  """

  The average scale applied to each axis (read-only).

  """

  owner: typing.Any = ...

  """

  The item this is wrapping or None  (read-only).

  """

  row: Matrix = ...

  """

  Access the matrix by rows (default), (read-only).

  """

  translation: Vector = ...

  """

  The translation component of the matrix.

  """

  def __add__(self, value: Matrix) -> Matrix:

    """

    Add another matrix to this one.

    """

    ...

  def __sub__(self, value: Matrix) -> Matrix:

    """

    Subtract another matrix from this one.

    """

    ...

  def __mul__(self, value: typing.Union[Matrix, float]) -> Matrix:

    """

    Multiply this matrix with another one or a scala value.

    """

    ...

  def __rmul__(self, value: float) -> Matrix:

    """

    Multiply this matrix with a scala value.

    """

    ...

  def __imul__(self, value: typing.Union[Matrix, float]) -> Matrix:

    """

    Multiply this matrix by another one or a scala value.

    """

    ...

  def __matmul__(self, value: typing.Union[Matrix, Vector, Quaternion]) -> typing.Union[Matrix, Vector, Quaternion]:

    """

    Multiply this matrix with another matrix, a vector, or quaternion.

    """

    ...

  def __imatmul__(self, value: typing.Union[Matrix, Vector, Quaternion]) -> typing.Union[Matrix, Vector, Quaternion]:

    """

    Multiply this matrix with another matrix, a vector, or quaternion.

    """

    ...

  def __invert__(self) -> Matrix:

    """

    Invert this matrix.

    """

    ...

  def __truediv__(self, value: float) -> Matrix:

    """

    Divide this matrix by a float value.

    """

    ...

  def __itruediv__(self, value: float) -> Matrix:

    """

    Divide this matrix by a float value.

    """

    ...

  def __getitem__(self, index: int) -> Vector:

    """

    Get the row at given index.

    """

    ...

  def __setitem__(self, index: int, value: typing.Union[Vector, typing.Tuple[float, ...]]) -> None:

    """

    Set the row at given index.

    """

    ...

class Quaternion:

  """

  This object gives access to Quaternions in Blender.

  The constructor takes arguments in various forms:

  (), *no args*
    Create an identity quaternion

  (*wxyz*)
    Create a quaternion from a ``(w, x, y, z)`` vector.

  (*exponential_map*)
    Create a quaternion from a 3d exponential map vector.

    :meth:`to_exponential_map`

  (*axis, angle*)
    Create a quaternion representing a rotation of *angle* radians over *axis*.

    :meth:`to_axis_angle`

  .. code::

    import mathutils
    import math

    # A new rotation 90 degrees about the Y axis.
    quat_a = mathutils.Quaternion((0.7071068, 0.0, 0.7071068, 0.0))

    # Passing values to Quaternion's directly can be confusing so axis, angle
    # is supported for initializing too.
    quat_b = mathutils.Quaternion((0.0, 1.0, 0.0), math.radians(90.0))

    print("Check quaternions match", quat_a == quat_b)

    # Like matrices, quaternions can be multiplied to accumulate rotational values.
    quat_a = mathutils.Quaternion((0.0, 1.0, 0.0), math.radians(90.0))
    quat_b = mathutils.Quaternion((0.0, 0.0, 1.0), math.radians(45.0))
    quat_out = quat_a @ quat_b

    # Print the quaternion, euler degrees for mere mortals and (axis, angle).
    print("Final Rotation:")
    print(quat_out)
    print("{:.2f}, {:.2f}, {:.2f}".format(*(math.degrees(a) for a in quat_out.to_euler())))
    print("({:.2f}, {:.2f}, {:.2f}), {:.2f}".format(*quat_out.axis, math.degrees(quat_out.angle)))

    # Multiple rotations can be interpolated using the exponential map.
    quat_c = mathutils.Quaternion((1.0, 0.0, 0.0), math.radians(15.0))
    exp_avg = (quat_a.to_exponential_map() +
               quat_b.to_exponential_map() +
               quat_c.to_exponential_map()) / 3.0
    quat_avg = mathutils.Quaternion(exp_avg)
    print("Average rotation:")
    print(quat_avg)

    # Direct buffer access is supported.
    print(memoryview(quat_avg).tobytes())

  """

  def __init__(self) -> None:

    """

    :arg seq:         
      size 3 or 4

    :type seq:        
      :class:`Vector`

    :arg angle:       
      rotation angle, in radians

    :type angle:      
      float

    """

    ...

  def conjugate(self) -> None:

    """

    Set the quaternion to its conjugate (negate x, y, z).

    """

    ...

  def conjugated(self) -> Quaternion:

    """

    Return a new conjugated quaternion.

    """

    ...

  def copy(self) -> Quaternion:

    """

    Returns a copy of this quaternion.

    Note: use this to get a copy of a wrapped quaternion with
no reference to the original data.

    """

    ...

  def cross(self) -> Quaternion:

    """

    Return the cross product of this quaternion and another.

    """

    ...

  def dot(self) -> float:

    """

    Return the dot product of this quaternion and another.

    """

    ...

  def freeze(self) -> None:

    """

    Make this object immutable.

    After this the object can be hashed, used in dictionaries & sets.

    """

    ...

  def identity(self) -> None:

    """

    Set the quaternion to an identity quaternion.

    """

    ...

  def invert(self) -> None:

    """

    Set the quaternion to its inverse.

    """

    ...

  def inverted(self) -> Quaternion:

    """

    Return a new, inverted quaternion.

    """

    ...

  def make_compatible(self) -> None:

    """

    Make this quaternion compatible with another,
so interpolating between them works as intended.

    """

    ...

  def negate(self) -> None:

    """

    Set the quaternion to its negative.

    """

    ...

  def normalize(self) -> None:

    """

    Normalize the quaternion.

    """

    ...

  def normalized(self) -> Quaternion:

    """

    Return a new normalized quaternion.

    """

    ...

  def rotate(self) -> None:

    """

    Rotates the quaternion by another mathutils value.

    """

    ...

  def rotation_difference(self) -> Quaternion:

    """

    Returns a quaternion representing the rotational difference.

    """

    ...

  def slerp(self) -> Quaternion:

    """

    Returns the interpolation of two quaternions.

    """

    ...

  def to_axis_angle(self) -> typing.Any:

    """

    Return the axis, angle representation of the quaternion.

    """

    ...

  def to_euler(self) -> Euler:

    """

    Return Euler representation of the quaternion.

    """

    ...

  def to_exponential_map(self) -> Vector:

    """

    Return the exponential map representation of the quaternion.

    This representation consist of the rotation axis multiplied by the rotation angle.
Such a representation is useful for interpolation between multiple orientations.

    To convert back to a quaternion, pass it to the :class:`Quaternion` constructor.

    """

    ...

  def to_matrix(self) -> Matrix:

    """

    Return a matrix representation of the quaternion.

    """

    ...

  def to_swing_twist(self) -> typing.Any:

    """

    Split the rotation into a swing quaternion with the specified
axis fixed at zero, and the remaining twist rotation angle.

    """

    ...

  angle: float = ...

  """

  Angle of the quaternion.

  """

  axis: Vector = ...

  """

  Quaternion axis as a vector.

  """

  is_frozen: bool = ...

  """

  True when this object has been frozen (read-only).

  """

  is_valid: bool = ...

  """

  True when the owner of this data is valid.

  """

  is_wrapped: bool = ...

  """

  True when this object wraps external data (read-only).

  """

  magnitude: float = ...

  """

  Size of the quaternion (read-only).

  """

  owner: typing.Any = ...

  """

  The item this is wrapping or None  (read-only).

  """

  w: float = ...

  """

  Quaternion axis value.

  """

  x: float = ...

  """

  Quaternion axis value.

  """

  y: float = ...

  """

  Quaternion axis value.

  """

  z: float = ...

  """

  Quaternion axis value.

  """

  def __add__(self, value: Quaternion) -> Quaternion:

    """

    Add another quaternion to this one.

    """

    ...

  def __sub__(self, value: Quaternion) -> Quaternion:

    """

    Subtract another quaternion from this one.

    """

    ...

  def __mul__(self, value: typing.Union[Quaternion, float]) -> Quaternion:

    """

    Multiply this quaternion with another one or a scala value.

    """

    ...

  def __rmul__(self, value: float) -> Quaternion:

    """

    Multiply this quaternion with a scala value.

    """

    ...

  def __imul__(self, value: typing.Union[Quaternion, float]) -> Quaternion:

    """

    Multiply this quaternion with another one or a scala value.

    """

    ...

  def __matmul__(self, value: typing.Union[Quaternion, Vector]) -> typing.Union[Quaternion, Vector]:

    """

    Multiply with another quaternion or a vector.

    """

    ...

  def __imatmul__(self, value: typing.Union[Quaternion, Vector]) -> typing.Union[Quaternion, Vector]:

    """

    Multiply with another quaternion or a vector.

    """

    ...

  def __truediv__(self, value: float) -> Quaternion:

    """

    Divide this quaternion by a float value.

    """

    ...

  def __itruediv__(self, value: float) -> Quaternion:

    """

    Divide this quaternion by a float value.

    """

    ...

  def __getitem__(self, index: int) -> float:

    """

    Get quaternion component at index.

    """

    ...

  def __setitem__(self, index: int, value: float) -> None:

    """

    Set quaternion component at index.

    """

    ...

class Vector:

  """

  This object gives access to Vectors in Blender.

  .. code::

    import mathutils

    # Zero length vector.
    vec = mathutils.Vector((0.0, 0.0, 1.0))

    # Unit length vector.
    vec_a = vec.normalized()

    vec_b = mathutils.Vector((0.0, 1.0, 2.0))

    vec2d = mathutils.Vector((1.0, 2.0))
    vec3d = mathutils.Vector((1.0, 0.0, 0.0))
    vec4d = vec_a.to_4d()

    # Other `mathutils` types.
    quat = mathutils.Quaternion()
    matrix = mathutils.Matrix()

    # Comparison operators can be done on Vector classes:

    # (In)equality operators == and != test component values, e.g. 1,2,3 != 3,2,1
    vec_a == vec_b
    vec_a != vec_b

    # Ordering operators >, >=, > and <= test vector length.
    vec_a > vec_b
    vec_a >= vec_b
    vec_a < vec_b
    vec_a <= vec_b


    # Math can be performed on Vector classes.
    vec_a + vec_b
    vec_a - vec_b
    vec_a @ vec_b
    vec_a * 10.0
    matrix @ vec_a
    quat @ vec_a
    -vec_a


    # You can access a vector object like a sequence.
    x = vec_a[0]
    len(vec)
    vec_a[:] = vec_b
    vec_a[:] = 1.0, 2.0, 3.0
    vec2d[:] = vec3d[:2]


    # Vectors support 'swizzle' operations.
    # See https://en.wikipedia.org/wiki/Swizzling_(computer_graphics)
    vec.xyz = vec.zyx
    vec.xy = vec4d.zw
    vec.xyz = vec4d.wzz
    vec4d.wxyz = vec.yxyx

    # Direct buffer access is supported.
    raw_data = memoryview(vec).tobytes()

  """

  def __init__(self) -> None:

    """

    :arg seq:         
      Components of the vector, must be a sequence of at least two.

    :type seq:        
      Sequence[float]

    """

    ...

  @classmethod

  def Fill(cls) -> None:

    """

    Create a vector of length size with all values set to fill.

    """

    ...

  @classmethod

  def Linspace(cls) -> None:

    """

    Create a vector of the specified size which is filled with linearly spaced values between start and stop values.

    """

    ...

  @classmethod

  def Range(cls) -> None:

    """

    Create a filled with a range of values.

      This method can also be called with a single argument, in which case the argument is interpreted as ``stop`` and ``start`` defaults to 0.

    """

    ...

  @classmethod

  def Repeat(cls) -> None:

    """

    Create a vector by repeating the values in vector until the required size is reached.

    """

    ...

  def angle(self) -> float:

    """

    Return the angle between two vectors.

    """

    ...

  def angle_signed(self) -> float:

    """

    Return the signed angle between two 2D vectors (clockwise is positive).

    """

    ...

  def copy(self) -> Vector:

    """

    Returns a copy of this vector.

    Note: use this to get a copy of a wrapped vector with
no reference to the original data.

    """

    ...

  def cross(self) -> Vector:

    """

    Return the cross product of this vector and another.

    Note: both vectors must be 2D or 3D

    """

    ...

  def dot(self) -> float:

    """

    Return the dot product of this vector and another.

    """

    ...

  def freeze(self) -> None:

    """

    Make this object immutable.

    After this the object can be hashed, used in dictionaries & sets.

    """

    ...

  def lerp(self) -> Vector:

    """

    Returns the interpolation of two vectors.

    """

    ...

  def negate(self) -> None:

    """

    Set all values to their negative.

    """

    ...

  def normalize(self) -> None:

    """

    Normalize the vector, making the length of the vector always 1.0.

    Warning: Normalizing a vector where all values are zero has no effect.

    Note: Normalize works for vectors of all sizes,
however 4D Vectors w axis is left untouched.

    """

    ...

  def normalized(self) -> Vector:

    """

    Return a new, normalized vector.

    """

    ...

  def orthogonal(self) -> Vector:

    """

    Return a perpendicular vector.

    Note: the axis is undefined, only use when any orthogonal vector is acceptable.

    """

    ...

  def project(self) -> Vector:

    """

    Return the projection of this vector onto the *other*.

    """

    ...

  def reflect(self) -> Vector:

    """

    Return the reflection vector from the *mirror* argument.

    """

    ...

  def resize(self) -> None:

    """

    Resize the vector to have size number of elements.

    """

    ...

  def resize_2d(self) -> None:

    """

    Resize the vector to 2D  (x, y).

    """

    ...

  def resize_3d(self) -> None:

    """

    Resize the vector to 3D  (x, y, z).

    """

    ...

  def resize_4d(self) -> None:

    """

    Resize the vector to 4D (x, y, z, w).

    """

    ...

  def resized(self) -> Vector:

    """

    Return a resized copy of the vector with size number of elements.

    """

    ...

  def rotate(self) -> None:

    """

    Rotate the vector by a rotation value.

    Note: 2D vectors are a special case that can only be rotated by a 2x2 matrix.

    """

    ...

  def rotation_difference(self) -> Quaternion:

    """

    Returns a quaternion representing the rotational difference between this
vector and another.

    Note: 2D vectors raise an :exc:`AttributeError`.

    """

    ...

  def slerp(self) -> Vector:

    """

    Returns the interpolation of two non-zero vectors (spherical coordinates).

    """

    ...

  def to_2d(self) -> Vector:

    """

    Return a 2d copy of the vector.

    """

    ...

  def to_3d(self) -> Vector:

    """

    Return a 3d copy of the vector.

    """

    ...

  def to_4d(self) -> Vector:

    """

    Return a 4d copy of the vector.

    """

    ...

  def to_track_quat(self) -> Quaternion:

    """

    Return a quaternion rotation from the vector and the track and up axis.

    """

    ...

  def to_tuple(self) -> typing.Any:

    """

    Return this vector as a tuple with a given precision.

    """

    ...

  def zero(self) -> None:

    """

    Set all values to zero.

    """

    ...

  is_frozen: bool = ...

  """

  True when this object has been frozen (read-only).

  """

  is_valid: bool = ...

  """

  True when the owner of this data is valid.

  """

  is_wrapped: bool = ...

  """

  True when this object wraps external data (read-only).

  """

  length: float = ...

  """

  Vector Length.

  """

  length_squared: float = ...

  """

  Vector length squared (v.dot(v)).

  """

  magnitude: float = ...

  """

  Vector Length.

  """

  owner: typing.Any = ...

  """

  The item this is wrapping or None  (read-only).

  """

  w: float = ...

  """

  Vector W axis (4D Vectors only).

  """

  ww: Vector = ...

  www: Vector = ...

  wwww: Vector = ...

  wwwx: Vector = ...

  wwwy: Vector = ...

  wwwz: Vector = ...

  wwx: Vector = ...

  wwxw: Vector = ...

  wwxx: Vector = ...

  wwxy: Vector = ...

  wwxz: Vector = ...

  wwy: Vector = ...

  wwyw: Vector = ...

  wwyx: Vector = ...

  wwyy: Vector = ...

  wwyz: Vector = ...

  wwz: Vector = ...

  wwzw: Vector = ...

  wwzx: Vector = ...

  wwzy: Vector = ...

  wwzz: Vector = ...

  wx: Vector = ...

  wxw: Vector = ...

  wxww: Vector = ...

  wxwx: Vector = ...

  wxwy: Vector = ...

  wxwz: Vector = ...

  wxx: Vector = ...

  wxxw: Vector = ...

  wxxx: Vector = ...

  wxxy: Vector = ...

  wxxz: Vector = ...

  wxy: Vector = ...

  wxyw: Vector = ...

  wxyx: Vector = ...

  wxyy: Vector = ...

  wxyz: Vector = ...

  wxz: Vector = ...

  wxzw: Vector = ...

  wxzx: Vector = ...

  wxzy: Vector = ...

  wxzz: Vector = ...

  wy: Vector = ...

  wyw: Vector = ...

  wyww: Vector = ...

  wywx: Vector = ...

  wywy: Vector = ...

  wywz: Vector = ...

  wyx: Vector = ...

  wyxw: Vector = ...

  wyxx: Vector = ...

  wyxy: Vector = ...

  wyxz: Vector = ...

  wyy: Vector = ...

  wyyw: Vector = ...

  wyyx: Vector = ...

  wyyy: Vector = ...

  wyyz: Vector = ...

  wyz: Vector = ...

  wyzw: Vector = ...

  wyzx: Vector = ...

  wyzy: Vector = ...

  wyzz: Vector = ...

  wz: Vector = ...

  wzw: Vector = ...

  wzww: Vector = ...

  wzwx: Vector = ...

  wzwy: Vector = ...

  wzwz: Vector = ...

  wzx: Vector = ...

  wzxw: Vector = ...

  wzxx: Vector = ...

  wzxy: Vector = ...

  wzxz: Vector = ...

  wzy: Vector = ...

  wzyw: Vector = ...

  wzyx: Vector = ...

  wzyy: Vector = ...

  wzyz: Vector = ...

  wzz: Vector = ...

  wzzw: Vector = ...

  wzzx: Vector = ...

  wzzy: Vector = ...

  wzzz: Vector = ...

  x: float = ...

  """

  Vector X axis.

  """

  xw: Vector = ...

  xww: Vector = ...

  xwww: Vector = ...

  xwwx: Vector = ...

  xwwy: Vector = ...

  xwwz: Vector = ...

  xwx: Vector = ...

  xwxw: Vector = ...

  xwxx: Vector = ...

  xwxy: Vector = ...

  xwxz: Vector = ...

  xwy: Vector = ...

  xwyw: Vector = ...

  xwyx: Vector = ...

  xwyy: Vector = ...

  xwyz: Vector = ...

  xwz: Vector = ...

  xwzw: Vector = ...

  xwzx: Vector = ...

  xwzy: Vector = ...

  xwzz: Vector = ...

  xx: Vector = ...

  xxw: Vector = ...

  xxww: Vector = ...

  xxwx: Vector = ...

  xxwy: Vector = ...

  xxwz: Vector = ...

  xxx: Vector = ...

  xxxw: Vector = ...

  xxxx: Vector = ...

  xxxy: Vector = ...

  xxxz: Vector = ...

  xxy: Vector = ...

  xxyw: Vector = ...

  xxyx: Vector = ...

  xxyy: Vector = ...

  xxyz: Vector = ...

  xxz: Vector = ...

  xxzw: Vector = ...

  xxzx: Vector = ...

  xxzy: Vector = ...

  xxzz: Vector = ...

  xy: Vector = ...

  xyw: Vector = ...

  xyww: Vector = ...

  xywx: Vector = ...

  xywy: Vector = ...

  xywz: Vector = ...

  xyx: Vector = ...

  xyxw: Vector = ...

  xyxx: Vector = ...

  xyxy: Vector = ...

  xyxz: Vector = ...

  xyy: Vector = ...

  xyyw: Vector = ...

  xyyx: Vector = ...

  xyyy: Vector = ...

  xyyz: Vector = ...

  xyz: Vector = ...

  xyzw: Vector = ...

  xyzx: Vector = ...

  xyzy: Vector = ...

  xyzz: Vector = ...

  xz: Vector = ...

  xzw: Vector = ...

  xzww: Vector = ...

  xzwx: Vector = ...

  xzwy: Vector = ...

  xzwz: Vector = ...

  xzx: Vector = ...

  xzxw: Vector = ...

  xzxx: Vector = ...

  xzxy: Vector = ...

  xzxz: Vector = ...

  xzy: Vector = ...

  xzyw: Vector = ...

  xzyx: Vector = ...

  xzyy: Vector = ...

  xzyz: Vector = ...

  xzz: Vector = ...

  xzzw: Vector = ...

  xzzx: Vector = ...

  xzzy: Vector = ...

  xzzz: Vector = ...

  y: float = ...

  """

  Vector Y axis.

  """

  yw: Vector = ...

  yww: Vector = ...

  ywww: Vector = ...

  ywwx: Vector = ...

  ywwy: Vector = ...

  ywwz: Vector = ...

  ywx: Vector = ...

  ywxw: Vector = ...

  ywxx: Vector = ...

  ywxy: Vector = ...

  ywxz: Vector = ...

  ywy: Vector = ...

  ywyw: Vector = ...

  ywyx: Vector = ...

  ywyy: Vector = ...

  ywyz: Vector = ...

  ywz: Vector = ...

  ywzw: Vector = ...

  ywzx: Vector = ...

  ywzy: Vector = ...

  ywzz: Vector = ...

  yx: Vector = ...

  yxw: Vector = ...

  yxww: Vector = ...

  yxwx: Vector = ...

  yxwy: Vector = ...

  yxwz: Vector = ...

  yxx: Vector = ...

  yxxw: Vector = ...

  yxxx: Vector = ...

  yxxy: Vector = ...

  yxxz: Vector = ...

  yxy: Vector = ...

  yxyw: Vector = ...

  yxyx: Vector = ...

  yxyy: Vector = ...

  yxyz: Vector = ...

  yxz: Vector = ...

  yxzw: Vector = ...

  yxzx: Vector = ...

  yxzy: Vector = ...

  yxzz: Vector = ...

  yy: Vector = ...

  yyw: Vector = ...

  yyww: Vector = ...

  yywx: Vector = ...

  yywy: Vector = ...

  yywz: Vector = ...

  yyx: Vector = ...

  yyxw: Vector = ...

  yyxx: Vector = ...

  yyxy: Vector = ...

  yyxz: Vector = ...

  yyy: Vector = ...

  yyyw: Vector = ...

  yyyx: Vector = ...

  yyyy: Vector = ...

  yyyz: Vector = ...

  yyz: Vector = ...

  yyzw: Vector = ...

  yyzx: Vector = ...

  yyzy: Vector = ...

  yyzz: Vector = ...

  yz: Vector = ...

  yzw: Vector = ...

  yzww: Vector = ...

  yzwx: Vector = ...

  yzwy: Vector = ...

  yzwz: Vector = ...

  yzx: Vector = ...

  yzxw: Vector = ...

  yzxx: Vector = ...

  yzxy: Vector = ...

  yzxz: Vector = ...

  yzy: Vector = ...

  yzyw: Vector = ...

  yzyx: Vector = ...

  yzyy: Vector = ...

  yzyz: Vector = ...

  yzz: Vector = ...

  yzzw: Vector = ...

  yzzx: Vector = ...

  yzzy: Vector = ...

  yzzz: Vector = ...

  z: float = ...

  """

  Vector Z axis (3D Vectors only).

  """

  zw: Vector = ...

  zww: Vector = ...

  zwww: Vector = ...

  zwwx: Vector = ...

  zwwy: Vector = ...

  zwwz: Vector = ...

  zwx: Vector = ...

  zwxw: Vector = ...

  zwxx: Vector = ...

  zwxy: Vector = ...

  zwxz: Vector = ...

  zwy: Vector = ...

  zwyw: Vector = ...

  zwyx: Vector = ...

  zwyy: Vector = ...

  zwyz: Vector = ...

  zwz: Vector = ...

  zwzw: Vector = ...

  zwzx: Vector = ...

  zwzy: Vector = ...

  zwzz: Vector = ...

  zx: Vector = ...

  zxw: Vector = ...

  zxww: Vector = ...

  zxwx: Vector = ...

  zxwy: Vector = ...

  zxwz: Vector = ...

  zxx: Vector = ...

  zxxw: Vector = ...

  zxxx: Vector = ...

  zxxy: Vector = ...

  zxxz: Vector = ...

  zxy: Vector = ...

  zxyw: Vector = ...

  zxyx: Vector = ...

  zxyy: Vector = ...

  zxyz: Vector = ...

  zxz: Vector = ...

  zxzw: Vector = ...

  zxzx: Vector = ...

  zxzy: Vector = ...

  zxzz: Vector = ...

  zy: Vector = ...

  zyw: Vector = ...

  zyww: Vector = ...

  zywx: Vector = ...

  zywy: Vector = ...

  zywz: Vector = ...

  zyx: Vector = ...

  zyxw: Vector = ...

  zyxx: Vector = ...

  zyxy: Vector = ...

  zyxz: Vector = ...

  zyy: Vector = ...

  zyyw: Vector = ...

  zyyx: Vector = ...

  zyyy: Vector = ...

  zyyz: Vector = ...

  zyz: Vector = ...

  zyzw: Vector = ...

  zyzx: Vector = ...

  zyzy: Vector = ...

  zyzz: Vector = ...

  zz: Vector = ...

  zzw: Vector = ...

  zzww: Vector = ...

  zzwx: Vector = ...

  zzwy: Vector = ...

  zzwz: Vector = ...

  zzx: Vector = ...

  zzxw: Vector = ...

  zzxx: Vector = ...

  zzxy: Vector = ...

  zzxz: Vector = ...

  zzy: Vector = ...

  zzyw: Vector = ...

  zzyx: Vector = ...

  zzyy: Vector = ...

  zzyz: Vector = ...

  zzz: Vector = ...

  zzzw: Vector = ...

  zzzx: Vector = ...

  zzzy: Vector = ...

  zzzz: Vector = ...

  def __add__(self, value: Vector) -> Vector:

    """

    Add another vector to this one.

    """

    ...

  def __sub__(self, value: Vector) -> Vector:

    """

    Subtract another vector from this one.

    """

    ...

  def __mul__(self, value: typing.Union[Vector, float]) -> Vector:

    """

    Multiply this vector with another one or a scala value.

    """

    ...

  def __rmul__(self, value: float) -> Vector:

    """

    Multiply this vector with a scala value.

    """

    ...

  def __imul__(self, value: typing.Union[Vector, float]) -> Vector:

    """

    Multiply this vector with another one or a scala value.

    """

    ...

  def __matmul__(self, value: typing.Union[Matrix, Vector]) -> typing.Union[Vector, float]:

    """

    Multiply this vector with a matrix or another vector.

    """

    ...

  def __imatmul__(self, value: typing.Union[Matrix, Vector]) -> typing.Union[Vector, float]:

    """

    Multiply this vector with a matrix or another vector.

    """

    ...

  def __truediv__(self, value: float) -> Vector:

    """

    Divide this vector by a float value.

    """

    ...

  def __itruediv__(self, value: float) -> Vector:

    """

    Divide this vector by a float value.

    """

    ...

  def __getitem__(self, index: int) -> float:

    """

    Get vector component at index.

    """

    ...

  def __setitem__(self, index: int, value: float) -> None:

    """

    Set vector component at index.

    """

    ...
