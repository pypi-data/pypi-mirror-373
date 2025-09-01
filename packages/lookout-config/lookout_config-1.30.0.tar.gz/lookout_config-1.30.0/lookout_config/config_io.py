import yaml
import os
from typing import Any
from pathlib import Path

from lookout_config.types import LookoutConfig
from lookout_config.helpers import YamlDumper


class ConfigIO:
    """Configuration I/O handler for Lookout configuration files."""

    file_name = "lookout.yml"
    schema_url = "https://greenroom-robotics.github.io/lookout/schemas/lookout.schema.json"

    def __init__(self, config_directory: str | Path = ""):
        """Initialize ConfigIO with a configurable config directory.

        Args:
            config_directory: Base configuration directory path.
        """
        if str(config_directory).startswith("~"):
            self.config_directory = Path(config_directory).expanduser()
        else:
            self.config_directory = (
                Path("~/.config/greenroom").joinpath(config_directory).expanduser()
            )

    def get_path(self) -> Path:
        """Returns the full path to the lookout configuration file."""
        return self.config_directory / self.file_name

    def parse(self, config: dict[str, Any]) -> LookoutConfig:
        """Parse a configuration dictionary into a LookoutConfig object."""
        return LookoutConfig(**config or {})

    def read(self) -> LookoutConfig:
        """Read and parse the lookout configuration file."""
        path = self.get_path()
        with open(path) as stream:
            return self.parse(yaml.safe_load(stream))

    def write(self, config: LookoutConfig):
        """Write a LookoutConfig object to the configuration file."""
        path = self.get_path()
        # Make the parent dir if it doesn't exist
        os.makedirs(path.parent, exist_ok=True)
        json_string = config.model_dump(mode="json")
        with open(path, "w") as stream:
            print(f"Writing: {path}")
            headers = f"# yaml-language-server: $schema={ConfigIO.schema_url}"
            data = "\n".join([headers, yaml.dump(json_string, Dumper=YamlDumper, sort_keys=True)])
            stream.write(data)
