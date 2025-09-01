from __future__ import annotations

import typing

__all__: list[str] = ["ConnectionMode"]

class ConnectionMode:
    """
    Members:

      Direct : Directly called by the emitter.

      Async : Called asynchronously.
    """

    Async: typing.ClassVar[
        ConnectionMode
    ]  # value = amulet.utils.event._connection_mode.ConnectionMode.Async
    Direct: typing.ClassVar[
        ConnectionMode
    ]  # value = amulet.utils.event._connection_mode.ConnectionMode.Direct
    __members__: typing.ClassVar[
        dict[str, ConnectionMode]
    ]  # value = {'Direct': amulet.utils.event._connection_mode.ConnectionMode.Direct, 'Async': amulet.utils.event._connection_mode.ConnectionMode.Async}
    def __eq__(self, other: typing.Any) -> bool: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: typing.SupportsInt) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: typing.Any) -> bool: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...
