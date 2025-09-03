# ======================================================================================================================
#
# GLOBAL OBSERVERS PACKAGE
#
# This package contains all global observer classes used for collecting observations
# across the entire training process, not specific to individual agents.
#
# ======================================================================================================================


from .gradient_observers import GlobalFirstOrderGradients, GlobalSecondOrderGradients
from .hyperparameter_observers import InitialHyperparameters, ModelFamilyOneHot, OptimizerTypeOneHot
from .loss_observers import (
    LHOPTLossRatio,
    LHOPTTrainingLoss,
    LHOPTValidationLoss,
    LossRatio,
    PercentileOfLossAtEachCheckpoint,
    TrainingLoss,
    TrainingScore,
    ValidationLoss,
    ValidationScore,
)
from .model_observers import (
    GlobalActivations,
    GlobalLAMBTrustRatio,
    GlobalParameters,
    GlobalParameterUpdates,
    NumberOfLayers,
    NumberOfParameters,
)
from .progress_observers import EpochsCompleted, ProgressAtEachCheckpoint, TrainingProgress

__all__ = [
    InitialHyperparameters.__name__,
    OptimizerTypeOneHot.__name__,
    ModelFamilyOneHot.__name__,
    TrainingLoss.__name__,
    ValidationLoss.__name__,
    LossRatio.__name__,
    TrainingScore.__name__,
    ValidationScore.__name__,
    GlobalFirstOrderGradients.__name__,
    GlobalSecondOrderGradients.__name__,
    GlobalActivations.__name__,
    GlobalParameterUpdates.__name__,
    GlobalParameters.__name__,
    GlobalLAMBTrustRatio.__name__,
    NumberOfParameters.__name__,
    NumberOfLayers.__name__,
    TrainingProgress.__name__,
    EpochsCompleted.__name__,
    ProgressAtEachCheckpoint.__name__,
    LHOPTTrainingLoss.__name__,
    LHOPTValidationLoss.__name__,
    LHOPTLossRatio.__name__,
    PercentileOfLossAtEachCheckpoint.__name__,
]
