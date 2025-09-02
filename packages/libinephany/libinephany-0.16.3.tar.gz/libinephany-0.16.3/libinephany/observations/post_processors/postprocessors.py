# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

from abc import ABC, abstractmethod
from copy import deepcopy
from difflib import SequenceMatcher

from libinephany.pydantic_models.configs.observer_config import ObserverConfig

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class ObservationPostProcessor(ABC):

    def __init__(
        self,
        observer_config: ObserverConfig,
        **kwargs,
    ) -> None:
        """
        :param observer_config: ObserverConfig that can be used to inform various observation calculations.
        """

        self.observer_config = observer_config

    @abstractmethod
    def postprocess(
        self,
        global_observations: list[float | int],
        local_observations: dict[str, list[float | int]],
    ) -> tuple[list[float | int], dict[str, list[float | int]]]:
        """
        :param global_observations: Global observations to post-process.
        :param local_observations: Dictionary mapping agent IDs to local observations of that agent.
        :return: Tuple of post-processed global and local observations.
        """

        raise NotImplementedError


class AppendAdjacentLocalObservations(ObservationPostProcessor):

    def __init__(
        self,
        append_left_adjacent: bool,
        append_right_adjacent: bool,
        **kwargs,
    ) -> None:
        """
        :param append_left_adjacent: Whether to append the local observations of the agent in the i-1th position to each
        agent.
        :param append_right_adjacent: Whether to append the local observations of the agent in the i+1th position to
        each agent.
        """

        super().__init__(**kwargs)

        self.append_left_adjacent = append_left_adjacent
        self.append_right_adjacent = append_right_adjacent

        if not append_left_adjacent and not append_right_adjacent:
            raise ValueError(
                f"{self.__class__.__name__} required at least one of 'append_left_adjacent' or 'append_right_adjacent' "
                f"to be True."
            )

    @staticmethod
    def append_adjacent_local_observations(
        local_observations: dict[str, list[float | int]],
        agent_id: str,
        module_index: int,
        invalid_index: int,
        append_to: list[float | int],
        agent_modules: list[str],
        adjacent_module_index: int,
    ) -> list[float | int]:
        """
        :param local_observations: Local observations to get adjacent agent local observations from.
        :param agent_id: ID of the agent having local observations appended to it.
        :param module_index: Index of the agent's module in agent_modules.
        :param invalid_index: Index which is invalid for the agent to have observations appended to it.
        :param append_to: Local observations to append the adjacent observations to.
        :param agent_modules: List of agent controlled inner model modules.
        :param adjacent_module_index: Index in agent_modules of the adjacent module.
        :return: Updated append_to.
        """

        if module_index == invalid_index:
            append_to += [0] * len(local_observations[agent_id])

        else:
            adjacent_module = agent_modules[adjacent_module_index]

            adj_agent_id = max(
                local_observations.keys(), key=lambda adjacent: SequenceMatcher(None, adjacent_module, adjacent).ratio()
            )

            append_to += local_observations[adj_agent_id]

        return append_to

    def postprocess(
        self,
        global_observations: list[float | int],
        local_observations: dict[str, list[float | int]],
    ) -> tuple[list[float | int], dict[str, list[float | int]]]:
        """
        :param global_observations: Global observations to post-process.
        :param local_observations: Dictionary mapping agent IDs to local observations of that agent.
        :return: Tuple of post-processed global and local observations.
        """

        agent_modules = list(self.observer_config.agent_modules.keys())
        post_processed = {}

        for agent_id, agent_locals in local_observations.items():
            post_processed_locals = deepcopy(agent_locals)

            agent_module_name = max(agent_modules, key=lambda layer: SequenceMatcher(None, agent_id, layer).ratio())
            module_index = agent_modules.index(agent_module_name)

            if self.append_left_adjacent:
                post_processed_locals = self.append_adjacent_local_observations(
                    local_observations=local_observations,
                    agent_id=agent_id,
                    module_index=module_index,
                    invalid_index=0,
                    append_to=post_processed_locals,
                    agent_modules=agent_modules,
                    adjacent_module_index=module_index - 1,
                )

            if self.append_right_adjacent:
                post_processed_locals = self.append_adjacent_local_observations(
                    local_observations=local_observations,
                    agent_id=agent_id,
                    module_index=module_index,
                    invalid_index=len(agent_modules) - 1,
                    append_to=post_processed_locals,
                    agent_modules=agent_modules,
                    adjacent_module_index=module_index + 1,
                )

            post_processed[agent_id] = post_processed_locals

        return global_observations, post_processed
