"""


Ui Operators
************

:func:`assign_default_button`

:func:`button_execute`

:func:`button_string_clear`

:func:`copy_as_driver_button`

:func:`copy_data_path_button`

:func:`copy_driver_to_selected_button`

:func:`copy_python_command_button`

:func:`copy_to_selected_button`

:func:`drop_color`

:func:`drop_material`

:func:`drop_name`

:func:`editsource`

:func:`eyedropper_bone`

:func:`eyedropper_color`

:func:`eyedropper_colorramp`

:func:`eyedropper_colorramp_point`

:func:`eyedropper_depth`

:func:`eyedropper_driver`

:func:`eyedropper_grease_pencil_color`

:func:`eyedropper_id`

:func:`jump_to_target_button`

:func:`list_start_filter`

:func:`override_add_button`

:func:`override_idtemplate_clear`

:func:`override_idtemplate_make`

:func:`override_idtemplate_reset`

:func:`override_remove_button`

:func:`reloadtranslation`

:func:`reset_default_button`

:func:`unset_property_button`

:func:`view_drop`

:func:`view_item_delete`

:func:`view_item_rename`

:func:`view_item_select`

:func:`view_scroll`

:func:`view_start_filter`

"""

import typing

def assign_default_button() -> None:

  """

  Set this property's current value as the new default

  """

  ...

def button_execute(*args, skip_depressed: bool = False) -> None:

  """

  Presses active button

  """

  ...

def button_string_clear() -> None:

  """

  Unsets the text of the active button

  """

  ...

def copy_as_driver_button() -> None:

  """

  Create a new driver with this property as input, and copy it to the internal clipboard. Use Paste Driver to add it to the target property, or Paste Driver Variables to extend an existing driver

  """

  ...

def copy_data_path_button(*args, full_path: bool = False) -> None:

  """

  Copy the RNA data path for this property to the clipboard

  """

  ...

def copy_driver_to_selected_button(*args, all: bool = False) -> None:

  """

  Copy the property's driver from the active item to the same property of all selected items, if the same property exists

  """

  ...

def copy_python_command_button() -> None:

  """

  Copy the Python command matching this button

  """

  ...

def copy_to_selected_button(*args, all: bool = True) -> None:

  """

  Copy the property's value from the active item to the same property of all selected items if the same property exists

  """

  ...

def drop_color(*args, color: typing.Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0), gamma: bool = False, has_alpha: bool = False) -> None:

  """

  Drop colors to buttons

  """

  ...

def drop_material(*args, session_uid: int = 0) -> None:

  """

  Drag material to Material slots in Properties

  """

  ...

def drop_name(*args, string: str = '') -> None:

  """

  Drop name to button

  """

  ...

def editsource() -> None:

  """

  Edit UI source code of the active button

  """

  ...

def eyedropper_bone() -> None:

  """

  Sample a bone from the 3D View or the Outliner to store in a property

  """

  ...

def eyedropper_color(*args, prop_data_path: str = '') -> None:

  """

  Sample a color from the Blender window to store in a property

  """

  ...

def eyedropper_colorramp() -> None:

  """

  Sample a color band

  """

  ...

def eyedropper_colorramp_point() -> None:

  """

  Point-sample a color band

  """

  ...

def eyedropper_depth(*args, prop_data_path: str = '') -> None:

  """

  Sample depth from the 3D view

  """

  ...

def eyedropper_driver(*args, mapping_type: str = 'SINGLE_MANY') -> None:

  """

  Pick a property to use as a driver target

  """

  ...

def eyedropper_grease_pencil_color(*args, mode: str = 'MATERIAL', material_mode: str = 'STROKE') -> None:

  """

  Sample a color from the Blender Window and create Grease Pencil material

  """

  ...

def eyedropper_id() -> None:

  """

  Sample a data-block from the 3D View to store in a property

  """

  ...

def jump_to_target_button() -> None:

  """

  Switch to the target object or bone

  """

  ...

def list_start_filter() -> None:

  """

  Start entering filter text for the list in focus

  """

  ...

def override_add_button(*args, all: bool = True) -> None:

  """

  Create an override operation

  """

  ...

def override_idtemplate_clear() -> None:

  """

  Delete the selected local override and relink its usages to the linked data-block if possible, else reset it and mark it as non editable

  """

  ...

def override_idtemplate_make() -> None:

  """

  Create a local override of the selected linked data-block, and its hierarchy of dependencies

  """

  ...

def override_idtemplate_reset() -> None:

  """

  Reset the selected local override to its linked reference values

  """

  ...

def override_remove_button(*args, all: bool = True) -> None:

  """

  Remove an override operation

  """

  ...

def reloadtranslation() -> None:

  """

  Force a full reload of UI translation

  """

  ...

def reset_default_button(*args, all: bool = True) -> None:

  """

  Reset this property's value to its default value

  """

  ...

def unset_property_button() -> None:

  """

  Clear the property and use default or generated value in operators

  """

  ...

def view_drop() -> None:

  """

  Drag and drop onto a data-set or item within the data-set

  """

  ...

def view_item_delete() -> None:

  """

  Delete selected list item

  """

  ...

def view_item_rename() -> None:

  """

  Rename the active item in the data-set view

  """

  ...

def view_item_select(*args, extend: bool = False, range_select: bool = False) -> None:

  """

  Activate selected view item

  """

  ...

def view_scroll() -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def view_start_filter() -> None:

  """

  Start entering filter text for the data-set in focus

  """

  ...
