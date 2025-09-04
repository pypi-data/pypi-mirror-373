# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, TypeAlias, final

from libinephany.observations import observation_utils
from libinephany.observations.observation_utils import StatisticStorageTypes
from libinephany.pydantic_models.configs.observer_config import ObserverConfig
from libinephany.pydantic_models.schemas.observation_models import ObservationInputs
from libinephany.pydantic_models.schemas.tensor_statistics import TensorStatistics
from libinephany.pydantic_models.states.hyperparameter_states import HyperparameterStates
from libinephany.utils.exceptions import InvalidObservationSizeError
from libinephany.utils.standardizers import Standardizer

# ======================================================================================================================
#
# CONSTANTS
#
# ======================================================================================================================

CachedObservationData: TypeAlias = int | float | list[int | float] | TensorStatistics | dict[str, float | int]

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class Observer(ABC):

    TRAIN = "train"
    INFER = "infer"

    def __init__(
        self,
        *,
        standardizer: Standardizer | None,
        observer_config: ObserverConfig,
        should_standardize: bool = True,
        skip_statistics: list[str] | None = None,
        **kwargs,
    ) -> None:
        """
        :param standardizer: None or the standardizer to apply to the returned observations.
        :param global_config: ObserverConfig that can be used to inform various observation calculations.
        :param should_standardize: Whether standardization should be applied to returned values.
        :param skip_statistics: If the observation uses the TensorStatistic model to return observations, names of the
        fields in the model to not include in returned observations.
        :param kwargs: Miscellaneous keyword arguments.
        """

        self._mode = self.TRAIN
        self._validated_observation = False
        self._cached_observation: CachedObservationData | None = None

        self.observer_config = observer_config
        self.standardize = standardizer if standardizer is not None else observation_utils.null_standardizer
        self.should_standardize = should_standardize and self.can_standardize

        self.skip_statistics = TensorStatistics.filter_skip_statistics(skip_statistics=skip_statistics)

    @final
    @property
    def in_training_mode(self) -> bool:
        """
        :return: Whether the observer is in training mode.
        """

        return self._mode == self.TRAIN

    @final
    @property
    def observation_format(self) -> StatisticStorageTypes:
        """
        :return: Format the observation returns data in. Must be one of the enum attributes in the StatisticStorageTypes
        enumeration class.
        """

        observation_format = self._get_observation_format()

        if observation_format in StatisticStorageTypes:
            return observation_format

        raise ValueError(
            f"The type of observation format that observations should return must be in the "
            f"{StatisticStorageTypes.__name__} enumeration class. {observation_format} is not and so "
            f"{self.__class__.__name__} is invalid!"
        )

    @property
    def observation_size(self) -> int:
        """
        :return: Number of elements in the observation vector this observation takes up.
        """

        observation_format = self.observation_format

        if observation_format is StatisticStorageTypes.TENSOR_STATISTICS:
            return len([field for field in TensorStatistics.model_fields.keys() if field not in self.skip_statistics])

        elif observation_format is StatisticStorageTypes.FLOAT:
            return 1

        elif observation_format is StatisticStorageTypes.VECTOR:
            return self.vector_length

        else:
            raise ValueError(f"{observation_format} is not a recognised format that observations can return!")

    @property
    def vector_length(self) -> int:
        """
        :return: Length of the vector returned by this observation if it returns a vector.
        """

        raise NotImplementedError

    @property
    def can_standardize(self) -> bool:
        """
        :return: Whether the observation can be standardized.
        """

        return True

    @property
    def can_inform(self) -> bool:
        """
        :return: Whether observations from the observer can be used in the agent info dictionary.
        """

        return True

    @property
    @abstractmethod
    def standardizer_key_infix(self) -> str:
        """
        :return: String to infix into the standardizer statistic key to ensure uniqueness.
        """

        raise NotImplementedError

    @abstractmethod
    def _get_observation_format(self) -> StatisticStorageTypes:
        """
        :return: Format the observation returns data in. Must be one of the enum attributes in the StatisticStorageTypes
        enumeration class.
        """

        raise NotImplementedError

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
        names to floats or TensorStatistic models.
        :param action_taken: Action taken by the agent this class instance is assigned to.
        :return: Single float/int, list of floats/ints or TensorStatistics model to add to the observation vector.
        """

        raise NotImplementedError

    @final
    def _validate_observation(self, observations: list[float | int]) -> None:
        """
        :param observations: Observation vector to validate.
        """

        if len(observations) != self.observation_size:
            raise InvalidObservationSizeError(
                f"The observation vector returned by {self.__class__.__name__} has length {len(observations)} but the "
                f"expected length is {self.observation_size}!"
            )

        self._validated_observation = True

    @abstractmethod
    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping statistic tracker class names to kwargs for the class or None if no kwargs are
        needed.
        """

        raise NotImplementedError

    @final
    def observe(
        self,
        observation_inputs: ObservationInputs,
        hyperparameter_states: HyperparameterStates,
        tracked_statistics: dict[str, dict[str, float | TensorStatistics]],
        action_taken: float | int | None,
    ) -> list[float | int]:
        """
        :param observation_inputs: Observation input metrics not calculated with statistic trackers.
        :param hyperparameter_states: HyperparameterStates that manages the hyperparameters.
        :param tracked_statistics: Dictionary mapping statistic tracker class names to dictionaries mapping module
        names to floats or TensorStatistic models.
        :param action_taken: Action taken by the agent this class instance is assigned to.
        :return: List of floats or integers to add to the agent's observation vector.
        """

        observations = self._observe(
            observation_inputs=observation_inputs,
            hyperparameter_states=hyperparameter_states,
            tracked_statistics=tracked_statistics,
            action_taken=action_taken,
        )

        if self.can_inform and self._cached_observation is None:
            self._cached_observation = deepcopy(observations)

        if self.observation_format is StatisticStorageTypes.TENSOR_STATISTICS:
            observations = observations.to_list(skip_statistics=self.skip_statistics)  # type: ignore

        observations = [observations] if not isinstance(observations, list) else observations  # type: ignore

        if self.should_standardize:
            observations = [
                self.standardize(
                    statistics_key=f"{self.__class__.__name__}-{self.standardizer_key_infix}-{i}",
                    value_to_standardize=observation,
                )
                for i, observation in enumerate(observations)
            ]

        if not self._validated_observation:
            self._validate_observation(observations=observations)

        return observations

    @final
    def inform(self) -> float | int | dict[str, float] | None:
        """
        :return: The cached observation. If the observation format is TensorStatistics then it is converted to a
        dictionary with the statistics specified in skip_statistics excluded.
        """

        if not self.can_inform:
            return None

        if self._cached_observation is None:
            raise ValueError(
                f"{self.__class__.__name__} cannot inform when no observation has been cached! Ensure observe(...) has "
                f"been called before inform(...)!"
            )

        if self.observation_format is StatisticStorageTypes.TENSOR_STATISTICS:
            observation = self._cached_observation.model_dump(exclude=set(self.skip_statistics))  # type: ignore

        else:
            observation = self._cached_observation

        self._cached_observation = None

        return observation

    @final
    def train(self) -> None:
        """
        Sets the observer to train mode.
        """

        self._mode = self.TRAIN

    @final
    def infer(self) -> None:
        """
        Sets the observer to inference mode.
        """

        self._mode = self.INFER

    def reset(self) -> None:
        """
        Resets the observer.
        """

        pass


class LocalObserver(Observer, ABC):

    def __init__(
        self,
        *,
        agent_id: str,
        parameter_group_name: str | None,
        number_of_discrete_actions: int | None,
        action_scheme_index: int,
        number_of_action_schemes: int,
        **kwargs,
    ) -> None:
        """
        :param agent_id: ID of the agent this observation is assigned to.
        :param parameter_group_name: Name of the parameter group this agent is modulating.
        :param number_of_discrete_actions: The number of discrete actions that can be taken by this agent type's
        policy.
        :param action_scheme_index: Index of the action scheme in use in the list of possible action schemes.
        :param number_of_action_schemes: Number of action schemes available.
        :param kwargs: Miscellaneous keyword arguments.
        """

        super().__init__(**kwargs)

        self.agent_id = agent_id
        self.parameter_group_name = parameter_group_name

        self.number_of_discrete_actions = number_of_discrete_actions
        self.action_scheme_index = action_scheme_index
        self.number_of_action_schemes = number_of_action_schemes

    @property
    def standardizer_key_infix(self) -> str:
        """
        :return: String to infix into the standardizer statistic key to ensure uniqueness.
        """

        return self.agent_id

    @abstractmethod
    def _get_observation_format(self) -> StatisticStorageTypes:
        """
        :return: Format the observation returns data in. Must be one of the enum attributes in the StatisticStorageTypes
        enumeration class.
        """

        raise NotImplementedError

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
        names to floats or TensorStatistic models.
        :param action_taken: Action taken by the agent this class instance is assigned to.
        :return: Single float/int, list of floats/ints or TensorStatistics model to add to the observation vector.
        """

        raise NotImplementedError

    @abstractmethod
    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping statistic tracker class names to kwargs for the class or None if no kwargs are
        needed.
        """

        raise NotImplementedError


class GlobalObserver(Observer, ABC):

    @property
    def standardizer_key_infix(self) -> str:
        """
        :return: String to infix into the standardizer statistic key to ensure uniqueness.
        """

        return "Global"

    @abstractmethod
    def _get_observation_format(self) -> StatisticStorageTypes:
        """
        :return: Format the observation returns data in. Must be one of the enum attributes in the StatisticStorageTypes
        enumeration class.
        """

        raise NotImplementedError

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
        names to floats or TensorStatistic models.
        :param action_taken: Action taken by the agent this class instance is assigned to.
        :return: Single float/int, list of floats/ints or TensorStatistics model to add to the observation vector.
        """

        raise NotImplementedError

    @abstractmethod
    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping statistic tracker class names to kwargs for the class or None if no kwargs are
        needed.
        """

        raise NotImplementedError
