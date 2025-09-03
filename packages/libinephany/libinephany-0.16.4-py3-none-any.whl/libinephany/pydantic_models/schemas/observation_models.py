# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

from typing import Any

import numpy as np
from numpy.typing import DTypeLike
from pydantic import BaseModel, model_validator

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class ObservationInputs(BaseModel):
    training_loss: float
    validation_loss: float

    training_score: float
    validation_score: float

    training_progress: float
    epochs_completed: int

    @model_validator(mode="before")
    def none_to_zero(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        :param data: Data to validate and turn all fields given None as their value who have float or int annotations
        to 0.0.
        :return: Validated model data.
        """

        for field, value in data.items():
            field_type = cls.model_fields[field].annotation

            if value is None and (field_type is int or field_type is float):
                data[field] = 0.0 if field_type is float else 0

        return data


class Observations(BaseModel):

    observation_inputs: ObservationInputs

    hit_invalid_value: bool

    agent_observations: dict[str, list[float | int]]
    observations_as_dict: dict[str, dict[str, list[float | int]]] | None = None

    def observations_as_arrays(self, dtype: DTypeLike = np.float32) -> dict[str, np.ndarray]:
        """
        :param dtype: Data type to cast the observations to.
        :return: Dictionary mapping agent IDs to their observation vectors as numpy arrays.
        """

        return {
            agent_id: np.array(observation_vector, dtype=dtype)
            for agent_id, observation_vector in self.agent_observations.items()
        }
