# models.py (m3-pyapi)
# M3 data models

from dataclasses import dataclass, asdict, fields
from typing import List


def from_dict(dtype, data):
    """ Recursively generate a dataclass from a dict """
    try:
        field_map = {field.name: field.type for field in fields(dtype)}
        return dtype(**{key: from_dict(field_map[key], val) for key, val in data.items()})
    except:
        return data


@dataclass
class CachedAncillaryDatum:
    uuid: str = None
    imaged_moment_uuid: str = None

    # Position
    latitude: float = None
    longitude: float = None
    depth_meters: float = None
    altitude_meters: float = None

    # Coordinate reference system
    crs: str = None

    # CTDO
    salinity: float = None
    temperature_celsius: float = None
    oxygen: float = None
    pressure_dbar: float = None

    # Transmissometer
    light_transmission: float = None

    # Camera Pose
    x: float = None
    y: float = None
    z: float = None
    pose_position_units: str = None
    phi: float = None
    theta: float = None
    psi: float = None

    @property
    def properties(self):
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class ImageListing:
    cameraId: str = None
    deploymentId: str = None
    files: List[str] = None


@dataclass
class ImageParams:
    uri: str = None
    cameraId: str = None
    deploymentId: str = None
    name: str = None


@dataclass
class Media:
    video_sequence_uuid: str = None
    video_reference_uuid: str = None
    video_uuid: str = None
    video_sequence_name: str = None
    camera_id: str = None
    video_name: str = None
    uri: str = None
    start_timestamp: str = None
    duration_millis: int = None
    container: str = None
    video_codec: str = None
    audio_codec: str = None
    width: int = None
    height: int = None
    frame_rate: float = None
    size_bytes: int = None
    description: str = None
    sha512: str = None


@dataclass
class CachedVideoReferenceInfo:
    mission_contact: str = None
    platform_name: str = None
    video_reference_uuid: str = None
    mission_id: str = None
    last_updated_time: str = None
    uuid: str = None


@dataclass
class Association:
    link_name: str = None
    link_value: str = None
    to_concept: str = None
    mime_type: str = None
    uuid: str = None


@dataclass
class ImageReference:
    description: str = None
    url: str = None
    height_pixels: int = None
    width_pixels: int = None
    format: str = None
    uuid: str = None


@dataclass
class Observation:
    observation_uuid: str = None
    concept: str = None
    observer: str = None
    observation_timestamp: str = None
    video_reference_uuid: str = None
    imaged_moment_uuid: str = None
    elapsed_time_millis: int = None
    recorded_timestamp: str = None
    group: str = None
    activity: str = None
    associations: List[Association] = None
    image_references: List[ImageReference] = None


@dataclass
class ImagedMoment:
    recorded_date: str = None
    timecode: str = None
    video_reference_uuid: str = None
    observations: List[Observation] = None
    image_references: List[ImageReference] = None
    ancillary_data: CachedAncillaryDatum = None
    last_updated_time: str = None
    uuid: str = None
