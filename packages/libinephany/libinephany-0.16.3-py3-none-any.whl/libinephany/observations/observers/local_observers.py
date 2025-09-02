# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

from typing import Any

from libinephany.observations import observation_utils, statistic_trackers
from libinephany.observations.observation_utils import StatisticStorageTypes
from libinephany.observations.observers.base_observers import LocalObserver
from libinephany.pydantic_models.schemas.observation_models import ObservationInputs
from libinephany.pydantic_models.schemas.tensor_statistics import TensorStatistics
from libinephany.pydantic_models.states.hyperparameter_states import HyperparameterStates
from libinephany.utils import exceptions
from libinephany.utils.enums import ModuleTypes
from libinephany.utils.transforms import HyperparameterTransformType

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class FirstOrderGradients(LocalObserver):

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

        assert self.parameter_group_name is not None

        statistics = tracked_statistics[statistic_trackers.FirstOrderGradients.__name__]

        if self.parameter_group_name not in statistics:
            return TensorStatistics()

        agent_stats = statistics[self.parameter_group_name]

        return agent_stats

    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping statistic tracker class names to kwargs for the class or None if no kwargs are
        needed.
        """

        return {statistic_trackers.FirstOrderGradients.__name__: dict(skip_statistics=self.skip_statistics)}


class SecondOrderGradients(LocalObserver):

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

        assert self.parameter_group_name is not None

        statistics = tracked_statistics[statistic_trackers.SecondOrderGradients.__name__]

        if self.parameter_group_name not in statistics:
            return TensorStatistics()

        agent_stats = statistics[self.parameter_group_name]

        return agent_stats

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


class Activations(LocalObserver):

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

        assert self.parameter_group_name is not None

        statistics = tracked_statistics[statistic_trackers.ActivationStatistics.__name__]

        if self.parameter_group_name not in statistics:
            return TensorStatistics()

        agent_stats = statistics[self.parameter_group_name]

        return agent_stats

    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping statistic tracker class names to kwargs for the class or None if no kwargs are
        needed.
        """

        return {statistic_trackers.ActivationStatistics.__name__: dict(skip_statistics=self.skip_statistics)}


class ParameterUpdates(LocalObserver):

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

        assert self.parameter_group_name is not None

        statistics = tracked_statistics[statistic_trackers.ParameterUpdateStatistics.__name__]

        if self.parameter_group_name not in statistics:
            return TensorStatistics()

        agent_stats = statistics[self.parameter_group_name]

        return agent_stats

    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping statistic tracker class names to kwargs for the class or None if no kwargs are
        needed.
        """

        return {statistic_trackers.ParameterUpdateStatistics.__name__: dict(skip_statistics=self.skip_statistics)}


class Parameters(LocalObserver):

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

        assert self.parameter_group_name is not None

        statistics = tracked_statistics[statistic_trackers.ParameterStatistics.__name__]

        if self.parameter_group_name not in statistics:
            return TensorStatistics()

        agent_stats = statistics[self.parameter_group_name]

        return agent_stats

    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping statistic tracker class names to kwargs for the class or None if no kwargs are
        needed.
        """

        return {statistic_trackers.ParameterStatistics.__name__: dict(skip_statistics=self.skip_statistics)}


class LAMBTrustRatio(LocalObserver):

    def __init__(
        self,
        *,
        use_log_transform: bool = False,
        **kwargs,
    ) -> None:
        """
        :param use_log_transform: Whether to transform the LAMB trust ratio by taking ln(1 + R).
        :param kwargs: Other observation keyword arguments.
        """

        super().__init__(**kwargs)

        self.use_log_transform = use_log_transform

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

        assert self.parameter_group_name is not None

        statistics = tracked_statistics[statistic_trackers.LAMBTrustRatioStatistics.__name__]

        if self.parameter_group_name not in statistics:
            return 0.0

        agent_stats = statistics[self.parameter_group_name]

        return agent_stats

    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping statistic tracker class names to kwargs for the class or None if no kwargs are
        needed.
        """

        return {statistic_trackers.LAMBTrustRatioStatistics.__name__: dict(use_log_transform=self.use_log_transform)}


class ActionOneHot(LocalObserver):

    DISCRETE_INDEX = 0

    @property
    def is_discrete(self) -> bool:
        """
        :return: Whether the agent is using discrete actions.
        """

        valid_actions = self.number_of_discrete_actions is not None and self.number_of_discrete_actions > 0
        return self.action_scheme_index == self.DISCRETE_INDEX and valid_actions

    @property
    def vector_length(self) -> int:
        """
        :return: Length of the vector returned by this observation if it returns a vector.
        """

        if self.is_discrete:
            return self.number_of_discrete_actions

        return 0

    @property
    def can_inform(self) -> bool:
        """
        :return: Whether observations from the observer can be used in the agent info dictionary.
        """

        return False

    def _get_observation_format(self) -> StatisticStorageTypes:
        """
        :return: Format the observation returns data in. Must be one of the enum attributes in the StatisticStorageTypes
        enumeration class.
        """

        return StatisticStorageTypes.VECTOR

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

        if not self.is_discrete:
            return []

        return observation_utils.create_one_hot_observation(
            vector_length=self.vector_length, one_hot_index=action_taken if action_taken is None else int(action_taken)
        )

    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping statistic tracker class names to kwargs for the class or None if no kwargs are
        needed.
        """

        return {}


class ActionSchemeOneHot(LocalObserver):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        exceptions.warn_once(
            f"{str(self.__class__.__name__)} is deprecated and will be removed in an upcoming release."
        )

    @property
    def vector_length(self) -> int:
        """
        :return: Length of the vector returned by this observation if it returns a vector.
        """

        return self.number_of_action_schemes

    @property
    def can_inform(self) -> bool:
        """
        :return: Whether observations from the observer can be used in the agent info dictionary.
        """

        return False

    def _get_observation_format(self) -> StatisticStorageTypes:
        """
        :return: Format the observation returns data in. Must be one of the enum attributes in the StatisticStorageTypes
        enumeration class.
        """

        return StatisticStorageTypes.VECTOR

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
        assert self.parameter_group_name is not None

        return observation_utils.create_one_hot_observation(
            vector_length=self.vector_length, one_hot_index=self.action_scheme_index
        )

    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping statistic tracker class names to kwargs for the class or None if no kwargs are
        needed.
        """

        return {}


class DepthOneHot(LocalObserver):

    @property
    def vector_length(self) -> int:
        """
        :return: Length of the vector returned by this observation if it returns a vector.
        """

        return 3

    @property
    def can_inform(self) -> bool:
        """
        :return: Whether observations from the observer can be used in the agent info dictionary.
        """

        return False

    def _get_observation_format(self) -> StatisticStorageTypes:
        """
        :return: Format the observation returns data in. Must be one of the enum attributes in the StatisticStorageTypes
        enumeration class.
        """

        return StatisticStorageTypes.VECTOR

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

        assert self.parameter_group_name is not None

        return observation_utils.create_one_hot_depth_encoding(
            agent_controlled_modules=list(self.observer_config.agent_modules.keys()),
            parameter_group_name=self.parameter_group_name,
        )

    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping statistic tracker class names to kwargs for the class or None if no kwargs are
        needed.
        """

        return {}


class ModuleTypeOneHot(LocalObserver):

    MODULE_TYPE_TO_IDX = {
        "convolutional": 0,
        "attention": 1,
        "linear": 2,
        "embedding": 3,
    }

    @property
    def vector_length(self) -> int:
        """
        :return: Length of the vector returned by this observation if it returns a vector.
        """

        return len(ModuleTypes)

    @property
    def can_inform(self) -> bool:
        """
        :return: Whether observations from the observer can be used in the agent info dictionary.
        """

        return False

    def _get_observation_format(self) -> StatisticStorageTypes:
        """
        :return: Format the observation returns data in. Must be one of the enum attributes in the StatisticStorageTypes
        enumeration class.
        """

        return StatisticStorageTypes.VECTOR

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

        assert self.parameter_group_name is not None

        agent_modules = self.observer_config.agent_modules
        module_type = agent_modules[self.parameter_group_name]

        if module_type in {field.value for field in ModuleTypes}:
            one_hot_index = ModuleTypes.get_index(module_type)

        else:
            one_hot_index = None

        return observation_utils.create_one_hot_observation(
            vector_length=self.vector_length, one_hot_index=one_hot_index
        )

    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping statistic tracker class names to kwargs for the class or None if no kwargs are
        needed.
        """

        return {}


class CurrentHyperparameters(LocalObserver):

    def __init__(self, skip_hparams: list[str] | None = None, **kwargs) -> None:
        """
        :param skip_hparams: Names of the hyperparameters to not include in the initial values vector returned by
        this observation.
        :param kwargs: Miscellaneous keyword arguments.
        """

        super().__init__(**kwargs)

        self.skip_hparams = skip_hparams if skip_hparams is not None else []

    @property
    def can_standardize(self) -> bool:
        """
        :return: Whether the observation can be standardized.
        """

        return False

    @property
    def can_inform(self) -> bool:
        """
        :return: Whether observations from the observer can be used in the agent info dictionary.
        """

        return False

    @property
    def vector_length(self) -> int:
        """
        :return: Length of the vector returned by this observation if it returns a vector.
        """

        available_hparams = HyperparameterStates.get_layerwise_hyperparameters()

        return len(
            [hparam for hparam in available_hparams if not any(skipped in hparam for skipped in self.skip_hparams)]
        )

    def _get_observation_format(self) -> StatisticStorageTypes:
        """
        :return: Format the observation returns data in. Must be one of the enum attributes in the StatisticStorageTypes
        enumeration class.
        """

        return StatisticStorageTypes.VECTOR

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

        assert self.parameter_group_name is not None

        current_internal_values = hyperparameter_states[self.parameter_group_name].get_current_internal_values(
            skip_hparams=self.skip_hparams
        )

        self._cached_observation = current_internal_values

        return list(current_internal_values.values())

    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping statistic tracker class names to kwargs for the class or None if no kwargs are
        needed.
        """

        return {}


class CurrentHyperparameterDeltas(LocalObserver):

    def __init__(self, skip_hparams: list[str] | None = None, **kwargs) -> None:
        """
        :param skip_hparams: Names of the hyperparameters to not include in the initial deltas vector returned by
        this observation.
        :param kwargs: Miscellaneous keyword arguments.
        """

        super().__init__(**kwargs)

        self.skip_hparams = skip_hparams if skip_hparams is not None else []

    @property
    def can_standardize(self) -> bool:
        """
        :return: Whether the observation can be standardized.
        """

        return False

    @property
    def can_inform(self) -> bool:
        """
        :return: Whether observations from the observer can be used in the agent info dictionary.
        """

        return False

    @property
    def vector_length(self) -> int:
        """
        :return: Length of the vector returned by this observation if it returns a vector.
        """

        available_hparams = HyperparameterStates.get_layerwise_hyperparameters()

        return len(
            [hparam for hparam in available_hparams if not any(skipped in hparam for skipped in self.skip_hparams)]
        )

    def _get_observation_format(self) -> StatisticStorageTypes:
        """
        :return: Format the observation returns data in. Must be one of the enum attributes in the StatisticStorageTypes
        enumeration class.
        """

        return StatisticStorageTypes.VECTOR

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

        assert self.parameter_group_name is not None

        current_deltas = hyperparameter_states[self.parameter_group_name].get_current_deltas(
            skip_hparams=self.skip_hparams
        )

        self._cached_observation = current_deltas

        return list(current_deltas.values())

    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping statistic tracker class names to kwargs for the class or None if no kwargs are
        needed.
        """

        return {}


class HyperparameterTransformTypes(LocalObserver):

    TRANSFORM_TYPE_TO_IDX = dict(((s, i) for i, s in enumerate(HyperparameterTransformType)))

    def __init__(self, skip_hparams: list[str] | None = None, **kwargs) -> None:
        """
        :param skip_hparams: Names of the hyperparameters to not include in the transforms vector returned by
        this observation.
        :param kwargs: Miscellaneous keyword arguments.
        """

        super().__init__(**kwargs)

        self.skip_hparams = skip_hparams if skip_hparams is not None else []

    @property
    def can_standardize(self) -> bool:
        """
        :return: Whether the observation can be standardized.
        """

        return False

    @property
    def can_inform(self) -> bool:
        """
        :return: Whether observations from the observer can be used in the agent info dictionary.
        """

        return False

    @property
    def vector_length(self) -> int:
        """
        :return: Length of the vector returned by this observation if it returns a vector.
        """

        available_hparams = HyperparameterStates.get_layerwise_hyperparameters()

        return len(HyperparameterTransformType) * len(
            [hparam for hparam in available_hparams if not any(skipped in hparam for skipped in self.skip_hparams)]
        )

    def _get_observation_format(self) -> StatisticStorageTypes:
        """
        :return: Format the observation returns data in. Must be one of the enum attributes in the StatisticStorageTypes
        enumeration class.
        """

        return StatisticStorageTypes.VECTOR

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

        assert self.parameter_group_name is not None

        parameter_group_hparams = hyperparameter_states[self.parameter_group_name]
        hyperparameter_transform_types = parameter_group_hparams.get_hyperparameter_transform_types(
            skip_hparams=self.skip_hparams
        )
        hyperparameter_transform_types_onehot_list = [
            observation_utils.create_one_hot_observation(
                vector_length=len(HyperparameterTransformType), one_hot_index=self.TRANSFORM_TYPE_TO_IDX[transform_type]
            )
            for transform_type in hyperparameter_transform_types.values()
        ]
        hyperparameter_transform_types_onehot_concat = observation_utils.concatenate_lists(
            hyperparameter_transform_types_onehot_list
        )

        return hyperparameter_transform_types_onehot_concat

    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping statistic tracker class names to kwargs for the class or None if no kwargs are
        needed.
        """

        return {}


class SinusoidalDepth(LocalObserver):

    def __init__(self, dimensionality: int = 16, **kwargs) -> None:
        """
        :param dimensionality:
        :param kwargs: Miscellaneous keyword arguments.
        """

        super().__init__(**kwargs)

        assert dimensionality % 2 == 0, "Dimensionality of a sinusoidal depth encoding must be even."

        self.dimensionality = dimensionality

    @property
    def vector_length(self) -> int:
        """
        :return: Length of the vector returned by this observation if it returns a vector.
        """

        return self.dimensionality

    @property
    def can_inform(self) -> bool:
        """
        :return: Whether observations from the observer can be used in the agent info dictionary.
        """

        return False

    def _get_observation_format(self) -> StatisticStorageTypes:
        """
        :return: Format the observation returns data in. Must be one of the enum attributes in the StatisticStorageTypes
        enumeration class.
        """

        return StatisticStorageTypes.VECTOR

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

        assert self.parameter_group_name is not None

        return observation_utils.create_sinusoidal_depth_encoding(
            agent_controlled_modules=list(self.observer_config.agent_modules.keys()),
            parameter_group_name=self.parameter_group_name,
            dimensionality=self.dimensionality,
        )

    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping statistic tracker class names to kwargs for the class or None if no kwargs are
        needed.
        """

        return {}


class PercentageDepth(LocalObserver):

    @property
    def can_inform(self) -> bool:
        """
        :return: Whether observations from the observer can be used in the agent info dictionary.
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

        assert self.parameter_group_name is not None

        modules = list(self.observer_config.agent_modules.keys())
        depth = modules.index(self.parameter_group_name)

        return depth / len(modules)

    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping statistic tracker class names to kwargs for the class or None if no kwargs are
        needed.
        """

        return {}
