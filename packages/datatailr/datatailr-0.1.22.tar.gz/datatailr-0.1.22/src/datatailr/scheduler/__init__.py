# *************************************************************************
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
# *************************************************************************

r"""
Datatailr Scheduler Module
==========================

The `datatailr.scheduler` module provides a framework for scheduling and managing batch jobs.

The main job types are:
_______________________

- **Batch**: Represents a batch job that can be scheduled and executed.
  The job can include multiple tasks which can be run in parallel or sequentially.
- **Service**: Represents a service job that runs continuously.
- **App**: Represents a web app or a dashboard, which can be built using one of the supported frameworks,
  such as `Streamlit <https://streamlit.io/>`_, `Dash <https://dash.plotly.com/>`_, or `Panel <https://panel.holoviz.org/>`_.
- **Excel**: Represents an Excel add-in.
"""

from datatailr.errors import BatchJobError
from datatailr.scheduler.base import (
    EntryPoint,
    Environment,
    Job,
    JobType,
    Resources,
    set_allow_unsafe_scheduling,
)
from datatailr.scheduler.batch import Batch, BatchJob, DuplicateJobNameError
from datatailr.scheduler.batch_decorator import batch_decorator as batch_job
from datatailr.scheduler.schedule import Schedule

__all__ = [
    "Job",
    "JobType",
    "Environment",
    "Resources",
    "EntryPoint",
    "Batch",
    "BatchJob",
    "batch_job",
    "BatchJobError",
    "DuplicateJobNameError",
    "set_allow_unsafe_scheduling",
    "Schedule",
]
