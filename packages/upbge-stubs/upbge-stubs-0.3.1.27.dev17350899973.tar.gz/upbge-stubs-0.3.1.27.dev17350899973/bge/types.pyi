"""


Game Types (bge.types)
**********************


Introduction
============

This module contains the classes that appear as instances in the Game Engine. A
script must interact with these classes if it is to affect the behaviour of
objects in a game.

The following example would move an object (i.e. an instance of
:class:`~bge.types.KX_GameObject`) one unit up.

.. code:: python

  # bge.types.SCA_PythonController
  cont = bge.logic.getCurrentController()

  # bge.types.KX_GameObject
  obj = cont.owner
  obj.worldPosition.z += 1

To run the code, it could be placed in a Blender text block and executed with
a :class:`~bge.types.SCA_PythonController` logic brick.


Types
=====

"""

import typing

import mathutils

import logging

import gpu

import bpy

import aud

class BL_ArmatureBone:

  """

  Proxy to Blender bone structure. All fields are read-only and comply to RNA names.
All space attribute correspond to the rest pose.

  """

  name: str = ...

  """

  bone name.

  """

  connected: bool = ...

  """

  true when the bone head is struck to the parent's tail.

  """

  hinge: bool = ...

  """

  true when bone doesn't inherit rotation or scale from parent bone.

  """

  inherit_scale: bool = ...

  """

  true when bone inherits scaling from parent bone.

  """

  bbone_segments: int = ...

  """

  number of B-bone segments.

  """

  roll: float = ...

  """

  bone rotation around head-tail axis.

  """

  head: mathutils.Vector = ...

  """

  location of head end of the bone in parent bone space.

  """

  tail: mathutils.Vector = ...

  """

  location of head end of the bone in parent bone space.

  """

  length: float = ...

  """

  bone length.

  """

  arm_head: mathutils.Vector = ...

  """

  location of head end of the bone in armature space.

  """

  arm_tail: mathutils.Vector = ...

  """

  location of tail end of the bone in armature space.

  """

  arm_mat: mathutils.Matrix = ...

  """

  matrix of the bone head in armature space.

  Note: This matrix has no scale part.

  """

  bone_mat: mathutils.Matrix = ...

  """

  rotation matrix of the bone in parent bone space.

  """

  parent: BL_ArmatureBone = ...

  """

  parent bone, or None for root bone.

  """

  children: typing.List[BL_ArmatureBone] = ...

  """

  list of bone's children.

  """

class BL_ArmatureChannel:

  """

  Proxy to armature pose channel. Allows to read and set armature pose.
The attributes are identical to RNA attributes, but mostly in read-only mode.

  """

  name: str = ...

  """

  channel name (=bone name), read-only.

  """

  bone: BL_ArmatureBone = ...

  """

  return the bone object corresponding to this pose channel, read-only.

  """

  parent: BL_ArmatureChannel = ...

  """

  return the parent channel object, None if root channel, read-only.

  """

  has_ik: bool = ...

  """

  true if the bone is part of an active IK chain, read-only.
This flag is not set when an IK constraint is defined but not enabled (miss target information for example).

  """

  ik_dof_x: bool = ...

  """

  true if the bone is free to rotation in the X axis, read-only.

  """

  ik_dof_y: bool = ...

  """

  true if the bone is free to rotation in the Y axis, read-only.

  """

  ik_dof_z: bool = ...

  """

  true if the bone is free to rotation in the Z axis, read-only.

  """

  ik_limit_x: bool = ...

  """

  true if a limit is imposed on X rotation, read-only.

  """

  ik_limit_y: bool = ...

  """

  true if a limit is imposed on Y rotation, read-only.

  """

  ik_limit_z: bool = ...

  """

  true if a limit is imposed on Z rotation, read-only.

  """

  ik_rot_control: bool = ...

  """

  true if channel rotation should applied as IK constraint, read-only.

  """

  ik_lin_control: bool = ...

  """

  true if channel size should applied as IK constraint, read-only.

  """

  location: mathutils.Vector = ...

  """

  displacement of the bone head in armature local space, read-write.

  Note: You can only move a bone if it is unconnected to its parent. An action playing on the armature may change the value. An IK chain does not update this value, see joint_rotation.

  Note: Changing this field has no immediate effect, the pose is updated when the armature is updated during the graphic render (see :data:`BL_ArmatureObject.update <bge.types.BL_ArmatureObject.update>`).

  """

  scale: mathutils.Vector = ...

  """

  scale of the bone relative to its parent, read-write.

  Note: An action playing on the armature may change the value.  An IK chain does not update this value, see joint_rotation.

  Note: Changing this field has no immediate effect, the pose is updated when the armature is updated during the graphic render (see :data:`BL_ArmatureObject.update <bge.types.BL_ArmatureObject.update>`)

  """

  rotation_quaternion: mathutils.Vector = ...

  """

  rotation of the bone relative to its parent expressed as a quaternion, read-write.

  Note: This field is only used if rotation_mode is 0. An action playing on the armature may change the value.  An IK chain does not update this value, see joint_rotation.

  Note: Changing this field has no immediate effect, the pose is updated when the armature is updated during the graphic render (see :data:`BL_ArmatureObject.update <bge.types.BL_ArmatureObject.update>`)

  """

  rotation_euler: mathutils.Vector = ...

  """

  rotation of the bone relative to its parent expressed as a set of euler angles, read-write.

  Note: This field is only used if rotation_mode is > 0. You must always pass the angles in [X, Y, Z] order; the order of applying the angles to the bone depends on rotation_mode. An action playing on the armature may change this field.  An IK chain does not update this value, see joint_rotation.

  Note: Changing this field has no immediate effect, the pose is updated when the armature is updated during the graphic render (see :data:`BL_ArmatureObject.update <bge.types.BL_ArmatureObject.update>`)

  """

  rotation_mode: int = ...

  """

  Method of updating the bone rotation, read-write.

  """

  channel_matrix: mathutils.Matrix = ...

  """

  pose matrix in bone space (deformation of the bone due to action, constraint, etc), Read-only.
This field is updated after the graphic render, it represents the current pose.

  """

  pose_matrix: mathutils.Matrix = ...

  """

  pose matrix in armature space, read-only,
This field is updated after the graphic render, it represents the current pose.

  """

  pose_head: mathutils.Vector = ...

  """

  position of bone head in armature space, read-only.

  """

  pose_tail: mathutils.Vector = ...

  """

  position of bone tail in armature space, read-only.

  """

  ik_min_x: float = ...

  """

  minimum value of X rotation in degree (<= 0) when X rotation is limited (see ik_limit_x), read-only.

  """

  ik_max_x: float = ...

  """

  maximum value of X rotation in degree (>= 0) when X rotation is limited (see ik_limit_x), read-only.

  """

  ik_min_y: float = ...

  """

  minimum value of Y rotation in degree (<= 0) when Y rotation is limited (see ik_limit_y), read-only.

  """

  ik_max_y: float = ...

  """

  maximum value of Y rotation in degree (>= 0) when Y rotation is limited (see ik_limit_y), read-only.

  """

  ik_min_z: float = ...

  """

  minimum value of Z rotation in degree (<= 0) when Z rotation is limited (see ik_limit_z), read-only.

  """

  ik_max_z: float = ...

  """

  maximum value of Z rotation in degree (>= 0) when Z rotation is limited (see ik_limit_z), read-only.

  """

  ik_stiffness_x: float = ...

  """

  bone rotation stiffness in X axis, read-only.

  """

  ik_stiffness_y: float = ...

  """

  bone rotation stiffness in Y axis, read-only.

  """

  ik_stiffness_z: float = ...

  """

  bone rotation stiffness in Z axis, read-only.

  """

  ik_stretch: float = ...

  """

  ratio of scale change that is allowed, 0=bone can't change size, read-only.

  """

  ik_rot_weight: float = ...

  """

  weight of rotation constraint when ik_rot_control is set, read-write.

  """

  ik_lin_weight: float = ...

  """

  weight of size constraint when ik_lin_control is set, read-write.

  """

  joint_rotation: mathutils.Vector = ...

  """

  Control bone rotation in term of joint angle (for robotic applications), read-write.

  When writing to this attribute, you pass a [x, y, z] vector and an appropriate set of euler angles or quaternion is calculated according to the rotation_mode.

  When you read this attribute, the current pose matrix is converted into a [x, y, z] vector representing the joint angles.

  The value and the meaning of the x, y, z depends on the ik_dof_x/ik_dof_y/ik_dof_z attributes:

  * 1DoF joint X, Y or Z: the corresponding x, y, or z value is used an a joint angle in radiant

  * 2DoF joint X+Y or Z+Y: treated as 2 successive 1DoF joints: first X or Z, then Y. The x or z value is used as a joint angle in radiant along the X or Z axis, followed by a rotation along the new Y axis of y radiants.

  * 2DoF joint X+Z: treated as a 2DoF joint with rotation axis on the X/Z plane. The x and z values are used as the coordinates of the rotation vector in the X/Z plane.

  * 3DoF joint X+Y+Z: treated as a revolute joint. The [x, y, z] vector represents the equivalent rotation vector to bring the joint from the rest pose to the new pose.

  Note: The bone must be part of an IK chain if you want to set the ik_dof_x/ik_dof_y/ik_dof_z attributes via the UI, but this will interfere with this attribute since the IK solver will overwrite the pose. You can stay in control of the armature if you create an IK constraint but do not finalize it (e.g. don't set a target) the IK solver will not run but the IK panel will show up on the UI for each bone in the chain.

  Note: [0, 0, 0] always corresponds to the rest pose.

  Note: You must request the armature pose to update and wait for the next graphic frame to see the effect of setting this attribute (see :data:`BL_ArmatureObject.update <bge.types.BL_ArmatureObject.update>`).

  Note: You can read the result of the calculation in rotation or euler_rotation attributes after setting this attribute.

  """

class BL_ArmatureConstraint:

  """

  Proxy to Armature Constraint. Allows to change constraint on the fly.
Obtained through :class:`~bge.types.BL_ArmatureObject`.constraints.

  Note: Not all armature constraints are supported in the GE.

  """

  type: int = ...

  """

  Type of constraint, (read-only).

  Use one of ::`these constants<armatureconstraint-constants-type>`.

  """

  name: str = ...

  """

  Name of constraint constructed as <bone_name>:<constraint_name>. constraints list.

  This name is also the key subscript on :class:`~bge.types.BL_ArmatureObject`.

  """

  enforce: float = ...

  """

  fraction of constraint effect that is enforced. Between 0 and 1.

  """

  headtail: float = ...

  """

  Position of target between head and tail of the target bone: 0=head, 1=tail.

  Note: Only used if the target is a bone (i.e target object is an armature.

  """

  lin_error: float = ...

  """

  runtime linear error (in Blender units) on constraint at the current frame.

  This is a runtime value updated on each frame by the IK solver. Only available on IK constraint and iTaSC solver.

  """

  rot_error: float = ...

  """

  Runtime rotation error (in radiant) on constraint at the current frame.

  This is a runtime value updated on each frame by the IK solver. Only available on IK constraint and iTaSC solver.

  It is only set if the constraint has a rotation part, for example, a CopyPose+Rotation IK constraint.

  """

  target: KX_GameObject = ...

  """

  Primary target object for the constraint. The position of this object in the GE will be used as target for the constraint.

  """

  subtarget: KX_GameObject = ...

  """

  Secondary target object for the constraint. The position of this object in the GE will be used as secondary target for the constraint.

  Currently this is only used for pole target on IK constraint.

  """

  active: bool = ...

  """

  True if the constraint is active.

  Note: An inactive constraint does not update lin_error and rot_error.

  """

  ik_weight: float = ...

  """

  Weight of the IK constraint between 0 and 1.

  Only defined for IK constraint.

  """

  ik_type: int = ...

  """

  Type of IK constraint, (read-only).

  Use one of ::`these constants<armatureconstraint-constants-ik-type>`.

  """

  ik_flag: int = ...

  """

  Combination of IK constraint option flags, read-only.

  Use one of ::`these constants<armatureconstraint-constants-ik-flag>`.

  """

  ik_dist: float = ...

  """

  Distance the constraint is trying to maintain with target, only used when ik_type=CONSTRAINT_IK_DISTANCE.

  """

  ik_mode: int = ...

  """

  Use one of ::`these constants<armatureconstraint-constants-ik-mode>`.

  Additional mode for IK constraint. Currently only used for Distance constraint:

  """

class BL_ArmatureObject:

  """

  An armature object.

  """

  constraints: typing.List[BL_ArmatureConstraint] = ...

  """

  The list of armature constraint defined on this armature.
Elements of the list can be accessed by index or string.
The key format for string access is '<bone_name>:<constraint_name>'.

  """

  channels: typing.List[BL_ArmatureChannel] = ...

  """

  The list of armature channels.
Elements of the list can be accessed by index or name the bone.

  """

  def update(self) -> None:

    """

    Ensures that the armature will be updated on next graphic frame.

    This action is unnecessary if a KX_ArmatureActuator with mode run is active
or if an action is playing. Use this function in other cases. It must be called
on each frame to ensure that the armature is updated continuously.

    """

    ...

  def draw(self) -> None:

    """

    Draw lines that represent armature to view it in real time.

    """

    ...

class BL_Shader:

  """

  BL_Shader is a class used to compile and use custom shaders scripts.
This header set the ``#version`` directive, so the user must not define his own *#version*.
Since 0.3.0, this class is only used with custom 2D filters.

  Deprecated since version 0.3.0: The list of python callbacks executed when the shader is used to render an object.
All the functions can expect as argument the object currently rendered.

  .. code:: python

    def callback(object):
        print("render object %r" % object.name)

  Deprecated since version 0.3.0: The list of python callbacks executed when the shader is begin used to render.

  :type:            
    list of functions and/or methods

  Deprecated since version 0.3.0: Clear the shader. Use this method before the source is changed with :data:`setSource`.

  Deprecated since version 0.3.0: Set attribute location. (The parameter is ignored a.t.m. and the value of "tangent" is always used.)

  :arg enum:        
    attribute location value

  :type enum:       
    integer

  Deprecated since version 0.3.0: Set the vertex and fragment programs

  :arg vertexProgram:
    Vertex program

  :type vertexProgram:
    string

  :arg fragmentProgram:
    Fragment program

  :type fragmentProgram:
    string

  :arg apply:       
    Enable the shader.

  :type apply:      
    boolean

  Deprecated since version 0.3.0: Set the vertex, fragment and geometry shader programs.

  :arg sources:     
    Dictionary of all programs. The keys :data:`vertex`, :data:`fragment` and :data:`geometry` represent shader programs of the same name.
:data:`geometry` is an optional program.
This dictionary can be similar to:

    .. code:: python

      sources = {
          "vertex" : vertexProgram,
          "fragment" : fragmentProgram,
          "geometry" : geometryProgram
      }

  :type sources:    
    dict

  :arg apply:       
    Enable the shader.

  :type apply:      
    boolean

  Deprecated since version 0.3.0: Set a uniform with a float value that reflects the eye being render in stereo mode:
0.0 for the left eye, 0.5 for the right eye. In non stereo mode, the value of the uniform
is fixed to 0.0. The typical use of this uniform is in stereo mode to sample stereo textures
containing the left and right eye images in a top-bottom order.

  :arg name:        
    the uniform name

  :type name:       
    string

  """

  enabled: bool = ...

  """

  Set shader enabled to use.

  """

  objectCallbacks: typing.Any = ...

  bindCallbacks: typing.Any = ...

  def setUniformfv(self, name: str, fList: typing.List[float]) -> None:

    """

    Set a uniform with a list of float values

    """

    ...

  def delSource(self) -> None:

    ...

  def getFragmentProg(self) -> str:

    """

    Returns the fragment program.

    """

    ...

  def getVertexProg(self) -> str:

    """

    Get the vertex program.

    """

    ...

  def isValid(self) -> bool:

    """

    Check if the shader is valid.

    """

    ...

  def setAttrib(self, enum: typing.Any) -> None:

    ...

  def setSampler(self, name: str, index: int) -> None:

    """

    Set uniform texture sample index.

    """

    ...

  def setSource(self, vertexProgram: typing.Any, fragmentProgram: typing.Any, apply: typing.Any) -> None:

    ...

  def setSourceList(self, sources: typing.Any, apply: typing.Any) -> None:

    ...

  def setUniform1f(self, name: str, fx: float) -> None:

    """

    Set a uniform with 1 float value.

    """

    ...

  def setUniform1i(self, name: str, ix: int) -> None:

    """

    Set a uniform with an integer value.

    """

    ...

  def setUniform2f(self, name: str, fx: float, fy: float) -> None:

    """

    Set a uniform with 2 float values

    """

    ...

  def setUniform2i(self, name: str, ix: int, iy: int) -> None:

    """

    Set a uniform with 2 integer values

    """

    ...

  def setUniform3f(self, name: str, fx: float, fy: float, fz: float) -> None:

    """

    Set a uniform with 3 float values.

    """

    ...

  def setUniform3i(self, name: str, ix: int, iy: int, iz: int) -> None:

    """

    Set a uniform with 3 integer values

    """

    ...

  def setUniform4f(self, name: str, fx: float, fy: float, fz: float, fw: float) -> None:

    """

    Set a uniform with 4 float values.

    """

    ...

  def setUniform4i(self, name: str, ix: int, iy: int, iz: int, iw: int) -> None:

    """

    Set a uniform with 4 integer values

    """

    ...

  def setUniformDef(self, name: str, type: int) -> None:

    """

    Define a new uniform

    """

    ...

  def setUniformMatrix3(self, name: str, mat: mathutils.Matrix, transpose: bool) -> None:

    """

    Set a uniform with a 3x3 matrix value

    """

    ...

  def setUniformMatrix4(self, name: str, mat: mathutils.Matrix, transpose: bool) -> None:

    """

    Set a uniform with a 4x4 matrix value

    """

    ...

  def setUniformiv(self, name: str, iList: typing.List[int]) -> None:

    """

    Set a uniform with a list of integer values

    """

    ...

  def setUniformEyef(self, name: typing.Any) -> None:

    ...

  def validate(self) -> None:

    """

    Validate the shader object.

    """

    ...

class BL_Texture:

  """

  This is kept for backward compatibility with some scripts (bindCode mainly).

  """

  bindCode: int = ...

  """

  Texture bind code/Id/number.

  """

class EXP_ListValue:

  """

  This is a list like object used in the game engine internally that behaves similar to a python list in most ways.

  As well as the normal index lookup (``val= clist[i]``), EXP_ListValue supports string lookups (``val= scene.objects["Cube"]``)

  Other operations such as ``len(clist)``, ``list(clist)``, ``clist[0:10]`` are also supported.

  """

  def append(self, val: typing.Any) -> None:

    """

    Add an item to the list (like pythons append)

    Warning: Appending values to the list can cause crashes when the list is used internally by the game engine.

    """

    ...

  def count(self, val: typing.Any) -> int:

    """

    Count the number of instances of a value in the list.

    """

    ...

  def index(self, val: typing.Any) -> int:

    """

    Return the index of a value in the list.

    """

    ...

  def reverse(self) -> None:

    """

    Reverse the order of the list.

    """

    ...

  def get(self, key: typing.Any, default: typing.Any = None) -> None:

    """

    Return the value matching key, or the default value if its not found.

    """

    ...

  def filter(self, name: typing.Any, prop: typing.Any) -> None:

    """

    Return a list of items with name matching *name* regex and with a property matching *prop* regex.
If *name* is empty every items are checked, if *prop* is empty no property check is proceeded.

    """

    ...

  def from_id(self, id: typing.Any) -> None:

    """

    This is a function especially for the game engine to return a value with a specific id.

    Since object names are not always unique, the id of an object can be used to get an object from the CValueList.

    Example:

    .. code:: python

      myObID=id(gameObject)
      ob= scene.objects.from_id(myObID)

    Where ``myObID`` is an int or long from the id function.

    This has the advantage that you can store the id in places you could not store a gameObject.

    Warning: The id is derived from a memory location and will be different each time the game engine starts.

    Warning: The id can't be stored as an integer in game object properties, as those only have a limited range that the id may not be contained in. Instead an id can be stored as a string game property and converted back to an integer for use in from_id lookups.

    """

    ...

class EXP_PropValue:

  """

  This class has no python functions

  """

  ...

class EXP_PyObjectPlus:

  """

  EXP_PyObjectPlus base class of most other types in the Game Engine.

  """

  invalid: bool = ...

  """

  Test if the object has been freed by the game engine and is no longer valid.

  Normally this is not a problem but when storing game engine data in the GameLogic module,
KX_Scenes or other KX_GameObjects its possible to hold a reference to invalid data.
Calling an attribute or method on an invalid object will raise a SystemError.

  The invalid attribute allows testing for this case without exception handling.

  """

class EXP_Value:

  """

  This class is a basis for other classes.

  """

  name: str = ...

  """

  The name of this EXP_Value derived object (read-only).

  """

class KX_2DFilter:

  """

  2D filter shader object. Can be alternated with :class:`~bge.types.BL_Shader`'s functions.

  Note: Since version 0.5+, the following builtin uniforms are available via the UBO ``g_data`` (type ``bgl_Data``):

      ``g_data.width``
        Rendered texture width (float)

      ``g_data.height``
        Rendered texture height (float)

      ``g_data.coo_offset[9]``
        Texture coordinate offsets for 3x3 filters (vec4[9])

    The following builtin samplers are available:

      ``bgl_RenderedTexture``
        RENDERED_TEXTURE_UNIFORM

      ``bgl_DepthTexture``
        DEPTH_TEXTURE_UNIFORM

    The following builtin attributes are available:

      ``bgl_TexCoord``
        texture coordinates / UV

      ``fragColor``
        returned result of 2D filter

  """

  ...

class KX_2DFilterFrameBuffer:

  """

  2D filter custom off screen (framebuffer in 0.3+).

  """

  width: int = ...

  """

  The off screen width, always canvas width in 0.3+ (read-only).

  """

  height: int = ...

  """

  The off screen height, always canvas height in 0.3+ (read-only).

  """

  def getColorTexture(self) -> gpu.types.GPUTexture:

    ...

  def getDepthTexture(self) -> gpu.types.GPUTexture:

    ...

class KX_2DFilterManager:

  """

  2D filter manager used to add, remove and find filters in a scene.

  """

  def addFilter(self, index: int, type: int, fragmentProgram: str) -> KX_2DFilter:

    """

    Add a filter to the pass index :data:`index`, type :data:`type` and fragment program if custom filter.

    """

    ...

  def removeFilter(self, index: int) -> None:

    """

    Remove filter to the pass index :data:`index`.

    """

    ...

  def getFilter(self, index: int) -> KX_2DFilter:

    """

    Return filter to the pass index :data:`index`.

    """

    ...

class KX_BlenderMaterial:

  """

  This is kept for backward compatibility with some scripts.

  """

  textures: typing.List[typing.Any] = ...

  """

  List of all material's textures (read only).

  """

class KX_Camera:

  """

  A Camera object.

  """

  INSIDE: typing.Any = ...

  """

  See :data:`sphereInsideFrustum` and :data:`boxInsideFrustum`

  """

  INTERSECT: typing.Any = ...

  """

  See :data:`sphereInsideFrustum` and :data:`boxInsideFrustum`

  """

  OUTSIDE: typing.Any = ...

  """

  See :data:`sphereInsideFrustum` and :data:`boxInsideFrustum`

  """

  lens: float = ...

  """

  The camera's lens value.

  """

  lodDistanceFactor: float = ...

  """

  The factor to multiply distance to camera to adjust levels of detail.
A float < 1.0f will make the distance to camera used to compute
levels of detail decrease.

  """

  fov: float = ...

  """

  The camera's field of view value.

  """

  ortho_scale: float = ...

  """

  The camera's view scale when in orthographic mode.

  """

  near: float = ...

  """

  The camera's near clip distance.

  """

  far: float = ...

  """

  The camera's far clip distance.

  """

  shift_x: float = ...

  """

  The camera's horizontal shift.

  """

  shift_y: float = ...

  """

  The camera's vertical shift.

  """

  perspective: bool = ...

  """

  True if this camera has a perspective transform, False for an orthographic projection.

  """

  projection_matrix: mathutils.Matrix = ...

  """

  This camera's 4x4 projection matrix.

  Note: This is the identity matrix prior to rendering the first frame (any Python done on frame 1).

  """

  modelview_matrix: mathutils.Matrix = ...

  """

  This camera's 4x4 model view matrix. (read-only).

  Note: This matrix is regenerated every frame from the camera's position and orientation. Also, this is the identity matrix prior to rendering the first frame (any Python done on frame 1).

  """

  camera_to_world: mathutils.Matrix = ...

  """

  This camera's camera to world transform. (read-only).

  Note: This matrix is regenerated every frame from the camera's position and orientation.

  """

  world_to_camera: mathutils.Matrix = ...

  """

  This camera's world to camera transform. (read-only).

  Note: Regenerated every frame from the camera's position and orientation.

  Note: This is camera_to_world inverted.

  """

  useViewport: bool = ...

  """

  True when the camera is used as a viewport, set True to enable a viewport for this camera.

  """

  activityCulling: bool = ...

  """

  True if this camera is used to compute object distance for object activity culling.

  """

  def sphereInsideFrustum(self, centre: typing.List[typing.Any], radius: float) -> int:

    """

    Tests the given sphere against the view frustum.

    Note: When the camera is first initialized the result will be invalid because the projection matrix has not been set.

    .. code:: python

      from bge import logic
      cont = logic.getCurrentController()
      cam = cont.owner

      # A sphere of radius 4.0 located at [x, y, z] = [1.0, 1.0, 1.0]
      if (cam.sphereInsideFrustum([1.0, 1.0, 1.0], 4) != cam.OUTSIDE):
          # Sphere is inside frustum !
          # Do something useful !
      else:
          # Sphere is outside frustum

    """

    ...

  def boxInsideFrustum(self, box: typing.List[typing.List[typing.Any]]) -> None:

    """

    Tests the given box against the view frustum.

    Note: When the camera is first initialized the result will be invalid because the projection matrix has not been set.

    .. code:: python

      from bge import logic
      cont = logic.getCurrentController()
      cam = cont.owner

      # Box to test...
      box = []
      box.append([-1.0, -1.0, -1.0])
      box.append([-1.0, -1.0,  1.0])
      box.append([-1.0,  1.0, -1.0])
      box.append([-1.0,  1.0,  1.0])
      box.append([ 1.0, -1.0, -1.0])
      box.append([ 1.0, -1.0,  1.0])
      box.append([ 1.0,  1.0, -1.0])
      box.append([ 1.0,  1.0,  1.0])

      if (cam.boxInsideFrustum(box) != cam.OUTSIDE):
        # Box is inside/intersects frustum !
        # Do something useful !
      else:
        # Box is outside the frustum !

    """

    ...

  def pointInsideFrustum(self, point: mathutils.Vector) -> bool:

    """

    Tests the given point against the view frustum.

    Note: When the camera is first initialized the result will be invalid because the projection matrix has not been set.

    .. code:: python

      from bge import logic
      cont = logic.getCurrentController()
      cam = cont.owner

      # Test point [0.0, 0.0, 0.0]
      if (cam.pointInsideFrustum([0.0, 0.0, 0.0])):
        # Point is inside frustum !
        # Do something useful !
      else:
        # Box is outside the frustum !

    """

    ...

  def getCameraToWorld(self) -> mathutils.Matrix:

    """

    Returns the camera-to-world transform.

    """

    ...

  def getWorldToCamera(self) -> mathutils.Matrix:

    """

    Returns the world-to-camera transform.

    This returns the inverse matrix of getCameraToWorld().

    """

    ...

  def setOnTop(self) -> None:

    """

    Set this cameras viewport ontop of all other viewport.

    """

    ...

  def setViewport(self, left: int, bottom: int, right: int, top: int) -> None:

    """

    Sets the region of this viewport on the screen in pixels.

    Use :data:`bge.render.getWindowHeight` and :data:`bge.render.getWindowWidth` to calculate values relative to the entire display.

    .. code:: python

      import bge

      scene = bge.logic.getCurrentScene()

      cam1 = scene.objects["cam1"]
      cam2 = scene.objects["cam2"]

      cam1.useViewport = True
      cam2.useViewport = True

      width = bge.render.getWindowWidth()
      height = bge.render.getWindowHeight()

      # Try to do a vertical split of the view (setViewport(left, bottom, right, top))
      cam1.setViewport(0, 0, int(width / 2), height)
      cam2.setViewport(int(width / 2), 0, width, height)

    """

    ...

  def getScreenPosition(self, object: KX_GameObject) -> typing.List[typing.Any]:

    """

    Gets the position of an object projected on screen space.

    .. code:: python

      # For an object in the middle of the screen, coord = [0.5, 0.5]
      coord = camera.getScreenPosition(object)

    """

    ...

  def getScreenVect(self, x: float, y: float) -> mathutils.Vector:

    """

    Gets the vector from the camera position in the screen coordinate direction.

    .. code:: python

      # Gets the vector of the camera front direction:
      m_vect = camera.getScreenVect(0.5, 0.5)

    """

    ...

  def getScreenRay(self, x: float, y: float, dist: float = inf, property: str = None) -> KX_GameObject:

    """

    Look towards a screen coordinate (x, y) and find first object hit within dist that matches prop.
The ray is similar to KX_GameObject->rayCastTo.

    .. code:: python

      # Gets an object with a property "wall" in front of the camera within a distance of 100:
      target = camera.getScreenRay(0.5, 0.5, 100, "wall")

    """

    ...

class KX_CharacterWrapper:

  """

  A wrapper to expose character physics options.

  """

  onGround: bool = ...

  """

  Whether or not the character is on the ground. (read-only)

  """

  gravity: mathutils.Vector = ...

  """

  The gravity vector used for the character.

  """

  fallSpeed: float = ...

  """

  The character falling speed.

  """

  maxJumps: int = ...

  """

  The maximum number of jumps a character can perform before having to touch the ground. By default this is set to 1. 2 allows for a double jump, etc.

  """

  jumpCount: int = ...

  """

  The current jump count. This can be used to have different logic for a single jump versus a double jump. For example, a different animation for the second jump.

  """

  jumpSpeed: float = ...

  """

  The character jumping speed.

  """

  maxSlope: float = ...

  """

  The maximum slope which the character can climb.

  """

  walkDirection: mathutils.Vector = ...

  """

  The speed and direction the character is traveling in using world coordinates. This should be used instead of applyMovement() to properly move the character.

  """

  def jump(self) -> None:

    """

    The character jumps based on it's jump speed.

    """

    ...

  def setVelocity(self, velocity: mathutils.Vector, time: float, local: bool = False) -> None:

    """

    Sets the character's linear velocity for a given period.

    This method sets character's velocity through it's center of mass during a period.

    """

    ...

  def reset(self) -> None:

    """

    Resets the character velocity and walk direction.

    """

    ...

class KX_CollisionContactPoint:

  """

  A collision contact point passed to the collision callbacks.

  .. code:: python

    import bge

    def oncollision(object, point, normal, points):
        print("Hit by", object)
        for point in points:
            print(point.localPointA)
            print(point.localPointB)
            print(point.worldPoint)
            print(point.normal)
            print(point.combinedFriction)
            print(point.combinedRestitution)
            print(point.appliedImpulse)

    cont = bge.logic.getCurrentController()
    own = cont.owner
    own.collisionCallbacks = [oncollision]

  """

  localPointA: mathutils.Vector = ...

  """

  The contact point in the owner object space.

  """

  localPointB: mathutils.Vector = ...

  """

  The contact point in the collider object space.

  """

  worldPoint: mathutils.Vector = ...

  """

  The contact point in world space.

  """

  normal: mathutils.Vector = ...

  """

  The contact normal in owner object space.

  """

  combinedFriction: float = ...

  """

  The combined friction of the owner and collider object.

  """

  combinedRollingFriction: float = ...

  """

  The combined rolling friction of the owner and collider object.

  """

  combinedRestitution: float = ...

  """

  The combined restitution of the owner and collider object.

  """

  appliedImpulse: float = ...

  """

  The applied impulse to the owner object.

  """

class KX_ConstraintWrapper:

  """

  KX_ConstraintWrapper

  """

  def getConstraintId(self, val: typing.Any) -> int:

    """

    Returns the constraint ID

    """

    ...

  def setParam(self, axis: int, value0: typing.Any, value1: typing.Any) -> None:

    """

    Set the constraint limits

    Note: * Lowerlimit == Upperlimit -> axis is locked

      * Lowerlimit > Upperlimit -> axis is free

      * Lowerlimit < Upperlimit -> axis it limited in that range

    For PHY_LINEHINGE_CONSTRAINT = 2 or PHY_ANGULAR_CONSTRAINT = 3:

    axis = 3 is a constraint limit, with low/high limit value
      * 3: X axis angle

    :arg value0 (min):
      Set the minimum limit of the axis

    :type value0:     
      float

    :arg value1 (max):
      Set the maximum limit of the axis

    :type value1:     
      float

    For PHY_CONE_TWIST_CONSTRAINT = 4:

    axis = 3..5 are constraint limits, high limit values
      * 3: X axis angle

      * 4: Y axis angle

      * 5: Z axis angle

    :arg value0 (min):
      Set the minimum limit of the axis

    :type value0:     
      float

    :arg value1 (max):
      Set the maximum limit of the axis

    :type value1:     
      float

    For PHY_GENERIC_6DOF_CONSTRAINT = 12:

    axis = 0..2 are constraint limits, with low/high limit value
      * 0: X axis position

      * 1: Y axis position

      * 2: Z axis position

    axis = 3..5 are relative constraint (Euler) angles in radians
      * 3: X axis angle

      * 4: Y axis angle

      * 5: Z axis angle

    :arg value0 (min):
      Set the minimum limit of the axis

    :type value0:     
      float

    :arg value1 (max):
      Set the maximum limit of the axis

    :type value1:     
      float

    axis = 6..8 are translational motors, with value0=target velocity, value1 = max motor force
      * 6: X axis position

      * 7: Y axis position

      * 8: Z axis position

    axis = 9..11 are rotational motors, with value0=target velocity, value1 = max motor force
      * 9: X axis angle

      * 10: Y axis angle

      * 11: Z axis angle

    :arg value0 (speed):
      Set the linear velocity of the axis

    :type value0:     
      float Range: -10,000.00 to 10,000.00

    :arg value1 (force):
      Set the maximum force limit of the axis

    :type value1:     
      float Range: -10,000.00 to 10,000.00

    axis = 12..14 are for linear springs on each of the position of freedom
      * 12: X axis position

      * 13: Y axis position

      * 14: Z axis position

    axis = 15..17 are for angular springs on each of the angle of freedom in radians
      * 15: X axis angle

      * 16: Y axis angle

      * 17: Z axis angle

    :arg value0 (stiffness):
      Set the stiffness of the spring

    :type value0:     
      float

    :arg value1 (damping):
      Tendency of the spring to return to it's original position

    :type value1:     
      float
1.0 = springs back to original position (no damping)
0.0 = don't springs back

    """

    ...

  def getParam(self, axis: int) -> None:

    """

    Get the constraint position or euler angle of a generic 6DOF constraint

    axis = 0..2 are linear constraint values
      * 0: X axis position

      * 1: Y axis position

      * 2: Z axis position

    :return:          
      position

    :rtype:           
      float

    axis = 3..5 are relative constraint (Euler) angles in radians
      * 3: X axis angle

      * 4: Y axis angle

      * 5: Z axis angle

    :return:          
      angle

    :rtype:           
      float

    """

    ...

  constraint_id: int = ...

  """

  Returns the constraint ID  (read only)

  """

  constraint_type: typing.Union[bge.constraints.POINTTOPOINT_CONSTRAINT, bge.constraints.LINEHINGE_CONSTRAINT, bge.constraints.ANGULAR_CONSTRAINT, bge.constraints.CONETWIST_CONSTRAINT, bge.constraints.VEHICLE_CONSTRAINT, bge.constraints.GENERIC_6DOF_CONSTRAINT] = ...

  """

  Returns the constraint type (read only)

  """

  breakingThreshold: float = ...

  """

  The impulse threshold breaking the constraint, if the constraint is broken :data:`enabled` is set to *False*.

  """

  enabled: bool = ...

  """

  The status of the constraint. Set to *True* to restore a constraint after breaking.

  """

class KX_FontObject:

  """

  A Font game object.

  It is possible to use attributes from :type: :class:`~bpy.types.TextCurve`

  .. code:: python

    import bge

    # Use bge module to get/set game property + transform
    font_object = (bge.logic.getCurrentController()).owner
    font_object["Text"] = "Text Example"
    font_object.worldPosition = [-2.5, 1.0, 0.0]

    # Use bpy.types.TextCurve attributes to set other text settings
    font_object_text = font_object.blenderObject.data
    font_object_text.size = 1
    font_object_text.resolution_u = 4
    font_object_text.align_x = "LEFT"

  """

  ...

class KX_GameObject:

  """

  All game objects are derived from this class.

  Properties assigned to game objects are accessible as attributes of this class.

  Note: Calling ANY method or attribute on an object that has been removed from a scene will raise a SystemError,
if an object may have been removed since last accessing it use the :attr:`~bge.types.EXP_PyObjectPlus.invalid` attribute to check.

  KX_GameObject can be subclassed to extend functionality. For example:

  .. code:: python

    import bge

    class CustomGameObject(bge.types.KX_GameObject):
        RATE = 0.05

        def __init__(self, old_owner):
            # "old_owner" can just be ignored. At this point, "self" is
            # already the object in the scene, and "old_owner" has been
            # destroyed.

            # New attributes can be defined - but we could also use a game
            # property, like "self['rate']".
            self.rate = CustomGameObject.RATE

        def update(self):
            self.worldPosition.z += self.rate

            # switch direction
            if self.worldPosition.z > 1.0:
                self.rate = -CustomGameObject.RATE
            elif self.worldPosition.z < 0.0:
                self.rate = CustomGameObject.RATE

    # Called first
    def mutate(cont):
        old_object = cont.owner
        mutated_object = CustomGameObject(cont.owner)

        # After calling the constructor above, references to the old object
        # should not be used.
        assert(old_object is not mutated_object)
        assert(old_object.invalid)
        assert(mutated_object is cont.owner)

    # Called later - note we are now working with the mutated object.
    def update(cont):
        cont.owner.update()

  When subclassing objects other than empties and meshes, the specific type
should be used - e.g. inherit from :class:`~bge.types.BL_ArmatureObject` when the object
to mutate is an armature.

  Deprecated since version 0.3.0: The layer mask used for shadow and real-time cube map render.

  Deprecated since version 0.3.0: (You can use bpy.types.Object.bound_box instead) The object's bounding volume box used for culling.

  :type:            
    :class:`~bge.types.KX_BoundingBox`

  Deprecated since version 0.3.0: Returns True if the object is culled, else False.

  Warning: This variable returns an invalid value if it is called outside the scene's callbacks :attr:`KX_Scene.pre_draw <~bge.types.KX_Scene.pre_draw>` and :attr:`KX_Scene.post_draw <~bge.types.KX_Scene.post_draw>`.

  :type:            
    boolean (read only)

  Deprecated since version 0.3.0: occlusion capability flag.

  :type:            
    boolean

  Deprecated since version 0.3.0: The object batch group containing the batched mesh.

  :type:            
    :class:`~bge.types.KX_BatchGroup`

  Deprecated since version 0.3.0: Sets the game object's occlusion capability.

  :arg occlusion:   
    the state to set the occlusion to.

  :type occlusion:  
    boolean

  :arg recursive:   
    optional argument to set all childrens visibility flag too, defaults to False if no value passed.

  :type recursive:  
    boolean

  Deprecated since version 0.0.0: Gets the game object's reaction force.The reaction force is the force applied to this object over the last simulation timestep.
This also includes impulses, eg from collisions.

  :return:          
    the reaction force of this object.

  :rtype:           
    Vector((fx, fy, fz))

  Note: This is not implemented at the moment. (Removed when switching from Sumo to Bullet)

  """

  name: str = ...

  """

  The object's name.

  """

  mass: float = ...

  """

  The object's mass

  Note: The object must have a physics controller for the mass to be applied, otherwise the mass value will be returned as 0.0.

  """

  friction: float = ...

  """

  The object's friction

  Note: The object must have a physics controller for the friction to be applied, otherwise the friction value will be returned as 0.0.

  """

  isSuspendDynamics: bool = ...

  """

  The object's dynamic state (read-only).

  :meth:`suspendDynamics` and :meth:`restoreDynamics` allow you to change the state.

  """

  linearDamping: float = ...

  """

  The object's linear damping, also known as translational damping. Can be set simultaneously with angular damping using the :meth:`setDamping` method.

  Note: The object must have a physics controller for the linear damping to be applied, otherwise the value will be returned as 0.0.

  """

  angularDamping: float = ...

  """

  The object's angular damping, also known as rotationation damping. Can be set simultaneously with linear damping using the :meth:`setDamping` method.

  Note: The object must have a physics controller for the angular damping to be applied, otherwise the value will be returned as 0.0.

  """

  linVelocityMin: float = ...

  """

  Enforces the object keeps moving at a minimum velocity.

  Note: Applies to dynamic and rigid body objects only.

  Note: A value of 0.0 disables this option.

  Note: While objects are stationary the minimum velocity will not be applied.

  """

  linVelocityMax: float = ...

  """

  Clamp the maximum linear velocity to prevent objects moving beyond a set speed.

  Note: Applies to dynamic and rigid body objects only.

  Note: A value of 0.0 disables this option (rather than setting it stationary).

  """

  angularVelocityMin: float = ...

  """

  Enforces the object keeps rotating at a minimum velocity. A value of 0.0 disables this.

  Note: Applies to dynamic and rigid body objects only.
While objects are stationary the minimum velocity will not be applied.

  """

  angularVelocityMax: float = ...

  """

  Clamp the maximum angular velocity to prevent objects rotating beyond a set speed.
A value of 0.0 disables clamping; it does not stop rotation.

  Note: Applies to dynamic and rigid body objects only.

  """

  localInertia: mathutils.Vector = ...

  """

  the object's inertia vector in local coordinates. Read only.

  """

  parent: KX_GameObject = ...

  """

  The object's parent object. (read-only).

  """

  groupMembers: typing.Union[typing.Sequence[KX_GameObject], typing.Mapping[str, KX_GameObject], EXP_ListValue] = ...

  """

  Returns the list of group members if the object is a group object (dupli group instance), otherwise None is returned.

  """

  groupObject: KX_GameObject = ...

  """

  Returns the group object (dupli group instance) that the object belongs to or None if the object is not part of a group.

  """

  collisionGroup: int = ...

  """

  The object's collision group.

  """

  collisionMask: int = ...

  """

  The object's collision mask.

  """

  collisionCallbacks: typing.List[typing.Callable] = ...

  """

  A list of functions to be called when a collision occurs.

  Callbacks should either accept one argument *(object)*, or four
arguments *(object, point, normal, points)*. For simplicity, per
colliding object the first collision point is reported in second
and third argument.

  .. code:: python

    # Function form
    def callback_four(object, point, normal, points):
        print('Hit by %r with %i contacts points' % (object.name, len(points)))

    def callback_three(object, point, normal):
        print('Hit by %r at %s with normal %s' % (object.name, point, normal))

    def callback_one(object):
        print('Hit by %r' % object.name)

    def register_callback(controller):
        controller.owner.collisionCallbacks.append(callback_four)
        controller.owner.collisionCallbacks.append(callback_three)
        controller.owner.collisionCallbacks.append(callback_one)


    # Method form
    class YourGameEntity(bge.types.KX_GameObject):
        def __init__(self, old_owner):
            self.collisionCallbacks.append(self.on_collision_four)
            self.collisionCallbacks.append(self.on_collision_three)
            self.collisionCallbacks.append(self.on_collision_one)

        def on_collision_four(self, object, point, normal, points):
            print('Hit by %r with %i contacts points' % (object.name, len(points)))

        def on_collision_three(self, object, point, normal):
            print('Hit by %r at %s with normal %s' % (object.name, point, normal))

        def on_collision_one(self, object):
            print('Hit by %r' % object.name)

  Note: For backward compatibility, a callback with variable number of
arguments (using **args*) will be passed only the *object*
argument. Only when there is more than one fixed argument (not
counting *self* for methods) will the four-argument form be
used.

  """

  scene: KX_Scene = ...

  """

  The object's scene. (read-only).

  """

  visible: bool = ...

  """

  visibility flag.

  Note: Game logic will still run for invisible objects.

  """

  layer: typing.Any = ...

  cullingBox: typing.Any = ...

  culled: typing.Any = ...

  color: mathutils.Vector = ...

  """

  The object color of the object. [r, g, b, a]

  """

  physicsCulling: bool = ...

  """

  True if the object suspends its physics depending on its nearest distance to any camera.

  """

  logicCulling: bool = ...

  """

  True if the object suspends its logic and animation depending on its nearest distance to any camera.

  """

  physicsCullingRadius: float = ...

  """

  Suspend object's physics if this radius is smaller than its nearest distance to any camera
and :data:`physicsCulling` set to *True*.

  """

  logicCullingRadius: float = ...

  """

  Suspend object's logic and animation if this radius is smaller than its nearest distance to any camera
and :data:`logicCulling` set to *True*.

  """

  occlusion: typing.Any = ...

  position: mathutils.Vector = ...

  """

  The object's position. [x, y, z] On write: local position, on read: world position

  Deprecated since version 0.0.1: Use :attr:`localPosition` and :attr:`worldPosition`.

  """

  orientation: mathutils.Matrix = ...

  """

  The object's orientation. 3x3 Matrix. You can also write a Quaternion or Euler vector. On write: local orientation, on read: world orientation

  Deprecated since version 0.0.1: Use :attr:`localOrientation` and :attr:`worldOrientation`.

  """

  scaling: mathutils.Vector = ...

  """

  The object's scaling factor. [sx, sy, sz] On write: local scaling, on read: world scaling

  Deprecated since version 0.0.1: Use :attr:`localScale` and :attr:`worldScale`.

  """

  localOrientation: mathutils.Matrix = ...

  """

  The object's local orientation. 3x3 Matrix. You can also write a Quaternion or Euler vector.

  """

  worldOrientation: mathutils.Matrix = ...

  """

  The object's world orientation. 3x3 Matrix.

  """

  localScale: mathutils.Vector = ...

  """

  The object's local scaling factor. [sx, sy, sz]

  """

  worldScale: mathutils.Vector = ...

  """

  The object's world scaling factor. [sx, sy, sz]

  """

  localPosition: mathutils.Vector = ...

  """

  The object's local position. [x, y, z]

  """

  worldPosition: mathutils.Vector = ...

  """

  The object's world position. [x, y, z]

  """

  localTransform: mathutils.Matrix = ...

  """

  The object's local space transform matrix. 4x4 Matrix.

  """

  worldTransform: mathutils.Matrix = ...

  """

  The object's world space transform matrix. 4x4 Matrix.

  """

  localLinearVelocity: mathutils.Vector = ...

  """

  The object's local linear velocity. [x, y, z]

  """

  worldLinearVelocity: mathutils.Vector = ...

  """

  The object's world linear velocity. [x, y, z]

  """

  localAngularVelocity: mathutils.Vector = ...

  """

  The object's local angular velocity. [x, y, z]

  """

  worldAngularVelocity: mathutils.Vector = ...

  """

  The object's world angular velocity. [x, y, z]

  """

  gravity: mathutils.Vector = ...

  """

  The object's gravity. [x, y, z]

  """

  timeOffset: float = ...

  """

  adjust the slowparent delay at runtime.

  """

  blenderObject: bpy.types.Object = ...

  """

  This KX_GameObject's Object.

  """

  state: int = ...

  """

  the game object's state bitmask, using the first 30 bits, one bit must always be set.

  """

  meshes: typing.List[KX_MeshProxy] = ...

  """

  a list meshes for this object.

  Note: Most objects use only 1 mesh.

  Note: Changes to this list will not update the KX_GameObject.

  """

  batchGroup: typing.Any = ...

  sensors: typing.List[typing.Any] = ...

  """

  a sequence of :class:`~bge.types.SCA_ISensor` objects with string/index lookups and iterator support.

  Note: This attribute is experimental and may be removed (but probably wont be).

  Note: Changes to this list will not update the KX_GameObject.

  """

  controllers: typing.List[SCA_ISensor] = ...

  """

  a sequence of :class:`~bge.types.SCA_IController` objects with string/index lookups and iterator support.

  Note: This attribute is experimental and may be removed (but probably wont be).

  Note: Changes to this list will not update the KX_GameObject.

  """

  actuators: typing.List[typing.Any] = ...

  """

  a list of :class:`~bge.types.SCA_IActuator` with string/index lookups and iterator support.

  Note: This attribute is experimental and may be removed (but probably wont be).

  Note: Changes to this list will not update the KX_GameObject.

  """

  attrDict: typing.Dict[str, typing.Any] = ...

  """

  get the objects internal python attribute dictionary for direct (faster) access.

  """

  components: typing.Union[typing.Sequence[KX_PythonComponent], typing.Mapping[str, KX_PythonComponent], EXP_ListValue] = ...

  """

  All python components.

  """

  children: typing.Union[typing.Sequence[KX_GameObject], typing.Mapping[str, KX_GameObject], EXP_ListValue] = ...

  """

  direct children of this object, (read-only).

  """

  childrenRecursive: typing.Union[typing.Sequence[KX_GameObject], typing.Mapping[str, KX_GameObject], EXP_ListValue] = ...

  """

  all children of this object including children's children, (read-only).

  """

  life: float = ...

  """

  The number of frames until the object ends, assumes one frame is 1/60 second (read-only).

  """

  debug: bool = ...

  """

  If true, the object's debug properties will be displayed on screen.

  """

  debugRecursive: bool = ...

  """

  If true, the object's and children's debug properties will be displayed on screen.

  """

  currentLodLevel: int = ...

  """

  The index of the level of detail (LOD) currently used by this object (read-only).

  """

  lodManager: KX_LodManager = ...

  """

  Return the lod manager of this object.
Needed to access to lod manager to set attributes of levels of detail of this object.
The lod manager is shared between instance objects and can be changed to use the lod levels of an other object.
If the lod manager is set to *None* the object's mesh backs to the mesh of the previous first lod level.

  """

  onRemove: typing.List[typing.Any] = ...

  """

  A list of callables to run when the KX_GameObject is destroyed.

  .. code:: python

    @gameobj.onRemove.append
    def callback(gameobj):
       print('exiting %s...' % gameobj.name)

  or

  .. code:: python

    cont = bge.logic.getCurrentController()
    gameobj = cont.owner

    def callback():
       print('exiting' %s...' % gameobj.name)

    gameobj.onRemove.append(callback)

  """

  @property

  def logger(self) -> logging.Logger:

    """

    A logger instance that can be used to log messages related to this object (read-only).

    """

    ...

  @property

  def loggerName(self) -> str:

    """

    A name used to create the logger instance. By default, it takes the form *Type[Name]*
and can be optionally overridden as below:

    .. code:: python

      @property
      def loggerName():
         return "MyObject"

    """

    ...

  def endObject(self) -> None:

    """

    Delete this object, can be used in place of the EndObject Actuator.

    The actual removal of the object from the scene is delayed.

    """

    ...

  def replaceMesh(self, mesh: typing.Union[KX_MeshProxy, str], useDisplayMesh: bool = True, usePhysicsMesh: bool = False) -> None:

    """

    Replace the mesh of this object with a new mesh. This works the same was as the actuator.

    """

    ...

  def setVisible(self, visible: bool, recursive: bool = None) -> None:

    """

    Sets the game object's visible flag.

    """

    ...

  def setOcclusion(self, occlusion: typing.Any, recursive: typing.Any = None) -> None:

    ...

  def alignAxisToVect(self, vect: mathutils.Vector, axis: int = 2, factor: float = 1.0) -> None:

    """

    Aligns any of the game object's axis along the given vector.

    """

    ...

  def getAxisVect(self, vect: mathutils.Vector) -> typing.Any:

    """

    Returns the axis vector rotates by the object's worldspace orientation.
This is the equivalent of multiplying the vector by the orientation matrix.

    """

    ...

  def applyMovement(self, movement: mathutils.Vector, local: typing.Any = None) -> None:

    """

    Sets the game object's movement.

    """

    ...

  def applyRotation(self, rotation: mathutils.Vector, local: typing.Any = None) -> None:

    """

    Sets the game object's rotation.

    """

    ...

  def applyForce(self, force: mathutils.Vector, local: bool = None) -> None:

    """

    Sets the game object's force.

    This requires a dynamic object.

    """

    ...

  def applyTorque(self, torque: mathutils.Vector, local: bool = None) -> None:

    """

    Sets the game object's torque.

    This requires a dynamic object.

    """

    ...

  def getLinearVelocity(self, local: bool = None) -> mathutils.Vector:

    """

    Gets the game object's linear velocity.

    This method returns the game object's velocity through it's center of mass, ie no angular velocity component.

    """

    ...

  def setLinearVelocity(self, velocity: mathutils.Vector, local: bool = None) -> None:

    """

    Sets the game object's linear velocity.

    This method sets game object's velocity through it's center of mass,
ie no angular velocity component.

    This requires a dynamic object.

    """

    ...

  def getAngularVelocity(self, local: bool = None) -> mathutils.Vector:

    """

    Gets the game object's angular velocity.

    """

    ...

  def setAngularVelocity(self, velocity: bool, local: typing.Any = None) -> None:

    """

    Sets the game object's angular velocity.

    This requires a dynamic object.

    """

    ...

  def getVelocity(self, point: mathutils.Vector = None) -> mathutils.Vector:

    """

    Gets the game object's velocity at the specified point.

    Gets the game object's velocity at the specified point, including angular
components.

    """

    ...

  def getReactionForce(self) -> None:

    ...

  def applyImpulse(self, point: typing.Any, impulse: mathutils.Vector, local: bool = None) -> None:

    """

    Applies an impulse to the game object.

    This will apply the specified impulse to the game object at the specified point.
If point != position, applyImpulse will also change the object's angular momentum.
Otherwise, only linear momentum will change.

    """

    ...

  def setDamping(self, linear_damping: float, angular_damping: float) -> None:

    """

    Sets both the :attr:`linearDamping` and :attr:`angularDamping` simultaneously. This is more efficient than setting both properties individually.

    """

    ...

  def suspendPhysics(self, freeConstraints: bool = None) -> None:

    """

    Suspends physics for this object.

    """

    ...

  def restorePhysics(self) -> None:

    """

    Resumes physics for this object. Also reinstates collisions.

    """

    ...

  def suspendDynamics(self, ghost: bool = None) -> None:

    """

    Suspends dynamics physics for this object.

    :attr:`isSuspendDynamics` allows you to inspect whether the object is in a suspended state.

    """

    ...

  def restoreDynamics(self) -> None:

    """

    Resumes dynamics physics for this object. Also reinstates collisions; the object will no longer be a ghost.

    Note: The objects linear velocity will be applied from when the dynamics were suspended.

    """

    ...

  def enableRigidBody(self) -> None:

    """

    Enables rigid body physics for this object.

    Rigid body physics allows the object to roll on collisions.

    """

    ...

  def disableRigidBody(self) -> None:

    """

    Disables rigid body physics for this object.

    """

    ...

  def setCcdMotionThreshold(self, ccd_motion_threshold: float) -> None:

    """

    Sets :attr:`ccdMotionThreshold` that is the delta of movement that has to happen in one physics tick to trigger the continuous motion detection.

    Note: Setting the motion threshold to 0.0 deactive the Collision Continuous Detection (CCD).

    """

    ...

  def setCcdSweptSphereRadius(self, ccd_swept_sphere_radius: float) -> None:

    """

    Sets :attr:`ccdSweptSphereRadius` that is the radius of the sphere that is used to check for possible collisions when ccd is activated.

    """

    ...

  def setParent(self, parent: KX_GameObject, compound: bool = True, ghost: bool = True) -> None:

    """

    Sets this object's parent.
Control the shape status with the optional compound and ghost parameters:

    In that case you can control if it should be ghost or not:

    Note: If the object type is sensor, it stays ghost regardless of ghost parameter

    """

    ...

  def removeParent(self) -> None:

    """

    Removes this objects parent.

    """

    ...

  def getPhysicsId(self) -> None:

    """

    Returns the user data object associated with this game object's physics controller.

    """

    ...

  def getPropertyNames(self) -> typing.List[typing.Any]:

    """

    Gets a list of all property names.

    """

    ...

  def getDistanceTo(self, other: typing.Union[KX_GameObject, typing.List[typing.Any]]) -> float:

    ...

  def getVectTo(self, other: typing.Union[KX_GameObject, typing.List[typing.Any]]) -> typing.Any:

    """

    Returns the vector and the distance to another object or point.
The vector is normalized unless the distance is 0, in which a zero length vector is returned.

    """

    ...

  def rayCastTo(self, other: KX_GameObject, dist: float = 0, prop: str = '') -> KX_GameObject:

    """

    Look towards another point/object and find first object hit within dist that matches prop.

    The ray is always casted from the center of the object, ignoring the object itself.
The ray is casted towards the center of another object or an explicit [x, y, z] point.
Use rayCast() if you need to retrieve the hit point

    """

    ...

  def rayCast(self, objto: KX_GameObject, objfrom: KX_GameObject = None, dist: float = 0, prop: str = '', face: int = False, xray: int = False, poly: int = 0, mask: int = 65535) -> typing.Any:

    """

    Look from a point/object to another point/object and find first object hit within dist that matches prop.
if poly is 0, returns a 3-tuple with object reference, hit point and hit normal or (None, None, None) if no hit.
if poly is 1, returns a 4-tuple with in addition a :class:`~bge.types.KX_PolyProxy` as 4th element.
if poly is 2, returns a 5-tuple with in addition a 2D vector with the UV mapping of the hit point as 5th element.

    .. code:: python

      # shoot along the axis gun-gunAim (gunAim should be collision-free)
      obj, point, normal = gun.rayCast(gunAim, None, 50)
      if obj:
         # do something
         pass

    The face parameter determines the orientation of the normal.

    * 0 => hit normal is always oriented towards the ray origin (as if you casted the ray from outside)

    * 1 => hit normal is the real face normal (only for mesh object, otherwise face has no effect)

    The ray has X-Ray capability if xray parameter is 1, otherwise the first object hit (other than self object) stops the ray.
The prop and xray parameters interact as follow.

    * prop off, xray off: return closest hit or no hit if there is no object on the full extend of the ray.

    * prop off, xray on : idem.

    * prop on, xray off: return closest hit if it matches prop, no hit otherwise.

    * prop on, xray on : return closest hit matching prop or no hit if there is no object matching prop on the full extend of the ray.

    The :class:`~bge.types.KX_PolyProxy` 4th element of the return tuple when poly=1 allows to retrieve information on the polygon hit by the ray.
If there is no hit or the hit object is not a static mesh, None is returned as 4th element.

    The ray ignores collision-free objects and faces that dont have the collision flag enabled, you can however use ghost objects.

    Note: The ray ignores the object on which the method is called. It is casted from/to object center or explicit [x, y, z] points.

    """

    ...

  def collide(self, obj: typing.Union[str, KX_GameObject]) -> typing.Any:

    """

    Test if this object collides object :data:`obj`.

    """

    ...

  def setCollisionMargin(self, margin: float) -> None:

    """

    Set the objects collision margin.

    Note: If this object has no physics controller (a physics ID of zero), this function will raise RuntimeError.

    """

    ...

  def sendMessage(self, subject: str, body: str = '', to: str = '') -> None:

    """

    Sends a message.

    """

    ...

  def reinstancePhysicsMesh(self, gameObject: str, meshObject: str, dupli: bool, evaluated: bool) -> bool:

    """

    Updates the physics system with the changed mesh.

    If no arguments are given the physics mesh will be re-created from the first mesh assigned to the game object.

    Note: If this object has instances the other instances will be updated too.

    Note: The gameObject argument has an advantage that it can convert from a mesh with modifiers applied (such as the Subdivision Surface modifier).

    Warning: Only triangle mesh type objects are supported currently (not convex hull)

    Warning: If the object is a part of a compound object it will fail (parent or child)

    Warning: Rebuilding the physics mesh can be slow, running many times per second will give a performance hit.

    Warning: Duplicate the physics mesh can use much more memory, use this option only for duplicated meshes else use :meth:`replacePhysicsShape`.

    """

    ...

  def replacePhysicsShape(self, gameObject: str) -> bool:

    """

    Replace the current physics shape.

    Warning: Triangle mesh shapes are not supported.

    """

    ...

  def get(self, key: typing.Any, default: typing.Any = None) -> None:

    """

    Return the value matching key, or the default value if its not found.
:arg key: the matching key
:type key: string
:arg default: optional default value is the key isn't matching, defaults to None if no value passed.
:return: The key value or a default.

    """

    ...

  def playAction(self, name: str, start_frame: typing.Any, end_frame: typing.Any, layer: int = 0, priority: int = 0, blendin: float = 0, play_mode: int = KX_ACTION_MODE_PLAY, layer_weight: float = 0.0, ipo_flags: int = 0, speed: float = 1.0, blend_mode: int = KX_ACTION_BLEND_BLEND) -> None:

    """

    Plays an action.

    """

    ...

  def stopAction(self, layer: int = None) -> None:

    """

    Stop playing the action on the given layer.

    """

    ...

  def getActionFrame(self, layer: int = None) -> float:

    """

    Gets the current frame of the action playing in the supplied layer.

    """

    ...

  def getActionName(self, layer: int = None) -> str:

    """

    Gets the name of the current action playing in the supplied layer.

    """

    ...

  def setActionFrame(self, frame: float, layer: int = None) -> None:

    """

    Set the current frame of the action playing in the supplied layer.

    """

    ...

  def isPlayingAction(self, layer: int = None) -> bool:

    """

    Checks to see if there is an action playing in the given layer.

    """

    ...

  def addDebugProperty(self, name: str, debug: bool = None) -> None:

    """

    Adds a single debug property to the debug list.

    """

    ...

class KX_LibLoadStatus:

  """

  Libload is deprecated since 0.3+. An object providing information about a LibLoad() operation.

  .. code:: python

    # Print a message when an async LibLoad is done
    import bge

    def finished_cb(status):
        print("Library (%s) loaded in %.2fms." % (status.libraryName, status.timeTaken))

    bge.logic.LibLoad('myblend.blend', 'Scene', asynchronous=True).onFinish = finished_cb

  """

  onFinish: typing.Callable = ...

  """

  A callback that gets called when the lib load is done.

  """

  finished: bool = ...

  """

  The current status of the lib load.

  """

  progress: float = ...

  """

  The current progress of the lib load as a normalized value from 0.0 to 1.0.

  """

  libraryName: str = ...

  """

  The name of the library being loaded (the first argument to LibLoad).

  """

  timeTaken: float = ...

  """

  The amount of time, in seconds, the lib load took (0 until the operation is complete).

  """

class KX_LightObject:

  """

  A Light game object.

  It is possible to use attributes from :type: :class:`~bpy.types.Light`

  .. code:: python

    import bge

    # Use bge module to get/set game property + transform
    kxlight = (bge.logic.getCurrentController()).owner
    kxlight["Text"] = "Text Example"
    kxlight.worldPosition = [-2.5, 1.0, 0.0]

    # Use bpy.types.Light attributes to set other light settings
    lightData = kxlight.blenderObject.data
    lightData.energy = 1000.0
    lightData.color = [1.0, 0.0, 0.0]
    lightData.type = "POINT"

  """

  ...

class KX_LodLevel:

  """

  A single lod level for a game object lod manager.

  Deprecated since version 0.3.0: Return True if the lod level uses a different mesh than the original object mesh. (read only)

  Deprecated since version 0.3.0: Return True if the lod level uses a different material than the original object mesh material. (read only)

  :type:            
    boolean

  """

  mesh: KX_MeshProxy = ...

  """

  The mesh used for this lod level. (read only)

  """

  level: int = ...

  """

  The number of the lod level. (read only)

  """

  distance: float = ...

  """

  Distance to begin using this level of detail. (read only)

  """

  hysteresis: float = ...

  """

  Minimum distance factor change required to transition to the previous level of detail in percent. (read only)

  """

  useMesh: typing.Any = ...

  useMaterial: typing.Any = ...

  useHysteresis: bool = ...

  """

  Return true if the lod level uses hysteresis override. (read only)

  """

class KX_LodManager:

  """

  This class contains a list of all levels of detail used by a game object.

  """

  levels: typing.List[KX_LodLevel] = ...

  """

  Return the list of all levels of detail of the lod manager.

  """

  distanceFactor: float = ...

  """

  Method to multiply the distance to the camera.

  """

class KX_MeshProxy:

  """

  A mesh object.

  You can only read the vertex properties of a mesh object. In upbge 0.3+, KX_MeshProxy,
KX_PolyProxy, and KX_VertexProxy are only a representation of the physics shape as it was
when it was converted in BL_DataConversion.
Previously this kind of meshes were used both for render and physics, but since 0.3+,
it is only useful in limited cases. In most cases, bpy API should be used instead.

  Note:
The physics simulation doesn't currently update KX_Mesh/Poly/VertexProxy.

  1. Mesh Objects are converted from Blender at scene load.

  2. The Converter groups polygons by Material. A material holds:

     1. The texture.

     2. The Blender material.

     3. The Tile properties

     4. The face properties - (From the "Texture Face" panel)

     5. Transparency & z sorting

     6. Light layer

     7. Polygon shape (triangle/quad)

     8. Game Object

  3. Vertices will be split by face if necessary.  Vertices can only be shared between faces if:

     1. They are at the same position

     2. UV coordinates are the same

     3. Their normals are the same (both polygons are "Set Smooth")

     4. They are the same color, for example: a cube has 24 vertices: 6 faces with 4 vertices per face.

  The correct method of iterating over every :class:`~bge.types.KX_VertexProxy` in a game object

  .. code:: python

    from bge import logic

    cont = logic.getCurrentController()
    object = cont.owner

    for mesh in object.meshes:
       for m_index in range(len(mesh.materials)):
          for v_index in range(mesh.getVertexArrayLength(m_index)):
             vertex = mesh.getVertex(m_index, v_index)
             # Do something with vertex here...

  """

  materials: typing.List[KX_BlenderMaterial] = ...

  numPolygons: int = ...

  numMaterials: int = ...

  polygons: KX_PolyProxy = ...

  """

  Returns the list of polygons of this mesh.

  """

  def getMaterialName(self, matid: int) -> str:

    """

    Gets the name of the specified material.

    """

    ...

  def getTextureName(self, matid: int) -> str:

    """

    Gets the name of the specified material's texture.

    """

    ...

  def getVertexArrayLength(self, matid: int) -> int:

    """

    Gets the length of the vertex array associated with the specified material.

    There is one vertex array for each material.

    """

    ...

  def getVertex(self, matid: int, index: int) -> KX_VertexProxy:

    """

    Gets the specified vertex from the mesh object.

    """

    ...

  def getPolygon(self, index: int) -> KX_PolyProxy:

    """

    Gets the specified polygon from the mesh.

    """

    ...

class KX_NavMeshObject:

  """

  Python interface for using and controlling navigation meshes.

  """

  def findPath(self, start: typing.Any, goal: typing.Any) -> typing.List[typing.Any]:

    """

    Finds the path from start to goal points.

    """

    ...

  def raycast(self, start: typing.Any, goal: typing.Any) -> float:

    """

    Raycast from start to goal points.

    """

    ...

  def draw(self, mode: typing.Any) -> None:

    """

    Draws a debug mesh for the navigation mesh.

    """

    ...

  def rebuild(self) -> None:

    """

    Rebuild the navigation mesh.

    """

    ...

class KX_PolyProxy:

  """

  A polygon holds the index of the vertex forming the poylgon.
You can only read the vertex properties of a mesh object. In upbge 0.3+, KX_MeshProxy,
KX_PolyProxy, and KX_VertexProxy are only a representation of the physics shape as it was
when it was converted in BL_DataConversion.
Previously this kind of meshes were used both for render and physics, but since 0.3+,
it is only useful in limited cases. In most cases, bpy API should be used instead.

  Note:
The physics simulation doesn't currently update KX_Mesh/Poly/VertexProxy.

  """

  material_name: str = ...

  """

  The name of polygon material, empty if no material.

  """

  material: KX_BlenderMaterial = ...

  """

  The material of the polygon.

  """

  texture_name: str = ...

  """

  The texture name of the polygon.

  """

  material_id: int = ...

  """

  The material index of the polygon, use this to retrieve vertex proxy from mesh proxy.

  """

  v1: int = ...

  """

  vertex index of the first vertex of the polygon, use this to retrieve vertex proxy from mesh proxy.

  """

  v2: int = ...

  """

  vertex index of the second vertex of the polygon, use this to retrieve vertex proxy from mesh proxy.

  """

  v3: int = ...

  """

  vertex index of the third vertex of the polygon, use this to retrieve vertex proxy from mesh proxy.

  """

  v4: int = ...

  """

  Vertex index of the fourth vertex of the polygon, 0 if polygon has only 3 vertex
Use this to retrieve vertex proxy from mesh proxy.

  """

  visible: int = ...

  """

  visible state of the polygon: 1=visible, 0=invisible.

  """

  collide: int = ...

  """

  collide state of the polygon: 1=receives collision, 0=collision free.

  """

  vertices: KX_VertexProxy = ...

  """

  Returns the list of vertices of this polygon.

  """

  def getMaterialName(self) -> str:

    """

    Returns the polygon material name with MA prefix

    """

    ...

  def getMaterial(self) -> KX_BlenderMaterial:

    ...

  def getTextureName(self) -> str:

    ...

  def getMaterialIndex(self) -> int:

    """

    Returns the material bucket index of the polygon.
This index and the ones returned by getVertexIndex() are needed to retrieve the vertex proxy from :class:`~bge.types.KX_MeshProxy`.

    """

    ...

  def getNumVertex(self) -> int:

    """

    Returns the number of vertex of the polygon.

    """

    ...

  def isVisible(self) -> bool:

    """

    Returns whether the polygon is visible or not

    """

    ...

  def isCollider(self) -> int:

    """

    Returns whether the polygon is receives collision or not

    """

    ...

  def getVertexIndex(self, vertex: typing.Any) -> int:

    """

    Returns the mesh vertex index of a polygon vertex
This index and the one returned by getMaterialIndex() are needed to retrieve the vertex proxy from :class:`~bge.types.KX_MeshProxy`.

    """

    ...

  def getMesh(self) -> KX_MeshProxy:

    """

    Returns a mesh proxy

    """

    ...

class KX_PythonComponent:

  """

  Python component can be compared to python logic bricks with parameters.
The python component is a script loaded in the UI, this script defined a component class by inheriting from :class:`~bge.types.KX_PythonComponent`.
This class must contain a dictionary of properties: :attr:`args` and two default functions: :meth:`start` and :meth:`update`.

  The script must have .py extension.

  The component properties are loaded from the :attr:`args` attribute from the UI at loading time.
When the game start the function :meth:`start` is called with as arguments a dictionary of the properties' name and value.
The :meth:`update` function is called every frames during the logic stage before running logics bricks,
the goal of this function is to handle and process everything.

  The following component example moves and rotates the object when pressing the keys W, A, S and D.

  .. code:: python

    import bge
    from collections import OrderedDict

    class ThirdPerson(bge.types.KX_PythonComponent):
        \"\"\"Basic third person controls

        W: move forward
        A: turn left
        S: move backward
        D: turn right

        \"\"\"

        #

        args = OrderedDict([
            ("Move Speed", 0.1),
            ("Turn Speed", 0.04)
        ])

        def start(self, args):
            self.move_speed = args['Move Speed']
            self.turn_speed = args['Turn Speed']

        def update(self):
            keyboard = bge.logic.keyboard.events

            move = 0
            rotate = 0

            if keyboard[bge.events.WKEY]:
                move += self.move_speed
            if keyboard[bge.events.SKEY]:
                move -= self.move_speed

            if keyboard[bge.events.AKEY]:
                rotate += self.turn_speed
            if keyboard[bge.events.DKEY]:
                rotate -= self.turn_speed

            self.object.applyMovement((0, move, 0), True)
            self.object.applyRotation((0, 0, rotate), True)

  Since the components are loaded for the first time outside the bge, then :attr:`bge` is a fake module that contains only the class
:class:`~bge.types.KX_PythonComponent` to avoid importing all the bge modules.
This behavior is safer but creates some issues at loading when the user want to use functions or attributes from the bge modules other
than the :class:`~bge.types.KX_PythonComponent` class. The way is to not call these functions at loading outside the bge. To detect it, the bge
module contains the attribute :attr:`__component__` when it's imported outside the bge.

  The following component example add a "Cube" object at initialization and move it along x for each update. It shows that the user can
use functions from scene and load the component outside the bge by setting global attributes in a condition at the beginning of the
script.

  .. code:: python

    import bge

    if not hasattr(bge, "__component__"):
        global scene
        scene = bge.logic.getCurrentScene()

    class Component(bge.types.KX_PythonComponent):
        args = {}

        def start(self, args):
            scene.addObject("Cube")

        def update(self):
            scene.objects["Cube"].worldPosition.x += 0.1

  The property types supported are float, integer, boolean, string, set (for enumeration) and Vector 2D, 3D and 4D. The following example
show all of these property types.

  .. code:: python

    from bge import *
    from mathutils import *
    from collections import OrderedDict

    class Component(types.KX_PythonComponent):
         args = OrderedDict([
             ("Float", 58.6),
             ("Integer", 150),
             ("Boolean", True),
             ("String", "Cube"),
             ("Enum", {"Enum 1", "Enum 2", "Enum 3"}),
             ("Vector 2D", Vector((0.8, 0.7))),
             ("Vector 3D", Vector((0.4, 0.3, 0.1))),
             ("Vector 4D", Vector((0.5, 0.2, 0.9, 0.6)))
         ])

         def start(self, args):
             print(args)

         def update(self):
             pass

  """

  object: KX_GameObject = ...

  """

  The object owner of the component.

  """

  args: typing.Dict[str, typing.Any] = ...

  """

  Dictionary of the component properties, the keys are string and the value can be: float, integer, Vector(2D/3D/4D), set, string.

  """

  @property

  def logger(self) -> logging.Logger:

    """

    A logger instance that can be used to log messages related to this object (read-only).

    """

    ...

  @property

  def loggerName(self) -> str:

    """

    A name used to create the logger instance. By default, it takes the form *Type[Name]*
and can be optionally overridden as below:

    .. code:: python

      @property
      def loggerName():
         return "MyObject"

    """

    ...

  def start(self, args: typing.Dict[str, typing.Any]) -> None:

    """

    Initialize the component.

    Warning: This function must be inherited in the python component class.

    """

    ...

  def update(self) -> None:

    """

    Process the logic of the component.

    Warning: This function must be inherited in the python component class.

    """

    ...

  def dispose(self) -> None:

    """

    Function called when the component is destroyed.

    Warning: This function must be inherited in the python component class.

    """

    ...

class KX_Scene:

  """

  An active scene that gives access to objects, cameras, lights and scene attributes.

  The activity culling stuff is supposed to disable logic bricks when their owner gets too far
from the active camera.  It was taken from some code lurking at the back of KX_Scene - who knows
what it does!

  .. code:: python

    from bge import logic

    # get the scene
    scene = logic.getCurrentScene()

    # print all the objects in the scene
    for object in scene.objects:
       print(object.name)

    # get an object named 'Cube'
    object = scene.objects["Cube"]

    # get the first object in the scene.
    object = scene.objects[0]

  .. code:: python

    # Get the depth of an object in the camera view.
    from bge import logic

    object = logic.getCurrentController().owner
    cam = logic.getCurrentScene().active_camera

    # Depth is negative and decreasing further from the camera
    depth = object.position[0]*cam.world_to_camera[2][0] + object.position[1]*cam.world_to_camera[2][1] + object.position[2]*cam.world_to_camera[2][2] + cam.world_to_camera[2][3]

  @bug: All attributes are read only at the moment.

  Deprecated since version 0.3.0: The override camera used for scene culling, if set to None the culling is proceeded with the camera used to render.

  Deprecated since version 0.3.0: The current active world, (read-only).

  :type:            
    :class:`~bge.types.KX_WorldInfo`

  Deprecated since version 0.3.0: True if the scene is suspended, (read-only).

  :type:            
    boolean

  Deprecated since version 0.3.0: True when Dynamic Bounding box Volume Tree is set (read-only).

  :type:            
    boolean

  Deprecated since version 0.3.0: Suspends this scene.

  Deprecated since version 0.3.0: Resume this scene.

  """

  name: str = ...

  """

  The scene's name, (read-only).

  """

  objects: typing.Union[typing.Sequence[KX_GameObject], typing.Mapping[str, KX_GameObject], EXP_ListValue] = ...

  """

  A list of objects in the scene, (read-only).

  """

  objectsInactive: typing.Union[typing.Sequence[KX_GameObject], typing.Mapping[str, KX_GameObject], EXP_ListValue] = ...

  """

  A list of objects on background layers (used for the addObject actuator), (read-only).

  """

  lights: typing.Union[typing.Sequence[KX_LightObject], typing.Mapping[str, KX_LightObject], EXP_ListValue] = ...

  """

  A list of lights in the scene, (read-only).

  """

  cameras: typing.Union[typing.Sequence[KX_Camera], typing.Mapping[str, KX_Camera], EXP_ListValue] = ...

  """

  A list of cameras in the scene, (read-only).

  """

  texts: typing.Union[typing.Sequence[KX_FontObject], typing.Mapping[str, KX_FontObject], EXP_ListValue] = ...

  """

  A list of texts in the scene, (read-only).

  """

  active_camera: KX_Camera = ...

  """

  The current active camera.

  .. code:: python

    import bge

    own = bge.logic.getCurrentController().owner
    scene = own.scene

    scene.active_camera = scene.objects["Camera.001"]

  Note: This can be set directly from python to avoid using the :class:`~bge.types.KX_SceneActuator`.

  """

  overrideCullingCamera: typing.Any = ...

  world: typing.Any = ...

  filterManager: KX_2DFilterManager = ...

  """

  The scene's 2D filter manager, (read-only).

  """

  suspended: typing.Any = ...

  activityCulling: bool = ...

  """

  True if the scene allow object activity culling.

  """

  dbvt_culling: typing.Any = ...

  pre_draw: typing.List[typing.Any] = ...

  """

  A list of callables to be run before the render step. The callbacks can take as argument the rendered camera.

  """

  post_draw: typing.List[typing.Any] = ...

  """

  A list of callables to be run after the render step.

  """

  pre_draw_setup: typing.List[typing.Any] = ...

  """

  A list of callables to be run before the drawing setup (i.e., before the model view and projection matrices are computed).
The callbacks can take as argument the rendered camera, the camera could be temporary in case of stereo rendering.

  """

  onRemove: typing.List[typing.Any] = ...

  """

  A list of callables to run when the scene is destroyed.

  .. code:: python

    @scene.onRemove.append
    def callback(scene):
       print('exiting %s...' % scene.name)

  """

  gravity: mathutils.Vector = ...

  """

  The scene gravity using the world x, y and z axis.

  """

  @property

  def logger(self) -> logging.Logger:

    """

    A logger instance that can be used to log messages related to this object (read-only).

    """

    ...

  @property

  def loggerName(self) -> str:

    """

    A name used to create the logger instance. By default, it takes the form *KX_Scene[Name]*.

    """

    ...

  def addObject(self, object: typing.Union[KX_GameObject, str], reference: typing.Union[KX_GameObject, str], time: float = 0.0, dupli: bool = False) -> KX_GameObject:

    """

    Adds an object to the scene like the Add Object Actuator would.

    """

    ...

  def end(self) -> None:

    """

    Removes the scene from the game.

    """

    ...

  def restart(self) -> None:

    """

    Restarts the scene.

    """

    ...

  def replace(self, scene: str) -> bool:

    """

    Replaces this scene with another one.

    """

    ...

  def suspend(self) -> None:

    ...

  def resume(self) -> None:

    ...

  def get(self, key: typing.Any, default: typing.Any = None) -> None:

    """

    Return the value matching key, or the default value if its not found.
:return: The key value or a default.

    """

    ...

  def drawObstacleSimulation(self) -> None:

    """

    Draw debug visualization of obstacle simulation.

    """

    ...

  def convertBlenderObject(self, blenderObject: bpy.types.Object) -> KX_GameObject:

    """

    Converts a :class:`~bpy.types.Object` into a :class:`~bge.types.KX_GameObject` during runtime.
For example, you can append an Object from another .blend file during bge runtime
using: bpy.ops.wm.append(...) then convert this Object into a KX_GameObject to have
logic bricks, physics... converted. This is meant to replace libload.

    """

    ...

  def convertBlenderObjectsList(self, blenderObjectsList: typing.List[bpy.types.Object], asynchronous: bool) -> None:

    """

    Converts all bpy.types.Object inside a python List into its correspondent :class:`~bge.types.KX_GameObject` during runtime.
For example, you can append an Object List during bge runtime using: ob = object_data_add(...) and ML.append(ob) then convert the Objects
inside the List into several KX_GameObject to have logic bricks, physics... converted. This is meant to replace libload.
The conversion can be asynchronous or synchronous.

    """

    ...

  def convertBlenderCollection(self, blenderCollection: bpy.types.Collection, asynchronous: bool) -> None:

    """

    Converts all bpy.types.Object inside a Collection into its correspondent :class:`~bge.types.KX_GameObject` during runtime.
For example, you can append a Collection from another .blend file during bge runtime
using: bpy.ops.wm.append(...) then convert the Objects inside the Collection into several KX_GameObject to have
logic bricks, physics... converted. This is meant to replace libload. The conversion can be asynchronous
or synchronous.

    """

    ...

  def convertBlenderAction(self, Action: bpy.types.Action) -> None:

    """

    Registers a bpy.types.Action into the bge logic manager to be abled to play it during runtime.
For example, you can append an Action from another .blend file during bge runtime
using: bpy.ops.wm.append(...) then register this Action to be abled to play it.

    """

    ...

  def unregisterBlenderAction(self, Action: bpy.types.Action) -> None:

    """

    Unregisters a bpy.types.Action from the bge logic manager.
The unregistered action will still be in the .blend file
but can't be played anymore with bge. If you want to completely
remove the action you need to call bpy.data.actions.remove(Action, do_unlink=True)
after you unregistered it from bge logic manager.

    """

    ...

  def addOverlayCollection(self, kxCamera: KX_Camera, blenderCollection: bpy.types.Collection) -> None:

    """

    Adds an overlay collection (as with collection actuator) to render this collection objects
during a second render pass in overlay using the KX_Camera passed as argument.

    """

    ...

  def removeOverlayCollection(self, blenderCollection: bpy.types.Collection) -> None:

    """

    Removes an overlay collection (as with collection actuator).

    """

    ...

  def getGameObjectFromObject(self, blenderObject: bpy.types.Object) -> KX_GameObject:

    """

    Get the KX_GameObject corresponding to the blenderObject.

    """

    ...

class KX_VehicleWrapper:

  """

  KX_VehicleWrapper

  TODO - description

  """

  def addWheel(self, wheel: KX_GameObject, attachPos: mathutils.Vector, downDir: mathutils.Vector, axleDir: mathutils.Vector, suspensionRestLength: float, wheelRadius: float, hasSteering: bool) -> None:

    """

    Add a wheel to the vehicle

    """

    ...

  def applyBraking(self, force: float, wheelIndex: int) -> None:

    """

    Apply a braking force to the specified wheel

    """

    ...

  def applyEngineForce(self, force: float, wheelIndex: int) -> None:

    """

    Apply an engine force to the specified wheel

    """

    ...

  def getConstraintId(self) -> int:

    """

    Get the constraint ID

    """

    ...

  def getConstraintType(self) -> int:

    """

    Returns the constraint type.

    """

    ...

  def getNumWheels(self) -> int:

    """

    Returns the number of wheels.

    """

    ...

  def getWheelOrientationQuaternion(self, wheelIndex: int) -> typing.Any:

    """

    Returns the wheel orientation as a quaternion.

    """

    ...

  def getWheelPosition(self, wheelIndex: int) -> typing.Any:

    """

    Returns the position of the specified wheel

    """

    ...

  def getWheelRotation(self, wheelIndex: int) -> float:

    """

    Returns the rotation of the specified wheel

    """

    ...

  def setRollInfluence(self, rollInfluece: float, wheelIndex: int) -> None:

    """

    Set the specified wheel's roll influence.
The higher the roll influence the more the vehicle will tend to roll over in corners.

    """

    ...

  def setSteeringValue(self, steering: float, wheelIndex: int) -> None:

    """

    Set the specified wheel's steering

    """

    ...

  def setSuspensionCompression(self, compression: float, wheelIndex: int) -> None:

    """

    Set the specified wheel's compression

    """

    ...

  def setSuspensionDamping(self, damping: float, wheelIndex: int) -> None:

    """

    Set the specified wheel's damping

    """

    ...

  def setSuspensionStiffness(self, stiffness: float, wheelIndex: int) -> None:

    """

    Set the specified wheel's stiffness

    """

    ...

  def setTyreFriction(self, friction: float, wheelIndex: int) -> None:

    """

    Set the specified wheel's tyre friction

    """

    ...

  rayMask: typing.Any = ...

  """

  Set ray cast mask.

  """

class KX_VertexProxy:

  """

  A vertex holds position, UV, color and normal information.
You can only read the vertex properties of a mesh object. In upbge 0.3+, KX_MeshProxy,
KX_PolyProxy, and KX_VertexProxy are only a representation of the physics shape as it was
when it was converted in BL_DataConversion.
Previously this kind of meshes were used both for render and physics, but since 0.3+,
it is only useful in limited cases. In most cases, bpy API should be used instead.

  Note:
The physics simulation doesn't currently update KX_Mesh/Poly/VertexProxy.

  """

  XYZ: mathutils.Vector = ...

  """

  The position of the vertex.

  """

  UV: mathutils.Vector = ...

  """

  The texture coordinates of the vertex.

  """

  uvs: typing.List[typing.Any] = ...

  """

  The texture coordinates list of the vertex.

  """

  normal: mathutils.Vector = ...

  """

  The normal of the vertex.

  """

  color: mathutils.Vector = ...

  """

  The color of the vertex.

  Black = [0.0, 0.0, 0.0, 1.0], White = [1.0, 1.0, 1.0, 1.0]

  """

  colors: typing.List[typing.Any] = ...

  """

  The color list of the vertex.

  """

  x: float = ...

  """

  The x coordinate of the vertex.

  """

  y: float = ...

  """

  The y coordinate of the vertex.

  """

  z: float = ...

  """

  The z coordinate of the vertex.

  """

  u: float = ...

  """

  The u texture coordinate of the vertex.

  """

  v: float = ...

  """

  The v texture coordinate of the vertex.

  """

  u2: float = ...

  """

  The second u texture coordinate of the vertex.

  """

  v2: float = ...

  """

  The second v texture coordinate of the vertex.

  """

  r: float = ...

  """

  The red component of the vertex color. 0.0 <= r <= 1.0.

  """

  g: float = ...

  """

  The green component of the vertex color. 0.0 <= g <= 1.0.

  """

  b: float = ...

  """

  The blue component of the vertex color. 0.0 <= b <= 1.0.

  """

  a: float = ...

  """

  The alpha component of the vertex color. 0.0 <= a <= 1.0.

  """

  def getXYZ(self) -> mathutils.Vector:

    """

    Gets the position of this vertex.

    """

    ...

  def getUV(self) -> mathutils.Vector:

    """

    Gets the UV (texture) coordinates of this vertex.

    """

    ...

  def getUV2(self) -> mathutils.Vector:

    """

    Gets the 2nd UV (texture) coordinates of this vertex.

    """

    ...

  def getRGBA(self) -> int:

    """

    Gets the color of this vertex.

    The color is represented as four bytes packed into an integer value.  The color is
packed as RGBA.

    Since Python offers no way to get each byte without shifting, you must use the struct module to
access color in an machine independent way.

    Because of this, it is suggested you use the r, g, b and a attributes or the color attribute instead.

    .. code:: python

      import struct;
      col = struct.unpack('4B', struct.pack('I', v.getRGBA()))
      # col = (r, g, b, a)
      # black = (  0, 0, 0, 255)
      # white = (255, 255, 255, 255)

    """

    ...

  def getNormal(self) -> mathutils.Vector:

    """

    Gets the normal vector of this vertex.

    """

    ...

class SCA_2DFilterActuator:

  """

  Create, enable and disable 2D filters.

  The following properties don't have an immediate effect.
You must active the actuator to get the result.
The actuator is not persistent: it automatically stops itself after setting up the filter
but the filter remains active. To stop a filter you must activate the actuator with 'type'
set to :data:`~bge.logic.RAS_2DFILTER_DISABLED` or :data:`~bge.logic.RAS_2DFILTER_NOFILTER`.

  Deprecated since version 0.3.0: action on motion blur: 0=enable, 1=disable.

  Deprecated since version 0.3.0: argument for motion blur filter.

  :type:            
    float (0.0-100.0)

  """

  shaderText: str = ...

  """

  shader source code for custom shader.

  """

  disableMotionBlur: typing.Any = ...

  mode: int = ...

  """

  Type of 2D filter, use one of ::`these constants <Two-D-FilterActuator-mode>`.

  """

  passNumber: int = ...

  """

  order number of filter in the stack of 2D filters. Filters are executed in increasing order of passNb.

  Only be one filter can be defined per passNb.

  """

  value: typing.Any = ...

class SCA_ANDController:

  """

  An AND controller activates only when all linked sensors are activated.

  There are no special python methods for this controller.

  """

  ...

class SCA_ActionActuator:

  """

  Action Actuators apply an action to an actor.

  """

  action: str = ...

  """

  The name of the action to set as the current action.

  """

  frameStart: float = ...

  """

  Specifies the starting frame of the animation.

  """

  frameEnd: float = ...

  """

  Specifies the ending frame of the animation.

  """

  blendIn: float = ...

  """

  Specifies the number of frames of animation to generate when making transitions between actions.

  """

  priority: int = ...

  """

  Sets the priority of this actuator. Actuators will lower priority numbers will override actuators with higher numbers.

  """

  frame: float = ...

  """

  Sets the current frame for the animation.

  """

  propName: str = ...

  """

  Sets the property to be used in FromProp playback mode.

  """

  mode: int = ...

  """

  The operation mode of the actuator. Can be one of ::`these constants<action-actuator>`.

  """

  useContinue: bool = ...

  """

  The actions continue option, True or False. When True, the action will always play from where last left off,
otherwise negative events to this actuator will reset it to its start frame.

  """

  framePropName: str = ...

  """

  The name of the property that is set to the current frame number.

  """

class SCA_ActuatorSensor:

  """

  Actuator sensor detect change in actuator state of the parent object.
It generates a positive pulse if the corresponding actuator is activated
and a negative pulse if the actuator is deactivated.

  """

  actuator: str = ...

  """

  the name of the actuator that the sensor is monitoring.

  """

class SCA_AddObjectActuator:

  """

  Edit Object Actuator (in Add Object Mode)

  Warning: An Add Object actuator will be ignored if at game start, the linked object doesn't exist (or is empty) or the linked object is in an active layer.

    .. code:: none

      Error: GameObject 'Name' has a AddObjectActuator 'ActuatorName' without object (in 'nonactive' layer)

  """

  object: KX_GameObject = ...

  """

  the object this actuator adds.

  """

  objectLastCreated: KX_GameObject = ...

  """

  the last added object from this actuator (read-only).

  """

  time: float = ...

  """

  the lifetime of added objects, in frames. Set to 0 to disable automatic deletion.

  """

  linearVelocity: typing.List[typing.Any] = ...

  """

  the initial linear velocity of added objects.

  """

  angularVelocity: typing.List[typing.Any] = ...

  """

  the initial angular velocity of added objects.

  """

  def instantAddObject(self) -> None:

    """

    adds the object without needing to calling SCA_PythonController.activate()

    Note: Use objectLastCreated to get the newly created object.

    """

    ...

class SCA_AlwaysSensor:

  """

  This sensor is always activated.

  """

  ...

class SCA_ArmatureActuator:

  """

  Armature Actuators change constraint condition on armatures.

  """

  type: int = ...

  """

  The type of action that the actuator executes when it is active.

  Can be one of ::`these constants <armatureactuator-constants-type>`

  """

  constraint: BL_ArmatureConstraint = ...

  """

  The constraint object this actuator is controlling.

  """

  target: KX_GameObject = ...

  """

  The object that this actuator will set as primary target to the constraint it controls.

  """

  subtarget: KX_GameObject = ...

  """

  The object that this actuator will set as secondary target to the constraint it controls.

  Note: Currently, the only secondary target is the pole target for IK constraint.

  """

  weight: float = ...

  """

  The weight this actuator will set on the constraint it controls.

  Note: Currently only the IK constraint has a weight. It must be a value between 0 and 1.

  Note: A weight of 0 disables a constraint while still updating constraint runtime values (see :class:`~bge.types.BL_ArmatureConstraint`)

  """

  influence: float = ...

  """

  The influence this actuator will set on the constraint it controls.

  """

class SCA_ArmatureSensor:

  """

  Armature sensor detect conditions on armatures.

  """

  type: int = ...

  """

  The type of measurement that the sensor make when it is active.

  Can be one of ::`these constants <armaturesensor-type>`

  """

  constraint: BL_ArmatureConstraint = ...

  """

  The constraint object this sensor is watching.

  """

  value: float = ...

  """

  The threshold used in the comparison with the constraint error
The linear error is only updated on CopyPose/Distance IK constraint with iTaSC solver
The rotation error is only updated on CopyPose+rotation IK constraint with iTaSC solver
The linear error on CopyPose is always >= 0: it is the norm of the distance between the target and the bone
The rotation error on CopyPose is always >= 0: it is the norm of the equivalent rotation vector between the bone and the target orientations
The linear error on Distance can be positive if the distance between the bone and the target is greater than the desired distance, and negative if the distance is smaller.

  """

class SCA_CameraActuator:

  """

  Applies changes to a camera.

  """

  damping: float = ...

  """

  strength of of the camera following movement.

  """

  axis: int = ...

  """

  The camera axis (0, 1, 2) for positive ``XYZ``, (3, 4, 5) for negative ``XYZ``.

  """

  min: float = ...

  """

  minimum distance to the target object maintained by the actuator.

  """

  max: float = ...

  """

  maximum distance to stay from the target object.

  """

  height: float = ...

  """

  height to stay above the target object.

  """

  object: KX_GameObject = ...

  """

  the object this actuator tracks.

  """

class SCA_CollisionSensor:

  """

  Collision sensor detects collisions between objects.

  """

  propName: str = ...

  """

  The property or material to collide with.

  """

  useMaterial: bool = ...

  """

  Determines if the sensor is looking for a property or material. KX_True = Find material; KX_False = Find property.

  """

  usePulseCollision: bool = ...

  """

  When enabled, changes to the set of colliding objects generate a pulse.

  """

  hitObject: KX_GameObject = ...

  """

  The last collided object. (read-only).

  """

  hitObjectList: typing.Union[typing.Sequence[KX_GameObject], typing.Mapping[str, KX_GameObject], EXP_ListValue] = ...

  """

  A list of colliding objects. (read-only).

  """

  hitMaterial: str = ...

  """

  The material of the object in the face hit by the ray. (read-only).

  """

class SCA_ConstraintActuator:

  """

  A constraint actuator limits the position, rotation, distance or orientation of an object.

  """

  damp: int = ...

  """

  Time constant of the constraint expressed in frame (not use by Force field constraint).

  """

  rotDamp: int = ...

  """

  Time constant for the rotation expressed in frame (only for the distance constraint), 0 = use damp for rotation as well.

  """

  direction: typing.Any = ...

  """

  The reference direction in world coordinate for the orientation constraint.

  """

  option: int = ...

  """

  Binary combination of ::`these constants <constraint-actuator-option>`

  """

  time: int = ...

  """

  activation time of the actuator. The actuator disables itself after this many frame. If set to 0, the actuator is not limited in time.

  """

  propName: str = ...

  """

  the name of the property or material for the ray detection of the distance constraint.

  """

  min: float = ...

  """

  The lower bound of the constraint. For the rotation and orientation constraint, it represents radiant.

  """

  distance: float = ...

  """

  the target distance of the distance constraint.

  """

  max: float = ...

  """

  the upper bound of the constraint. For rotation and orientation constraints, it represents radiant.

  """

  rayLength: float = ...

  """

  the length of the ray of the distance constraint.

  """

  limit: int = ...

  """

  type of constraint. Use one of the ::`these constants <constraint-actuator-limit>`

  """

class SCA_DelaySensor:

  """

  The Delay sensor generates positive and negative triggers at precise time,
expressed in number of frames. The delay parameter defines the length of the initial OFF period. A positive trigger is generated at the end of this period.

  The duration parameter defines the length of the ON period following the OFF period.
There is a negative trigger at the end of the ON period. If duration is 0, the sensor stays ON and there is no negative trigger.

  The sensor runs the OFF-ON cycle once unless the repeat option is set: the OFF-ON cycle repeats indefinitely (or the OFF cycle if duration is 0).

  Use :meth:`SCA_ISensor.reset <bge.types.SCA_ISensor.reset>` at any time to restart sensor.

  """

  delay: int = ...

  """

  length of the initial OFF period as number of frame, 0 for immediate trigger.

  """

  duration: int = ...

  """

  length of the ON period in number of frame after the initial OFF period.

  If duration is greater than 0, a negative trigger is sent at the end of the ON pulse.

  """

  repeat: int = ...

  """

  1 if the OFF-ON cycle should be repeated indefinitely, 0 if it should run once.

  """

class SCA_DynamicActuator:

  """

  Dynamic Actuator.

  """

  mode: int = ...

  """

  the type of operation of the actuator, 0-4

  * KX_DYN_RESTORE_DYNAMICS(0)

  * KX_DYN_DISABLE_DYNAMICS(1)

  * KX_DYN_ENABLE_RIGID_BODY(2)

  * KX_DYN_DISABLE_RIGID_BODY(3)

  * KX_DYN_SET_MASS(4)

  """

  mass: float = ...

  """

  the mass value for the KX_DYN_SET_MASS operation.

  """

class SCA_EndObjectActuator:

  """

  Edit Object Actuator (in End Object mode)

  This actuator has no python methods.

  """

  ...

class SCA_GameActuator:

  """

  The game actuator loads a new .blend file, restarts the current .blend file or quits the game.

  """

  fileName: str = ...

  """

  the new .blend file to load.

  """

  mode: int = ...

  """

  The mode of this actuator. Can be on of ::`these constants <game-actuator>`

  """

class SCA_IActuator:

  """

  Base class for all actuator logic bricks.

  """

  ...

class SCA_IController:

  """

  Base class for all controller logic bricks.

  """

  state: int = ...

  """

  The controllers state bitmask. This can be used with the GameObject's state to test if the controller is active.

  """

  sensors: typing.Sequence[typing.Any] = ...

  """

  A list of sensors linked to this controller.

  Note: The sensors are not necessarily owned by the same object.

  Note: When objects are instanced in dupligroups links may be lost from objects outside the dupligroup.

  """

  actuators: typing.Sequence[typing.Any] = ...

  """

  A list of actuators linked to this controller.

  Note: The sensors are not necessarily owned by the same object.

  Note: When objects are instanced in dupligroups links may be lost from objects outside the dupligroup.

  """

  useHighPriority: bool = ...

  """

  When set the controller executes always before all other controllers that dont have this set.

  Note: Order of execution between high priority controllers is not guaranteed.

  """

class SCA_ILogicBrick:

  """

  Base class for all logic bricks.

  """

  executePriority: int = ...

  """

  This determines the order controllers are evaluated, and actuators are activated (lower priority is executed first).

  """

  owner: KX_GameObject = ...

  """

  The game object this logic brick is attached to (read-only).

  """

  name: str = ...

  """

  The name of this logic brick (read-only).

  """

class SCA_IObject:

  """

  This class has no python functions

  """

  ...

class SCA_ISensor:

  """

  Base class for all sensor logic bricks.

  """

  usePosPulseMode: bool = ...

  """

  Flag to turn positive pulse mode on and off.

  """

  useNegPulseMode: bool = ...

  """

  Flag to turn negative pulse mode on and off.

  """

  frequency: int = ...

  """

  The frequency for pulse mode sensors.

  Deprecated since version 0.0.1: Use :attr:`skippedTicks`

  """

  skippedTicks: int = ...

  """

  Number of logic ticks skipped between 2 active pulses

  """

  level: bool = ...

  """

  level Option whether to detect level or edge transition when entering a state.
It makes a difference only in case of logic state transition (state actuator).
A level detector will immediately generate a pulse, negative or positive
depending on the sensor condition, as soon as the state is activated.
A edge detector will wait for a state change before generating a pulse.
note: mutually exclusive with :attr:`tap`, enabling will disable :attr:`tap`.

  """

  tap: bool = ...

  """

  When enabled only sensors that are just activated will send a positive event,
after this they will be detected as negative by the controllers.
This will make a key that's held act as if its only tapped for an instant.
note: mutually exclusive with :attr:`level`, enabling will disable :attr:`level`.

  """

  invert: bool = ...

  """

  Flag to set if this sensor activates on positive or negative events.

  """

  triggered: bool = ...

  """

  True if this sensor brick is in a positive state. (read-only).

  """

  positive: bool = ...

  """

  True if this sensor brick is in a positive state. (read-only).

  """

  pos_ticks: int = ...

  """

  The number of ticks since the last positive pulse (read-only).

  """

  neg_ticks: int = ...

  """

  The number of ticks since the last negative pulse (read-only).

  """

  status: int = ...

  """

  The status of the sensor (read-only): can be one of ::`these constants<sensor-status>`.

  Note: This convenient attribute combines the values of triggered and positive attributes.

  """

  def reset(self) -> None:

    """

    Reset sensor internal state, effect depends on the type of sensor and settings.

    The sensor is put in its initial state as if it was just activated.

    """

    ...

class SCA_InputEvent:

  """

  Events for a keyboard or mouse input.

  """

  status: typing.List[int] = ...

  """

  A list of existing status of the input from the last frame.
Can contain :data:`bge.logic.KX_INPUT_NONE` and :data:`bge.logic.KX_INPUT_ACTIVE`.
The list always contains one value.
The first value of the list is the last value of the list in the last frame. (read-only)

  """

  queue: typing.List[int] = ...

  """

  A list of existing events of the input from the last frame.
Can contain :data:`bge.logic.KX_INPUT_JUST_ACTIVATED` and :data:`bge.logic.KX_INPUT_JUST_RELEASED`.
The list can be empty. (read-only)

  """

  values: typing.List[int] = ...

  """

  A list of existing value of the input from the last frame.
For keyboard it contains 1 or 0 and for mouse the coordinate of the mouse or the movement of the wheel mouse.
The list contains always one value, the size of the list is the same than :data:`queue` + 1 only for keyboard inputs.
The first value of the list is the last value of the list in the last frame. (read-only)

  Example to get the non-normalized mouse coordinates:

  .. code:: python

    import bge

    x = bge.logic.mouse.inputs[bge.events.MOUSEX].values[-1]
    y = bge.logic.mouse.inputs[bge.events.MOUSEY].values[-1]

    print("Mouse non-normalized position: x: {0}, y: {1}".format(x, y))

  """

  inactive: bool = ...

  """

  True if the input was inactive from the last frame.

  """

  active: bool = ...

  """

  True if the input was active from the last frame.

  """

  activated: bool = ...

  """

  True if the input was activated from the last frame.

  """

  released: bool = ...

  """

  True if the input was released from the last frame.

  Example to execute some action when I click or release mouse left button:

  .. code:: python

    import bge

    mouse = bge.logic.mouse.inputs
    mouse_left_button = mouse[bge.events.LEFTMOUSE]

    if mouse_left_button.activated:
       # ...
    elif mouse_left_button.active:
       # ...
    elif mouse_left_button.released:
       # ...
    elif mouse_left_button.inactive:
       # ...

  """

  type: int = ...

  """

  The type of the input.
One of ::`these constants<keyboard-keys>`

  """

class SCA_JoystickSensor:

  """

  This sensor detects player joystick events.

  """

  axisValues: typing.List[int] = ...

  """

  The state of the joysticks axis as a list of values :attr:`numAxis` long. (read-only).

  Each specifying the value of an axis between -32767 and 32767 depending on how far the axis is pushed, 0 for nothing.
The first 2 values are used by most joysticks and gamepads for directional control. 3rd and 4th values are only on some joysticks and can be used for arbitrary controls.

  * left:[-32767, 0, ...]

  * right:[32767, 0, ...]

  * up:[0, -32767, ...]

  * down:[0, 32767, ...]

  """

  axisSingle: int = ...

  """

  like :attr:`axisValues` but returns a single axis value that is set by the sensor. (read-only).

  Note: Only use this for "Single Axis" type sensors otherwise it will raise an error.

  """

  hatValues: typing.List[int] = ...

  """

  The state of the joysticks hats as a list of values :attr:`numHats` long. (read-only).

  Each specifying the direction of the hat from 1 to 12, 0 when inactive.

  Hat directions are as follows...

  * 0:None

  * 1:Up

  * 2:Right

  * 4:Down

  * 8:Left

  * 3:Up - Right

  * 6:Down - Right

  * 12:Down - Left

  * 9:Up - Left

  Deprecated since version 0.2.2: Use :attr:`button` instead.

  """

  hatSingle: int = ...

  """

  Like :attr:`hatValues` but returns a single hat direction value that is set by the sensor. (read-only).

  Deprecated since version 0.2.2: Use :attr:`button` instead.

  """

  numAxis: int = ...

  """

  The number of axes for the joystick at this index. (read-only).

  """

  numButtons: int = ...

  """

  The number of buttons for the joystick at this index. (read-only).

  """

  numHats: int = ...

  """

  The number of hats for the joystick at this index. (read-only).

  Deprecated since version 0.2.2: Use :attr:`numButtons` instead.

  """

  connected: bool = ...

  """

  True if a joystick is connected at this joysticks index. (read-only).

  """

  index: int = ...

  """

  The joystick index to use (from 0 to 7). The first joystick is always 0.

  """

  threshold: int = ...

  """

  Axis threshold. Joystick axis motion below this threshold wont trigger an event. Use values between (0 and 32767), lower values are more sensitive.

  """

  button: int = ...

  """

  The button index the sensor reacts to (first button = 0). When the "All Events" toggle is set, this option has no effect.

  """

  axis: typing.Any = ...

  """

  The axis this sensor reacts to, as a list of two values [axisIndex, axisDirection]

  * axisIndex: the axis index to use when detecting axis movement, 1=primary directional control, 2=secondary directional control.

  * axisDirection: 0=right, 1=up, 2=left, 3=down.

  """

  hat: typing.Any = ...

  """

  The hat the sensor reacts to, as a list of two values: [hatIndex, hatDirection]

  * hatIndex: the hat index to use when detecting hat movement, 1=primary hat, 2=secondary hat (4 max).

  * hatDirection: 1-12.

  Deprecated since version 0.2.2: Use :attr:`button` instead.

  """

  def getButtonActiveList(self) -> typing.List[typing.Any]:

    ...

  def getButtonStatus(self, buttonIndex: int) -> bool:

    ...

class SCA_KeyboardSensor:

  """

  A keyboard sensor detects player key presses.

  See module :mod:`bge.events` for keycode values.

  """

  key: int = ...

  """

  The key code this sensor is looking for. Expects a keycode from :mod:`bge.events` module.

  """

  hold1: int = ...

  """

  The key code for the first modifier this sensor is looking for. Expects a keycode from :mod:`bge.events` module.

  """

  hold2: int = ...

  """

  The key code for the second modifier this sensor is looking for. Expects a keycode from :mod:`bge.events` module.

  """

  toggleProperty: str = ...

  """

  The name of the property that indicates whether or not to log keystrokes as a string.

  """

  targetProperty: str = ...

  """

  The name of the property that receives keystrokes in case in case a string is logged.

  """

  useAllKeys: bool = ...

  """

  Flag to determine whether or not to accept all keys.

  """

  inputs: typing.Dict[typing.Any, SCA_InputEvent] = ...

  """

  A list of pressed input keys that have either been pressed, or just released, or are active this frame. (read-only).

  """

  events: typing.List[typing.Any] = ...

  """

  a list of pressed keys that have either been pressed, or just released, or are active this frame. (read-only).

  Deprecated since version 0.2.2: Use :data:`inputs`

  """

  def getKeyStatus(self, keycode: int) -> int:

    """

    Get the status of a key.

    """

    ...

class SCA_MouseActuator:

  """

  The mouse actuator gives control over the visibility of the mouse cursor and rotates the parent object according to mouse movement.

  """

  def reset(self) -> None:

    """

    Undoes the rotation caused by the mouse actuator.

    """

    ...

  visible: bool = ...

  """

  The visibility of the mouse cursor.

  """

  use_axis_x: bool = ...

  """

  Mouse movement along the x axis effects object rotation.

  """

  use_axis_y: bool = ...

  """

  Mouse movement along the y axis effects object rotation.

  """

  threshold: typing.List[float] = ...

  """

  Amount of movement from the mouse required before rotation is triggered.

  The values in the list should be between 0.0 and 0.5.

  """

  reset_x: bool = ...

  """

  Mouse is locked to the center of the screen on the x axis.

  """

  reset_y: bool = ...

  """

  Mouse is locked to the center of the screen on the y axis.

  """

  object_axis: typing.List[int] = ...

  """

  The object's 3D axis to rotate with the mouse movement. ([x, y])

  * KX_ACT_MOUSE_OBJECT_AXIS_X

  * KX_ACT_MOUSE_OBJECT_AXIS_Y

  * KX_ACT_MOUSE_OBJECT_AXIS_Z

  """

  local_x: bool = ...

  """

  Rotation caused by mouse movement along the x axis is local.

  """

  local_y: bool = ...

  """

  Rotation caused by mouse movement along the y axis is local.

  """

  sensitivity: typing.List[float] = ...

  """

  The amount of rotation caused by mouse movement along the x and y axis.

  Negative values invert the rotation.

  """

  limit_x: typing.List[float] = ...

  """

  The minimum and maximum angle of rotation caused by mouse movement along the x axis in degrees.
limit_x[0] is minimum, limit_x[1] is maximum.

  """

  limit_y: typing.List[float] = ...

  """

  The minimum and maximum angle of rotation caused by mouse movement along the y axis in degrees.
limit_y[0] is minimum, limit_y[1] is maximum.

  """

  angle: typing.List[float] = ...

  """

  The current rotational offset caused by the mouse actuator in degrees.

  """

class SCA_MouseFocusSensor:

  """

  The mouse focus sensor detects when the mouse is over the current game object.

  The mouse focus sensor works by transforming the mouse coordinates from 2d device
space to 3d space then raycasting away from the camera.

  """

  raySource: typing.List[float] = ...

  """

  The worldspace source of the ray (the view position).

  """

  rayTarget: typing.List[float] = ...

  """

  The worldspace target of the ray.

  """

  rayDirection: typing.List[float] = ...

  """

  The :attr:`rayTarget` - :attr:`raySource` normalized.

  """

  hitObject: KX_GameObject = ...

  """

  the last object the mouse was over.

  """

  hitPosition: typing.List[float] = ...

  """

  The worldspace position of the ray intersection.

  """

  hitNormal: typing.List[float] = ...

  """

  the worldspace normal from the face at point of intersection.

  """

  hitUV: typing.List[float] = ...

  """

  the UV coordinates at the point of intersection.

  If the object has no UV mapping, it returns [0, 0].

  The UV coordinates are not normalized, they can be < 0 or > 1 depending on the UV mapping.

  """

  usePulseFocus: bool = ...

  """

  When enabled, moving the mouse over a different object generates a pulse. (only used when the 'Mouse Over Any' sensor option is set).

  """

  useXRay: bool = ...

  """

    If enabled it allows the sensor to see through game objects that don't have the selected property or material.

  """

  mask: int = ...

  """

  The collision mask (16 layers mapped to a 16-bit integer) combined with each object's collision group, to hit only a subset of the
objects in the scene. Only those objects for which ``collisionGroup & mask`` is true can be hit.

  """

  propName: str = ...

  """

    The property or material the sensor is looking for.

  """

  useMaterial: bool = ...

  """

    Determines if the sensor is looking for a property or material. KX_True = Find material; KX_False = Find property.

  """

class SCA_MouseSensor:

  """

  Mouse Sensor logic brick.

  """

  position: typing.Any = ...

  """

  current [x, y] coordinates of the mouse, in frame coordinates (pixels).

  """

  mode: int = ...

  """

  sensor mode. one of the following constants:

  * KX_MOUSESENSORMODE_LEFTBUTTON(1)

  * KX_MOUSESENSORMODE_MIDDLEBUTTON(2)

  * KX_MOUSESENSORMODE_RIGHTBUTTON(3)

  * KX_MOUSESENSORMODE_BUTTON4(4)

  * KX_MOUSESENSORMODE_BUTTON5(5)

  * KX_MOUSESENSORMODE_BUTTON6(6)

  * KX_MOUSESENSORMODE_BUTTON7(7)

  * KX_MOUSESENSORMODE_WHEELUP(8)

  * KX_MOUSESENSORMODE_WHEELDOWN(9)

  * KX_MOUSESENSORMODE_MOVEMENT(10)

  """

  def getButtonStatus(self, button: int) -> int:

    """

    Get the mouse button status.

    """

    ...

class SCA_NANDController:

  """

  An NAND controller activates when all linked sensors are not active.

  There are no special python methods for this controller.

  """

  ...

class SCA_NORController:

  """

  An NOR controller activates only when all linked sensors are de-activated.

  There are no special python methods for this controller.

  """

  ...

class SCA_NearSensor:

  """

  A near sensor is a specialised form of touch sensor.

  """

  distance: float = ...

  """

  The near sensor activates when an object is within this distance.

  """

  resetDistance: float = ...

  """

  The near sensor deactivates when the object exceeds this distance.

  """

class SCA_NetworkMessageActuator:

  """

  Message Actuator

  """

  propName: str = ...

  """

  Messages will only be sent to objects with the given property name.

  """

  subject: str = ...

  """

  The subject field of the message.

  """

  body: str = ...

  """

  The body of the message.

  """

  usePropBody: bool = ...

  """

  Send a property instead of a regular body message.

  """

class SCA_NetworkMessageSensor:

  """

  The Message Sensor logic brick.

  Currently only loopback (local) networks are supported.

  """

  subject: str = ...

  """

  The subject the sensor is looking for.

  """

  frameMessageCount: int = ...

  """

  The number of messages received since the last frame. (read-only).

  """

  subjects: typing.List[str] = ...

  """

  The list of message subjects received. (read-only).

  """

  bodies: typing.List[str] = ...

  """

  The list of message bodies received. (read-only).

  """

class SCA_ORController:

  """

  An OR controller activates when any connected sensor activates.

  There are no special python methods for this controller.

  """

  ...

class SCA_ObjectActuator:

  """

  The object actuator ("Motion Actuator") applies force, torque, displacement, angular displacement,
velocity, or angular velocity to an object.
Servo control allows to regulate force to achieve a certain speed target.

  """

  force: mathutils.Vector = ...

  """

  The force applied by the actuator.

  """

  useLocalForce: bool = ...

  """

  A flag specifying if the force is local.

  """

  torque: mathutils.Vector = ...

  """

  The torque applied by the actuator.

  """

  useLocalTorque: bool = ...

  """

  A flag specifying if the torque is local.

  """

  dLoc: mathutils.Vector = ...

  """

  The displacement vector applied by the actuator.

  """

  useLocalDLoc: bool = ...

  """

  A flag specifying if the dLoc is local.

  """

  dRot: mathutils.Vector = ...

  """

  The angular displacement vector applied by the actuator

  Note: Since the displacement is applied every frame, you must adjust the displacement based on the frame rate, or you game experience will depend on the player's computer speed.

  """

  useLocalDRot: bool = ...

  """

  A flag specifying if the dRot is local.

  """

  linV: mathutils.Vector = ...

  """

  The linear velocity applied by the actuator.

  """

  useLocalLinV: bool = ...

  """

  A flag specifying if the linear velocity is local.

  Note: This is the target speed for servo controllers.

  """

  angV: mathutils.Vector = ...

  """

  The angular velocity applied by the actuator.

  """

  useLocalAngV: bool = ...

  """

  A flag specifying if the angular velocity is local.

  """

  damping: int = ...

  """

  The damping parameter of the servo controller.

  """

  forceLimitX: typing.List[typing.Any] = ...

  """

  The min/max force limit along the X axis and activates or deactivates the limits in the servo controller.

  """

  forceLimitY: typing.List[typing.Any] = ...

  """

  The min/max force limit along the Y axis and activates or deactivates the limits in the servo controller.

  """

  forceLimitZ: typing.List[typing.Any] = ...

  """

  The min/max force limit along the Z axis and activates or deactivates the limits in the servo controller.

  """

  pid: typing.List[float] = ...

  """

  The PID coefficients of the servo controller.

  """

  reference: KX_GameObject = ...

  """

  The object that is used as reference to compute the velocity for the servo controller.

  """

class SCA_ParentActuator:

  """

  The parent actuator can set or remove an objects parent object.

  """

  object: KX_GameObject = ...

  """

  the object this actuator sets the parent too.

  """

  mode: int = ...

  """

  The mode of this actuator.

  """

  compound: bool = ...

  """

  Whether the object shape should be added to the parent compound shape when parenting.

  Effective only if the parent is already a compound shape.

  """

  ghost: bool = ...

  """

  Whether the object should be made ghost when parenting
Effective only if the shape is not added to the parent compound shape.

  """

class SCA_PropertyActuator:

  """

  Property Actuator

  """

  propName: str = ...

  """

  the property on which to operate.

  """

  value: str = ...

  """

  the value with which the actuator operates.

  """

  mode: int = ...

  """

  TODO - add constants to game logic dict!.

  """

class SCA_PropertySensor:

  """

  Activates when the game object property matches.

  """

  mode: int = ...

  """

  Type of check on the property. Can be one of ::`these constants <logic-property-sensor>`

  """

  propName: str = ...

  """

  the property the sensor operates.

  """

  value: str = ...

  """

  the value with which the sensor compares to the value of the property.

  """

  min: str = ...

  """

  the minimum value of the range used to evaluate the property when in interval mode.

  """

  max: str = ...

  """

  the maximum value of the range used to evaluate the property when in interval mode.

  """

class SCA_PythonController:

  """

  A Python controller uses a Python script to activate it's actuators,
based on it's sensors.

  """

  owner: KX_GameObject = ...

  """

  The object the controller is attached to.

  """

  script: str = ...

  """

  The value of this variable depends on the execution method.

  * When 'Script' execution mode is set this value contains the entire python script as a single string (not the script name as you might expect) which can be modified to run different scripts.

  * When 'Module' execution mode is set this value will contain a single line string - module name and function "module.func" or "package.module.func" where the module names are python textblocks or external scripts.

  Note: Once this is set the script name given for warnings will remain unchanged.

  """

  mode: int = ...

  """

  the execution mode for this controller (read-only).

  * Script: 0, Execite the :attr:`script` as a python code.

  * Module: 1, Execite the :attr:`script` as a module and function.

  """

  def activate(self, actuator: typing.Union[SCA_IActuator, str]) -> None:

    """

    Activates an actuator attached to this controller.

    """

    ...

  def deactivate(self, actuator: typing.Union[SCA_IActuator, str]) -> None:

    """

    Deactivates an actuator attached to this controller.

    """

    ...

class SCA_PythonJoystick:

  """

  A Python interface to a joystick.

  """

  name: str = ...

  """

  The name assigned to the joystick by the operating system. (read-only)

  """

  activeButtons: typing.List[typing.Any] = ...

  """

  A list of active button values. (read-only)

  """

  axisValues: typing.List[int] = ...

  """

  The state of the joysticks axis as a list of values :attr:`numAxis` long. (read-only).

  Each specifying the value of an axis between -1.0 and 1.0
depending on how far the axis is pushed, 0 for nothing.
The first 2 values are used by most joysticks and gamepads for directional control.
3rd and 4th values are only on some joysticks and can be used for arbitrary controls.

  * left:[-1.0, 0.0, ...]

  * right:[1.0, 0.0, ...]

  * up:[0.0, -1.0, ...]

  * down:[0.0, 1.0, ...]

  """

  hatValues: typing.Any = ...

  """

  Deprecated since version 0.2.2: Use :attr:`activeButtons` instead.

  """

  numAxis: int = ...

  """

  The number of axes for the joystick at this index. (read-only).

  """

  numButtons: int = ...

  """

  The number of buttons for the joystick at this index. (read-only).

  """

  numHats: typing.Any = ...

  """

  Deprecated since version 0.2.2: Use :attr:`numButtons` instead.

  """

  def startVibration(self) -> None:

    """

    Starts the vibration.

    """

    ...

  def stopVibration(self) -> None:

    """

    Stops the vibration.

    """

    ...

  strengthLeft: float = ...

  """

  Strength of the Low frequency joystick's motor (placed at left position usually).

  """

  strengthRight: float = ...

  """

  Strength of the High frequency joystick's motor (placed at right position usually).

  """

  duration: int = ...

  """

  Duration of the vibration in milliseconds.

  """

  isVibrating: bool = ...

  """

  Check status of joystick vibration

  """

  hasVibration: bool = ...

  """

  Check if the joystick supports vibration

  """

class SCA_PythonKeyboard:

  """

  The current keyboard.

  """

  inputs: typing.Dict[typing.Any, SCA_InputEvent] = ...

  """

  A dictionary containing the input of each keyboard key. (read-only).

  """

  events: typing.Dict[typing.Any, typing.Any] = ...

  """

  A dictionary containing the status of each keyboard event or key. (read-only).

  Deprecated since version 0.2.2: Use :attr:`inputs`.

  """

  activeInputs: typing.Dict[typing.Any, SCA_InputEvent] = ...

  """

  A dictionary containing the input of only the active keyboard keys. (read-only).

  """

  active_events: typing.Dict[typing.Any, typing.Any] = ...

  """

  A dictionary containing the status of only the active keyboard events or keys. (read-only).

  Deprecated since version 0.2.2: Use :attr:`activeInputs`.

  """

  text: str = ...

  """

  The typed unicode text from the last frame.

  """

  def getClipboard(self) -> str:

    """

    Gets the clipboard text.

    """

    ...

  def setClipboard(self, text: str) -> None:

    """

    Sets the clipboard text.

    """

    ...

class SCA_PythonMouse:

  """

  The current mouse.

  """

  inputs: typing.Dict[typing.Any, SCA_InputEvent] = ...

  """

  A dictionary containing the input of each mouse event. (read-only).

  """

  events: typing.Dict[typing.Any, typing.Any] = ...

  """

  a dictionary containing the status of each mouse event. (read-only).

  Deprecated since version 0.2.2: Use :attr:`inputs`.

  """

  activeInputs: typing.Dict[typing.Any, SCA_InputEvent] = ...

  """

  A dictionary containing the input of only the active mouse events. (read-only).

  """

  active_events: typing.Dict[typing.Any, typing.Any] = ...

  """

  a dictionary containing the status of only the active mouse events. (read-only).

  Deprecated since version 0.2.2: Use :data:`activeInputs`.

  """

  position: typing.Tuple[typing.Any, ...] = ...

  """

  The normalized x and y position of the mouse cursor.

  """

  visible: bool = ...

  """

  The visibility of the mouse cursor.

  """

class SCA_RadarSensor:

  """

  Radar sensor is a near sensor with a conical sensor object.

  """

  coneOrigin: typing.List[float] = ...

  """

  The origin of the cone with which to test. The origin is in the middle of the cone. (read-only).

  """

  coneTarget: typing.List[float] = ...

  """

  The center of the bottom face of the cone with which to test. (read-only).

  """

  distance: float = ...

  """

  The height of the cone with which to test (read-only).

  """

  angle: float = ...

  """

  The angle of the cone (in degrees) with which to test (read-only).

  """

  axis: int = ...

  """

  The axis on which the radar cone is cast.

  KX_RADAR_AXIS_POS_X, KX_RADAR_AXIS_POS_Y, KX_RADAR_AXIS_POS_Z,
KX_RADAR_AXIS_NEG_X, KX_RADAR_AXIS_NEG_Y, KX_RADAR_AXIS_NEG_Z

  """

class SCA_RandomActuator:

  """

  Random Actuator

  """

  seed: int = ...

  """

  Seed of the random number generator.

  Equal seeds produce equal series. If the seed is 0, the generator will produce the same value on every call.

  """

  para1: float = ...

  """

  the first parameter of the active distribution.

  Refer to the documentation of the generator types for the meaning of this value.

  """

  para2: float = ...

  """

  the second parameter of the active distribution.

  Refer to the documentation of the generator types for the meaning of this value.

  """

  distribution: int = ...

  """

  Distribution type. (read-only). Can be one of ::`these constants <logic-random-distributions>`

  """

  propName: str = ...

  """

  the name of the property to set with the random value.

  If the generator and property types do not match, the assignment is ignored.

  """

  def setBoolConst(self, value: bool) -> None:

    """

    Sets this generator to produce a constant boolean value.

    """

    ...

  def setBoolUniform(self) -> None:

    """

    Sets this generator to produce a uniform boolean distribution.

    The generator will generate True or False with 50% chance.

    """

    ...

  def setBoolBernouilli(self, value: float) -> None:

    """

    Sets this generator to produce a Bernouilli distribution.

    """

    ...

  def setIntConst(self, value: int) -> None:

    """

    Sets this generator to always produce the given value.

    """

    ...

  def setIntUniform(self, lower_bound: int, upper_bound: int) -> None:

    """

    Sets this generator to produce a random value between the given lower and
upper bounds (inclusive).

    """

    ...

  def setIntPoisson(self, value: float) -> None:

    """

    Generate a Poisson-distributed number.

    This performs a series of Bernouilli tests with parameter value.
It returns the number of tries needed to achieve success.

    """

    ...

  def setFloatConst(self, value: float) -> None:

    """

    Always generate the given value.

    """

    ...

  def setFloatUniform(self, lower_bound: float, upper_bound: float) -> None:

    """

    Generates a random float between lower_bound and upper_bound with a
uniform distribution.

    """

    ...

  def setFloatNormal(self, mean: float, standard_deviation: float) -> None:

    """

    Generates a random float from the given normal distribution.

    """

    ...

  def setFloatNegativeExponential(self, half_life: float) -> None:

    """

    Generate negative-exponentially distributed numbers.

    The half-life 'time' is characterized by half_life.

    """

    ...

class SCA_RandomSensor:

  """

  This sensor activates randomly.

  """

  lastDraw: int = ...

  """

  The seed of the random number generator.

  """

  seed: int = ...

  """

  The seed of the random number generator.

  """

class SCA_RaySensor:

  """

  A ray sensor detects the first object in a given direction.

  """

  propName: str = ...

  """

  The property the ray is looking for.

  """

  range: float = ...

  """

  The distance of the ray.

  """

  useMaterial: bool = ...

  """

  Whether or not to look for a material (false = property).

  """

  useXRay: bool = ...

  """

  Whether or not to use XRay.

  """

  mask: int = ...

  """

  The collision mask (16 layers mapped to a 16-bit integer) combined with each object's collision group, to hit only a subset of the
objects in the scene. Only those objects for which ``collisionGroup & mask`` is true can be hit.

  """

  hitObject: KX_GameObject = ...

  """

  The game object that was hit by the ray. (read-only).

  """

  hitPosition: typing.List[typing.Any] = ...

  """

  The position (in worldcoordinates) where the object was hit by the ray. (read-only).

  """

  hitNormal: typing.List[typing.Any] = ...

  """

  The normal (in worldcoordinates) of the object at the location where the object was hit by the ray. (read-only).

  """

  hitMaterial: str = ...

  """

  The material of the object in the face hit by the ray. (read-only).

  """

  rayDirection: typing.List[typing.Any] = ...

  """

  The direction from the ray (in worldcoordinates). (read-only).

  """

  axis: int = ...

  """

  The axis the ray is pointing on.

  * KX_RAY_AXIS_POS_X

  * KX_RAY_AXIS_POS_Y

  * KX_RAY_AXIS_POS_Z

  * KX_RAY_AXIS_NEG_X

  * KX_RAY_AXIS_NEG_Y

  * KX_RAY_AXIS_NEG_Z

  """

class SCA_ReplaceMeshActuator:

  """

  Edit Object actuator, in Replace Mesh mode.

  Warning: Replace mesh actuators will be ignored if at game start, the named mesh doesn't exist.This will generate a warning in the console

    .. code:: none

      Error: GameObject 'Name' ReplaceMeshActuator 'ActuatorName' without object

  .. code:: python

    # Level-of-detail
    # Switch a game object's mesh based on its depth in the camera view.
    # +----------+     +-----------+     +-------------------------------------+
    # | Always   +-----+ Python    +-----+ Edit Object (Replace Mesh) LOD.Mesh |
    # +----------+     +-----------+     +-------------------------------------+
    from bge import logic

    # List detail meshes here
    # Mesh (name, near, far)
    # Meshes overlap so that they don't 'pop' when on the edge of the distance.
    meshes = ((".Hi", 0.0, -20.0),
          (".Med", -15.0, -50.0),
          (".Lo", -40.0, -100.0)
        )

    cont = logic.getCurrentController()
    object = cont.owner
    actuator = cont.actuators["LOD." + obj.name]
    camera = logic.getCurrentScene().active_camera

    def Depth(pos, plane):
      return pos[0]*plane[0] + pos[1]*plane[1] + pos[2]*plane[2] + plane[3]

    # Depth is negative and decreasing further from the camera
    depth = Depth(object.position, camera.world_to_camera[2])

    newmesh = None
    curmesh = None
    # Find the lowest detail mesh for depth
    for mesh in meshes:
      if depth < mesh[1] and depth > mesh[2]:
        newmesh = mesh
      if "ME" + object.name + mesh[0] == actuator.getMesh():
          curmesh = mesh

    if newmesh != None and "ME" + object.name + newmesh[0] != actuator.mesh:
      # The mesh is a different mesh - switch it.
      # Check the current mesh is not a better fit.
      if curmesh == None or curmesh[1] < depth or curmesh[2] > depth:
        actuator.mesh = object.name + newmesh[0]
        cont.activate(actuator)

  """

  mesh: KX_MeshProxy = ...

  """

  :class:`~bge.types.KX_MeshProxy` or the name of the mesh that will replace the current one.

  Set to None to disable actuator.

  """

  useDisplayMesh: bool = ...

  """

  when true the displayed mesh is replaced.

  """

  usePhysicsMesh: bool = ...

  """

  when true the physics mesh is replaced.

  """

  def instantReplaceMesh(self) -> None:

    """

    Immediately replace mesh without delay.

    """

    ...

class SCA_SceneActuator:

  """

  Scene Actuator logic brick.

  Warning: Scene actuators that use a scene name will be ignored if at game start, the named scene doesn't exist or is emptyThis will generate a warning in the console:

    .. code:: none

      Error: GameObject 'Name' has a SceneActuator 'ActuatorName' (SetScene) without scene

  """

  scene: str = ...

  """

  the name of the scene to change to/overlay/underlay/remove/suspend/resume.

  """

  camera: KX_Camera = ...

  """

  the camera to change to.

  Note: When setting the attribute, you can use either a :class:`~bge.types.KX_Camera` or the name of the camera.

  """

  useRestart: bool = ...

  """

  Set flag to True to restart the sene.

  """

  mode: int = ...

  """

  The mode of the actuator.

  """

class SCA_SoundActuator:

  """

  Sound Actuator.

  The :meth:`startSound`, :meth:`pauseSound` and :meth:`stopSound` do not require the actuator to be activated - they act instantly provided that the actuator has been activated once at least.

  """

  volume: float = ...

  """

  The volume (gain) of the sound.

  """

  time: float = ...

  """

  The current position in the audio stream (in seconds).

  """

  pitch: float = ...

  """

  The pitch of the sound.

  """

  mode: int = ...

  """

  The operation mode of the actuator. Can be one of ::`these constants<logic-sound-actuator>`

  """

  sound: aud.Sound = ...

  """

  The sound the actuator should play.

  """

  is3D: bool = ...

  """

  Whether or not the actuator should be using 3D sound. (read-only)

  """

  preload: bool = ...

  """

  Control whether to keep a RAM-buffered copy for fast re-triggers

  """

  volume_maximum: float = ...

  """

  The maximum gain of the sound, no matter how near it is.

  """

  volume_minimum: float = ...

  """

  The minimum gain of the sound, no matter how far it is away.

  """

  distance_reference: float = ...

  """

  The distance where the sound has a gain of 1.0.

  """

  distance_maximum: float = ...

  """

  The maximum distance at which you can hear the sound.

  """

  attenuation: float = ...

  """

  The influence factor on volume depending on distance.

  """

  cone_angle_inner: float = ...

  """

  The angle of the inner cone.

  """

  cone_angle_outer: float = ...

  """

  The angle of the outer cone.

  """

  cone_volume_outer: float = ...

  """

  The gain outside the outer cone (the gain in the outer cone will be interpolated between this value and the normal gain in the inner cone).

  """

  def startSound(self) -> None:

    """

    Starts the sound.

    """

    ...

  def pauseSound(self) -> None:

    """

    Pauses the sound.

    """

    ...

  def stopSound(self) -> None:

    """

    Stops the sound.

    """

    ...

class SCA_StateActuator:

  """

  State actuator changes the state mask of parent object.

  """

  operation: int = ...

  """

  Type of bit operation to be applied on object state mask.

  You can use one of ::`these constants <state-actuator-operation>`

  """

  mask: int = ...

  """

  Value that defines the bits that will be modified by the operation.

  The bits that are 1 in the mask will be updated in the object state.

  The bits that are 0 are will be left unmodified expect for the Copy operation which copies the mask to the object state.

  """

class SCA_SteeringActuator:

  """

  Steering Actuator for navigation.

  """

  behavior: int = ...

  """

  The steering behavior to use. One of ::`these constants <logic-steering-actuator>`.

  """

  velocity: float = ...

  """

  Velocity magnitude

  """

  acceleration: float = ...

  """

  Max acceleration

  """

  turnspeed: float = ...

  """

  Max turn speed

  """

  distance: float = ...

  """

  Relax distance

  """

  target: KX_GameObject = ...

  """

  Target object

  """

  navmesh: KX_GameObject = ...

  """

  Navigation mesh

  """

  selfterminated: bool = ...

  """

  Terminate when target is reached

  """

  enableVisualization: bool = ...

  """

  Enable debug visualization

  """

  pathUpdatePeriod: int = ...

  """

  Path update period

  """

  path: typing.List[mathutils.Vector] = ...

  """

  Path point list.

  """

class SCA_TrackToActuator:

  """

  Edit Object actuator in Track To mode.

  Warning: Track To Actuators will be ignored if at game start, the object to track to is invalid.This will generate a warning in the console:

    .. code:: none

      GameObject 'Name' no object in EditObjectActuator 'ActuatorName'

  """

  object: KX_GameObject = ...

  """

  the object this actuator tracks.

  """

  time: int = ...

  """

  the time in frames with which to delay the tracking motion.

  """

  use3D: bool = ...

  """

  the tracking motion to use 3D.

  """

  upAxis: int = ...

  """

  The axis that points upward.

  * KX_TRACK_UPAXIS_POS_X

  * KX_TRACK_UPAXIS_POS_Y

  * KX_TRACK_UPAXIS_POS_Z

  """

  trackAxis: int = ...

  """

  The axis that points to the target object.

  * KX_TRACK_TRAXIS_POS_X

  * KX_TRACK_TRAXIS_POS_Y

  * KX_TRACK_TRAXIS_POS_Z

  * KX_TRACK_TRAXIS_NEG_X

  * KX_TRACK_TRAXIS_NEG_Y

  * KX_TRACK_TRAXIS_NEG_Z

  """

class SCA_VibrationActuator:

  """

  Vibration Actuator.

  """

  joyindex: int = ...

  """

  Joystick index.

  """

  strengthLeft: float = ...

  """

  Strength of the Low frequency joystick's motor (placed at left position usually).

  """

  strengthRight: float = ...

  """

  Strength of the High frequency joystick's motor (placed at right position usually).

  """

  duration: int = ...

  """

  Duration of the vibration in milliseconds.

  """

  isVibrating: bool = ...

  """

  Check status of joystick vibration

  """

  hasVibration: bool = ...

  """

  Check if the joystick supports vibration

  """

  def startVibration(self) -> None:

    """

    Starts the vibration.

    """

    ...

  def stopVibration(self) -> None:

    """

    Stops the vibration.

    """

    ...

class SCA_VisibilityActuator:

  """

  Visibility Actuator.

  """

  visibility: bool = ...

  """

  whether the actuator makes its parent object visible or invisible.

  """

  useOcclusion: bool = ...

  """

  whether the actuator makes its parent object an occluder or not.

  """

  useRecursion: bool = ...

  """

  whether the visibility/occlusion should be propagated to all children of the object.

  """

class SCA_XNORController:

  """

  An XNOR controller activates when all linked sensors are the same (activated or inative).

  There are no special python methods for this controller.

  """

  ...

class SCA_XORController:

  """

  An XOR controller activates when there is the input is mixed, but not when all are on or off.

  There are no special python methods for this controller.

  """

  ...
