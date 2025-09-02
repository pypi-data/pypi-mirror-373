from amsdal_data.transactions.background.connections.base import AsyncWorkerConnectionBase as AsyncWorkerConnectionBase, WorkerConnectionBase as WorkerConnectionBase
from amsdal_utils.utils.singleton import Singleton
from collections.abc import Callable as Callable
from typing import Any

class BackgroundTransactionManager(metaclass=Singleton):
    __connection: WorkerConnectionBase | None
    __transactions_cache: list[tuple[Callable[..., Any], dict[str, Any]]]
    def __init__(self) -> None: ...
    def initialize_connection(self, *, raise_on_no_worker: bool = False) -> None:
        """Retrieve connection config from AmsdalConfigManager and initialize connection"""
    def register_connection(self, connection: WorkerConnectionBase) -> None:
        """
        Registers a worker connection and processes any cached transactions.

        This method sets the provided connection as the active worker connection. If there are any
        transactions cached from before the connection was established, it registers those transactions
        with the new connection and clears the cache.

        Args:
            connection (WorkerConnectionBase): The worker connection to register.

        Returns:
            None
        """
    def register_transaction(self, func: Callable[..., Any], **transaction_kwargs: Any) -> None:
        """
        Registers a transaction with the specified function and keyword arguments.

        If there is no active connection, the transaction is cached. Otherwise, it is registered
        immediately with the active connection.

        Args:
            func (Callable[..., Any]): The function to execute as part of the transaction.
            transaction_kwargs (Any): The keyword arguments to pass to the transaction function.

        Returns:
            None
        """
    @property
    def connection(self) -> WorkerConnectionBase:
        """
        Retrieves the active worker connection.

        This property returns the currently registered worker connection. If no connection is registered,
        it raises an AmsdalInitiationError.

        Returns:
            WorkerConnectionBase: The active worker connection.

        Raises:
            AmsdalInitiationError: If no worker connection is registered.
        """

class AsyncBackgroundTransactionManager(metaclass=Singleton):
    __connection: AsyncWorkerConnectionBase | None
    __transactions_cache: list[tuple[Callable[..., Any], dict[str, Any]]]
    def __init__(self) -> None: ...
    def initialize_connection(self, *, raise_on_no_worker: bool = False) -> None:
        """Retrieve connection config from AmsdalConfigManager and initialize connection"""
    def register_connection(self, connection: AsyncWorkerConnectionBase) -> None:
        """
        Registers a worker connection and processes any cached transactions.

        This method sets the provided connection as the active worker connection. If there are any
        transactions cached from before the connection was established, it registers those transactions
        with the new connection and clears the cache.

        Args:
            connection (AsyncWorkerConnectionBase): The worker connection to register.

        Returns:
            None
        """
    def register_transaction(self, func: Callable[..., Any], **transaction_kwargs: Any) -> None:
        """
        Registers a transaction with the specified function and keyword arguments.

        If there is no active connection, the transaction is cached. Otherwise, it is registered
        immediately with the active connection.

        Args:
            func (Callable[..., Any]): The function to execute as part of the transaction.
            transaction_kwargs (Any): The keyword arguments to pass to the transaction function.

        Returns:
            None
        """
    @property
    def connection(self) -> AsyncWorkerConnectionBase:
        """
        Retrieves the active worker connection.

        This property returns the currently registered worker connection. If no connection is registered,
        it raises an AmsdalInitiationError.

        Returns:
            AsyncWorkerConnectionBase: The active worker connection.

        Raises:
            AmsdalInitiationError: If no worker connection is registered.
        """
