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
from typing import Optional

from datatailr.wrapper import dt__User

# Datatailr User API Client
__client__ = dt__User()


class User:
    """
    Representing a Datatailr User.

    This class provides methods to interact with the Datatailr User API.
    It allows you to create, update, delete, and manage users within the Datatailr platform.

    Attributes:
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        name (str): The username of the user.
        email (str): The email address of the user.
        user_id (int): The unique identifier for the user.
        primary_group_id (int): The primary group of the user.
        is_system_user (bool): Indicates if the user is a system user.

    Static Methods:
        signed_user() -> Optional['User']:
            Retrieve the currently signed-in user, if available.
        add(name: str, first_name: str = None, last_name: str = None, email: str = None, password: str = None, primary_group_id: int = None, is_system_user: bool = False) -> 'User':
            Create a new user with the specified username, first name, last name, and email.
        get(name: str) -> 'User':
            Retrieve a user by their username.
        exists(name: str) -> bool:
            Check if a user exists by their username.
        ls() -> list:
            List all users available in the Datatailr platform.
        remove(name: str) -> None:
            Remove a user by their username.

    Instance Methods:
        verify() -> None:
            Refresh the user information from the Datatailr API.
    """

    def __init__(self, name):
        self.__name = name
        self.__first_name = None
        self.__last_name = None
        self.__email = None
        self.__user_id = None
        self.__primary_group_id = None
        self.__is_system_user = False
        self.__expiry__ = None
        self.__signature__ = None

        self.__refresh__()

    def __repr__(self):
        return (
            f"User(name={self.name}, first_name={self.first_name}, "
            f"last_name={self.last_name}, email={self.email}, "
            f"user_id={self.user_id}, primary_group_id={self.primary_group_id}, "
            f"is_system_user={self.is_system_user})"
        )

    def __str__(self):
        return f"<User: {self.name} | {self.user_id}>"

    def __eq__(self, other):
        if not isinstance(other, User):
            return NotImplemented
        return (
            self.user_id == other.user_id
            and self.name == other.name
            and self.email == other.email
            and self.primary_group_id == other.primary_group_id
            and self.is_system_user == other.is_system_user
            and self.first_name == other.first_name
            and self.last_name == other.last_name
        )

    def __refresh__(self):
        if not self.name:
            raise ValueError("Name is not set. Cannot refresh user.")
        user = __client__.get(self.name)
        if user:
            self.__name = user["name"]
            self.__first_name = user["first_name"]
            self.__last_name = user["last_name"]
            self.__email = user.get("email")
            self.__user_id = user["user_id"]
            self.__primary_group_id = user["primary_group_id"]
            self.__is_system_user = user["is_system"]

    @property
    def first_name(self):
        return self.__first_name

    @property
    def last_name(self):
        return self.__last_name

    @property
    def name(self):
        return self.__name

    @property
    def email(self):
        return self.__email

    @property
    def user_id(self):
        return self.__user_id

    @property
    def primary_group_id(self):
        return self.__primary_group_id

    @property
    def primary_group(self):
        if self.__primary_group_id is not None:
            from datatailr.group import Group

            return Group.get(self.__primary_group_id)
        return None

    @property
    def is_system_user(self):
        return self.__is_system_user

    @staticmethod
    def get(name: str) -> User:
        return User(name)

    @staticmethod
    def signed_user() -> User:
        user_signature_and_expiry = __client__.signed_user()
        if user_signature_and_expiry:
            user = User(name=user_signature_and_expiry["name"])
            user.__expiry__ = user_signature_and_expiry["expiry"]
            user.__signature__ = user_signature_and_expiry["signature"]
            return user

        raise PermissionError(
            "No signed user found. Please ensure you are signed in to Datatailr."
        )

    @staticmethod
    def add(
        name: str,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        primary_group: str,
        is_system_user: bool = False,
    ) -> Optional["User"]:
        if is_system_user:
            if password is not None:
                raise Warning(
                    "Password is not required for system users. It will be ignored."
                )
            new_user = __client__.add(
                name,
                first_name=first_name,
                last_name=last_name,
                email=email,
                primary_group=primary_group,
                system=is_system_user,
                json_enrichened=True,
            )
        else:
            new_user = __client__.add(
                name,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                primary_group=primary_group,
                system=is_system_user,
                json_enrichened=True,
            )

        return User(new_user["name"]) if new_user else None

    @staticmethod
    def exists(name: str) -> bool:
        return __client__.exists(name)

    @staticmethod
    def ls() -> list:
        users = __client__.ls()
        return [User.get(user["name"]) for user in users]

    @staticmethod
    def remove(name: str) -> None:
        __client__.rm(name)
        return None

    def verify(self) -> None:
        return __client__.verify(self.name, self.__expiry__, self.__signature__)
