# ======================================================================================================================
#
# GRADIENT OBSERVERS
#
# ======================================================================================================================

from typing import Any

from libinephany.observations import observation_utils, statistic_trackers
from libinephany.observations.observation_utils import StatisticStorageTypes
from libinephany.observations.observers.base_observers import GlobalObserver
from libinephany.observations.observers.global_observers.base_classes import LHOPTBaseObserver
from libinephany.observations.observers.global_observers.constants import LHOPT_CONSTANTS
from libinephany.pydantic_models.schemas.observation_models import ObservationInputs
from libinephany.pydantic_models.schemas.tensor_statistics import TensorStatistics
from libinephany.pydantic_models.states.hyperparameter_states import HyperparameterStates


class GlobalFirstOrderGradients(GlobalObserver):

    def _get_observation_format(self) -> StatisticStorageTypes:
        """
        :return: Format the observation returns data in. Must be one of the enum attributes in the StatisticStorageTypes
        enumeration class.
        """

        return StatisticStorageTypes.TENSOR_STATISTICS

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

        statistics = tracked_statistics[statistic_trackers.FirstOrderGradients.__name__]

        return observation_utils.average_tensor_statistics(tensor_statistics=list(statistics.values()))  # type: ignore

    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping statistic tracker class names to kwargs for the class or None if no kwargs are
        needed.
        """

        return {statistic_trackers.FirstOrderGradients.__name__: dict(skip_statistics=self.skip_statistics)}


class GlobalSecondOrderGradients(GlobalObserver):

    def __init__(
        self,
        *,
        compute_hessian_diagonal: bool = False,
        **kwargs,
    ) -> None:
        """
        :param compute_hessian_diagonal: Whether to compute the Hessian diagonal to determine second order gradients
        or use the squared first order gradients as approximations in the same way Adam does.
        :param kwargs: Miscellaneous keyword arguments.
        """

        super().__init__(**kwargs)

        self.compute_hessian_diagonal = compute_hessian_diagonal

    def _get_observation_format(self) -> StatisticStorageTypes:
        """
        :return: Format the observation returns data in. Must be one of the enum attributes in the StatisticStorageTypes
        enumeration class.
        """

        return StatisticStorageTypes.TENSOR_STATISTICS

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

        statistics = tracked_statistics[statistic_trackers.SecondOrderGradients.__name__]

        return observation_utils.average_tensor_statistics(tensor_statistics=list(statistics.values()))  # type: ignore

    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping statistic tracker class names to kwargs for the class or None if no kwargs are
        needed.
        """

        return {
            statistic_trackers.SecondOrderGradients.__name__: dict(
                skip_statistics=self.skip_statistics, compute_hessian_diagonal=self.compute_hessian_diagonal
            )
        }


class LHOPTGradientVarianceFraction(LHOPTBaseObserver):
    """
    This is a global observer from the OpenAI paper "Learning to Optimize with Reinforcement Learning"
    https://arxiv.org/abs/2305.18291.

    It returns two-dimensional observations: [raw_value, cdf_feature] for gradient variance fraction values.
    """

    def __init__(
        self,
        *,
        variance_threshold: float = LHOPT_CONSTANTS["DEFAULT_VARIANCE_THRESHOLD"],
        **kwargs,
    ) -> None:
        """
        :param variance_threshold: Threshold for variance comparison in gradient variance fraction calculation
        :param kwargs: Other observation keyword arguments.
        """
        super().__init__(**kwargs)
        self.variance_threshold = variance_threshold

    @property
    def can_standardize(self) -> bool:
        """
        This observer has its own CDF calculation, no need to standardize.
        :return: Whether the observation can be standardized.
        """
        return False

    def _get_observation_format(self) -> StatisticStorageTypes:
        """
        :return: Format the observation returns data in. Must be one of the enum attributes in the StatisticStorageTypes
        enumeration class.
        """
        return StatisticStorageTypes.VECTOR

    @property
    def vector_length(self) -> int:
        """
        :return: Length of the vector returned by this observation if it returns a vector.
        """
        return 2  # [raw_value, cdf_feature]

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
        if statistic_trackers.GradientVarianceFraction.__name__ not in tracked_statistics:
            return [0.0, 0.0]

        raw_value = list(tracked_statistics[statistic_trackers.GradientVarianceFraction.__name__].values())[0]  # type: ignore[list-item]

        cdf_feature = self._compute_cdf_feature(raw_value)  # type: ignore[arg-type]
        self._update_time()

        return [raw_value, cdf_feature]  # type: ignore[list-item]

    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping statistic tracker class names to kwargs for the class or None if no kwargs are
        needed.
        """

        return {
            statistic_trackers.GradientVarianceFraction.__name__: dict(variance_threshold=self.variance_threshold),
        }
