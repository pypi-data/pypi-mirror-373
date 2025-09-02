##########################################################################
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
##########################################################################

from typing import Any
from datatailr.wrapper import dt__Job
import re


__CLIENT__ = dt__Job()


class Schedule:
    """
    Represents a schedule for batch jobs.
    """

    def __init__(
        self,
        cron_expression: str = "",
        at_minutes: list[int] | None = None,
        every_minute: int | None = None,
        at_hours: list[int] | None = None,
        every_hour: int | None = None,
        weekdays: list[str] | None = None,
        day_of_month: int | None = None,
        in_month: list[str] | None = None,
        every_month: int | None = None,
        timezone: str | None = None,
        run_after_job_uuid: str | None = None,
        run_after_job_name: str | None = None,
        run_after_job_condition: str | None = None,
    ):
        self.at_minutes = at_minutes
        self.every_minute = every_minute
        self.at_hours = at_hours
        self.every_hour = every_hour
        self.weekdays = weekdays
        self.day_of_month = day_of_month
        self.in_month = in_month
        self.every_month = every_month
        self.timezone = timezone
        self.run_after_job_uuid = run_after_job_uuid
        self.run_after_job_name = run_after_job_name
        self.run_after_job_condition = run_after_job_condition
        self.schedule_expression = None
        self.cron_expression = cron_expression

        self.__is_set__ = False

    def __str__(self) -> str:
        self.__compile__()
        return self.cron_expression

    def __repr__(self) -> str:
        self.__compile__()
        return f"Schedule(cron_expression={self.cron_expression}, timezone={self.timezone}) - {self.schedule_expression}"

    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)
        if name in [
            "at_minutes",
            "at_hours",
            "every_minute",
            "every_hour",
            "weekdays",
            "day_of_month",
            "in_month",
            "every_month",
        ]:
            self.__is_set__ = False

    def __compile__(self):
        if self.__is_set__:
            return
        argument_name = [
            "at_minutes",
            "at_hours",
            "every_minute",
            "every_hour",
            "weekdays",
            "day_of_month",
            "in_month",
            "every_month",
            "run_after_job_uuid",
            "run_after_job_name",
            "run_after_job_condition",
        ]
        arguments = {}

        for key in argument_name:
            if hasattr(self, key) and getattr(self, key) is not None:
                value = getattr(self, key)
                if isinstance(value, list):
                    value = ",".join(map(str, value))
                arguments[key] = value

        result = __CLIENT__.run("", cron_string=True, **arguments)
        match = re.match(r"^(.*?)\s*\((.*?)\)$", result)
        if match:
            cron_expression, schedule_expression = match.groups()
            self.cron_expression = "0 " + cron_expression.strip()
            self.schedule_expression = schedule_expression.strip()
        self.__is_set__ = True

    def get_cron_string(self) -> str:
        """
        Returns the compiled cron string.
        """
        self.__compile__()
        return self.cron_expression
