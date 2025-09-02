# *************************************************************************
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
# *************************************************************************

import os

from datatailr.scheduler.constants import BATCH_JOB_ARGUMENTS


def get_available_env_args():
    """
    Get the available environment variables for batch job arguments.

    This function retrieves the environment variables that match the keys defined in DATATAILR_BATCH_JOB_ARGUMENTS.

    Returns:
        dict: A dictionary of available environment variables for batch jobs.
    """
    available_args = {}
    for key, value in os.environ.items():
        arg_key = key.replace("DATATAILR_BATCH_ARG_", "").lower()
        if arg_key in BATCH_JOB_ARGUMENTS:
            available_args[arg_key] = value
    return available_args
