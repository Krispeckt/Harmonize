from typing import overload

from harmonize.abstract import Filter

__all__ = (
    "Tremolo",
)


class Tremolo(Filter[dict[str, float]]):
    """
    Represents a tremolo filter. Extended from :class:`harmonize.abstract.Filter`
    """

    def __init__(self, frequency: float = 2.0, depth: float = 0.5) -> None:
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
        Updates the tremolo effect values.

        Note
        ----
            Frequency must be bigger than 0. Depth must be bigger than 0, and less than or equal to 1.

        Parameters
        ----------
            **kwargs: Keyword arguments containing the tremolo effect values to update.

        Raises
        ------
            ValueError
                If either frequency or depth are not valid.

        Returns
        -------
            None
        """
        if 'frequency' in kwargs:
            frequency = float(kwargs.pop('frequency'))

            if frequency < 0:
                raise ValueError('Frequency must be bigger than 0')

            self.values['frequency'] = frequency

        if 'depth' in kwargs:
            depth = float(kwargs.pop('depth'))

            if not 0 < depth <= 1:
                raise ValueError('Depth must be bigger than 0, and less than or equal to 1.')

            self.values['depth'] = depth

    def to_dict(self) -> dict[str, dict[str, float]]:
        """
        Converts the tremolo effect values to a dictionary.

        Returns
        -------
            dict[str, dict[str, float]]: A dictionary containing the tremolo effect values.
        """
        return {'tremolo': self.values}
