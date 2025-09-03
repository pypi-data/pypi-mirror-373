# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

from abc import ABC, abstractmethod
from types import ModuleType
from typing import Any, final

from libinephany.observations.observers import global_observers, local_observers
from libinephany.observations.observers.base_observers import GlobalObserver, LocalObserver
from libinephany.pydantic_models.configs.observer_config import AgentObserverConfig, ObserverConfig
from libinephany.pydantic_models.schemas.observation_models import ObservationInputs
from libinephany.pydantic_models.schemas.tensor_statistics import TensorStatistics
from libinephany.pydantic_models.states.hyperparameter_states import HyperparameterStates
from libinephany.utils.standardizers import Standardizer
from libinephany.utils.typing import ObservationInformation

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class ObserverContainer(ABC):

    def __init__(
        self,
        global_config: ObserverConfig,
        agent_config: AgentObserverConfig,
        standardizer: Standardizer | None,
        **kwargs,
    ) -> None:
        """
        :param global_config: ObserverConfig that can be used to inform various observation calculations.
        :param agent_config: AgentObserverConfig storing configuration of the agent's actions and observation space for
        this type of agent.
        :param standardizer: None or the standardizer to apply to the returned observations.
        :param kwargs: Miscellaneous kwargs.
        """

        self.global_config = global_config
        self.agent_config = agent_config
        self.standardizer = standardizer

        self._observers: list[LocalObserver | GlobalObserver] = self._build_observers()

    @property
    @abstractmethod
    def observer_config(self) -> dict[str, dict[str, Any] | None] | None:
        """
        :return: Config of the various observers to construct.
        """

        raise NotImplementedError

    @property
    @abstractmethod
    def observer_module(self) -> ModuleType:
        """
        :return: Module in which the observer classes are stored.
        """

        raise NotImplementedError

    @property
    @abstractmethod
    def required_observer_kwargs(self) -> dict[str, Any]:
        """
        :return: Dictionary of kwargs required by the observers in the set observer module.
        """

        raise NotImplementedError

    @final
    @property
    def total_observer_size(self) -> int:
        """
        :return: Total size of the observation vector this container produces.
        """

        return sum(observer.observation_size for observer in self._observers)

    @final
    def _build_observers(
        self,
    ) -> list[LocalObserver | GlobalObserver]:
        """
        :return: List of instantiated observers.
        """

        if self.observer_config is None:
            return []

        observers = []

        for observer_name, additional_observer_kwargs in self.observer_config.items():
            try:
                observer_type: type[LocalObserver | GlobalObserver] = getattr(self.observer_module, observer_name)

            except AttributeError as e:
                raise AttributeError(f"The class {observer_name} does not exist within {self.observer_module}!") from e

            if additional_observer_kwargs is None:
                additional_observer_kwargs = {}

            observer_kwargs = self.required_observer_kwargs
            observer_kwargs.update(**additional_observer_kwargs)

            observer = observer_type(
                standardizer=self.standardizer,
                observer_config=self.global_config,
                **observer_kwargs,
            )

            observers.append(observer)

        return observers

    @final
    def get_required_trackers(self) -> list[dict[str, dict[str, Any] | None]]:
        """
        :return: List of trackers required by each of the stored observers.
        """

        return [observer.get_required_trackers() for observer in self._observers]

    @final
    def observe(
        self,
        observation_inputs: ObservationInputs,
        hyperparameter_states: HyperparameterStates,
        tracked_statistics: dict[str, dict[str, float | TensorStatistics]],
        action_taken: float | int | None,
        return_dict: bool = False,
    ) -> tuple[list[float | int], dict[str, list[float | int]] | None]:
        """
        :param observation_inputs: Observation input metrics not calculated with statistic trackers.
        :param hyperparameter_states: HyperparameterStates that manages the hyperparameters.
        :param tracked_statistics: Dictionary mapping statistic tracker class names to dictionaries mapping module
        names to floats or TensorStatistic models.
        :param action_taken: Action taken by the agent this class instance is assigned to.
        :param return_dict: Whether to return a dictionary of observations as well as the normal vector.
        :return: Tuple of a list of floats or integers to add to the agent's observation vector and a dictionary of
        observations as well as the normal vector.
        """

        observations = []
        observations_dict = {}

        for observer in self._observers:
            observer_obs = observer.observe(
                observation_inputs=observation_inputs,
                hyperparameter_states=hyperparameter_states,
                tracked_statistics=tracked_statistics,
                action_taken=action_taken,
            )

            if return_dict:
                observations_dict[observer.__class__.__name__] = observer_obs

            observations += observer_obs

        return observations, observations_dict if return_dict else None

    @final
    def inform(self) -> ObservationInformation:
        """
        :return: Dictionary mapping inform keys to observations to add to agent info.
        """

        informed = {}

        for observer in self._observers:
            observer_info = observer.inform()

            if observer_info is not None:
                informed[observer.__class__.__name__] = observer_info

        return informed

    @final
    def reset(self) -> None:
        """
        Resets all observers in the container.
        """

        for observer in self._observers:
            observer.reset()

    @final
    def train(self) -> None:
        """
        Sets all observers into training mode.
        """

        for observer in self._observers:
            observer.train()

    @final
    def infer(self) -> None:
        """
        Sets all observers into inference mode.
        """

        for observer in self._observers:
            observer.infer()


class LocalObserverContainer(ObserverContainer):

    def __init__(self, agent_id: str, parameter_group_name: str | None, **kwargs) -> None:
        """
        :param agent_id: ID of the agent this container serves.
        :param parameter_group_name: Name of the parameter group the agent that this container serves is controlling.
        :param kwargs: Kwargs for the base class.
        """

        self.agent_id = agent_id
        self.parameter_group_name = parameter_group_name

        super().__init__(**kwargs)

    @property
    def observer_config(self) -> dict[str, dict[str, Any] | None] | None:
        """
        :return: Config of the various observers to construct.
        """

        return self.agent_config.local_observers

    @property
    def observer_module(self) -> ModuleType:
        """
        :return: Module in which the observer classes are stored.
        """

        return local_observers

    @property
    def required_observer_kwargs(self) -> dict[str, Any]:
        """
        :return: Dictionary of kwargs required by the observers in the set observer module.
        """

        return dict(
            agent_id=self.agent_id,
            parameter_group_name=self.parameter_group_name,
            number_of_discrete_actions=self.agent_config.number_of_discrete_actions,
            action_scheme_index=self.agent_config.action_scheme_index,
            number_of_action_schemes=self.agent_config.number_of_action_schemes,
        )


class GlobalObserverContainer(ObserverContainer):

    @property
    def observer_config(self) -> dict[str, dict[str, Any] | None] | None:
        """
        :return: Config of the various observers to construct.
        """

        return self.agent_config.global_observers

    @property
    def observer_module(self) -> ModuleType:
        """
        :return: Module in which the observer classes are stored.
        """

        return global_observers

    @property
    def required_observer_kwargs(self) -> dict[str, Any]:
        """
        :return: Dictionary of kwargs required by the observers in the set observer module.
        """

        return {}
