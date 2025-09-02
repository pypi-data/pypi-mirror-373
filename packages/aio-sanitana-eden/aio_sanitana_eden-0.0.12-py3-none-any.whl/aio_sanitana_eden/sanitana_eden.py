"""Sanitana Eden API client."""

import asyncio
from collections.abc import Callable
from typing import Any, NamedTuple

from .const import LOGGER, MAC, MAC0

CALLBACK_TYPE = Callable[[], None]


class SanitanaEdenState(NamedTuple):
    """Represents the state of the Sanitana Eden device.

    Fields:
        radio_on (int): 1 if radio is on, 0 otherwise.
        radio_frequency (int): Radio frequency in hundredths of MHz (8750-10800).
        radio_volume (int): Radio volume (0-63).
        bluetooth_on (int): 1 if Bluetooth is on, 0 otherwise.
        light_red (int): Red channel brightness (0-255).
        light_green (int): Green channel brightness (0-255).
        light_blue (int): Blue channel brightness (0-255).
        steam_temperature (int): Steam temperature in Celsius (0-60).
        steam_remaining (int): Remaining steam program time (0-1024).
        reserved1 (int): Reserved for future use.
        reserved2 (int): Reserved for future use.
        reserved3 (int): Reserved for future use.
    """

    radio_on: int = 0
    radio_frequency: int = 0
    radio_volume: int = 0
    bluetooth_on: int = 0
    light_red: int = 0
    light_green: int = 0
    light_blue: int = 0
    steam_temperature: int = 0
    steam_remaining: int = 0
    reserved1: int = 0
    reserved2: int = 0
    reserved3: int = 0


class SanitanaEden:
    """Controls a Sanitana Eden steam shower.

    Attributes:
        radio (SanitanaEdenRadio): Controls radio functions.
        bluetooth (SanitanaEdenBluetooth): Controls bluetooth functions.
        light (SanitanaEdenLight): Controls light functions.
        steam (SanitanaEdenSteam): Controls steam functions.
        available (bool): Indicates connection availability; initialized to False, set to True when valid data is received in _run_reader, and reset to False on connection errors in _run.
    """

    def __init__(
        self,
        host: str,
        port: int,
        reconnect_interval: float = 30.0,
        poll_interval: float = 2.0,
    ) -> None:
        """Initialize a SanitanaEden object.

        Args:
            host (str): The hostname or IP address of the Sanitana Eden device.
            port (int): The port number to connect to the Sanitana Eden device.
            reconnect_interval (float): The interval (in seconds) to wait before attempting to reconnect.
            poll_interval (float): The interval (in seconds) to wait between polling for updates.
        """

        self._host = host
        self._port = port
        self._reconnect_interval = reconnect_interval
        self._poll_interval = poll_interval
        self._available = False
        self._state = SanitanaEdenState()
        self._task: asyncio.Task[None] | None = None
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._listeners: set[CALLBACK_TYPE] = set()
        self._pending_update = False
        self.radio = SanitanaEdenRadio(self)
        self.bluetooth = SanitanaEdenBluetooth(self)
        self.light = SanitanaEdenLight(self)
        self.steam = SanitanaEdenSteam(self)

    # Async functions to setup/shutdown
    async def async_setup(self) -> None:
        """Start async runner."""
        LOGGER.debug("Starting async runner")
        self._task = asyncio.create_task(self._run())

    async def async_shutdown(self) -> None:
        """Shut down the SanitanaEden async infrastructure."""
        if self._task is not None:
            try:
                LOGGER.debug("Stopping async runner")
                self._task.cancel()
                await self._task
            except asyncio.CancelledError:
                pass
            finally:
                self._task = None

    async def async_update(self) -> None:
        """Poll for state from Sanitana Eden."""
        await self._write(b"o")

    def add_listener(self, update_callback: CALLBACK_TYPE) -> CALLBACK_TYPE:
        """Listen for data updates."""

        def remove_listener() -> None:
            """Remove update listener."""
            self._listeners.discard(update_callback)

        self._listeners.add(update_callback)
        return remove_listener

    def _update_listeners(self) -> None:
        """Notify all listeners of an update."""
        if self._pending_update:
            for update_callback in self._listeners:
                update_callback()
            self._pending_update = False

    # Exposed property for availability
    @property
    def available(self) -> bool:
        """Available."""
        return self._available

    def _setattr_if_changed(self, attr: str, value: Any) -> None:
        if getattr(self, attr) != value:
            setattr(self, attr, value)
            self._pending_update = True

    async def _run(self):
        while True:
            try:
                LOGGER.debug("Connecting to %s:%d", self._host, self._port)
                self._reader, self._writer = await asyncio.open_connection(
                    self._host, self._port
                )
                LOGGER.debug("Connected to %s:%d", self._host, self._port)
                async with asyncio.TaskGroup() as tg:
                    tg.create_task(self._run_reader())
                    if self._poll_interval > 0:
                        tg.create_task(self._run_poller())
            except ExceptionGroup as eg:
                LOGGER.exception(eg)
            except BaseExceptionGroup as beg:
                LOGGER.exception(beg)
            except Exception as e:
                LOGGER.exception(e)
            finally:
                if self._writer is not None:
                    self._writer.close()
                    await self._writer.wait_closed()
                self._writer = None
                self._reader = None
                # Mark as unavailable
                self._setattr_if_changed("_available", False)
                self._update_listeners()
            # Run again in 30 seconds
            LOGGER.debug("Reconnecting in %d seconds", self._reconnect_interval)
            await asyncio.sleep(self._reconnect_interval)

    async def _run_poller(self) -> None:
        while True:
            await self.async_update()
            await asyncio.sleep(self._poll_interval)

    async def _run_reader(self) -> None:
        while True:
            b = await self._readline()
            cmd, args = self._decode(b)
            if cmd is None:
                continue
            if cmd in [b"A"]:
                continue
            if (
                isinstance(args, tuple)
                and len(args) == 12
                and all(isinstance(a, int) for a in args)
            ):
                self._setattr_if_changed("_state", SanitanaEdenState(*args))
                self._setattr_if_changed("_available", True)
                self._update_listeners()

    def _encode(self, cmd: bytes, *args: int) -> bytes:
        result = b"".join(
            (
                b"@",
                MAC,
                MAC0,
                cmd,
                b" " if args else b"",
                b" ".join(str(a).encode("ascii") for a in args),
                b"*&\n",
            )
        )
        LOGGER.debug("=> %s", result)
        return result

    async def _write(self, cmd: bytes, *args: int) -> None:
        assert self._writer is not None
        self._writer.write(self._encode(cmd, *args))
        await self._writer.drain()

    async def _readline(self) -> bytes:
        assert self._reader is not None
        return await self._reader.readline()

    def _decode(
        self, data: bytes
    ) -> tuple[bytes | None, tuple[int, ...] | tuple[str, ...]]:
        LOGGER.debug("<= %s", data)
        if data[0:1] != b"@" or data[-3:] != b"*&\n":
            return (None, [])
        cmd = data[35:36]
        data2 = data[36:-3].decode()
        if cmd in [b"A"]:
            args = tuple(a for a in data2.split("#") if a)
        else:
            args = tuple(int(a) for a in data2.split(" ") if a)
        return (cmd, args)


class SanitanaEdenRadio:
    """Represent the radio functions of a Sanitana Eden."""

    def __init__(self, se: SanitanaEden):
        """Initialize."""
        self._se = se

    @property
    def is_on(self) -> bool:
        """Return True if the radio is on."""
        return self._se._state.radio_on != 0

    @property
    def frequency(self) -> float:
        """Return the frequency in MHz the radio is tuned to (range 87.5-108, step 0.01)."""
        return float(self._se._state.radio_frequency) / 100.0

    @property
    def volume(self) -> float:
        """Return the volume of the radio (range 0-63, step 1)."""
        return float(self._se._state.radio_volume)

    async def async_turn_on(self, **_) -> None:
        """Turn radio on."""
        await self._se._write(
            b"j", 1, self._se._state.radio_frequency, self._se._state.radio_volume
        )

    async def async_turn_off(self, **_) -> None:
        """Turn radio off."""
        await self._se._write(
            b"j", 0, self._se._state.radio_frequency, self._se._state.radio_volume
        )

    async def async_set_frequency(self, frequency: float) -> None:
        """Set the frequency the radio is tuned to."""
        await self._se._write(
            b"j",
            self._se._state.radio_on,
            int(frequency * 100.0),
            self._se._state.radio_volume,
        )

    async def async_set_volume(self, volume: float) -> None:
        """Set the radio volume."""
        await self._se._write(
            b"j", self._se._state.radio_on, self._se._state.radio_frequency, int(volume)
        )


class SanitanaEdenBluetooth:
    """Represent the bluetooth functions of a Sanitana Eden."""

    def __init__(self, se: SanitanaEden):
        """Initialize."""
        self._se = se

    @property
    def is_on(self) -> bool:
        """Return True if the entity is on."""
        return bool(self._se._state.bluetooth_on)

    async def async_turn_on(self, **_) -> None:
        """Turn bluetooth on."""
        await self._se._write(b"r", 1)

    async def async_turn_off(self, **_) -> None:
        """Turn bluetooth off."""
        await self._se._write(b"r", 0)


class SanitanaEdenLight:
    """Represent the light functions on a Sanitana Eden."""

    def __init__(self, se: SanitanaEden):
        """Initialize a SanitanaEdenLight."""
        self._se = se

    @property
    def _light(self) -> tuple[int, int, int]:
        return (
            self._se._state.light_red,
            self._se._state.light_green,
            self._se._state.light_blue,
        )

    @property
    def brightness(self) -> int:
        """Return the brightness of the light (0..255)."""
        return max(self._light)

    @property
    def is_on(self) -> bool:
        """Return True if the light is on."""
        return self.brightness != 0

    @property
    def rgb_color(self) -> tuple[int, int, int]:
        """Return the RGB color of the light as a tuple[int,int,int]."""
        brightness = self.brightness
        if brightness == 0:
            return (255, 255, 255)

        return tuple(int(x * 255 / brightness) for x in self._light)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn light on."""
        rgb_color: tuple[int, ...] = kwargs.get("rgb_color") or self.rgb_color
        brightness: int = kwargs.get("brightness") or self.brightness or 255
        rgb_color = tuple(int(x * brightness / 255) for x in rgb_color)
        await self._se._write(b"m", *rgb_color)

    async def async_turn_off(self, **_) -> None:
        """Turn light off."""
        await self._se._write(b"m", 0, 0, 0)


class SanitanaEdenSteam:
    """Represent the steam functions of a Sanitana Eden."""

    def __init__(self, se: SanitanaEden):
        """Initialize."""
        self._se = se

    @property
    def is_on(self) -> bool:
        """Return True if the steam generator is on."""
        return (
            self._se._state.steam_temperature != 0
            or self._se._state.steam_remaining != 0
        )

    @property
    def temperature(self) -> float:
        """Return the temperature in degrees Celcius of the steam program."""
        return float(self._se._state.steam_temperature)

    @property
    def remaining(self) -> float:
        """Fraction (0.0 to 1.0) of steam program still remaining, counting down from 1024."""
        return float(self._se._state.steam_remaining) / 1024.0

    async def async_turn_on(self, temperature: float, minutes: float) -> None:
        """Turn on steam generator."""
        await self._se._write(b"n", int(temperature), int(minutes))

    async def async_turn_off(self) -> None:
        """Turn steam generator off."""
        await self._se._write(b"n", 0, 0)
