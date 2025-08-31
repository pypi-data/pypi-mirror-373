"""


BVHTree Utilities (mathutils.bvhtree)
*************************************

BVH tree structures for proximity searches and ray casts on geometry.

:class:`mathutils.bvhtree.BVHTree`

"""

import typing

class mathutils.bvhtree.BVHTree:

  """"""

  @classmethod

  def FromBMesh(cls, bmesh: BMesh, *args, epsilon: float = 0.0) -> None:

    """

    BVH tree based on :class:`BMesh` data.

    """

    ...

  @classmethod

  def FromObject(cls, object: Object, depsgraph: Depsgraph, *args, deform: bool = True, render: typing.Any = False, cage: bool = False, epsilon: float = 0.0) -> None:

    """

    BVH tree based on :class:`Object` data.

    """

    ...

  @classmethod

  def FromPolygons(cls, vertices: typing.Any, polygons: typing.Any, *args, all_triangles: bool = False, epsilon: float = 0.0) -> None:

    """

    BVH tree constructed geometry passed in as arguments.

    """

    ...

  def find_nearest(self) -> typing.Any:

    """

    Find the nearest element (typically face index) to a point.

    """

    ...

  def find_nearest_range(self) -> typing.Any:

    """

    Find the nearest elements (typically face index) to a point in the distance range.

    """

    ...

  def overlap(self) -> typing.Any:

    """

    Find overlapping indices between 2 trees.

    """

    ...

  def ray_cast(self) -> typing.Any:

    """

    Cast a ray onto the mesh.

    """

    ...
