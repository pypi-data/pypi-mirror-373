# Updates here should also be made to:
# * lookout_interfaces/msg/Config.msg
# * lookout_config_manager/mappers.py

from enum import Enum
from typing import Any, Literal, Union

from greenstream_config.types import Camera, Offsets
from pydantic import BaseModel, ConfigDict
from pydantic.fields import Field


class Mode(str, Enum):
    SIMULATOR = "simulator"
    HARDWARE = "hardware"
    STUBS = "stubs"
    ROSBAG = "rosbag"

    def __str__(self) -> str:
        return self.value


class PositioningSystem(str, Enum):
    NONE = "none"
    SEPTENTRIO_INS = "septentrio_ins"
    ADNAV_INS = "advanced_navigation_ins"
    NMEA_2000_SAT_COMPASS = "nmea_2000_sat_compass"
    NMEA_2000_COMPASS = "nmea_2000_compass"
    NMEA_0183_SAT_COMPASS = "nmea_0183_sat_compass"
    NMEA_0183_COMPASS = "nmea_0183_compass"

    def __str__(self) -> str:
        return self.value


class LogLevel(str, Enum):
    INFO = "info"
    DEBUG = "debug"

    def __str__(self) -> str:
        return self.value


class Network(str, Enum):
    SHARED = "shared"
    HOST = "host"

    def __str__(self) -> str:
        return self.value


class GeolocationMode(str, Enum):
    NONE = "none"
    RELATIVE_BEARING = "relative_bearing"
    ABSOLUTE_BEARING = "absolute_bearing"
    RANGE_BEARING = "range_bearing"

    def __str__(self) -> str:
        return self.value


class CudaVersion(str, Enum):
    CUDA_12_4 = "12.4"
    CUDA_12_6 = "12.6"

    def __str__(self) -> str:
        return self.value


class Point(BaseModel):
    x: int = Field(description="X coordinate in pixels")
    y: int = Field(description="Y coordinate in pixels")

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        return False


class Polygon(BaseModel):
    points: list[Point] = Field(description="List of points defining the polygon vertices")


class VesselOffsets(BaseModel):
    name: str = Field(description="Name of the vessel model file")
    baselink_to_ins: Offsets = Field(description="Offset from vessel baselink to INS sensor")
    baselink_to_waterline: Offsets = Field(description="Offset from vessel baselink to waterline")


class DiscoverySimple(BaseModel):
    type: Literal["simple"] = "simple"
    ros_domain_id: int = Field(
        default=0,
        description="ROS domain ID",
    )
    own_ip: str = Field(
        default="0.0.0.0",
        description="IP/host/interface address of the primary network interface. This is where DDS traffic will route to.",
    )


class DiscoveryFastDDS(BaseModel):
    type: Literal["fastdds"] = "fastdds"
    with_discovery_server: bool = Field(
        default=True,
        description="Run the discovery server. It will bind to 0.0.0.0:11811",
    )
    discovery_server_ip: str = Field(
        default="0.0.0.0",
        description="IP/host/interface of the discovery server. Assumes port of 11811",
    )
    own_ip: str = Field(
        default="0.0.0.0",
        description="IP/host/interface address of the primary network interface. This is where DDS traffic will route to.",
    )


class DiscoveryZenoh(BaseModel):
    type: Literal["zenoh"] = "zenoh"
    with_discovery_server: bool = Field(default=True, description="Run the zenoh router")
    discovery_server_ip: str = Field(
        default="0.0.0.0",
        description="IP/host/interface of the discovery server.",
    )


Discovery = Union[DiscoveryZenoh, DiscoveryFastDDS, DiscoverySimple]


class LookoutConfig(BaseModel):
    # So enum values are written and read to the yml correctly
    model_config = ConfigDict(
        use_enum_values=False,
        json_encoders={
            Mode: lambda v: v.value,
            LogLevel: lambda v: v.value,
            Network: lambda v: v.value,
            GeolocationMode: lambda v: v.value,
            PositioningSystem: lambda v: v.value,
            CudaVersion: lambda v: v.value,
        },
    )
    namespace_vessel: str = Field(default="vessel_1", description="ROS namespace for the vessel")
    gama_vessel: bool = Field(
        default=False, description="Whether this is running on a Gama vessel"
    )
    mode: Mode = Field(default=Mode.HARDWARE, description="Operating mode for the system")
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging verbosity level")
    cameras: list[Camera] = Field(default_factory=list)
    network: Network = Field(default=Network.HOST, description="Docker network mode to use")
    gpu: bool = Field(default=True, description="Enable GPU acceleration for processing")
    geolocation_mode: GeolocationMode = Field(
        default=GeolocationMode.NONE,
        description="Method for determining target geolocations",
    )
    positioning_system: PositioningSystem = Field(
        default=PositioningSystem.NONE,
        description="Type of positioning/navigation system to use",
    )
    offsets: VesselOffsets = Field(
        default=VesselOffsets(
            name="",
            baselink_to_ins=Offsets(
                forward=1.4160, left=0.153, up=0.184, roll=None, pitch=None, yaw=None
            ),
            baselink_to_waterline=Offsets(
                up=-1.0,
                forward=None,
                left=None,
                roll=None,
                pitch=None,
                yaw=None,
            ),
        ),
        description="Physical offsets and vessel model configuration",
    )
    components: Any = Field(
        default_factory=dict,
        description="Dynamic component configurations generated from ROS parameters",
    )
    prod: bool = Field(
        default=True,
        description="Whether to run in production mode with optimized settings",
    )
    log_directory: str = Field(
        default="~/greenroom/lookout/logs",
        description="Directory path for storing log files",
    )
    models_directory: str = Field(
        default="~/greenroom/lookout/models",
        description="Directory path for AI/ML model files",
    )
    recording_directory: str = Field(
        default="~/greenroom/lookout/recordings",
        description="Directory path for storing video recordings",
    )
    discovery: Discovery = Field(
        default_factory=DiscoverySimple,
        discriminator="type",
    )
    use_ais_web_receiver: bool = Field(
        default=False, description="Whether to run the AIS web receiver node"
    )
    use_rosbag_scheduler: bool = Field(
        default=False, description="Whether to run the rosbag scheduler node"
    )
    cuda_version: CudaVersion = Field(
        default=CudaVersion.CUDA_12_6, description="CUDA version to use for GPU operations"
    )
