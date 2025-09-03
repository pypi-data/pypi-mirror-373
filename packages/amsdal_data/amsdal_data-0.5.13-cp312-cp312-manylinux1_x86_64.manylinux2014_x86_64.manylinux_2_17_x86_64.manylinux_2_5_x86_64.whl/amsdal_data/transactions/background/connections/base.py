from abc import ABC
from abc import abstractmethod
from collections.abc import Callable
from collections.abc import Coroutine
from enum import Enum
from typing import Any

from amsdal_glue_core.common.interfaces.connectable import AsyncConnectable
from amsdal_glue_core.common.interfaces.connectable import Connectable


class WorkerMode(str, Enum):
    """Worker mode."""

    EXECUTOR = 'executor'
    """Execute tasks."""

    SCHEDULER = 'scheduler'
    """Create new tasks depending on the schedule configuration."""

    HYBRID = 'hybrid'
    """Execute tasks and create new tasks depending on the schedule configuration."""


class WorkerConnectionBase(Connectable, ABC):
    @abstractmethod
    def register_transaction(self, func: Callable[..., Any], **transaction_kwargs: Any) -> None: ...

    @abstractmethod
    def submit(
        self,
        func: Callable[..., Any],
        func_args: tuple[Any, ...],
        func_kwargs: dict[str, Any],
        transaction_kwargs: dict[str, Any],
    ) -> None: ...

    @abstractmethod
    def run_worker(
        self,
        init_function: Callable[..., None] | None = None,
        shutdown_function: Callable[..., None] | None = None,
        mode: WorkerMode = WorkerMode.EXECUTOR,
    ) -> None: ...


class AsyncWorkerConnectionBase(AsyncConnectable, ABC):
    @abstractmethod
    def register_transaction(self, func: Callable[..., Any], **transaction_kwargs: Any) -> None: ...

    @abstractmethod
    async def submit(
        self,
        func: Callable[..., Any],
        func_args: tuple[Any, ...],
        func_kwargs: dict[str, Any],
        transaction_kwargs: dict[str, Any],
    ) -> None: ...

    @abstractmethod
    async def run_worker(
        self,
        init_function: Coroutine[Any, Any, Any] | None = None,
        shutdown_function: Coroutine[Any, Any, Any] | None = None,
        mode: WorkerMode = WorkerMode.EXECUTOR,
    ) -> None: ...
