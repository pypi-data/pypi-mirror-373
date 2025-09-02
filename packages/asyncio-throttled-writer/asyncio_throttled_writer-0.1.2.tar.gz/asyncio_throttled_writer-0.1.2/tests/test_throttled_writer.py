"""
Tests for ThrottledStreamWriter class.
"""
import asyncio
import time
import pytest
from unittest.mock import Mock
from asyncio_throttled_writer import ThrottledStreamWriter


class MockStreamWriter:
    """Mock StreamWriter for testing purposes."""

    def __init__(self):
        self.written_data = []
        self.closed = False
        self.is_closing_flag = False
        self.transport_mock = Mock()
        self.drain_called = 0

    def write(self, data):
        self.written_data.append(data)

    async def drain(self):
        self.drain_called += 1

    def close(self):
        self.closed = True
        self.is_closing_flag = True

    async def wait_closed(self):
        pass

    def is_closing(self):
        return self.is_closing_flag

    def can_write_eof(self):
        return True

    def write_eof(self):
        pass

    def get_extra_info(self, name, default=None):
        return f"extra_info_{name}" if name else default

    @property
    def transport(self):
        return self.transport_mock

    async def start_tls(self, sslcontext, *, server_hostname=None,
                       ssl_handshake_timeout=None, ssl_shutdown_timeout=None):
        return Mock()

    def __del__(self, warnings=...):
        pass


@pytest.fixture
def mock_writer():
    """Create a mock StreamWriter for testing."""
    return MockStreamWriter()


@pytest.fixture
def throttled_writer(mock_writer):
    """Create a ThrottledStreamWriter with mock writer."""
    return ThrottledStreamWriter(mock_writer)


def test_initialization(mock_writer):
    """Test that ThrottledStreamWriter initializes correctly."""
    throttled = ThrottledStreamWriter(mock_writer)
    assert throttled.writer == mock_writer
    assert throttled._min_send_interval_ns == 1_000_000  # 1ms default
    assert throttled._last_send_time_ns == 0
    assert isinstance(throttled._send_lock, asyncio.Lock)


def test_set_min_send_interval_ms(throttled_writer):
    """Test setting minimum send interval."""
    # Test positive value
    throttled_writer.set_min_send_interval_ms(100)
    assert throttled_writer._min_send_interval_ns == 100_000_000

    # Test zero value
    throttled_writer.set_min_send_interval_ms(0)
    assert throttled_writer._min_send_interval_ns == 0

    # Test negative value (should be treated as 0)
    throttled_writer.set_min_send_interval_ms(-50)
    assert throttled_writer._min_send_interval_ns == 0


@pytest.mark.asyncio
async def test_write_no_throttle(throttled_writer, mock_writer):
    """Test write without throttling."""
    data = b"test data"
    await throttled_writer.write(data, mode="no_throttle")

    assert mock_writer.written_data == [data]
    assert mock_writer.drain_called == 1


@pytest.mark.asyncio
async def test_write_whole_mode(throttled_writer, mock_writer):
    """Test write in whole mode."""
    throttled_writer.set_min_send_interval_ms(0)  # No delay for testing
    data = b"test data"

    await throttled_writer.write(data, mode="whole")

    assert mock_writer.written_data == [data]


@pytest.mark.asyncio
async def test_write_bytewise_mode(throttled_writer, mock_writer):
    """Test write in bytewise mode."""
    throttled_writer.set_min_send_interval_ms(0)  # No delay for testing
    data = b"abc"

    await throttled_writer.write(data, mode="bytewise")

    expected = [bytes([b]) for b in data]
    assert mock_writer.written_data == expected


@pytest.mark.asyncio
async def test_write_invalid_mode(throttled_writer):
    """Test write with invalid mode raises ValueError."""
    with pytest.raises(ValueError, match="Invalid mode"):
        await throttled_writer.write(b"test", mode="invalid")


@pytest.mark.asyncio
async def test_throttling_timing(mock_writer):
    """Test that throttling actually delays writes."""
    throttled = ThrottledStreamWriter(mock_writer)
    throttled.set_min_send_interval_ms(50)  # 50ms delay

    start_time = time.monotonic()

    # First write should be immediate
    await throttled.write(b"first", mode="whole")
    first_write_time = time.monotonic()

    # Second write should be delayed
    await throttled.write(b"second", mode="whole")
    second_write_time = time.monotonic()

    # Check that there was a delay between writes
    delay = second_write_time - first_write_time
    assert delay >= 0.045  # Allow for some timing variance

    assert mock_writer.written_data == [b"first", b"second"]


def test_close(throttled_writer, mock_writer):
    """Test the close method."""
    throttled_writer.close()
    assert mock_writer.closed


def test_transport_property(throttled_writer, mock_writer):
    """Test the transport property."""
    assert throttled_writer.transport == mock_writer.transport_mock


@pytest.mark.asyncio
async def test_drain_method(throttled_writer, mock_writer):
    """Test the drain method."""
    await throttled_writer.drain()
    assert mock_writer.drain_called == 1


@pytest.mark.asyncio
async def test_realistic_usage_pattern(mock_writer):
    """Test a realistic usage pattern."""
    throttled = ThrottledStreamWriter(mock_writer)
    throttled.set_min_send_interval_ms(10)

    # Simulate a protocol handshake
    await throttled.write(b"HELLO\n", mode="no_throttle")

    # Send some throttled data
    for i in range(3):
        await throttled.write(f"DATA {i}\n".encode(), mode="whole")

    # Close connection
    await throttled.write(b"BYE\n", mode="no_throttle")
    throttled.close()

    expected_data = [
        b"HELLO\n",
        b"DATA 0\n",
        b"DATA 1\n",
        b"DATA 2\n",
        b"BYE\n"
    ]
    assert mock_writer.written_data == expected_data
    assert mock_writer.closed
