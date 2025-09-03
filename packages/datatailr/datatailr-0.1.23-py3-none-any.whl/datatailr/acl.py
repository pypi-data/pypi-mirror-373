# *************************************************************************
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
# *************************************************************************

from __future__ import annotations

import json
from typing import List, Optional, Union

from datatailr import Group, User


class ACL:
    """
    A class to represent an Access Control List (ACL) for managing permissions.
    """

    def __init__(
        self,
        user: Union[User, str],
        group: Optional[Union[Group, str]] = None,
        permissions: Optional[List[str]] = None,
    ):
        if user is None:
            user = User.signed_user()
        self.user = user if isinstance(user, User) else User.get(user)
        if self.user is not None:
            self.group = (
                group if group and isinstance(group, Group) else self.user.primary_group
            )
        self.permissions = permissions or "rwr---"

        self.__group_can_read = False
        self.__group_can_write = False
        self.__user_can_read = False
        self.__user_can_write = False
        self.__world_readable = False

        self.__parse_permissions_string()

    def __parse_permissions_string(self):
        """
        Parse the permissions and set the corresponding flags.
        """
        if isinstance(self.permissions, str):
            self.permissions = list(self.permissions)
        if len(self.permissions) != 6:
            raise ValueError(
                "Permissions must be a list of 6 characters. representing 'r', 'w', and '-' for user, group, and world."
            )
        self.__user_can_read = self.permissions[0] == "r"
        self.__user_can_write = self.permissions[1] == "w"
        self.__group_can_read = self.permissions[2] == "r"
        self.__group_can_write = self.permissions[3] == "w"
        self.__world_readable = self.permissions[4] == "r"
        self.__world_writable = self.permissions[5] == "w"

    def _set_permissions_string(self):
        """
        Set the permissions string based on the current flags.
        """
        self.permissions = (
            f"{'r' if self.__user_can_read else '-'}"
            f"{'w' if self.__user_can_write else '-'}"
            f"{'r' if self.__group_can_read else '-'}"
            f"{'w' if self.__group_can_write else '-'}"
            f"{'r' if self.__world_readable else '-'}"
            f"{'w' if self.__world_writable else '-'}"
        )

    def __repr__(self):
        return (
            f"ACL(user={self.user}, group={self.group}, permissions={self.permissions})"
        )

    def to_dict(self):
        return {
            "user": self.user.name,
            "group": self.group.name if self.group else "dtusers",
            "group_can_read": self.__group_can_read,
            "group_can_write": self.__group_can_write,
            "user_can_read": self.__user_can_read,
            "user_can_write": self.__user_can_write,
            "world_readable": self.__world_readable,
            "world_writable": self.__world_writable,
        }

    @classmethod
    def from_dict(cls, acl_dict: dict) -> ACL:
        """
        Create an ACL instance from a dictionary.
        """
        user = User(acl_dict["user"])
        group = Group.get(acl_dict["group"]) if "group" in acl_dict else None
        acl = cls(user=user, group=group)
        acl.__group_can_read = acl_dict.get("group_can_read", False)
        acl.__group_can_write = acl_dict.get("group_can_write", False)
        acl.__user_can_read = acl_dict.get("user_can_read", False)
        acl.__user_can_write = acl_dict.get("user_can_write", False)
        acl.__world_readable = acl_dict.get("world_readable", False)
        acl.__world_writable = acl_dict.get("world_writable", False)
        acl._set_permissions_string()
        return acl

    def to_json(self):
        return json.dumps(self.to_dict())
