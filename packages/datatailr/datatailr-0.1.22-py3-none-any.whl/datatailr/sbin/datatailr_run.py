#!/usr/bin/env python3

# *************************************************************************
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
# *************************************************************************


# The purpose of this script is to be the entrypoint for all jobs running on datatailr.
# The main functions of the script are:
#     1. Create a linux user and group for the job.
#     2. Set the environment variables for the job.
#     3. Run the job in a separate process, as the newly created user and pass all relevant environment variables.
# There are muliple environment variables which are required for the job to run.
# Some of them are necessary for the setup stage, which is executed directly in this script as the linux root user.
# Others are passed to the job script, which is executed in a separate process with only the users' privileges and not as a root user.
#
# Setup environment variables:
#     DATATAILR_USER - the user under which the job will run.
#     DATATAILR_GROUP - the group under which the job will run.
#     DATATAILR_UID - the user ID of the user as it is defined in the system.
#     DATATAILR_GID - the group ID of the group as it is defined in the system.
#     DATATAILR_JOB_TYPE - the type of job to run. (batch\service\app\excel\IDE)
# Job environment variables (not all are always relevant, depending on the job type):
#     DATATAILR_BATCH_RUN_ID - the unique identifier for the batch run.
#     DATATAILR_BATCH_ID - the unique identifier for the batch.
#     DATATAILR_JOB_ID - the unique identifier for the job.


import os
import sys
from typing import Tuple
from datatailr.logging import DatatailrLogger


logger = DatatailrLogger(os.path.abspath(__file__)).get_logger()


def get_env_var(name: str, default: str | None = None) -> str:
    """
    Get an environment variable.
    If the variable is not set, raise an error.
    """
    if name not in os.environ:
        if default is not None:
            return default
        logger.error(f"Environment variable '{name}' is not set.")
        raise ValueError(f"Environment variable '{name}' is not set.")
    return os.environ[name]


def create_user_and_group() -> Tuple[str, str]:
    """
    Create a user and group for the job.
    The user and group names are taken from the environment variables DATATAILR_USER and DATATAILR_GROUP.
    The group and user are created with the same uid and gid as passed in the environment variables DATATAILR_UID and DATATAILR_GID.
    If the user or group already exists, do nothing.
    """
    user = get_env_var("DATATAILR_USER")
    group = get_env_var("DATATAILR_GROUP")
    uid = get_env_var("DATATAILR_UID")
    gid = get_env_var("DATATAILR_GID")

    # Create group if it does not exist
    os.system(f"getent group {group} || groupadd {group} -g {gid} -o")

    # Create user if it does not exist
    os.system(
        f"getent passwd {user} || useradd -g {group} -s /bin/bash -m {user} -u {uid} -o"
    )
    return user, group


def run_command_as_user(command: str, user: str, env_vars: dict):
    """
    Run a command as a specific user with the given environment variables.
    """
    env_vars.update({"PATH": get_env_var("PATH")})
    env_vars.update({"PYTHONPATH": get_env_var("PYTHONPATH", "")})
    env_vars_str = " ".join(f"{key}='{value}'" for key, value in env_vars.items())
    full_command = f"sudo -u {user} {env_vars_str} {command}"
    logger.debug(f"Running command: {full_command}")
    status = os.system(full_command)
    if status != 0:
        logger.error(f"Command failed with status {status / 256:g}")
        sys.exit(1)


def main():
    user, _ = create_user_and_group()
    job_type = get_env_var("DATATAILR_JOB_TYPE")

    job_name = get_env_var("DATATAILR_JOB_NAME")
    job_id = get_env_var("DATATAILR_JOB_ID")

    if job_type == "batch":
        run_id = get_env_var("DATATAILR_BATCH_RUN_ID")
        batch_id = get_env_var("DATATAILR_BATCH_ID")
        entrypoint = get_env_var("DATATAILR_BATCH_ENTRYPOINT")
        env = {
            "DATATAILR_BATCH_RUN_ID": run_id,
            "DATATAILR_BATCH_ID": batch_id,
            "DATATAILR_JOB_ID": job_id,
            "DATATAILR_BATCH_ENTRYPOINT": entrypoint,
        }
        run_command_as_user("datatailr_run_batch", user, env)
    elif job_type == "service":
        port = get_env_var("DATATAILR_SERVICE_PORT")
        entrypoint = get_env_var("DATATAILR_ENTRYPOINT")
        env = {
            "DATATAILR_JOB_NAME": job_name,
            "DATATAILR_JOB_ID": job_id,
            "DATATAILR_ENTRYPOINT": entrypoint,
            "DATATAILR_SERVICE_PORT": port,
        }
        run_command_as_user("datatailr_run_service", user, env)
    elif job_type == "app":
        entrypoint = get_env_var("DATATAILR_ENTRYPOINT")
        env = {
            "DATATAILR_JOB_NAME": job_name,
            "DATATAILR_JOB_ID": job_id,
            "DATATAILR_ENTRYPOINT": entrypoint,
        }
        run_command_as_user("datatailr_run_app", user, env)
    elif job_type == "excel":
        host = get_env_var("DATATAILR_HOST")
        entrypoint = get_env_var("DATATAILR_ENTRYPOINT")
        env = {
            "DATATAILR_JOB_NAME": job_name,
            "DATATAILR_JOB_ID": job_id,
            "DATATAILR_ENTRYPOINT": entrypoint,
            "DATATAILR_HOST": host,
        }
        run_command_as_user("datatailr_run_excel", user, env)
    elif job_type == "IDE":
        pass
    else:
        raise ValueError(f"Unknown job type: {job_type}")


if __name__ == "__main__":
    try:
        logger.debug("Starting job execution...")
        main()
        logger.debug("Job executed successfully.")
    except Exception as e:
        logger.error(f"Error during job execution: {e}")
        raise
