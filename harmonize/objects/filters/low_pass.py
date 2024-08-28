from harmonize.abstract import Filter

__all__ = (
    "LowPass",
)


class LowPass(Filter[float]):
    def __init__(self, smoothing: float = 20.0) -> None:
        """
        Initializes a new instance of the LowPass class.

        Args:
            smoothing (float): The smoothing value. Defaults to 20.0.

        Returns:
            None
        """
        super().__init__(smoothing)

    def update(self, *, smoothing: float) -> None:
        """
        Updates the LowPass filter with a new smoothing value.

        Args:
            smoothing (float): The new smoothing value. Must be bigger than 1.

        Returns:
            None
        """
        smoothing = float(smoothing)
        if smoothing <= 1:
            raise ValueError('smoothing must be bigger than 1')

        self.values = smoothing

    def to_dict(self) -> dict[str, dict[str, float]]:
        """
        Converts the LowPass filter to a dictionary.

        Returns:
            dict[str, dict[str, float]]: A dictionary containing the LowPass filter's smoothing value.
        """
        return {'lowPass': {'smoothing': self.values}}

