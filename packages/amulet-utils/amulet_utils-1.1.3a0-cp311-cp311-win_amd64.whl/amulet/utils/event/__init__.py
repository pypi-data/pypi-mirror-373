from __future__ import annotations

import typing as _typing
from . import _connection_mode
from ._connection_mode import ConnectionMode

if _typing.TYPE_CHECKING:
    import collections.abc


_Args = _typing.TypeVarTuple("_Args")


class EventToken(_typing.Protocol[*_Args]):
    pass


@_typing.runtime_checkable
class Event(_typing.Protocol[*_Args]):
    def connect(
        self,
        callback: collections.abc.Callable[[*_Args], None],
        mode: ConnectionMode = ConnectionMode.Direct,
    ) -> EventToken[*_Args]:
        """
        Connect a callback to this event and return a token.
        The token must be kept alive for the callback to work.
        The token is used to disconnect the callback when it is not needed.
        Thread safe.
        """

    def disconnect(self, token: EventToken[*_Args]) -> None:
        """
        Disconnect a callback.
        Token is the value returned by connect.
        Thread safe.
        """

    def dispatch(self, *args: *_Args) -> None:
        """
        Call all callbacks with the given arguments from this thread.
        Blocks until all callbacks are processed.
        Thread safe.
        """
