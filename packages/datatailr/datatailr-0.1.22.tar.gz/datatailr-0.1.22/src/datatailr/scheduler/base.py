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

from datetime import datetime
import importlib.util
import json
import os
import tempfile
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional, Tuple, Union

from datatailr import ACL, Environment, User, is_dt_installed
from datatailr.wrapper import dt__Job
from datatailr.scheduler.constants import DEFAULT_TASK_MEMORY, DEFAULT_TASK_CPU
from datatailr.build.image import Image
from datatailr.errors import BatchJobError
from datatailr.logging import DatatailrLogger
from datatailr.utils import run_shell_command

logger = DatatailrLogger(os.path.abspath(__file__)).get_logger()
__client__ = dt__Job()


def set_allow_unsafe_scheduling(allow: bool):
    """
    Set whether to allow unsafe scheduling of jobs.
    This is a global setting that affects how jobs are scheduled.
    """
    if allow:
        os.environ["DATATAILR_ALLOW_UNSAFE_SCHEDULING"] = "true"
    else:
        os.environ.pop("DATATAILR_ALLOW_UNSAFE_SCHEDULING", None)


class RepoValidationError(BatchJobError):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class JobType(Enum):
    """
    Enum representing different types of DataTailr jobs.
    """

    BATCH = "batch"
    SERVICE = "service"
    APP = "app"
    EXCEL = "excel"
    UNKNOWN = "unknown"

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"JobType.{self.name}('{self.value}')"


@dataclass
class Resources:
    """
    Represents the resources required for a job.
    """

    memory: str = DEFAULT_TASK_MEMORY
    cpu: float = DEFAULT_TASK_CPU


class EntryPoint:
    """
    Represents an entry point for a DataTailr job.
    This can be a function or a callable object.
    """

    def __init__(
        self,
        type: JobType,
        func: Callable,
    ):
        self.func = func
        self.module_name = func.__module__
        self.function_name = func.__name__
        self.type = type

        # Find the absolute path to the repository and then the relative path to the module.
        # This will be used in the creation of the code 'bundle' when building the image.
        module_spec = importlib.util.find_spec(func.__module__)
        if module_spec is not None and module_spec.origin is not None:
            package_root = module_spec.origin
        else:
            package_root = "."
        module_parts = self.module_name.split(".")
        for _ in module_parts:
            package_root = os.path.dirname(package_root)
        path_to_repo = run_shell_command(
            f"cd {package_root} && git rev-parse --show-toplevel"
        )[0]
        path_to_module = os.path.relpath(package_root, path_to_repo)
        self.path_to_repo = path_to_repo
        self.path_to_module = path_to_module

    def __call__(self, *args, **kwargs):
        os.environ.update(kwargs.pop("env", {}))
        if self.type == JobType.BATCH:
            module = importlib.import_module(self.module_name)
            func = getattr(module, self.function_name)
            return func(*args, **kwargs)

        elif self.type == JobType.SERVICE:
            raise NotImplementedError("Service jobs are not yet implemented.")

        elif self.type == JobType.APP:
            raise NotImplementedError("App jobs are not yet implemented.")

    def __repr__(self):
        return f"EntryPoint({self.function_name} from {self.module_name}, type={self.type})"

    def __str__(self):
        return f"{self.module_name}:{self.function_name}"


class Job:
    def __init__(
        self,
        name: str,
        environment: Optional[Environment] = Environment.DEV,
        image: Optional[Image] = None,
        run_as: Optional[Union[str, User]] = None,
        resources: Resources = Resources(memory="128m", cpu=0.25),
        acl: Optional[ACL] = None,
        python_version: str = "3.12",
        python_requirements: str = "",
        build_script_pre: str = "",
        build_script_post: str = "",
        type: Optional[JobType] = JobType.UNKNOWN,
        entrypoint: Optional[EntryPoint] = None,
        update_existing: bool = False,
    ):
        if environment is None:
            environment = Environment.DEV

        if update_existing:
            existing_job = self.__get_existing__(name, environment)
            if existing_job:
                self.from_dict(existing_job)
                return

        if run_as is None:
            run_as = User.signed_user()
        if environment is None:
            environment = Environment.DEV
        elif isinstance(environment, str):
            environment = Environment(environment.lower())
        if isinstance(environment, str):
            environment = Environment(environment)
        self.acl = acl or ACL(user=run_as)
        self.environment = environment
        self.name = name
        self.run_as = run_as
        self.resources = resources
        if image is None:
            image = Image(
                acl=self.acl,
                python_version=python_version,
                python_requirements=python_requirements,
                build_script_pre=build_script_pre,
                build_script_post=build_script_post,
            )
        self.image = image
        self.type = type if entrypoint is None else entrypoint.type
        self.entrypoint = entrypoint
        self.__id = str(uuid.uuid4())

    @property
    def id(self) -> str:
        """
        Unique identifier for the job.
        """
        return self.__id

    @classmethod
    def __get_existing__(
        cls, job_name: str, environment: Environment
    ) -> Optional[dict]:
        """
        Retrieve an existing job instance from the DataTailr platform.
        Based on the job name and environment.
        """
        job_list = __client__.ls(filter=f"name={job_name},environment={environment}")
        if not isinstance(job_list, list):
            return None
        if len(job_list) == 0:
            return None
        if len(job_list) > 1:
            raise BatchJobError(
                f"Multiple jobs found with name '{job_name}' in environment '{environment}'."
            )
        return job_list[0]

    def __repr__(self):
        return (
            f"Job(name={self.name}, environment={self.environment}, "
            f"run_as={self.run_as}, resources={self.resources}, "
            f"acl={self.acl}, type={self.type}, "
            f"entrypoint={self.entrypoint}, image={self.image})"
        )

    def to_dict(self):
        """
        Convert the Job instance to a dictionary representation.
        """
        job_dict = {
            "environment": str(self.environment),
            "image": self.image.to_dict(),
            "type": str(self.type) if self.type else None,
            "name": self.name,
            "run_as": self.run_as.name
            if isinstance(self.run_as, User)
            else self.run_as,
            "acl": self.acl.to_dict(),
            "memory": self.resources.memory,
            "cpu": self.resources.cpu,
        }
        if self.type != JobType.BATCH:
            job_dict["entrypoint"] = str(self.entrypoint) if self.entrypoint else None
            job_dict["image"] = (self.image,)
            job_dict["memory"] = (self.resources.memory,)
            job_dict["cpu"] = self.resources.cpu
        return job_dict

    def from_dict(self, job_dict: dict):
        self.name = job_dict["name"]
        self.image = job_dict["image"]

        environment = job_dict.get("environment", "dev")
        environment = Environment(environment.lower())
        self.environment = environment

        user = job_dict["run_as"]["name"]
        user = User(user.lower())
        self.run_as = user

        self.resources = Resources(memory=job_dict["memory"], cpu=job_dict["num_cpus"])
        acl = job_dict.get("acl", None)
        if acl is None:
            acl = ACL(user=self.run_as)
        else:
            acl = ACL.from_dict(acl)
        self.acl = acl
        self.python_requirements = (job_dict.get("python_requirements", ""),)
        self.build_script_pre = (job_dict.get("build_script_pre", ""),)
        self.build_script_post = (job_dict.get("build_script_post", ""),)
        self.type = JobType(job_dict.get("type", "unknown").lower())
        self.state = job_dict["state"]
        self.create_time = datetime.fromtimestamp(job_dict["create_time"] * 1e-6)
        self.version = job_dict["version"]
        self.__id = job_dict["id"]

    def to_json(self):
        """
        Convert the Job instance to a JSON string representation.
        """
        return json.dumps(self.to_dict())

    def verify_repo_is_ready(self) -> Tuple[str, str]:
        """
        Verify if the repository is ready for job execution.
        The check consists of two parts:
        1. Check if there are uncommitted changes in the repository.
        2. Check if the local commit matches the remote HEAD (the repo is synced with the remote).
        Returns a tuple of (branch: str, commit_hash: str).
        """
        path_to_repo = self.image.path_to_repo or "."
        local_commit = run_shell_command(f"cd {path_to_repo} && git rev-parse HEAD")[0]
        branch_name = run_shell_command(
            f"cd {path_to_repo} && git rev-parse --abbrev-ref HEAD"
        )[0]

        if os.getenv("DATATAILR_ALLOW_UNSAFE_SCHEDULING", "false").lower() == "true":
            return branch_name, local_commit
        return_code = run_shell_command(f"cd {path_to_repo} && git diff --exit-code")
        is_committed = return_code is not None and return_code[1] == 0

        if not is_committed:
            raise RepoValidationError(
                "Please commit your changes before running the job."
            )

        remote_commit = run_shell_command(
            f"cd {path_to_repo} && git ls-remote origin HEAD"
        )[0].split("\t")[0]

        if local_commit != remote_commit:
            raise RepoValidationError(
                "Please sync your local repository with the remote before running the job."
            )

        return branch_name, local_commit

    def __prepare__(self) -> str:
        branch_name, local_commit = self.verify_repo_is_ready()
        self.image.update(
            branch_name=branch_name,
            commit_hash=local_commit,
        )
        logger.info(
            f"Running job '{self.name}' in environment '{self.environment}' as '{self.run_as}'"
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
            temp_file.write(self.to_json().encode())
        return temp_file.name

    def get_schedule_args(self) -> dict:
        """
        Returns additional arguments for scheduling the job.
        Override or extend this method as needed.
        """
        return {}

    def __run_command__(self, command: str) -> Tuple[bool, str]:
        """
        Run a command in the context of the job.
        This is used to execute the job's entry point.
        """
        if not is_dt_installed():
            raise NotImplementedError(
                "DataTailr is not installed. Please install DataTailr to run this job."
            )
        try:
            temp_file_name = self.__prepare__()

            if command == "run":
                __client__.run(f"file://{temp_file_name}", **self.get_schedule_args())
            elif command == "save":
                __client__.save(f"file://{temp_file_name}", **self.get_schedule_args())
            elif command == "start":
                __client__.start(self.name, environment=self.environment)
            else:
                raise ValueError(f"Unknown command: {command}")
            os.remove(temp_file_name)
        except Exception as e:
            logger.error(f"Error running command '{command}': {e}")
            return False, str(e)
        return True, f"Job '{self.name}' {command}d successfully."

    def save(self) -> Tuple[bool, str]:
        """
        Save the job to the DataTailr platform.
        If the job already exists, it will be updated.
        The repository state is verified and an image is prepared for execution.
        """
        return self.__run_command__("save")

    def run(self) -> Tuple[bool, str]:
        """
        Run the job.
        This is equivalent to running job.save() and then job.start().
        """
        return self.__run_command__("run")

    def start(self) -> Tuple[bool, str]:
        """
        Start the job. This will start the job execution on a schedule for batches if a schedule was specified.
        For other types of jobs and for batches without a schedule the job will be run immediately.
        """
        return self.__run_command__("start")

    def promote(
        self,
        from_environment: Optional[Environment] = None,
        version: Optional[str | int] = None,
    ) -> Tuple[bool, str]:
        """
        Promote the job to the next environment.
        This method is used to promote a version of the job from one environment to the next one.
        If none of the environments to promote from are specified, it defaults to promote from all environments.
        """
        promote_kwargs = {}
        if version is not None:
            promote_kwargs["version"] = str(version)
        if from_environment is not None:
            promote_kwargs["environment"] = str(from_environment)
        try:
            __client__.promote(self.name, **promote_kwargs)
            return True, f"Job '{self.name}' promoted successfully."
        except Exception as e:
            logger.error(f"Error promoting job '{self.name}': {e}")
            return False, str(e)

    def versions(self, environment: Optional[Environment] = None) -> list[str] | None:
        """
        List all versions of the job in the specified environment.
        If no environment is specified, it lists versions across all environments.
        """
        command_kwargs = {}
        if environment is not None:
            command_kwargs["environment"] = str(environment)
        return __client__.versions(self.name, **command_kwargs)
