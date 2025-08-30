from enum import Enum
from typing import Iterable, Any, Collection

from sapiopycommons.general.exceptions import SapioException


class ArrayTransformation(Enum):
    """
    An enumeration of the different transformations that can be applied to a 2D array.
    """
    ROTATE_CLOCKWISE = 0
    ROTATE_COUNTER_CLOCKWISE = 1
    ROTATE_180_DEGREES = 2
    MIRROR_HORIZONTAL = 3
    MIRROR_VERTICAL = 4


# FR-47524: Create a DataStructureUtils class that implements various collection utility functions from our Java
# libraries.
class DataStructureUtil:
    """
    Utility class for working with data structures. Copies from ListUtil, SetUtil, and various other classes in
    our Java library.
    """
    @staticmethod
    def find_first_or_none(values: Iterable[Any]) -> Any | None:
        """
        Get the first value from an iterable, or None if the iterable is empty.

        :param values: An iterable of values.
        :return: The first value from the input, or None if the input is empty.
        """
        return next(iter(values), None)

    @staticmethod
    def remove_null_values(values: Iterable[Any]) -> list[Any]:
        """
        Remove null values from a list.

        :param values: An iterable of values.
        :return: A list containing all the non-null values from the input.
        """
        return [value for value in values if value is not None]

    @staticmethod
    def transform_2d_array(values: Collection[Collection[Any]], transformation: ArrayTransformation) \
            -> Collection[Collection[Any]]:
        """
        Perform a transformation on a 2D list.

        :param values: An iterable of iterables. The iterables should all be of the same size.
        :param transformation: The transformation to apply to the input.
        :return: A new 2D list containing the input transformed according to the specified transformation.
        """
        x: int = len(values)
        for row in values:
            y = len(row)
            if y != x:
                raise SapioException(f"Input must be a square 2D array. The provided array has a length of {x} but "
                                     f"at least one row has a length of {y}.")

        match transformation:
            case ArrayTransformation.ROTATE_CLOCKWISE:
                return [list(row) for row in zip(*values[::-1])]
            case ArrayTransformation.ROTATE_COUNTER_CLOCKWISE:
                return [list(row) for row in zip(*values)][::-1]
            case ArrayTransformation.ROTATE_180_DEGREES:
                return [row[::-1] for row in values[::-1]]
            case ArrayTransformation.MIRROR_HORIZONTAL:
                return [list(row[::-1]) for row in values]
            case ArrayTransformation.MIRROR_VERTICAL:
                return values[::-1]

        raise SapioException(f"Invalid transformation: {transformation}")

    @staticmethod
    def flatten_to_list(values: Iterable[Iterable[Any]]) -> list[Any]:
        """
        Flatten a list of lists into a single list.

        :param values: An iterable of iterables.
        :return: A single list containing all the values from the input. Elements are in the order they appear in the
            input.
        """
        return [item for sublist in values for item in sublist]

    @staticmethod
    def flatten_to_set(values: Iterable[Iterable[Any]]) -> set[Any]:
        """
        Flatten a list of lists into a single set.

        :param values: An iterable of iterables.
        :return: A single set containing all the values from the input. Elements are in the order they appear in the
            input.
        """
        return {item for subset in values for item in subset}

    @staticmethod
    def invert_dictionary(dictionary: dict[Any, Any], list_values: bool = False) \
            -> dict[Any, Any] | dict[Any, list[Any]]:
        """
        Invert a dictionary, swapping keys and values. Note that the values of the input dictionary must be hashable.

        :param dictionary: A dictionary to invert.
        :param list_values: If false, keys that share the same value in the input dictionary will be overwritten in
            the output dictionary so that only the last key remains. If true, the values of the output dictionary will
            be lists where input keys that share the same value will be stored together.
        :return: A new dictionary with the keys and values swapped.
        """
        if list_values:
            inverted = {}
            for key, value in dictionary.items():
                inverted.setdefault(value, []).append(key)
            return inverted
        return {value: key for key, value in dictionary.items()}
