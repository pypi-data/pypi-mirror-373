##########################################################################
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
##########################################################################

from __future__ import annotations

import tempfile

from datatailr.wrapper import dt__Blob

# Datatailr Blob API Client
__client__ = dt__Blob()


class Blob:
    def ls(self, path: str) -> list[str]:
        """
        List files in the specified path.

        :param path: The path to list files from.
        :return: A list of file names in the specified path.
        """
        return __client__.ls(path)

    def get_file(self, name: str, path: str):
        """
        Copy a blob file to a local file.

        Args:
            name (str): The name of the blob to retrieve.
            path (str): The path to store the blob as a file.
        """
        return __client__.cp(f"blob://{name}", path)

    def put_file(self, name: str, path: str):
        """
        Copy a local file to a blob.

        Args:
            name (str): The name of the blob to create.
            path (str): The path of the local file to copy.
        """
        return __client__.cp(path, f"blob://{name}")

    def exists(self, name: str) -> bool:
        """
        Check if a blob exists.

        Args:
            name (str): The name of the blob to check.

        Returns:
            bool: True if the blob exists, False otherwise.
        """
        return __client__.exists(name)

    def delete(self, name: str):
        """
        Delete a blob.

        Args:
            name (str): The name of the blob to delete.
        """
        return __client__.rm(name)

    def get_blob(self, name: str):
        """
        Get a blob object.

        Args:
            name (str): The name of the blob to retrieve.

        Returns:
            Blob: The blob object.
        """
        # Since direct reading and writting of blobs is not implemented yet, we are using a temporary file.
        # This is a workaround to allow reading the blob content directly from the blob storage.

        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            self.get_file(name, temp_file.name)
            with open(temp_file.name, "r") as f:
                return f.read()

    def put_blob(self, name: str, blob):
        """
        Put a blob object into the blob storage.

        Args:
            name (str): The name of the blob to create.
            blob: The blob object to store.
        """
        # Since direct reading and writting of blobs is not implemented yet, we are using a temporary file.
        # This is a workaround to allow writing the blob content directly to the blob storage.
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            with open(temp_file.name, "w") as f:
                f.write(blob)
            self.put_file(name, temp_file.name)
