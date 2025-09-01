from typing import List, Literal, Optional

from pydantic import BaseModel, Field, model_validator


class Offsets(BaseModel):
    """Spatial offsets in the Front-Left-Up (FLU) coordinate frame."""

    roll: Optional[float] = Field(None, description="Roll rotation in radians (FLU frame)")
    pitch: Optional[float] = Field(None, description="Pitch rotation in radians (FLU frame)")
    yaw: Optional[float] = Field(None, description="Yaw rotation in radians (FLU frame)")
    forward: Optional[float] = Field(None, description="Forward translation in meters")
    left: Optional[float] = Field(None, description="Left translation in meters")
    up: Optional[float] = Field(None, description="Up translation in meters")


class PTZOffsets(Offsets):
    """PTZ-specific offsets with joint type specification."""

    type: Literal["pan", "tilt"] = Field(description="PTZ joint type (pan or tilt)")


class Camera(BaseModel):
    """Camera configuration for video streaming and control."""

    name: str = Field(
        description="Camera identifier used in frame IDs, ROS topics, and WebRTC streams"
    )
    order: int = Field(description="Display order in the web UI")
    type: str = Field(default="color", description="Camera type (e.g., color, ir, depth)")
    publish_camera_info: bool = Field(
        default=True, description="Whether to launch camera info publisher node"
    )
    ptz: bool = Field(
        default=False, description="Whether to launch PTZ driver for pan-tilt-zoom control"
    )
    camera_offsets: Optional[Offsets] = Field(
        None, description="Camera position offsets relative to base_link"
    )
    ptz_offsets: List[PTZOffsets] = Field(
        default=[], description="PTZ joint offsets (required when ptz=True)"
    )

    @model_validator(mode="after")
    def validate_ptz_with_offsets(cls, model):
        """Ensure that ptz_offsets is set when ptz is True."""
        if model.ptz and not model.ptz_offsets:
            raise ValueError("ptz_offsets cannot be empty when ptz is set to True")
        return model


class GreenstreamConfig(BaseModel):
    """Complete configuration for the Greenstream video streaming system."""

    cameras: List[Camera] = Field(description="List of camera configurations to deploy")
    signalling_server_port: int = Field(
        default=8443, description="Port for the WebRTC signalling server"
    )
    namespace_vessel: str = Field(
        default="vessel_1", description="Vessel identifier for multi-vessel deployments"
    )
    namespace_application: str = Field(default="greenstream", description="Application namespace")
    ui_port: int = Field(default=8000, description="Port for the web UI server")
    debug: bool = Field(default=False, description="Enable debug logging and tracing")
    diagnostics_topic: str = Field(default="diagnostics", description="ROS diagnostics topic name")
    cert_path: Optional[str] = Field(None, description="SSL certificate path for HTTPS signalling")
    cert_password: Optional[str] = Field(None, description="SSL certificate password")
