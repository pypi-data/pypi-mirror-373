from collections.abc import Callable
from typing import Any

from amsdal_utils.config.manager import AmsdalConfigManager
from amsdal_utils.errors import AmsdalInitiationError
from amsdal_utils.utils.singleton import Singleton

from amsdal_data.transactions.background.connections.base import AsyncWorkerConnectionBase
from amsdal_data.transactions.background.connections.base import WorkerConnectionBase


class BackgroundTransactionManager(metaclass=Singleton):
    def __init__(self) -> None:
        self.__connection: WorkerConnectionBase | None = None
        self.__transactions_cache: list[tuple[Callable[..., Any], dict[str, Any]]] = []

    def initialize_connection(self, *, raise_on_no_worker: bool = False) -> None:
        """Retrieve connection config from AmsdalConfigManager and initialize connection"""
        from amsdal_data.application import DataApplication

        if self.__connection is not None:
            msg = 'Background transaction connection is already registered'
            raise AmsdalInitiationError(msg)

        _config = AmsdalConfigManager().get_config()

        if not _config.resources_config.worker:
            if raise_on_no_worker:
                msg = 'Worker config is not provided'
                raise AmsdalInitiationError(msg)

            return

        connection_name = _config.resources_config.worker
        connection = DataApplication().get_extra_connection(connection_name)

        self.register_connection(connection)

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
        self.__connection = connection

        if self.__transactions_cache:
            for func, transaction_kwargs in self.__transactions_cache:
                self.__connection.register_transaction(func, **transaction_kwargs)

            self.__transactions_cache.clear()

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
        if self.__connection is None:
            self.__transactions_cache.append((func, transaction_kwargs))

        else:
            self.__connection.register_transaction(func, **transaction_kwargs)

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
        if self.__connection is None:
            msg = 'Background transaction connection is not registered'
            raise AmsdalInitiationError(msg)
        return self.__connection


class AsyncBackgroundTransactionManager(metaclass=Singleton):
    def __init__(self) -> None:
        self.__connection: AsyncWorkerConnectionBase | None = None
        self.__transactions_cache: list[tuple[Callable[..., Any], dict[str, Any]]] = []

    def initialize_connection(self, *, raise_on_no_worker: bool = False) -> None:
        """Retrieve connection config from AmsdalConfigManager and initialize connection"""
        from amsdal_data.application import AsyncDataApplication

        if self.__connection is not None:
            msg = 'Background transaction connection is already registered'
            raise AmsdalInitiationError(msg)

        _config = AmsdalConfigManager().get_config()

        if not _config.resources_config.worker:
            if raise_on_no_worker:
                msg = 'Worker config is not provided'
                raise AmsdalInitiationError(msg)

            return

        connection_name = _config.resources_config.worker
        connection = AsyncDataApplication().get_extra_connection(connection_name)

        self.register_connection(connection)

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
        self.__connection = connection

        if self.__transactions_cache:
            for func, transaction_kwargs in self.__transactions_cache:
                self.__connection.register_transaction(func, **transaction_kwargs)

            self.__transactions_cache.clear()

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
        if self.__connection is None:
            self.__transactions_cache.append((func, transaction_kwargs))

        else:
            self.__connection.register_transaction(func, **transaction_kwargs)

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
        if self.__connection is None:
            msg = 'Background transaction connection is not registered'
            raise AmsdalInitiationError(msg)
        return self.__connection
