from _typeshed import Incomplete
from amsdal_data.connections.constants import PRIMARY_PARTITION_KEY as PRIMARY_PARTITION_KEY
from amsdal_data.data_models.transaction_context import TransactionContext as TransactionContext
from amsdal_data.transactions.errors import AmsdalTransactionError as AmsdalTransactionError
from amsdal_utils.models.data_models.transaction import Transaction
from amsdal_utils.utils.singleton import Singleton
from contextvars import ContextVar
from typing import Any

logger: Incomplete
ASYNC_TRANSACTION_CONTEXT: ContextVar[TransactionContext | None]
ASYNC_TRANSACTION_OBJECT: ContextVar[Transaction | None]

class AmsdalTransactionManager(metaclass=Singleton):
    context: TransactionContext | None
    transaction_object: Transaction | None
    operation_manager: Incomplete
    def __init__(self) -> None: ...
    @property
    def transaction_id(self) -> str | None: ...
    def begin(self, context: TransactionContext, transaction_kwargs: dict[str, Any]) -> None:
        """
        Begins a transaction.

        Args:
            context (TransactionContext): The context of the transaction.
            transaction_kwargs (dict[str, Any]): The keyword arguments for the transaction.

        Returns:
            None
        """
    def commit(self, return_value: Any) -> None:
        """
        Commits (stores) the transaction to the database.

        Args:
            return_value (Any): The return value of the transaction.

        Returns:
            None

        Raises:
            AmsdalTransactionError: If there is no ongoing transaction or if the transaction commit fails.
        """
    def rollback(self) -> None:
        """
        Rolls back the transaction.

        Args:
            None

        Returns:
            None
        """
    def _store_transaction(self) -> None: ...
    def get_root_transaction_id(self) -> str | None: ...

class AmsdalAsyncTransactionManager(metaclass=Singleton):
    operation_manager: Incomplete
    def __init__(self) -> None: ...
    @property
    def transaction_id(self) -> str | None: ...
    @property
    def context(self) -> TransactionContext | None: ...
    @context.setter
    def context(self, value: TransactionContext | None) -> None: ...
    @property
    def transaction_object(self) -> Transaction | None: ...
    @transaction_object.setter
    def transaction_object(self, value: Transaction | None) -> None: ...
    async def begin(self, context: TransactionContext, transaction_kwargs: dict[str, Any]) -> None:
        """
        Begins a transaction.

        Args:
            context (TransactionContext): The context of the transaction.
            transaction_kwargs (dict[str, Any]): The keyword arguments for the transaction.

        Returns:
            None
        """
    async def commit(self, return_value: Any) -> None:
        """
        Commits (stores) the transaction to the database.

        Args:
            return_value (Any): The return value of the transaction.

        Returns:
            None

        Raises:
            AmsdalTransactionError: If there is no ongoing transaction or if the transaction commit fails.
        """
    async def rollback(self) -> None:
        """
        Rolls back the transaction.

        Args:
            None

        Returns:
            None
        """
    async def _store_transaction(self) -> None: ...
    def get_root_transaction_id(self) -> str | None: ...
