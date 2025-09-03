from _typeshed import Incomplete
from amsdal_data.transactions.background.connections.base import AsyncWorkerConnectionBase as AsyncWorkerConnectionBase, WorkerConnectionBase as WorkerConnectionBase, WorkerMode as WorkerMode
from amsdal_data.transactions.background.schedule.config import SCHEDULE_TYPE as SCHEDULE_TYPE, ScheduleConfig as ScheduleConfig
from amsdal_data.transactions.background.schedule.crontab import Crontab as Crontab
from celery import Celery
from collections.abc import Callable as Callable, Coroutine
from typing import Any

class CeleryConnection(WorkerConnectionBase):
    app: Incomplete
    scheduled_tasks: dict[str, dict[str, Any]]
    def __init__(self, app: Celery | None = None) -> None: ...
    def _convert_schedule(self, schedule: SCHEDULE_TYPE) -> Any: ...
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
    def submit(self, func: Callable[..., Any], func_args: tuple[Any, ...], func_kwargs: dict[str, Any], transaction_kwargs: dict[str, Any]) -> None:
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
    def run_worker(self, init_function: Callable[..., None] | None = None, shutdown_function: Callable[..., None] | None = None, mode: WorkerMode = ...) -> None:
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
    def _populate_default_env_vars(self, connection_kwargs: dict[str, Any]) -> dict[str, Any]: ...
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
    def disconnect(self) -> None: ...
    @property
    def is_connected(self) -> bool: ...
    @property
    def is_alive(self) -> bool: ...

def _to_sync(func: Callable[..., Any]) -> Callable[..., Any]: ...

class AsyncCeleryConnection(AsyncWorkerConnectionBase):
    app: Incomplete
    scheduled_tasks: dict[str, dict[str, Any]]
    def __init__(self, app: Celery | None = None) -> None: ...
    def _convert_schedule(self, schedule: SCHEDULE_TYPE) -> Any: ...
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
    async def submit(self, func: Callable[..., Any], func_args: tuple[Any, ...], func_kwargs: dict[str, Any], transaction_kwargs: dict[str, Any]) -> None:
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
    async def run_worker(self, init_function: Coroutine[Any, Any, Any] | None = None, shutdown_function: Coroutine[Any, Any, Any] | None = None, mode: WorkerMode = ...) -> None:
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
    def _populate_default_env_vars(self, connection_kwargs: dict[str, Any]) -> dict[str, Any]: ...
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
    async def disconnect(self) -> None: ...
    @property
    async def is_connected(self) -> bool: ...
    @property
    async def is_alive(self) -> bool: ...
