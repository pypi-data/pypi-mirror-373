# *************************************************************************
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
# *************************************************************************

import json
import os
import subprocess
from typing import Union

from datatailr.utils import is_dt_installed

API_JSON_PATH: Union[str, None] = None

if is_dt_installed() or os.path.exists("/opt/datatailr/etc/api.json"):
    API_JSON_PATH = os.path.join("/opt", "datatailr", "etc", "api.json")
    CLI_TOOL = "dt"
else:
    # For running local tests, use api.json from the repo and a mock CLI tool
    import sys

    if any("unittest" in arg for arg in sys.argv):
        API_JSON_PATH = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "..", "dt", "api.json"
        )
    CLI_TOOL = "echo"


def type_map(arg_type):
    mapping = {
        "String": "str",
        "file": "str",
        "boolean": "bool",
        "int": "int",
        "float": "float",
    }
    return mapping.get(arg_type, "str")


def add_quotes(arg):
    """Add quotes to the argument if it contains spaces or special characters."""
    if isinstance(arg, str) and (" " in arg or '"' in arg or "'" in arg):
        return f'"{arg}"'
    return str(arg)


def make_method(cmd_name, sub_name, sub_def):
    arg_names = sub_def.get("non_options", {}).get("arg_names", [])
    arg_types = sub_def.get("non_options", {}).get("arg_types", [])
    min_args = sub_def.get("non_options", {}).get("min", len(arg_names))
    max_args = sub_def.get("non_options", {}).get("max", len(arg_names))
    options = sub_def.get("options", [])
    option_names = [opt[1] for opt in options]
    description = sub_def.get("description", "")
    help_text = sub_def.get("help", "")
    return_type = "str"

    # Build docstring
    doc = f"""{description}\n\n{help_text}\n"""
    if arg_names:
        doc += "\nArgs:\n"
        for n, t in zip(arg_names, arg_types):
            doc += f"    {n} ({type_map(t)}):\n"
    if options:
        doc += "\nOptions:\n"
        for opt in options:
            short, long, opt_type = opt[:3]
            doc += f"    --{long} ({opt_type})\n"
    doc += f"\nReturns:\n    {return_type}\n"

    def method(self, *args, **kwargs):
        # Accept required args as either positional or keyword arguments
        all_args = list(args)
        used_kwargs = set()
        kwargs = {k.replace("_", "-"): v for k, v in kwargs.items()}
        # Fill missing positional args from kwargs if available
        for i in range(len(all_args), len(arg_names)):
            arg_name = arg_names[i]
            if arg_name in kwargs:
                all_args.append(kwargs[arg_name])
                used_kwargs.add(arg_name)
        # Argument count check
        missing = []
        if len(all_args) < min_args:
            for i in range(len(all_args), min_args):
                if i < len(arg_names):
                    missing.append(
                        f"{arg_names[i]}: {type_map(arg_types[i]) if i < len(arg_types) else 'str'}"
                    )
        if not (min_args <= len(all_args) <= max_args):
            msg = f"{cmd_name}{' ' + sub_name if sub_name else ''} expects between {min_args} and {max_args} arguments, got {len(all_args)}."
            if missing:
                msg += f" Missing: {', '.join(missing)}"
            raise TypeError(msg)
        # Argument type check
        for i, (arg, expected_type) in enumerate(zip(all_args, arg_types)):
            py_type = eval(type_map(expected_type))
            if not isinstance(arg, py_type):
                raise TypeError(
                    f"Argument '{arg_names[i]}' must be of type {py_type.__name__}, got {type(arg).__name__}"
                )
        # Disallow unexpected kwargs (only allow options and used arg-names)
        allowed_kwargs = set(option_names) | set(arg_names)
        unexpected_kwargs = set(kwargs.keys()) - allowed_kwargs
        if unexpected_kwargs:
            raise TypeError(
                f"{cmd_name}{' ' + sub_name if sub_name else ''} got unexpected keyword arguments: {', '.join(unexpected_kwargs)}. Expected: {', '.join(allowed_kwargs)}"
            )
        cmd = [self.cli_tool, cmd_name]
        if sub_name:
            cmd.append(sub_name)
        for arg in all_args:
            cmd.append(add_quotes(str(arg)))
        # Only pass option kwargs (not those used for required args)
        if "json" in allowed_kwargs:
            kwargs["json"] = True  # Ensure JSON output if 'json' is an option
        for k, v in kwargs.items():
            if k in option_names:
                # Find the option definition
                opt_def = next((opt for opt in options if opt[1] == k), None)
                if opt_def and opt_def[2] == "no_argument":
                    if v:
                        cmd.append(f"--{k}")
                    # If v is False, omit it (do nothing)
                else:
                    # For options that require a value
                    cmd.append(f"--{k}={v}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{result.stderr}")
        try:
            return json.loads(result.stdout) if result.stdout else None
        except json.JSONDecodeError:
            return result.stdout.strip()

    method.__doc__ = doc
    return method


def create_class(cmd_name, command):
    class_name = cmd_name.capitalize()
    sub_commands = command.get("sub_commands", {})
    # Create a new class with only cli_tool attribute
    cls = type(class_name, (object,), {"cli_tool": CLI_TOOL})
    if sub_commands:
        for sub_name, sub_def in sub_commands.items():
            sub_name = (
                sub_name  # Convert hyphens to underscores for Python method names
            )
            method = make_method(cmd_name, sub_name, sub_def)
            setattr(cls, sub_name.replace("-", "_"), method)
    else:
        method = make_method(cmd_name, None, command)
        setattr(cls, cmd_name, method)
    return cls


# Load API JSON and create classes at import time
if API_JSON_PATH and os.path.exists(API_JSON_PATH):
    with open(API_JSON_PATH, "r") as f:
        api = json.load(f)

    for cmd_name, command in api.items():
        cls = create_class(cmd_name, command)
        globals()["dt__" + cmd_name.capitalize()] = cls


class mock_cli_tool:
    """
    Mock CLI tool for local usage of the DataTailr platform.
    This function simulates the CLI tool behavior by returning a predefined response.
    """

    # make it possible to use any function, even if it doesn't eist in the class
    def mock_method(self, name, *args, **kwargs):
        def fun(*args, **kwargs):
            return {"mocked": name, "args": args, "kwargs": kwargs}

        return fun

    def __getattr__(self, name):
        return self.mock_method(name)


dt__User = globals().get("dt__User", mock_cli_tool)
dt__Group = globals().get("dt__Group", mock_cli_tool)
dt__Job = globals().get("dt__Job", mock_cli_tool)
dt__Blob = globals().get("dt__Blob", mock_cli_tool)
dt__Dns = globals().get("dt__Dns", mock_cli_tool)
dt__System = globals().get("dt__System", mock_cli_tool)
dt__Sms = globals().get("dt__Sms", mock_cli_tool)
dt__Email = globals().get("dt__Email", mock_cli_tool)
dt__Kv = globals().get("dt__Kv", mock_cli_tool)
dt__Log = globals().get("dt__Log", mock_cli_tool)
dt__Node = globals().get("dt__Node", mock_cli_tool)
dt__Tag = globals().get("dt__Tag", mock_cli_tool)
dt__Registry = globals().get("dt__Registry", mock_cli_tool)
dt__Service = globals().get("dt__Service", mock_cli_tool)
dt__Settings = globals().get("dt__Settings", mock_cli_tool)
