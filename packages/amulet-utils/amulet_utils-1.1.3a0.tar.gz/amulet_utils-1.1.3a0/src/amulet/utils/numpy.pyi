from __future__ import annotations

import collections.abc

import numpy
import numpy.typing

__all__: list[str] = ["unique_inverse"]

def unique_inverse(
    array: collections.abc.Buffer,
) -> tuple[numpy.typing.NDArray[numpy.uint32], numpy.typing.NDArray[numpy.uint32]]: ...
