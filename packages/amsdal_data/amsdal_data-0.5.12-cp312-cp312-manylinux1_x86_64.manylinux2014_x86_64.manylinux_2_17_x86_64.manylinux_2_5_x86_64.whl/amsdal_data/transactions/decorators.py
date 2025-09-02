import inspect
import json
import os
from collections.abc import Callable
from functools import wraps
from typing import Any
from typing import ParamSpec
from typing import Protocol
from typing import TypeVar
from typing import overload

from amsdal_utils.config.manager import AmsdalConfigManager
from amsdal_utils.models.data_models.address import Address
from amsdal_utils.models.enums import Versions
from amsdal_utils.utils.identifier import get_identifier

from amsdal_data.data_models.transaction_context import TransactionContext
from amsdal_data.enums import CoreResource
from amsdal_data.transactions.background.manager import AsyncBackgroundTransactionManager
from amsdal_data.transactions.background.manager import BackgroundTransactionManager
from amsdal_data.transactions.background.schedule.config import SCHEDULE_TYPE
from amsdal_data.transactions.background.schedule.config import ScheduleConfig
from amsdal_data.transactions.constants import TRANSACTION_CLASS_NAME

P = ParamSpec('P')
R = TypeVar('R')
R_co = TypeVar('R_co', covariant=True)


class Transaction(Protocol[P, R_co]):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...

    def submit(self, *args: P.args, **kwargs: P.kwargs) -> None: ...


class AsyncTransaction(Protocol[P, R_co]):
    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...

    def submit(self, *args: P.args, **kwargs: P.kwargs) -> None: ...


@overload
def transaction(name: Callable[P, R]) -> Transaction[P, R]: ...


@overload
def transaction(
    name: str | None = None,
    schedule_config: ScheduleConfig | None = None,
    schedule: SCHEDULE_TYPE | None = None,
    **transaction_kwargs: Any,
) -> Callable[[Callable[P, R]], Transaction[P, R]]: ...


def transaction(
    name: str | Callable[P, R] | None = None,
    schedule_config: ScheduleConfig | None = None,
    schedule: SCHEDULE_TYPE | None = None,
    **transaction_kwargs: Any,
) -> Transaction[P, R] | Callable[[Callable[P, R]], Transaction[P, R]]:
    """
    Decorator to register a function as a transaction.

    This decorator can be used to register a function as a transaction with optional scheduling
    configuration. If both `schedule_config` and `schedule` are provided, a ValueError is raised.

    Args:
        name (str | Callable[P, R] | None, optional): The name of the transaction or the function to be decorated.
            If a string is provided, it is used as the transaction label. If a function is provided, it is decorated.
            Defaults to None.
        schedule_config (ScheduleConfig | None, optional): The schedule configuration for the transaction.
            Defaults to None.
        schedule (SCHEDULE_TYPE | None, optional): The schedule type for the transaction. Defaults to None.
        **transaction_kwargs (Any): Additional keyword arguments to pass to the transaction function.

    Returns:
        Transaction[P, R] | Callable[[Callable[P, R]], Transaction[P, R]]: The decorated transaction function or a
        decorator function if `name` is a string or None.

    Raises:
        ValueError: If both `schedule_config` and `schedule` are provided.
    """
    if schedule_config is not None and schedule is not None:
        msg = 'Only one of schedule_config or schedule can be provided'
        raise ValueError(msg)

    def _transaction(func: Callable[P, R]) -> Transaction[P, R]:
        # these are internal transactions, we don't want to register them
        transaction_kwargs['schedule_config'] = schedule_config
        transaction_kwargs['schedule'] = schedule

        if not func.__module__.startswith(('amsdal.', 'amsdal_data.', 'amsdal_models.', 'amsdal_server.')):
            BackgroundTransactionManager().register_transaction(func, **transaction_kwargs)

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            with TransactionFlow(func, *args, transaction_kwargs=transaction_kwargs, **kwargs) as transaction_flow:
                result = func(*args, **kwargs)
                transaction_flow.set_return_value(result)
                return result

        def _submit(*args: P.args, **kwargs: P.kwargs) -> None:
            BackgroundTransactionManager().connection.submit(
                func=func,
                func_args=args,
                func_kwargs=kwargs,
                transaction_kwargs=transaction_kwargs,
            )

        wrapper.submit = _submit  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    if name is None:
        return _transaction
    elif isinstance(name, str):
        _transaction.__transaction_name__ = name  # type: ignore[attr-defined]
        transaction_kwargs['label'] = name
        return _transaction

    return _transaction(name)


def async_transaction(
    name: str | Callable[P, R] | None = None,
    schedule_config: ScheduleConfig | None = None,
    schedule: SCHEDULE_TYPE | None = None,
    **transaction_kwargs: Any,
) -> Transaction[P, R] | Callable[[Callable[P, R]], Transaction[P, R]]:
    """
    Decorator to register a function as a transaction.

    This decorator can be used to register a function as a transaction with optional scheduling
    configuration. If both `schedule_config` and `schedule` are provided, a ValueError is raised.

    Args:
        name (str | Callable[P, R] | None, optional): The name of the transaction or the function to be decorated.
            If a string is provided, it is used as the transaction label. If a function is provided, it is decorated.
            Defaults to None.
        schedule_config (ScheduleConfig | None, optional): The schedule configuration for the transaction.
            Defaults to None.
        schedule (SCHEDULE_TYPE | None, optional): The schedule type for the transaction. Defaults to None.
        **transaction_kwargs (Any): Additional keyword arguments to pass to the transaction function.

    Returns:
        Transaction[P, R] | Callable[[Callable[P, R]], Transaction[P, R]]: The decorated transaction function or a
        decorator function if `name` is a string or None.

    Raises:
        ValueError: If both `schedule_config` and `schedule` are provided.
    """
    if schedule_config is not None and schedule is not None:
        msg = 'Only one of schedule_config or schedule can be provided'
        raise ValueError(msg)

    def _transaction(func: Callable[P, R]) -> Transaction[P, R]:
        # these are internal transactions, we don't want to register them
        transaction_kwargs['schedule_config'] = schedule_config
        transaction_kwargs['schedule'] = schedule

        if not func.__module__.startswith(('amsdal.', 'amsdal_data.', 'amsdal_models.', 'amsdal_server.')):
            AsyncBackgroundTransactionManager().register_transaction(func, **transaction_kwargs)

        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            async with TransactionFlow(
                func, *args, transaction_kwargs=transaction_kwargs, **kwargs
            ) as transaction_flow:
                result = await func(*args, **kwargs)  # type: ignore[misc]
                transaction_flow.set_return_value(result)
                return result

        async def _submit(*args: P.args, **kwargs: P.kwargs) -> None:
            await AsyncBackgroundTransactionManager().connection.submit(
                func=func,
                func_args=args,
                func_kwargs=kwargs,
                transaction_kwargs=transaction_kwargs,
            )

        wrapper.submit = _submit  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    if name is None:
        return _transaction
    elif isinstance(name, str):
        _transaction.__transaction_name__ = name  # type: ignore[attr-defined]
        transaction_kwargs['label'] = name
        return _transaction

    return _transaction(name)


def raw_transaction(func: Callable[P, R]) -> Callable[P, R]:
    """
    Decorator to execute a function within a transaction flow context.

    This decorator wraps the provided function, ensuring it is executed within a transaction flow.
    It captures the return value and handles any exceptions that may occur during execution.

    Args:
        func (Callable[P, R]): The function to be executed within the transaction flow.

    Returns:
        Callable[P, R]: The wrapped function that executes within a transaction flow.
    """

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        with TransactionFlow(func, *args, transaction_kwargs={}, **kwargs) as transaction_flow:
            result = func(*args, **kwargs)
            transaction_flow.set_return_value(result)
            return result

    return wrapper


class TransactionFlow:
    def __init__(self, func: Callable[..., Any], *args: Any, transaction_kwargs: dict[str, Any], **kwargs: Any) -> None:
        self.return_value: Any = None
        self.context = TransactionContext(
            address=Address(
                resource=CoreResource.TRANSACTION,
                class_name=TRANSACTION_CLASS_NAME,
                class_version=Versions.LATEST,
                object_id=get_identifier(),
                object_version=Versions.LATEST,
            ),
            method_name=func.__name__,
            execution_location=self._get_execution_location(func),
            arguments=self._serialize_arguments({'args:': args, 'kwargs': kwargs}),
        )
        self.transaction_kwargs: dict[str, Any] = transaction_kwargs

        if 'label' not in self.transaction_kwargs:
            self.transaction_kwargs['label'] = func.__name__

    def __enter__(self) -> 'TransactionFlow':
        from amsdal_data.transactions.manager import AmsdalTransactionManager

        if AmsdalConfigManager().get_config().async_mode:
            msg = 'Regular transactions are not supported in async mode'
            raise ValueError(msg)

        transaction_manager = AmsdalTransactionManager()
        transaction_manager.begin(self.context, self.transaction_kwargs)
        return self

    async def __aenter__(self) -> 'TransactionFlow':
        from amsdal_data.transactions.manager import AmsdalAsyncTransactionManager

        if not AmsdalConfigManager().get_config().async_mode:
            msg = 'Async transactions are not supported in regular mode'
            raise ValueError(msg)

        transaction_manager = AmsdalAsyncTransactionManager()
        await transaction_manager.begin(self.context, self.transaction_kwargs)

        return self

    def set_return_value(self, value: Any) -> None:
        self.return_value = value

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        from amsdal_data.transactions.manager import AmsdalTransactionManager

        transaction_manager = AmsdalTransactionManager()

        if exc_type is not None:
            transaction_manager.rollback()
        else:
            transaction_manager.commit(self.return_value)

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        from amsdal_data.transactions.manager import AmsdalAsyncTransactionManager

        transaction_manager = AmsdalAsyncTransactionManager()

        if exc_type is not None:
            await transaction_manager.rollback()
        else:
            await transaction_manager.commit(self.return_value)

    def _serialize_arguments(self, data: Any) -> Any:
        if isinstance(data, dict):
            return {self._serialize_arguments(k): self._serialize_arguments(v) for k, v in data.items()}
        elif isinstance(data, list | tuple | set):
            return [self._serialize_arguments(x) for x in data]

        try:
            json.dumps(data)
            return data
        except Exception:
            return str(data)

    @staticmethod
    def _get_execution_location(func: Any) -> str:
        _file = None

        try:
            _file = inspect.getfile(func)
        except TypeError:
            # If that raises a TypeError, try to get the file with __pyx_capi__
            if hasattr(func, '__module__') and func.__module__:
                module = __import__(func.__module__)

                if hasattr(module, '__pyx_capi__') and func.__name__ in module.__pyx_capi__:
                    _file = inspect.getfile(module.__pyx_capi__[func.__name__])

        return os.path.abspath(_file) if _file else ''
