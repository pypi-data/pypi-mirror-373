# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

from typing import Any, cast

from pydantic import BaseModel, ConfigDict, ValidationError, field_serializer, field_validator, model_validator

from libinephany.utils.enums import AgentTypes

# ======================================================================================================================
#
# CONSTANTS
#
# ======================================================================================================================

SKIP_TYPE_CONVERSIONS = ["initial_delta", "scale"]

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class HParamConfig(BaseModel):

    model_config = ConfigDict(arbitrary_types_allowed=True, validate_assignment=True)

    max_hparam_value: float | int
    min_hparam_value: float | int
    initial_value: float | int
    initial_delta: float
    scale: float
    hparam_dtype: type[float | int] = float
    transform: str = "identity"

    sampler: str
    sample_initial_values: bool = False
    sample_lower_bound: float | int
    sample_upper_bound: float | int
    sample_step: int | float | None = None
    sample_discrete_values: list[float | int] | None = None

    @field_validator("hparam_dtype", mode="before")
    @classmethod
    def _parse_dtype(cls, dtype: type[float | int] | str | None) -> type[float | int]:
        if dtype is None:
            return float
        if type(dtype) is type:
            return dtype
        if type(dtype) is str:
            if dtype == "float":
                return float
            if dtype == "int":
                return int
        raise ValidationError

    @model_validator(mode="after")
    def _ensure_type(self) -> "HParamConfig":
        """
        :return: Updated hparam config.
        """

        for field, value in self.__dict__.items():
            if field in SKIP_TYPE_CONVERSIONS:
                continue

            if value is not None and not isinstance(value, (str, type, bool, list)):
                self.__dict__[field] = self.hparam_dtype(value)

        return self

    @field_serializer("hparam_dtype")
    def serialize_type(self, value: type[int | float], *args, **kwargs) -> str:
        """
        :param value: Value to serialize.
        :return: Serialized type.
        """

        return value.__name__

    def override(self, overrides: dict[str, Any]) -> None:
        """
        :param overrides: Overrides to apply to the hyperparameter config.
        """

        for field, value in overrides.items():
            if not hasattr(self, field):
                raise AttributeError(f"{self.__class__.__name__} does not have field {field} to override!")

            if not isinstance(field, (str, type, bool)):
                setattr(self, field, self.hparam_dtype(value))

            else:
                setattr(self, field, value)

        self.model_validate(self, strict=True)


class LearningRateHParamConfig(HParamConfig):
    max_hparam_value: float | int = 1e-2
    min_hparam_value: float | int = 1e-10
    initial_value: float = 0.001
    initial_delta: float = 0.0
    scale: float = 1.0

    sampler: str = "RoundRobinDiscreteValueSampler"
    sample_initial_values: bool = True
    sample_lower_bound: float | int = 1e-5
    sample_upper_bound: float | int = 1e-2
    sample_discrete_values: list[float | int] | None = [0.0, 0.01, 0.001, 0.0001, 0.003, 0.0003]


class WeightDecayHParamConfig(HParamConfig):
    max_hparam_value: float | int = 1.0
    min_hparam_value: float | int = 0.0
    initial_value: float = 0.001
    initial_delta: float = 0.0
    scale: float = 1.0

    sampler: str = "RoundRobinDiscreteValueSampler"
    sample_initial_values: bool = True
    sample_lower_bound: float | int = 1e-5
    sample_upper_bound: float | int = 1e-1
    sample_discrete_values: list[float | int] | None = [0.0, 0.1, 0.01, 0.001, 0.0001, 0.00001]


class DropoutHParamConfig(HParamConfig):
    max_hparam_value: float | int = 0.9
    min_hparam_value: float | int = 0.0
    initial_value: float = 0.05
    initial_delta: float = 0.0
    scale: float = 1.0

    sampler: str = "DiscreteRangeSampler"
    sample_initial_values: bool = False
    sample_lower_bound: float | int = 0.0
    sample_upper_bound: float | int = 0.5
    sample_step: float = 0.1


class GradientNormClippingHParamConfig(HParamConfig):
    max_hparam_value: float | int = 10.0
    min_hparam_value: float | int = 0.1
    initial_value: float = 1.0
    initial_delta: float = 0.0
    scale: float = 1.0

    sampler: str = "RoundRobinDiscreteValueSampler"
    sample_initial_values: bool = False
    sample_lower_bound: float | int = 5.0
    sample_upper_bound: float | int = 1e-1
    sample_discrete_values: list[float | int] | None = [0.1, 0.5, 1.0, 3.0, 5.0, 10.0]


class AdamBetaOneHParamConfig(HParamConfig):
    max_hparam_value: float | int = 0.99
    min_hparam_value: float | int = 0.0
    initial_value: float = 0.9
    initial_delta: float = 0.0
    scale: float = 1.0

    sampler: str = "DiscreteRangeSampler"
    sample_initial_values: bool = False
    sample_lower_bound: float = 0.0
    sample_upper_bound: float = 0.99
    sample_step: float = 0.01
    sample_discrete_values: list[float | int] | None = None


class AdamBetaTwoHParamConfig(HParamConfig):
    max_hparam_value: float | int = 0.99
    min_hparam_value: float | int = 0.0
    initial_value: float = 0.99
    initial_delta: float = 0.0
    scale: float = 1.0

    sampler: str = "DiscreteRangeSampler"
    sample_initial_values: bool = False
    sample_lower_bound: float = 0.0
    sample_upper_bound: float = 0.99
    sample_step: float = 0.01
    sample_discrete_values: list[float | int] | None = None


class AdamEpsHParamConfig(HParamConfig):
    max_hparam_value: float | int = 1e-3
    min_hparam_value: float | int = 1e-15
    initial_value: float = 1e-8
    initial_delta: float = 0.0
    scale: float = 1.0

    sampler: str = "DiscreteRangeSampler"
    sample_initial_values: bool = False
    sample_lower_bound: float = 0.0
    sample_upper_bound: float = 0.99
    sample_step: float = 0.01
    sample_discrete_values: list[float | int] | None = None


class SGDMomentumHParamConfig(HParamConfig):
    max_hparam_value: float | int = 1.0
    min_hparam_value: float | int = 0.0
    initial_value: float = 0.9
    initial_delta: float = 0.0
    scale: float = 1.0

    sampler: str = "DiscreteRangeSampler"
    sample_initial_values: bool = False
    sample_lower_bound: float = 0.0
    sample_upper_bound: float = 1.0
    sample_step: float = 0.05
    sample_discrete_values: list[float | int] | None = None


class BatchSizeHParamConfig(HParamConfig):
    max_hparam_value: float | int = 512
    min_hparam_value: float | int = 8
    hparam_dtype: type[float | int] = int
    initial_value: int = 128
    initial_delta: float = 0.0
    scale: float = 1.0

    sampler: str = "DiscreteRangeSampler"
    sample_initial_values: bool = False
    sample_lower_bound: int = 8
    sample_upper_bound: int = 512
    sample_step: int = 8
    sample_discrete_values: list[float | int] | None = None


class GradientAccumulationHParamConfig(HParamConfig):
    max_hparam_value: float | int = 64
    min_hparam_value: float | int = 1
    hparam_dtype: type[float | int] = int
    initial_value: int = 1
    initial_delta: float = 0.0
    scale: float = 1.0

    sampler: str = "DiscreteRangeSampler"
    sample_initial_values: bool = False
    sample_lower_bound: int = 1
    sample_upper_bound: int = 64
    sample_step: int = 1
    sample_discrete_values: list[float | int] | None = None
    force_limit: float | int = 64


class EpochsHParamConfig(HParamConfig):
    max_hparam_value: float | int = 16
    min_hparam_value: float | int = 1
    hparam_dtype: type[float | int] = int
    initial_value: int = 1
    initial_delta: float = 0.0
    scale: float = 1.0

    sampler: str = "DiscreteRangeSampler"
    sample_initial_values: bool = False
    sample_lower_bound: int = 1
    sample_upper_bound: int = 3
    sample_step: int = 1


class TokensHParamConfig(HParamConfig):
    max_hparam_value: float | int = 1e9
    min_hparam_value: float | int = 25e6
    hparam_dtype: type[float | int] = int
    initial_value: int = int(25e6)
    initial_delta: float = 0.0
    scale: float = 1.0

    sampler: str = "DiscreteRangeSampler"
    sample_initial_values: bool = False
    sample_lower_bound: int = int(25e6)
    sample_upper_bound: int = int(1e9)
    sample_step: int = int(1e6)


class SamplesHParamConfig(HParamConfig):
    max_hparam_value: float | int = 1e9
    min_hparam_value: float | int = 1e4
    hparam_dtype: type[float | int] = int
    initial_value: int = int(1e5)
    initial_delta: float = 0.0
    scale: float = 1.0

    sampler: str = "DiscreteRangeSampler"
    sample_initial_values: bool = False
    sample_lower_bound: int = int(1e4)
    sample_upper_bound: int = int(1e7)
    sample_step: int = int(1e4)


class HParamConfigs(BaseModel):

    learning_rate_config: HParamConfig = LearningRateHParamConfig()
    weight_decay_config: HParamConfig = WeightDecayHParamConfig()
    dropout_config: HParamConfig = DropoutHParamConfig()
    gradient_norm_clipping_config: HParamConfig = GradientNormClippingHParamConfig()
    adam_beta_one_config: HParamConfig = AdamBetaOneHParamConfig()
    adam_beta_two_config: HParamConfig = AdamBetaTwoHParamConfig()
    adam_eps_config: HParamConfig = AdamEpsHParamConfig()
    sgd_momentum_config: HParamConfig = SGDMomentumHParamConfig()

    batch_size_config: HParamConfig = BatchSizeHParamConfig()
    gradient_accumulation_config: GradientAccumulationHParamConfig = GradientAccumulationHParamConfig()
    epochs_config: HParamConfig = EpochsHParamConfig()
    token_config: HParamConfig = TokensHParamConfig()
    samples_config: HParamConfig = SamplesHParamConfig()

    constraints: dict[str, dict[str, Any] | None] | None = {
        "FirstDefaultParamorphConstraint": None,
    }

    def override(self, overrides: dict[str, dict[str, Any]] | None) -> None:
        """
        :param overrides: None or config overrides to apply.
        """

        if overrides is not None:
            for config_name, config_overrides in overrides.items():
                if not hasattr(self, config_name):
                    raise AttributeError(
                        f"{self.__class__.__name__} does not have hyperparameter config {config_name}!"
                    )

                config = getattr(self, config_name)
                config.override(overrides=config_overrides)

    def set_hyperparameter_config_from_agent_type(
        self, agent_type: str | AgentTypes, hparam_config: HParamConfig
    ) -> None:
        """
        :param agent_type: Type of agent to set the hyperparameter config for.
        :param hparam_config: HParamConfig for the agent type to set.
        :raises ValueError: If given agent type is not known.
        """

        agent_type = AgentTypes(agent_type)

        match agent_type:
            case AgentTypes.LearningRateAgent:
                self.learning_rate_config = hparam_config

            case AgentTypes.WeightDecayAgent:
                self.weight_decay_config = hparam_config

            case AgentTypes.DropoutAgent:
                self.dropout_config = hparam_config

            case AgentTypes.GradientClippingAgent:
                self.gradient_norm_clipping_config = hparam_config

            case AgentTypes.AdamBetaOneAgent:
                self.adam_beta_one_config = hparam_config

            case AgentTypes.AdamBetaTwoAgent:
                self.adam_beta_two_config = hparam_config

            case AgentTypes.AdamEpsAgent:
                self.adam_eps_config = hparam_config

            case AgentTypes.SGDMomentumAgent:
                self.sgd_momentum_config = hparam_config

            case AgentTypes.BatchSize:
                self.batch_size_config = hparam_config

            case AgentTypes.GradientAccumulationAgent:
                self.gradient_accumulation_config = cast(GradientAccumulationHParamConfig, hparam_config)

            case AgentTypes.Epochs:
                self.epochs_config = hparam_config

            case AgentTypes.Tokens:
                self.token_config = hparam_config

            case AgentTypes.Samples:
                self.samples_config = hparam_config

            case _:
                raise ValueError(f"Unknown agent type: {agent_type.value}.")

    def get_hyperparameter_config_from_agent_type(self, agent_type: str | AgentTypes) -> HParamConfig:
        """
        :param agent_type: Type of agent to get the hyperparameter config for.
        :return: Corresponding hyperparameter config to the given agent type.
        :raises ValueError: If given agent type is not known.
        """

        agent_type = AgentTypes(agent_type)

        match agent_type:
            case AgentTypes.LearningRateAgent:
                return self.learning_rate_config

            case AgentTypes.WeightDecayAgent:
                return self.weight_decay_config

            case AgentTypes.DropoutAgent:
                return self.dropout_config

            case AgentTypes.GradientClippingAgent:
                return self.gradient_norm_clipping_config

            case AgentTypes.AdamBetaOneAgent:
                return self.adam_beta_one_config

            case AgentTypes.AdamBetaTwoAgent:
                return self.adam_beta_two_config

            case AgentTypes.AdamEpsAgent:
                return self.adam_eps_config

            case AgentTypes.SGDMomentumAgent:
                return self.sgd_momentum_config

            case AgentTypes.BatchSize:
                return self.batch_size_config

            case AgentTypes.GradientAccumulationAgent:
                return self.gradient_accumulation_config

            case AgentTypes.Epochs:
                return self.epochs_config

            case AgentTypes.Tokens:
                return self.token_config

            case AgentTypes.Samples:
                return self.samples_config

            case _:
                raise ValueError(f"Unknown agent type: {agent_type.value}.")
