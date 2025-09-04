# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

from typing import Any

import gymnasium as gym

from libinephany.observations.observer_pipeline import ObserverPipeline
from libinephany.pydantic_models.configs.observer_config import ObserverConfig
from libinephany.pydantic_models.schemas.agent_info import AgentInfo
from libinephany.pydantic_models.schemas.observation_models import ObservationInputs, Observations
from libinephany.pydantic_models.schemas.tensor_statistics import TensorStatistics
from libinephany.pydantic_models.states.hyperparameter_states import HyperparameterStates
from libinephany.utils import standardizers

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class ObserverPipelineCoordinator:

    def __init__(
        self,
        observer_config: ObserverConfig,
    ):
        """
        :param observer_config: ObserverConfig that contains various parameters applicable to all agent observers as
        well as the observer configs for specific agents.
        """

        self.observer_config = observer_config
        self.standardizer = standardizers.get_standardizer(
            standardizer_name=self.observer_config.standardizer,
            standardizer_arguments=self.observer_config.standardizer_arguments,
        )

        self.pipelines: list[ObserverPipeline] = self._build_pipelines()

    @staticmethod
    def _merge_pipeline_requirements(
        pipeline: ObserverPipeline, required_trackers: dict[str, dict[str, Any] | None]
    ) -> dict[str, dict[str, Any] | None]:
        """
        :param pipeline: ObserverPipeline to compile the tracker requirements of its observers.
        :param required_trackers: Running dictionary of merged requirements.
        :return: Merged tracker requirements.
        """

        pipeline_requirements = pipeline.get_required_trackers()

        for observer_requirement in pipeline_requirements:
            for tracker_name, tracker_kwargs in observer_requirement.items():
                if tracker_name in required_trackers and tracker_kwargs != required_trackers[tracker_name]:
                    raise ValueError(
                        f"Conflict for tracker '{tracker_name}': "
                        f"Existing value: {required_trackers[tracker_name]}, "
                        f"New value: {tracker_kwargs}"
                    )

                else:
                    required_trackers[tracker_name] = tracker_kwargs

        return required_trackers

    def _build_pipelines(self) -> list[ObserverPipeline]:
        """
        :return: List of pipelines for each agent type.
        """

        return [
            ObserverPipeline(
                observer_config=self.observer_config,
                agent_config=agent_config,
                standardizer=self.standardizer,
                agent_id_to_modules=agent_id_to_modules,
            )
            for (agent_config, agent_id_to_modules) in self.observer_config.agents_to_modules_by_type
        ]

    def get_required_trackers(self) -> dict[str, dict[str, Any] | None]:
        """
        :return: Dictionary mapping tracker names to None or the kwargs for that tracker.
        """

        required_trackers: dict[str, dict[str, Any] | None] = {}

        for pipeline in self.pipelines:
            required_trackers = self._merge_pipeline_requirements(
                pipeline=pipeline, required_trackers=required_trackers
            )

        return required_trackers

    def get_observation_space(self) -> gym.spaces.Dict:
        """
        :return: Gymnasium dictionary space mapping Agent IDs to observation spaces.
        """

        spaces: dict[str, gym.spaces.Space] = {}

        for pipeline in self.pipelines:
            observations_spaces = pipeline.get_observation_spaces()

            spaces.update(**observations_spaces)

        if not spaces:
            raise ValueError("No observation spaces have been created!")

        return gym.spaces.Dict(spaces)

    def observe(
        self,
        observation_inputs: ObservationInputs,
        hyperparameter_states: HyperparameterStates,
        tracked_statistics: dict[str, dict[str, float | TensorStatistics]],
        actions_taken: dict[str, float | int | None],
        return_dict: bool = False,
    ) -> Observations:
        """
        :param observation_inputs: Observation input metrics not calculated with statistic trackers.
        :param hyperparameter_states: HyperparameterStates that manages the hyperparameters.
        :param tracked_statistics: Dictionary mapping statistic tracker class names to dictionaries mapping module
        names to floats or TensorStatistic models.
        :param actions_taken: Dictionary mapping agent IDs to actions taken by that agent.
        :param return_dict: Whether to return a dictionary of observations as well as the normal vector.
        :return: Observations pydantic model.
        """

        clipped_observations = False
        observations = {}
        observations_as_dict: dict[str, dict[str, list[float | int]]] = {}

        for pipeline in self.pipelines:
            pipeline_observations, pipeline_clipped_observations, pipeline_observations_dict = pipeline.observe(
                observation_inputs=observation_inputs,
                hyperparameter_states=hyperparameter_states,
                tracked_statistics=tracked_statistics,
                actions_taken=actions_taken,
                return_dict=return_dict,
            )

            clipped_observations = clipped_observations if clipped_observations else pipeline_clipped_observations

            for agent_id, agent_obs in pipeline_observations.items():
                if agent_id in observations:
                    raise KeyError(
                        f"Attempted to add observations for agent {agent_id} to observations dictionary but they are "
                        f"already present! This should not happen under any circumstances."
                    )

                observations[agent_id] = agent_obs

                if return_dict:
                    observations_as_dict[agent_id] = pipeline_observations_dict[agent_id]

        return Observations(
            observation_inputs=observation_inputs,
            agent_observations=observations,
            hit_invalid_value=clipped_observations,
            observations_as_dict=observations_as_dict if return_dict else None,
        )

    def inform(self) -> AgentInfo:
        """
        :return: AgentInfo model storing information about various global and local observations.
        """

        information = AgentInfo()

        for pipeline in self.pipelines:
            pipeline_global_information, pipeline_agent_information = pipeline.inform()

            information.update_global_information(new_information=pipeline_global_information)
            information.add_agent_information(agent_information=pipeline_agent_information)

        return information

    def reset(self) -> None:
        """
        Resets all observer pipelines.
        """

        for pipeline in self.pipelines:
            pipeline.reset()

    def train(self) -> None:
        """
        Sets all observer pipelines into training mode.
        """

        for pipeline in self.pipelines:
            pipeline.train()

    def infer(self) -> None:
        """
        Sets all observer pipelines into inference mode.
        """

        for pipeline in self.pipelines:
            pipeline.infer()
