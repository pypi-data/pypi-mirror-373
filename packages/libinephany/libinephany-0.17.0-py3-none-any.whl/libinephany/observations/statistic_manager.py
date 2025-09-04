# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

from collections import defaultdict
from typing import Any, Callable, DefaultDict

import torch
import torch.nn as nn
import torch.optim as optim

from libinephany.observations import observation_utils, statistic_trackers
from libinephany.observations.statistic_trackers import Statistic
from libinephany.pydantic_models.schemas.tensor_statistics import TensorStatistics
from libinephany.utils import torch_distributed_utils
from libinephany.utils.constants import PARAMS, SCHEDULER_GROUP_NAME

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class StatisticManager:

    def __init__(
        self,
        model: nn.Module,
        optimizer: optim.Optimizer,
        agent_modules: dict[str, str],
        can_nullify_gradients: bool = True,
        max_statistic_cache_size: int = 3,
        tensor_stats_downsample_percentage: float = 0.01,
        statistic_sample_frequency: int = 10,
    ) -> None:
        """
        :param model: Model to register forward hook trackers with.
        :param optimizer: Inner model optimizer which contains the parameter groups various metrics can be computed
        from.
        :param agent_modules: Dictionary mapping agent controlled module names to the type of module being controlled.
        :param can_nullify_gradients: Whether the manager can nullify the gradients after computing the various
        statistics. Clients can disable this if they need the gradients for further processing.
        :param max_statistic_cache_size: Maximum number of tensors to store internally before processing the tensors
        into statistics.
        :param tensor_stats_downsample_percentage: Percentage of elements of the tensors from the model to randomly
        sample to compute the statistics from.
        :param statistic_sample_frequency: How frequently to cache tensors from the model for later statistic
        computation.
        """

        self._required_trackers: dict[str, dict[str, Any] | None] | None = None

        self._trackers: dict[str, Statistic] = {}
        self.averaging_function = observation_utils.get_exponential_weighted_average  # Hard-coded for now.

        self.model = model
        self.optimizer = optimizer
        self.agent_modules = agent_modules
        self.can_nullify_gradients = can_nullify_gradients
        self.max_statistic_cache_size = max_statistic_cache_size
        self.tensor_stats_downsample_percentage = tensor_stats_downsample_percentage
        self.statistic_sample_frequency = statistic_sample_frequency

    @property
    def requires_gradient_graphs(self) -> bool:
        """
        :return: Whether the manager requires gradient graphs to be retained.
        """

        return any(tracker.requires_gradient_graphs for tracker in self._trackers.values())

    @staticmethod
    def _nullify_gradients(model: nn.Module) -> None:
        """
        :param model: Model to nullify the gradient of.
        """

        for parameter in model.parameters():
            parameter.grad = None

    @staticmethod
    def _clip_gradients(
        optimizer: optim.Optimizer,
        clipping_thresholds: DefaultDict[str, float],
        clipping_function: Callable[[list[torch.Tensor], float], None],
    ) -> None:
        """
        :param optimizer: Inner model optimizer which contains the parameter groups various metrics can be computed
        from.
        :param clipping_thresholds: Dictionary mapping parameter group names to gradient clipping thresholds for that
        parameter group.
        :param clipping_function: Function used to clip the gradients.
        """

        for parameter_group in optimizer.param_groups:
            parameter_group_name = parameter_group[SCHEDULER_GROUP_NAME]

            if parameter_group_name not in clipping_thresholds:
                continue

            clipping_threshold = clipping_thresholds[parameter_group_name]

            if clipping_threshold is None:
                continue

            clipping_function(parameter_group[PARAMS], clipping_threshold)

    def _iterate_trackers(
        self,
        optimizer: optim.Optimizer,
        model: nn.Module,
    ) -> None:
        """
        :param optimizer: Inner model optimizer which contains the parameter groups various metrics can be computed
        from.
        :param model: Inner model to gather statistics from.
        """

        tracker_order = None
        if torch_distributed_utils.is_scheduler_master_rank():
            tracker_order = list(self._trackers.keys())

        tracker_order = torch_distributed_utils.broadcast_data(data=tracker_order)

        for tracker_name in tracker_order:
            tracker = self._trackers[tracker_name]
            tracker.gather(optimizer=optimizer, model=model)

    def on_optimizer_step(
        self,
        *,
        clipping_function: Callable[[list[torch.Tensor], float], None] | None,
        clipping_thresholds: DefaultDict[str, float] | None = None,
    ) -> None:
        """
        :param clipping_function: Function used to clip the gradients.
        :param clipping_thresholds: Dictionary mapping parameter group names to gradient clipping thresholds for that
        parameter group.
        """

        if clipping_thresholds is not None and clipping_function is not None:
            self._clip_gradients(
                optimizer=self.optimizer, clipping_thresholds=clipping_thresholds, clipping_function=clipping_function
            )

        self._iterate_trackers(optimizer=self.optimizer, model=self.model)

        if self.can_nullify_gradients:
            self._nullify_gradients(model=self.model)

    def compile(self) -> dict[str, dict[str, float | TensorStatistics]] | None:
        """
        :return: Dictionary mapping statistic tracker class names to dictionaries mapping module names to floats or
        TensorStatistic models or None if the local rank is not the master rank.
        """

        if not torch_distributed_utils.is_scheduler_master_rank():
            return None

        compiled: DefaultDict[str, dict[str, float | TensorStatistics]] = defaultdict(dict)
        for tracker in self._trackers.values():
            data = tracker.fetch()
            compiled[tracker.__class__.__name__][tracker.parameter_group_name] = data

        return dict(compiled)

    def build_trackers(
        self,
        required_trackers: dict[str, dict[str, Any] | None] | None,
    ) -> None:
        """
        :param required_trackers: Dictionary mapping statistic tracker class names to kwargs for that class.
        """

        if required_trackers is not None:
            self._required_trackers = required_trackers

        if self._required_trackers is None:
            raise ValueError(
                f"{self.__class__.__name__} must be called with required_trackers not None at least once before trackers "
                f"can be constructed implicitly."
            )

        for required_tracker, tracker_kwargs in self._required_trackers.items():
            try:
                tracker_class: type[Statistic] = getattr(statistic_trackers, required_tracker)

            except AttributeError as e:
                raise AttributeError(f"Statistic tracker class {required_tracker} was not recognised!") from e

            if tracker_kwargs is None:
                tracker_kwargs = {}

            for parameter_group in self.optimizer.param_groups:
                if SCHEDULER_GROUP_NAME not in parameter_group:
                    continue

                parameter_group_name = parameter_group[SCHEDULER_GROUP_NAME]

                tracker = tracker_class(
                    parameter_group_name=parameter_group_name,
                    averaging_function=self.averaging_function,
                    agent_modules=self.agent_modules,
                    max_statistic_cache_size=self.max_statistic_cache_size,
                    tensor_stats_downsample_percentage=self.tensor_stats_downsample_percentage,
                    statistic_sample_frequency=self.statistic_sample_frequency,
                    **tracker_kwargs,
                )

                self._trackers[tracker.tracker_name] = tracker

                if tracker.uses_forward_hook:
                    tracker.register(model=self.model)

    def reset(self) -> None:
        """
        Resets internal state and rebuilds trackers for new model.
        """

        self._trackers = {}

        self.build_trackers(required_trackers=None)
