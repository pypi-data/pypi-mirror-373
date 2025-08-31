"""


Utilities (bpy.utils)
*********************

This module contains utility functions specific to blender but
not associated with blenders internal data.

:func:`blend_paths`

:func:`escape_identifier`

:func:`flip_name`

:func:`unescape_identifier`

:func:`register_class`

:func:`register_cli_command`

:func:`unregister_cli_command`

:func:`resource_path`

:func:`unregister_class`

:func:`keyconfig_init`

:func:`keyconfig_set`

:func:`load_scripts`

:func:`modules_from_path`

:func:`preset_find`

:func:`preset_paths`

:func:`refresh_script_paths`

:func:`app_template_paths`

:func:`time_from_frame`

:func:`register_manual_map`

:func:`unregister_manual_map`

:func:`register_preset_path`

:func:`unregister_preset_path`

:func:`register_classes_factory`

:func:`register_submodule_factory`

:func:`register_tool`

:func:`make_rna_paths`

:func:`manual_map`

:func:`manual_language_code`

:func:`script_path_user`

:func:`extension_path_user`

:func:`script_paths`

:func:`smpte_from_frame`

:func:`smpte_from_seconds`

:func:`unregister_tool`

:func:`user_resource`

:func:`execfile`

:func:`expose_bundled_modules`

"""

from . import units

from . import previews

import typing

def blend_paths(*args, absolute: bool = False, packed: bool = False, local: bool = False) -> typing.List[str]:

  """

  Returns a list of paths to external files referenced by the loaded .blend file.

  """

  ...

def escape_identifier(string: str) -> str:

  """

  Simple string escaping function used for animation paths.

  """

  ...

def flip_name(name: str, *args, strip_digits: bool = False) -> str:

  """

  Flip a name between left/right sides, useful for
mirroring bone names.

  """

  ...

def unescape_identifier(string: str) -> str:

  """

  Simple string un-escape function used for animation paths.
This performs the reverse of :func:`escape_identifier`.

  """

  ...

def register_class(cls: typing.Any) -> None:

  """

  Register a subclass of a Blender type class.

  Note: If the class has a *register* class method it will be called
before registration.

  """

  ...

def register_cli_command(self, id: str, execute: typing.Callable) -> typing.Any:

  """

  Register a command, accessible via the (``-c`` / ``--command``) command-line argument.

  **Custom Commands**

  Registering commands makes it possible to conveniently expose command line
functionality via commands passed to (``-c`` / ``--command``).

  .. code::

    import os

    import bpy


    def sysinfo_print():
        \"\"\"
        Report basic system information.
        \"\"\"

        import pprint
        import platform
        import textwrap

        width = 80
        indent = 2

        print("Blender {:s}".format(bpy.app.version_string))
        print("Running on: {:s}-{:s}".format(platform.platform(), platform.machine()))
        print("Processors: {!r}".format(os.cpu_count()))
        print()

        # Dump `bpy.app`.
        for attr in dir(bpy.app):
            if attr.startswith("_"):
                continue
            # Overly verbose.
            if attr in {"handlers", "build_cflags", "build_cxxflags"}:
                continue

            value = getattr(bpy.app, attr)
            if attr.startswith("build_"):
                pass
            elif isinstance(value, tuple):
                pass
            else:
                # Otherwise ignore.
                continue

            if isinstance(value, bytes):
                value = value.decode("utf-8", errors="ignore")

            if isinstance(value, str):
                pass
            elif isinstance(value, tuple) and hasattr(value, "__dir__"):
                value = {
                    attr_sub: value_sub
                    for attr_sub in dir(value)
                    # Exclude built-ins.
                    if not attr_sub.startswith(("_", "n_"))
                    # Exclude methods.
                    if not callable(value_sub := getattr(value, attr_sub))
                }
                value = pprint.pformat(value, indent=0, width=width)
            else:
                value = pprint.pformat(value, indent=0, width=width)

            print("{:s}:\n{:s}\n".format(attr, textwrap.indent(value, " " * indent)))


    def sysinfo_command(argv):
        if argv and argv[0] == "--help":
            print("Print system information & exit!")
            return 0

        sysinfo_print()
        return 0


    cli_commands = []


    def register():
        cli_commands.append(bpy.utils.register_cli_command("sysinfo", sysinfo_command))


    def unregister():
        for cmd in cli_commands:
            bpy.utils.unregister_cli_command(cmd)
        cli_commands.clear()


    if __name__ == "__main__":
        register()

  **Using Python Argument Parsing**

  This example shows how the Python ``argparse`` module can be used with a custom command.

  Using ``argparse`` is generally recommended as it has many useful utilities and
generates a ``--help`` message for your command.

  .. code::

    import os
    import sys

    import bpy


    def argparse_create():
        import argparse

        parser = argparse.ArgumentParser(
            prog=os.path.basename(sys.argv[0]) + " --command keyconfig_export",
            description="Write key-configuration to a file.",
        )

        parser.add_argument(
            "-o", "--output",
            dest="output",
            metavar='OUTPUT',
            type=str,
            help="The path to write the keymap to.",
            required=True,
        )

        parser.add_argument(
            "-a", "--all",
            dest="all",
            action="store_true",
            help="Write all key-maps (not only customized key-maps).",
            required=False,
        )

        return parser


    def keyconfig_export(argv):
        parser = argparse_create()
        args = parser.parse_args(argv)

        # Ensure the key configuration is loaded in background mode.
        bpy.utils.keyconfig_init()

        bpy.ops.preferences.keyconfig_export(
            filepath=args.output,
            all=args.all,
        )

        return 0


    cli_commands = []


    def register():
        cli_commands.append(bpy.utils.register_cli_command("keyconfig_export", keyconfig_export))


    def unregister():
        for cmd in cli_commands:
            bpy.utils.unregister_cli_command(cmd)
        cli_commands.clear()


    if __name__ == "__main__":
        register()

  """

  ...

def unregister_cli_command(self, handle: typing.Any) -> None:

  """

  Unregister a CLI command.

  """

  ...

def resource_path(type: str, *args, major: int = bpy.app.version[0], minor: str = bpy.app.version[1]) -> str:

  """

  Return the base path for storing system files.

  """

  ...

def unregister_class(cls: typing.Any) -> None:

  """

  Unload the Python class from blender.

  Note: If the class has an *unregister* class method it will be called
before unregistering.

  """

  ...

def keyconfig_init() -> None:

  ...

def keyconfig_set(filepath: typing.Any, *args, report: typing.Any = None) -> None:

  ...

def load_scripts(*args, reload_scripts: bool = False, refresh_scripts: bool = False, extensions: bool = True) -> None:

  """

  Load scripts and run each modules register function.

  """

  ...

def modules_from_path(path: str, loaded_modules: typing.Any) -> typing.List[ModuleType]:

  """

  Load all modules in a path and return them as a list.

  """

  ...

def preset_find(name: typing.Any, preset_path: typing.Any, *args, display_name: typing.Any = False, ext: typing.Any = '.py') -> None:

  ...

def preset_paths(subdir: str) -> typing.List[str]:

  """

  Returns a list of paths for a specific preset.

  """

  ...

def refresh_script_paths() -> None:

  """

  Run this after creating new script paths to update sys.path

  """

  ...

def app_template_paths(*args, path: str = None) -> typing.Any:

  """

  Returns valid application template paths.

  """

  ...

def time_from_frame(frame: int, *args, fps: typing.Any = None, fps_base: typing.Any = None) -> typing.Any:

  """

  Returns the time from a frame number .

  If *fps* and *fps_base* are not given the current scene is used.

  """

  ...

def register_manual_map(manual_hook: typing.Any) -> None:

  ...

def unregister_manual_map(manual_hook: typing.Any) -> None:

  ...

def register_preset_path(path: str) -> bool:

  """

  Register a preset search path.

  """

  ...

def unregister_preset_path(path: str) -> bool:

  """

  Unregister a preset search path.

  """

  ...

def register_classes_factory(classes: typing.Any) -> None:

  """

  Utility function to create register and unregister functions
which simply registers and unregisters a sequence of classes.

  """

  ...

def register_submodule_factory(module_name: str, submodule_names: typing.List[str]) -> typing.Any:

  """

  Utility function to create register and unregister functions
which simply load submodules,
calling their register & unregister functions.

  Note: Modules are registered in the order given,
unregistered in reverse order.

  """

  ...

def register_tool(tool_cls: typing.Any, *args, after: typing.Any = None, separator: bool = False, group: bool = False) -> None:

  """

  Register a tool in the toolbar.

  """

  ...

def make_rna_paths(struct_name: str, prop_name: str, enum_name: str) -> typing.Any:

  """

  Create RNA "paths" from given names.

  """

  ...

def manual_map() -> None:

  ...

def manual_language_code(default: typing.Any = 'en') -> str:

  ...

def script_path_user() -> None:

  """

  returns the env var and falls back to home dir or None

  """

  ...

def extension_path_user(package: str, *args, path: str = '', create: bool = False) -> str:

  """

  Return a user writable directory associated with an extension.

  Note: This allows each extension to have its own user directory to store files.The location of the extension it self is not a suitable place to store files
because it is cleared each upgrade and the users may not have write permissions
to the repository (typically "System" repositories).

  """

  ...

def script_paths(*args, subdir: str = None, user_pref: bool = True, check_all: bool = False, use_user: bool = True, use_system_environment: bool = True) -> typing.List[str]:

  """

  Returns a list of valid script paths.

  """

  ...

def smpte_from_frame(frame: int, *args, fps: typing.Any = None, fps_base: typing.Any = None) -> str:

  """

  Returns an SMPTE formatted string from the *frame*:
``HH:MM:SS:FF``.

  If *fps* and *fps_base* are not given the current scene is used.

  """

  ...

def smpte_from_seconds(time: int, *args, fps: typing.Any = None, fps_base: typing.Any = None) -> str:

  """

  Returns an SMPTE formatted string from the *time*:
``HH:MM:SS:FF``.

  If *fps* and *fps_base* are not given the current scene is used.

  """

  ...

def unregister_tool(tool_cls: typing.Any) -> None:

  ...

def user_resource(resource_type: str, *args, path: str = '', create: bool = False) -> str:

  """

  Return a user resource path (normally from the users home directory).

  """

  ...

def execfile(filepath: str, *args, mod: typing.Any = None) -> typing.Any:

  """

  Execute a file path as a Python script.

  """

  ...

def expose_bundled_modules() -> None:

  """

  For Blender as a Python module, add bundled VFX library python bindings
to ``sys.path``. These may be used instead of dedicated packages, to ensure
the libraries are compatible with Blender.

  """

  ...
