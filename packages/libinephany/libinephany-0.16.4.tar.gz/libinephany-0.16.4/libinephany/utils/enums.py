# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

from enum import Enum

from libinephany.utils.constants import (
    ADAM_BETA_ONE,
    ADAM_BETA_TWO,
    ADAM_EPS,
    BATCH_SIZE,
    DROPOUT,
    EPOCHS,
    GRAD_NORM_CLIP,
    GRADIENT_ACCUMULATION,
    LEARNING_RATE,
    SAMPLES,
    SGD_MOMENTUM,
    TOKENS,
    WEIGHT_DECAY,
)

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class EnumWithIndices(Enum):

    @classmethod
    def get_index(cls, enum_name: str) -> int:
        """
        :param enum_name: Name of the enum to get the position index for.
        :return: Index position of the given enum in the list of possible schemas.
        :raises ValueError: When given enum does not match any types stored in the enum class.
        """

        as_list = list(cls)  # type: ignore

        for i, action in enumerate(as_list):
            if action.value == enum_name:
                return i

        raise ValueError(f"Unknown enum name {enum_name}.")

    @classmethod
    def get_from_index(cls, index: int) -> "EnumWithIndices":
        """
        :param index: Index of the enum to get.
        :return: Enum corresponding to the given index.
        """

        as_list = list(cls)

        return as_list[index]


class AgentTypes(EnumWithIndices):

    # Active Agents
    LearningRateAgent = LEARNING_RATE
    WeightDecayAgent = WEIGHT_DECAY
    DropoutAgent = DROPOUT
    GradientClippingAgent = GRAD_NORM_CLIP
    AdamBetaOneAgent = ADAM_BETA_ONE
    AdamBetaTwoAgent = ADAM_BETA_TWO
    AdamEpsAgent = ADAM_EPS
    SGDMomentumAgent = SGD_MOMENTUM
    GradientAccumulationAgent = GRADIENT_ACCUMULATION

    # Deprecated or Non-Agent
    BatchSize = BATCH_SIZE
    Epochs = EPOCHS
    Tokens = TOKENS
    Samples = SAMPLES

    @classmethod
    def get_possible_active_agents(cls) -> list["AgentTypes"]:
        """
        :return: List of active agents.
        """

        return [
            cls.LearningRateAgent,
            cls.WeightDecayAgent,
            cls.DropoutAgent,
            cls.GradientClippingAgent,
            cls.AdamBetaOneAgent,
            cls.AdamBetaTwoAgent,
            cls.AdamEpsAgent,
            cls.SGDMomentumAgent,
            cls.GradientAccumulationAgent,
        ]


class ModelFamilies(EnumWithIndices):

    OLMo = "olmo"
    GPT = "gpt"
    BERT = "bert"


class ModuleTypes(EnumWithIndices):

    Convolutional = "convolutional"
    Attention = "attention"
    Linear = "linear"
    Embedding = "embedding"
