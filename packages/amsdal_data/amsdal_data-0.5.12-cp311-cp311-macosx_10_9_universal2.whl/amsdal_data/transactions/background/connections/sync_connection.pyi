from _typeshed import Incomplete
from amsdal_data.transactions.background.connections.base import WorkerConnectionBase as WorkerConnectionBase, WorkerMode as WorkerMode
from collections.abc import Callable as Callable
from typing import Any

logger: Incomplete

class SyncBackgroundTransactionConnection(WorkerConnectionBase):
    """
    Synchronous implementation of the WorkerConnectionBase.

    This class provides a synchronous implementation of the WorkerConnectionBase, which is used
    for registering transactions, submitting tasks, and running workers in different modes.
    """
    def __init__(self) -> None: ...
    def register_transaction(self, func: Callable[..., Any], **transaction_kwargs: Any) -> None: ...
    def submit(self, func: Callable[..., Any], func_args: tuple[Any, ...], func_kwargs: dict[str, Any], transaction_kwargs: dict[str, Any]) -> None:
        """
        Submits a task with the specified function, arguments, keyword arguments, and transaction arguments.

        This method executes the given function with the provided arguments and keyword arguments.
        It is a synchronous implementation and directly calls the function.

        Args:
            func (Callable[..., Any]): The function to execute.
            func_args (tuple[Any, ...]): The positional arguments to pass to the function.
            func_kwargs (dict[str, Any]): The keyword arguments to pass to the function.
            transaction_kwargs (dict[str, Any]): Additional keyword arguments for the transaction.

        Returns:
            None
        """
    def run_worker(self, init_function: Callable[..., None] | None = None, shutdown_function: Callable[..., None] | None = None, mode: WorkerMode = ...) -> None:
        """
        Logs a warning that running workers is not supported in synchronous mode.

        This method is a placeholder for running workers in synchronous mode. It logs a warning
        indicating that this operation is not supported.

        Args:
            init_function (Callable[..., None] | None, optional): A function to initialize the worker. Defaults to None.
            mode (WorkerMode, optional): The mode in which to run the worker. Defaults to WorkerMode.EXECUTOR.

        Returns:
            None
        """
    def connect(self, **kwargs: Any) -> None: ...
    def disconnect(self) -> None: ...
    @property
    def is_connected(self) -> bool: ...
    @property
    def is_alive(self) -> bool: ...
