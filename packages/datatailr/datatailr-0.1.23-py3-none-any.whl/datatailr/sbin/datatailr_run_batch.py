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

import importlib
import os

from datatailr.logging import DatatailrLogger

logger = DatatailrLogger(os.path.abspath(__file__)).get_logger()


def run():
    logger.info("Running Datatailr batch job")
    entry_point = os.environ.get("DATATAILR_BATCH_ENTRYPOINT")
    batch_run_id = os.environ.get("DATATAILR_BATCH_RUN_ID")
    batch_id = os.environ.get("DATATAILR_BATCH_ID")
    job_id = os.environ.get("DATATAILR_JOB_ID")
    logger.info(f"Batch run ID: {batch_run_id}, Batch ID: {batch_id}, Job ID: {job_id}")

    if entry_point is None:
        raise ValueError(
            "Environment variable 'DATATAILR_BATCH_ENTRYPOINT' is not set."
        )
    if batch_run_id is None:
        raise ValueError("Environment variable 'DATATAILR_BATCH_RUN_ID' is not set.")
    if batch_id is None:
        raise ValueError("Environment variable 'DATATAILR_BATCH_ID' is not set.")
    if job_id is None:
        raise ValueError("Environment variable 'DATATAILR_JOB_ID' is not set.")

    module_name, func_name = entry_point.split(":", 1)
    module = importlib.import_module(module_name)
    function = getattr(module, func_name)
    if not callable(function):
        raise ValueError(
            f"The function '{func_name}' in module '{module_name}' is not callable."
        )
    function()
    logger.info("Datatailr batch job completed successfully.")
