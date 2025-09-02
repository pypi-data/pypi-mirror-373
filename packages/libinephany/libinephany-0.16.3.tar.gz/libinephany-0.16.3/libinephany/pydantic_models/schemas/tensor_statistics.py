# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

import torch
from pydantic import BaseModel

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class TensorStatistics(BaseModel):

    norm_: float = 0.0
    mean_: float = 0.0
    median_: float = 0.0
    variance_: float = 0.0
    tenth_percentile_: float = 0.0
    ninetieth_percentile_: float = 0.0
    inter_quartile_range_: float = 0.0

    @property
    def norm(self) -> float:
        """
        :return: Tensor norm.
        """

        return self.norm_

    @norm.setter
    def norm(self, tensor: torch.Tensor) -> None:
        """
        :param tensor: Tensor to compute the norm from.
        """

        self.norm_ = torch.norm(tensor, p=2).item()

    @property
    def mean(self) -> float:
        """
        :return: Tensor mean.
        """

        return self.mean_

    @mean.setter
    def mean(self, tensor: torch.Tensor) -> None:
        """
        :param tensor: Tensor to compute the mean from.
        """

        self.mean_ = tensor.mean().item()

    @property
    def median(self) -> float:
        """
        :return: Tensor median.
        """

        return self.median_

    @median.setter
    def median(self, tensor: torch.Tensor) -> None:
        """
        :param tensor: Tensor to compute the median from.
        """

        self.median_ = tensor.median().item()

    @property
    def variance(self) -> float:
        """
        :return: Tensor variance.
        """

        return self.variance_

    @variance.setter
    def variance(self, tensor: torch.Tensor) -> None:
        """
        :param tensor: Tensor to compute the variance from.
        """

        self.variance_ = tensor.var(unbiased=False).item()

    @property
    def tenth_percentile(self) -> float:
        """
        :return: Tensor tenth percentile.
        """

        return self.tenth_percentile_

    @tenth_percentile.setter
    def tenth_percentile(self, tensor: torch.Tensor) -> None:
        """
        :param tensor: Tensor to compute the tenth percentile from.
        """

        self.tenth_percentile_ = torch.quantile(tensor, 0.1).item()

    @property
    def ninetieth_percentile(self) -> float:
        """
        :return: Tensor ninetieth percentile.
        """

        return self.ninetieth_percentile_

    @ninetieth_percentile.setter
    def ninetieth_percentile(self, tensor: torch.Tensor) -> None:
        """
        :param tensor: Tensor to compute the ninetieth from.
        """

        self.ninetieth_percentile_ = torch.quantile(tensor, 0.9).item()

    @property
    def inter_quartile_range(self) -> float:
        """
        :return: Tensor inter-quartile range.
        """

        return self.inter_quartile_range_

    @inter_quartile_range.setter
    def inter_quartile_range(self, tensor: torch.Tensor) -> None:
        """
        :param tensor: Tensor to compute the inter-quartile range from.
        """

        self.inter_quartile_range_ = (torch.quantile(tensor, 0.75) - torch.quantile(tensor, 0.25)).item()

    @staticmethod
    def downsample_tensor(tensor: torch.Tensor, sample_percentage: float) -> torch.Tensor:
        """
        :param tensor: Tensor to downsample.
        :param sample_percentage: Percentage of the given tensor to randomly sample and compute statistics from.
        :return: Downsampled tensor.
        """

        if sample_percentage >= 1.0:
            return tensor

        input_size = tensor.numel()
        sample_size = max(int(input_size * sample_percentage), 1)

        random_indices = torch.randint(0, input_size, (sample_size,), device=tensor.device)
        tensor = tensor.view(-1)

        return tensor[random_indices]

    @classmethod
    def filter_skip_statistics(cls, skip_statistics: list[str] | None) -> list[str]:
        """
        :param skip_statistics: Names of the fields in the model to not include in returned observations.
        :return: Empty list if skip_statistics was None or skip_statistics filtered to include only the names of fields
        present in this pydantic model.
        """

        return (
            [skip_stat for skip_stat in skip_statistics if skip_stat in cls.model_fields.keys()]
            if skip_statistics is not None
            else []
        )

    @classmethod
    def build(
        cls, tensor: torch.Tensor, sample_percentage: float = 0.01, skip_statistics: list[str] | None = None
    ) -> "TensorStatistics":
        """
        :param tensor: Tensor to compute and store statistics of.
        :param sample_percentage: Percentage of the given tensor to randomly sample and compute statistics from.
        :param skip_statistics: If the observation uses the TensorStatistic model to return observations, names of the
        fields in the model to not include in returned observations.
        :return: Constructed tensor statistics.
        """

        stats = cls()
        downsampled_tensor = cls.downsample_tensor(tensor=tensor, sample_percentage=sample_percentage)

        for field, field_value in stats.model_dump().items():
            name = field[:-1] if field.endswith("_") else field

            if skip_statistics is not None and name in skip_statistics:
                continue

            setattr(stats, name, downsampled_tensor)

        return stats

    @classmethod
    def from_tensor(cls, tensor: torch.Tensor) -> "TensorStatistics":
        """
        :param tensor: Tensor to build the model from.
        :return: Reconstructed model.
        """

        return cls(
            norm_=tensor[0],
            mean_=tensor[1],
            median_=tensor[2],
            variance_=tensor[3],
            tenth_percentile_=tensor[4],
            ninetieth_percentile_=tensor[5],
            inter_quartile_range_=tensor[6],
        )

    def to_list(self, skip_statistics: list[str] | None) -> list[float]:
        """
        :param skip_statistics: None or a list of field names to skip from adding to the returned list.
        :return: List of field values.
        """

        if skip_statistics is None:
            skip_statistics = []

        if not all(skip_stat in self.model_fields.keys() for skip_stat in skip_statistics):
            raise ValueError(
                f"One or more skip statistic keys do not exist in TensorStatistics. Valid Skip Keys: "
                f"{list(self.model_fields.keys())} Given Skip Keys: {skip_statistics}"
            )

        as_list = []

        for field, field_value in self.model_dump().items():
            if field in skip_statistics:
                continue

            as_list.append(field_value)

        return as_list

    def to_tensor(self) -> torch.Tensor:
        """
        :return: Tensor with contents of the Pydantic model in a specific order.
        """

        return torch.tensor(
            [
                self.norm,
                self.mean,
                self.median,
                self.variance,
                self.tenth_percentile,
                self.ninetieth_percentile,
                self.inter_quartile_range,
            ]
        )
