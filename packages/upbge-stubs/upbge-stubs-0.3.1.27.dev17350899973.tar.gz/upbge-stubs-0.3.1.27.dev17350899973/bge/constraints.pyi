"""


Physics Constraints (bge.constraints)
*************************************

Bullet Physics provides collision detection
and rigid body dynamics for the Blender Game Engine.

Features:

* Vehicle simulation.

* Rigid body constraints: hinge and point to point (ball socket).

* Access to internal physics settings,
like deactivation time, and debugging features

Note: Note about parameter settingsSince this API is not well documented, it can be unclear what kind of values to use for setting parameters.
In general, damping settings should be in the range of 0 to 1 and
stiffness settings should not be much higher than about 10.


Examples
========

For more examples of Bullet physics and how to use them
see the `pybullet forum <https://pybullet.org/Bullet/phpBB3/viewforum.php?f=17>`_.


Basic Physics Constraint
========================

Example of how to create a hinge Physics Constraint between two objects.

.. code::

  from bge import logic
  from bge import constraints

  # get object list
  objects = logic.getCurrentScene().objects

  # get object named Object1 and Object 2
  object_1 = objects["Object1"]
  object_2 = objects["Object2"]

  # want to use Edge constraint type
  constraint_type = 2

  # get Object1 and Object2 physics IDs
  physics_id_1 = object_1.getPhysicsId()
  physics_id_2 = object_2.getPhysicsId()

  # use bottom right edge of Object1 for hinge position
  edge_position_x = 1.0
  edge_position_y = 0.0
  edge_position_z = -1.0

  # rotate the pivot z axis about 90 degrees
  edge_angle_x = 0.0
  edge_angle_y = 0.0
  edge_angle_z = 90.0

  # create an edge constraint
  constraints.createConstraint(physics_id_1, physics_id_2,
                               constraint_type,
                               edge_position_x, edge_position_y, edge_position_z,
                               edge_angle_x, edge_angle_y, edge_angle_z)


Functions
=========

:func:`createConstraint`

:func:`createVehicle`

:func:`exportBulletFile`

:func:`getAppliedImpulse`

:func:`getVehicleConstraint`

:func:`getCharacter`

:func:`removeConstraint`

:func:`setContactBreakingTreshold`

:func:`setDeactivationAngularTreshold`

:func:`setDeactivationLinearTreshold`

:func:`setDeactivationTime`

:func:`setERPNonContact`

:func:`setERPContact`

:func:`setCFM`

:func:`setDebugMode`

:func:`setGravity`

:func:`setNumIterations`

:func:`setNumTimeSubSteps`

:func:`setSolverDamping`

:func:`setSolverTau`

:func:`setSolverType`

:func:`setSorConstant`


Constants
---------

:data:`error`


Debug Mode Constants
~~~~~~~~~~~~~~~~~~~~

Debug mode to be used with :func:`setDebugMode`.

:data:`DBG_NODEBUG`

:data:`DBG_DRAWWIREFRAME`

:data:`DBG_DRAWAABB`

:data:`DBG_DRAWFREATURESTEXT`

:data:`DBG_DRAWCONTACTPOINTS`

:data:`DBG_NOHELPTEXT`

:data:`DBG_DRAWTEXT`

:data:`DBG_PROFILETIMINGS`

:data:`DBG_ENABLESATCOMPARISION`

:data:`DBG_DISABLEBULLETLCP`

:data:`DBG_ENABLECCD`

:data:`DBG_DRAWCONSTRAINTS`

:data:`DBG_DRAWCONSTRAINTLIMITS`

:data:`DBG_FASTWIREFRAME`


Create Constraint Constants
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Constraint type to be used with :func:`createConstraint`.

:data:`POINTTOPOINT_CONSTRAINT`

:data:`LINEHINGE_CONSTRAINT`

:data:`ANGULAR_CONSTRAINT`

:data:`CONETWIST_CONSTRAINT`

:data:`VEHICLE_CONSTRAINT`

:data:`GENERIC_6DOF_CONSTRAINT`

"""

import typing

import bge

def createConstraint(physicsid_1: int, physicsid_2: int, constraint_type: int, pivot_x: float = 0.0, pivot_y: float = 0.0, pivot_z: float = 0.0, axis_x: float = 0.0, axis_y: float = 0.0, axis_z: float = 0.0, flag: int = 0) -> bge.types.KX_ConstraintWrapper:

  """

  Creates a constraint.

  """

  ...

def createVehicle(physicsid: int) -> bge.types.KX_VehicleWrapper:

  """

  Creates a vehicle constraint.

  """

  ...

def exportBulletFile(filename: str) -> None:

  """

  Exports a file representing the dynamics world (usually using ``.bullet`` extension).

  See `Bullet binary serialization <http://bulletphysics.org/mediawiki-1.5.8/index.php/Bullet_binary_serialization>`_.

  """

  ...

def getAppliedImpulse(constraintId: int) -> float:

  ...

def getVehicleConstraint(constraintId: int) -> bge.types.KX_VehicleWrapper:

  ...

def getCharacter(gameobj: bge.types.KX_GameObject) -> bge.types.KX_CharacterWrapper:

  ...

def removeConstraint(constraintId: int) -> None:

  """

  Removes a constraint.

  """

  ...

def setContactBreakingTreshold(breakingTreshold: float) -> None:

  """

  Note: Reasonable default is 0.02 (if units are meters)

  Sets tresholds to do with contact point management.

  """

  ...

def setDeactivationAngularTreshold(angularTreshold: float) -> None:

  """

  Sets the angular velocity treshold.

  """

  ...

def setDeactivationLinearTreshold(linearTreshold: float) -> None:

  """

  Sets the linear velocity treshold.

  """

  ...

def setDeactivationTime(time: float) -> None:

  """

  Sets the time after which a resting rigidbody gets deactived.

  """

  ...

def setERPNonContact(erp: float) -> None:

  """

  Sets the Error Reduction Parameter (ERP) for non-contact constraints.
The Error Reduction Parameter (ERP) specifies what proportion of the joint error will be fixed during the next simulation step.
If ERP = 0.0 then no correcting force is applied and the bodies will eventually drift apart as the simulation proceeds.
If ERP = 1.0 then the simulation will attempt to fix all joint error during the next time step.
However, setting ERP = 1.0 is not recommended, as the joint error will not be completely fixed due to various internal approximations.
A value of ERP = 0.1 to 0.8 is recommended.

  """

  ...

def setERPContact(erp2: float) -> None:

  """

  Sets the Error Reduction Parameter (ERP) for contact constraints.
The Error Reduction Parameter (ERP) specifies what proportion of the joint error will be fixed during the next simulation step.
If ERP = 0.0 then no correcting force is applied and the bodies will eventually drift apart as the simulation proceeds.
If ERP = 1.0 then the simulation will attempt to fix all joint error during the next time step.
However, setting ERP = 1.0 is not recommended, as the joint error will not be completely fixed due to various internal approximations.
A value of ERP = 0.1 to 0.8 is recommended.

  """

  ...

def setCFM(cfm: float) -> None:

  """

  Sets the Constraint Force Mixing (CFM) for soft constraints.
If the Constraint Force Mixing (CFM) is set to zero, the constraint will be hard.
If CFM is set to a positive value, it will be possible to violate the constraint by pushing on it (for example, for contact constraints by forcing the two contacting objects together).
In other words the constraint will be soft, and the softness will increase as CFM increases.

  """

  ...

def setDebugMode(mode: int) -> None:

  """

  Sets the debug mode.

  """

  ...

def setGravity(x: float, y: float, z: float) -> None:

  """

  Sets the gravity force.

  Sets the linear air damping for rigidbodies.

  """

  ...

def setNumIterations(numiter: int) -> None:

  """

  Sets the number of iterations for an iterative constraint solver.

  """

  ...

def setNumTimeSubSteps(numsubstep: int) -> None:

  """

  Sets the number of substeps for each physics proceed. Tradeoff quality for performance.

  """

  ...

def setSolverDamping(damping: float) -> None:

  """

  Note: Very experimental, not recommended

  Sets the damper constant of a penalty based solver.

  """

  ...

def setSolverTau(tau: float) -> None:

  """

  Note: Very experimental, not recommended

  Sets the spring constant of a penalty based solver.

  """

  ...

def setSolverType(solverType: int) -> None:

  """

  Note: Very experimental, not recommended

  Sets the solver type.

  """

  ...

def setSorConstant(sor: float) -> None:

  """

  Note: Very experimental, not recommended

  Sets the successive overrelaxation constant.

  """

  ...

error: str = ...

"""

Symbolic constant string that indicates error.

"""

DBG_NODEBUG: int = ...

"""

No debug.

"""

DBG_DRAWWIREFRAME: int = ...

"""

Draw wireframe in debug.

"""

DBG_DRAWAABB: int = ...

"""

Draw Axis Aligned Bounding Box in debug.

"""

DBG_DRAWFREATURESTEXT: int = ...

"""

Draw features text in debug.

"""

DBG_DRAWCONTACTPOINTS: int = ...

"""

Draw contact points in debug.

"""

DBG_NOHELPTEXT: int = ...

"""

Debug without help text.

"""

DBG_DRAWTEXT: int = ...

"""

Draw text in debug.

"""

DBG_PROFILETIMINGS: int = ...

"""

Draw profile timings in debug.

"""

DBG_ENABLESATCOMPARISION: int = ...

"""

Enable sat comparison in debug.

"""

DBG_DISABLEBULLETLCP: int = ...

"""

Disable Bullet LCP.

"""

DBG_ENABLECCD: int = ...

"""

Enable Continuous Collision Detection in debug.

"""

DBG_DRAWCONSTRAINTS: int = ...

"""

Draw constraints in debug.

"""

DBG_DRAWCONSTRAINTLIMITS: int = ...

"""

Draw constraint limits in debug.

"""

DBG_FASTWIREFRAME: int = ...

"""

Draw a fast wireframe in debug.

"""

POINTTOPOINT_CONSTRAINT: int = ...

""""""

LINEHINGE_CONSTRAINT: int = ...

""""""

ANGULAR_CONSTRAINT: int = ...

""""""

CONETWIST_CONSTRAINT: int = ...

""""""

VEHICLE_CONSTRAINT: int = ...

""""""

GENERIC_6DOF_CONSTRAINT: int = ...

""""""
