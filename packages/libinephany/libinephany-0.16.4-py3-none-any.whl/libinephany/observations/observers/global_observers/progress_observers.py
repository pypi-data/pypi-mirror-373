# ======================================================================================================================
#
# imports
#
# ======================================================================================================================

from typing import Any

from libinephany.observations.observation_utils import StatisticStorageTypes
from libinephany.observations.observers.base_observers import GlobalObserver
from libinephany.observations.observers.global_observers.base_classes import LHOPTCheckpointBaseObserver
from libinephany.pydantic_models.schemas.observation_models import ObservationInputs
from libinephany.pydantic_models.schemas.tensor_statistics import TensorStatistics
from libinephany.pydantic_models.states.hyperparameter_states import HyperparameterStates


class TrainingProgress(GlobalObserver):

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

        return observation_inputs.training_progress

    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping statistic tracker class names to kwargs for the class or None if no kwargs are
        needed.
        """

        return {}


class EpochsCompleted(GlobalObserver):

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

        return observation_inputs.epochs_completed

    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping statistic tracker class names to kwargs for the class or None if no kwargs are
        needed.
        """

        return {}


class ProgressAtEachCheckpoint(LHOPTCheckpointBaseObserver):
    """
    This is a global observer from the paper "Learning to Optimize with Reinforcement Learning"
    https://arxiv.org/abs/2305.18291.

    It returns a single float value that is the training progress at the current checkpoint.
    The observation tracks training progress and returns the progress value only when a checkpoint is reached.
    """

    def _observe(
        self,
        observation_inputs: ObservationInputs,
        hyperparameter_states: HyperparameterStates,
        tracked_statistics: dict[str, dict[str, float | TensorStatistics]],
        action_taken: float | int | None,
    ) -> float:
        """
        Returns training progress at each checkpoint interval.

        Before checkpoint: returns progress towards next checkpoint (0 to 1)
        At checkpoint: returns the actual training progress value
        """
        current_progress = observation_inputs.training_progress

        # Cold start: If the last progress is not set, set it to the first progress record
        self._cold_start(current_progress)

        self._update_history(current_progress)

        # Check if we should create a checkpoint
        if self._should_create_checkpoint():
            # Return the progress at this checkpoint
            self.last_value = current_progress
            return current_progress
        else:
            return self.last_value
