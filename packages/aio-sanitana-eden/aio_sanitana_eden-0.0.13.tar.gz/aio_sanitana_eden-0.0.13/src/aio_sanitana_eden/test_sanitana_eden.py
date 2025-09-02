import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from .sanitana_eden import SanitanaEden, SanitanaEdenState, CALLBACK_TYPE


@pytest.fixture
def eden():
    return SanitanaEden("127.0.0.1", 1234, reconnect_interval=1, poll_interval=0)


def test_initial_state(eden):
    assert eden._host == "127.0.0.1"
    assert eden._port == 1234
    assert eden._reconnect_interval == 1
    assert eden._poll_interval == 0
    assert eden._available is False
    assert isinstance(eden._state, SanitanaEdenState)
    assert eden.radio is not None
    assert eden.bluetooth is not None
    assert eden.light is not None
    assert eden.steam is not None


def test_available_property(eden):
    eden._available = True
    assert eden.available is True
    eden._available = False
    assert eden.available is False


def test_add_and_remove_listener(eden):
    called = []

    def cb():
        called.append(True)

    remove = eden.add_listener(cb)
    assert cb in eden._listeners
    remove()
    assert cb not in eden._listeners


def test_update_listeners(eden):
    called = []

    def cb():
        called.append(True)

    eden.add_listener(cb)
    eden._pending_update = True
    eden._update_listeners()
    assert called == [True]
    assert eden._pending_update is False


def test_setattr_if_changed_sets_and_flags(eden):
    eden._pending_update = False
    eden._setattr_if_changed("_available", True)
    assert eden._available is True
    assert eden._pending_update is True


def test_setattr_if_changed_no_change(eden):
    eden._available = False
    eden._pending_update = False
    eden._setattr_if_changed("_available", False)
    assert eden._pending_update is False


def test_encode_and_decode_roundtrip(eden):
    cmd = b"j"
    args = (1, 8750, 10)
    encoded = eden._encode(cmd, *args)
    assert encoded.startswith(b"@")
    assert encoded.endswith(b"*&\n")
    decoded_cmd, decoded_args = eden._decode(encoded)
    assert decoded_cmd == cmd
    assert decoded_args[:3] == args


def test_decode_invalid_data(eden):
    data = b"invalid"
    cmd, args = eden._decode(data)
    assert cmd is None
    assert args == []


def test_decode_cmd_A(eden):
    # Simulate a response with cmd 'A'
    data = b"@" + b"x" * 33 + b"A" + b"1#2#3#*&\n"
    cmd, args = eden._decode(data)
    assert cmd == b"A"
    assert args == ("1", "2", "3")


@pytest.mark.asyncio
async def test_async_update_calls_write(monkeypatch, eden):
    called = {}

    async def fake_write(cmd, *args):
        called["cmd"] = cmd
        called["args"] = args

    eden._write = fake_write
    await eden.async_update()
    assert called["cmd"] == b"o"


@pytest.mark.asyncio
async def test_async_setup_and_shutdown(monkeypatch, eden):
    # Patch _run to exit immediately
    async def fake_run():
        await asyncio.sleep(0)

    monkeypatch.setattr(eden, "_run", fake_run)
    await eden.async_setup()
    assert eden._task is not None
    await eden.async_shutdown()
    assert eden._task is None


@pytest.mark.asyncio
async def test_run_reader_valid(monkeypatch, eden):
    # Patch _readline to return valid data then raise CancelledError
    state_args = (1, 8750, 10, 1, 255, 128, 64, 60, 1024, 0, 0, 0)
    encoded = eden._encode(b"j", *state_args)

    async def fake_readline():
        if not hasattr(fake_readline, "called"):
            fake_readline.called = True
            return encoded
        raise asyncio.CancelledError()

    eden._readline = fake_readline
    eden._setattr_if_changed = MagicMock()
    eden._update_listeners = MagicMock()
    with pytest.raises(asyncio.CancelledError):
        await eden._run_reader()
    assert eden._setattr_if_changed.call_count >= 2
    assert eden._update_listeners.called


@pytest.mark.asyncio
async def test_run_poller(monkeypatch, eden):
    # Patch async_update and sleep to exit after one call
    called = []

    async def fake_update():
        called.append(True)

    async def fake_sleep(_):
        raise asyncio.CancelledError()

    eden.async_update = fake_update
    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    with pytest.raises(asyncio.CancelledError):
        await eden._run_poller()
    assert called == [True]


@pytest.mark.asyncio
async def test_write_and_readline(monkeypatch, eden):
    # Setup writer and reader mocks
    class Writer:
        def __init__(self):
            self.data = None
            self.closed = False

        def write(self, data):
            self.data = data

        async def drain(self):
            pass

        def close(self):
            self.closed = True

        async def wait_closed(self):
            pass

    class Reader:
        async def readline(self):
            return b"@" + b"x" * 33 + b"j" + "1 2 3*&\n"

    eden._writer = Writer()
    eden._reader = Reader()
    await eden._write(b"j", 1, 2, 3)
    assert eden._writer.data.startswith(b"@")
    line = await eden._readline()
    assert line.startswith(b"@")


def test_radio_properties(eden):
    eden._state = SanitanaEdenState(radio_on=1, radio_frequency=9000, radio_volume=10)
    assert eden.radio.is_on is True
    assert eden.radio.frequency == 90.0
    assert eden.radio.volume == 10.0


@pytest.mark.asyncio
async def test_radio_async_methods(monkeypatch, eden):
    eden._state = SanitanaEdenState(radio_on=1, radio_frequency=9000, radio_volume=10)
    called = {}

    async def fake_write(cmd, *args):
        called["cmd"] = cmd
        called["args"] = args

    eden._write = fake_write
    await eden.radio.async_turn_on()
    assert called["cmd"] == b"j"
    await eden.radio.async_turn_off()
    await eden.radio.async_set_frequency(95.5)
    await eden.radio.async_set_volume(20)


def test_bluetooth_properties(eden):
    eden._state = SanitanaEdenState(bluetooth_on=1)
    assert eden.bluetooth.is_on is True
    eden._state = SanitanaEdenState(bluetooth_on=0)
    assert eden.bluetooth.is_on is False


@pytest.mark.asyncio
async def test_bluetooth_async_methods(monkeypatch, eden):
    called = {}

    async def fake_write(cmd, *args):
        called["cmd"] = cmd
        called["args"] = args

    eden._write = fake_write
    await eden.bluetooth.async_turn_on()
    assert called["cmd"] == b"r"
    await eden.bluetooth.async_turn_off()


def test_light_properties(eden):
    eden._state = SanitanaEdenState(light_red=128, light_green=64, light_blue=32)
    assert eden.light.brightness == 128
    assert eden.light.is_on is True
    assert eden.light.rgb_color == (255, 127, 63)
    eden._state = SanitanaEdenState(light_red=0, light_green=0, light_blue=0)
    assert eden.light.is_on is False
    assert eden.light.rgb_color == (255, 255, 255)


@pytest.mark.asyncio
async def test_light_async_methods(monkeypatch, eden):
    called = {}

    async def fake_write(cmd, *args):
        called["cmd"] = cmd
        called["args"] = args

    eden._write = fake_write
    eden._state = SanitanaEdenState(light_red=128, light_green=64, light_blue=32)
    await eden.light.async_turn_on()
    assert called["cmd"] == b"m"
    await eden.light.async_turn_off()
    assert called["cmd"] == b"m"


def test_steam_properties(eden):
    eden._state = SanitanaEdenState(steam_temperature=50, steam_remaining=512)
    assert eden.steam.is_on is True
    assert eden.steam.temperature == 50.0
    assert eden.steam.remaining == 0.5
    eden._state = SanitanaEdenState(steam_temperature=0, steam_remaining=0)
    assert eden.steam.is_on is False


@pytest.mark.asyncio
async def test_steam_async_methods(monkeypatch, eden):
    called = {}

    async def fake_write(cmd, *args):
        called["cmd"] = cmd
        called["args"] = args

    eden._write = fake_write
    await eden.steam.async_turn_on(45, 20)
    assert called["cmd"] == b"n"
    await eden.steam.async_turn_off()
    assert called["cmd"] == b"n"
