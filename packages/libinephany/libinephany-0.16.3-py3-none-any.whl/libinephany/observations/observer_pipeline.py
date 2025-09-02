# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

import copy
from typing import Any

import gymnasium as gym
import numpy as np

from libinephany.observations.observers.observer_containers import GlobalObserverContainer, LocalObserverContainer
from libinephany.observations.post_processors import postprocessors
from libinephany.observations.post_processors.postprocessors import ObservationPostProcessor
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


class ObserverPipeline:

    def __init__(
        self,
        observer_config: ObserverConfig,
        agent_config: AgentObserverConfig,
        standardizer: Standardizer | None,
        agent_id_to_modules: dict[str, str | None],
    ):
        """
        :param observer_config: ObserverConfig that contains various parameters applicable to all agent observers as
        well as the observer configs for specific agents.
        :param agent_config: AgentObserverConfig storing configuration of the agent's actions and observation space for
        this type of agent.
        :param standardizer: None or the standardizer to apply to the returned observations.
        :param agent_id_to_modules: Dictionary mapping agent IDs to None or the name of the parameter group that agent
        is modulating.
        """

        self.observer_config = observer_config
        self.agent_config = agent_config
        self.standardizer = standardizer
        self.agent_id_to_modules = agent_id_to_modules

        self.global_observers = GlobalObserverContainer(
            global_config=observer_config,
            agent_config=agent_config,
            standardizer=standardizer,
        )

        self.local_observers: dict[str, LocalObserverContainer] = self._build_local_observers(
            agent_id_to_modules=agent_id_to_modules,
        )

        self.post_processors: list[ObservationPostProcessor] = self._build_post_processors()

        self.clipping_threshold = self.observer_config.observation_clipping_threshold
        self.invalid_threshold = self.observer_config.invalid_observation_threshold

    @property
    def observation_size(self) -> int:
        """
        :return: Total size of the observation vectors produced by this pipeline.
        """

        globals_size = self.global_observers.total_observer_size
        locals_size = list(self.local_observers.values())[0].total_observer_size

        total_size = globals_size + locals_size

        if self.agent_config.prepend_invalid_indicator:
            total_size += 1

        return total_size

    def _build_local_observers(
        self,
        agent_id_to_modules: dict[str, str | None],
    ) -> dict[str, LocalObserverContainer]:
        """
        :param agent_id_to_modules: Dictionary mapping agent IDs to None or the name of the parameter group that agent
        is modulating.
        :return: Dictionary mapping agent IDs to LocalObserverContainers for each agent.
        """

        observers = {}

        for agent_id, parameter_group_name in agent_id_to_modules.items():
            observers[agent_id] = LocalObserverContainer(
                global_config=self.observer_config,
                agent_config=self.agent_config,
                standardizer=self.standardizer,
                agent_id=agent_id,
                parameter_group_name=parameter_group_name,
            )

        return observers

    def _build_post_processors(self) -> list[ObservationPostProcessor]:
        """
        :return: List of post-processors to apply to the global and local observations.
        """

        if self.agent_config.postprocessors is None:
            return []

        post_processors = []

        for observer_name, post_processor_kwargs in self.agent_config.postprocessors.items():
            try:
                post_processor_type: type[ObservationPostProcessor] = getattr(postprocessors, observer_name)

            except AttributeError as e:
                raise AttributeError(f"The class {observer_name} does not exist within {postprocessors}!") from e

            if post_processor_kwargs is None:
                post_processor_kwargs = {}

            post_processor = post_processor_type(
                observer_config=self.observer_config,
                **post_processor_kwargs,
            )

            post_processors.append(post_processor)

        return post_processors

    @staticmethod
    def merge_globals_to_locals(
        global_obs: list[float | int],
        local_obs: dict[str, list[float | int]],
    ) -> dict[str, list[float | int]]:
        """
        :param global_obs: Global observations to post-process.
        :param local_obs: Dictionary mapping agent IDs to local observations of that agent.
        :return: Tuple of clipped global and local observations.
        :return: Dictionary mapping agent ID to that agent's completed observation vector.
        """

        return {agent_id: global_obs + agent_obs for agent_id, agent_obs in local_obs.items()}

    def get_required_trackers(self) -> list[dict[str, dict[str, Any] | None]]:
        """
        :return: List of trackers required by each of the stored observers.
        """

        required_trackers = self.global_observers.get_required_trackers()

        for agent_container in self.local_observers.values():
            required_trackers += agent_container.get_required_trackers()

        return required_trackers

    def clip_observation_vector(self, observation_vector: list[float | int]) -> tuple[bool, list[float | int]]:
        """
        :param observation_vector: Observations to clip.
        :return: Tuple indicating whether an observation was clipped and a list of the post-processed observations.
        """

        invalid_encountered = False
        post_processed = []

        for observation in observation_vector:
            if abs(observation) >= self.clipping_threshold:
                if abs(observation) >= self.invalid_threshold:
                    invalid_encountered = True

                observation = -self.clipping_threshold if observation < 0 else self.clipping_threshold

            elif np.isnan(observation):
                observation = self.observer_config.invalid_observation_replacement_value
                invalid_encountered = True

            post_processed.append(observation)

        return invalid_encountered, post_processed

    def clip_observations(
        self,
        globals_to_clip: list[float | int],
        locals_to_clip: dict[str, list[float | int]],
    ) -> tuple[list[float | int], dict[str, list[float | int]], bool]:
        """
        :param globals_to_clip: Global observations to post-process.
        :param locals_to_clip: Dictionary mapping agent IDs to local observations of that agent.
        :return: Tuple of clipped global and local observations and whether any observation clipping occurred.
        """

        invalid_encountered, globals_to_clip = self.clip_observation_vector(observation_vector=globals_to_clip)
        post_processed_locals = {}

        for agent_id, agent_observations in locals_to_clip.items():
            agent_invalid_encountered, post_processed = self.clip_observation_vector(
                observation_vector=agent_observations
            )

            post_processed_locals[agent_id] = post_processed
            invalid_encountered = invalid_encountered if invalid_encountered else agent_invalid_encountered

        if self.agent_config.prepend_invalid_indicator:
            globals_to_clip = [int(invalid_encountered)] + globals_to_clip

        return globals_to_clip, post_processed_locals, invalid_encountered

    def observe(
        self,
        observation_inputs: ObservationInputs,
        hyperparameter_states: HyperparameterStates,
        tracked_statistics: dict[str, dict[str, float | TensorStatistics]],
        actions_taken: dict[str, float | int | None],
        return_dict: bool = False,
    ) -> tuple[dict[str, list[float | int]], bool, dict[str, dict[str, list[float | int]]] | None]:
        """
        :param observation_inputs: Observation input metrics not calculated with statistic trackers.
        :param hyperparameter_states: HyperparameterStates that manages the hyperparameters.
        :param tracked_statistics: Dictionary mapping statistic tracker class names to dictionaries mapping module
        names to floats or TensorStatistic models.
        :param actions_taken: Dictionary mapping agent IDs to actions taken by that agent.
        :param return_dict: Whether to return a dictionary of observations as well as the normal vector.
        :return: Tuple of a dictionary mapping agent ID to that agent's completed observation vector, a boolean
        indicating whether an observation clip occurred and a dictionary of observations.
        """

        global_obs, global_obs_dict = self.global_observers.observe(
            observation_inputs=observation_inputs,
            hyperparameter_states=hyperparameter_states,
            tracked_statistics=tracked_statistics,
            action_taken=None,
            return_dict=return_dict,
        )

        local_obs: dict[str, list[float | int]] = {}
        obs_as_dict: dict[str, dict[str, list[float | int]]] = {}

        for agent_id, agent_observers in self.local_observers.items():
            local_obs[agent_id], local_obs_dict = agent_observers.observe(
                observation_inputs=observation_inputs,
                hyperparameter_states=hyperparameter_states,
                tracked_statistics=tracked_statistics,
                action_taken=actions_taken[agent_id] if agent_id in actions_taken else None,
                return_dict=return_dict,
            )

            if return_dict:
                obs_as_dict[agent_id] = copy.deepcopy(global_obs_dict)
                obs_as_dict[agent_id].update(local_obs_dict)

        for post_processor in self.post_processors:
            global_obs, local_obs = post_processor.postprocess(
                global_observations=global_obs, local_observations=local_obs
            )

        global_obs, local_obs, obs_clipped = self.clip_observations(
            globals_to_clip=global_obs, locals_to_clip=local_obs
        )
        merged_obs = self.merge_globals_to_locals(global_obs=global_obs, local_obs=local_obs)

        return merged_obs, obs_clipped, obs_as_dict if return_dict else None

    def inform(self) -> tuple[ObservationInformation, dict[str, ObservationInformation]]:
        """
        :return: Dictionary of observation info to add to the agent info.
        """

        global_information = self.global_observers.inform()

        agent_information = {agent_id: observer.inform() for agent_id, observer in self.local_observers.items()}

        return global_information, agent_information

    def get_observation_spaces(self) -> dict[str, gym.spaces.Box]:
        """
        :return: Dictionary mapping agent IDs to their observation spaces.
        """

        return {
            agent_id: gym.spaces.Box(low=-np.inf, high=np.inf, shape=(self.observation_size,), dtype=np.float32)
            for agent_id in self.local_observers
        }

    def reset(self) -> None:
        """
        Resets all global and local observers.
        """

        self.global_observers.reset()

        for local_observers in self.local_observers.values():
            local_observers.reset()

    def train(self) -> None:
        """
        Sets all observer containers into training mode.
        """

        self.global_observers.train()

        for local_observers in self.local_observers.values():
            local_observers.train()

    def infer(self) -> None:
        """
        Sets all observer containers into inference mode.
        """

        self.global_observers.infer()

        for local_observers in self.local_observers.values():
            local_observers.infer()
