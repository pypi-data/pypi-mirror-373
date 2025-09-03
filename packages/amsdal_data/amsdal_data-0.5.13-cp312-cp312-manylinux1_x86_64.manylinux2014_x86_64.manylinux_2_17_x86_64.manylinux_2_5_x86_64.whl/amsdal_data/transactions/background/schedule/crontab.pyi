from _typeshed import Incomplete

class Crontab:
    """
    Represents a crontab schedule.

    This class is used to define a crontab schedule with specific time intervals for minute, hour,
    day of the week, day of the month, and month of the year.

    Attributes:
        minute (str): The minute field of the crontab schedule. Defaults to '*'.
        hour (str): The hour field of the crontab schedule. Defaults to '*'.
        day_of_week (str): The day of the week field of the crontab schedule. Defaults to '*'.
        day_of_month (str): The day of the month field of the crontab schedule. Defaults to '*'.
        month_of_year (str): The month of the year field of the crontab schedule. Defaults to '*'.
    """
    minute: Incomplete
    hour: Incomplete
    day_of_week: Incomplete
    day_of_month: Incomplete
    month_of_year: Incomplete
    def __init__(self, minute: str = '*', hour: str = '*', day_of_week: str = '*', day_of_month: str = '*', month_of_year: str = '*') -> None: ...
