from harmonize.abstract import Filter

__all__ = (
    "Rotation",
)


class Rotation(Filter[float]):
    def __init__(self, rotation_hz: float = 0.0) -> None:
        """
        Initializes a new instance of the Rotation class.

        Args:
            rotation_hz (float, optional): The rotation frequency in hertz. Defaults to 0.0.

        Returns:
            None
        """
        super().__init__(rotation_hz)

    def update(self, *, rotation_hz: float) -> None:
        """
        Updates the Rotation filter with a new rotation frequency.

        Args:
            rotation_hz (float): The new rotation frequency in hertz.

        Raises:
            ValueError: If rotation_hz is less than 0.

        Returns:
            None
        """
        rotation_hz = float(rotation_hz)

        if rotation_hz < 0:
            raise ValueError('rotation_hz must be bigger than or equal to 0')

        self.values = rotation_hz

    def to_dict(self) -> dict[str, dict[str, float]]:
        """
        Converts the Rotation filter to a dictionary representation.

        Returns:
            dict[str, dict[str, float]]: A dictionary containing the rotation frequency in hertz.
        """
        return {'rotation': {'rotationHz': self.values}}
