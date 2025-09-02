# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

import math
from abc import abstractmethod
from typing import Any

import numpy as np

from libinephany.utils import random_seeds

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class Sampler:

    def __init__(self, lower_bound: float | int | None, upper_bound: float | int | None, **kwargs) -> None:
        """
        :param lower_bound: Lower bound of the distribution to sample from.
        :param upper_bound: Upper bound of the distribution to sample from.
        :param kwargs: Miscellaneous keyword arguments.
        """

        if upper_bound is not None and lower_bound is not None and upper_bound < lower_bound:
            upper_bound, lower_bound = lower_bound, upper_bound

        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def __call__(
        self,
        number_of_samples: int = 1,
        seed: int | None = None,
    ) -> list[Any] | np.ndarray | float:
        """
        :param number_of_samples: Number of samples to make.
        :param seed: Random seed to use for distribution sampling.
        :return: List/Array of sampled values or a single sampled value.
        """

        if seed is not None:
            random_seeds.set_all_seeds(seed)

        sample = self.sample(number_of_samples=number_of_samples)

        if isinstance(sample, np.ndarray) and sample.size == 1:
            return sample.item()

        elif isinstance(sample, list) and len(sample) == 1:
            return sample[0]

        return sample

    @abstractmethod
    def sample(self, number_of_samples: int = 1, **kwargs) -> np.ndarray | list[Any]:
        """
        :param number_of_samples: Number of samples to make.
        :param kwargs: Miscellaneous keyword arguments.
        :return: Array of sampled values.
        """

        raise NotImplementedError

    @classmethod
    def get_subclasses(cls):
        """Recursively gets subclasses of the Sampler class."""
        for subclass in cls.__subclasses__():
            yield from subclass.get_subclasses()
            yield subclass


class LogUniformSampler(Sampler):

    def sample(self, number_of_samples: int = 1, **kwargs) -> np.ndarray | list[Any]:
        """
        :param number_of_samples: Number of samples to make.
        :param kwargs: Miscellaneous keyword arguments.
        :return: Array of sampled values.
        """

        return sample_from_log_uniform(
            lower_bound=self.lower_bound, upper_bound=self.upper_bound, number_of_samples=number_of_samples
        )


class UniformSampler(Sampler):

    def sample(self, number_of_samples: int = 1, **kwargs) -> np.ndarray | list[Any]:
        """
        :param number_of_samples: Number of samples to make.
        :param kwargs: Miscellaneous keyword arguments.
        :return: Array of sampled values.
        """

        return sample_from_uniform(
            lower_bound=self.lower_bound, upper_bound=self.upper_bound, number_of_samples=number_of_samples
        )


class DiscreteRangeSampler(Sampler):

    def __init__(
        self,
        step: float,
        lower_bound: float | int,
        upper_bound: float | int,
        sample_dtype: type[np.generic | float | int] = np.float64,
        **kwargs,
    ) -> None:
        """
        :param step: Difference between each value in the discrete range.
        :param lower_bound: Lower bound of the distribution to sample from.
        :param upper_bound: Upper bound of the distribution to sample from.
        :param sample_dtype: Datatype the returned samples should have.
        :param kwargs: Miscellaneous keyword arguments.
        """

        super().__init__(lower_bound=lower_bound, upper_bound=upper_bound, **kwargs)

        self.step = step
        self.sample_dtype = sample_dtype

    def sample(self, number_of_samples: int = 1, **kwargs) -> np.ndarray | list[Any]:
        """
        :param number_of_samples: Number of samples to make.
        :param kwargs: Miscellaneous keyword arguments.
        :return: Array of sampled values.
        """

        return sample_from_discrete_range(
            lower_bound=self.lower_bound,
            upper_bound=self.upper_bound,
            number_of_samples=number_of_samples,
            step=self.step,
        ).astype(self.sample_dtype)


class RoundRobinSampler(Sampler):

    def __init__(self, lower_bound: float | int, upper_bound: float | int, **kwargs) -> None:
        """
        :param lower_bound: Lower bound of the distribution to sample from.
        :param upper_bound: Upper bound of the distribution to sample from.
        :param kwargs: Miscellaneous keyword arguments.
        """
        super().__init__(lower_bound=lower_bound, upper_bound=upper_bound, **kwargs)

        self.magnitude_list = self.generate_magnitude_list()
        self.sampled_elements: set[float] = set()

    def generate_magnitude_list(self) -> list[float]:
        """
        :return: List of possible values that can be sampled in the sampler.
        """

        start_magnitude = math.floor(math.log10(self.upper_bound))
        end_magnitude = math.floor(math.log10(self.lower_bound))

        magnitude_list = []

        for magnitude in range(start_magnitude, end_magnitude - 1, -1):
            for i in range(1, 10):
                value = i * 10**magnitude

                if self.lower_bound <= value <= self.upper_bound:
                    magnitude_list.append(value)

        return magnitude_list

    def sample(self, number_of_samples: int = 1, **kwargs) -> np.ndarray | list[Any]:
        """
        :param number_of_samples: Number of samples to make.
        :param kwargs: Miscellaneous keyword arguments.
        :return: Array of sampled values.
        """

        if len(self.sampled_elements) == len(self.magnitude_list):
            self.sampled_elements = set()

        sample_choices = [element for element in self.magnitude_list if element not in self.sampled_elements]
        sample = []

        for _ in range(number_of_samples):
            choice = np.random.choice(sample_choices, size=1).item()
            sample_choices.remove(choice)
            sample.append(choice)

        self.sampled_elements.update(sample)

        return np.array(sample)


class DiscreteValueSampler(Sampler):

    def __init__(
        self,
        discrete_values: list[float | int | str],
        sample_dtype: type[np.generic | float | int | str] = np.float64,
        **kwargs,
    ) -> None:
        """
        :param discrete_values: List of discrete values to sample from.
        :param kwargs: Miscellaneous keyword arguments.
        """

        if sample_dtype == str and any(isinstance(value, str) for value in discrete_values):
            lower_bound, upper_bound = None, None

        else:
            lower_bound = min(discrete_values)
            upper_bound = max(discrete_values)

        super().__init__(lower_bound=lower_bound, upper_bound=upper_bound)  # type: ignore

        self.discrete_values = discrete_values
        self.sample_dtype = sample_dtype

    def sample(self, number_of_samples: int = 1, **kwargs) -> np.ndarray | list[Any]:
        """
        :param number_of_samples: Number of samples to make.
        :param kwargs: Miscellaneous keyword arguments.
        :return: Array of sampled values.
        """

        return sample_from_discrete_values(
            discrete_values=self.discrete_values,
            number_of_samples=number_of_samples,
        ).astype(self.sample_dtype)


class DiscreteValueListSampler(DiscreteValueSampler):

    def __init__(
        self,
        length: int,
        discrete_values: list[float | int | str],
        sample_dtype: type[np.generic | float | int | str] = np.float64,
        **kwargs,
    ) -> None:
        """
        :param length: Length of list to sample.
        :param discrete_values: List of discrete values to sample from.
        :param kwargs: Miscellaneous keyword arguments.
        """

        super().__init__(discrete_values=discrete_values, sample_dtype=sample_dtype)
        self.list_length = length

    def sample(self, number_of_samples: int = 1, **kwargs) -> list[np.ndarray | list[Any]]:
        """
        :param number_of_samples: Number of samples to make.
        :param kwargs: Miscellaneous keyword arguments.
        :return: Array of sampled values.
        """

        return [super().sample(number_of_samples=self.list_length) for _ in range(number_of_samples)]


class RoundRobinDiscreteValueSampler(Sampler):

    def __init__(
        self,
        discrete_values: list[float | int],
        sample_dtype: type[np.generic | float | int] = np.float64,
        **kwargs,
    ) -> None:
        """
        :param discrete_values: List of discrete values to sample from.
        :param kwargs: Miscellaneous keyword arguments.
        """

        super().__init__(lower_bound=min(discrete_values), upper_bound=max(discrete_values))

        self.discrete_values = discrete_values
        self.sample_dtype = sample_dtype

        self.sampled_elements: set[float] = set()

    def sample(self, number_of_samples: int = 1, **kwargs) -> np.ndarray | list[Any]:
        """
        :param number_of_samples: Number of samples to make.
        :param kwargs: Miscellaneous keyword arguments.
        :return: Array of sampled values.
        """

        if len(self.sampled_elements) == len(self.discrete_values):
            self.sampled_elements = set()

        sample_choices = [element for element in self.discrete_values if element not in self.sampled_elements]
        sample = []

        for _ in range(number_of_samples):
            choice = np.random.choice(sample_choices, size=1).item()
            sample_choices.remove(choice)
            sample.append(choice)

        self.sampled_elements.update(sample)

        return np.array(sample)


# ======================================================================================================================
#
# FUNCTIONS
#
# ======================================================================================================================


def build_sampler(sampler_name: str, lower_bound: float | int, upper_bound: float | int, **kwargs) -> Sampler:
    """
    :param sampler_name: Name of the sampler to build.
    :param lower_bound: Smallest value that can be sampled by the sampler.
    :param upper_bound: Largest value that can be sampled by the sampler.
    :param kwargs: Miscellaneous keyword arguments that may be required depending on the sampler chosen.
    :return: Constructed sampler.
    """

    possible_samplers = {sampler_type.__name__: sampler_type for sampler_type in Sampler.get_subclasses()}

    try:
        return possible_samplers[sampler_name](lower_bound=lower_bound, upper_bound=upper_bound, **kwargs)  # type: ignore

    except KeyError as e:
        raise ValueError(
            f"Unrecognised sampler {sampler_name}! Possible values: {list(possible_samplers.keys())}."
        ) from e


def sample_from_log_uniform(
    lower_bound: float | int, upper_bound: float | int, number_of_samples: int = 1
) -> np.ndarray:
    """
    :param lower_bound: Lower bound of the distribution.
    :param upper_bound: Upper bound of the distribution.
    :param number_of_samples: Number of samples to make.
    :return: Sampled result.
    """

    sample = np.random.uniform(math.log(lower_bound), math.log(upper_bound), size=number_of_samples)
    sample = np.exp(sample)

    return sample


def sample_from_uniform(lower_bound: float | int, upper_bound: float | int, number_of_samples: int = 1) -> np.ndarray:
    """
    :param lower_bound: Lower bound of the distribution.
    :param upper_bound: Upper bound of the distribution.
    :param number_of_samples: Number of samples to make.
    :return: Sampled result.
    """

    return np.random.uniform(lower_bound, upper_bound, size=number_of_samples)


def sample_from_discrete_range(
    lower_bound: float | int, upper_bound: float | int, step: float, number_of_samples: int = 1
) -> np.ndarray:
    """
    :param lower_bound: Lower bound of the distribution.
    :param upper_bound: Upper bound of the distribution.
    :param step: Difference between each value in the discrete range.
    :param number_of_samples: Number of samples to make.
    :return: Sampled result.
    """

    sample = np.arange(lower_bound, upper_bound + step, step, dtype=np.float64)

    sample = np.random.choice(sample, size=number_of_samples)

    return sample


def sample_from_discrete_values(discrete_values: list[float | int | str], number_of_samples: int = 1) -> np.ndarray:
    """
    :param discrete_values: List of discrete values to sample from.
    :param number_of_samples: Number of samples to make.
    :return: Sampled result.
    """

    sample = np.random.choice(discrete_values, size=number_of_samples)

    return sample
