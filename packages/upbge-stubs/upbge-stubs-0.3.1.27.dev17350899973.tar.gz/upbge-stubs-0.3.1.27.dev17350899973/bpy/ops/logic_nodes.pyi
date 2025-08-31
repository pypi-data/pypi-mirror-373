"""


Logic Nodes Operators
*********************

:func:`add_component`

:func:`add_game_property`

:func:`add_global_category`

:func:`add_global_property`

:func:`add_logic_tree_property`

:func:`add_portal_in`

:func:`add_portal_out`

:func:`add_socket`

:func:`add_template`

:func:`apply_logic_tree`

:func:`audio_system`

:func:`custom_mainloop`

:func:`custom_mainloop_tree`

:func:`custom_node_templates`

:func:`edit_custom_node`

:func:`find_logic_tree`

:func:`generate_code`

:func:`get_owner`

:func:`install_pyfmodex`

:func:`install_upbge_stubs`

:func:`install_uplogic`

NOTE: This may take a few seconds and requires internet connection.

  :File:            
    `addons_core/bge_netlogic/ops/installuplogic.py:35 <https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bge_netlogic/ops/installuplogic.py#L35>`_

:func:`key_selector`

:func:`load_font`

:func:`load_image`

:func:`load_sound`

:func:`move_game_property`

:func:`node_search`

:func:`open_donate`

:func:`open_github`

:func:`open_upbge_docs`

:func:`open_upbge_manual`

:func:`pack_new_tree`

WARNING: All Nodes connected to selection must be selected too

  :arg new_tree_name:
    New Tree Name

  :type new_tree_name:
    string, (optional, never None)

  :File:            
    `addons_core/bge_netlogic/ops/packnewtree.py:147 <https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bge_netlogic/ops/packnewtree.py#L147>`_

:func:`register_custom_node`

:func:`reload_components`

:func:`reload_texts`

:func:`remove_custom_node`

:func:`remove_game_property`

:func:`remove_global_category`

:func:`remove_global_property`

:func:`remove_logic_tree_property`

:func:`remove_socket`

:func:`reset_empty_scale`

:func:`save_custom_node`

:func:`start_ui_preview`

:func:`unapply_logic_tree`

"""

import typing

def add_component(*args, component: str = '') -> None:

  """

  Add a python Component to the selected object

  """

  ...

def add_game_property() -> None:

  """

  Adds a property available to the UPBGE

  """

  ...

def add_global_category() -> None:

  """

  Add a global value category

  """

  ...

def add_global_property() -> None:

  """

  Add a value accessible from anywhere

  """

  ...

def add_logic_tree_property() -> None:

  """

  Adds a property available to the UPBGE

  """

  ...

def add_portal_in(*args, portal_name: str = 'Portal', mode: str = '1') -> None:

  """

  Create a new portal

  """

  ...

def add_portal_out(*args, portal_name: str = '') -> None:

  """

  Create a new portal

  """

  ...

def add_socket(*args, socket_type: str = 'NLListItemSocket') -> None:

  """

  Add a socket to this node

  """

  ...

def add_template(*args, nl_template_name: str = '', owner: str = '') -> None:

  """

  Add a template

  """

  ...

def apply_logic_tree(*args, owner: str = '') -> None:

  """

  Apply the current tree to the selected objects.

  """

  ...

def audio_system() -> None:

  """

  Select the object this tree is applied to

  """

  ...

def custom_mainloop() -> None:

  """

  Use a custom Mainloop for this scene

  """

  ...

def custom_mainloop_tree() -> None:

  """

  Use a custom Mainloop for this scene

  """

  ...

def custom_node_templates() -> None:

  """

  Load Custom Logic Node Templates

  """

  ...

def edit_custom_node(*args, index: int = 0) -> None:

  """

  Edit Custom Logic Node

  """

  ...

def find_logic_tree(*args, tree_name: str = '') -> None:

  """

  Edit

  """

  ...

def generate_code(*args, uplogic_installed: bool = False) -> None:

  """

  Force generation of code, needed only after updating or if encountering issues

  """

  ...

def get_owner(*args, applied_object: str = '') -> None:

  """

  Select the object this tree is applied to

  """

  ...

def install_pyfmodex() -> None:

  """

  NOTE: This may take a few seconds and requires internet connection.

  """

  ...

def install_upbge_stubs() -> None:

  """

  Downloads the latest version of the upbge-stubs module to support autocomplet in your IDE.NOTE: This may take a few seconds and requires internet connection.

  """

  ...

def install_uplogic() -> None:

  """

  Downloads the latest version of the uplogic module required for running logic nodes.

  """

  ...

def key_selector(*args, keycode: str = '', is_socket: bool = True) -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def load_font(*args, filepath: str = '', filter_glob: str = '*args.ttf;*args.otf;') -> None:

  """

  Load an image file

  """

  ...

def load_image(*args, filepath: str = '', filter_glob: str = '*args.jpg;*args.png;*args.jpeg;*args.JPEG;') -> None:

  """

  Load an image file

  """

  ...

def load_sound(*args, filepath: str = '', filter_glob: str = '*args.wav;*args.mp3;*args.ogg*args') -> None:

  """

  Load a sound file

  """

  ...

def move_game_property(*args, index: int = 0, direction: str = '') -> None:

  """

  Move Game Property

  """

  ...

def node_search(*args, node: str = '') -> None:

  """

  Search for registered Logic Nodes

  """

  ...

def open_donate() -> None:

  """

  Please consider supporting this Add-On

  """

  ...

def open_github() -> None:

  """

  Get involved with development

  """

  ...

def open_upbge_docs() -> None:

  """

  UPBGE API Documentation

  """

  ...

def open_upbge_manual() -> None:

  """

  Manual on engine and node usage

  """

  ...

def pack_new_tree(*args, new_tree_name: typing.Any = 'NewTree') -> None:

  """

  Convert selected Nodes to a new tree. Will be applied to selected object.

  """

  ...

def register_custom_node(*args, text_name: str = '') -> None:

  """

  Register Custom Logic Node

  """

  ...

def reload_components() -> None:

  """

  Reload all components applied to this object

  """

  ...

def reload_texts() -> None:

  """

  Reload all externally saved scripts

  """

  ...

def remove_custom_node(*args, index: int = 0) -> None:

  """

  Remove Custom Logic Node

  """

  ...

def remove_game_property(*args, index: int = 0) -> None:

  """

  Remove this property

  """

  ...

def remove_global_category() -> None:

  """

  Remove a global value category

  """

  ...

def remove_global_property() -> None:

  """

  Remove a value accessible from anywhere

  """

  ...

def remove_logic_tree_property(*args, prop_index: int = 0) -> None:

  """

  Remove a value accessible from anywhere

  """

  ...

def remove_socket() -> None:

  """

  Remove this socket

  """

  ...

def reset_empty_scale() -> None:

  """

  Reset the volume scale

  """

  ...

def save_custom_node(*args, index: int = 0) -> None:

  """

  Save Custom Logic Node

  """

  ...

def start_ui_preview() -> None:

  """

  Show this canvas and its children. Children are determined by connected 'Widget' sockets, 'Condition' sockets don't matter

  """

  ...

def unapply_logic_tree(*args, tree_name: str = '', from_obj_name: str = '') -> None:

  """

  Remove the tree from the selected objects

  """

  ...
