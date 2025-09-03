# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable

import numpy as np

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class HyperparameterTransformType(Enum):

    IDENTITY = "identity"
    LOG = "log"
    LOG1M = "log1m"


class HyperparameterTransform(ABC):
    """Abstract class for hyperparameter transformations."""

    @abstractmethod
    def to_internal(self, value: float | int) -> float | int:
        """Transforms an 'external' hyperparameter value into an 'internal' one."""

        raise NotImplementedError

    @abstractmethod
    def to_external(self, value: float | int) -> float | int:
        """Transforms an 'internal' hyperparameter value into an 'external' one."""

        raise NotImplementedError


class IdentityTransform(HyperparameterTransform):
    """Applies an identity transform to a hyperparameter."""

    def to_internal(self, value: float | int) -> float | int:
        return value

    def to_external(self, value: float | int) -> float | int:
        return value


class LogTransform(HyperparameterTransform):
    """Applies a logarithmic transform to a hyperparameter."""

    def to_internal(self, value: float | int) -> float | int:
        return np.log(value)

    def to_external(self, value: float | int) -> float | int:
        return np.exp(value)


class Log1mTransform(HyperparameterTransform):
    """Transforms a variable by log(1-x)."""

    def to_internal(self, value: float | int) -> float | int:
        return np.log1p(-value)

    def to_external(self, value: float | int) -> float | int:
        return -np.expm1(value)


# ======================================================================================================================
#
# CONSTANTS
#
# ======================================================================================================================

HYPERPARAMETER_TRANSFORM_REGISTRY: dict[HyperparameterTransformType, type[HyperparameterTransform]] = {
    HyperparameterTransformType.IDENTITY: IdentityTransform,
    HyperparameterTransformType.LOG: LogTransform,
    HyperparameterTransformType.LOG1M: Log1mTransform,
}

# ======================================================================================================================
#
# FUNCTIONS
#
# ======================================================================================================================


def transform_and_sort_hparam_values(
    transform_fn: Callable[[float | int], float | int], first_value: float | int, second_value: float | int
) -> tuple[float | int, float | int]:
    """
    :param transform_fn: The transform function to apply to the values.
    :param first_value: First value to sort.
    :param second_value: Second value to sort.
    :return: Tuple of the two given values with the smaller value being the first element.
    """
    first_value = transform_fn(first_value)
    second_value = transform_fn(second_value)

    return min(first_value, second_value), max(first_value, second_value)
