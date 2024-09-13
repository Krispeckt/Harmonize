from typing import overload

from harmonize.abstract import Filter

__all__ = (
    "Timescale",
)


class Timescale(Filter[dict[str, float]]):
    """
    Represents a timescale filter. Extended from :class:`harmonize.abstract.Filter`
    """

    def __init__(
            self,
            speed: float = 1.0,
            pitch: float = 1.0,
            rate: float = 1.0
    ) -> None:
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
        Updates the Timescale filter with new values for speed, pitch, and/or rate.

        Note
        ----
            All new values must be greater than or equal to 0.

        Parameters
        ----------
            **kwargs: A dictionary containing the new values for speed, pitch, and/or rate.

        Raises
        ------
            ValueError
                If any of the new values for speed, pitch, and/or rate are not greater than 0.

        Returns
        -------
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

        Returns
        -------
            dict[str, dict[str, float]]: A dictionary containing the Timescale filter values.
        """
        return {'timescale': self.values}
