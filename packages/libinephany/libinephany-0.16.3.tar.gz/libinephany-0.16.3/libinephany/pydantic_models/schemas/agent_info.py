# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

import numpy as np
from pydantic import BaseModel, ConfigDict

from libinephany.utils.typing import ObservationInformation

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class AgentInfo(BaseModel):

    model_config = ConfigDict(extra="allow")

    global_information: ObservationInformation = {}
    agent_information: dict[str, ObservationInformation] = {}

    def _add_agent_information(self, agent_id: str, agent_information: ObservationInformation) -> None:
        """
        :param agent_id: ID of the agent that the given information is from.
        :param agent_information: Information from a particular agent to store.
        """

        if agent_id in self.agent_information:
            raise ValueError(f"Agent {agent_id} already exists within AgentInfo model!")

        self.agent_information[agent_id] = agent_information

    def add_agent_information(self, agent_information: dict[str, ObservationInformation]) -> None:
        """
        :param agent_information: Information from a particular agent to store.
        """

        for agent_id, single_agent_info in agent_information.items():
            self._add_agent_information(agent_id=agent_id, agent_information=single_agent_info)

    def update_global_information(self, new_information: ObservationInformation) -> None:
        """
        :param new_information: Additional global information to store.
        """

        for key, value in new_information.items():
            is_nan = False

            if not isinstance(value, dict):
                is_nan = np.isnan(value)

            if key in self.global_information and not isinstance(self.global_information[key], dict):
                is_nan = is_nan or np.isnan(self.global_information[key])  # type: ignore

            if key in self.global_information and not is_nan and value != self.global_information[key]:
                raise ValueError(
                    f"Value mismatch in global observations! Key {key} came with value {value} which conflicts with "
                    f"pre-existing value {self.global_information[key]}."
                )

            self.global_information[key] = value
