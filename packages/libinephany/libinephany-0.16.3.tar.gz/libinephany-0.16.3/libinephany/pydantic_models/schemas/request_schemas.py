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


class BackendRequest(BaseModel):

    observation_array: list[list[float]] = []
    observations_with_history: list[list[float]] = []
    hidden_states: list[list[Any]] = []

    max_history_length: int


class AgentScheduleRequest(BaseModel):
    observations: list[float]
    agent_type: str | None

    hyperparameter_internal_value: float | int
    max_hyperparameter_internal_value: float | int
    min_hyperparameter_internal_value: float | int


class ClientScheduleRequest(BaseModel):
    run_slug: str
    inephany_model_id: str

    observations: dict[str, AgentScheduleRequest]


class ClientPolicySchemaRequest(BaseModel):
    inephany_model_id: str
    agent_types: list[str]
