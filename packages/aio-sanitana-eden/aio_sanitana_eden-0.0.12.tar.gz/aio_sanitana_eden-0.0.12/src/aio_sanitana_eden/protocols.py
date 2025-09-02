"""Asyncio protocols."""

from asyncio import DatagramProtocol, DatagramTransport, Future, Queue, TaskGroup
from typing import Any, NoReturn


class _QueuedDatagramProtocol(DatagramProtocol):
    """Asyncio UDP Protocol providing async/await interface for sending and receiving packets."""

    _transport: DatagramTransport

    def __init__(self, tg: TaskGroup, disconnect: Future) -> None:
        """Initialize a QueuedDatagramProtocol.

        Args:
            tg (TaskGroup): asyncio TaskGroup to create any tasks in
            disconnect (Future): gets set when the socket is finally closed.
        """

        self._tg: TaskGroup = tg
        self._disconnect: Future = disconnect
        self._send_queue = Queue()
        self._receive_queue = Queue()
        self._sender_task = tg.create_task(self._run_sender())

    async def send(
        self, data: bytes, addr: tuple[str | Any, int] | None = None
    ) -> None:
        """Put datagram in send queue."""
        await self._send_queue.put((data, addr))

    async def receive(self) -> tuple[bytes, tuple[str | Any, int]]:
        """Receive datagram from receive queue."""
        data, addr = await self._receive_queue.get()
        self._receive_queue.task_done()
        return (data, addr)

    async def send_receive(self, m: bytes) -> tuple[bytes, tuple[str | Any, int]]:
        """Put a datagram in send queue and await a response on the receive queue."""
        await self.send(m)
        data, addr = await self.receive()
        return (data, addr)

    async def _run_sender(self):
        while True:
            message, addr = await self._send_queue.get()
            self._transport.sendto(message, addr)
            self._send_queue.task_done()

    def connection_made(self, transport: DatagramTransport) -> None:
        """Call when a connection is made."""
        self._transport = transport

    def datagram_received(self, data: bytes, addr: tuple[str | Any, int]) -> None:
        """Call when a datagram is received."""
        self._receive_queue.put_nowait((data, addr))

    def error_received(self, exc: Exception) -> NoReturn:
        """Call when a send or receive operation receives an OSError."""
        raise exc

    def connection_lost(self, exc: Exception) -> NoReturn:
        """Call when a connection is lost or closed."""

        self._sender_task.cancel()
        self._disconnect.set_result(True)
        if exc is not None:
            raise exc
