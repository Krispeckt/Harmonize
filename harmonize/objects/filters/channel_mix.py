from typing import overload

from harmonize.abstract import Filter

__all__ = (
    "ChannelMix",
)


class ChannelMix(Filter[dict[str, float]]):
    def __init__(
            self, left_to_left: float = 1.0,
            left_to_right: float = 0.0,
            right_to_left: float = 0.0,
            right_to_right: float = 0.0
    ) -> None:
        """
        Initializes a new instance of the ChannelMix filter.

        Args:
            left_to_left (float): The amount of the left channel to send to the left channel. Defaults to 1.0.
            left_to_right (float): The amount of the left channel to send to the right channel. Defaults to 0.0.
            right_to_left (float): The amount of the right channel to send to the left channel. Defaults to 0.0.
            right_to_right (float): The amount of the right channel to send to the right channel. Defaults to 0.0.

        Returns:
            None
        """
        super().__init__({
            'leftToLeft': left_to_left,
            'leftToRight': left_to_right,
            'rightToLeft': right_to_left,
            'rightToRight': right_to_right
        })

    @overload
    def update(self, left_to_left: float) -> None:
        ...

    @overload
    def update(self, left_to_right: float) -> None:
        ...

    @overload
    def update(self, right_to_left: float) -> None:
        ...

    @overload
    def update(self, right_to_right: float) -> None:
        ...

    def update(self, **kwargs) -> None:
        """
        Updates the channel mix values.

        Args:
            **kwargs: Keyword arguments containing the channel mix values to update.
                - left_to_left (float): The amount of the left channel to send to the left channel. Must be between 0 and 1.
                - left_to_right (float): The amount of the left channel to send to the right channel. Must be between 0 and 1.
                - right_to_left (float): The amount of the right channel to send to the left channel. Must be between 0 and 1.
                - right_to_right (float): The amount of the right channel to send to the right channel. Must be between 0 and 1.

        Returns:
            None
        """
        if 'left_to_left' in kwargs:
            left_to_left = float(kwargs.pop('left_to_left'))

            if not 0 <= left_to_left <= 1:
                raise ValueError('left_to_left must be bigger than or equal to 0, and less than or equal to 1.')

            self.values['leftToLeft'] = left_to_left

        if 'left_to_right' in kwargs:
            left_to_right = float(kwargs.pop('left_to_right'))

            if not 0 <= left_to_right <= 1:
                raise ValueError('left_to_right must be bigger than or equal to 0, and less than or equal to 1.')

            self.values['leftToRight'] = left_to_right

        if 'right_to_left' in kwargs:
            right_to_left = float(kwargs.pop('right_to_left'))

            if not 0 <= right_to_left <= 1:
                raise ValueError('right_to_left must be bigger than or equal to 0, and less than or equal to 1.')

            self.values['rightToLeft'] = right_to_left

        if 'right_to_right' in kwargs:
            right_to_right = float(kwargs.pop('right_to_right'))

            if not 0 <= right_to_right <= 1:
                raise ValueError('right_to_right must be bigger than or equal to 0, and less than or equal to 1.')

            self.values['rightToRight'] = right_to_right

    def to_dict(self) -> dict[str, dict[str, float]]:
        """
        Converts the ChannelMix filter to a dictionary.

        Returns:
            dict[str, dict[str, float]]: A dictionary containing the channel mix values.
        """
        return {'channelMix': self.values}
