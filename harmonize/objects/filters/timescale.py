from typing import overload

from harmonize.abstract import Filter

__all__ = (
    "Timescale",
)


class Timescale(Filter[dict[str, float]]):
    def __init__(
            self,
            speed: float = 1.0,
            pitch: float = 1.0,
            rate: float = 1.0
    ) -> None:
        """
        Initializes a new instance of the Timescale filter.

        Args:
            speed: The speed of the filter, defaults to 1.0.
            pitch: The pitch of the filter, defaults to 1.0.
            rate: The rate of the filter, defaults to 1.0.

        Returns:
            None
        """
        super().__init__({'speed': speed, 'pitch': pitch, 'rate': rate})

    @overload
    def update(self, *, speed: float) -> None:
        ...

    @overload
    def update(self, *, pitch: float) -> None:
        ...

    @overload
    def update(self, *, rate: float) -> None:
        ...

    @overload
    def update(self, *, speed: float, pitch: float) -> None:
        ...

    @overload
    def update(self, *, speed: float, rate: float) -> None:
        ...

    @overload
    def update(self, *, rate: float, pitch: float) -> None:
        ...

    @overload
    def update(self, *, speed: float, rate: float, pitch: float) -> None:
        ...

    def update(self, **kwargs) -> None:
        """
        Updates the Timescale filter with the provided keyword arguments.

        Args:
            **kwargs: Keyword arguments to update the filter.
                - speed (float): The speed of the filter. Must be bigger than 0.
                - pitch (float): The pitch of the filter. Must be bigger than 0.
                - rate (float): The rate of the filter. Must be bigger than 0.

        Returns:
            None
        """
        if 'speed' in kwargs:
            speed = float(kwargs.pop('speed'))

            if speed <= 0:
                raise ValueError('Speed must be bigger than 0')

            self.values['speed'] = speed

        if 'pitch' in kwargs:
            pitch = float(kwargs.pop('pitch'))

            if pitch <= 0:
                raise ValueError('Pitch must be bigger than 0')

            self.values['pitch'] = pitch

        if 'rate' in kwargs:
            rate = float(kwargs.pop('rate'))

            if rate <= 0:
                raise ValueError('Rate must be bigger than 0')

            self.values['rate'] = rate

    def to_dict(self) -> dict[str, dict[str, float]]:
        """
        Converts the Timescale filter to a dictionary.

        Returns:
            dict[str, dict[str, float]]: A dictionary containing the Timescale filter values.
        """
        return {'timescale': self.values}
