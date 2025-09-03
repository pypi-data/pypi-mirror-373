from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import GameClient
    from .schema import events

__all__ = [
    "GameClient",
    "events",
]


def __getattr__(name):
    if name == "GameClient":
        from .client import GameClient

        return GameClient
    if name == "events":
        from .schema import events

        return events

    raise AttributeError(f"Module '{__name__}' has no attribute '{name}'")
