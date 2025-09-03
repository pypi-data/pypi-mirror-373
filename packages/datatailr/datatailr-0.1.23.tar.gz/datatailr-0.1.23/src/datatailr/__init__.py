# *************************************************************************
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
# *************************************************************************

from datatailr.wrapper import dt__System, mock_cli_tool
from datatailr.group import Group
from datatailr.user import User
from datatailr.acl import ACL
from datatailr.blob import Blob
from datatailr.build import Image
from datatailr.utils import Environment, is_dt_installed
from datatailr.version import __version__

system = dt__System()
if isinstance(system, mock_cli_tool):
    __provider__ = "not installed"
else:
    __provider__ = system.provider()

__all__ = [
    "ACL",
    "Blob",
    "Environment",
    "Group",
    "Image",
    "User",
    "__version__",
    "__provider__",
    "is_dt_installed",
]
