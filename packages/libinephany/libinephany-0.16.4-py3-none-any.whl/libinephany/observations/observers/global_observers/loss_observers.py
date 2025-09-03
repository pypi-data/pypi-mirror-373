# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

import math
from typing import Any

from libinephany.observations.observation_utils import StatisticStorageTypes
from libinephany.observations.observers.base_observers import GlobalObserver
from libinephany.observations.observers.global_observers.base_classes import (
    LHOPTCheckpointBaseObserver,
    LHOPTOuterStepBaseObserver,
)
from libinephany.observations.observers.global_observers.constants import LHOPT_CONSTANTS
from libinephany.pydantic_models.schemas.observation_models import ObservationInputs
from libinephany.pydantic_models.schemas.tensor_statistics import TensorStatistics
from libinephany.pydantic_models.states.hyperparameter_states import HyperparameterStates

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class TrainingLoss(GlobalObserver):

    @property
    def can_standardize(self) -> bool:
        """
        :return: Whether the observation can be standardized.
        """

        return False

    def _get_observation_format(self) -> StatisticStorageTypes:
        """
        :return: Format the observation returns data in. Must be one of the enum attributes in the StatisticStorageTypes
        enumeration class.
        """

        return StatisticStorageTypes.FLOAT

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
        names to floats or TensorStatistic models.
        :param action_taken: Action taken by the agent this class instance is assigned to.
        :return: Single float/int, list of floats/ints or TensorStatistics model to add to the observation vector.
        """

        return observation_inputs.training_loss

    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping statistic tracker class names to kwargs for the class or None if no kwargs are
        needed.
        """

        return {}


class ValidationLoss(GlobalObserver):

    @property
    def can_standardize(self) -> bool:
        """
        :return: Whether the observation can be standardized.
        """

        return False

    def _get_observation_format(self) -> StatisticStorageTypes:
        """
        :return: Format the observation returns data in. Must be one of the enum attributes in the StatisticStorageTypes
        enumeration class.
        """

        return StatisticStorageTypes.FLOAT

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
        names to floats or TensorStatistic models.
        :param action_taken: Action taken by the agent this class instance is assigned to.
        :return: Single float/int, list of floats/ints or TensorStatistics model to add to the observation vector.
        """

        return observation_inputs.validation_loss

    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping statistic tracker class names to kwargs for the class or None if no kwargs are
        needed.
        """

        return {}


class LossRatio(GlobalObserver):

    def _get_observation_format(self) -> StatisticStorageTypes:
        """
        :return: Format the observation returns data in. Must be one of the enum attributes in the StatisticStorageTypes
        enumeration class.
        """

        return StatisticStorageTypes.FLOAT

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
        names to floats or TensorStatistic models.
        :param action_taken: Action taken by the agent this class instance is assigned to.
        :return: Single float/int, list of floats/ints or TensorStatistics model to add to the observation vector.
        """

        if observation_inputs.validation_loss == 0:
            return 0

        return observation_inputs.training_loss / observation_inputs.validation_loss

    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping statistic tracker class names to kwargs for the class or None if no kwargs are
        needed.
        """

        return {}


class TrainingScore(GlobalObserver):

    def _get_observation_format(self) -> StatisticStorageTypes:
        """
        :return: Format the observation returns data in. Must be one of the enum attributes in the StatisticStorageTypes
        enumeration class.
        """

        return StatisticStorageTypes.FLOAT

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
        names to floats or TensorStatistic models.
        :param action_taken: Action taken by the agent this class instance is assigned to.
        :return: Single float/int, list of floats/ints or TensorStatistics model to add to the observation vector.
        """

        return observation_inputs.training_score

    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping statistic tracker class names to kwargs for the class or None if no kwargs are
        needed.
        """

        return {}


class ValidationScore(GlobalObserver):

    def _get_observation_format(self) -> StatisticStorageTypes:
        """
        :return: Format the observation returns data in. Must be one of the enum attributes in the StatisticStorageTypes
        enumeration class.
        """

        return StatisticStorageTypes.FLOAT

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
        names to floats or TensorStatistic models.
        :param action_taken: Action taken by the agent this class instance is assigned to.
        :return: Single float/int, list of floats/ints or TensorStatistics model to add to the observation vector.
        """

        return observation_inputs.validation_score

    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping statistic tracker class names to kwargs for the class or None if no kwargs are
        needed.
        """

        return {}


class LHOPTTrainingLoss(LHOPTOuterStepBaseObserver):
    """
    This is a global observer from the OpenAI paper "Learning to Optimize with Reinforcement Learning"
    https://arxiv.org/abs/2305.18291.

    It returns three-dimensional observations: [is_nan, is_inf, cdf_feature] for training loss values.

    This observer use the CDF calculation from the paper and applies CDF transformation using the CDF mean and std.
    """

    def _observe(
        self,
        observation_inputs: ObservationInputs,
        hyperparameter_states: HyperparameterStates,
        tracked_statistics: dict[str, dict[str, float | TensorStatistics]],
        action_taken: float | int | None,
    ) -> list[int | float]:
        """
        :param observation_inputs: Observation input metrics not calculated with statistic trackers.
        :param hyperparameter_states: HyperparameterStates that manages the hyperparameters.
        :param tracked_statistics: Dictionary mapping statistic tracker class names to dictionaries mapping module
        names to floats or TensorStatistic models.
        :param action_taken: Action taken by the agent this class instance is assigned to.
        :return: List of three features: [is_nan, is_inf, cdf_feature]
        """

        training_loss = observation_inputs.training_loss

        cdf_feature = self._compute_cdf_feature(training_loss)

        self._update_time()

        return [int(math.isnan(training_loss)), int(math.isinf(training_loss)), cdf_feature]

    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping statistic tracker class names to kwargs for the class or None if no kwargs are
        needed.
        """

        return {}

    def reset(self) -> None:
        """Reset the observer by clearing the time series."""
        self._time_series: list[tuple[float, float]] = []
        self._current_time: float = 0.0

    @property
    def vector_length(self) -> int:
        """
        :return: Length of the vector returned by this observation if it returns a vector.
        """
        return 3  # [is_nan, is_inf, cdf_feature]


class LHOPTValidationLoss(LHOPTOuterStepBaseObserver):
    """
    This is a global observer from the OpenAI paper "Learning to Optimize with Reinforcement Learning"
    https://arxiv.org/abs/2305.18291.

    It returns three-dimensional observations: [is_nan, is_inf, cdf_feature] for validation loss values.

    This observer use the CDF calculation from the paper and applies CDF transformation using the CDF mean and std.
    """

    def _observe(
        self,
        observation_inputs: ObservationInputs,
        hyperparameter_states: HyperparameterStates,
        tracked_statistics: dict[str, dict[str, float | TensorStatistics]],
        action_taken: float | int | None,
    ) -> list[int | float]:
        """
        :param observation_inputs: Observation input metrics not calculated with statistic trackers.
        :param hyperparameter_states: HyperparameterStates that manages the hyperparameters.
        :param tracked_statistics: Dictionary mapping statistic tracker class names to dictionaries mapping module
        names to floats or TensorStatistics models.
        :param action_taken: Action taken by the agent this class instance is assigned to.
        :return: List of three features: [is_nan, is_inf, cdf_feature]
        """

        validation_loss = observation_inputs.validation_loss

        cdf_feature = self._compute_cdf_feature(validation_loss)

        self._update_time()

        return [int(math.isnan(validation_loss)), int(math.isinf(validation_loss)), cdf_feature]

    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping statistic tracker class names to kwargs for the class or None if no kwargs are
        needed.
        """

        return {}

    def reset(self) -> None:
        """Reset the observer by clearing the time series."""
        self._time_series: list[tuple[float, float]] = []
        self._current_time: float = 0.0

    @property
    def vector_length(self) -> int:
        """
        :return: Length of the vector returned by this observation if it returns a vector.
        """
        return 3  # [is_nan, is_inf, cdf_feature]


class LHOPTLossRatio(LHOPTOuterStepBaseObserver):
    """
    This is a global observer from the OpenAI paper "Learning to Optimize with Reinforcement Learning"
    https://arxiv.org/abs/2305.18291.

    It returns three-dimensional observations: [is_nan, tanh, cdf_feature] for loss ratio values.

    This observer computes the logarithm of the ratio between validation_score and training_score,
    providing three features:
    1. is_nan - whether the log ratio is NaN
    2. tanh(log_ratio) - bounded feature using hyperbolic tangent
    3. cdf_feature - CDF transformed feature using CDF mean and std
    """

    def _observe(
        self,
        observation_inputs: ObservationInputs,
        hyperparameter_states: HyperparameterStates,
        tracked_statistics: dict[str, dict[str, float | TensorStatistics]],
        action_taken: float | int | None,
    ) -> list[int | float]:
        """
        :param observation_inputs: Observation input metrics not calculated with statistic trackers.
        :param hyperparameter_states: HyperparameterStates that manages the hyperparameters.
        :param tracked_statistics: Dictionary mapping statistic tracker class names to dictionaries mapping module
        names to floats or TensorStatistics models.
        :param action_taken: Action taken by the agent this class instance is assigned to.
        :return: List of three features: [is_nan, tanh, cdf_feature]
        """

        log_ratio = self._compute_log_ratio(
            training_score=observation_inputs.training_score, validation_score=observation_inputs.validation_score
        )

        tanh_feature = math.tanh(max(-LHOPT_CONSTANTS["TANH_BOUND"], min(LHOPT_CONSTANTS["TANH_BOUND"], log_ratio)))

        cdf_feature = self._compute_cdf_feature(log_ratio)

        self._update_time()

        return [int(math.isnan(log_ratio)), tanh_feature, cdf_feature]

    def _compute_log_ratio(self, training_score: float, validation_score: float) -> float:
        """
        Compute the log ratio of validation_score to training_score.

        :param training_score: Training score value
        :param validation_score: Validation score value
        :return: Log ratio value
        """
        if training_score <= 0:
            return 0.0

        if validation_score <= 0:
            return 0.0

        # Calculate the ratio of validation_score to training_score
        score_ratio = validation_score / training_score

        return math.log(score_ratio)

    @property
    def vector_length(self) -> int:
        """
        :return: Length of the vector returned by this observation if it returns a vector.
        """
        return 3  # [is_nan, tanh, cdf_feature]


class PercentileOfLossAtEachCheckpoint(LHOPTCheckpointBaseObserver):
    """
    Observer that computes percentile of loss values at each checkpoint.
    """

    def __init__(
        self,
        checkpoint_interval: int = LHOPT_CONSTANTS["DEFAULT_CHECKPOINT_INTERVAL"],
        percentile: float = LHOPT_CONSTANTS["DEFAULT_PERCENTILE"],
        **kwargs,
    ) -> None:
        """
        :param checkpoint_interval: How often to create checkpoints (in training steps).
        :param percentile: Percentile to compute (0.0 to 1.0).
        :param kwargs: Miscellaneous keyword arguments.
        """
        super().__init__(checkpoint_interval=checkpoint_interval, **kwargs)
        self.percentile = max(0.0, min(1.0, percentile))

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
        :return: Percentile value of loss at checkpoint.
        """
        training_loss = observation_inputs.training_loss

        # Handle cold start
        self._cold_start(training_loss)

        # Update history
        self._update_history(training_loss)

        # Check if we should create a checkpoint
        if self._should_create_checkpoint():
            # Compute percentile
            sorted_history = sorted(self._history)
            index = int(self.percentile * (len(sorted_history) - 1))
            percentile_value = sorted_history[index]

            self._cached_observation = percentile_value
            return percentile_value
        else:
            # Return last value during warm-up
            self._cached_observation = self.last_value
            return self.last_value
