# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

import math
from abc import ABC, abstractmethod
from typing import Any, Callable, final

import torch
import torch.distributed as dist
import torch.nn as nn
import torch.optim as optim
from torch.distributed import ReduceOp

from libinephany.observations import observation_utils
from libinephany.observations.observation_utils import StatisticStorageTypes
from libinephany.pydantic_models.schemas.tensor_statistics import TensorStatistics
from libinephany.utils import torch_distributed_utils
from libinephany.utils.constants import PARAMS, SCHEDULER_GROUP_NAME
from libinephany.utils.torch_distributed_utils import MASTER_SCHEDULER_RANK
from libinephany.utils.torch_utils import ACTIVATIONS

# ======================================================================================================================
#
# CONSTANTS
#
# ======================================================================================================================

StatisticsStorage = list[torch.Tensor] | list[TensorStatistics] | list[float]

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class Statistic(ABC):

    def __init__(
        self,
        *,
        parameter_group_name: str,
        averaging_function: Callable[[list[float]], float],
        agent_modules: dict[str, str],
        max_statistic_cache_size: int = 3,
        tensor_stats_downsample_percentage: float = 0.01,
        statistic_sample_frequency: int = 10,
        **kwargs,
    ) -> None:
        """
        :param parameter_group: Name of the parameter group to gather statistics from.
        :param averaging_function: Averaging function to apply over the metrics.
        :param agent_modules: Dictionary mapping agent controlled module names to the type of module being controlled.
        :param max_statistic_cache_size: Maximum number of tensors to store internally before processing the tensors
        into statistics.
        :param tensor_stats_downsample_percentage: Percentage of elements of the tensors from the model to randomly
        sample to compute the statistics from.
        :param statistic_sample_frequency: How frequently to cache tensors from the model for later statistic
        computation.
        :param kwargs: Other observation keyword arguments.
        """

        self._tensor_cache: list[torch.Tensor] = []
        self._data: StatisticsStorage = []

        self._averaging_function = averaging_function
        self._sample_number = 0

        self.parameter_group_name = parameter_group_name
        self.agent_modules = agent_modules
        self.max_cache_size = max_statistic_cache_size
        self.downsample_percent = tensor_stats_downsample_percentage
        self.sample_frequency = statistic_sample_frequency
        self.skip_statistics: list[str] | None = None

    @final
    @property
    def tracker_name(self) -> str:
        """
        :return: Name of the tracker.
        """

        return f"{self.__class__.__name__}-{self.parameter_group_name}"

    @final
    @property
    def storage_format(self) -> StatisticStorageTypes:
        """
        :return: Storage format this observation stores data in. Must be one of the enum attributes in the
        StatisticStorageTypes enumeration class.
        """

        storage_format = self._get_storage_format()

        if storage_format in StatisticStorageTypes:
            return storage_format

        raise ValueError(
            f"The type of storage format statistic trackers should return must be in the "
            f"{StatisticStorageTypes.__name__} enumeration class. {storage_format} is not and so "
            f"{self.__class__.__name__} is invalid!"
        )

    @property
    def uses_forward_hook(self) -> bool:
        """
        :return: Whether this local observation relies on PyTorch's register_forward_hook.
        """

        return False

    @property
    def requires_gradient_graphs(self) -> bool:
        """
        :return: Whether the tracker requires gradient graphs to be retained.
        """

        return False

    @property
    def hook_module_type_names(self) -> list[str]:
        """
        :return: Names of the module types to hook the observation into.
        """

        raise NotImplementedError

    def _get_forward_hook(self) -> Callable[[nn.Module, torch.Tensor, torch.Tensor], None]:
        """
        :return: Forward hook to register the function with.
        """

        raise NotImplementedError

    @abstractmethod
    def _gather(
        self,
        *,
        optimizer: optim.Optimizer,
        model: nn.Module,
        parameters: list[torch.Tensor],
        parameter_group: dict[str, Any],
    ) -> torch.Tensor | TensorStatistics | float | None:
        """
        :param optimizer: Optimizer the given parameters and parameter group came from.
        :param model: Inner model to gather statistics from.
        :param parameters: List of parameters to gather statistics from.
        :return: None, TensorStatistics model or a float.
        """

        raise NotImplementedError

    @abstractmethod
    def _get_storage_format(self) -> StatisticStorageTypes:
        """
        :return: Storage format this observation stores data in. Must be one of the enum attributes in the
        StatisticStorageTypes enumeration class.
        """

        raise NotImplementedError

    @staticmethod
    def _get_parameters(parameter_group: dict[str, Any]) -> list[torch.Tensor]:
        """
        :param parameter_group: Parameter group to extract parameter tensors and name from.
        :return: List of the parameter tensors for the given parameter group.
        """

        return [p for p in parameter_group[PARAMS] if p.requires_grad]

    def _find_parameter_group(self, optimizer: optim.Optimizer) -> dict[str, Any]:
        """
        :param optimizer: Optimizer storing references to all parameter groups in the (possibly) distributed model.
        :return: Parameter group corresponding to the parameter group named by the parameter_group_name instance
        variable.
        :raises KeyError: If a parameter group with the stored parameter_group_name could not be found in the optimizer.
        """

        for param_group in optimizer.param_groups:
            if SCHEDULER_GROUP_NAME in param_group:
                group_name = param_group[SCHEDULER_GROUP_NAME]

                if group_name == self.parameter_group_name:
                    return param_group

        raise KeyError(f"Could not find parameter group with name {self.parameter_group_name}.")

    def _process_tensor_cache(self) -> None:
        """
        Processes the tensor cache to build a TensorStatistic model.
        """

        if self._tensor_cache:
            concatenated = torch.cat(self._tensor_cache)
            self._tensor_cache = []

            statistics = TensorStatistics.build(
                tensor=concatenated, skip_statistics=self.skip_statistics, sample_percentage=self.downsample_percent
            )
            self._data.append(statistics)  # type: ignore

    @staticmethod
    @final
    def _determine_reduction_shape(statistic: torch.Tensor | TensorStatistics | float | None) -> list[int] | None:
        """
        :param statistic: Statistic to get the shape for as defined by the master rank.
        :return: Shape of the statistic according to the master rank.
        """

        shape = None

        if torch_distributed_utils.is_scheduler_master_rank():
            if isinstance(statistic, torch.Tensor):
                shape = statistic.view(-1).shape

            elif isinstance(statistic, TensorStatistics):
                shape = statistic.to_tensor().view(-1).shape

            elif statistic is not None:
                shape = torch.tensor([statistic]).shape

        broadcasted_shape = list(shape) if shape is not None else None
        broadcasted_shape = torch_distributed_utils.broadcast_data(data=broadcasted_shape)

        return broadcasted_shape

    @final
    def _distributed_reduce(
        self, statistic: torch.Tensor | TensorStatistics | float | None
    ) -> torch.Tensor | TensorStatistics | float | None:
        """
        :param statistic: Statistic to reduce across all distributed ranks. This can be a Torch tensor, a float or a
        TensorStatistics object.
        :return: None if this rank is not the master rank or the reduced statistic if it is.
        """

        if not torch_distributed_utils.is_distributed():
            return statistic

        shape = self._determine_reduction_shape(statistic=statistic)

        if statistic is None:
            to_reduce = torch.zeros(shape, dtype=torch.float64)

        elif isinstance(statistic, torch.Tensor):
            to_reduce = statistic.clone().to(torch.float64).view(-1)

        elif isinstance(statistic, TensorStatistics):
            to_reduce = statistic.to_tensor().to(torch.float64).view(-1)

        else:
            to_reduce = torch.tensor([statistic], dtype=torch.float64)

        to_reduce = to_reduce.to(torch_distributed_utils.get_local_device())
        dist.reduce(to_reduce, dst=MASTER_SCHEDULER_RANK, op=ReduceOp.SUM)

        if not torch_distributed_utils.is_scheduler_master_rank():
            return None

        if isinstance(statistic, TensorStatistics):
            return TensorStatistics.from_tensor(tensor=to_reduce)

        elif statistic is not None and not isinstance(statistic, torch.Tensor):
            return to_reduce.item()

        return to_reduce

    @final
    def gather(
        self,
        *,
        optimizer: optim.Optimizer,
        model: nn.Module,
    ) -> None:
        """
        :param optimizer: Optimizer the given parameters and parameter group came from.
        :param model: Inner model to gather statistics from.
        """

        parameter_group = self._find_parameter_group(optimizer=optimizer)
        parameters = self._get_parameters(parameter_group=parameter_group)

        if self._sample_number % self.sample_frequency == 0:
            statistic = self._gather(
                optimizer=optimizer, model=model, parameters=parameters, parameter_group=parameter_group
            )

            statistic = self._distributed_reduce(statistic=statistic)

            if torch_distributed_utils.is_scheduler_master_rank():
                if isinstance(statistic, torch.Tensor):
                    statistic = statistic.view(-1)
                    self._tensor_cache.append(statistic)

                    if len(self._tensor_cache) >= self.max_cache_size:
                        self._process_tensor_cache()

                elif statistic is not None:
                    self._data.append(statistic)  # type: ignore

        self._sample_number += 1

    @final
    def fetch(self) -> TensorStatistics | float | None:
        """
        :return: None if this method is called on a rank other than the master rank otherwise a dictionary mapping
        parameter group names to TensorStatistic models or floats.
        """

        if not torch_distributed_utils.is_scheduler_master_rank():
            return None

        if self.storage_format is StatisticStorageTypes.TENSOR_STATISTICS:
            self._process_tensor_cache()

            results = observation_utils.apply_averaging_function_to_tensor_statistics(
                tensor_statistics=self._data, averaging_function=self._averaging_function  # type: ignore
            )

        elif self.storage_format is StatisticStorageTypes.FLOAT:
            results = self._averaging_function(self._data)  # type: ignore

        else:
            raise ValueError(f"Data storage type {self.storage_format} is invalid!")

        self.reset()

        return results  # type: ignore

    @final
    def register(self, model: nn.Module) -> None:
        """
        :param model: Model to register the hooks with.
        """

        if not self.uses_forward_hook:
            raise RuntimeError(
                f"The LocalObservation {self.__class__.__name__} does not use forward hooks. The register method should"
                f"not have been called!"
            )

        for name, module in model.named_modules():
            if self.parameter_group_name not in name:
                continue

            if module.__class__.__name__ not in self.hook_module_type_names:
                continue

            module.register_forward_hook(self._get_forward_hook())

    def reset(self) -> None:
        """
        Clears any internal states.
        """

        self._tensor_cache = []
        self._data = []
        self._sample_number = 0


class FirstOrderGradients(Statistic):

    def __init__(
        self,
        *,
        skip_statistics: list[str] | None = None,
        **kwargs,
    ) -> None:
        """
        :param skip_statistics: If the observation uses the TensorStatistic model to return observations, names of the
        fields in the model to not include in returned observations.
        :param kwargs: Other observation keyword arguments.
        """

        super().__init__(**kwargs)

        self.skip_statistics = skip_statistics

    def _get_storage_format(self) -> StatisticStorageTypes:
        """
        :return: Storage format this observation stores data in. Must be one of the enum attributes in the
        StatisticStorageTypes enumeration class.
        """

        return StatisticStorageTypes.TENSOR_STATISTICS

    def _gather(
        self,
        *,
        optimizer: optim.Optimizer,
        model: nn.Module,
        parameters: list[torch.Tensor],
        parameter_group: dict[str, Any],
    ) -> torch.Tensor | TensorStatistics | float | None:
        """
        :param optimizer: Optimizer the given parameters and parameter group came from.
        :param model: Inner model to gather statistics from.
        :param parameters: List of parameters to gather statistics from.
        :param parameter_group: Parameter group the parameters originate from.
        :return: None, TensorStatistics model or a float.
        """

        gradients = [
            p.grad.view(-1) for p in parameters if observation_utils.tensor_on_local_rank(p) and p.grad is not None
        ]

        if not gradients:
            return None

        stacked_grads = torch.cat(gradients)

        return stacked_grads


class SecondOrderGradients(Statistic):

    def __init__(
        self,
        *,
        compute_hessian_diagonal: bool = False,
        skip_statistics: list[str] | None = None,
        **kwargs,
    ) -> None:
        """
        :param compute_hessian_diagonal: Whether to compute the Hessian diagonal to determine second order gradients
        or use the squared first order gradients as approximations in the same way Adam does.
        :param skip_statistics: If the observation uses the TensorStatistic model to return observations, names of the
        fields in the model to not include in returned observations.
        :param kwargs: Other observation keyword arguments.
        """

        super().__init__(**kwargs)

        self.compute_hessian_diagonal = compute_hessian_diagonal
        self.skip_statistics = skip_statistics

    @property
    def requires_gradient_graphs(self) -> bool:
        """
        :return: Whether the statistic requires gradient graphs to be retained.
        """

        return self.compute_hessian_diagonal

    def _get_storage_format(self) -> StatisticStorageTypes:
        """
        :return: Storage format this observation stores data in. Must be one of the enum attributes in the
        StatisticStorageTypes enumeration class.
        """

        return StatisticStorageTypes.TENSOR_STATISTICS

    @staticmethod
    def compute_hessian_diagonals(parameters: list[torch.Tensor]) -> torch.Tensor:
        """
        :param parameters: Parameters to compute the hessian diagonal matrices for.
        :return: Tensor containing the hessian diagonal matrices for all given parameters.
        """

        hessian_diagonals = []

        for parameter in parameters:
            if parameter.grad is not None:
                so_gradient = torch.autograd.grad(
                    outputs=parameter.grad.clone(),
                    inputs=parameter,
                    grad_outputs=torch.ones_like(parameter.grad, requires_grad=True),
                    only_inputs=True,
                    retain_graph=True,
                    create_graph=True,
                    allow_unused=True,
                )[0]

                if so_gradient is not None:
                    hessian_diagonals.append(so_gradient.view(-1))
                else:
                    hessian_diagonals.append(torch.zeros_like(parameter.view(-1)))

        return torch.cat(hessian_diagonals)

    def _gather(
        self,
        *,
        optimizer: optim.Optimizer,
        model: nn.Module,
        parameters: list[torch.Tensor],
        parameter_group: dict[str, Any],
    ) -> torch.Tensor | TensorStatistics | float | None:
        """
        :param optimizer: Optimizer the given parameters and parameter group came from.
        :param model: Inner model to gather statistics from.
        :param parameters: List of parameters to gather statistics from.
        :param parameter_group: Parameter group the parameters originate from.
        :return: None, TensorStatistics model or a float.
        """

        fo_gradients = [
            p.grad.view(-1) for p in parameters if observation_utils.tensor_on_local_rank(p) and p.grad is not None
        ]

        if not fo_gradients:
            return None

        if self.compute_hessian_diagonal:
            so_grad_tensor = self.compute_hessian_diagonals(parameters=parameters)

        else:
            so_grad_tensor = torch.cat(fo_gradients) ** 2

        return so_grad_tensor


class ActivationStatistics(Statistic):

    def __init__(
        self,
        *,
        skip_statistics: list[str] | None = None,
        **kwargs,
    ) -> None:
        """
        :param skip_statistics: If the observation uses the TensorStatistic model to return observations, names of the
        fields in the model to not include in returned observations.
        :param kwargs: Other observation keyword arguments.
        """

        super().__init__(**kwargs)

        self.skip_statistics = skip_statistics

    @property
    def uses_forward_hook(self) -> bool:
        """
        :return: Whether this local observation relies on PyTorch's register_forward_hook.
        """

        return True

    @property
    def hook_module_type_names(self) -> list[str]:
        """
        :return: Names of the module types to hook the observation into.
        """

        return ACTIVATIONS

    def _get_forward_hook(self) -> Callable[[nn.Module, torch.Tensor, torch.Tensor], None]:
        """
        :return: Forward hook to register the function with.
        """

        def hook(module: nn.Module, layer_input: torch.Tensor, layer_output: torch.Tensor) -> None:
            """
            :param module: Module the hook was registered with. Not used here.
            :param layer_input: Input to the module. Not used here.
            :param layer_output: Output of the module.
            """

            if self._sample_number % self.sample_frequency == 0:
                statistics = TensorStatistics.build(
                    tensor=layer_output, skip_statistics=self.skip_statistics, sample_percentage=self.downsample_percent
                )
                self._data.append(statistics)  # type: ignore

            self._sample_number += 1

        return hook

    def _get_storage_format(self) -> StatisticStorageTypes:
        """
        :return: Storage format this observation stores data in. Must be one of the enum attributes in the
        StatisticStorageTypes enumeration class.
        """

        return StatisticStorageTypes.TENSOR_STATISTICS

    def _gather(
        self,
        *,
        optimizer: optim.Optimizer,
        model: nn.Module,
        parameters: list[torch.Tensor],
        parameter_group: dict[str, Any],
    ) -> torch.Tensor | TensorStatistics | float | None:
        """
        :param optimizer: Optimizer the given parameters and parameter group came from.
        :param model: Inner model to gather statistics from.
        :param parameters: List of parameters to gather statistics from.
        :param parameter_group: Parameter group the parameters originate from.
        :return: None.
        """

        return None


class ParameterUpdateStatistics(Statistic):

    def __init__(
        self,
        *,
        skip_statistics: list[str] | None = None,
        **kwargs,
    ) -> None:
        """
        :param skip_statistics: If the observation uses the TensorStatistic model to return observations, names of the
        fields in the model to not include in returned observations.
        :param kwargs: Other observation keyword arguments.
        """

        super().__init__(**kwargs)

        self.skip_statistics = skip_statistics

    def _get_storage_format(self) -> StatisticStorageTypes:
        """
        :return: Storage format this observation stores data in. Must be one of the enum attributes in the
        StatisticStorageTypes enumeration class.
        """

        return StatisticStorageTypes.TENSOR_STATISTICS

    def _gather(
        self,
        *,
        optimizer: optim.Optimizer,
        model: nn.Module,
        parameters: list[torch.Tensor],
        parameter_group: dict[str, Any],
    ) -> torch.Tensor | TensorStatistics | float | None:
        """
        :param optimizer: Optimizer the given parameters and parameter group came from.
        :param model: Inner model to gather statistics from.
        :param parameters: List of parameters to gather statistics from.
        :param parameter_group: Parameter group the parameters originate from.
        :return: None, TensorStatistics model or a float.
        """

        update_tensor = observation_utils.form_update_tensor(
            optimizer=optimizer, parameters=parameters, parameter_group=parameter_group
        )

        if update_tensor is None:
            update_tensor = torch.cat([torch.zeros(p.view(-1).shape, device=p.device) for p in parameters])

        return update_tensor


class ParameterStatistics(Statistic):

    def __init__(
        self,
        *,
        skip_statistics: list[str] | None = None,
        **kwargs,
    ) -> None:
        """
        :param skip_statistics: If the observation uses the TensorStatistic model to return observations, names of the
        fields in the model to not include in returned observations.
        :param kwargs: Other observation keyword arguments.
        """

        super().__init__(**kwargs)

        self.skip_statistics = skip_statistics

    def _get_storage_format(self) -> StatisticStorageTypes:
        """
        :return: Storage format this observation stores data in. Must be one of the enum attributes in the
        StatisticStorageTypes enumeration class.
        """

        return StatisticStorageTypes.TENSOR_STATISTICS

    def _gather(
        self,
        *,
        optimizer: optim.Optimizer,
        model: nn.Module,
        parameters: list[torch.Tensor],
        parameter_group: dict[str, Any],
    ) -> torch.Tensor | TensorStatistics | float | None:
        """
        :param optimizer: Optimizer the given parameters and parameter group came from.
        :param model: Inner model to gather statistics from.
        :param parameters: List of parameters to gather statistics from.
        :param parameter_group: Parameter group the parameters originate from.
        :return: None, TensorStatistics model or a float.
        """

        return torch.cat([p.data.view(-1) for p in parameters if observation_utils.tensor_on_local_rank(p)])


class LAMBTrustRatioStatistics(Statistic):

    def __init__(
        self,
        *,
        use_log_transform: bool = False,
        **kwargs,
    ) -> None:
        """
        :param use_log_transform: Whether to transform the LAMB trust ratio by taking ln(1 + R).
        :param kwargs: Other observation keyword arguments.
        """

        super().__init__(**kwargs)

        self.use_log_transform = use_log_transform

    def _get_storage_format(self) -> StatisticStorageTypes:
        """
        :return: Storage format this observation stores data in. Must be one of the enum attributes in the
        StatisticStorageTypes enumeration class.
        """

        return StatisticStorageTypes.FLOAT

    def _gather(
        self,
        *,
        optimizer: optim.Optimizer,
        model: nn.Module,
        parameters: list[torch.Tensor],
        parameter_group: dict[str, Any],
    ) -> torch.Tensor | TensorStatistics | float | None:
        """
        :param optimizer: Optimizer the given parameters and parameter group came from.
        :param model: Inner model to gather statistics from.
        :param parameters: List of parameters to gather statistics from.
        :param parameter_group: Parameter group the parameters originate from.
        :return: None, TensorStatistics model or a float.
        """

        weights_list = [p.data.view(-1) for p in parameters if observation_utils.tensor_on_local_rank(p)]
        if weights_list:
            weights = torch.cat(weights_list)

        else:
            weights = None

        updates = observation_utils.form_update_tensor(
            optimizer=optimizer, parameters=parameters, parameter_group=parameter_group
        )

        update_norm = torch.norm(updates, p=2).item() if updates is not None else 0
        weight_norm = torch.norm(weights, p=2).item() if weights is not None else 0

        lamb_trust_ratio = 0.0
        if update_norm > 0:
            lamb_trust_ratio = weight_norm / update_norm

            if self.use_log_transform:
                lamb_trust_ratio = math.log(1 + lamb_trust_ratio)

        return lamb_trust_ratio


class NumberOfParameters(Statistic):

    def __init__(
        self,
        **kwargs,
    ) -> None:
        """
        :param kwargs: Other observation keyword arguments.
        """

        super().__init__(**kwargs)

        self._count: int | None = None

    def _get_storage_format(self) -> StatisticStorageTypes:
        """
        :return: Storage format this observation stores data in. Must be one of the enum attributes in the
        StatisticStorageTypes enumeration class.
        """

        return StatisticStorageTypes.FLOAT

    def _gather(
        self,
        *,
        optimizer: optim.Optimizer,
        model: nn.Module,
        parameters: list[torch.Tensor],
        parameter_group: dict[str, Any],
    ) -> torch.Tensor | TensorStatistics | float | None:
        """
        :param optimizer: Optimizer the given parameters and parameter group came from.
        :param model: Inner model to gather statistics from.
        :param parameters: List of parameters to gather statistics from.
        :param parameter_group: Parameter group the parameters originate from.
        :return: None, TensorStatistics model or a float.
        """

        if not torch_distributed_utils.is_scheduler_master_rank():
            return None

        if self._count is not None:
            return self._count

        count = sum(parameter.numel() for parameter in model.parameters())
        self._count = count

        return count


class NumberOfLayers(Statistic):

    def __init__(
        self,
        *,
        trainable_only: bool = False,
        **kwargs,
    ) -> None:
        """
        :param use_log_transform: Whether to transform the number of layers by ln(1 + N).
        :param trainable_only: Whether to only count trainable layers.
        :param kwargs: Other observation keyword arguments.
        """

        super().__init__(**kwargs)

        self._count: int | None = None

        self.trainable_only = trainable_only

    def _get_storage_format(self) -> StatisticStorageTypes:
        """
        :return: Storage format this observation stores data in. Must be one of the enum attributes in the
        StatisticStorageTypes enumeration class.
        """

        return StatisticStorageTypes.FLOAT

    def count_layers_recursively(self, module: nn.Module):
        """
        :param module: The PyTorch model or module to count the number of layers of.
        :return: Total count of layers matching the criteria.
        """

        count = 0

        for submodule in module.children():
            if not list(submodule.children()):
                if self.trainable_only:
                    if any(p.requires_grad for p in submodule.parameters()):
                        count += 1
                else:
                    count += 1

            else:
                count += self.count_layers_recursively(submodule)

        return count

    def _gather(
        self,
        *,
        optimizer: optim.Optimizer,
        model: nn.Module,
        parameters: list[torch.Tensor],
        parameter_group: dict[str, Any],
    ) -> torch.Tensor | TensorStatistics | float | None:
        """
        :param optimizer: Optimizer the given parameters and parameter group came from.
        :param model: Inner model to gather statistics from.
        :param parameters: List of parameters to gather statistics from.
        :param parameter_group: Parameter group the parameters originate from.
        :return: None, TensorStatistics model or a float.
        """

        if not torch_distributed_utils.is_scheduler_master_rank():
            return None

        if self._count is not None:
            return self._count

        count = self.count_layers_recursively(module=model)
        self._count = count

        return count
