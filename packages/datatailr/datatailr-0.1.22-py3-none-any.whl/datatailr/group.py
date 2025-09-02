# *************************************************************************
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
# *************************************************************************

from typing import Optional, Union

from datatailr.wrapper import dt__Group


# Datatailr Group API Client
__client__ = dt__Group()


class Group:
    """
    Representing a Datatailr Group.

    This class provides methods to interact with the Datatailr Group API.
    It allows you to create, update, delete, and manage groups within the Datatailr platform.

    Attributes:
        name (str): The name of the group.
        members (list): A list of members in the group.
        group_id (int): The unique identifier for the group.

    Static Methods:
        add(name: str) -> 'Group':
            Create a new group with the specified name.
        get(name: str) -> 'Group':
            Retrieve a group by its name.
        list() -> list:
            List all groups available in the Datatailr platform.
        remove(name: str) -> None:
            Remove a group by its name.
        exists(name: str) -> bool:
            Check if a group exists by its name.

    Instance Methods:
        add_users(usernames: list) -> None:
            Add users to the group.
        remove_users(usernames: list) -> None:
            Remove users from the group.
    """

    def __init__(self, name: str):
        self.__name: str = name
        self.__members: list = []
        self.__group_id: int | None = None

        self.__refresh__()

    def __repr__(self):
        return (
            f"Group(name={self.name}, members={self.members}, group_id={self.group_id})"
        )

    def __str__(self):
        return f"<Group: {self.name} | {self.group_id}>"

    def __eq__(self, other):
        if not isinstance(other, Group):
            return NotImplemented
        return (
            self.group_id == other.group_id
            and self.name == other.name
            and set(self.members) == set(other.members)
        )

    def __refresh__(self):
        if not self.name:
            raise ValueError("Name is not set. Cannot refresh group.")
        group = __client__.get(self.name)
        if group:
            self.__name = group["name"]
            self.__members = group["members"]
            self.__group_id = group["group_id"]
        else:
            raise ValueError(f"Group '{self.name}' does not exist.")

    @property
    def name(self) -> str:
        return self.__name

    @property
    def members(self) -> list:
        return self.__members

    @property
    def group_id(self) -> Optional[int]:
        return self.__group_id

    @staticmethod
    def get(name_or_id: Union[str, int]) -> Optional["Group"]:
        if isinstance(name_or_id, int):
            return next((g for g in Group.ls() if g.group_id == name_or_id), None)
        return Group(name_or_id)

    @staticmethod
    def add(name: str) -> Optional["Group"]:
        __client__.add(name)
        return Group.get(name)

    @staticmethod
    def ls() -> list:
        groups = __client__.ls()
        return [Group.get(group["name"]) for group in groups]

    @staticmethod
    def remove(name: str) -> None:
        __client__.rm(name)
        return None

    @staticmethod
    def exists(name: str) -> bool:
        return __client__.exists(name)

    def add_users(self, usernames: list) -> None:
        if not self.name:
            raise ValueError("Name is not set. Cannot add users.")
        __client__.add_users(self.name, ",".join(usernames))
        self.__refresh__()

    def remove_users(self, usernames: list) -> None:
        if not self.name:
            raise ValueError("Name is not set. Cannot remove users.")
        __client__.rm_users(self.name, ",".join(usernames))
        self.__refresh__()

    def is_member(self, user) -> bool:
        if not self.name:
            raise ValueError("Name is not set. Cannot check membership.")
        return (
            user.user_id in self.members
            if hasattr(user, "user_id")
            else user in self.members
        )
