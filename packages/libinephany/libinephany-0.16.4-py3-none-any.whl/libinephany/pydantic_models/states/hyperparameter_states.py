# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

from abc import abstractmethod
from typing import Any, Callable

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, computed_field

from libinephany.pydantic_models.configs.hyperparameter_configs import HParamConfig, HParamConfigs
from libinephany.utils import samplers
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
from libinephany.utils.enums import AgentTypes
from libinephany.utils.transforms import (
    HYPERPARAMETER_TRANSFORM_REGISTRY,
    HyperparameterTransform,
    HyperparameterTransformType,
)

# ======================================================================================================================
#
# CONSTANTS
#
# ======================================================================================================================

INITIAL_PREFIX = "initial_"

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class UpdateCallbacks(BaseModel):

    learning_rate: Callable[..., None]
    weight_decay: Callable[..., None]
    dropout: Callable[..., None]
    grad_norm_clip: Callable[..., None]
    adam_beta_one: Callable[..., None]
    adam_beta_two: Callable[..., None]
    adam_eps: Callable[..., None]
    sgd_momentum: Callable[..., None]

    batch_size: Callable[..., None] | None
    gradient_accumulation: Callable[..., None] | None
    epochs: Callable[..., None] | None

    def __getitem__(self, item: str) -> Callable[..., None] | None:
        """
        :param item: Name of the item to get.
        :return: Corresponding callback for the given item.
        """

        return getattr(self, item)

    def __contains__(self, item: str) -> bool:
        """
        :param item: Field to check for presence in this object.
        :return: Whether the instance has a field called the same thing as the value of the item parameter.
        """

        return item in self.model_fields


class Hyperparameter(BaseModel):

    update_callback: Callable | None = Field(..., repr=False, exclude=True)
    transform_type: HyperparameterTransformType
    dtype: type[float | int]

    initial_internal_value: float | int | None
    current_internal_value: float | int | None

    initial_delta: float | int | None
    current_delta: float | int | None

    current_scale: float | int | None

    parameter_group_name: str | None
    name: str

    @classmethod
    def build(
        cls,
        initial_external_value: float | int | None,
        initial_delta: float | int | None,
        scale: float | int | None,
        update_callback: Callable[..., None] | None,
        transform_type: str | HyperparameterTransformType,
        hparam_dtype: type[float | int],
        parameter_group_name: str | None,
        name: str,
    ) -> "Hyperparameter":
        """
        :param initial_external_value: Starting external value of the hyperparameter.
        :param initial_delta: Starting delta of the hyperparameter.
        :param scale: Scale of the hyperparameter.
        :param update_callback: Callback used to set the hyperparameter in the optimizer/model when its value changes.
        :param parameter_group_name: Name of the hyperparameter group this hyperparameter corresponds to if it is a
        layerwise hyperparameter or None if it is not.
        :param transform_type: Type of hyperparameter transform applied to this hyperparameter.
        :param hparam_dtype: The datatype of the hyperparameter
        :param name: Name of the hyperparameter being controlled.
        :return: Constructed Hyperparameter object.
        """

        transform_type = HyperparameterTransformType(transform_type)
        transform = HYPERPARAMETER_TRANSFORM_REGISTRY[transform_type]()

        # Handle None values by setting internal values to None
        current_internal_value = None
        initial_internal_value = None
        if initial_external_value is not None:
            current_internal_value = transform.to_internal(initial_external_value)
            initial_internal_value = transform.to_internal(initial_external_value)

        return cls(
            update_callback=update_callback,
            current_internal_value=current_internal_value,
            initial_internal_value=initial_internal_value,
            current_delta=initial_delta,
            initial_delta=initial_delta,
            current_scale=scale,
            parameter_group_name=parameter_group_name,
            transform_type=transform_type,
            dtype=hparam_dtype,
            name=name,
        )

    @property
    def transform(self) -> HyperparameterTransform:
        """
        :return: The transform class of the hyperparameter.
        """

        return HYPERPARAMETER_TRANSFORM_REGISTRY[self.transform_type]()

    @property
    def external_value(self) -> float | int | None:
        """
        :return: Current external value of the hyperparameter.
        """

        if self.current_internal_value is None:
            return None
        return self.dtype(self.transform.to_external(self.current_internal_value))

    @external_value.setter
    def external_value(self, new_external_value: float | int | None) -> None:
        """
        :param new_external_value: New external value to set the hyperparameter to.
        """

        if new_external_value is None:
            self.internal_value = None
        else:
            self.internal_value = self.transform.to_internal(new_external_value)

    @property
    def internal_value(self) -> float | int | None:
        """
        :return: Current internal value of the hyperparameter.
        """

        return self.current_internal_value

    @internal_value.setter
    def internal_value(self, new_internal_value: float | int | None) -> None:
        """
        :param new_internal_value: New internal value to set the hyperparameter to.
        """

        self.current_internal_value = new_internal_value

        if self.update_callback is not None and self.external_value is not None:
            if self.parameter_group_name is not None:
                self.update_callback(parameter_group_name=self.parameter_group_name, value=self.external_value)

            else:
                self.update_callback(value=self.external_value)

    @property
    def delta(self) -> float | int | None:
        """
        :return: Current delta of the hyperparameter.
        """

        return self.current_delta

    @delta.setter
    def delta(self, new_delta: float | int | None) -> None:
        """
        :param new_delta: New delta to set the hyperparameter to.
        """

        self.current_delta = new_delta

    @property
    def scale(self) -> float | int | None:
        """
        :return: Current scale of the hyperparameter.
        """

        return self.current_scale

    def set_sampled_initial_value(self, initial_external_value: float | int | None) -> None:
        """
        :param initial_external_value: Sampled external value to set the hyperparameter to.
        """

        if initial_external_value is None:
            self.initial_internal_value = None
        else:
            self.initial_internal_value = self.transform.to_internal(initial_external_value)

    def set_to_initial_value(self) -> None:
        """
        Sets the hyperparameter to its initial internal value and delta.
        """

        self.internal_value = self.initial_internal_value
        self.delta = self.initial_delta


class HyperparameterContainer(BaseModel):

    @classmethod
    @abstractmethod
    def build(
        cls,
        hparam_configs: dict[str, HParamConfig],
        update_callbacks: UpdateCallbacks,
        parameter_group_name: str | None = None,
    ) -> "HyperparameterContainer":
        """
        :param hparam_configs: Dictionary mapping hyperparameter names to hyperparameter configs.
        :param update_callbacks: Update callbacks used to update the values of hyperparameters in the InnerTask.
        :param parameter_group_name: Name of the parameter group this object is responsible for.
        :return: Constructed HyperparameterContainer object.
        """

        raise NotImplementedError

    @classmethod
    def get_hyperparameters(cls) -> list[str]:
        """
        :return: Hyperparameters associated with the ParameterGroupHParams class.
        """

        return [
            field_name
            for field_name, field_value in cls.model_fields.items()
            if field_value.annotation is Hyperparameter
        ]

    def get_hyperparameter_by_name(self, name: str | AgentTypes) -> Hyperparameter:
        """
        :param name: Name of the hyperparameter to try and get.
        :return: Hyperparameter with the corresponding name.
        :raises KeyError: If no hyperparameter with the given name can be found.
        """

        name = name.value if isinstance(name, AgentTypes) else name

        for field_name, field_value in self.model_fields.items():
            if field_value.annotation is not Hyperparameter:
                continue

            hyperparameter = getattr(self, field_name)

            if hyperparameter.name == name:
                return hyperparameter

        raise KeyError(
            f"Could not find hyperparameter with name {name} in {self.__class__.__name__} with hyperparameters "
            f"{self.get_hyperparameters()}."
        )

    def get_initial_internal_values(self, skip_hparams: list[str] | None = None) -> dict[str, float | int | None]:
        """
        :param skip_hparams: Names of the hyperparameters to not include in the initial values vector returned by
        this observation.
        :return: Dictionary mapping hyperparameter names to their current values for this parameter group.
        """

        if skip_hparams is None:
            skip_hparams = []

        return {
            field_name: field_value.initial_internal_value
            for field_name, field_value in self.__dict__.items()
            if isinstance(field_value, Hyperparameter) and field_name not in skip_hparams
        }

    def get_current_internal_values(self, skip_hparams: list[str] | None = None) -> dict[str, float | int | None]:
        """
        :param skip_hparams: Names of the hyperparameters to not include in the current values vector returned by
        this observation.
        :return: Dictionary mapping hyperparameter names to their current values for this parameter group.
        """

        if skip_hparams is None:
            skip_hparams = []

        return {
            field_name: field_value.current_internal_value
            for field_name, field_value in self.__dict__.items()
            if isinstance(field_value, Hyperparameter) and field_name not in skip_hparams
        }

    def get_current_deltas(self, skip_hparams: list[str] | None = None) -> dict[str, float | int | None]:
        """
        :param skip_hparams: Names of the hyperparameters to not include in the current deltas vector returned by
        this observation.
        :return: Dictionary mapping hyperparameter names to their current deltas for this parameter group.
        """

        if skip_hparams is None:
            skip_hparams = []

        return {
            field_name: field_value.current_delta
            for field_name, field_value in self.__dict__.items()
            if isinstance(field_value, Hyperparameter) and field_name not in skip_hparams
        }

    def set_internal_values(self, internal_values: dict[str, float | int | None]) -> None:
        """
        :param internal_values: Dictionary mapping hyperparameter names to their new internal values.
        """

        for field_name, field_value in internal_values.items():
            if hasattr(self, field_name) and isinstance(getattr(self, field_name), Hyperparameter):
                getattr(self, field_name).internal_value = field_value

    def set_deltas(self, deltas: dict[str, float | int | None]) -> None:
        """
        :param deltas: Dictionary mapping hyperparameter names to their new deltas.
        """

        for field_name, field_value in deltas.items():
            if hasattr(self, field_name) and isinstance(getattr(self, field_name), Hyperparameter):
                getattr(self, field_name).delta = field_value

    def set_sampled_initial_values(
        self, sample_initial_external_values: dict[str, np.ndarray | float | int | None]
    ) -> None:
        """
        :param sample_initial_external_values: Dictionary mapping hyperparameter names to newly sampled initial
        external values.
        """

        for hyperparameter_name, initial_external_value in sample_initial_external_values.items():
            if hasattr(self, hyperparameter_name):
                getattr(self, hyperparameter_name).set_sampled_initial_value(
                    initial_external_value=initial_external_value
                )

    def set_to_initial_values(self) -> None:
        """
        Sets all hyperparameters to their initial values and deltas.
        """

        for attr_name, attr in self.__dict__.items():
            if isinstance(attr, Hyperparameter):
                attr.set_to_initial_value()


class ParameterGroupHParams(HyperparameterContainer):

    parameter_group_name: str

    learning_rate: Hyperparameter
    weight_decay: Hyperparameter
    dropout: Hyperparameter
    grad_norm_clip: Hyperparameter
    adam_beta_one: Hyperparameter
    adam_beta_two: Hyperparameter
    adam_eps: Hyperparameter
    sgd_momentum: Hyperparameter

    @classmethod
    def build(
        cls,
        hparam_configs: dict[str, HParamConfig],
        update_callbacks: UpdateCallbacks,
        parameter_group_name: str | None = None,
    ) -> "ParameterGroupHParams":
        """
        :param hparam_configs: Dictionary mapping hyperparameter names to hyperparameter configs.
        :param update_callbacks: Update callbacks used to update the values of hyperparameters in the InnerTask.
        :param parameter_group_name: Name of the parameter group this object is responsible for.
        :return: Constructed ParameterGroupHParams object.
        """

        if parameter_group_name is None:
            raise ValueError(f"Expected parameter_group_name while building {cls.__name__}; got None.")

        hyperparameters = {}

        for hyperparameter_name, hyperparameter_config in hparam_configs.items():
            initial_external_value = hyperparameter_config.initial_value
            initial_delta = hyperparameter_config.initial_delta
            scale = hyperparameter_config.scale
            callback = None if hyperparameter_name not in update_callbacks else update_callbacks[hyperparameter_name]

            hyperparameters[hyperparameter_name] = Hyperparameter.build(
                initial_external_value=initial_external_value,
                initial_delta=initial_delta,
                scale=scale,
                update_callback=callback,
                parameter_group_name=parameter_group_name,
                transform_type=hyperparameter_config.transform,
                hparam_dtype=hyperparameter_config.hparam_dtype,
                name=hyperparameter_name,
            )

        return cls(
            parameter_group_name=parameter_group_name,
            **hyperparameters,
        )

    def get_hyperparameter_transform_types(
        self, skip_hparams: list[str] | None = None
    ) -> dict[str, HyperparameterTransformType]:
        """
        :return: Dictionary mapping hyperparameter names to their transform type for this parameter group.
        """

        if skip_hparams is None:
            skip_hparams = []

        return {
            field_name: field_value.transform_type
            for field_name, field_value in self.__dict__.items()
            if isinstance(field_value, Hyperparameter) and field_name not in skip_hparams
        }


class GlobalHParams(HyperparameterContainer):

    batch_size: Hyperparameter
    gradient_accumulation: Hyperparameter
    epochs: Hyperparameter
    tokens: Hyperparameter
    samples: Hyperparameter

    @classmethod
    def build(
        cls,
        hparam_configs: dict[str, HParamConfig],
        update_callbacks: UpdateCallbacks,
        parameter_group_name: str | None = None,
    ) -> "GlobalHParams":
        """
        :param hparam_configs: Dictionary mapping hyperparameter names to hyperparameter configs.
        :param update_callbacks: Update callbacks used to update the values of hyperparameters in the InnerTask.
        :param parameter_group_name: Should always be None for this class.
        :return: Constructed GlobalHParams object.
        """

        if parameter_group_name is not None:
            raise ValueError(
                f"Got unexpected parameter_group_name '{parameter_group_name}' while building {cls.__name__}; "
                f"expected None."
            )

        hyperparameters = {}

        for hyperparameter_name, hyperparameter_config in hparam_configs.items():
            callback = None if hyperparameter_name not in update_callbacks else update_callbacks[hyperparameter_name]

            hyperparameters[hyperparameter_name] = Hyperparameter.build(
                initial_external_value=hyperparameter_config.initial_value,
                initial_delta=hyperparameter_config.initial_delta,
                scale=hyperparameter_config.scale,
                update_callback=callback,
                parameter_group_name=None,
                transform_type=hyperparameter_config.transform,
                hparam_dtype=hyperparameter_config.hparam_dtype,
                name=hyperparameter_name,
            )

        return cls(**hyperparameters)


class HyperparameterStates(BaseModel):

    model_config = ConfigDict(arbitrary_types_allowed=True)

    update_callbacks: UpdateCallbacks
    hparam_configs: HParamConfigs
    layerwise_hparam_configs: dict[str, HParamConfig]
    global_hparam_configs: dict[str, HParamConfig]
    hparam_samplers: dict[str, samplers.Sampler]

    global_hparams: GlobalHParams
    parameter_group_hparams: dict[str, ParameterGroupHParams] = {}
    initial_hyperparameter_internal_values: dict[str, float | int] = {}
    initial_hyperparameter_external_values: dict[str, float | int] = {}

    batches_processed: int = 0
    tokens_processed: int = 0

    def __getitem__(self, item: str) -> ParameterGroupHParams:
        """
        :param item: Name of the item to retrieve.
        :return: ParameterGroupHParams of the given item.
        """

        if item not in self.parameter_group_hparams:
            raise KeyError(f"{item} is not in possible parameter groups.")

        return self.parameter_group_hparams[item]

    def __getattr__(self, item: str) -> Any:
        """
        :param item: Name of the attribute to get.
        :return: Attribute value.
        """

        if INITIAL_PREFIX in item:
            hyperparameter_name = item.replace(INITIAL_PREFIX, "")

            return self.initial_hyperparameter_external_values[hyperparameter_name]

        return super().__getattr__(item)  # type: ignore

    @computed_field  # type: ignore[misc]
    @property
    def batch_size(self) -> Hyperparameter:
        """
        :return: The batch size of the inner model.
        """
        return self.global_hparams.batch_size

    @computed_field  # type: ignore[misc]
    @property
    def gradient_accumulation(self) -> Hyperparameter:
        """
        :return: The gradient accumulation steps of the inner model.
        """
        return self.global_hparams.gradient_accumulation

    @computed_field  # type: ignore[misc]
    @property
    def epochs(self) -> Hyperparameter:
        """
        :return: The batch size of the inner model.
        """
        return self.global_hparams.epochs

    @computed_field  # type: ignore[misc]
    @property
    def tokens(self) -> Hyperparameter:
        """
        :return: Tokens hyperparameter.
        """

        return self.global_hparams.tokens

    @computed_field  # type: ignore[misc]
    @property
    def samples(self) -> Hyperparameter:
        """
        :return: Samples hyperparameter.
        """

        return self.global_hparams.samples

    @property
    def max_tokens_to_process(self) -> int | None:
        """
        :return: Number of tokens to process in the episode.
        """

        if self.hparam_configs.token_config.sample_initial_values:
            tokens_value = self.tokens.external_value
            epochs_value = self.epochs.external_value
            if tokens_value is not None and epochs_value is not None:
                return int(tokens_value * epochs_value)

        return None

    @computed_field  # type: ignore[misc]
    @property
    def all_hparam_configs(self) -> dict[str, HParamConfig]:
        """
        :return: Hyperparameter configs for all (layerwise and global) hyperparameters.
        """
        return {**self.global_hparam_configs, **self.layerwise_hparam_configs}

    @classmethod
    def build(
        cls,
        hparam_configs: HParamConfigs,
        update_callbacks: UpdateCallbacks,
        parameter_group_names: list[str],
    ) -> "HyperparameterStates":
        """
        :param hparam_configs: Hyperparameter configs for all hyperparameters relevant to the InnerTask.
        :param update_callbacks: Update callbacks used to update the values of hyperparameters in the InnerTask.
        :param parameter_group_names: List of parameter group names to add.
        :return: Constructed HyperparameterStates object.
        """

        layerwise_hparam_config_mapping = cls.get_layerwise_hparam_config_mapping(hparam_configs=hparam_configs)
        global_hparam_config_mapping = cls.get_global_hparam_config_mapping(hparam_configs=hparam_configs)
        all_hparam_config_mapping = cls.get_all_hparam_config_mapping(hparam_configs=hparam_configs)
        hparam_samplers = cls.build_samplers(hparam_configs=all_hparam_config_mapping)
        initial_hyperparameter_external_values = cls.get_initial_hparam_external_value_mapping(
            hparam_configs=hparam_configs
        )
        initial_hyperparameter_internal_values = cls.map_external_values_dict_to_internal_values(
            external_values_dict=initial_hyperparameter_external_values, hparam_configs=hparam_configs
        )

        global_hparams = GlobalHParams.build(
            hparam_configs=global_hparam_config_mapping,
            update_callbacks=update_callbacks,
        )

        inner_task_state = cls(
            update_callbacks=update_callbacks,
            hparam_configs=hparam_configs,
            layerwise_hparam_configs=layerwise_hparam_config_mapping,
            global_hparam_configs=global_hparam_config_mapping,
            hparam_samplers=hparam_samplers,
            global_hparams=global_hparams,
            initial_hyperparameter_internal_values=initial_hyperparameter_internal_values,
            initial_hyperparameter_external_values=initial_hyperparameter_external_values,
        )

        inner_task_state.add_parameter_groups(parameter_group_names=parameter_group_names)

        return inner_task_state

    @classmethod
    def get_global_hyperparameters(cls) -> list[str]:
        """
        :return: Global hyperparameters associated with the model.
        """

        return GlobalHParams.get_hyperparameters()

    @classmethod
    def get_layerwise_hyperparameters(cls) -> list[str]:
        """
        :return: Layerwise hyperparameters associated with the model.
        """

        return ParameterGroupHParams.get_hyperparameters()

    @classmethod
    def get_all_hyperparameters(cls) -> list[str]:
        """
        :return: All hyperparameters (global and layerwise) associated with the model.
        """

        return cls.get_global_hyperparameters() + cls.get_layerwise_hyperparameters()

    @staticmethod
    def get_global_hparam_config_mapping(hparam_configs: HParamConfigs) -> dict[str, HParamConfig]:
        """
        :param hparam_configs: Hyperparameter configs for all global hyperparameters relevant to the InnerTask.
        :return: Mapping of hyperparameter names to their corresponding hyperparameter config.
        """

        return {
            BATCH_SIZE: hparam_configs.batch_size_config,
            GRADIENT_ACCUMULATION: hparam_configs.gradient_accumulation_config,
            EPOCHS: hparam_configs.epochs_config,
            TOKENS: hparam_configs.token_config,
            SAMPLES: hparam_configs.samples_config,
        }

    @staticmethod
    def get_layerwise_hparam_config_mapping(hparam_configs: HParamConfigs) -> dict[str, HParamConfig]:
        """
        :param hparam_configs: Hyperparameter configs for all layerwise hyperparameters relevant to the InnerTask.
        :return: Mapping of hyperparameter names to their corresponding hyperparameter config.
        """

        return {
            LEARNING_RATE: hparam_configs.learning_rate_config,
            WEIGHT_DECAY: hparam_configs.weight_decay_config,
            DROPOUT: hparam_configs.dropout_config,
            GRAD_NORM_CLIP: hparam_configs.gradient_norm_clipping_config,
            ADAM_BETA_ONE: hparam_configs.adam_beta_one_config,
            ADAM_BETA_TWO: hparam_configs.adam_beta_two_config,
            ADAM_EPS: hparam_configs.adam_eps_config,
            SGD_MOMENTUM: hparam_configs.sgd_momentum_config,
        }

    @staticmethod
    def get_all_hparam_config_mapping(hparam_configs: HParamConfigs) -> dict[str, HParamConfig]:
        """
        :param hparam_configs: Hyperparameter configs for all global and layerwise hyperparameters relevant to the InnerTask.
        :return: Mapping of hyperparameter names to their corresponding hyperparameter config.
        """
        return {
            **HyperparameterStates.get_global_hparam_config_mapping(hparam_configs),
            **HyperparameterStates.get_layerwise_hparam_config_mapping(hparam_configs),
        }

    @staticmethod
    def get_initial_hparam_external_value_mapping(hparam_configs: HParamConfigs) -> dict[str, float | int]:
        """
        :param hparam_configs: Hyperparameter configs for all hyperparameters relevant to the InnerTask.
        :return: Mapping of hyperparameter names to their corresponding initial value.
        """

        hparam_config_dict = HyperparameterStates.get_all_hparam_config_mapping(hparam_configs)
        return {hparam: config.initial_value for hparam, config in hparam_config_dict.items()}

    @staticmethod
    def map_external_values_dict_to_internal_values(
        external_values_dict: dict[str, float | int], hparam_configs: HParamConfigs
    ) -> dict[str, float | int]:
        """
        :param external_values_dict: Dict mapping hyperparameter names to external values.
        :param hparam_configs: Hyperparameter configs for all hyperparameters relevant to the InnerTask.
        :return: Mapping of hyperparameter names to their corresponding internal value.
        """
        hparam_config_dict = HyperparameterStates.get_all_hparam_config_mapping(hparam_configs)
        transforms_dict = {
            hparam: HYPERPARAMETER_TRANSFORM_REGISTRY[HyperparameterTransformType(config.transform)]()
            for hparam, config in hparam_config_dict.items()
        }
        return {
            hparam: transforms_dict[hparam].to_internal(external_value)
            for hparam, external_value in external_values_dict.items()
        }

    @staticmethod
    def build_samplers(hparam_configs: dict[str, HParamConfig]) -> dict[str, samplers.Sampler]:
        """
        :param hparam_configs: Mapping of hyperparameter names to their corresponding hyperparameter config.
        :return: Dictionary mapping hyperparameter names to their corresponding samplers.
        """

        hparam_samplers = {}

        for hyperparameter_name, hyperparameter_config in hparam_configs.items():
            sampler = samplers.build_sampler(
                sampler_name=hyperparameter_config.sampler,
                lower_bound=hyperparameter_config.sample_lower_bound,
                upper_bound=hyperparameter_config.sample_upper_bound,
                discrete_values=hyperparameter_config.sample_discrete_values,
                step=hyperparameter_config.sample_step,
                sample_dtype=hyperparameter_config.hparam_dtype,
            )
            hparam_samplers[hyperparameter_name] = sampler

        return hparam_samplers

    def add_parameter_group(self, parameter_group_name: str) -> None:
        """
        :param parameter_group_name: Name of the parameter group to add.
        """

        self.parameter_group_hparams[parameter_group_name] = ParameterGroupHParams.build(
            update_callbacks=self.update_callbacks,
            hparam_configs=self.layerwise_hparam_configs,
            parameter_group_name=parameter_group_name,
        )

    def add_parameter_groups(self, parameter_group_names: list[str]) -> None:
        """
        :param parameter_group_names: List of parameter group names to add.
        """

        for parameter_group_name in parameter_group_names:
            self.add_parameter_group(parameter_group_name=parameter_group_name)

    def resample(self) -> None:
        """
        Resamples initial hyperparameter values and sets them.
        """

        external_value_samples = {}
        all_hparam_configs = self.get_all_hparam_config_mapping(hparam_configs=self.hparam_configs)

        for hparam_name, sampler in self.hparam_samplers.items():
            hparam_config = all_hparam_configs[hparam_name]

            if hparam_config.sample_initial_values:
                sampled_external_value = sampler()
                if isinstance(sampled_external_value, np.ndarray):
                    external_value_samples[hparam_name] = sampled_external_value[0].item()
                else:
                    external_value_samples[hparam_name] = sampled_external_value

        self.global_hparams.set_sampled_initial_values(sample_initial_external_values=external_value_samples)

        for parameter_group_hparams in self.parameter_group_hparams.values():
            parameter_group_hparams.set_sampled_initial_values(
                sample_initial_external_values=external_value_samples
            )  # type: ignore

        internal_value_samples = self.map_external_values_dict_to_internal_values(
            external_values_dict=external_value_samples,
            hparam_configs=self.hparam_configs,
        )

        self.initial_hyperparameter_external_values.update(external_value_samples)  # type: ignore
        self.initial_hyperparameter_internal_values.update(internal_value_samples)  # type: ignore

    def set_to_initial_values(self) -> None:
        """
        Sets all global hyperparameters and hyperparameters in all hyperparameter groups to their initial values and
        deltas.
        """

        self.batches_processed = 0
        self.tokens_processed = 0

        self.global_hparams.set_to_initial_values()

        for parameter_group_hparams in self.parameter_group_hparams.values():
            parameter_group_hparams.set_to_initial_values()

    def get_initial_internal_values(self, skip_hparams: list[str] | None = None) -> dict[str, float | int | None]:
        """
        :param skip_hparams: Hyperparameters to ignore while retrieving initial values.
        :return: Dictionary mapping hyperparameter names to their initial values at the start of training.
        """

        initial_internal_values = {
            **self.global_hparams.get_initial_internal_values(skip_hparams),
            **next(iter(self.parameter_group_hparams.values())).get_initial_internal_values(skip_hparams),
        }
        initial_internal_values = {
            hparam_name: initial_internal_values.get(hparam_name, None)
            for hparam_name in self.initial_hyperparameter_internal_values
        }

        return initial_internal_values
