# ======================================================================================================================
#
# BASE CLASSES
#
# ======================================================================================================================

from abc import ABC, abstractmethod
from typing import Any

from libinephany.observations.observation_utils import StatisticStorageTypes, compute_cdf_feature
from libinephany.observations.observers.base_observers import GlobalObserver
from libinephany.observations.observers.global_observers.constants import LHOPT_CONSTANTS
from libinephany.pydantic_models.schemas.observation_models import ObservationInputs
from libinephany.pydantic_models.schemas.tensor_statistics import TensorStatistics
from libinephany.pydantic_models.states.hyperparameter_states import HyperparameterStates


class LHOPTOuterStepBaseObserver(GlobalObserver, ABC):
    """
    Base class for LHOPT outer step observers to eliminate duplicate code.
    """

    def __init__(
        self,
        decay_factor: float = LHOPT_CONSTANTS["DEFAULT_DECAY_FACTOR"],
        time_window: int = LHOPT_CONSTANTS["DEFAULT_TIME_WINDOW"],
        **kwargs,
    ) -> None:
        """
        :param decay_factor: Decay factor for CDF calculation in [1, 2.5, 5, 10, 20]
        :param time_window: Number of time steps to consider for CDF calculation
        :param kwargs: Other observation keyword arguments.
        """
        super().__init__(**kwargs)
        self.decay_factor = max(0.0, decay_factor)
        self.time_window = max(1, time_window)

        # Store time series data for CDF calculation
        self._time_series: list[tuple[float, float]] = []  # (time, value) pairs
        self._current_time: float = 0.0

    @property
    def can_standardize(self) -> bool:
        """
        This observer has its own CDF calculation, no need to standardize.
        :return: Whether the observation can be standardized.
        """
        return False

    def _get_observation_format(self) -> StatisticStorageTypes:
        """
        :return: Format the observation returns data in. Must be one of the StatisticStorageTypes
        enumeration class.
        """
        return StatisticStorageTypes.VECTOR

    def _compute_cdf_feature(self, value: float) -> float:
        """
        Compute CDF feature for the given value.
        training loss will be added to the time series after this call.
        :param value: The value to compute CDF feature for
        :return: CDF feature value
        """
        return compute_cdf_feature(value, self._time_series, self.decay_factor, self._current_time, self.time_window)

    def _update_time(self) -> None:
        """Update the current time counter."""
        self._current_time += 1.0

    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping statistic tracker class names to kwargs for the class or None if no kwargs are
        needed.
        """
        return {}

    def reset(self) -> None:
        """Reset the observer by clearing the time series."""
        self._time_series = []
        self._current_time = 0.0

    @abstractmethod
    def _observe(
        self,
        observation_inputs: ObservationInputs,
        hyperparameter_states: HyperparameterStates,
        tracked_statistics: dict[str, dict[str, float | TensorStatistics]],
        action_taken: float | int | None,
    ) -> float | int | list[int | float] | TensorStatistics:
        """
        :param observation_inputs: Observation input metrics not calculated with statistic trackers.
        :param hyperparameter_states: HyperparameterStates that manages the hyperparameters.
        :param tracked_statistics: Dictionary mapping statistic tracker class names to dictionaries mapping module
        :param action_taken: Action taken by the agent this class instance is assigned to.
        """
        raise NotImplementedError


class LHOPTCheckpointBaseObserver(GlobalObserver, ABC):
    """
    Base class for checkpoint-based observers to eliminate duplicate code.
    """

    def __init__(self, checkpoint_interval: int = LHOPT_CONSTANTS["DEFAULT_CHECKPOINT_INTERVAL"], **kwargs) -> None:
        """
        :param checkpoint_interval: How often to create checkpoints (in outer model steps).
        :param kwargs: Miscellaneous keyword arguments.
        """
        super().__init__(**kwargs)
        self.checkpoint_interval = checkpoint_interval
        self._history: list[float] = []
        self.last_value: float | None = None

    @property
    def can_standardize(self) -> bool:
        """
        This observer has its own CDF calculation, no need to standardize.
        :return: Whether the observation can be standardized.
        """
        return False

    def _get_observation_format(self) -> StatisticStorageTypes:
        """
        :return: Format the observation returns data in.
        """
        return StatisticStorageTypes.FLOAT

    def _update_history(self, value: float) -> None:
        """
        Update the history with a new value and maintain sliding window.

        :param value: The new value to add to history
        """
        self._history.append(value)

        # Keep only the last checkpoint_interval values for sliding window
        if len(self._history) > self.checkpoint_interval:
            self._history = self._history[-self.checkpoint_interval :]

    def _should_create_checkpoint(self) -> bool:
        """
        Check if we should create a checkpoint.

        :return: True if checkpoint should be created, False otherwise
        """
        return len(self._history) >= self.checkpoint_interval

    def _cold_start(self, value: float) -> None:
        """
        Handle cold start by setting the last value if not already set.

        :param value: The value to set as last value if cold start
        """
        if self.last_value is None:
            self.last_value = value

    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping statistic tracker class names to kwargs for the class or None if no kwargs are
        needed.
        """
        return {}

    def reset(self) -> None:
        """Reset the observer by clearing history."""
        self._history = []
        self.last_value = None

    @abstractmethod
    def _observe(
        self,
        observation_inputs: ObservationInputs,
        hyperparameter_states: HyperparameterStates,
        tracked_statistics: dict[str, dict[str, float | TensorStatistics]],
        action_taken: float | int | None,
    ) -> float | int | list[int | float] | TensorStatistics:
        """
        :param observation_inputs: Observation input metrics not calculated with statistic trackers.
        :param hyperparameter_states: HyperparameterStates that manages the hyperparameters.
        :param tracked_statistics: Dictionary mapping statistic tracker class names to dictionaries mapping module
        :param action_taken: Action taken by the agent this class instance is assigned to.
        """
        raise NotImplementedError
