import sys
import asyncio
from contextlib import asynccontextmanager


@asynccontextmanager
async def stdio_server():
    """
    Async context manager for MCP stdio transport.
    Mirrors the monorepo implementation to ensure compatibility.
    """
    loop = asyncio.get_running_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    writer_transport, writer_protocol = await loop.connect_write_pipe(asyncio.streams.FlowControlMixin, sys.stdout)
    writer = asyncio.StreamWriter(writer_transport, writer_protocol, reader, loop)
    try:
        yield (reader, writer)
    finally:
        writer.close()
        await writer.wait_closed()


