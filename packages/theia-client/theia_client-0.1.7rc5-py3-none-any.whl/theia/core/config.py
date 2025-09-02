import dataclasses
import pathlib

import yaml


@dataclasses.dataclass(kw_only=True)
class CameraConfig:
    resolution: tuple[int, int]
    rtsp_url: str


@dataclasses.dataclass(kw_only=True)
class ServerConfig:
    cameras: dict[str, CameraConfig]
    close_bbox_diagonal: float
    http_port: int
    recording_lifetime_s: float
    status_frequency_hz: float

    @property
    def camera_ids(self) -> list[str]:
        return list(self.cameras.keys())


def load(path: pathlib.Path) -> ServerConfig:
    """Loads the server configuration from a YAML file."""
    with open(path, "r") as f:
        loaded_cfg = yaml.safe_load(f)
    cams = {
        cam_id: CameraConfig(
            # YAML doesn't have built in tuple support so we convert it here.
            resolution=tuple(cam_dict["resolution"]),
            rtsp_url=cam_dict["rtsp_url"],
        )
        for cam_id, cam_dict in loaded_cfg.get("cameras", {}).items()
    }
    server_cfg = ServerConfig(
        cameras=cams,
        close_bbox_diagonal=loaded_cfg["close_bbox_diagonal"],
        http_port=loaded_cfg["http_port"],
        recording_lifetime_s=loaded_cfg["recording_lifetime_s"],
        status_frequency_hz=loaded_cfg["status_frequency_hz"],
    )
    if len(server_cfg.cameras) == 0:
        raise ValueError("Configuration must specify at least one camera.")
    return server_cfg


def save(config: ServerConfig, path: pathlib.Path) -> None:
    """Saves the server configuration to a YAML file."""
    data = dataclasses.asdict(config)

    # YAML doesn't have built in tuple support so we convert it here.
    for cam_cfg in data["cameras"].values():
        cam_cfg["resolution"] = list(cam_cfg["resolution"])

    with open(path, "w") as f:
        yaml.safe_dump(data, f)
