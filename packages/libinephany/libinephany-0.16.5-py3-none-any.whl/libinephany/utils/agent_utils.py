# ======================================================================================================================
#
# FUNCTIONS
#
# ======================================================================================================================

from libinephany.utils.constants import PREFIXES, PREFIXES_TO_HPARAMS, SUFFIXES

# ======================================================================================================================
#
# CONSTANTS
#
# ======================================================================================================================

ID_CONNECTOR = "-"

# ======================================================================================================================
#
# FUNCTIONS
#
# ======================================================================================================================


def _strip_substrings(strip_from: str, substrings: list[str]) -> str:
    """
    :param strip_from: String to strip given substrings from.
    :param substrings: Substrings to strip from the given string.
    :return: Given string stripped of given substrings.
    """

    for substring in substrings:
        strip_from = strip_from.replace(substring, "")

    if strip_from[0] == ID_CONNECTOR:
        strip_from = strip_from[1:]

    if strip_from[-1] == ID_CONNECTOR:
        strip_from = strip_from[:-1]

    return strip_from


def create_agent_id(layer_name: str, prefix: str, suffix: str | None) -> str:
    """
    :param layer_name: None or the name of the layer being controlled by the agent.
    :param prefix: Prefix to prepend to the agent ID.
    :param suffix: Suffix to append to the agent ID.
    :return: Agent ID.
    """

    agent_id = f"{prefix}{ID_CONNECTOR}{layer_name}"

    if suffix is not None:
        agent_id = f"{agent_id}{ID_CONNECTOR}{suffix}"

    return agent_id


def extract_parameter_group_name(agent_id: str) -> str:
    """
    :param agent_id: Agent ID to extract parameter group name.
    :return: Extracted parameter group name.
    """

    no_prefixes = _strip_substrings(strip_from=agent_id, substrings=PREFIXES)
    layer_name = _strip_substrings(strip_from=no_prefixes, substrings=SUFFIXES)

    return layer_name


def extract_agent_type(agent_id: str) -> str:
    """
    :param agent_id: Agent ID to extract the agent type from.
    :return: Prefix designating the agent type.
    :raises ValueError: When no agent ID prefix is found.
    """

    for prefix in PREFIXES:
        if agent_id.startswith(prefix):
            return PREFIXES_TO_HPARAMS[prefix]

    raise ValueError(f"Unknown agent type with ID {agent_id}.")
