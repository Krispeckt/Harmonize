from __future__ import annotations

from typing import Optional

__all__ = (
    "DLLNode",
)


class DLLNode:
    __slots__ = ("value", "previous", "later")

    def __init__(
            self,
            value: Optional[any] = None,
            previous: Optional[DLLNode] = None,
            later: Optional[DLLNode] = None
    ) -> None:
        self.value = value
        self.previous = previous
        self.later = later
