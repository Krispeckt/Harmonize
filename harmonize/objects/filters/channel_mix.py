from typing import overload

from harmonize.abstract import Filter

__all__ = (
    "ChannelMix",
)


class ChannelMix(Filter[dict[str, float]]):
    """
    Represents a channel mix filter. Extended from :class:`harmonize.abstract.Filter`
    """

    def __init__(
            self, left_to_left: float = 1.0,
            left_to_right: float = 0.0,
            right_to_left: float = 0.0,
            right_to_right: float = 0.0
    ) -> None:
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
        Updates the channel mix values of the filter.

        Note
        ----
            All parameters must be bigger than or equal to 0, and less than or equal to 1.

        Parameters
        ----------
            **kwargs
                A dictionary containing the new channel mix values to update.

        Returns
        -------
            None
                This function does not return any value. It updates the internal state of the filter.

        Raises
        ------
            ValueError
                If any of the new channel mix values are not within the range [0, 1].
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
