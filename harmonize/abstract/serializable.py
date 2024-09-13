from __future__ import annotations

__all__ = (
    "Serializable",
)


class Serializable:
    """
    Abstract base class for objects that can be serialized and deserialized.
    """

    @classmethod
    def from_dict(cls, data: dict) -> Serializable:
        """
        Creates and returns a new instance of the class from the given dictionary data.

        Parameters:
            data (dict): A dictionary containing the data to initialize the new instance.

        Returns:
            Serializable: A new instance of the class initialized with the given data.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError

    @property
    def raw(self) -> dict:
        # Implementation of the raw property goes here.
        return ...
