from typing import overload

from harmonize.abstract import Filter

__all__ = (
    "Karaoke",
)


class Karaoke(Filter[dict[str, float]]):
    def __init__(
            self,
            level: float = 1.0,
            mono_level: float = 1.0,
            filter_band: float = 220.0,
            filter_width: float = 100.0
    ) -> None:
        """
        Initializes a Karaoke filter object.

        Args:
            level (float): The level of the filter. Defaults to 1.0.
            mono_level (float): The level of the mono filter. Defaults to 1.0.
            filter_band (float): The band of the filter. Defaults to 220.0.
            filter_width (float): The width of the filter. Defaults to 100.0.

        Returns:
            None
        """
        super().__init__({
            'level': level,
            'monoLevel': mono_level,
            'filterBand': filter_band,
            'filterWidth': filter_width
        })

    @overload
    def update(self, *, level: float) -> None:
        ...

    @overload
    def update(self, *, mono_level: float) -> None:
        ...

    @overload
    def update(self, *, filter_band: float) -> None:
        ...

    @overload
    def update(self, *, filter_width: float) -> None:
        ...

    @overload
    def update(
            self, *,
            level: float,
            mono_level: float
    ) -> None:
        ...

    @overload
    def update(
            self, *,
            level: float,
            filter_width: float
    ) -> None:
        ...

    @overload
    def update(
            self, *,
            level: float,
            filter_band: float
    ) -> None:
        ...

    @overload
    def update(
            self, *,
            mono_level: float,
            filter_width: float
    ) -> None:
        ...

    @overload
    def update(
            self, *,
            mono_level: float,
            filter_band: float
    ) -> None:
        ...

    @overload
    def update(
            self, *,
            filter_band: float,
            filter_width: float
    ) -> None:
        ...

    @overload
    def update(
            self, *,
            level: float,
            mono_level: float,
            filter_width: float
    ) -> None:
        ...

    @overload
    def update(
            self, *,
            level: float,
            mono_level: float,
            filter_band: float
    ) -> None:
        ...

    @overload
    def update(
            self, *,
            level: float,
            mono_level: float,
            filter_band: float,
            filter_width: float
    ) -> None:
        ...

    def update(self, **kwargs) -> None:
        """
        Update the values of the Karaoke filter object.

        Args:
            **kwargs (dict): A dictionary containing the updated values for the filter.
                Possible keys are:
                    - 'level' (float): The level of the filter.
                    - 'mono_level' (float): The level of the mono filter.
                    - 'filter_band' (float): The band of the filter.
                    - 'filter_width' (float): The width of the filter.

        Returns:
            None
        """
        if 'level' in kwargs:
            self.values['level'] = float(kwargs.pop('level'))

        if 'mono_level' in kwargs:
            self.values['monoLevel'] = float(kwargs.pop('mono_level'))

        if 'filter_band' in kwargs:
            self.values['filterBand'] = float(kwargs.pop('filter_band'))

        if 'filter_width' in kwargs:
            self.values['filterWidth'] = float(kwargs.pop('filter_width'))

    def to_dict(self) -> dict[str, dict[str, float]]:
        """
        Converts the Karaoke filter object to a dictionary.

        Returns:
            dict[str, dict[str, float]]: A dictionary containing the Karaoke filter values.
        """
        return {'karaoke': self.values}
