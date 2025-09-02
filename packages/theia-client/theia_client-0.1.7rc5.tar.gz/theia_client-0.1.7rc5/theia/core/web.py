def status_path() -> str:
    """Returns the path component for the status endpoint."""
    return "/api/status"


def ready_path() -> str:
    """Returns the path component for the ready endpoint."""
    return "/api/ready"


def _stream_image_path_prefix(stream_id: str) -> str:
    """Returns the path prefix component for a stream's image endpoint."""
    return f"/api/{stream_id}/image"


def stream_image_path(stream_id: str, pts: int) -> str:
    """Returns the path component for a stream's image endpoint."""
    return f"{_stream_image_path_prefix(stream_id)}/{pts}"


def stream_image_path_template(stream_id: str) -> str:
    """Returns the path template for a stream's image endpoint."""
    return _stream_image_path_prefix(stream_id) + "/{pts:int}"
