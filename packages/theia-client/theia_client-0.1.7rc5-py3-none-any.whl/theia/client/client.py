import asyncio
import ipaddress
from typing import AsyncGenerator

import aiohttp

from theia.core import primitives, timing, web

_DEFAULT_TIMEOUT_S = 2
_DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=_DEFAULT_TIMEOUT_S)


class Client:
    """A basic client for interacting with the Theia server.

    Offers basic asyncio-based HTTP and WebSocket connections to the server.
    """

    def __init__(self, host: ipaddress.IPv4Address | str, port: int):
        self._base_url = f"http://{host}:{port}"
        self._session: aiohttp.ClientSession | None = None

    async def open(self, timeout: float | None = None) -> None:
        """Opens an HTTP session linking the client to the server.

        By default, this will wait until the server is ready. If a timeout is provided,
        it will raise an aiohttp.ClientError if the server is not reachable within the
        given timeout.
        """
        if self._session:
            return
        await self._wait_for_server_ready(timeout)
        self._session = aiohttp.ClientSession(self._base_url, raise_for_status=True)

    async def close(self) -> None:
        """Closes the HTTP session linking the client to the server."""
        if self._session:
            await self._session.close()
            self._session = None

    async def status_stream(self) -> AsyncGenerator[primitives.SystemStatus, None]:
        """Establishes a websocket connection and yields realtime status updates.

        Raises a aiohttp.client_exceptions.WSMessageTypeError if the server shuts down
        while the client is still connected.
        """
        if not self._session:
            raise RuntimeError("Client is not open.")

        path = web.status_path()
        async with self._session.ws_connect(path) as ws:
            while not ws.closed:
                raw_status = await ws.receive_json()
                yield primitives.SystemStatus.from_dict(raw_status)

    async def get_image(
        self, stream_id: str, pts: int, draw: bool | None = None
    ) -> bytes:
        """Gets the image corresponding to the given pts.

        Specify draw to True in order to include the frame's bounding boxes on the
        image. Otherwise the image will be returned as is.

        Raises a RuntimeError if the client is not open.
        """
        if not self._session:
            raise RuntimeError("Client is not open.")

        path = web.stream_image_path(stream_id, pts)
        params: dict[str, str] = {}
        if draw is not None:
            params["draw"] = str(draw).lower()
        async with self._session.get(path, params=params) as resp:
            resp.raise_for_status()
            image = await resp.read()
            return image

    async def _get_ready(self) -> None:
        """Check if the server is ready. Does NOT require that the client is open.

        Raises an aiohttp.ClientError if the server is not ready to accept connections.
        """
        full_path = self._base_url + web.ready_path()
        # Uses the aiohttp basic API because the session may not be open yet.
        async with aiohttp.request("GET", full_path) as resp:
            resp.raise_for_status()
            if resp.status != 200:
                raise RuntimeError("Encountered unexpected response from server!")
            return

    async def _wait_for_server_ready(self, timeout: float | None) -> None:
        """Waits until the server is ready.

        Raises an aiohttp.ClientError if the server is not reachable within the given
        timeout.
        """
        timer = timing.Timer(timeout)
        while True:
            try:
                await self._get_ready()
                break
            except aiohttp.ClientError:
                if timeout is not None and timer.is_finished():
                    raise
                await asyncio.sleep(1)
