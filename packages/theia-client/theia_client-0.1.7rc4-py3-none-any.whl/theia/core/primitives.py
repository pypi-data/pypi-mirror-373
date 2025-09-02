from __future__ import annotations

import dataclasses
import enum
from typing import Any


@dataclasses.dataclass(kw_only=True)
class SafetyConfig:
    """Safety parameters used in determining whether a pedestrian has been detected."""

    close_bbox_diagonal: float
    min_stopping_confidence: float
    min_throughput_hz: float
    monitor_window_s: float


@dataclasses.dataclass(frozen=True, kw_only=True)
class BoundingBox:
    """Represents a 2D bounding on the image plane defined by its top left and bottom
    right corners. The coordinates are expressed in pixels with the X coordinates
    measured from the image's left edge, and the Y coordinates are measured from the top
    of the image.

    p0 -------
    | |__O__| |
    |    |    |
    |  _/|_   |
     ------- p1

    Where: p0 = (x0, y0), p1 = (x1, y1)
    """

    x0: int
    y0: int
    x1: int
    y1: int

    @property
    def width(self) -> int:
        return self.x1 - self.x0

    @property
    def height(self) -> int:
        return self.y1 - self.y0

    @property
    def diagonal(self) -> float:
        """Length of the diagonal of this bounding box in pixels."""
        return (self.width**2 + self.height**2) ** 0.5

    @property
    def area(self) -> int:
        return self.width * self.height

    def intersection(self, other: BoundingBox) -> int:
        intersect_w = min(self.x1, other.x1) - max(self.x0, other.x0)
        intersect_h = min(self.y1, other.y1) - max(self.y0, other.y0)
        if intersect_w < 0 or intersect_h < 0:
            return 0
        else:
            return intersect_w * intersect_h


@dataclasses.dataclass(frozen=True, kw_only=True)
class Detection:
    """A detected object within an image."""

    bounding_box: BoundingBox
    confidence: float

    @classmethod
    def from_dict(cls, detection_dict: dict) -> Detection:
        """Reconstructs a Detection from a dictionary."""
        bounding_box_obj = detection_dict["bounding_box"]
        bounding_box = BoundingBox(**bounding_box_obj)
        return cls(bounding_box=bounding_box, confidence=detection_dict["confidence"])


@dataclasses.dataclass(frozen=True, kw_only=True)
class EvaluatedDetection(Detection):
    """A detection evaluated on whether the object is close and/or confident.

    Primarily exists for use in StreamStatus in WebSocket messages from Theia to
    clients.
    """

    is_close: bool
    is_confident: bool

    @classmethod
    def from_dict(cls, det_dict: dict) -> EvaluatedDetection:
        bbox = BoundingBox(**det_dict["bounding_box"])
        return cls(
            bounding_box=bbox,
            confidence=det_dict["confidence"],
            is_close=det_dict["is_close"],
            is_confident=det_dict["is_confident"],
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class EvaluatedInference:
    """An inference with EvaluatedDetections."""

    pts: int
    evaluated_detections: list[EvaluatedDetection]

    @classmethod
    def from_dict(cls, inf_dict: dict) -> EvaluatedInference:
        eval_detections = [
            EvaluatedDetection.from_dict(det_dict)
            for det_dict in inf_dict["evaluated_detections"]
        ]
        return cls(pts=inf_dict["pts"], evaluated_detections=eval_detections)


class SafetyState(enum.IntEnum):
    """A state that reflects safety conditions in a stream."""

    HEALTHY = enum.auto()
    PEDESTRIAN_PRESENT = enum.auto()
    LOW_INFERENCE_THROUGHPUT = enum.auto()
    LOW_DECODE_THROUGHPUT = enum.auto()


def _parse_latest_evaluated_inference(obj: Any) -> EvaluatedInference | None:
    if obj is None:
        return None
    if isinstance(obj, EvaluatedInference):
        return obj
    if isinstance(obj, dict):
        return EvaluatedInference.from_dict(obj)
    raise ValueError(f"Invalid type: {type(obj)}")


def _parse_safety_state(obj: Any) -> SafetyState:
    if isinstance(obj, SafetyState):
        return obj
    if isinstance(obj, int):
        return SafetyState(obj)
    raise ValueError(f"Invalid type: {type(obj)}")


@dataclasses.dataclass(kw_only=True)
class StreamStatus:
    """Comprises the current status of a stream.

    The decode_fps reflects how fast frames are being decoded from RTSP streams.
    The inference_fps reflects how fast inferences are being generated.
    The latest_evaluated_inference contains the most recent inference with
    safety-evaluated detections, or None if no inference has been processed yet.
    """

    decode_fps: float
    inference_fps: float
    latest_evaluated_inference: EvaluatedInference | None
    safety_state: SafetyState

    @classmethod
    def from_dict(cls, status_dict: dict) -> StreamStatus:
        latest_evaluated_inference_obj = status_dict.get("latest_evaluated_inference")
        latest_evaluated_inference = _parse_latest_evaluated_inference(
            latest_evaluated_inference_obj
        )

        safety_state_obj = status_dict.get("safety_state")
        safety_state = _parse_safety_state(safety_state_obj)

        return cls(
            decode_fps=status_dict["decode_fps"],
            latest_evaluated_inference=latest_evaluated_inference,
            inference_fps=status_dict["inference_fps"],
            safety_state=safety_state,
        )


@dataclasses.dataclass(kw_only=True)
class SystemStatus:
    """Aggregates individual stream statuses with an overall system stafety state."""

    stream_statuses: dict[str, StreamStatus]

    @classmethod
    def from_dict(cls, status_dict: dict) -> SystemStatus:
        stream_status_dicts = status_dict["stream_statuses"]
        stream_statuses = {
            stream_id: StreamStatus.from_dict(stream_status_dict)
            for stream_id, stream_status_dict in stream_status_dicts.items()
        }
        return cls(stream_statuses=stream_statuses)
