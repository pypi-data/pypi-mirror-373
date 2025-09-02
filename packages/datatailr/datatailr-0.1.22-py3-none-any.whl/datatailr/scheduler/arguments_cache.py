##########################################################################
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
##########################################################################

"""
Module for caching arguments passed to batch jobs.

This module provides two backends for caching:
1. In-memory cache for local runs.
2. Persistent cache using the dt__Blob module for remote runs.

The cache stores arguments as a dictionary of dictionaries, where the outer dictionary's keys are job names
and the inner dictionaries contain the arguments.

This module is for internal use of the datatailr package.
"""

from datatailr.dt_json import json
import os
import pickle
from typing import Any, Dict, Optional

from datatailr import is_dt_installed, Blob
from datatailr.errors import DatatailrError
from datatailr.logging import DatatailrLogger


__BLOB_STORAGE__ = Blob()
logger = DatatailrLogger(__name__).get_logger()


class CacheNotFoundError(DatatailrError):
    """Custom error for cache operations."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ArgumentsCache:
    def __init__(self, use_persistent_cache: bool = is_dt_installed()):
        """
        Initialize the ArgumentsCache.

        :param use_persistent_cache: If True, use the persistent cache backend. Otherwise, use in-memory cache.
        """
        self.use_persistent_cache = use_persistent_cache
        if not self.use_persistent_cache:
            # Create a temp folder, for local caching
            os.makedirs("/tmp/datatailr/batch/arguments", exist_ok=True)
            os.makedirs("/tmp/datatailr/batch/results", exist_ok=True)

    def add_arguments(self, batch_id: str, arguments: Dict[str, Any]):
        """
        Add arguments to the cache for a specific job and batch run.

        :param batch_run_id: Identifier for the batch run.
        :param job_name: Name of the job.
        :param arguments: Dictionary of arguments to store.
        """
        path = f"/tmp/datatailr/batch/arguments/{batch_id}.pkl"
        if self.use_persistent_cache:
            self._add_to_persistent_cache(path, arguments)
        else:
            with open(path, "wb") as f:
                pickle.dump(arguments, f)

    def get_arguments(
        self, batch_id: str, job: str, batch_run_id: Optional[str]
    ) -> Dict[str, Any]:
        """
        Retrieve arguments from the cache for a specific job and batch run.

        :param batch_run_id: Identifier for the batch run.
        :param job_name: Name of the job.
        :return: Dictionary of arguments.
        """
        logger.info(
            f"Retrieving arguments for {batch_id=}, {job=}, {batch_run_id=}, {self.use_persistent_cache=}"
        )
        path = f"/tmp/datatailr/batch/arguments/{batch_id}.pkl"
        if self.use_persistent_cache and isinstance(job, str):
            try:
                arg_keys = self._get_from_persistent_cache(path)
            except RuntimeError:
                return {}
        else:
            if not os.path.exists(path):
                raise CacheNotFoundError(
                    f"Cache file not found: {path}. Ensure that the arguments have been cached."
                )
            with open(path, "rb") as f:
                try:
                    arg_keys = pickle.load(f)
                except EOFError:
                    return {}
                if not isinstance(arg_keys, dict):
                    raise TypeError(
                        f"Expected a dictionary for arguments, got {type(arg_keys)}"
                    )
        if batch_run_id is None:
            return arg_keys[job]
        args = {
            name: self.get_result(batch_run_id, value)
            for name, value in arg_keys[job].items()
        }
        return args

    def add_result(self, batch_run_id: str, job: str, result: Any):
        """
        Add the result of a batch job to the cache.

        :param batch_run_id: Identifier for the batch run.
        :param job: Name of the job.
        :param result: Result of the batch job.
        """
        path = f"/tmp/datatailr/batch/results/{batch_run_id}_{job}.pkl"
        logger.info(
            f"Adding result for {batch_run_id=}, {job=}, {result=}, {self.use_persistent_cache=}"
        )
        if self.use_persistent_cache and isinstance(job, str):
            self._add_to_persistent_cache(path, result)
        else:
            with open(path, "wb") as f:
                pickle.dump(result, f)

    def get_result(self, batch_run_id: str, job: Any) -> Any:
        """
        Retrieve the result of a batch job from the cache.

        :param batch_run_id: Identifier for the batch run.
        :param job: Name of the job.
        :return: Result of the batch job.
        """
        path = f"/tmp/datatailr/batch/results/{batch_run_id}_{job}.pkl"
        if self.use_persistent_cache and isinstance(job, str):
            return self._get_from_persistent_cache(path)
        else:
            if not os.path.exists(path):
                return job
            with open(path, "rb") as f:
                try:
                    return pickle.load(f)
                except EOFError:
                    return None

    def _add_to_persistent_cache(self, path: str, blob: Any):
        """
        Add arguments to the persistent cache.
        This method serializes the blob using pickle and stores it in the Blob storage.
        :param path: Path in the Blob storage where the blob will be stored.
        :param blob: The blob to store, typically a dictionary of arguments.
        :raises TypeError: If the blob cannot be pickled.

        """
        path = path.replace("/tmp/", "")
        logger.info(f"Adding arguments to persistent cache for {path=}")
        __BLOB_STORAGE__.put_blob(path, json.dumps(blob))

    def _get_from_persistent_cache(self, path: str) -> Any:
        """
        Retrieve arguments from the persistent cache.

        :param path: Path in the Blob storage where the blob is stored.
        """
        path = path.replace("/tmp/", "")
        logger.info(f"Retrieving arguments from persistent cache for {path=}")
        data = __BLOB_STORAGE__.get_blob(path)
        return json.loads(data)
