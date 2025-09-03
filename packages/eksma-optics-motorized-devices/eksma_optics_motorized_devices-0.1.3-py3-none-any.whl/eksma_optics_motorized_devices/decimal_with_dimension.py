from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class DecimalWithDimension:
    """
    Represents a numeric value with a dimensional unit (e.g., '12nm', '100ms').

    :param value: The numeric portion of the value.
    :type value: int
    :param dimension: The unit or dimension (e.g., 'nm', 'ms').
    :type dimension: str
    """

    value: int
    dimension: str

    def __int__(self) -> int:
        """
        Convert the value to an integer.

        :return: Integer representation of the value.
        :rtype: int
        """
        return int(self.value)

    def __float__(self) -> float:
        """
        Convert the value to a float.

        :return: Float representation of the value.
        :rtype: float
        """
        return float(self.value)

    def __str__(self) -> str:
        """
        Return the string representation of the object.

        :return: A string combining value and dimension (e.g., '12nm').
        :rtype: str
        """
        return f"{self.value}{self.dimension}"

    @staticmethod
    def from_string(value: str) -> DecimalWithDimension:
        """
        Parse a string into a :class:``DecimalWithDimension`` instance.

        The string must consist of a numeric value followed by a non-digit dimension string.

        :param value: A string representing a dimensioned number (e.g., '12nm').
        :type value: str
        :raises ValueError: If the string format is invalid.
        :return: A new instance of :class:``DecimalWithDimension``.
        :rtype: DecimalWithDimension
        """
        match = re.search(r"^(\d+)(\D\w+)$", value)
        if not match:
            msg = f"invalid format: {value}"
            raise ValueError(msg)

        numeric_value, dimension = match.groups()

        return DecimalWithDimension(int(numeric_value), dimension)
