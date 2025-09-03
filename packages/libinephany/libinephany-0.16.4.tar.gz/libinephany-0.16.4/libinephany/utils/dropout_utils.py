# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

from typing import TypeAlias

import torch.nn as nn

# ======================================================================================================================
#
# CONSTANTS
#
# ======================================================================================================================

DropoutLayer: TypeAlias = (
    nn.Dropout | nn.Dropout1d | nn.Dropout2d | nn.Dropout3d | nn.AlphaDropout | nn.FeatureAlphaDropout
)

# ======================================================================================================================
#
# FUNCTIONS
#
# ======================================================================================================================


def create_torch_dropout_mapping(model: nn.Module, parameter_group_names: list[str]) -> dict[str, list[DropoutLayer]]:
    """
    :param model: Model to create dropout mapping from.
    :param parameter_group_names: Names of the parameter groups.
    :return: Dictionary mapping parameter group names to a list of the dropout layers present in that parameter group.
    """

    dropout_mapping: dict[str, list[DropoutLayer]] = {
        parameter_group_name: [] for parameter_group_name in parameter_group_names
    }

    for parameter_group_name in parameter_group_names:
        for module_name, module in model.named_modules():
            if parameter_group_name not in module_name:
                continue

            if isinstance(module, DropoutLayer):
                dropout_mapping[parameter_group_name].append(module)

    return dropout_mapping


def set_torch_dropout(
    dropout_layer_mapping: dict[str, list[DropoutLayer]] | None, parameter_group_name: str, dropout: float
) -> None:
    """
    :param dropout_layer_mapping: Mapping from parameter group names to a list of the dropout layers present in that
    parameter group.
    :param parameter_group_name: Name of the parameter group to set the dropout probability of.
    :param dropout: Dropout to set the given parameter group to.

    :note: Operation done in-place.
    """

    if dropout_layer_mapping is None:
        raise ValueError("No dropout layer mapping present. Cannot get dropout.")

    if parameter_group_name not in dropout_layer_mapping:
        return

    for dropout_layer in dropout_layer_mapping[parameter_group_name]:
        dropout_layer.p = dropout


def get_torch_parameter_group_dropout(
    dropout_layer_mapping: dict[str, list[DropoutLayer]] | None, parameter_group_name: str
) -> float | None:
    """
    :param dropout_layer_mapping: Mapping from parameter group names to a list of the dropout layers present in that
    parameter group.
    :param parameter_group_name: Name of the parameter group to get the dropout probability of.

    :note: Operation done in-place.
    """

    if dropout_layer_mapping is None:
        raise ValueError("No dropout layer mapping present. Cannot get dropout.")

    if parameter_group_name not in dropout_layer_mapping:
        return None

    if dropout_layer_mapping[parameter_group_name]:
        return dropout_layer_mapping[parameter_group_name][0].p

    return None
