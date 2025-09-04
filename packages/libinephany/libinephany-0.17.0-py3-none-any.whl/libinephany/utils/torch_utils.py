# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

import torch.nn as nn
from torch.optim import Optimizer
from torch.optim.lr_scheduler import LRScheduler
from transformers.activations import ACT2CLS

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class NoOpLRScheduler(LRScheduler):
    """
    A learning rate scheduler that does nothing - preserves the current learning rates.
    This effectively disables any learning rate scheduling while preserving any
    modifications made to the learning rates by agents or other means.
    """

    def __init__(self, optimizer: Optimizer, last_epoch: int = -1) -> None:
        """
        :param optimizer: Optimizer which handles gradient descent.
        :param last_epoch: Epoch at which this scheduler was initialised.
        """
        super().__init__(optimizer=optimizer, last_epoch=last_epoch)

    def get_lr(self) -> list[float]:  # type: ignore
        """
        :return: The current learning rates of the parameter groups exactly as they are.
        This preserves any modifications made by agents or other means.
        """
        return [group["lr"] for group in self.optimizer.param_groups]


# ======================================================================================================================
#
# CONSTANTS
#
# ======================================================================================================================

PYTORCH_ACTIVATIONS = [
    nn.ReLU.__name__,
    nn.LeakyReLU.__name__,
    nn.PReLU.__name__,
    nn.ReLU6.__name__,
    nn.SELU.__name__,
    nn.CELU.__name__,
    nn.GELU.__name__,
    nn.Sigmoid.__name__,
    nn.Tanh.__name__,
    nn.Hardtanh.__name__,
    nn.Softplus.__name__,
    nn.Softshrink.__name__,
    nn.Softsign.__name__,
    nn.ELU.__name__,
    nn.LogSigmoid.__name__,
    nn.Hardsigmoid.__name__,
    nn.Hardswish.__name__,
    nn.Hardshrink.__name__,
    nn.SiLU.__name__,
    nn.Mish.__name__,
    nn.Softmin.__name__,
    nn.Softmax.__name__,
    nn.LogSoftmax.__name__,
    nn.Tanhshrink.__name__,
]
HUGGINGFACE_ACTIVATIONS = [
    activation.__name__ if not isinstance(activation, tuple) else activation[0].__name__  # type: ignore
    for activation in ACT2CLS.values()
]
ACTIVATIONS = PYTORCH_ACTIVATIONS + HUGGINGFACE_ACTIVATIONS
