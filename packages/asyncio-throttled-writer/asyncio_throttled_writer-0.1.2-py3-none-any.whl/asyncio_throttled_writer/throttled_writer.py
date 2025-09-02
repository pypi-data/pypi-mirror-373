import asyncio
import time
from asyncio import StreamWriter
from typing import Literal


class ThrottledStreamWriter(StreamWriter):
    """
    A throttled stream writer for asyncio applications.

    This class wraps an asyncio StreamWriter and provides throttling capabilities
    to prevent flooding of network connections by enforcing minimum intervals
    between write operations.
    """

    def __del__(self, warnings=...):
        self.writer.__del__(warnings)

    async def start_tls(self, sslcontext, *, server_hostname=None, ssl_handshake_timeout=None,
                        ssl_shutdown_timeout=None):
        return await self.writer.start_tls(sslcontext, server_hostname=server_hostname,
                                           ssl_handshake_timeout=ssl_handshake_timeout,
                                           ssl_shutdown_timeout=ssl_shutdown_timeout)

    def can_write_eof(self):
        return self.writer.can_write_eof()

    def write_eof(self):
        self.writer.write_eof()

    def writelines(self, data):
        """
        Write multiple lines of data.
        Note: This method writes all data synchronously without throttling.
        For throttled writes, use individual write() calls.
        """
        for d in data:
            self.writer.write(d)

    @property
    def transport(self):
        return self.writer.transport

    def __init__(self, writer: StreamWriter):
        """
        Initialize the throttled stream writer.

        :param writer: An instance of asyncio StreamWriter to wrap.
        """

        self.writer = writer
        self._min_send_interval_ns = 0  # Minimum send interval in nanoseconds
        self._last_send_time_ns = 0  # Last send time in nanoseconds
        self._send_lock = asyncio.Lock()  # Lock for throttled writes
        self.set_min_send_interval_ms(1)

    async def drain(self):
        """Drain the underlying writer."""
        await self.writer.drain()

    def set_min_send_interval_ms(self, ms: float) -> None:
        """
        Set the minimum send interval in milliseconds for throttling writes.
        :param ms: Minimum interval in milliseconds. If negative, it will be set to 0.
        """

        # Convert milliseconds to nanoseconds
        self._min_send_interval_ns = int((ms if ms >= 0 else 0) * 1_000_000)

    async def _throttled_write(self, data: bytes, mode: Literal["bytewise"] | Literal["whole"] = "whole",
                               drain: bool = False) -> None:
        """
        Write data with throttling to prevent flooding.

        This method ensures that writes are spaced out by at least the minimum
        send interval defined by `_min_send_interval_ns`.

        @:param data: The data to send, as bytes.
        @:param mode: If "bytewise", send data one byte at a time with throttling applied to each byte.
                      If "whole", send the entire message at once. Default is "whole".
        @:param drain: If True, call drain after each write to push out data quickly
        @:return: None
        """
        if mode not in ["bytewise", "whole"]:
            raise ValueError("Invalid mode. Must be 'bytewise' or 'whole'.")

        # Prepare packets based on mode
        # In "bytewise" mode, send each byte separately
        # In "whole" mode, send the entire data at once
        packets = [data if mode == "whole" else bytes([b]) for b in data] if mode == "bytewise" else [data]

        # Ensure only one throttled write operation occurs at a time
        async with self._send_lock:

            # Send each packet with throttling
            for packet in packets:

                # Calculate the time to wait before sending the next packet
                wait_ns = self._min_send_interval_ns - (time.monotonic_ns() - self._last_send_time_ns)

                if self._last_send_time_ns != 0 and wait_ns > 0:
                    # Sleep for the required wait time in seconds
                    await asyncio.sleep(wait_ns / 1_000_000_000)

                self.writer.write(packet)

                # Optionally drain to push out quickly - throughput may suffer
                if drain:
                    await self.writer.drain()

                # Update the last send time
                self._last_send_time_ns = time.monotonic_ns()

    async def write(self, msg_bytes: bytes,
                    mode: Literal["no_throttle"] | Literal["bytewise"] | Literal["whole"] = "whole",
                    drain: bool = False) -> None:
        """
        Send raw bytes with optional throttling applied.

            :param msg_bytes: The bytes to send.
            :param mode: If "bytewise", send data one byte at a time with throttling applied to each byte.
                         If "whole", send the entire message at once. Default is "whole".
        """
        if mode not in ["no_throttle", "bytewise", "whole"]:
            raise ValueError("Invalid mode. Must be 'no_throttle', 'bytewise', or 'whole'.")

        if mode == "no_throttle":
            self.writer.write(msg_bytes)
            await self.writer.drain()
        else:
            await self._throttled_write(msg_bytes, mode, drain)

    def close(self):
        """Close the underlying writer."""
        self.writer.close()

    async def wait_closed(self):
        """Wait for the underlying writer to close."""
        await self.writer.wait_closed()

    @property
    def is_closing(self) -> bool:
        """Check if the underlying writer is closing."""
        return self.writer.is_closing()

    def get_extra_info(self, name, default=None):
        """Get extra info from the underlying writer."""
        return self.writer.get_extra_info(name, default)
