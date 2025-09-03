import fractions
import functools
import io
import threading
from abc import ABC, abstractmethod
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
from types import TracebackType
from typing import Iterable

import av
import av.container
import av.frame
import av.stream
import numpy as np
from pydub import AudioSegment

from ..asyncio import run_in_threadpool
from .filters import AlphaExtractor, AlphaMerger, BaseAlphaMerger, NotAlphaMerger

TIME_BASE = fractions.Fraction(1, 90000)


class PyAVInterface(ABC):
    _container: av.container.Container
    _streams: tuple[av.VideoStream, ...]

    def __init__(self):
        self.__container_init_lock = threading.Lock()

    def _init_container(self):
        if self._container is None:
            with self.__container_init_lock:
                self._create_container()

    @abstractmethod
    def _create_container(self):
        """create container"""

    @property
    def container(self) -> av.container.Container:
        self._init_container()
        return self._container

    @property
    def streams(self) -> tuple[av.VideoStream, ...]:
        self._init_container()
        return self._streams

    @property
    def fps(self):
        return self.streams[0].base_rate or self.streams[0].codec_context.framerate

    @property
    def width(self):
        return self.streams[0].codec_context.width

    @property
    def height(self):
        return self.streams[0].codec_context.height

    @property
    def pix_fmt(self):
        return self.streams[0].format.name

    def __enter__(self):
        self.container.__enter__()
        return self

    def __exit__(self, *args):
        self.container.__exit__(*args)

    async def __aenter__(self):
        await run_in_threadpool(self.container.__enter__)

    async def __aexit__(self):
        await run_in_threadpool(self.container.__exit__)


class BasePyAVReader(PyAVInterface):
    container: av.container.InputContainer

    def __init__(
        self,
        path,
        *,
        format: str,
        buffer_size: int,
        filter: tuple[type[av.frame.Frame]],
        options={},
    ):
        super().__init__()
        self._container = None
        self._path = path
        self._format = format
        self._buffer_size = buffer_size
        self._filter = filter
        self._options = options

        self._codec_contexts = {}

    @abstractmethod
    def __iter__(self):
        raise NotImplementedError

    def _create_container(self):
        if self._container is None:
            container = av.open(
                self._path,
                "r",
                format=self._format,
                buffer_size=self._buffer_size,
                options=self._options,
            )

            self._streams = tuple()
            if av.VideoFrame in self._filter:
                self._streams = container.streams.video
                for stream in self._streams:
                    if stream.codec_context.name in ("vp8", "vp9"):
                        if stream.codec_context.name == "vp8":
                            codec_name = "libvpx"
                        elif stream.codec_context.name == "vp9":
                            codec_name = "libvpx-vp9"
                        codec = av.codec.Codec(codec_name, "r")
                        self._codec_contexts[stream] = codec.create()
                    else:
                        self._codec_contexts[stream] = stream.codec_context

            self._audio_streams = tuple()
            if av.AudioFrame in self._filter:
                self._audio_streams = container.streams.audio
                for stream in self._audio_streams:
                    self._codec_contexts[stream] = stream.codec_context

            self._container = container

    @property
    def codec_contexts(self) -> dict[av.stream.Stream, av.CodecContext]:
        self._init_container()
        return self._codec_contexts

    @property
    def audio_streams(self) -> tuple[av.AudioStream, ...]:
        self._init_container()
        return self._audio_streams


class PyAVReader(BasePyAVReader):
    def __init__(
        self,
        path,
        start=0,
        end=(2 << 62) - 1,
        *,
        format=None,
        buffer_size=32768,
        filter=(av.VideoFrame, av.AudioFrame),
        options={},
    ):
        super().__init__(
            path, format=format, buffer_size=buffer_size, filter=filter, options=options
        )
        self.start = start
        self.end = end
        self._alpha_merger = None

    @property
    def alpha_merger(self) -> BaseAlphaMerger:
        if self._alpha_merger is None:
            if len(self.streams) < 2:
                self._alpha_merger = NotAlphaMerger()
            elif len(self.streams) == 2:
                self._alpha_merger = AlphaMerger(
                    self.streams[0].format.name, self.streams[1].format.name
                )
            else:
                raise NotImplementedError
        return self._alpha_merger

    def __iter__(self):
        with self:
            for packet in self.container.demux(self.streams + self.audio_streams):
                for frame in self.codec_contexts[packet.stream].decode(packet):
                    if (
                        packet.stream in self.streams
                        and not (
                            self.start
                            <= round(frame.pts * self.fps * frame.time_base)
                            < self.end
                        )
                        or packet.stream in self.audio_streams
                        and not (
                            self.start - frame.time_base
                            <= frame.pts * frame.time_base
                            < self.end + frame.time_base
                        )
                    ):
                        continue

                    if packet.stream in self.audio_streams:
                        yield frame
                    elif packet.stream is self.streams[0]:
                        self.alpha_merger.push_image(frame)
                    else:
                        self.alpha_merger.push_alpha(frame)

                while (result := self.alpha_merger.pull()) is not None:
                    yield result
        if isinstance(self.alpha_merger, AlphaMerger):
            self.alpha_merger.close()


def create_stream(
    container: av.container.OutputContainer,
    codec_name: str,
    rate: int | fractions.Fraction,
    width: int,
    height: int,
    pix_fmt: str,
    bit_rate: int,
    time_base: fractions.Fraction,
    options: dict,
):
    stream = container.add_stream(
        codec_name=codec_name,
        rate=rate,
        width=width,
        height=height,
        pix_fmt=pix_fmt,
        bit_rate=bit_rate,
        time_base=time_base,
    )
    stream.options = options
    return stream


class PyAVWriter(PyAVInterface):
    container: av.container.OutputContainer

    def __init__(
        self,
        path: str | Path | io.IOBase | None,
        fps: fractions.Fraction = None,
        *,
        width: int = 640,
        height: int = 480,
        codec_name="libvpx-vp9",
        pix_fmt="yuva420p",
        buffer_size=32768,
        bit_rate=1024 * 1024,
        alpha_stream: bool | str = False,
        audio_codec_name=None,
        audio_sample_rate=48000,
        audio_format="s16",
        audio_layout="stereo",
        audio_bit_rate=192000,
        format=None,
        options={},
        container_options={},
    ):
        super().__init__()

        assert codec_name is not None or audio_codec_name is not None

        if codec_name is not None:
            if pix_fmt == "rgb24" and codec_name == "rawvideo" and alpha_stream:
                pix_fmt = "rgba"
                alpha_stream = False
            elif (
                pix_fmt == "yuv420p"
                and codec_name.startswith("libvpx")
                and alpha_stream
            ):
                pix_fmt = "yuva420p"
                alpha_stream = False
            elif (pix_fmt.startswith("yuva") or pix_fmt == "rgba") and alpha_stream:
                alpha_stream = False

        self._path = path
        self._width = width
        self._height = height
        self._fps = fps
        self._codex_contexts: dict[av.VideoStream, av.VideoCodecContext] = {}
        self._codec_name = codec_name
        self._pix_fmt = pix_fmt
        self._buffer_size = buffer_size
        self._bit_rate = bit_rate
        self._alpha_stream = alpha_stream
        self._audio_codec_name = audio_codec_name
        self._audio_sample_rate = audio_sample_rate
        self._audio_format = audio_format
        self._audio_layout = audio_layout
        self._audio_bit_rate = audio_bit_rate
        self._format = format
        self._options = options
        self._container_options = container_options

        self._container = None
        self._alpha_extractor = None

        self.__frames = 0

        self.pool = None
        self.future: Future[av.VideoFrame | av.AudioFrame] = None

        self.write_lazy = self.lazy(self.write)
        self.write_video_frame_lazy = self.lazy(self.write_video_frame)
        self.write_audio_lazy = self.lazy(self.write_audio)
        self.write_audio_frame_lazy = self.lazy(self.write_audio_frame)

    def lazy_register_path(self, path: str | Path | io.IOBase):
        if self._path is not None:
            raise ValueError
        self._path = path

    def _create_container(self):
        if self._path is None:
            raise ValueError

        container = av.open(
            self._path,
            "w",
            buffer_size=self._buffer_size,
            format=self._format,
            options=self._options,
            container_options=self._container_options,
        )
        streams = []
        if self._codec_name is not None:
            pix_fmts = [self._pix_fmt]
            if self._alpha_stream:
                pix_fmts.append(
                    self._pix_fmt if self._alpha_stream == True else self._alpha_stream
                )

            for pf in pix_fmts:
                stream = create_stream(
                    container,
                    codec_name=self._codec_name,
                    rate=self._fps,
                    width=self._width,
                    height=self._height,
                    pix_fmt=pf,
                    bit_rate=self._bit_rate,
                    time_base=TIME_BASE,
                    options=self._options,
                )
                streams.append(stream)

        audio_stream = None
        if self._audio_codec_name is not None:
            audio_stream = container.add_stream(
                codec_name=self._audio_codec_name, rate=self._audio_sample_rate
            )
            audio_stream.format = self._audio_format
            audio_stream.layout = self._audio_layout
            audio_stream.bit_rate = self._audio_bit_rate

        self._streams = streams
        self._audio_stream = audio_stream
        self._container = container

    @property
    def audio_stream(self) -> av.AudioStream:
        self._init_container()
        return self._audio_stream

    @property
    def alpha_extractor(self):
        if self._alpha_extractor is None and self._alpha_stream:
            self._alpha_extractor = AlphaExtractor()
        return self._alpha_extractor

    def array_to_frame(self, array):
        if self.streams[0].pix_fmt.startswith("yuva") or len(self.streams) == 2:
            frame = av.VideoFrame.from_ndarray(array, format="rgba")
        else:
            frame = av.VideoFrame.from_ndarray(array[..., :3], format="rgb24")
        return frame

    def lazy(self, func):
        @functools.wraps(func)
        def _func(*args, **kwargs):
            if self.pool is None:
                self.pool = ThreadPoolExecutor(1)

            if self.future is not None:
                self.future.result()
                del self.future

            self.future = self.pool.submit(func, *args, **kwargs)

        return func

    def write(self, array):
        frame = self.array_to_frame(array)
        self.write_video_frame(frame)

    def create_codec_context(self, stream: av.VideoStream):
        stream_cc = stream.codec_context
        cc = stream.codec.create("video")

        cc.width = stream.width
        cc.height = stream.height

        cc.pix_fmt = stream_cc.pix_fmt
        cc.bit_rate = stream_cc.bit_rate
        cc.time_base = stream_cc.time_base
        cc.color_primaries = stream_cc.color_primaries
        cc.color_range = stream_cc.color_range
        cc.color_trc = stream_cc.color_trc

        cc.framerate = stream_cc.framerate
        cc.gop_size = stream_cc.gop_size
        cc.qmax = stream_cc.qmax
        cc.qmin = stream_cc.qmin

        cc.options = stream_cc.options

        return cc

    def _encode_video_frame(self, stream: av.VideoStream, frame: av.VideoFrame):
        cc = self._codex_contexts.get(stream.index)
        if cc is None:
            stream.width = frame.width
            stream.height = frame.height
            cc = stream.codec_context
            if cc.coded_width == cc.coded_height == 0:
                pass
            elif (cc.coded_width, cc.coded_height) == (frame.width, frame.height):
                pass
            else:
                cc = self.create_codec_context(stream)

            self._codex_contexts[stream.index] = cc
        elif (stream.width, stream.height) != (frame.width, frame.height):
            stream.width = frame.width
            stream.height = frame.height
            for packet in cc.encode():
                packet.stream = stream
                yield packet
            cc = self.create_codec_context(stream)
            self._codex_contexts[stream.index] = cc

        for packet in cc.encode_lazy(frame):
            packet.stream = stream
            yield packet

    def encode_video_frame(self, frame: av.VideoFrame):
        frames = [frame]
        if self.alpha_extractor is not None:
            frames.append(self.alpha_extractor(frame))

        for stream, frame in zip(self.streams, frames):
            frame.time_base = TIME_BASE
            frame.pts = round(self.__frames / self.fps / TIME_BASE)
            yield from self._encode_video_frame(stream, frame)

        self.__frames += 1

    def write_video_frame(self, frame: av.VideoFrame):
        for packet in self.encode_video_frame(frame):
            self.container.mux_one(packet)

    def encode_video_frames(self, iterator: Iterable[av.VideoFrame]):
        for frame in iterator:
            for packet in self.encode_video_frame(frame):
                yield packet

    def write_audio(self, audio_segment: AudioSegment):
        audio_segment = (
            audio_segment.set_channels(self.audio_stream.layout.nb_channels)
            .set_sample_width(self.audio_stream.format.bytes)
            .set_frame_rate(self.audio_stream.sample_rate)
        )
        frame = av.AudioFrame.from_ndarray(
            np.array(audio_segment.get_array_of_samples()).reshape(1, -1),
            format=self.audio_stream.format.name,
            layout=self.audio_stream.layout.name,
        )
        frame.sample_rate = audio_segment.frame_rate
        self.write_audio_frame(frame)

    def write_audio_frame(self, frame: av.AudioFrame):
        for packet in self.encode_audio_frames([frame]):
            self.container.mux_one(packet)

    def encode_audio_frames(self, iterator: Iterable[av.AudioFrame]):
        for frame in iterator:
            for packet in self.audio_stream.codec_context.encode_lazy(frame):
                packet.stream = self.audio_stream
                yield packet

    def flush(self):
        if self.future is not None:
            self.future.result()
            del self.future
            self.future = None

        if self.alpha_extractor is not None:
            self.alpha_extractor.close()
        for stream in self.streams:
            cc = self._codex_contexts.get(stream.index)
            if cc is not None:
                self.container.mux(cc.encode())
        if self.audio_stream is not None:
            self.container.mux(self.audio_stream.encode())

    def __exit__(
        self,
        t: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ):
        if exc is None:
            self.flush()
        super().__exit__(t, exc, tb)
