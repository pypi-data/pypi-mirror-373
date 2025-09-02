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
import sys
import runpy
from importlib.resources import files

from datatailr.logging import DatatailrLogger


logger = DatatailrLogger(os.path.abspath(__file__)).get_logger()


def run():
    logger.info("Starting Datatailr app...")
    entrypoint = os.environ.get("DATATAILR_ENTRYPOINT")
    if entrypoint is None or ":" not in entrypoint:
        raise ValueError(
            "Environment variable 'DATATAILR_ENTRYPOINT' is not in the format 'module_name:file_name'."
        )

    module_name, file_name = entrypoint.split(":")

    script = files(module_name).joinpath(file_name)
    sys.argv = ["streamlit", "run", str(script), *sys.argv[1:]]
    logger.info(f"Running entrypoint: {entrypoint}")
    runpy.run_module("streamlit", run_name="__main__")
