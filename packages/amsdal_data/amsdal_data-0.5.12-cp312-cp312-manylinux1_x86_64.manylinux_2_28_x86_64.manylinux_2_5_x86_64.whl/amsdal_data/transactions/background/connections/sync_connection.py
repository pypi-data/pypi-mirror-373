import logging
from collections.abc import Callable
from typing import Any

from amsdal_data.transactions.background.connections.base import WorkerConnectionBase
from amsdal_data.transactions.background.connections.base import WorkerMode

logger = logging.getLogger(__name__)


class SyncBackgroundTransactionConnection(WorkerConnectionBase):
    """
    Synchronous implementation of the WorkerConnectionBase.

    This class provides a synchronous implementation of the WorkerConnectionBase, which is used
    for registering transactions, submitting tasks, and running workers in different modes.
    """

    def __init__(self) -> None:
        pass

    def register_transaction(self, func: Callable[..., Any], **transaction_kwargs: Any) -> None:
        pass

    def submit(
        self,
        func: Callable[..., Any],
        func_args: tuple[Any, ...],
        func_kwargs: dict[str, Any],
        transaction_kwargs: dict[str, Any],  # noqa: ARG002
    ) -> None:
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
        return func(*func_args, **func_kwargs)

    def run_worker(
        self,
        init_function: Callable[..., None] | None = None,  # noqa: ARG002
        shutdown_function: Callable[..., None] | None = None,  # noqa: ARG002
        mode: WorkerMode = WorkerMode.EXECUTOR,  # noqa: ARG002
    ) -> None:
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
        logger.warning('SyncBackgroundTransactionConnection does not support running workers')

    def connect(self, **kwargs: Any) -> None:
        pass

    def disconnect(self) -> None:
        pass

    @property
    def is_connected(self) -> bool:
        return True

    @property
    def is_alive(self) -> bool:
        return True
