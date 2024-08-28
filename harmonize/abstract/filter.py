from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar('T', dict[str, any], list[float], list[int], float)

__all__ = (
    "Filter",
)


class Filter(ABC, Generic[T]):
    def __init__(self, values: T, plugin_filter: bool = False) -> None:
        """
        Initializes a Filter instance.

        Args:
            values (T): The values associated with the filter.
            plugin_filter (bool, optional): Whether the filter is a plugin filter. Defaults to False.

        Returns:
            None
        """
        self.values: T = values
        self.plugin_filter: bool = plugin_filter

    @abstractmethod
    def update(self, **kwargs) -> None:
        """
        Updates the filter with the given keyword arguments.

        Args:
            **kwargs: The keyword arguments to update the filter with.

        Returns:
            None: This function does not return anything.

        Raises:
            NotImplementedError: This function is meant to be overridden by subclasses and raises an error if not implemented.
        """
        raise NotImplementedError

    @abstractmethod
    def to_dict(self) -> dict[str, T]:
        """
        Converts the filter to a dictionary representation.

        Returns:
            dict[str, T]: A dictionary containing the filter's values.
        """
        raise NotImplementedError

    def __hash__(self) -> int:
        return hash(self.values)

    def __eq__(self, other: any) -> bool:
        if not isinstance(other, Filter):
            raise ValueError("Filters can only be compared with other Filters")

        return all([
            self.values == other.values,
            self.plugin_filter == other.plugin_filter
        ])
