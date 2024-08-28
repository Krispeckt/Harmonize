from typing import overload

from harmonize.abstract import Filter

__all__ = (
    "Vibrato",
)


class Vibrato(Filter[dict[str, float]]):
    def __init__(self, frequency: float = 2.0, depth: float = 0.5) -> None:
        """
        Initializes a new instance of the Vibrato class.

        Args:
            frequency (float): The frequency of the vibrato effect. Defaults to 2.0.
            depth (float): The depth of the vibrato effect. Defaults to 0.5.

        Returns:
            None
        """
        super().__init__({'frequency': frequency, 'depth': depth})

    @overload
    def update(self, *, frequency: float) -> None:
        ...

    @overload
    def update(self, *, depth: float) -> None:
        ...

    @overload
    def update(self, *, frequency: float, depth: float) -> None:
        ...

    def update(self, **kwargs) -> None:
        """
        Updates the vibrato effect values.

        Args:
            **kwargs: Keyword arguments containing the vibrato effect values to update.
                - frequency (float): The frequency of the vibrato effect. Must be bigger than 0, and less than or equal to 14.
                - depth (float): The depth of the vibrato effect. Must be bigger than 0, and less than or equal to 1.

        Returns:
            None
        """
        if 'frequency' in kwargs:
            frequency = float(kwargs.pop('frequency'))

            if not 0 < frequency <= 14:
                raise ValueError('Frequency must be bigger than 0, and less than or equal to 14')

            self.values['frequency'] = frequency

        if 'depth' in kwargs:
            depth = float(kwargs.pop('depth'))

            if not 0 < depth <= 1:
                raise ValueError('Depth must be bigger than 0, and less than or equal to 1.')

            self.values['depth'] = depth

    def to_dict(self) -> dict[str, dict[str, float]]:
        """
        Converts the vibrato effect values to a dictionary.

        Returns:
            dict[str, dict[str, float]]: A dictionary containing the vibrato effect values.
        """
        return {'vibrato': self.values}

