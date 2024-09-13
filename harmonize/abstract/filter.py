from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar('T', dict[str, any], list[float], list[int], float)

__all__ = (
    "Filter",
)


class Filter(ABC, Generic[T]):
    """Basic class of filters

    Note
    ----
        This class can be used if additional filters are used that are not implemented

    Operations
    ----------
        .. describe:: x == y

            Checks if two filters are the same.

        .. describe:: x != y

            Checks if two filters are not the same.

        .. describe:: hash(x)

            Return the filter's hash.

    Attributes
    ----------
        values : TypeVar (dict[str, any], list[float], list[int], floa)
            Values Needed Lavalink. See :class:`harmonize.objects.ChannelMix` for example
        plugin_filter : bool
            A flag indicating whether the filter is a plugin filter. Default is False.

    """

    def __init__(self, values: T, plugin_filter: bool = False) -> None:
        self.values: T = values
        self.plugin_filter: bool = plugin_filter

    @abstractmethod
    def update(self, **kwargs) -> None:
        """
        Update the filter with new parameters.

        Parameters
        ----------
        kwargs : dict
            Keyword arguments representing the new parameters for the filter.

        Raises
        ------
        NotImplementedError
            If the method is not implemented in a subclass.

        Returns
        -------
        None

        """
        raise NotImplementedError

    @abstractmethod
    def to_dict(self) -> dict[str, T]:
        """
        Convert the filter to a dictionary representation.

        Returns
        -------
        dict[str, T]
            A dictionary representation of the filter.

        Raises
        ------
        NotImplementedError
            If the method is not implemented in a subclass.

        """
        raise NotImplementedError

    def __hash__(self) -> int:
        return hash(str(self.values))

    def __eq__(self, other: any) -> bool:
        if not isinstance(other, Filter):
            raise ValueError("Filters can only be compared with other Filters")

        return all([
            self.values == other.values,
            self.plugin_filter == other.plugin_filter
        ])

    def __ne__(self, other: any) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return (
            f"<harmonize.abstract.Filter "
            f"values={self.values} "
            f"plugin_filter={self.plugin_filter}>"
        )
