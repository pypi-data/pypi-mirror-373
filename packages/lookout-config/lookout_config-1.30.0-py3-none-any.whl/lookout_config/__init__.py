# IMPORTANT
# After changing this file, run `python3 -m lookout_config.generate_schemas`
# To re-generate the json schemas
import os
from pathlib import Path

from lookout_config.types import (
    LookoutConfig,
    Mode,
    LogLevel,
    Network,
    GeolocationMode,
    Point,
    Polygon,
    Camera,
    PositioningSystem,
)
from lookout_config.config_io import ConfigIO


def get_config_io() -> ConfigIO:
    """Get a ConfigIO instance using the LOOKOUT_CONFIG_DIR environment variable."""
    config_dir = os.environ.get("LOOKOUT_CONFIG_DIR")
    if config_dir is None:
        raise ValueError("LOOKOUT_CONFIG_DIR environment variable is not set.")
    return ConfigIO(config_directory=config_dir)


__all__ = [
    "get_config_io",
    "ConfigIO",
    "LookoutConfig",
    "Mode",
    "LogLevel",
    "Network",
    "GeolocationMode",
    "Point",
    "Polygon",
    "Camera",
    "PositioningSystem",
]
