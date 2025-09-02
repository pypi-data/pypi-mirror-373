from amsdal_data.data_models.lock_object import LockObject as LockObject
from amsdal_data.lock.base import LockBase as LockBase
from amsdal_utils.models.data_models.address import Address as Address
from threading import Lock
from typing import Any

class ThreadLock(LockBase):
    """
    A thread lock implementation of the LockBase class.
    """
    def connect(self, *args: Any, **kwargs: Any) -> None: ...
    def disconnect(self) -> None: ...
    @property
    def is_connected(self) -> bool: ...
    @property
    def is_alive(self) -> bool: ...
    locks: dict[Address, Lock]
    lock_data: dict[Address, LockObject]
    def __init__(self) -> None: ...
    def acquire(self, target_address: Address, *, timeout_ms: int = -1, blocking: bool = True, metadata: dict[str, Any] | None = None) -> bool:
        """
        Acquires the lock for a specific target (resource) with optional timeout, blocking, and metadata parameters.

        Args:
            target_address (Address): The target address to acquire the lock for.
            timeout_ms (int, optional): The timeout in milliseconds. Defaults to -1 (no timeout).
            blocking (bool, optional): Whether to block until the lock is acquired. Defaults to True.
            metadata (dict[str, Any] | None, optional): The metadata to store with the lock. Defaults to None.

        Returns:
            bool: True if the lock was acquired, False otherwise.
        """
    def release(self, target_address: Address) -> None:
        """
        Releases the lock for a specific target (resource).

        Args:
            target_address (Address): The target address to release the lock for.

        Raises:
            RuntimeError: If the lock is not acquired.

        Returns:
            None
        """
