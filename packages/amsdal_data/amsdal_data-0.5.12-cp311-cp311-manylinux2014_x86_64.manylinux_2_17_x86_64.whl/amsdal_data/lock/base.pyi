import abc
from abc import ABC, abstractmethod
from amsdal_glue_core.common.interfaces.connectable import Connectable
from amsdal_utils.models.data_models.address import Address as Address
from typing import Any

class LockBase(Connectable, ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def acquire(self, target_address: Address, *, timeout_ms: int = -1, blocking: bool = True, metadata: dict[str, Any] | None = None) -> bool: ...
    @abstractmethod
    def release(self, target_address: Address) -> None: ...
