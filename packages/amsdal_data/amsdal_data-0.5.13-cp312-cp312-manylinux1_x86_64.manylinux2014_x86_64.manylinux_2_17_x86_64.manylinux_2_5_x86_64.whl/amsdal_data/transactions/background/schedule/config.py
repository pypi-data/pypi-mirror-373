from datetime import timedelta
from typing import Any
from typing import TypeAlias

from amsdal_data.transactions.background.schedule.crontab import Crontab

SCHEDULE_TYPE: TypeAlias = float | int | Crontab | timedelta


class ScheduleConfig:
    """
    Configuration for scheduling tasks.

    This class is used to define the schedule configuration for tasks, including the schedule type,
    positional arguments, and keyword arguments.

    Attributes:
        schedule (SCHEDULE_TYPE): The schedule type, which can be a float, int, Crontab, or timedelta.
        args (tuple[Any] | None): The positional arguments for the task. Defaults to None.
        kwargs (dict[str, Any] | None): The keyword arguments for the task. Defaults to None.
    """

    def __init__(
        self,
        schedule: SCHEDULE_TYPE,
        args: tuple[Any] | None = None,
        kwargs: dict[str, Any] | None = None,
    ) -> None:
        self.schedule = schedule
        self.args = args
        self.kwargs = kwargs
