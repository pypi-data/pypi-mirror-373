import asyncio
import threading
from abc import ABC, abstractmethod
from collections import deque
from io import BufferedIOBase, BytesIO
from typing import Iterator

from .utils import DisposableEvent


# Only writing in one thread and reading from one thread is guaranteed
class BaseQueueIO(BufferedIOBase):
    _exc: Exception

    def __init__(self):
        self._ready_async = asyncio.Event()
        self._ready_sync = threading.Event()
        self._evt = DisposableEvent()
        self._eof = False
        self._exc = None

    def readable(self):
        return True

    def writable(self):
        return True

    @abstractmethod
    def _write(self, data: bytes) -> None:
        """write data"""

    def write(self, data: bytes) -> None:
        self._write(data)
        self._evt.set()
        if not self._ready_sync.is_set():
            self._ready_async.set()
            self._ready_sync.set()

    async def aready(self):
        await self._ready_async.wait()

    def ready(self):
        self._ready_sync.wait()

    @abstractmethod
    def _read(self, size: int = -1) -> bytes | None:
        """read data"""

    def read(self, size: int = -1) -> bytes:
        while True:
            if self._exc is not None:
                raise self._exc

            data = self._read(size)

            if data is None:
                if self._eof:
                    return self._read(size) or b""
                self._evt.wait()
            else:
                return data

    def close(self):
        self._eof = True
        self._evt.set()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def exc(self, exc):
        self._exc = exc
        self._evt.set()


class PopIO(BaseQueueIO):
    def __init__(self):
        super().__init__()
        self._buffer = deque()

    def _write(self, data: bytes) -> None:
        self._buffer.append(data)

    def pop(self):
        while self._buffer:
            yield self._buffer.popleft()

    def _read(self, size: int = -1) -> bytes | None:
        ret = []
        length = 0

        while self._buffer and (size < 0 or length < size):
            item = self._buffer.popleft()
            length += len(item)
            ret.append(item)

        if not ret:
            return None

        if length <= size or size < 0:
            return b"".join(ret)

        mem = memoryview(ret[-1])
        last, remain = mem[: size - length], mem[size - length :]
        self._buffer.appendleft(remain)
        ret[-1] = last
        return b"".join(ret)

    def tell(self):
        pass


class QueueIO(BaseQueueIO):
    def __init__(self):
        super().__init__()
        self._buffer = bytearray()

    def _write(self, data: bytes) -> None:
        self._buffer.extend(data)

    def _read(self, size: int = -1) -> bytes | None:
        if size < 0:
            size = len(self._buffer)

        ret = bytes(memoryview(self._buffer)[:size])

        if not ret:
            return None

        del self._buffer[:size]
        return ret


class IterIO:
    def __init__(self, iterator: Iterator[bytes]):
        self._iterator = iter(iterator)
        self._remain = BytesIO()
        self._pivot = 0

    def wriable(self):
        return False

    def seekable(self):
        return False

    def read(self, size: int = -1) -> bytes:
        try:
            while size < 0 or self._remain.tell() < size:
                self._remain.write(next(self._iterator))
        except StopIteration:
            pass

        value = self._remain.getvalue()
        ret = value[:size] if size >= 0 else value

        self._remain.seek(0)
        self._remain.write(value[len(ret) :])
        self._remain.truncate()
        return ret
