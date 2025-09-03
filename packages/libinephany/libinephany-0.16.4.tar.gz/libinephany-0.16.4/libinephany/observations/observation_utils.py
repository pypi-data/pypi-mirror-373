# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

import math
from enum import Enum
from itertools import chain
from typing import Any, Callable

import numpy as np
import pandas as pd
import torch
import torch.optim as optim
from scipy.stats import norm

from libinephany.pydantic_models.schemas.tensor_statistics import TensorStatistics
from libinephany.utils import optim_utils

# ======================================================================================================================
#
# CONSTANTS
#
# ======================================================================================================================

EXP_AVERAGE = "exp_avg"
MIN_DECAY_FACTOR = 1e-10

MIN_TOTAL_WEIGHT = 1e-15  # Minimum total weight threshold for numerical stability

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class StatisticsCallStage(Enum):

    ON_BATCH_END = "on_batch_end"
    ON_OPTIMIZER_STEP = "on_optimizer_step"
    ON_TRAIN_END = "on_train_end"

    FORWARD_HOOK = "forward_hook"


class StatisticStorageTypes(Enum):

    TENSOR_STATISTICS = TensorStatistics.__name__
    FLOAT = float.__name__
    VECTOR = "vector"


# ======================================================================================================================
#
# FUNCTIONS
#
# ======================================================================================================================


def get_exponential_weighted_average(values: list[int | float]) -> float:
    """
    :param values: List of values to average via EWA.
    :return: EWA of the given values.
    """
    exp_weighted_average = pd.Series(values).ewm(alpha=0.1).mean().iloc[-1]
    assert isinstance(exp_weighted_average, float)
    return exp_weighted_average


def apply_averaging_function_to_tensor_statistics(
    tensor_statistics: list[TensorStatistics], averaging_function: Callable[[list[float]], float]
) -> TensorStatistics:
    """
    :param tensor_statistics: List of statistics models to average over.
    :param averaging_function: Function to average the values with.
    :return: TensorStatistics containing the average over all given tensor statistics.
    """

    fields = TensorStatistics.model_fields.keys()
    averaged_metrics = {
        field: averaging_function([getattr(statistics, field) for statistics in tensor_statistics]) for field in fields
    }

    return TensorStatistics(**averaged_metrics)


def apply_averaging_function_to_dictionary_of_tensor_statistics(
    data: dict[str, list[TensorStatistics]], averaging_function: Callable[[list[float]], float]
) -> dict[str, TensorStatistics]:
    """
    :param data: Dictionary mapping parameter group names to list of TensorStatistics from that parameter group.
    :param averaging_function: Function to average the values with.
    :return: Dictionary mapping parameter group names to TensorStatistics averaged over all statistics in the given
    TensorStatistics models.
    """

    return {
        group: apply_averaging_function_to_tensor_statistics(
            tensor_statistics=metrics, averaging_function=averaging_function
        )
        for group, metrics in data.items()
    }


def apply_averaging_function_to_dictionary_of_metric_lists(
    data: dict[str, list[float]], averaging_function: Callable[[list[float]], float]
) -> dict[str, float]:
    """
    :param data: Dictionary mapping parameter group names to list of metrics from that parameter group.
    :param averaging_function: Function to average the values with.
    :return: Dictionary mapping parameter group names to averages over all metrics from each parameter group.
    """

    return {group: averaging_function(metrics) for group, metrics in data.items()}


def average_tensor_statistics(tensor_statistics: list[TensorStatistics]) -> TensorStatistics:
    """
    :param tensor_statistics: List of TensorStatistics models to average into one model.
    :return: Averages over all given tensor statistics models.
    """

    averaged = {
        field: sum([getattr(statistics_model, field) for statistics_model in tensor_statistics])
        for field in TensorStatistics.model_fields.keys()
    }
    averaged = {field: total / len(tensor_statistics) for field, total in averaged.items()}

    return TensorStatistics(**averaged)


def create_one_hot_observation(vector_length: int, one_hot_index: int | None) -> list[int | float]:
    """
    :param vector_length: Length of the one-hot vector.
    :param one_hot_index: Index of the vector whose element should be set to 1.0, leaving all others as 0.0.
    :return: Constructed one-hot vector in a list.
    """

    if one_hot_index is not None and one_hot_index < 0:
        raise ValueError("One hot indices must be greater than 0.")

    one_hot = np.zeros(vector_length, dtype=np.int8)

    if one_hot_index is not None:
        one_hot[one_hot_index] = 1

    as_list = one_hot.tolist()

    assert isinstance(as_list, list), "One-hot vector must be a list."

    return as_list


def create_one_hot_depth_encoding(agent_controlled_modules: list[str], parameter_group_name: str) -> list[int | float]:
    """
    :param agent_controlled_modules: Ordered list of parameter group names in the inner model.
    :param parameter_group_name: Name of the parameter group to create a depth one-hot vector for.
    :return: Constructed one-hot depth encoding in a list.

    :note: GANNO encodes depths to one-hot vectors of length 3 regardless of the size of the model.
    """

    module_index = agent_controlled_modules.index(parameter_group_name)
    number_of_modules = len(agent_controlled_modules)

    one_hot_index = min(2, (module_index * 3) // number_of_modules)

    return create_one_hot_observation(vector_length=3, one_hot_index=one_hot_index)


def check_if_tensor_is_xpu(tensor: torch.Tensor | None) -> bool:
    """
    :param tensor: Tensor to check whether it is an XPU tensor.
    :return: Whether the tensor is an XPU tensor.
    """

    try:
        xpu_available = torch.xpu.is_available()
        return xpu_available and tensor.is_xpu

    except AttributeError:
        return False


def tensor_on_local_rank(tensor: torch.Tensor | None) -> bool:
    """
    :param tensor: Tensor to check whether it is owned by the local rank, partially or entirely.
    :return: Whether the tensor is owned by the local rank.
    """

    valid_tensor = tensor is not None and tensor.numel() > 0
    device_index = tensor.device.index if valid_tensor else None

    is_xpu = check_if_tensor_is_xpu(tensor)
    cuda_available = torch.cuda.is_available()

    if valid_tensor and is_xpu:
        current_device = torch.xpu.current_device()
        return device_index == current_device

    elif valid_tensor and cuda_available and tensor.is_cuda:
        current_device = torch.cuda.current_device()
        return device_index == current_device

    return valid_tensor


def form_update_tensor(
    optimizer: optim.Optimizer, parameters: list[torch.Tensor], parameter_group: dict[str, Any]
) -> None | torch.Tensor:
    """
    :param optimizer: Optimizer to form the update tensor from.
    :param parameters: Parameters to create the update tensor from.
    :param parameter_group: Parameter group within the optimizer the given parameters came from.
    :return: None or the formed update tensor.
    """

    if type(optimizer) in optim_utils.ADAM_OPTIMISERS:
        updates_list = [optimizer.state[p][EXP_AVERAGE].view(-1) for p in parameters if tensor_on_local_rank(p)]
        return torch.cat(updates_list) if updates_list else None

    elif type(optimizer) in optim_utils.SGD_OPTIMISERS:
        return optim_utils.compute_sgd_optimizer_update_stats(
            optimizer=optimizer, parameter_group=parameter_group, parameters=parameters
        )

    else:
        raise NotImplementedError(f"Optimizer {type(optimizer).__name__} is not supported!")


def null_standardizer(value_to_standardize: float, **kwargs) -> float:
    """
    :param value_to_standardize: Value to mock the standardization of.
    :return: Given value to standardize.
    """

    return value_to_standardize


def create_sinusoidal_depth_encoding(
    agent_controlled_modules: list[str], parameter_group_name: str, dimensionality: int
) -> list[int | float]:
    """
    :param agent_controlled_modules: Ordered list of parameter group names in the inner model.
    :param parameter_group_name: Name of the parameter group to create a depth encoding for.
    :param dimensionality: Length of the depth vector.
    :return: Sinusoidal depth encoding.
    """

    assert dimensionality % 2 == 0, "Dimensionality of a sinusoidal depth encoding must be even."

    depth = agent_controlled_modules.index(parameter_group_name)

    positions = np.arange(dimensionality // 2)
    frequencies = 1 / (10000 ** (2 * positions / dimensionality))

    encoding = np.zeros(dimensionality)
    encoding[0::2] = np.sin(depth * frequencies)
    encoding[1::2] = np.cos(depth * frequencies)

    vector = encoding.tolist()

    return vector


def concatenate_lists(lists: list[list[Any]]) -> list[Any]:
    """
    :param lists: Lists to concatenate.
    :return: Concatenated lists.
    """

    return list(chain(*lists))


def compute_cdf_weighted_mean_and_std(
    time_series: list[tuple[float, float]], decay_factor: float
) -> tuple[float, float]:
    """
    Compute the CDF-weighted standard deviation using the same exponential decay weights
    as the mean calculation, with numerical integration.

    :param time_series: List of (time, value) pairs
    :param decay_factor: Decay factor b in the exponential weight formula b in [1.25, 2.5, 5, 10, 20]
    :return: Tuple of (weighted mean, weighted standard deviation)
    """

    if len(time_series) == 0:
        return 0.0, 0.0

    if len(time_series) == 1:
        return time_series[0][1], 0.0

    sorted_series = sorted(time_series, key=lambda x: x[0])

    # Handle the special case when decay_factor = 1.0
    if abs(decay_factor - 1.0) < MIN_DECAY_FACTOR:
        # When decay_factor = 1.0, w(t) = 1 for all t
        # So the result is just the arithmetic mean
        values = [v for _, v in sorted_series]
        mean = float(np.mean(values))
        std = float(np.std(values))
        return mean, std

    log_decay_factor = math.log(decay_factor)

    total_weight = 0.0  # ∫ w(t) dt - total weight across all time intervals
    total_weighted_value = 0.0  # ∫ w(t) y(t) dt - total weighted value
    total_weighted_squared = 0.0  # ∫ w(t) y(t)² dt - total weighted squared value

    for time_series_index in range(len(sorted_series) - 1):
        start_time_point = sorted_series[time_series_index][0]
        end_time_point = sorted_series[time_series_index + 1][0]
        start_value = sorted_series[time_series_index][1]
        end_value = sorted_series[time_series_index + 1][1]

        time_interval = end_time_point - start_time_point
        assert time_interval > 0, "Time interval must be positive"

        interval_value = _weighted_interval_expectation(
            start_time_point=start_time_point,
            start_value=start_value,
            end_time_point=end_time_point,
            end_value=end_value,
            log_decay_factor=log_decay_factor,
        )
        interval_squared_value = _weighted_interval_expectation(
            start_time_point=start_time_point,
            start_value=start_value**2,
            end_time_point=end_time_point,
            end_value=end_value**2,
            log_decay_factor=log_decay_factor,
        )

        total_weighted_value += interval_value
        total_weighted_squared += interval_squared_value

    total_weight = (1 / log_decay_factor) * (
        math.exp(log_decay_factor * sorted_series[-1][0]) - math.exp(log_decay_factor * sorted_series[0][0])
    )
    # Check if total weight is too small (numerical stability)
    if total_weight < MIN_TOTAL_WEIGHT:
        values = [v for _, v in sorted_series]
        mean = float(np.mean(values))
        std = float(np.std(values))
        return mean, std

    # Calculate weighted mean: μ = ∫ w(t) y(t) dt / ∫ w(t) dt
    # This gives us the expected value under the weight distribution
    weighted_mean = float(total_weighted_value / total_weight)

    # Calculate weighted variance: Var = ∫ w(t) y(t)² dt / ∫ w(t) dt - μ²
    # This follows from the definition: Var(X) = E[X²] - (E[X])²
    # where E[X] = ∫ w(t) y(t) dt / ∫ w(t) dt and E[X²] = ∫ w(t) y(t)² dt / ∫ w(t) dt
    weighted_variance = float(total_weighted_squared / total_weight - weighted_mean**2)

    # Calculate weighted standard deviation: σ = √Var
    # This is the square root of the variance, representing the spread of values
    weighted_std = float(math.sqrt(max(0, weighted_variance)))

    return weighted_mean, weighted_std


def _weighted_interval_expectation(
    start_time_point: float,
    start_value: float,
    end_time_point: float,
    end_value: float,
    log_decay_factor: float,
) -> float:
    """
    Computes the weighted interval expectation from Appendix E of the LHOPT paper.

    :param start_time_point: the start time value of the interval.
    :param start_value: the value at start_time_point.
    :param end_time_point: the end time value of the interval.
    :param end_value: the value at end_time_point.
    :param log_decay_factor: the logarithm of the decay factor used to weight the expectation.
    :return: the exponentially-weighted expectation of the linear interpolation between the start and end points.
    """

    interval_gradient = (end_value - start_value) / (end_time_point - start_time_point)
    start_exp_time = math.exp(log_decay_factor * start_time_point)
    end_exp_time = math.exp(log_decay_factor * end_time_point)
    return (1 / log_decay_factor) * (end_value * end_exp_time - start_value * start_exp_time) - (
        1 / log_decay_factor**2
    ) * interval_gradient * (end_exp_time - start_exp_time)


def compute_cdf_feature(
    current_value: float,
    time_series: list[tuple[float, float]],
    decay_factor: float,
    current_time: float,
    time_window: int,
) -> float:
    """

    This function computes a CDF feature that represents the cumulative probability
    of the current value given the historical distribution, weighted by time decay.
    Uses scipy.stats.norm.cdf with loc (mean) and scale (std) computed from CDF utilities.

    The mean and std formula from the OpenAI paper:
    https://arxiv.org/pdf/2305.18290.pdf


    :param current_value: Current value to compute CDF feature for
    :param time_series: List of (time, value) pairs for CDF calculation. time_series will be updated in-place each time this function is called.
    :param decay_factor: Decay factor for CDF calculation (0 < factor < 1)
    :param current_time: Current time step
    :param time_window: Maximum number of time steps to keep in time series
    :return: CDF feature value (cumulative probability from normal distribution)
    """
    # Add current observation to time series
    time_series.append((current_time, current_value))

    # Keep only the last time_window observations
    if len(time_series) > time_window:
        time_series[:] = time_series[-time_window:]

    # If we don't have enough data, return 0.0
    if len(time_series) < 2:
        return 0.0

    # Compute CDF-weighted mean (loc) and standard deviation (scale)
    cdf_mean, cdf_std = compute_cdf_weighted_mean_and_std(time_series, decay_factor)

    # Compute CDF feature using scipy.stats.norm.cdf
    if cdf_std > 0:
        # Use norm.cdf with loc=cdf_mean and scale=cdf_std
        cdf_feature = norm.cdf(current_value, loc=cdf_mean, scale=cdf_std)
        return cdf_feature
    else:
        # If the standard deviation is 0, return 0.0
        return 0.0
