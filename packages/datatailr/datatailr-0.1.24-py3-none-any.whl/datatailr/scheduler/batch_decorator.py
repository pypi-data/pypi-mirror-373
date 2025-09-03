# *************************************************************************
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
# *************************************************************************

import functools
import inspect
import os
from typing import Callable

from datatailr.logging import DatatailrLogger
from datatailr.scheduler.arguments_cache import ArgumentsCache, CacheNotFoundError
from datatailr.scheduler.base import EntryPoint, JobType, Resources
from datatailr.scheduler.batch import (
    BatchJob,
    get_current_manager,
)
from datatailr.scheduler.constants import DEFAULT_TASK_CPU, DEFAULT_TASK_MEMORY
from datatailr.scheduler.utils import get_available_env_args

__ARGUMENTS_CACHE__ = ArgumentsCache()
__FUNCTIONS_CREATED_IN_DAG__: dict[Callable, str] = {}
logger = DatatailrLogger(__name__).get_logger()


def batch_run_id() -> str:
    return os.getenv("DATATAILR_BATCH_RUN_ID", "unknown")


def dag_id(job: BatchJob) -> str:
    return os.getenv(
        "DATATAILR_BATCH_ID", __FUNCTIONS_CREATED_IN_DAG__.get(job, "unknown")
    )


def batch_decorator(memory: str = DEFAULT_TASK_MEMORY, cpu: float = DEFAULT_TASK_CPU):
    """
    Decorator to mark a function as a batch job.
    This decorator can be used to wrap functions that should be executed as part of batch jobs.
    """

    def decorator(func) -> BatchJob:
        spec = inspect.getfullargspec(func)
        signature = inspect.signature(func)
        varargs = spec.varargs
        varkw = spec.varkw
        parameters = signature.parameters

        @functools.wraps(func)
        def batch_main(*args, **kwargs):
            dag = get_current_manager()
            if dag is None:
                logger.info(f'Function "{func.__name__}" is being executed.')
                # There are two possible scenarios:
                # 1. The function is called directly, not as part of a batch job. In this case, the args and kwargs should be used.
                # 2. The function is called as part of a batch job - it was constructed as part of a DAG and is now being executed.
                env_args = get_available_env_args()
                all_function_args = [
                    v.name
                    for v in parameters.values()
                    if v.kind
                    not in (
                        inspect.Parameter.VAR_POSITIONAL,
                        inspect.Parameter.VAR_KEYWORD,
                    )
                ]
                final_args = list(args)

                for name, value in env_args.items():
                    if name in all_function_args:
                        if len(final_args) < len(all_function_args):
                            final_args.extend(
                                [None] * (len(all_function_args) - len(final_args))
                            )
                        final_args[all_function_args.index(name)] = value
                try:
                    final_kwargs = __ARGUMENTS_CACHE__.get_arguments(
                        dag_id(func),
                        os.getenv("DATATAILR_JOB_NAME", func.__name__),
                        os.getenv("DATATAILR_BATCH_RUN_ID"),
                    )
                except CacheNotFoundError:
                    final_kwargs = kwargs

                if varargs is not None and varkw is None:
                    for key in list(final_kwargs.keys()):
                        if key not in parameters:
                            final_args.append(final_kwargs.pop(key))

                # Some of the loaded arguments are actually args and not kwargs.
                if len(final_args) == len(parameters.keys()):
                    for i, arg_name in enumerate(parameters.keys()):
                        final_args[i] = final_kwargs.pop(arg_name, final_args[i])
                result = func(*final_args, **final_kwargs)
                __ARGUMENTS_CACHE__.add_result(
                    batch_run_id(),
                    os.getenv("DATATAILR_JOB_NAME", func.__name__),
                    result,
                )
                return result
            else:
                if varargs is not None:
                    all_args = {job.name: job for job in args}
                else:
                    all_args = dict(zip(spec.args, args)) | kwargs
                dag.set_autorun(True)

                job = BatchJob(
                    name=func.__name__,
                    entrypoint=EntryPoint(
                        JobType.BATCH,
                        func=func,
                    ),
                    resources=Resources(memory=memory, cpu=cpu),
                    dependencies=[
                        value.name
                        for _, value in all_args.items()
                        if isinstance(value, BatchJob)
                    ],
                    dag=dag,
                )
                job.args = all_args
                __FUNCTIONS_CREATED_IN_DAG__[job.entrypoint.func] = dag.id
                return job

        module = inspect.getmodule(func)
        if hasattr(module, "__batch_main__"):
            if func.__name__ in getattr(module, "__batch_main__"):
                raise ValueError(f"Duplicate batch main function {func.__name__}")
            module.__batch_main__[func.__name__] = batch_main  # type: ignore
        else:
            setattr(module, "__batch_main__", {func.__name__: batch_main})

        # The return type is a BatchJob, but we use type: ignore to avoid type checking issues
        return batch_main  # type: ignore

    return decorator
