# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

from abc import abstractmethod
from typing import Any, final

import numpy as np

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class Standardizer:
    """
    Abstract class which defines the interface for environment observation standardizers to use.
    """

    def __init__(self, **kwargs) -> None:
        """
        :param kwargs: Keyword arguments included to allow for any signature in subclasses.
        """

        self._running_statistics: dict[str, Any] = {}

    @final
    def __call__(self, statistics_key: str, value_to_standardize: float) -> float:
        """
        :param statistics_key: Key which these statistics are stored under.
        :param value_to_standardize: New metric value to update statistics with and then standardize.
        :return: Standardized value.
        """

        return self.standardize(statistics_key=statistics_key, value_to_standardize=value_to_standardize)

    @final
    def _get_running_statistics(self, statistics_key: str) -> Any:
        """
        :param statistics_key: Key of the statistics to retrieve from stored statistics.
        :return: Stored statistics.
        """

        if statistics_key not in self._running_statistics:
            self._running_statistics[statistics_key] = self._get_default_statistics()

        return self._running_statistics[statistics_key]

    @abstractmethod
    def _get_default_statistics(self) -> Any:
        """
        :return: Default value of the statistics when they are not already present in the stored statistics.
        """

        raise NotImplementedError

    @abstractmethod
    def _standardize_value(self, statistics_key: str, value_to_standardize: float) -> float:
        """
        :param statistics_key: Key which these statistics are stored under.
        :param value_to_standardize: New metric value to standardize.
        :return: Standardized value.
        """

        raise NotImplementedError

    @abstractmethod
    def _update_running_statistics(self, statistics_key: str, value_to_standardize: float) -> None:
        """
        :param statistics_key: Key which these statistics are stored under.
        :param value_to_standardize: New metric value to update statistics with.
        """

        raise NotImplementedError

    @final
    def standardize(self, statistics_key: str, value_to_standardize: float) -> float:
        """
        :param statistics_key: Key which these statistics are stored under.
        :param value_to_standardize: New metric value to update statistics with and then standardize.
        :return: Standardized value.
        """

        try:
            self._update_running_statistics(statistics_key=statistics_key, value_to_standardize=value_to_standardize)
            standardized = self._standardize_value(
                statistics_key=statistics_key, value_to_standardize=value_to_standardize
            )
        except ArithmeticError:
            standardized = float("nan")

        return standardized

    def reset(self) -> None:
        """
        Empties the stored statistics dictionary.
        """

        self._running_statistics = {}


class EMAZScoreStandardizer(Standardizer):
    """
    Standardizer which standardizes metrics according to Z-scores computed from running means and variances using
    Exponential Moving Average.
    """

    def __init__(
        self,
        minimum_standard_deviation: float = 1e-2,
        standardization_epsilon: float = 1e-4,
        ema_learning_rate: float = 0.4,
        default_mean: float = 0,
        default_variance: float = 1,
        default_count: int = 0,
        **kwargs,
    ) -> None:
        """
        :param minimum_standard_deviation: Minimum value the standard deviation of a statistic that can be used in
        Z-score standardization.
        :param standardization_epsilon: Small value to add to the denominator of the Z-score standardization.
        :param ema_learning_rate: Factor which alters how quickly the EMA adapts to new values.
        :param default_mean: Default mean value for newly added statistics.
        :param default_variance: Default variance value for newly added statistics.
        :param default_count: Default counter value for newly added statistics.
        :param kwargs: Keyword arguments included to allow for any signature in subclasses.
        """

        super().__init__(**kwargs)

        self.minimum_standard_deviation = minimum_standard_deviation
        self.standardization_epsilon = standardization_epsilon

        self.ema_learning_rate = ema_learning_rate

        self.default_mean = default_mean
        self.default_variance = default_variance
        self.default_count = default_count

    def _get_default_statistics(self) -> tuple[float, float, int]:
        """
        :return: Default value of the statistics when they are not already present in the stored statistics.
        """

        return self.default_mean, self.default_variance, self.default_count

    def _standardize_value(self, statistics_key: str, value_to_standardize: float) -> float:
        """
        :param statistics_key: Key which these statistics are stored under.
        :param value_to_standardize: New metric value to standardize.
        :return: Standardized value.
        """

        current_ema, current_ema_variance, _ = self._get_running_statistics(statistics_key=statistics_key)

        standard_deviation = np.sqrt(current_ema_variance)
        standard_deviation = max(standard_deviation, self.minimum_standard_deviation)

        numerator = value_to_standardize - current_ema
        denominator = standard_deviation + self.standardization_epsilon

        standard_value = numerator / denominator
        assert isinstance(standard_value, float)

        return standard_value

    def _update_running_statistics(self, statistics_key: str, value_to_standardize: float) -> None:
        """
        :param statistics_key: Key which these statistics are stored under.
        :param value_to_standardize: New metric value to update statistics with.

        :todo: Vectorise this class using numpy.
        """

        current_ema, current_ema_variance, count = self._get_running_statistics(statistics_key=statistics_key)

        count += 1

        new_ema = self.ema_learning_rate * value_to_standardize + (1 - self.ema_learning_rate) * current_ema

        new_variance = self.ema_learning_rate * (value_to_standardize - new_ema) ** 2
        new_ema_variance = new_variance + (1 - self.ema_learning_rate) * current_ema_variance

        self._running_statistics[statistics_key] = (new_ema, new_ema_variance, count)


# ======================================================================================================================
#
# FUNCTIONS
#
# ======================================================================================================================


def get_standardizer(
    standardizer_name: str | None,
    standardizer_arguments: dict[str, Any],
) -> Standardizer | None:
    """
    :param standardizer_name: Name of the standardizer to get.
    :param standardizer_arguments: Arguments to instantiate the standardizer with.
    :return: Instantiated standardizer.
    """

    if standardizer_name is None:
        return None

    elif standardizer_name == EMAZScoreStandardizer.__name__:
        standardizer = EMAZScoreStandardizer

    else:
        raise ValueError(f"Unrecognised standardizer {standardizer_name}!")

    return standardizer(**standardizer_arguments)
