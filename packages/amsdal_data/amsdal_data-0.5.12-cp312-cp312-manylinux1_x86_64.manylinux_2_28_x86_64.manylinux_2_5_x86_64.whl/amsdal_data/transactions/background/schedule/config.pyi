from _typeshed import Incomplete
from amsdal_data.transactions.background.schedule.crontab import Crontab as Crontab
from datetime import timedelta
from typing import Any, TypeAlias

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
    schedule: Incomplete
    args: Incomplete
    kwargs: Incomplete
    def __init__(self, schedule: SCHEDULE_TYPE, args: tuple[Any] | None = None, kwargs: dict[str, Any] | None = None) -> None: ...
