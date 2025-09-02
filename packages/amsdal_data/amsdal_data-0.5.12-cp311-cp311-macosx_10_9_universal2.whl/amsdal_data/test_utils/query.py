from typing import Any

from amsdal_glue_core.common.interfaces.connection import ConnectionBase


class CaptureQueriesContext:
    """Context manager that captures queries executed by the specified connection.

    Args:
        connection (ConnectionBase): The connection to capture queries from.
    """

    def __init__(self, connection: ConnectionBase) -> None:
        self.connection = connection
        self.debug_mode = False

    def __enter__(self) -> 'CaptureQueriesContext':
        self.first_query = len(self.connection.queries)
        self.last_query: int | None = None
        self.debug_mode = self.connection.debug_mode

        self.connection.debug_mode = True

        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.last_query = len(self.connection.queries)
        self.connection.debug_mode = self.debug_mode

    @property
    def captured_queries(self) -> list[str]:
        return self.connection.queries[self.first_query : self.last_query]
