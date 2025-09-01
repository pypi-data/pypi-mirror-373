import tempfile
import pytest
from pathlib import Path

from lookout_config.config_io import ConfigIO
from lookout_config.types import (
    LookoutConfig,
    Mode,
    LogLevel,
    Network,
    GeolocationMode,
    PositioningSystem,
)


class TestConfigIO:
    def test_get_path_default_directory(self):
        """Test that get_path returns correct default path."""
        config_io = ConfigIO()
        expected_path = Path("~/.config/greenroom/lookout.yml").expanduser()
        assert config_io.get_path() == expected_path

    def test_get_path_custom_directory(self):
        """Test that get_path returns correct path with custom directory."""
        config_io = ConfigIO("custom/subdir")
        expected_path = Path("~/.config/greenroom/custom/subdir/lookout.yml").expanduser()
        assert config_io.get_path() == expected_path

    def test_parse_empty_config(self):
        """Test parsing empty configuration dictionary."""
        config_io = ConfigIO()
        result = config_io.parse({})
        assert isinstance(result, LookoutConfig)
        assert result.namespace_vessel == "vessel_1"  # default value
        assert result.mode == Mode.HARDWARE  # default value

    def test_parse_config_with_values(self):
        """Test parsing configuration dictionary with specific values."""
        config_io = ConfigIO()
        config_dict = {
            "namespace_vessel": "test_vessel",
            "mode": "simulator",
            "log_level": "debug",
            "gpu": False,
            "gama_vessel": True,
        }
        result = config_io.parse(config_dict)
        assert result.namespace_vessel == "test_vessel"
        assert result.mode == Mode.SIMULATOR
        assert result.log_level == LogLevel.DEBUG
        assert result.gpu is False
        assert result.gama_vessel is True

    def test_parse_none_config(self):
        """Test parsing None configuration."""
        config_io = ConfigIO()
        result = config_io.parse({})
        assert isinstance(result, LookoutConfig)
        assert result.namespace_vessel == "vessel_1"  # default value

    def test_write_and_read_config(self):
        """Test writing and reading configuration to/from temporary directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_io = ConfigIO(temp_dir)

            # Create a test configuration
            test_config = LookoutConfig(
                namespace_vessel="test_vessel_write",
                mode=Mode.SIMULATOR,
                log_level=LogLevel.DEBUG,
                gpu=False,
                gama_vessel=True,
            )

            # Write the configuration
            config_io.write(test_config)

            # Verify the file was created
            config_path = config_io.get_path()
            assert config_path.exists()

            # Read the configuration back
            read_config = config_io.read()

            # Verify the values match
            assert read_config.namespace_vessel == "test_vessel_write"
            assert read_config.mode == Mode.SIMULATOR
            assert read_config.log_level == LogLevel.DEBUG
            assert read_config.gpu is False
            assert read_config.gama_vessel is True

    def test_write_creates_parent_directory(self):
        """Test that write creates parent directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Use a nested path that doesn't exist
            nested_path = f"{temp_dir}/nested/subdir"
            config_io = ConfigIO(nested_path)

            test_config = LookoutConfig(namespace_vessel="test_nested")

            # Write should create the directory structure
            config_io.write(test_config)

            # Verify the file was created and directory exists
            config_path = config_io.get_path()
            assert config_path.exists()
            assert config_path.parent.exists()

    def test_write_includes_schema_header(self):
        """Test that written file includes YAML schema header."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_io = ConfigIO(temp_dir)
            test_config = LookoutConfig(namespace_vessel="test_schema")

            config_io.write(test_config)

            # Read the raw file content
            config_path = config_io.get_path()
            with open(config_path) as f:
                content = f.read()

            # Verify schema header is present
            expected_header = f"# yaml-language-server: $schema={ConfigIO.schema_url}"
            assert content.startswith(expected_header)

    def test_read_nonexistent_file_raises_error(self):
        """Test that reading a non-existent file raises FileNotFoundError."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_io = ConfigIO(f"{temp_dir}/nonexistent")

            with pytest.raises(FileNotFoundError):
                config_io.read()

    def test_write_read_roundtrip_preserves_all_fields(self):
        """Test that writing and reading preserves all configuration fields."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_io = ConfigIO(temp_dir)

            # Create a comprehensive configuration
            test_config = LookoutConfig(
                namespace_vessel="roundtrip_test",
                gama_vessel=True,
                mode=Mode.ROSBAG,
                log_level=LogLevel.DEBUG,
                cameras=[],
                network=Network.SHARED,
                gpu=False,
                geolocation_mode=GeolocationMode.RANGE_BEARING,
                positioning_system=PositioningSystem.SEPTENTRIO_INS,
                prod=False,
                log_directory="/custom/logs",
                models_directory="/custom/models",
                recording_directory="/custom/recordings",
            )

            # Write and read back
            config_io.write(test_config)
            read_config = config_io.read()

            # Verify all fields are preserved
            assert read_config.namespace_vessel == test_config.namespace_vessel
            assert read_config.gama_vessel == test_config.gama_vessel
            assert read_config.mode == test_config.mode
            assert read_config.log_level == test_config.log_level
            assert read_config.cameras == test_config.cameras
            assert read_config.network == test_config.network
            assert read_config.gpu == test_config.gpu
            assert read_config.geolocation_mode == test_config.geolocation_mode
            assert read_config.positioning_system == test_config.positioning_system
            assert read_config.prod == test_config.prod
            assert read_config.log_directory == test_config.log_directory
            assert read_config.models_directory == test_config.models_directory
            assert read_config.recording_directory == test_config.recording_directory
