"""Get info on a Sanitana Eden."""

import asyncio
from dataclasses import dataclass
from .exceptions import DeviceConnectionError
from .protocols import _QueuedDatagramProtocol


@dataclass(kw_only=True)
class SanitanaEdenInfo:
    """Represents info on a Sanitana Eden.

    Attributes:
        mac_used (str | None): MAC address used by the device.
        model (str | None): Model identifier of the device.
        protocol (str | None): Network protocol used.
        mode (str | None): Network mode (e.g., TCP/UDP).
        port (int | None): Network port number.
        mac_ap (str | None): MAC address of the access point.
        mac_sta (str | None): MAC address of the station.
    """

    mac_used: str | None = None
    model: str | None = None
    protocol: str | None = None
    mode: str | None = None
    port: int | None = None
    mac_ap: str | None = None
    mac_sta: str | None = None


async def async_get_info(host: str) -> SanitanaEdenInfo:
    """Retrieve information on a Sanitana Eden through its UDP socket."""

    result = SanitanaEdenInfo()
    loop = asyncio.get_running_loop()
    disconnect = loop.create_future()

    def _parse(data: bytes, _) -> list[str] | None:
        """Parse AT+ response from USR-WIFI232-G2 used in Sanitana Eden."""
        str_data = data.decode().rstrip("\n\r")
        if str_data.startswith("+ERR="):
            return None
        if str_data.startswith("+ok="):
            str_data = str_data[4:]
        return str_data.split(",")

    async with asyncio.TaskGroup() as tg:
        try:
            transport: asyncio.DatagramTransport
            protocol: _QueuedDatagramProtocol
            transport, protocol = await loop.create_datagram_endpoint(
                lambda: _QueuedDatagramProtocol(tg, disconnect),
                remote_addr=(host, 48899),
            )
        except Exception as e:
            raise DeviceConnectionError from e

        try:
            async with asyncio.timeout(3):
                if data := _parse(*await protocol.send_receive(b"HF-A11ASSISTHREAD")):
                    result.mac_used = data[1]
                    result.model = data[2]
                try:
                    async with asyncio.timeout(0.1):
                        await protocol.send(b"+ok")
                        await protocol.receive()
                except asyncio.TimeoutError:
                    pass
                if data := _parse(*await protocol.send_receive(b"AT+NETP\r")):
                    result.protocol = data[0]
                    result.mode = data[1]
                    try:
                        result.port = int(data[2])
                    except (ValueError, TypeError):
                        result.port = None
                if data := _parse(*await protocol.send_receive(b"AT+WAMAC\r")):
                    result.mac_ap = data[0]
                if data := _parse(*await protocol.send_receive(b"AT+WSMAC\r")):
                    result.mac_sta = data[0]
                return result
        except Exception as e:
            raise DeviceConnectionError from e
        finally:
            transport.close()
            await disconnect
