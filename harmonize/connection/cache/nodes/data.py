from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .dll import DLLNode

__all__ = (
    "DataNode",
)


@dataclass
class DataNode:
    key: any
    value: any
    frequency: int
    node: DLLNode
