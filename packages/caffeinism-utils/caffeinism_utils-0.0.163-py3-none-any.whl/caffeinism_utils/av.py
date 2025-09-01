import asyncio
import fractions
import functools
import io
import threading
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
from types import TracebackType
from typing import AsyncIterator, Callable, Iterable, Iterator

import av
import av.container
import av.filter
import av.filter.context
import av.frame
import av.stream
import numpy as np
from pydub import AudioSegment

from .asyncio import run_in_threadpool
from .io import PopIO
from .prefetch import aprefetch_iterator

TIME_BASE = fractions.Fraction(1, 90000)


class FilterContextOutput:
    def __init__(
        self, filter_context: av.filter.context.FilterContext, output_idx: int
    ):
        self._filter_context = filter_context
        self._output_idx = output_idx

    def push(self, frame: av.VideoFrame | None):
        self._filter_context.push(frame)

    def pull(self):
        return self._filter_context.pull()

    def link_to(self, input: "FilterContext", input_idx: int = 0):
        self._filter_context.link_to(
            input._filter_context,
            output_idx=self._output_idx,
            input_idx=input_idx,
        )

    def __rshift__(self, right: "FilterContext"):
        self.link_to(right, input_idx=0)
        return right.output()


class FilterContext:
    def __init__(self, filter_context: av.filter.context.FilterContext):
        self._filter_context = filter_context

    def process_command(
        self, cmd: str, arg: str | None = None, res_len: int = 1024, flags: int = 0
    ):
        self._filter_context.process_command(
            cmd=cmd, arg=arg, res_len=res_len, flags=flags
        )

    def output(self) -> list[FilterContextOutput] | FilterContextOutput:
        len_output = len(self._filter_context.outputs)
        if len_output < 2:
            return FilterContextOutput(self._filter_context, 0)
        else:
            return [
                FilterContextOutput(self._filter_context, i) for i in range(len_output)
            ]

    def __rrshift__(self, left: Iterable[FilterContextOutput] | FilterContextOutput):
        if isinstance(left, Iterable):
            for i, it in enumerate(left):
                it.link_to(self, input_idx=i)
        elif isinstance(left, FilterContext):
            left >> self
        else:
            raise NotImplementedError

        return self.output()


class Graph:
    def __init__(self):
        self._graph = av.filter.Graph()

    def add(
        self, filter: str | av.filter.Filter, args: str = None, **kwargs: str
    ) -> FilterContext:
        return FilterContext(self._graph.add(filter, args, **kwargs))

    def add_buffer(
        self,
        template: av.VideoStream | None = None,
        width: int | None = None,
        height: int | None = None,
        format: av.VideoFormat | None = None,
        name: str | None = None,
        time_base: fractions.Fraction | None = None,
    ):
        buffer = self._graph.add_buffer(
            template=template,
            width=width,
            height=height,
            format=format,
            name=name,
            time_base=time_base,
        )
        return FilterContextOutput(buffer, 0)

    def push(self, frame: av.VideoFrame | None):
        self._graph.push(frame)

    def pull(self):
        return self._graph.pull()

    def configure(self, auto_buffer: bool = True, force: bool = False):
        return self._graph.configure(auto_buffer=auto_buffer, force=force)


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
    def alpha_merger(self) -> "BaseAlphaMerger":
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


PyAVDisposableReader = PyAVReader


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

    def encode_video_frames(self, iterator: Iterator[av.VideoFrame]):
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

    def encode_audio_frames(self, iterator: Iterator[av.AudioFrame]):
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


class Filter(ABC):
    graph: av.filter.Graph | None

    def __init__(self):
        self.graph = None
        self._kwargs = {}

    def rebuild_graph(self, **kwargs):
        if self._kwargs != kwargs:
            self.close()
            self.graph = av.filter.Graph()
            self._rebuild_graph(**kwargs)
            self.graph.configure()
            self._kwargs = kwargs

    @abstractmethod
    def _rebuild_graph(**kwargs):
        "rebuild graph impl"

    def close(self):
        if self.graph is not None:
            self.graph.push(None)


class _Formatter(Filter):
    def __init__(self, to_pix_fmt: str):
        super().__init__()

        self._to_pix_fmt = to_pix_fmt

    def _rebuild_graph(self, width: int, height: int, pix_fmt: str):
        src = self.graph.add_buffer(
            width=width,
            height=height,
            format=pix_fmt,
            time_base=fractions.Fraction(1, 1000),
        )

        reformat = self.graph.add("format", self._to_pix_fmt)
        src.link_to(reformat)

        sink = self.graph.add("buffersink")
        reformat.link_to(sink)

    def __call__(self, frame: av.VideoFrame) -> av.VideoFrame:
        self.rebuild_graph(
            width=frame.width, height=frame.height, pix_fmt=frame.format.name
        )
        self.graph.push(frame)
        ret = self.graph.pull()
        ret.pts = None
        return ret


def to_rgba(reader: Iterator[av.VideoFrame]):
    formatter: dict[str, _Formatter] = {}

    for frame in reader:
        if frame.format.name not in formatter:
            formatter[frame.format.name] = _Formatter("rgba")

        yield formatter[frame.format.name](frame)

    for f in formatter.values():
        f.close()


def to_array(iterator: list[av.VideoFrame]):
    for frame in iterator:
        yield frame.to_ndarray()


class _AlphaExtractor(Filter):
    def __init__(self):
        super().__init__()

    def _rebuild_graph(self, width: int, height: int, pix_fmt: str):
        src = self.graph.add_buffer(
            width=width,
            height=height,
            format=pix_fmt,
            time_base=fractions.Fraction(1, 1000),
        )

        alphaextract = self.graph.add("alphaextract")
        src.link_to(alphaextract)

        alpha = self.graph.add("buffersink")
        alphaextract.link_to(alpha)

    def __call__(self, frame: av.VideoFrame):
        self.rebuild_graph(
            width=frame.width, height=frame.height, pix_fmt=frame.format.name
        )
        self.graph.push(frame)
        return self.graph.pull()


class AlphaExtractor:
    def __init__(self):
        self.alpha_extractors = defaultdict(_AlphaExtractor)

    def __call__(self, frame: av.VideoFrame):
        assert frame.height % 2 == 0

        return self.alpha_extractors[frame.format.name](frame)

    def close(self):
        for it in self.alpha_extractors.values():
            it.close()


class BaseAlphaMerger:
    @abstractmethod
    def push_image(self, frame: av.VideoFrame):
        """push image to merger"""

    @abstractmethod
    def push_alpha(self, frame: av.VideoFrame):
        """push alpha to merger"""

    @abstractmethod
    def pull(self):
        """pull merged image"""


class AlphaMerger(BaseAlphaMerger):
    def __init__(self, image_pix_fmt: str, alpha_pix_fmt: str):
        self.alpha_mergers = defaultdict(
            lambda: _AlphaMerger(image_pix_fmt, alpha_pix_fmt)
        )

    def push_image(self, frame: av.VideoFrame):
        self.alpha_mergers[(frame.width, frame.height)].push_image(frame)

    def push_alpha(self, frame: av.VideoFrame):
        self.alpha_mergers[(frame.width, frame.height)].push_alpha(frame)

    def pull(self) -> av.VideoFrame:
        keys = list(self.alpha_mergers)
        for key in keys:
            ret = self.alpha_mergers[key].pull()
            if ret is not None:
                return ret

            if len(keys) > 1:
                del self.alpha_mergers[key]

    def close(self):
        for it in self.alpha_mergers.values():
            it.close()


class _AlphaMerger(Filter, BaseAlphaMerger):
    def __init__(self, image_pix_fmt: str, alpha_pix_fmt: str):
        super().__init__()
        self.image_pix_fmt = image_pix_fmt
        self.alpha_pix_fmt = alpha_pix_fmt

    def _rebuild_graph(
        self,
        width: int,
        height: int,
    ):
        self.image = self.graph.add_buffer(
            width=width,
            height=height,
            format=self.image_pix_fmt,
            time_base=fractions.Fraction(1, 1000),
        )
        self.alpha = self.graph.add_buffer(
            width=width,
            height=height,
            format=self.alpha_pix_fmt,
            time_base=fractions.Fraction(1, 1000),
        )

        format = self.graph.add("format", "gray")
        self.alpha.link_to(format)

        alphamerge = self.graph.add("alphamerge")
        self.image.link_to(alphamerge, input_idx=0)
        format.link_to(alphamerge, input_idx=1)

        self.result = self.graph.add("buffersink")
        alphamerge.link_to(self.result)

    def push_image(self, frame: av.VideoFrame):
        self.rebuild_graph(width=frame.width, height=frame.height)
        self.image.push(frame)

    def push_alpha(self, frame: av.VideoFrame):
        self.rebuild_graph(width=frame.width, height=frame.height)
        self.alpha.push(frame)

    def pull(self) -> av.VideoFrame:
        try:
            return self.graph.pull()
        except BlockingIOError:
            return None


class NotAlphaMerger(BaseAlphaMerger):
    def __init__(self):
        self.queue = deque()

    def push_image(self, frame: av.VideoFrame):
        self.queue.append(frame)

    def push_alpha(self, frame: av.VideoFrame):
        raise NotImplementedError

    def pull(self) -> av.VideoFrame:
        try:
            return self.queue.popleft()
        except IndexError:
            return None


def get_dst_size(dst_size: tuple[int, int], background_image: np.ndarray):
    target_height, target_width = background_image.shape[:2]

    width, height = dst_size
    if target_height / height < target_width / width:
        width = round(target_height / height * width)
        height = target_height
    else:
        height = round(target_width / width * height)
        width = target_width

    width, height = width - width % 16, height - height % 16

    bg_top = (target_height - height) // 2
    bg_left = (target_width - width) // 2

    return (width, height), background_image[
        bg_top : bg_top + height, bg_left : bg_left + width, :
    ]


def get_src_size(
    left: float,
    top: float,
    height: float,
    dst_size: tuple[int, int],
    src_size: tuple[int, int],
):
    dst_width, dst_height = dst_size
    src_width, src_height = src_size

    target_frame_height = dst_height * height
    frame_width = min(
        round(src_width * target_frame_height / src_height),
        dst_width,
    )
    frame_height = round(src_height * frame_width / src_width)

    left = (left + 1) / 2
    left_limit = dst_width - frame_width

    x = round(left * left_limit)
    y = round(top * dst_height)

    return (x, y), (frame_width, frame_height)


class BaseOverlayer(Filter):
    def __init__(
        self,
        background_image: np.ndarray,
        x: int,
        y: int,
        pix_fmt: str = "yuva420p",
        mode: str = "straight",
        pre_overlay_filter: Callable[
            [av.filter.Graph, av.filter.context.FilterContext],
            av.filter.context.FilterContext,
        ] = lambda g, f: f,
        post_overlay_filter: Callable[
            [av.filter.Graph, av.filter.context.FilterContext],
            av.filter.context.FilterContext,
        ] = lambda g, f: f,
    ):
        super().__init__()
        self.pre_overlay_filter = pre_overlay_filter
        self.post_overlay_filter = post_overlay_filter

        self.background_image = av.VideoFrame.from_ndarray(
            background_image,
            format="rgb24" if background_image.shape[-1] == 3 else "rgba",
        )
        self.x = x
        self.y = y
        self.pix_fmt = pix_fmt
        self.mode = mode
        self.lock = threading.Lock()

    def _rebuild_graph(
        self,
        width: int,
        height: int,
        pix_fmt: str,
        x: int,
        y: int,
        bg_width: int,
        bg_height: int,
    ):
        self.src = self.graph.add_buffer(
            width=width,
            height=height,
            format=pix_fmt,
            time_base=fractions.Fraction(1, 1000),
        )
        self.dst = self.graph.add_buffer(
            width=bg_width,
            height=bg_height,
            format=self.background_image.format.name,
            time_base=fractions.Fraction(1, 1000),
        )

        pre_filtered = self.pre_overlay_filter(self.graph, self.src)

        overlay = self.graph.add(
            "overlay", f"x={x}:y={y}:alpha={self.mode}:format=auto"
        )
        self.dst.link_to(overlay, input_idx=0)
        pre_filtered.link_to(overlay, input_idx=1)

        format = self.graph.add("format", self.pix_fmt)
        overlay.link_to(format)

        post_filtered = self.post_overlay_filter(self.graph, format)

        sink = self.graph.add("buffersink")
        post_filtered.link_to(sink)

    def paste(self, frame: av.VideoFrame):
        with self.lock:
            self.rebuild_graph(
                width=frame.width,
                height=frame.height,
                pix_fmt=frame.format.name,
                x=self.x,
                y=self.y,
                bg_width=self.width,
                bg_height=self.height,
            )
            frame.pts = None
            self.src.push(frame)
            self.dst.push(self.background_image)
            ret = self.graph.pull()
            ret.pts = None
            return ret

    def paste_video(self, iterator: list[av.VideoFrame]):
        for it in iterator:
            yield self.paste(it)

    @property
    def width(self):
        return self.background_image.width

    @property
    def height(self):
        return self.background_image.height


class Overlayer(BaseOverlayer):
    def __init__(
        self,
        background_image: np.ndarray,
        dst_size: tuple[int, int],
        src_size: tuple[int, int],
        left=0.0,
        top=0.0,
        height=1.0,
        pix_fmt: str = "yuva420p",
        mode: str = "straight",
    ):
        self.background_origin = background_image
        src_size, src_pos, background_image = self._set_size(
            dst_size=dst_size,
            src_size=src_size,
            left=left,
            top=top,
            height=height,
        )
        self.src_size = src_size

        super().__init__(
            background_image,
            x=src_pos[0],
            y=src_pos[1],
            pix_fmt=pix_fmt,
            mode=mode,
            pre_overlay_filter=self._pre_overlay_filter,
        )

    def _set_size(
        self,
        dst_size: tuple[int, int],
        src_size: tuple[int, int],
        left=0.0,
        top=0.0,
        height=1.0,
    ):
        dst_size, background_image = get_dst_size(dst_size, self.background_origin)
        src_pos, src_size = get_src_size(left, top, height, dst_size, src_size)
        return src_size, src_pos, background_image

    def set_size(
        self,
        dst_size: tuple[int, int],
        src_size: tuple[int, int],
        background_image: np.ndarray = None,
        left=0.0,
        top=0.0,
        height=1.0,
    ):
        with self.lock:
            if background_image is not None:
                self.background_origin = background_image

            src_size, src_pos, background_image = self._set_size(
                dst_size=dst_size,
                src_size=src_size,
                left=left,
                top=top,
                height=height,
            )
            self.x = src_pos[0]
            self.y = src_pos[1]
            self.background_image = av.VideoFrame.from_ndarray(
                background_image,
                format="rgb24" if background_image.shape[-1] == 3 else "rgba",
            )
            self.src_size = src_size

    def _pre_overlay_filter(
        self, graph: av.filter.Graph, context: av.filter.context.FilterContext
    ) -> av.filter.context.FilterContext:
        scale = graph.add("scale", f"{self.src_size[0]}:{self.src_size[1]}")
        context.link_to(scale)
        return scale


class AsyncDecoder:
    def __init__(self, aiterator: AsyncIterator[bytes], **kwargs):
        self._aiterator = aiterator
        self._f = PopIO()
        self._kwargs = kwargs

    def decode(self) -> AsyncIterator[av.VideoFrame | av.AudioFrame]:
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
