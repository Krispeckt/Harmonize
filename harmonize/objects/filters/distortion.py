from typing import overload

from harmonize.abstract import Filter

__all__ = (
    "Distortion",
)


class Distortion(Filter[dict[str, float]]):
    def __init__(
            self,
            sin_offset: float = 0.0,
            sin_scale: float = 1.0,
            cos_offset: float = 0.0,
            cos_scale: float = 1.0,
            tan_offset: float = 0.0,
            tan_scale: float = 1.0,
            offset: float = 0.0,
            scale: float = 1.0
    ) -> None:
        """
        Initializes a new instance of the Distortion filter.

        Args:
            sin_offset (float): The sine offset value. Defaults to 0.0.
            sin_scale (float): The sine scale value. Defaults to 1.0.
            cos_offset (float): The cosine offset value. Defaults to 0.0.
            cos_scale (float): The cosine scale value. Defaults to 1.0.
            tan_offset (float): The tangent offset value. Defaults to 0.0.
            tan_scale (float): The tangent scale value. Defaults to 1.0.
            offset (float): The offset value. Defaults to 0.0.
            scale (float): The scale value. Defaults to 1.0.

        Returns:
            None
        """
        super().__init__({
            'sinOffset': sin_offset,
            'sinScale': sin_scale,
            'cosOffset': cos_offset,
            'cosScale': cos_scale,
            'tanOffset': tan_offset,
            'tanScale': tan_scale,
            'offset': offset,
            'scale': scale
        })

    @overload
    def update(self, sin_offset: float) -> None:
        ...

    @overload
    def update(self, sin_scale: float) -> None:
        ...

    @overload
    def update(self, cos_offset: float) -> None:
        ...

    @overload
    def update(self, cos_scale: float) -> None:
        ...

    @overload
    def update(self, tan_offset: float) -> None:
        ...

    @overload
    def update(self, tan_scale: float) -> None:
        ...

    @overload
    def update(self, offset: float) -> None:
        ...

    @overload
    def update(self, scale: float) -> None:
        ...

    def update(self, **kwargs) -> None:
        """
        Updates the distortion filter's values.

        Args:
            **kwargs: Keyword arguments to update the filter's values.
                - sin_offset (float): The sine offset value.
                - sin_scale (float): The sine scale value.
                - cos_offset (float): The cosine offset value.
                - cos_scale (float): The cosine scale value.
                - tan_offset (float): The tangent offset value.
                - tan_scale (float): The tangent scale value.
                - offset (float): The offset value.
                - scale (float): The scale value.

        Returns:
            None
        """
        if 'sin_offset' in kwargs:
            self.values['sinOffset'] = float(kwargs.pop('sin_offset'))

        if 'sin_scale' in kwargs:
            self.values['sinScale'] = float(kwargs.pop('sin_scale'))

        if 'cos_offset' in kwargs:
            self.values['cosOffset'] = float(kwargs.pop('cos_offset'))

        if 'cos_scale' in kwargs:
            self.values['cosScale'] = float(kwargs.pop('cos_scale'))

        if 'tan_offset' in kwargs:
            self.values['tanOffset'] = float(kwargs.pop('tan_offset'))

        if 'tan_scale' in kwargs:
            self.values['tanScale'] = float(kwargs.pop('tan_scale'))

        if 'offset' in kwargs:
            self.values['offset'] = float(kwargs.pop('offset'))

        if 'scale' in kwargs:
            self.values['scale'] = float(kwargs.pop('scale'))

    def to_dict(self) -> dict[str, dict[str, float]]:
        """
        Converts the distortion filter to a dictionary representation.

        Returns:
            dict[str, dict[str, float]]: A dictionary containing the distortion filter's values.
        """
        return {'distortion': self.values}
