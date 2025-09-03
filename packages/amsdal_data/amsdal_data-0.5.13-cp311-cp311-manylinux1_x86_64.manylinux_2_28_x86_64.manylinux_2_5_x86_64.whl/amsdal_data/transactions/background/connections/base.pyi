import abc
from abc import ABC, abstractmethod
from amsdal_glue_core.common.interfaces.connectable import AsyncConnectable, Connectable
from collections.abc import Callable as Callable, Coroutine
from enum import Enum
from typing import Any

class WorkerMode(str, Enum):
    """Worker mode."""
    EXECUTOR = 'executor'
    SCHEDULER = 'scheduler'
    HYBRID = 'hybrid'

class WorkerConnectionBase(Connectable, ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def register_transaction(self, func: Callable[..., Any], **transaction_kwargs: Any) -> None: ...
    @abstractmethod
    def submit(self, func: Callable[..., Any], func_args: tuple[Any, ...], func_kwargs: dict[str, Any], transaction_kwargs: dict[str, Any]) -> None: ...
    @abstractmethod
    def run_worker(self, init_function: Callable[..., None] | None = None, shutdown_function: Callable[..., None] | None = None, mode: WorkerMode = ...) -> None: ...

class AsyncWorkerConnectionBase(AsyncConnectable, ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def register_transaction(self, func: Callable[..., Any], **transaction_kwargs: Any) -> None: ...
    @abstractmethod
    async def submit(self, func: Callable[..., Any], func_args: tuple[Any, ...], func_kwargs: dict[str, Any], transaction_kwargs: dict[str, Any]) -> None: ...
    @abstractmethod
    async def run_worker(self, init_function: Coroutine[Any, Any, Any] | None = None, shutdown_function: Coroutine[Any, Any, Any] | None = None, mode: WorkerMode = ...) -> None: ...
