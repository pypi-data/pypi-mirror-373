# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

import random
import secrets

import numpy as np
import torch

# ======================================================================================================================
#
# FUNCTIONS
#
# ======================================================================================================================


def generate_true_random_seed(num_bits: int = 30) -> int:
    """
    :param num_bits: Number of bits to use in the random seed.
    :return: Truly random seed.
    """

    return secrets.randbits(k=num_bits)


def generate_random_seed(num_bits: int = 32, seed: int | None = None) -> int:
    """
    :param num_bits: Number of bits to use in the random seed.
    :param seed: Random seed used to generate the random seed in order to maintain consistency between developers.
    :return: Truly random seed.
    """

    if seed is not None:
        random.seed(seed)

    return random.getrandbits(num_bits)


def set_all_seeds(seed: int) -> None:
    """
    :param seed: Random seed to use for random, numpy, torch, CUDA and CUDNN.
    """

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
