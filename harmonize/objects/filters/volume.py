from harmonize.abstract import Filter


class Volume(Filter[float]):
    """
    Represents a volume filter. Extended from :class:`harmonize.abstract.Filter`
    """

    def __init__(self, volume: float = 1.0) -> None:
        super().__init__(volume)

    def update(self, *, volume: float) -> None:
        """
        Modifies the player volume.

        Note
        ----
            Volume must be bigger than or equal to 0, and less than or equal to 5

        Parameters
        ----------
            volume : float
                The new volume of the player. 1.0 means 100%/default.

        Raises
        ------
            ValueError
                If volume is not within the valid range.

        Returns
        -------
            None
        """
        volume = float(volume)

        if not 0 <= volume <= 5:
            raise ValueError('volume must be bigger than or equal to 0, and less than or equal to 5.')

        self.values = volume

    def to_dict(self) -> dict[str, float]:
        """
        Converts the volume filter to a dictionary representation.

        Returns
        -------
            dict[str, float]: A dictionary containing the volume filter's values.
        """
        return {'volume': self.values}
