# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

import copy
import inspect
from collections import defaultdict
from typing import Any

import torch
import torch.nn as nn
import torch.optim as optim
from accelerate.optimizer import AcceleratedOptimizer
from loguru import logger

from libinephany.utils.constants import PARAMS, SCHEDULER_GROUP_NAME

# ======================================================================================================================
#
# CONSTANTS
#
# ======================================================================================================================

ADAM_OPTIMISERS = [optim.Adam, optim.AdamW, optim.Adamax, optim.RAdam, optim.NAdam, optim.SparseAdam]
SGD_OPTIMISERS = [optim.SGD, optim.ASGD]  # type: ignore

PARAM_GROUP_LR = "lr"
MOMENTUM = "momentum"
MOMENTUM_BUFFER = "momentum_buffer"
MODULE_TYPE = "module_type"

LEFTOVER_PARAMS = "leftover_params"
LEFTOVER_MODULE_TYPE = "fixed"

# ======================================================================================================================
#
# FUNCTIONS
#
# ======================================================================================================================


def check_optimiser_is_adam_variant(optimizer: optim.Optimizer, raise_error: bool = True) -> bool:
    """
    :param optimizer: Optimizer of the inner model to check that it is an Adam variant.
    :param raise_error: Whether an error should be raised if the optimizer is an invalid type or not.
    :return: Whether the optimizer is a valid type.
    """

    if isinstance(optimizer, AcceleratedOptimizer):
        optimizer_unwrapped = optimizer.optimizer
    else:
        optimizer_unwrapped = optimizer

    if not any(isinstance(optimizer_unwrapped, adam_variant) for adam_variant in ADAM_OPTIMISERS):

        if raise_error:
            raise TypeError(
                f"Inner model optimizer is not an Adam variant. Got: {type(optimizer_unwrapped).__name__}. Expected one "
                f"of: {[adam_variant.__name__ for adam_variant in ADAM_OPTIMISERS]}"
            )

        return False

    return True


def check_optimiser_is_sgd_variant(optimizer: optim.Optimizer, raise_error: bool = True) -> bool:
    """
    :param optimizer: Optimizer of the inner model to check that it is an SGD variant.
    :param raise_error: Whether an error should be raised if the optimizer is an invalid type or not.
    :return: Whether the optimizer is a valid type.
    """

    if not any(isinstance(optimizer, sgd_variant) for sgd_variant in SGD_OPTIMISERS):

        if raise_error:
            raise TypeError(
                f"Inner model optimizer is not an SGD variant. Got: {type(optimizer).__name__}. Expected one "
                f"of: {[sgd_variant.__name__ for sgd_variant in SGD_OPTIMISERS]}"
            )

        return False

    return True


def compute_sgd_optimizer_update_stats(
    optimizer: optim.Optimizer, parameter_group: dict[str, Any], parameters: list[torch.Tensor]
) -> torch.Tensor | None:
    """
    :param optimizer: SGD optimizer to compute update stats for.
    :param parameter_group: Parameter group containing the learning rate and momentum.
    :param parameters: List of parameters to compute update stats from.
    :return: Tensor of demonstrating the SGD parameter updates or None.
    """

    if type(optimizer) not in SGD_OPTIMISERS:
        raise TypeError(f"Expected SGD Optimiser, not {type(optimizer).__name__}.")

    updates = []

    for param in parameters:
        if param.grad is not None and param.numel() > 0:
            update = parameter_group[PARAM_GROUP_LR] * param.grad

            if param in optimizer.state and MOMENTUM_BUFFER in optimizer.state[param]:
                update += parameter_group[MOMENTUM] * optimizer.state[param][MOMENTUM_BUFFER]

            updates.append(update.view(-1))

    if updates:
        return torch.cat(updates)

    else:
        return None


def filter_optimizer_kwargs(optimizer_class: type[optim.Optimizer], optimizer_kwargs: dict[str, Any]) -> dict:
    """
    :param optimizer_class: Class of optimizer to filter the given kwargs for.
    :param optimizer_kwargs: Optimizer-specific keyword arguments.
    :return: A filtered dictionary containing only valid keyword arguments for the given optimizer class.
    """

    optimizer_signature = inspect.signature(optimizer_class.__init__)

    valid_params = set(optimizer_signature.parameters.keys())

    return {arg_name: arg_value for arg_name, arg_value in optimizer_kwargs.items() if arg_name in valid_params}


def compile_parameter_groups(
    module_to_params: dict[str, list[torch.Tensor]],
    initial_lr: float,
    agent_controlled_modules: dict[str, str],
) -> list[dict[str, Any]]:
    """
    :param module_to_params: Mapping of module names to lists of parameters under that module.
    :param initial_lr: Initial learning rate for the parameter group.
    :param agent_controlled_modules: Dictionary mapping agent modules to their type.
    :return: List of compiled parameter groups.
    """

    return [
        {
            PARAM_GROUP_LR: initial_lr,
            SCHEDULER_GROUP_NAME: module_name,
            PARAMS: params,
            MODULE_TYPE: agent_controlled_modules[module_name],
        }
        for module_name, params in module_to_params.items()
    ]


def create_parameter_groups(
    model: torch.nn.Module,
    agent_controlled_modules: dict[str, str],
    initial_lr: float = 5e-4,
) -> list[dict[str, Any]]:
    """
    :param model: The PyTorch model for which to create parameter groups.
    :param agent_controlled_modules: Dictionary mapping agent modules to their type.
    :param initial_lr: The initial learning rate for all parameter groups.
    :return: A list of dictionaries, each representing a parameter group with 'params',
             'lr', and 'module_name' keys.
    """

    agent_controlled_modules = copy.deepcopy(agent_controlled_modules)

    leftover_params = {}
    module_to_params = defaultdict(list)

    module_splits = [mod.split(".") for mod in agent_controlled_modules.keys()]

    for name, param in model.named_parameters():
        name_split = name.split(".")
        found_module = False

        for module_split in module_splits:
            if name_split[: len(module_split)] == module_split:
                found_module = True

                module_to_params[".".join(module_split)].append(param)
                break

        if not found_module:
            leftover_params[name] = param

    if leftover_params:
        leftover_param_names = ", ".join(list(leftover_params.keys()))
        module_to_params[LEFTOVER_PARAMS] = list(leftover_params.values())
        agent_controlled_modules[LEFTOVER_PARAMS] = LEFTOVER_MODULE_TYPE

        logger.warning(f"The following parameters were not assigned to any group: {leftover_param_names}")

    # type: ignore
    return compile_parameter_groups(
        module_to_params=module_to_params,  # type: ignore
        initial_lr=initial_lr,
        agent_controlled_modules=agent_controlled_modules,
    )


def build_optimizer(
    model: nn.Module,
    agent_controlled_modules: dict[str, str],
    inner_model_optimizer: type[optim.Optimizer],
    initial_learning_rate: float,
    initial_weight_decay: float | None,
    optimizer_kwargs: dict[str, Any],
) -> optim.Optimizer:
    """
    :param model: Model to build an optimizer for.
    :param agent_controlled_modules: Dictionary mapping agent modules to their type.
    :param inner_model_optimizer: Type of the optimizer class to use.
    :param initial_learning_rate: Initial learning rate which all parameter group's learning rates will be set to.
    :param initial_weight_decay: Initial weight decay which all parameter group's weight decays will be set to.
    :param optimizer_kwargs: Optimizer-specific keyword arguments.
    :return: Constructed optimizer.
    """

    initial_weight_decay = initial_weight_decay if initial_weight_decay is not None else 0.0

    param_groups = create_parameter_groups(
        model=model,
        agent_controlled_modules=agent_controlled_modules,
        initial_lr=initial_learning_rate,
    )
    optimizer_kwargs = filter_optimizer_kwargs(optimizer_class=inner_model_optimizer, optimizer_kwargs=optimizer_kwargs)

    optimizer = inner_model_optimizer(
        param_groups, lr=initial_learning_rate, weight_decay=initial_weight_decay, **optimizer_kwargs
    )  # type: ignore

    assert isinstance(optimizer, optim.Optimizer)

    return optimizer
