# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

from typing import Any

from pydantic import BaseModel

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class AgentObserverConfig(BaseModel):
    global_observers: dict[str, dict[str, Any] | None] | None
    local_observers: dict[str, dict[str, Any] | None] | None
    postprocessors: dict[str, dict[str, Any] | None] | None

    prepend_invalid_indicator: bool

    number_of_discrete_actions: int | None

    action_scheme_index: int
    number_of_action_schemes: int


class ObserverConfig(BaseModel):
    observation_clipping_threshold: float
    invalid_observation_threshold: float
    invalid_observation_replacement_value: float

    standardizer: str
    standardizer_arguments: dict[str, Any]

    agent_modules: dict[str, str]
    agents_to_modules_by_type: list[tuple[AgentObserverConfig, dict[str, str | None]]]

    optimizer_name: str | None
    nn_family_name: str | None
