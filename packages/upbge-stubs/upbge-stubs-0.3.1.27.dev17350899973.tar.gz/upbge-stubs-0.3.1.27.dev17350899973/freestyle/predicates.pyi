"""


Freestyle Predicates (freestyle.predicates)
*******************************************

This module contains predicates operating on vertices (0D elements)
and polylines (1D elements).  It is also intended to be a collection
of examples for predicate definition in Python.

User-defined predicates inherit one of the following base classes,
depending on the object type (0D or 1D) to operate on and the arity
(unary or binary):

* :class:`freestyle.types.BinaryPredicate0D`

* :class:`freestyle.types.BinaryPredicate1D`

* :class:`freestyle.types.UnaryPredicate0D`

* :class:`freestyle.types.UnaryPredicate1D`

:class:`freestyle.predicates.AndBP1D`

:class:`freestyle.predicates.AndUP1D`

:class:`freestyle.predicates.ContourUP1D`

:class:`freestyle.predicates.DensityLowerThanUP1D`

:class:`freestyle.predicates.EqualToChainingTimeStampUP1D`

:class:`freestyle.predicates.EqualToTimeStampUP1D`

:class:`freestyle.predicates.ExternalContourUP1D`

:class:`freestyle.predicates.FalseBP1D`

:class:`freestyle.predicates.FalseUP0D`

:class:`freestyle.predicates.FalseUP1D`

:class:`freestyle.predicates.Length2DBP1D`

:class:`freestyle.predicates.MaterialBP1D`

:class:`freestyle.predicates.NotBP1D`

:class:`freestyle.predicates.NotUP1D`

:class:`freestyle.predicates.ObjectNamesUP1D`

:class:`freestyle.predicates.OrBP1D`

:class:`freestyle.predicates.OrUP1D`

:class:`freestyle.predicates.QuantitativeInvisibilityRangeUP1D`

:class:`freestyle.predicates.QuantitativeInvisibilityUP1D`

:class:`freestyle.predicates.SameShapeIdBP1D`

:class:`freestyle.predicates.ShapeUP1D`

:class:`freestyle.predicates.TrueBP1D`

:class:`freestyle.predicates.TrueUP0D`

:class:`freestyle.predicates.TrueUP1D`

:class:`freestyle.predicates.ViewMapGradientNormBP1D`

:class:`freestyle.predicates.WithinImageBoundaryUP1D`

:class:`freestyle.predicates.pyBackTVertexUP0D`

:class:`freestyle.predicates.pyClosedCurveUP1D`

:class:`freestyle.predicates.pyDensityFunctorUP1D`

:class:`freestyle.predicates.pyDensityUP1D`

:class:`freestyle.predicates.pyDensityVariableSigmaUP1D`

:class:`freestyle.predicates.pyHighDensityAnisotropyUP1D`

:class:`freestyle.predicates.pyHighDirectionalViewMapDensityUP1D`

:class:`freestyle.predicates.pyHighSteerableViewMapDensityUP1D`

:class:`freestyle.predicates.pyHighViewMapDensityUP1D`

:class:`freestyle.predicates.pyHighViewMapGradientNormUP1D`

:class:`freestyle.predicates.pyHigherCurvature2DAngleUP0D`

:class:`freestyle.predicates.pyHigherLengthUP1D`

:class:`freestyle.predicates.pyHigherNumberOfTurnsUP1D`

:class:`freestyle.predicates.pyIsInOccludersListUP1D`

:class:`freestyle.predicates.pyIsOccludedByIdListUP1D`

:class:`freestyle.predicates.pyIsOccludedByItselfUP1D`

:class:`freestyle.predicates.pyIsOccludedByUP1D`

:class:`freestyle.predicates.pyLengthBP1D`

:class:`freestyle.predicates.pyLowDirectionalViewMapDensityUP1D`

:class:`freestyle.predicates.pyLowSteerableViewMapDensityUP1D`

:class:`freestyle.predicates.pyNFirstUP1D`

:class:`freestyle.predicates.pyNatureBP1D`

:class:`freestyle.predicates.pyNatureUP1D`

:class:`freestyle.predicates.pyParameterUP0D`

:class:`freestyle.predicates.pyParameterUP0DGoodOne`

:class:`freestyle.predicates.pyProjectedXBP1D`

:class:`freestyle.predicates.pyProjectedYBP1D`

:class:`freestyle.predicates.pyShapeIdListUP1D`

:class:`freestyle.predicates.pyShapeIdUP1D`

:class:`freestyle.predicates.pyShuffleBP1D`

:class:`freestyle.predicates.pySilhouetteFirstBP1D`

:class:`freestyle.predicates.pyUEqualsUP0D`

:class:`freestyle.predicates.pyVertexNatureUP0D`

:class:`freestyle.predicates.pyViewMapGradientNormBP1D`

:class:`freestyle.predicates.pyZBP1D`

:class:`freestyle.predicates.pyZDiscontinuityBP1D`

:class:`freestyle.predicates.pyZSmallerUP1D`

"""

import typing

import freestyle

class freestyle.predicates.AndBP1D:

  ...

class freestyle.predicates.AndUP1D:

  ...

class freestyle.predicates.ContourUP1D:

  """

  Class hierarchy: :class:`freestyle.types.UnaryPredicate1D` > :class:`ContourUP1D`

  """

  def __call__(self, inter: freestyle.types.Interface1D) -> bool:

    """

    Returns true if the Interface1D is a contour. An Interface1D is a
contour if it is bordered by a different shape on each of its sides.

    """

    ...

class freestyle.predicates.DensityLowerThanUP1D:

  """

  Class hierarchy: :class:`freestyle.types.UnaryPredicate1D` > :class:`DensityLowerThanUP1D`

  """

  def __init__(self, threshold: float, sigma: float = 2.0) -> None:

    """

    Builds a DensityLowerThanUP1D object.

    """

    ...

  def __call__(self, inter: freestyle.types.Interface1D) -> bool:

    """

    Returns true if the density evaluated for the Interface1D is less
than a user-defined density value.

    """

    ...

class freestyle.predicates.EqualToChainingTimeStampUP1D:

  """

  Class hierarchy: :class:`freestyle.types.UnaryPredicate1D` > :class:`freestyle.types.EqualToChainingTimeStampUP1D`

  """

  def __init__(self, ts: int) -> None:

    """

    Builds a EqualToChainingTimeStampUP1D object.

    """

    ...

  def __call__(self, inter: freestyle.types.Interface1D) -> bool:

    """

    Returns true if the Interface1D's time stamp is equal to a certain
user-defined value.

    """

    ...

class freestyle.predicates.EqualToTimeStampUP1D:

  """

  Class hierarchy: :class:`freestyle.types.UnaryPredicate1D` > :class:`EqualToTimeStampUP1D`

  """

  def __init__(self, ts: int) -> None:

    """

    Builds a EqualToTimeStampUP1D object.

    """

    ...

  def __call__(self, inter: freestyle.types.Interface1D) -> bool:

    """

    Returns true if the Interface1D's time stamp is equal to a certain
user-defined value.

    """

    ...

class freestyle.predicates.ExternalContourUP1D:

  """

  Class hierarchy: :class:`freestyle.types.UnaryPredicate1D` > :class:`ExternalContourUP1D`

  """

  def __call__(self, inter: freestyle.types.Interface1D) -> bool:

    """

    Returns true if the Interface1D is an external contour.
An Interface1D is an external contour if it is bordered by no shape on
one of its sides.

    """

    ...

class freestyle.predicates.FalseBP1D:

  """

  Class hierarchy: :class:`freestyle.types.BinaryPredicate1D` > :class:`FalseBP1D`

  """

  def __call__(self, inter1: freestyle.types.Interface1D, inter2: freestyle.types.Interface1D) -> bool:

    """

    Always returns false.

    """

    ...

class freestyle.predicates.FalseUP0D:

  """

  Class hierarchy: :class:`freestyle.types.UnaryPredicate0D` > :class:`FalseUP0D`

  """

  def __call__(self, it: freestyle.types.Interface0DIterator) -> bool:

    """

    Always returns false.

    """

    ...

class freestyle.predicates.FalseUP1D:

  """

  Class hierarchy: :class:`freestyle.types.UnaryPredicate1D` > :class:`FalseUP1D`

  """

  def __call__(self, inter: freestyle.types.Interface1D) -> bool:

    """

    Always returns false.

    """

    ...

class freestyle.predicates.Length2DBP1D:

  """

  Class hierarchy: :class:`freestyle.types.BinaryPredicate1D` > :class:`Length2DBP1D`

  """

  def __call__(self, inter1: freestyle.types.Interface1D, inter2: freestyle.types.Interface1D) -> bool:

    """

    Returns true if the 2D length of inter1 is less than the 2D length
of inter2.

    """

    ...

class freestyle.predicates.MaterialBP1D:

  """

  Checks whether the two supplied ViewEdges have the same material.

  """

  ...

class freestyle.predicates.NotBP1D:

  ...

class freestyle.predicates.NotUP1D:

  ...

class freestyle.predicates.ObjectNamesUP1D:

  ...

class freestyle.predicates.OrBP1D:

  ...

class freestyle.predicates.OrUP1D:

  ...

class freestyle.predicates.QuantitativeInvisibilityRangeUP1D:

  ...

class freestyle.predicates.QuantitativeInvisibilityUP1D:

  """

  Class hierarchy: :class:`freestyle.types.UnaryPredicate1D` > :class:`QuantitativeInvisibilityUP1D`

  """

  def __init__(self, qi: int = 0) -> None:

    """

    Builds a QuantitativeInvisibilityUP1D object.

    """

    ...

  def __call__(self, inter: freestyle.types.Interface1D) -> bool:

    """

    Returns true if the Quantitative Invisibility evaluated at an
Interface1D, using the
:class:`freestyle.functions.QuantitativeInvisibilityF1D` functor,
equals a certain user-defined value.

    """

    ...

class freestyle.predicates.SameShapeIdBP1D:

  """

  Class hierarchy: :class:`freestyle.types.BinaryPredicate1D` > :class:`SameShapeIdBP1D`

  """

  def __call__(self, inter1: freestyle.types.Interface1D, inter2: freestyle.types.Interface1D) -> bool:

    """

    Returns true if inter1 and inter2 belong to the same shape.

    """

    ...

class freestyle.predicates.ShapeUP1D:

  """

  Class hierarchy: :class:`freestyle.types.UnaryPredicate1D` > :class:`ShapeUP1D`

  """

  def __init__(self, first: int, second: int = 0) -> None:

    """

    Builds a ShapeUP1D object.

    """

    ...

  def __call__(self, inter: freestyle.types.Interface1D) -> bool:

    """

    Returns true if the shape to which the Interface1D belongs to has the
same :class:`freestyle.types.Id` as the one specified by the user.

    """

    ...

class freestyle.predicates.TrueBP1D:

  """

  Class hierarchy: :class:`freestyle.types.BinaryPredicate1D` > :class:`TrueBP1D`

  """

  def __call__(self, inter1: freestyle.types.Interface1D, inter2: freestyle.types.Interface1D) -> bool:

    """

    Always returns true.

    """

    ...

class freestyle.predicates.TrueUP0D:

  """

  Class hierarchy: :class:`freestyle.types.UnaryPredicate0D` > :class:`TrueUP0D`

  """

  def __call__(self, it: freestyle.types.Interface0DIterator) -> bool:

    """

    Always returns true.

    """

    ...

class freestyle.predicates.TrueUP1D:

  """

  Class hierarchy: :class:`freestyle.types.UnaryPredicate1D` > :class:`TrueUP1D`

  """

  def __call__(self, inter: freestyle.types.Interface1D) -> bool:

    """

    Always returns true.

    """

    ...

class freestyle.predicates.ViewMapGradientNormBP1D:

  """

  Class hierarchy: :class:`freestyle.types.BinaryPredicate1D` > :class:`ViewMapGradientNormBP1D`

  """

  def __init__(self, level: int, integration_type: freestyle.types.IntegrationType = IntegrationType.MEAN, sampling: float = 2.0) -> None:

    """

    Builds a ViewMapGradientNormBP1D object.

    """

    ...

  def __call__(self, inter1: freestyle.types.Interface1D, inter2: freestyle.types.Interface1D) -> bool:

    """

    Returns true if the evaluation of the Gradient norm Function is
higher for inter1 than for inter2.

    """

    ...

class freestyle.predicates.WithinImageBoundaryUP1D:

  """

  Class hierarchy: :class:`freestyle.types.UnaryPredicate1D` > :class:`WithinImageBoundaryUP1D`

  """

  def __init__(self, xmin: float, ymin: float, xmax: float, ymax: float) -> None:

    """

    Builds an WithinImageBoundaryUP1D object.

    """

    ...

  def __call__(self, inter: typing.Any) -> None:

    """

    Returns true if the Interface1D intersects with image boundary.

    """

    ...

class freestyle.predicates.pyBackTVertexUP0D:

  """

  Check whether an Interface0DIterator references a TVertex and is
the one that is hidden (inferred from the context).

  """

  ...

class freestyle.predicates.pyClosedCurveUP1D:

  ...

class freestyle.predicates.pyDensityFunctorUP1D:

  ...

class freestyle.predicates.pyDensityUP1D:

  ...

class freestyle.predicates.pyDensityVariableSigmaUP1D:

  ...

class freestyle.predicates.pyHighDensityAnisotropyUP1D:

  ...

class freestyle.predicates.pyHighDirectionalViewMapDensityUP1D:

  ...

class freestyle.predicates.pyHighSteerableViewMapDensityUP1D:

  ...

class freestyle.predicates.pyHighViewMapDensityUP1D:

  ...

class freestyle.predicates.pyHighViewMapGradientNormUP1D:

  ...

class freestyle.predicates.pyHigherCurvature2DAngleUP0D:

  ...

class freestyle.predicates.pyHigherLengthUP1D:

  ...

class freestyle.predicates.pyHigherNumberOfTurnsUP1D:

  ...

class freestyle.predicates.pyIsInOccludersListUP1D:

  ...

class freestyle.predicates.pyIsOccludedByIdListUP1D:

  ...

class freestyle.predicates.pyIsOccludedByItselfUP1D:

  ...

class freestyle.predicates.pyIsOccludedByUP1D:

  ...

class freestyle.predicates.pyLengthBP1D:

  ...

class freestyle.predicates.pyLowDirectionalViewMapDensityUP1D:

  ...

class freestyle.predicates.pyLowSteerableViewMapDensityUP1D:

  ...

class freestyle.predicates.pyNFirstUP1D:

  ...

class freestyle.predicates.pyNatureBP1D:

  ...

class freestyle.predicates.pyNatureUP1D:

  ...

class freestyle.predicates.pyParameterUP0D:

  ...

class freestyle.predicates.pyParameterUP0DGoodOne:

  ...

class freestyle.predicates.pyProjectedXBP1D:

  ...

class freestyle.predicates.pyProjectedYBP1D:

  ...

class freestyle.predicates.pyShapeIdListUP1D:

  ...

class freestyle.predicates.pyShapeIdUP1D:

  ...

class freestyle.predicates.pyShuffleBP1D:

  ...

class freestyle.predicates.pySilhouetteFirstBP1D:

  ...

class freestyle.predicates.pyUEqualsUP0D:

  ...

class freestyle.predicates.pyVertexNatureUP0D:

  ...

class freestyle.predicates.pyViewMapGradientNormBP1D:

  ...

class freestyle.predicates.pyZBP1D:

  ...

class freestyle.predicates.pyZDiscontinuityBP1D:

  ...

class freestyle.predicates.pyZSmallerUP1D:

  ...
