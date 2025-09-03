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

import contextvars
import json
import os
from functools import reduce
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Union
import uuid

from datatailr import Image
from datatailr.errors import BatchJobError
from datatailr.logging import DatatailrLogger
from datatailr.scheduler.base import (
    ACL,
    EntryPoint,
    Environment,
    Job,
    JobType,
    Resources,
    User,
)
from datatailr.scheduler.constants import DEFAULT_TASK_CPU, DEFAULT_TASK_MEMORY
from datatailr.scheduler.arguments_cache import ArgumentsCache
from datatailr.scheduler.schedule import Schedule
from datatailr.utils import is_dt_installed

__DAG_CONTEXT__: contextvars.ContextVar = contextvars.ContextVar("dag_context")
__ARGUMENTS_CACHE__ = ArgumentsCache()
logger = DatatailrLogger(os.path.abspath(__file__)).get_logger()


def get_current_manager():
    return __DAG_CONTEXT__.get(None)


class CyclicDependencyError(BatchJobError):
    """
    Exception raised when a cyclic dependency is detected in the batch job dependencies.
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class DuplicateJobNameError(BatchJobError):
    """
    Exception raised when a job with a duplicate name is added to the batch.
    """

    def __init__(self, job_name: str):
        super().__init__(
            f"A job with the name '{job_name}' already exists in the batch."
        )
        self.job_name = job_name


class MissingDagError(BatchJobError):
    """
    Exception raised when a BatchJob is created outside the context of a Batch.
    """

    def __init__(self):
        super().__init__(
            "A BatchJob must be either created within the context of a Batch or a Batch object has to be provided as the dag argument."
        )


class CodePackageMismatchError(BatchJobError):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class BatchJob:
    """
    Represents a job within a batch job.

    This class can be extended to define specific configurations for each job in the batch.
    """

    def __init__(
        self,
        name: str,
        entrypoint: EntryPoint,
        resources: Optional[Resources] = None,
        dependencies: Sequence[Union[str, BatchJob]] = [],
        dag: Optional[Batch] = get_current_manager(),
        argument_mapping: Dict[str, str] = {},
    ):
        self.name = name
        self.entrypoint = entrypoint
        self.resources = resources
        self.dependencies: set = set(dependencies)
        if dag is None:
            raise MissingDagError()
        self.__id = dag.next_job_id
        self.dag = dag
        self.__args: Dict[str, Any] = {}
        self.dag.__BATCH_JOB_NAMES__[self.name] = self.__id
        self.dependencies = self.translate_dependencies()
        assert all(
            isinstance(dep, int) for dep in self.dependencies
        ), "All dependencies must be integers representing job IDs."
        self.dag.add_job(self)
        self.argument_mapping = argument_mapping or {}

    def __call__(self, *args, **kwds) -> BatchJob:
        """
        Allows the BatchJob instance to be called like a function, returning itself.
        This is useful for chaining or functional-style programming.
        """
        return self

    @property
    def args(self) -> Dict[str, Any]:
        """
        Returns the arguments for the BatchJob instance.
        """
        return self.__args or {}

    @args.setter
    def args(self, args: Dict[str, Any]):
        """
        Sets the arguments for the BatchJob instance.
        """
        if not isinstance(args, dict):
            raise TypeError(f"Expected a dictionary for args, got {type(args)}")
        self.__args = args

    @property
    def id(self) -> int:
        """
        Returns the unique identifier of the BatchJob instance.
        """
        return self.__id

    def alias(self, name: str) -> BatchJob:
        """
        Set an alias for the BatchJob instance.

        :param name: The alias name to set.
        """
        if name in self.dag.__BATCH_JOB_NAMES__:
            raise DuplicateJobNameError(name)
        assert self.dag.__BATCH_JOB_NAMES__.pop(self.name) == self.__id
        self.dag.__BATCH_JOB_NAMES__[name] = self.__id
        self.name = name
        return self

    def set_resources(
        self,
        resources: Optional[Resources] = None,
        memory: Optional[str] = None,
        cpu: Optional[float] = None,
    ) -> BatchJob:
        """
        Set the resources for the BatchJob instance.

        :param resources: The Resources instance to set.
        """
        if resources is not None:
            if not isinstance(resources, Resources):
                raise TypeError(f"Expected Resources instance, got {type(resources)}")
        else:
            resources = Resources(
                memory=memory or DEFAULT_TASK_MEMORY, cpu=cpu or DEFAULT_TASK_CPU
            )
        self.resources = resources
        return self

    def __repr__(self):
        return (
            f"BatchJob(name={self.name}, entrypoint={self.entrypoint}, "
            f"resources={self.resources}) (id={self.__id})"
        )

    def __getstate__(self) -> object:
        state = self.__dict__.copy()
        state.pop("dag", None)
        return state

    def __setstate__(self, state: dict):
        self.__dict__.update(state)

    def to_dict(self):
        """
        Convert the BatchJob instance to a dictionary representation.
        """
        return {
            "display_name": self.name,
            "name": self.name,
            "child_number": self.__id,
            "entrypoint": str(self.entrypoint),
            "memory": self.resources.memory if self.resources else DEFAULT_TASK_MEMORY,
            "cpu": self.resources.cpu if self.resources else DEFAULT_TASK_CPU,
            "depends_on": list(self.dependencies),
        }

    def to_json(self):
        """
        Convert the BatchJob instance to a JSON string representation.
        """
        return json.dumps(self.to_dict())

    def translate_dependencies(self) -> Set[int]:
        """
        Translate the dependencies of the BatchJob instance into a format suitable for the batch job.
        """

        def get_dependency_name(dep):
            if isinstance(dep, str):
                return dep
            elif isinstance(dep, BatchJob):
                return dep.name
            else:
                raise TypeError(f"Unsupported dependency type: {type(dep)}")

        return set(
            [
                self.dag.__BATCH_JOB_NAMES__[get_dependency_name(dep)]
                for dep in self.dependencies
            ]
        )

    def __add_dependency__(self, other):
        self.dependencies.add(other.__id)
        arg_name = self.argument_mapping.get(other.name, other.name)
        if arg_name is not None:
            self.__args[arg_name] = other

    def __lshift__(
        self, other: Sequence[BatchJob] | BatchJob
    ) -> Sequence[BatchJob] | BatchJob:
        if isinstance(other, list):
            for task in other:
                self.__add_dependency__(task)
        else:
            self.__add_dependency__(other)
        return other

    def __rshift__(
        self, other: Sequence[BatchJob] | BatchJob
    ) -> Sequence[BatchJob] | BatchJob:
        if isinstance(other, Sequence):
            for task in other:
                task.__add_dependency__(self)
        else:
            other.__add_dependency__(self)
        return other

    def __rrshift__(self, other: Sequence[BatchJob] | BatchJob) -> BatchJob:
        self.__lshift__(other)
        return self

    def __rlshift__(self, other: Sequence[BatchJob] | BatchJob) -> BatchJob:
        self.__rshift__(other)
        return self

    def __hash__(self):
        return self.__id

    def __lt__(self, other: BatchJob) -> bool:
        return self.__id < other.__id

    def run(self):
        """
        Execute the job's entrypoint.
        """
        if isinstance(self.entrypoint, EntryPoint):
            env = {
                "DATATAILR_BATCH_ID": str(self.dag.id),
                "DATATAILR_JOB_ID": str(self.__id),
                "DATATAILR_JOB_NAME": self.name,
            }
            self.entrypoint(env=env)
        else:
            raise TypeError(f"Invalid entrypoint type: {type(self.entrypoint)}")


class Batch(Job):
    """
    Represents a batch job in the scheduler.

    Inherits from Job and is used to define batch jobs with specific configurations.
    """

    def __init__(
        self,
        name: str,
        environment: Optional[Environment] = Environment.DEV,
        schedule: Optional[Schedule] = None,
        image: Optional[Image] = None,
        run_as: Optional[Union[str, User]] = None,
        resources: Resources = Resources(memory="100m", cpu=1),
        acl: Optional[ACL] = None,
        local_run: bool = False,
        python_requirements: str = "",
        build_script_pre: str = "",
        build_script_post: str = "",
    ):
        super().__init__(
            environment=environment,
            name=name,
            image=image,
            run_as=run_as,
            resources=resources,
            acl=acl,
            python_requirements=python_requirements,
            build_script_pre=build_script_pre,
            build_script_post=build_script_post,
            type=JobType.BATCH,
        )
        self.__jobs: List[BatchJob] = []
        self._auto_run = False
        self.__next_job_id = -1
        self.__BATCH_JOB_NAMES__: Dict[str, int] = {}
        self.__local_run = local_run
        self.__schedule = schedule

    @property
    def next_job_id(self):
        """
        Returns a generator for the next job ID in the batch.
        """
        self.__next_job_id += 1
        return self.__next_job_id

    def add_job(self, job: BatchJob):
        """
        Adds a job to the batch job.

        :param job: The BatchJob instance to add.
        """
        if not isinstance(job, BatchJob):
            raise TypeError(
                f"Only BatchJob instances can be added to a Batch. Got {type(job)} instead."
            )
        if self.get_job_by_name(job.name) is not None:
            raise DuplicateJobNameError(job.name)
        # Use the batch level resource values as defaults for jobs
        job.resources = job.resources or self.resources
        image_path_to_repo = self.image.path_to_repo
        image_path_to_module = self.image.path_to_module
        package_path_to_repo = job.entrypoint.path_to_repo
        package_path_to_module = job.entrypoint.path_to_module

        if image_path_to_repo is None:
            self.image.path_to_repo = package_path_to_repo
        elif package_path_to_repo != image_path_to_repo:
            raise CodePackageMismatchError(
                f"Function {job.entrypoint.function_name} is defined in a different package root: "
                f"{package_path_to_repo} != {image_path_to_repo}"
            )
        if image_path_to_module is None:
            self.image.path_to_module = package_path_to_module
        elif package_path_to_module != image_path_to_module:
            raise CodePackageMismatchError(
                f"Function {job.entrypoint.function_name} is defined in a different module: "
                f"{package_path_to_module} != {image_path_to_module}"
            )
        self.__jobs.append(job)

    def is_job_in(self, job: BatchJob) -> bool:
        return job in self.__jobs

    def get_job_by_name(self, job_name: str) -> Optional[BatchJob]:
        return next((job for job in self.__jobs if job.name == job_name), None)

    def to_dict(self):
        """
        Convert the Batch instance to a dictionary representation.
        """
        batch_dict = super().to_dict()
        batch_dict["jobs"] = [job.to_dict() for job in self.__jobs]
        batch_dict["schedule"] = str(self.__schedule) if self.__schedule else None
        return batch_dict

    def to_json(self):
        """
        Convert the Batch instance to a JSON string representation.
        """
        return json.dumps(self.to_dict(), indent=4)

    def __repr__(self):
        return (
            f"Batch(name={self.name}, environment={self.environment}, "
            f"run_as={self.run_as}, resources={self.resources}, "
            f"acl={self.acl}, {len(self.__jobs)} jobs)"
        )

    def set_autorun(self, auto_run):
        self._auto_run = auto_run

    def __enter__(self):
        self._token = __DAG_CONTEXT__.set(self)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        __DAG_CONTEXT__.reset(self._token)
        if self._auto_run:
            self.run()

    def __topological_sort__(self):
        jobs = {
            hash(job): set([hash(dep) for dep in job.dependencies])
            for job in self.__jobs
        }

        for k, v in jobs.items():
            v.discard(k)  # ignore self dependencies
        extra_items_in_deps = reduce(set.union, jobs.values()) - set(jobs.keys())
        jobs.update({item: set() for item in extra_items_in_deps})
        while True:
            ordered = set(item for item, dep in jobs.items() if not dep)
            if not ordered:
                break
            yield sorted(ordered)
            jobs = {
                item: (dep - ordered)
                for item, dep in jobs.items()
                if item not in ordered
            }
        if jobs:
            raise CyclicDependencyError(
                "A cyclic dependency exists amongst {}".format(jobs)
            )

    def get_schedule_args(self) -> Dict[str, Any]:
        if isinstance(self.__schedule, Schedule):
            args = {
                "at_minutes": self.__schedule.at_minutes,
                "every_minute": self.__schedule.every_minute,
                "at_hours": self.__schedule.at_hours,
                "every_hour": self.__schedule.every_hour,
                "weekdays": self.__schedule.weekdays,
                "day_of_month": self.__schedule.day_of_month,
                "in_month": self.__schedule.in_month,
                "every_month": self.__schedule.every_month,
                "timezone": self.__schedule.timezone,
                "run_after_job_uuid": self.__schedule.run_after_job_uuid,
                "run_after_job_name": self.__schedule.run_after_job_name,
                "run_after_job_condition": self.__schedule.run_after_job_condition,
            }
            args = {key: value for key, value in args.items() if value is not None}
            for key, value in args.items():
                if isinstance(value, list):
                    args[key] = ",".join(map(str, value))
            return args
        return {}

    def run(self) -> Tuple[bool, str]:
        def arg_name(arg: Union[BatchJob, str]) -> str:
            return arg.name if isinstance(arg, BatchJob) else arg

        def merged(dst: dict[str, str], src: dict[str, str]) -> dict[str, str]:
            # copy so we don't mutate the original mapping
            out = dict(dst)
            seen_vals = set(out.values())
            for k, v in src.items():
                if v not in seen_vals:
                    out[k] = v
                    seen_vals.add(v)
            return out

        args = {
            j.name: merged(
                j.argument_mapping, {k: arg_name(v) for k, v in j.args.items()}
            )
            for j in self.__jobs
        }

        __ARGUMENTS_CACHE__.add_arguments(self.id, args)
        if not self.__local_run and is_dt_installed():
            return super().run()
        else:
            os.environ["DATATAILR_BATCH_RUN_ID"] = uuid.uuid4().hex[:8]
            for step in self.__topological_sort__():
                for job_id in step:
                    job = self.__jobs[job_id]
                    logger.info(
                        f"Batch {self.name}, running job '{job.name}' in environment '{self.environment}' as '{self.run_as}'"
                    )
                    job.run()
            from datatailr.scheduler.batch_decorator import __FUNCTIONS_CREATED_IN_DAG__

            __FUNCTIONS_CREATED_IN_DAG__.clear()
            return True, ""
