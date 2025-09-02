import dataclasses
from typing import Any

from theia.core import primitives

_TEST_BBOX_DICT = {"x0": 10, "y0": 20, "x1": 100, "y1": 200}
_TEST_DETECTION_DICT = {"bounding_box": _TEST_BBOX_DICT, "confidence": 0.85}
_TEST_EVALUATED_DETECTION_DICT = {
    "bounding_box": _TEST_BBOX_DICT,
    "confidence": 0.85,
    "is_close": True,
    "is_confident": True,
}
_TEST_EVALUATED_INFERENCE_DICT = {
    "pts": 12345,
    "evaluated_detections": [
        _TEST_EVALUATED_DETECTION_DICT,
        _TEST_EVALUATED_DETECTION_DICT,
    ],
}
_TEST_STREAM_STATUS_DICT = {
    "decode_fps": 30.0,
    "latest_evaluated_inference": _TEST_EVALUATED_INFERENCE_DICT,
    "inference_fps": 25.0,
    "safety_state": 1,  # SafetyState.HEALTHY
}
_TEST_SYSTEM_STATUS_DICT = {
    "stream_statuses": {
        "cam1": _TEST_STREAM_STATUS_DICT,
        "cam2": _TEST_STREAM_STATUS_DICT,
    }
}


def test_detection_from_dict() -> None:
    """Tests that Detection.from_dict properly reconstructs nested BoundingBox."""
    detection = primitives.Detection.from_dict(_TEST_DETECTION_DICT)
    assert isinstance(detection.bounding_box, primitives.BoundingBox)


def _validate_evaluated_detection(evaluated_detection: Any) -> None:
    assert isinstance(evaluated_detection.bounding_box, primitives.BoundingBox)


def test_evaluated_detection_from_dict() -> None:
    """Tests that EvaluatedDetection.from_dict properly reconstructs nested objects."""
    evaluated_detection = primitives.EvaluatedDetection.from_dict(
        _TEST_EVALUATED_DETECTION_DICT
    )
    _validate_evaluated_detection(evaluated_detection)


def _validate_evaluated_inference(evaluated_inference: Any) -> None:
    for evaluated_detection in evaluated_inference.evaluated_detections:
        _validate_evaluated_detection(evaluated_detection)


def test_evaluated_inference_from_dict() -> None:
    """Tests that EvaluatedInference.from_dict properly reconstructs nested lists."""
    evaluated_inference = primitives.EvaluatedInference.from_dict(
        _TEST_EVALUATED_INFERENCE_DICT
    )
    _validate_evaluated_inference(evaluated_inference)


def _validate_stream_status(stream_status: Any) -> None:
    assert isinstance(stream_status.safety_state, primitives.SafetyState)
    assert isinstance(
        stream_status.latest_evaluated_inference, primitives.EvaluatedInference
    )


def test_stream_status_from_dict() -> None:
    """Tests that StreamStatus.from_dict properly handles enums and nested objects."""
    status = primitives.StreamStatus.from_dict(_TEST_STREAM_STATUS_DICT)
    _validate_stream_status(status)


def _validate_system_status(system_status: Any) -> None:
    for stream_status in system_status.stream_statuses.values():
        _validate_stream_status(stream_status)


def test_system_status_from_dict() -> None:
    """Tests that SystemStatus.from_dict properly reconstructs nested StreamStatus objects."""
    sys_status = primitives.SystemStatus.from_dict(_TEST_SYSTEM_STATUS_DICT)
    _validate_system_status(sys_status)


def test_stream_status_from_dict_idempotent() -> None:
    """Tests that StreamStatus.from_dict can handle already-converted objects."""
    status = primitives.StreamStatus.from_dict(_TEST_STREAM_STATUS_DICT)
    status_dict = dataclasses.asdict(status)
    loaded_status = primitives.StreamStatus.from_dict(status_dict)
    assert status == loaded_status
