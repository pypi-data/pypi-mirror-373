import asyncio
import os
from collections.abc import Callable
from collections.abc import Coroutine
from datetime import timedelta
from typing import Any

from celery import Celery
from celery.schedules import crontab
from celery.signals import worker_init
from celery.signals import worker_shutdown

from amsdal_data.transactions.background.connections.base import AsyncWorkerConnectionBase
from amsdal_data.transactions.background.connections.base import WorkerConnectionBase
from amsdal_data.transactions.background.connections.base import WorkerMode
from amsdal_data.transactions.background.schedule.config import SCHEDULE_TYPE
from amsdal_data.transactions.background.schedule.config import ScheduleConfig
from amsdal_data.transactions.background.schedule.crontab import Crontab


class CeleryConnection(WorkerConnectionBase):
    def __init__(self, app: Celery | None = None) -> None:
        self.app = app if app is not None else Celery()
        self.scheduled_tasks: dict[str, dict[str, Any]] = {}

    def _convert_schedule(self, schedule: SCHEDULE_TYPE) -> Any:
        if not isinstance(schedule, (Crontab, int, float, timedelta)):  # noqa: UP038
            msg = 'schedule must be an instance of Crontab, timedelta, int, or float'
            raise ValueError(msg)

        if isinstance(schedule, Crontab):
            return crontab(
                minute=schedule.minute,
                hour=schedule.hour,
                day_of_week=schedule.day_of_week,
                day_of_month=schedule.day_of_month,
                month_of_year=schedule.month_of_year,
            )

        return schedule

    def register_transaction(self, func: Callable[..., Any], **transaction_kwargs: Any) -> None:
        """
        Registers a transaction with the specified function and transaction arguments.

        This method registers a Celery task for the given function and updates the task schedule
        if scheduling information is provided in the transaction arguments.

        Args:
            func (Callable[..., Any]): The function to register as a Celery task.
            **transaction_kwargs (Any): Additional keyword arguments for the transaction, including:
                - label (str, optional): A custom label for the task. Defaults to the function's module and name.
                - schedule_config (ScheduleConfig, optional): Configuration for scheduling the task.
                - schedule (SCHEDULE_TYPE, optional): Direct schedule for the task.

        Raises:
            ValueError: If `schedule_config` is provided and is not an instance of `ScheduleConfig`.
            ValueError: If `schedule` is not an instance of `Crontab`, `timedelta`, `int`, or `float`.

        Returns:
            None
        """
        task_name = transaction_kwargs.get('label') or f'{func.__module__}.{func.__name__}'
        self.app.task(func, name=task_name)

        if transaction_kwargs.get('schedule_config') or transaction_kwargs.get('schedule'):
            task_config = {
                'task': task_name,
            }

            if transaction_kwargs.get('schedule_config'):
                schedule_config = transaction_kwargs['schedule_config']
                if not isinstance(schedule_config, ScheduleConfig):
                    msg = 'schedule_config must be an instance of ScheduleConfig'
                    raise ValueError(msg)

                task_config['schedule'] = self._convert_schedule(schedule_config.schedule)

                if schedule_config.args:
                    task_config['args'] = schedule_config.args
                if schedule_config.kwargs:
                    task_config['kwargs'] = schedule_config.kwargs

            if transaction_kwargs.get('schedule'):
                task_config['schedule'] = self._convert_schedule(transaction_kwargs['schedule'])

            self.scheduled_tasks[task_name] = task_config
            self.app.conf.beat_schedule = self.scheduled_tasks

    def submit(
        self,
        func: Callable[..., Any],
        func_args: tuple[Any, ...],
        func_kwargs: dict[str, Any],
        transaction_kwargs: dict[str, Any],
    ) -> None:
        """
        Submits a task with the specified function, arguments, keyword arguments, and transaction arguments.

        This method submits a Celery task for the given function with the provided arguments and keyword arguments.
        The task is identified by a custom label if provided in the transaction arguments.

        Args:
            func (Callable[..., Any]): The function to submit as a Celery task.
            func_args (tuple[Any, ...]): The positional arguments to pass to the function.
            func_kwargs (dict[str, Any]): The keyword arguments to pass to the function.
            transaction_kwargs (dict[str, Any]): Additional keyword arguments for the transaction, including:
                - label (str, optional): A custom label for the task. Defaults to the function's module and name.

        Returns:
            None
        """
        task_name = transaction_kwargs.get('label') or f'{func.__module__}.{func.__name__}'
        task = self.app.tasks[task_name]
        task.apply_async(func_args, func_kwargs)

    def run_worker(
        self,
        init_function: Callable[..., None] | None = None,
        shutdown_function: Callable[..., None] | None = None,
        mode: WorkerMode = WorkerMode.EXECUTOR,
    ) -> None:
        """
        Runs the worker in the specified mode, optionally initializing it with the provided function.

        This method starts the Celery worker in the specified mode. If an initialization function is provided,
        it connects to the `worker_init` signal to run the initialization function when the worker starts.

        Args:
            init_function (Callable[..., None] | None, optional): A function to initialize the worker. Defaults to None.
            mode (WorkerMode, optional): The mode in which to run the worker. Defaults to WorkerMode.EXECUTOR.

        Returns:
            None
        """
        if init_function:
            worker_init.connect(init_function)

        if shutdown_function:
            worker_shutdown.connect(shutdown_function)

        if mode == WorkerMode.SCHEDULER:
            self.app.worker_main(argv=['beat'])

        elif mode == WorkerMode.HYBRID:
            self.app.worker_main(argv=['worker', '--beat', '--loglevel=INFO'])

        else:
            self.app.worker_main(argv=['worker', '--loglevel=INFO'])

    def _populate_default_env_vars(self, connection_kwargs: dict[str, Any]) -> dict[str, Any]:
        for parameter_name, env_name in [
            ('broker_url', 'CELERY_BACKEND_URL'),
        ]:
            connection_kwargs.setdefault(parameter_name, os.getenv(env_name))

        return connection_kwargs

    def connect(self, **kwargs: Any) -> None:
        """
        Configures and connects the Celery application with the provided keyword arguments.

        This method updates the Celery application configuration with the provided keyword arguments.
        It also populates default environment variables for the connection parameters if they are not
        explicitly provided.

        Args:
            **kwargs (Any): Keyword arguments for configuring the Celery application.

        Returns:
            None
        """
        self.app.conf.update(**self._populate_default_env_vars(kwargs))

    def disconnect(self) -> None:
        pass

    @property
    def is_connected(self) -> bool:
        return True

    @property
    def is_alive(self) -> bool:
        return True


def _to_sync(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return asyncio.run(func(*args, **kwargs))

    return wrapper


class AsyncCeleryConnection(AsyncWorkerConnectionBase):
    def __init__(self, app: Celery | None = None) -> None:
        self.app = app if app is not None else Celery()
        self.scheduled_tasks: dict[str, dict[str, Any]] = {}

    def _convert_schedule(self, schedule: SCHEDULE_TYPE) -> Any:
        if not isinstance(schedule, (Crontab, int, float, timedelta)):  # noqa: UP038
            msg = 'schedule must be an instance of Crontab, timedelta, int, or float'
            raise ValueError(msg)

        if isinstance(schedule, Crontab):
            return crontab(
                minute=schedule.minute,
                hour=schedule.hour,
                day_of_week=schedule.day_of_week,
                day_of_month=schedule.day_of_month,
                month_of_year=schedule.month_of_year,
            )

        return schedule

    def register_transaction(self, func: Callable[..., Any], **transaction_kwargs: Any) -> None:
        """
        Registers a transaction with the specified function and transaction arguments.

        This method registers a Celery task for the given function and updates the task schedule
        if scheduling information is provided in the transaction arguments.

        Args:
            func (Callable[..., Any]): The function to register as a Celery task.
            **transaction_kwargs (Any): Additional keyword arguments for the transaction, including:
                - label (str, optional): A custom label for the task. Defaults to the function's module and name.
                - schedule_config (ScheduleConfig, optional): Configuration for scheduling the task.
                - schedule (SCHEDULE_TYPE, optional): Direct schedule for the task.

        Raises:
            ValueError: If `schedule_config` is provided and is not an instance of `ScheduleConfig`.
            ValueError: If `schedule` is not an instance of `Crontab`, `timedelta`, `int`, or `float`.

        Returns:
            None
        """
        task_name = transaction_kwargs.get('label') or f'{func.__module__}.{func.__name__}'
        self.app.task(_to_sync(func), name=task_name)

        if transaction_kwargs.get('schedule_config') or transaction_kwargs.get('schedule'):
            task_config = {
                'task': task_name,
            }

            if transaction_kwargs.get('schedule_config'):
                schedule_config = transaction_kwargs['schedule_config']
                if not isinstance(schedule_config, ScheduleConfig):
                    msg = 'schedule_config must be an instance of ScheduleConfig'
                    raise ValueError(msg)

                task_config['schedule'] = self._convert_schedule(schedule_config.schedule)

                if schedule_config.args:
                    task_config['args'] = schedule_config.args
                if schedule_config.kwargs:
                    task_config['kwargs'] = schedule_config.kwargs

            if transaction_kwargs.get('schedule'):
                task_config['schedule'] = self._convert_schedule(transaction_kwargs['schedule'])

            self.scheduled_tasks[task_name] = task_config
            self.app.conf.beat_schedule = self.scheduled_tasks

    async def submit(
        self,
        func: Callable[..., Any],
        func_args: tuple[Any, ...],
        func_kwargs: dict[str, Any],
        transaction_kwargs: dict[str, Any],
    ) -> None:
        """
        Submits a task with the specified function, arguments, keyword arguments, and transaction arguments.

        This method submits a Celery task for the given function with the provided arguments and keyword arguments.
        The task is identified by a custom label if provided in the transaction arguments.

        Args:
            func (Callable[..., Any]): The function to submit as a Celery task.
            func_args (tuple[Any, ...]): The positional arguments to pass to the function.
            func_kwargs (dict[str, Any]): The keyword arguments to pass to the function.
            transaction_kwargs (dict[str, Any]): Additional keyword arguments for the transaction, including:
                - label (str, optional): A custom label for the task. Defaults to the function's module and name.

        Returns:
            None
        """
        task_name = transaction_kwargs.get('label') or f'{func.__module__}.{func.__name__}'
        task = self.app.tasks[task_name]
        task.apply_async(func_args, func_kwargs)

    async def run_worker(
        self,
        init_function: Coroutine[Any, Any, Any] | None = None,
        shutdown_function: Coroutine[Any, Any, Any] | None = None,
        mode: WorkerMode = WorkerMode.EXECUTOR,
    ) -> None:
        """
        Runs the worker in the specified mode, optionally initializing it with the provided function.

        This method starts the Celery worker in the specified mode. If an initialization function is provided,
        it connects to the `worker_init` signal to run the initialization function when the worker starts.

        Args:
            init_function (Coroutine[Any, Any, Any] | None, optional): A function to initialize the worker.
                Defaults to None.
            mode (WorkerMode, optional): The mode in which to run the worker. Defaults to WorkerMode.EXECUTOR.

        Returns:
            None
        """
        if init_function:
            worker_init.connect(lambda **kwargs: asyncio.run(init_function))  # noqa: ARG005

        if shutdown_function:
            worker_shutdown.connect(lambda **kwargs: asyncio.run(shutdown_function))  # noqa: ARG005

        if mode == WorkerMode.SCHEDULER:
            self.app.worker_main(argv=['beat'])

        elif mode == WorkerMode.HYBRID:
            self.app.worker_main(argv=['worker', '--beat', '--loglevel=INFO'])

        else:
            self.app.worker_main(argv=['worker', '--loglevel=INFO'])

    def _populate_default_env_vars(self, connection_kwargs: dict[str, Any]) -> dict[str, Any]:
        for parameter_name, env_name in [
            ('broker_url', 'CELERY_BACKEND_URL'),
        ]:
            connection_kwargs.setdefault(parameter_name, os.getenv(env_name))

        return connection_kwargs

    async def connect(self, **kwargs: Any) -> None:
        """
        Configures and connects the Celery application with the provided keyword arguments.

        This method updates the Celery application configuration with the provided keyword arguments.
        It also populates default environment variables for the connection parameters if they are not
        explicitly provided.

        Args:
            **kwargs (Any): Keyword arguments for configuring the Celery application.

        Returns:
            None
        """
        self.app.conf.update(**self._populate_default_env_vars(kwargs))

    async def disconnect(self) -> None:
        pass

    @property
    async def is_connected(self) -> bool:
        return True

    @property
    async def is_alive(self) -> bool:
        return True
