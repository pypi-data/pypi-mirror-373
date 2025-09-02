import pyarrow as pa


class WriteBuffer:
    """used internally to capture the output of a stream in a memory efficient way"""

    def __init__(self):
        self.queue = []
        self.buf = b""
        self.closed = False

    def write(self, data: bytes | pa.Buffer):
        if isinstance(data, pa.Buffer):
            x: pa.Buffer = data
            data = x.to_pybytes()

        if len(self.buf) + len(data) > 1024 * 1024:
            self.queue.append(self.buf)
            self.buf = b""
        # concatenate small chunks
        self.buf += data

    def writable(self) -> bool:
        return True

    def readable(self) -> bool:
        return False

    def flush(self, partial: bool = False) -> list[bytes]:
        out = self.queue
        self.queue = []
        if not partial and self.buf != b"":
            out.append(self.buf)
            self.buf = b""
        return out
