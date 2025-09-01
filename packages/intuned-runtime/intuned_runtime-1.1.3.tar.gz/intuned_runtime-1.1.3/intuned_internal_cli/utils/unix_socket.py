import asyncio
import json
import socket
import struct
from typing import Any


class JSONUnixSocket:
    LENGTH_HEADER_LENGTH = 4

    def __init__(self, sock: socket.socket):
        self.socket = sock

    async def send_json(self, data: Any):
        # Convert data to JSON string and encode to bytes
        data_to_send = json.dumps(data).encode()
        # Calculate length
        length = len(data_to_send)
        # Pack length as 4-byte big-endian unsigned int
        length_header = struct.pack(">I", length)
        # Send length header followed by data
        return await asyncio.to_thread(self.socket.sendall, length_header + data_to_send)

    async def receive_json(self):
        buffer = bytearray()

        while True:
            try:
                # First, ensure we have the length header
                while len(buffer) < self.LENGTH_HEADER_LENGTH:
                    chunk = await asyncio.to_thread(self.socket.recv, 4096)
                    if not chunk:
                        return
                    buffer.extend(chunk)

                # Read the message length
                length = struct.unpack(">I", buffer[: self.LENGTH_HEADER_LENGTH])[0]
                total_length = length + self.LENGTH_HEADER_LENGTH

                # Read the full message
                while len(buffer) < total_length:
                    chunk = await asyncio.to_thread(self.socket.recv, 4096)
                    if not chunk:
                        return
                    buffer.extend(chunk)

                # Extract the JSON data
                data = buffer[self.LENGTH_HEADER_LENGTH : total_length]
                # Remove processed data from buffer
                buffer = buffer[total_length:]
                # Parse and yield the JSON data
                yield json.loads(data.decode())

            except OSError:
                break
