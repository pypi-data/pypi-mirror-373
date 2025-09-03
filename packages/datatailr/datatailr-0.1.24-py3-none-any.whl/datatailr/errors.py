##########################################################################
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
##########################################################################


class DatatailrError(Exception):
    """Base class for all DataTailr exceptions."""

    pass


class BatchJobError(DatatailrError):
    """Exception raised for errors related to batch jobs."""

    pass


class ScheduleError(DatatailrError):
    """Exception raised for errors related to scheduling."""

    pass
