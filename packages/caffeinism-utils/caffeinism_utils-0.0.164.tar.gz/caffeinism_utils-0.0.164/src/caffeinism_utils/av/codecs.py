import asyncio
from typing import AsyncIterable

import av

from ..asyncio import run_in_threadpool
from ..io import PopIO
from ..prefetch import aprefetch_iterator
from .io import PyAVReader, PyAVWriter


class AsyncDecoder:
    def __init__(self, aiterator: AsyncIterable[bytes], **kwargs):
        self._aiterator = aiterator
        self._f = PopIO()
        self._kwargs = kwargs

    def decode(self) -> AsyncIterable[av.VideoFrame | av.AudioFrame]:
        async def _pull():
            try:
                async for it in self._aiterator:
                    self._f.write(it)
            finally:
                self._f.close()

        pull_task = asyncio.create_task(_pull())

        def _decode():
            try:
                yield from PyAVReader(self._f, **self._kwargs)
            finally:
                if pull_task.done():
                    pull_task.result()
                else:
                    pull_task.cancel()

        return aprefetch_iterator(_decode())


class AsyncEncoder:
    def __init__(self, writer: PyAVWriter):
        self._writer = writer
        self._f = PopIO()
        writer.lazy_register_path(self._f)

    async def encode(self, frame: av.VideoFrame | av.AudioFrame):
        if isinstance(frame, av.VideoFrame):
            await run_in_threadpool(self._writer.write_video_frame_lazy, frame)
        elif isinstance(frame, av.AudioFrame):
            await run_in_threadpool(self._writer.write_audio_frame_lazy, frame)
        else:
            raise NotImplementedError

    async def aclose(self):
        await run_in_threadpool(self._writer.__exit__, None, None, None)
        await run_in_threadpool(self._f.close)

    def __aiter__(self):
        return self

    async def __anext__(self):
        if ret := await run_in_threadpool(self._f.read):
            return ret
        else:
            raise StopAsyncIteration


class VideoEncoder:
    def __init__(
        self, *, stream: av.VideoStream, codec_context: av.VideoCodecContext, **kwargs
    ):
        for key, value in kwargs.items():
            # if value is not None:
            setattr(codec_context, key, value)

        self.stream = stream
        self.codec_context = codec_context

    @classmethod
    def from_stream(cls, stream: av.VideoStream, width: int, height: int, **kwargs):
        stream_cc = stream.codec_context
        cc = stream.codec.create("video")

        _kwargs = {
            "pix_fmt": stream_cc.pix_fmt,
            "bit_rate": stream_cc.bit_rate,
            "time_base": stream_cc.time_base,
            "color_primaries": stream_cc.color_primaries,
            "color_range": stream_cc.color_range,
            "color_trc": stream_cc.color_trc,
            "framerate": stream_cc.framerate,
            "gop_size": stream_cc.gop_size,
            "qmax": stream_cc.qmax,
            "qmin": stream_cc.qmin,
            "options": stream_cc.options,
        }

        for key, value in kwargs.items():
            _kwargs[key] = value

        return cls(
            stream=stream,
            codec_context=cc,
            width=width,
            height=height,
            **_kwargs,
        )

    def encode(self, frame: av.VideoFrame):
        packets = self.codec_context.encode(frame)
        for packet in packets:
            packet.stream = self.stream
        return packets
