from _typeshed import Incomplete
from amsdal_glue_core.common.interfaces.connection import ConnectionBase as ConnectionBase
from typing import Any

class CaptureQueriesContext:
    """Context manager that captures queries executed by the specified connection.

    Args:
        connection (ConnectionBase): The connection to capture queries from.
    """
    connection: Incomplete
    debug_mode: bool
    def __init__(self, connection: ConnectionBase) -> None: ...
    first_query: Incomplete
    last_query: int | None
    def __enter__(self) -> CaptureQueriesContext: ...
    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None: ...
    @property
    def captured_queries(self) -> list[str]: ...
