from typing import overload

from harmonize.abstract import Filter

__all__ = (
    "Equalizer",
)


class Equalizer(Filter[list[float]]):
    def __init__(self, gains: list[float] = None) -> None:
        """
        Initializes an Equalizer filter.

        Args:
            gains: A list of 15 float values representing the gain for each frequency band.
                   If None, all gains are set to 0.0 by default.

        Returns:
            None
        """
        super().__init__([0.0] * 15 if gains is None else gains)

    @overload
    def update(self, *, bands: list[tuple[int, float]]) -> None:
        ...

    @overload
    def update(self, *, band: int, gain: int) -> None:
        ...

    def update(self, **kwargs) -> None:
        """
        Updates the equalizer filter with new gain values.

        Args:
            **kwargs: Keyword arguments containing the new gain values.
                      Can be either 'bands' or 'band' and 'gain'.

        Raises:
            ValueError: If the provided gain values are out of range.
            KeyError: If neither 'bands' nor 'band' and 'gain' are provided.

        Returns:
            None
        """
        if 'bands' in kwargs:
            bands = kwargs.pop('bands')

            if not isinstance(bands, list) or not all(
                    isinstance(pair, tuple) and len(pair) == 2 and
                    isinstance(pair[0], int) and 0 <= pair[0] <= 14 and
                    isinstance(pair[1], (float, int)) and -0.25 <= pair[1] <= 1.0
                    for pair in bands
            ):
                raise ValueError(
                    'Bands must be a list of tuples (band: int, gain: float) '
                    'with band between 0 and 14, and gain between -0.25 and 1.0'
                )

            for band, gain in bands:
                self.values[band] = gain

        elif 'band' in kwargs and 'gain' in kwargs:
            band = int(kwargs.pop('band'))
            gain = float(kwargs.pop('gain'))

            if not 0 <= band <= 14:
                raise ValueError('Band must be between 0 and 14 (start and end inclusive)')

            if not -0.25 <= gain <= 1.0:
                raise ValueError('Gain must be between -0.25 and 1.0 (start and end inclusive)')

            self.values[band] = gain
        else:
            raise KeyError('Expected parameter bands OR band and gain, but neither were provided')

    def to_dict(self) -> dict[str, any]:
        """
        Converts the Equalizer filter object to a dictionary representation.

        Returns:
            dict[str, any]: A dictionary representation of the Equalizer filter object, where each key-value pair represents a band and its corresponding gain.
        """
        return {'equalizer': [{'band': band, 'gain': gain} for band, gain in enumerate(self.values)]}
