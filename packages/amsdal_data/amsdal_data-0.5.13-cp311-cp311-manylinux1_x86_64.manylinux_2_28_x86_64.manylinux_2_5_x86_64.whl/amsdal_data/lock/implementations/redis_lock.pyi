import redis
from amsdal_data.errors import AmsdalConnectionError as AmsdalConnectionError
from amsdal_data.lock.base import LockBase as LockBase
from amsdal_utils.models.data_models.address import Address as Address
from typing import Any

class RedisLock(LockBase):
    """
    Represents a Redis-based lock mechanism.

    Attributes:
        client (redis.Redis): The Redis client used for lock operations.
    """
    client: redis.Redis
    @property
    def is_connected(self) -> bool:
        """
        Checks if the Redis client is connected.

        Returns:
            bool: True if the Redis client is connected, False otherwise.
        """
    @property
    def is_alive(self) -> bool:
        """
        Checks if the Redis client is alive by sending a ping command.

        Returns:
            bool: True if the Redis client is alive and responds to the ping, False otherwise.
        """
    def connect(self, host: str, *, port: int = 6379, username: str | None = None, password: str | None = None, ssl: bool = False, ssl_certfile: str | None = None, ssl_keyfile: str | None = None, ssl_ca_certs: str | None = None) -> None:
        """
        Connects to the Redis server with the specified parameters.

        Args:
            host (str): The hostname of the Redis server.
            port (int, optional): The port number of the Redis server. Defaults to 6379.
            username (str | None, optional): The username for Redis authentication. Defaults to None.
            password (str | None, optional): The password for Redis authentication. Defaults to None.
            ssl (bool, optional): Whether to use SSL for the connection. Defaults to False.
            ssl_certfile (str | None, optional): The path to the SSL certificate file. Defaults to None.
            ssl_keyfile (str | None, optional): The path to the SSL key file. Defaults to None.
            ssl_ca_certs (str | None, optional): The path to the SSL CA certificates file. Defaults to None.

        Returns:
            None
        """
    def disconnect(self) -> None:
        """
        Disconnects the Redis client.

        Returns:
            None
        """
    def acquire(self, target_address: Address, *, timeout_ms: int = -1, blocking: bool = True, metadata: dict[str, Any] | None = None) -> bool:
        """
        Acquires a lock for the given target address.

        Args:
            target_address (Address): The address to lock.
            timeout_ms (int, optional): The timeout in milliseconds to wait for the lock. Defaults to -1 (no timeout).
            blocking (bool, optional): Whether to block until the lock is acquired. Defaults to True.
            metadata (dict[str, Any] | None, optional): Additional metadata to associate with the lock. Defaults to None

        Returns:
            bool: True if the lock was acquired, False otherwise.
        """
    def release(self, target_address: Address) -> None:
        """
        Releases the lock for the given target address.

        Args:
            target_address (Address): The address to unlock.

        Returns:
            None
        """
    @staticmethod
    def _get_redis_client(host: str, *, port: int = 6379, username: str | None = None, password: str | None = None, ssl: bool = False, ssl_certfile: str | None = None, ssl_keyfile: str | None = None, ssl_ca_certs: str | None = None) -> Any: ...
