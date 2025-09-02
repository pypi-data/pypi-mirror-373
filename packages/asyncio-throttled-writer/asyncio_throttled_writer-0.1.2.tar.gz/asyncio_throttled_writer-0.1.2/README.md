# AsyncIO Throttled Writer

A Python library providing a throttled stream writer for asyncio applications. This library helps prevent network flooding by enforcing minimum intervals between write operations while maintaining the asyncio StreamWriter interface.

## Features

- **Throttling Control**: Set minimum intervals between write operations
- **Multiple Write Modes**: Support for bytewise, whole message, and non-throttled writes
- **AsyncIO Compatible**: Drop-in replacement for asyncio.StreamWriter
- **Thread-Safe**: Uses asyncio locks to ensure safe concurrent access
- **Flexible**: Configurable throttling intervals and optional drain operations

## Installation

```bash
pip install asyncio-throttled-writer
```

## Quick Start

```python
import asyncio
from asyncio_throttled_writer import ThrottledStreamWriter

async def example():
    # Create a regular asyncio connection
    reader, writer = await asyncio.open_connection('example.com', 80)
    
    # Wrap it with ThrottledStreamWriter
    throttled_writer = ThrottledStreamWriter(writer)
    
    # Set minimum interval between writes (in milliseconds)
    throttled_writer.set_min_send_interval_ms(100)  # 100ms between writes
    
    # Write data with throttling
    await throttled_writer.write(b'Hello, ')
    await throttled_writer.write(b'World!')
    
    # Clean up
    throttled_writer.close()
    await throttled_writer.wait_closed()

# Run the example
asyncio.run(example())
```

## API Reference

### ThrottledStreamWriter

A throttled wrapper around asyncio.StreamWriter that enforces minimum intervals between write operations.

#### Constructor

```python
ThrottledStreamWriter(writer: StreamWriter)
```

- `writer`: An asyncio StreamWriter instance to wrap

#### Methods

##### `set_min_send_interval_ms(ms: float) -> None`

Set the minimum interval between write operations.

- `ms`: Minimum interval in milliseconds (negative values are treated as 0)

##### `async write(msg_bytes: bytes, mode: str = "whole", drain: bool = False) -> None`

Write bytes with optional throttling.

- `msg_bytes`: The bytes to write
- `mode`: Write mode - one of:
  - `"whole"` (default): Send entire message at once with throttling
  - `"bytewise"`: Send one byte at a time with throttling per byte
  - `"no_throttle"`: Send immediately without throttling
- `drain`: If True, call drain after each write operation

##### `async drain() -> None`

Drain the underlying writer buffer.

##### `close() -> None`

Close the underlying writer.

##### `async wait_closed() -> None`

Wait for the underlying writer to close completely.

##### Other Methods

The class also provides all standard StreamWriter methods:
- `can_write_eof()`
- `write_eof()`
- `writelines(data)`
- `get_extra_info(name, default=None)`
- `is_closing` (property)
- `transport` (property)

## Usage Examples

### Basic Throttling

```python
import asyncio
from asyncio_throttled_writer import ThrottledStreamWriter

async def send_data():
    reader, writer = await asyncio.open_connection('localhost', 8080)
    throttled = ThrottledStreamWriter(writer)
    
    # Throttle to maximum 10 writes per second
    throttled.set_min_send_interval_ms(100)
    
    for i in range(5):
        await throttled.write(f"Message {i}\n".encode())
    
    throttled.close()
    await throttled.wait_closed()
```

### Bytewise Throttling

```python
async def slow_char_by_char():
    reader, writer = await asyncio.open_connection('localhost', 8080)
    throttled = ThrottledStreamWriter(writer)
    
    # Very slow: 1 character per second
    throttled.set_min_send_interval_ms(1000)
    
    # Send each byte with throttling
    await throttled.write(b"Hello World!", mode="bytewise")
    
    throttled.close()
    await throttled.wait_closed()
```

### Mixed Throttling and Non-Throttled Writes

```python
async def mixed_writes():
    reader, writer = await asyncio.open_connection('localhost', 8080)
    throttled = ThrottledStreamWriter(writer)
    
    throttled.set_min_send_interval_ms(500)
    
    # Fast initial handshake
    await throttled.write(b"CONNECT\n", mode="no_throttle")
    
    # Throttled data transmission
    for i in range(3):
        await throttled.write(f"DATA {i}\n".encode(), mode="whole")
    
    # Fast closing
    await throttled.write(b"QUIT\n", mode="no_throttle")
    
    throttled.close()
    await throttled.wait_closed()
```

## Use Cases

- **Rate-Limited APIs**: Prevent exceeding API rate limits
- **Network Congestion Control**: Avoid overwhelming slower network connections
- **Protocol Compliance**: Meet timing requirements of specific protocols
- **Testing**: Simulate slow network conditions for testing purposes
- **Embedded Systems**: Control data flow to resource-constrained devices

## Requirements

- Python 3.8+
- asyncio (built-in)

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
