from __future__ import annotations

from abc import ABC

__all__ = (
    "Serializable",
)


class Serializable(ABC):

    @classmethod
    def from_dict(cls, data: dict) -> Serializable: ...

    @property
    def raw(self) -> str:
        return ...
