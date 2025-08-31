"""


Poselib Operators
*****************

:func:`apply_pose_asset`

:func:`asset_delete`

:func:`asset_modify`

:func:`blend_pose_asset`

:func:`convert_old_object_poselib`

:func:`convert_old_poselib`

:func:`copy_as_asset`

:func:`create_pose_asset`

:func:`paste_asset`

:func:`pose_asset_select_bones`

:func:`restore_previous_action`

"""

import typing

def apply_pose_asset(*args, asset_library_type: str = 'LOCAL', asset_library_identifier: str = '', relative_asset_identifier: str = '', blend_factor: float = 1.0, flipped: bool = False) -> None:

  """

  Apply the given Pose Action to the rig

  """

  ...

def asset_delete() -> None:

  """

  Delete the selected Pose Asset

  """

  ...

def asset_modify(*args, mode: str = 'ADJUST') -> None:

  """

  Update the selected pose asset in the asset library from the currently selected bones. The mode defines how the asset is updated

  """

  ...

def blend_pose_asset(*args, asset_library_type: str = 'LOCAL', asset_library_identifier: str = '', relative_asset_identifier: str = '', blend_factor: float = 0.0, flipped: bool = False, release_confirm: bool = False) -> None:

  """

  Blend the given Pose Action to the rig

  """

  ...

def convert_old_object_poselib() -> None:

  """

  Create a pose asset for each pose marker in this legacy pose library data-block

  """

  ...

def convert_old_poselib() -> None:

  """

  Create a pose asset for each pose marker in the current action

  """

  ...

def copy_as_asset() -> None:

  """

  Create a new pose asset on the clipboard, to be pasted into an Asset Browser

  """

  ...

def create_pose_asset(*args, pose_name: str = '', asset_library_reference: str = '', catalog_path: str = '', activate_new_action: bool = False) -> None:

  """

  Create a new asset from the selected bones in the scene

  """

  ...

def paste_asset() -> None:

  """

  Paste the Asset that was previously copied using Copy As Asset

  """

  ...

def pose_asset_select_bones(*args, select: bool = True, flipped: bool = False) -> None:

  """

  Select those bones that are used in this pose

  """

  ...

def restore_previous_action() -> None:

  """

  Switch back to the previous Action, after creating a pose asset

  """

  ...
