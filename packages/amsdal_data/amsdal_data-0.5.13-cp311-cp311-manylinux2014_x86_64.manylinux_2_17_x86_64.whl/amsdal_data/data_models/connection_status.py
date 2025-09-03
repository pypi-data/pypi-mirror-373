from dataclasses import dataclass


@dataclass(kw_only=True)
class ConnectionStatus:
    name: str
    is_connected: bool
    is_alive: bool
