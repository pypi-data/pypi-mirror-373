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

import os
import subprocess

from datatailr.logging import DatatailrLogger

logger = DatatailrLogger(os.path.abspath(__file__)).get_logger()


def run():
    logger.info("Starting Datatailr excel add-in...")
    entrypoint = os.environ.get("DATATAILR_ENTRYPOINT")
    hostname = os.environ.get("DATATAILR_HOST")

    if entrypoint is None:
        raise ValueError("Environment variable 'DATATAILR_ENTRYPOINT' is not set.")

    if hostname is None:
        raise ValueError("Environment variable 'DATATAILR_HOST' is not set.")

    entrypoint = f'./dt-excel.sh -n -H "{hostname}" -p 8080 "{entrypoint}"'
    logger.info(f"Running entrypoint: {entrypoint}")
    subprocess.run(entrypoint, shell=True)
