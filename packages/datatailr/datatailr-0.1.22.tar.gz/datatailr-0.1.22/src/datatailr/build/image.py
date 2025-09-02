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
import re
from typing import Optional

from datatailr import ACL, User


class Image:
    """
    Represents a container image for a job.
    The image is defined based on its' python dependencies and two 'build scripts' expressed as Dockerfile commands.
    All attributes can be initialized with either a string or a file name.
    """

    def __init__(
        self,
        acl: Optional[ACL] = None,
        python_version: str = "3.12",
        python_requirements: str | list[str] = "",
        build_script_pre: str = "",
        build_script_post: str = "",
        branch_name: Optional[str] = None,
        commit_hash: Optional[str] = None,
        path_to_repo: Optional[str] = None,
        path_to_module: Optional[str] = None,
    ):
        self.python_version = python_version
        self.acl = acl
        self.python_requirements = python_requirements
        self.build_script_pre = build_script_pre
        self.build_script_post = build_script_post
        self.branch_name = branch_name
        self.commit_hash = commit_hash
        self.path_to_repo = path_to_repo
        self.path_to_module = path_to_module

    def __repr__(self):
        return f"Image(acl={self.acl},)"

    @property
    def python_version(self):
        return self._python_version

    @python_version.setter
    def python_version(self, value: str):
        if not isinstance(value, str):
            raise TypeError("python_version must be a string.")
        if not re.match(r"^\d+\.\d+(\.\d+)?$", value):
            raise ValueError("Invalid python_version format. Expected format: X.Y[.Z]")
        self._python_version = value

    @property
    def python_requirements(self):
        return self._python_requirements

    @python_requirements.setter
    def python_requirements(self, value: str | list[str]):
        if isinstance(value, str) and os.path.isfile(value):
            with open(value, "r") as f:
                value = f.read()
        elif isinstance(value, list):
            value = "\n".join(value)
        if not isinstance(value, str):
            raise TypeError(
                "python_requirements must be a string or a file path to a requirements file."
            )
        self._python_requirements = value

    @property
    def build_script_pre(self):
        return self._build_script_pre

    @build_script_pre.setter
    def build_script_pre(self, value: str):
        if not isinstance(value, str):
            raise TypeError(
                "build_script_pre must be a string or a file path to a script file."
            )
        if os.path.isfile(value):
            with open(value, "r") as f:
                value = f.read()
        self._build_script_pre = value

    @property
    def build_script_post(self):
        return self._build_script_post

    @build_script_post.setter
    def build_script_post(self, value: str):
        if not isinstance(value, str):
            raise TypeError(
                "build_script_post must be a string or a file path to a script file."
            )
        if os.path.isfile(value):
            with open(value, "r") as f:
                value = f.read()
        self._build_script_post = value

    @property
    def acl(self):
        return self._acl

    @acl.setter
    def acl(self, value: Optional[ACL]):
        if value is None:
            signed_user = User.signed_user()
            if signed_user is None:
                raise ValueError(
                    "ACL cannot be None. Please provide a valid ACL or ensure a user is signed in."
                )
        elif not isinstance(value, ACL):
            raise TypeError("acl must be an instance of ACL.")
        self._acl = value or ACL(signed_user)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if (
                key in ["branch_name", "commit_hash", "path_to_repo", "path_to_module"]
                and value is not None
                and not isinstance(value, str)
            ):
                raise TypeError(f"{key} must be a string or None.")
            if not hasattr(self, key):
                raise AttributeError(
                    f"'{self.__class__.__name__}' object has no attribute '{key}'"
                )
            setattr(self, key, value)

    def to_dict(self):
        """
        Convert the Image instance to a dictionary representation.
        """
        return {
            "acl": self.acl.to_dict(),
            "python_version": self.python_version,
            "python_requirements": self.python_requirements,
            "build_script_pre": self.build_script_pre,
            "build_script_post": self.build_script_post,
            "branch_name": self.branch_name,
            "commit_hash": self.commit_hash,
            "path_to_repo": self.path_to_repo,
            "path_to_module": self.path_to_module,
        }

    def to_json(self):
        """
        Convert the Image instance to a JSON string representation.
        """
        return json.dumps(self.to_dict(), indent=4)
