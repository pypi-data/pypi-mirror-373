# ======================================================================================================================
#
# CONSTANTS
#
# ======================================================================================================================

KEY_HEADER_CASE = "X-API-Key"
KEY_HEADER_NO_CASE = KEY_HEADER_CASE.lower()

TIMESTAMP_FORMAT = "%Y-%m-%d-%H-%M-%S"

RLLIB_TRUNC_EPISODES = "truncate_episodes"
RLLIB_COMP_EPISODES = "complete_episodes"

LEARNING_RATE = "learning_rate"
WEIGHT_DECAY = "weight_decay"
DROPOUT = "dropout"
GRAD_NORM_CLIP = "grad_norm_clip"
ADAM_BETA_ONE = "adam_beta_one"
ADAM_BETA_TWO = "adam_beta_two"
ADAM_EPS = "adam_eps"
SGD_MOMENTUM = "sgd_momentum"
BATCH_SIZE = "batch_size"
GRADIENT_ACCUMULATION = "gradient_accumulation"
EPOCHS = "epochs"
TOKENS = "tokens"
SAMPLES = "samples"

PARAMS = "params"

SCHEDULER_GROUP_NAME = "inephany_parameter_group_name"

AGENT_PREFIX_LR = "lr"
AGENT_PREFIX_WD = "weight-decay"
AGENT_PREFIX_DROPOUT = "dropout"
AGENT_PREFIX_CLIPPING = "grad-norm-clip"

AGENT_PREFIX_BETA_ONE = "adam-beta-one"
AGENT_PREFIX_BETA_TWO = "adam-beta-two"
AGENT_PREFIX_EPS = "adam-eps"

AGENT_PREFIX_SGD_MOMENTUM = "sgd-momentum"

AGENT_BATCH_SIZE = "batch-size"
AGENT_GRADIENT_ACCUMULATION = "gradient-accumulation"

AGENT_BANDIT_SUFFIX = "bandit-agent"

AGENT_TYPES = [
    LEARNING_RATE,
    WEIGHT_DECAY,
    DROPOUT,
    GRAD_NORM_CLIP,
    ADAM_BETA_ONE,
    ADAM_BETA_TWO,
    ADAM_EPS,
    SGD_MOMENTUM,
    GRADIENT_ACCUMULATION,
]
SUFFIXES = [AGENT_BANDIT_SUFFIX]
PREFIXES = [
    AGENT_PREFIX_LR,
    AGENT_PREFIX_WD,
    AGENT_PREFIX_DROPOUT,
    AGENT_PREFIX_CLIPPING,
    AGENT_PREFIX_BETA_ONE,
    AGENT_PREFIX_BETA_TWO,
    AGENT_PREFIX_EPS,
    AGENT_PREFIX_SGD_MOMENTUM,
    AGENT_GRADIENT_ACCUMULATION,
]
PREFIXES_TO_HPARAMS = {
    AGENT_PREFIX_LR: LEARNING_RATE,
    AGENT_PREFIX_WD: WEIGHT_DECAY,
    AGENT_PREFIX_DROPOUT: DROPOUT,
    AGENT_PREFIX_CLIPPING: GRAD_NORM_CLIP,
    AGENT_PREFIX_BETA_ONE: ADAM_BETA_ONE,
    AGENT_PREFIX_BETA_TWO: ADAM_BETA_TWO,
    AGENT_PREFIX_EPS: ADAM_EPS,
    AGENT_PREFIX_SGD_MOMENTUM: SGD_MOMENTUM,
    AGENT_GRADIENT_ACCUMULATION: GRADIENT_ACCUMULATION,
}
HPARAMS_TO_PREFIXES = {hparam: prefix for prefix, hparam in PREFIXES_TO_HPARAMS.items()}
