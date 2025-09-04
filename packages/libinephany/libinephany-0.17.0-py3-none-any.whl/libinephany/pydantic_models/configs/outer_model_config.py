# ======================================================================================================================
#
# BACKWARD COMPATIBILITY MODULE
#
# This module provides backward compatibility for older pickled models that reference
# libinephany.pydantic_models.configs.outer_model_config. The actual implementation
# has moved to libipcode.pydantic_models.configs.outer_model_config.
#
# This allows older models to deserialize without moving the config back to libinephany.
#
# ======================================================================================================================

try:
    # Re-export all classes from libipcode to maintain backward compatibility
    from libipcode.pydantic_models.configs.outer_model_config import OuterModelConfig, SharedActorCriticConfig
except ImportError:
    # If libipcode is not available, provide a fallback or raise a more helpful error
    raise ImportError(
        "libipcode is required for backward compatibility with older models. Ignore this message if you"
        " are not an Inephany developer."
    )

# Export all symbols to maintain the same interface
__all__ = [
    "OuterModelConfig",
    "SharedActorCriticConfig",
]
