import fractions
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from typing import Callable, Iterable

import av
import av.filter
import av.filter.context
import numpy as np


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


class Filter(ABC):
    _graph: Graph
    _buffers: list[FilterContextOutput]

    def __init__(
        self,
        graph: Graph,
        buffers: list[FilterContextOutput],
    ):
        self._graph = graph
        self._buffers = buffers

    def __call__(
        self, *frames: av.VideoFrame, **commands: dict[str, str]
    ) -> av.VideoFrame:
        self.process_command(**commands)
        self.push(*frames)
        ret = self._graph.pull()
        ret.pts = None
        return ret

    def process_command(self, **commands):
        "process command"

    def push(self, *frames):
        for frame, buffer in zip(frames, self._buffers):
            buffer.push(frame)

    def close(self):
        if self._graph is not None:
            self._graph.push(None)


class ScaledOverlay(Filter):
    def __init__(
        self,
        background_width: int,
        background_height: int,
        width: int,
        height: int,
        pix_fmt: str = "rgba",
    ):
        graph = Graph()
        super().__init__(
            graph,
            [
                self._graph.add_buffer(
                    width=background_width, height=background_height, format=pix_fmt
                ),
                self._graph.add_buffer(width=width, height=height, format=pix_fmt),
            ],
        )

        self._scale1 = self._graph.add("scale")
        self._scale2 = self._graph.add("scale")
        self._overlay = self._graph.add("overlay", format=pix_fmt.replace("a", ""))

        (
            (
                (self._buffers[0] >> self._scale1),
                (self._buffers[1] >> self._scale2),
            )
            >> self._overlay
            >> self._graph.add("buffersink")
        )

        self._graph.configure()

    def process_command(
        self,
        x: int,
        y: int,
        background_width: int = -1,
        background_height: int = -1,
        width: int = -1,
        height: int = -1,
    ):
        self._scale1.process_command("width", f"{background_width}")
        self._scale1.process_command("height", f"{background_height}")
        self._scale2.process_command("width", f"{width}")
        self._scale2.process_command("height", f"{height}")
        self._overlay.process_command("x", f"{x}")
        self._overlay.process_command("y", f"{y}")


class RebuildableFilter(Filter):
    def __init__(self):
        super().__init__(None, [])
        self._kwargs = {}

    def rebuild_graph(self, **kwargs):
        if self._kwargs != kwargs:
            self.close()
            self._graph = Graph()
            self._rebuild_graph(**kwargs)
            self._graph.configure()
            self._kwargs = kwargs

    @abstractmethod
    def _rebuild_graph(**kwargs):
        "rebuild graph impl"


def to_rgba(reader: Iterable[av.VideoFrame]):
    for frame in reader:
        yield frame.reformat(format="rgba")


def to_array(iterator: list[av.VideoFrame]):
    for frame in iterator:
        yield frame.to_ndarray()


class _AlphaExtractor(RebuildableFilter):
    def __init__(self):
        super().__init__()

    def _rebuild_graph(self, width: int, height: int, pix_fmt: str):
        self._buffers = [
            self._graph.add_buffer(
                width=width,
                height=height,
                format=pix_fmt,
                time_base=fractions.Fraction(1, 1000),
            ),
        ]

        (
            self._buffers
            >> self._graph.add("alphaextract")
            >> self._graph.add("buffersink")
        )

    def __call__(self, frame: av.VideoFrame):
        self.rebuild_graph(
            width=frame.width, height=frame.height, pix_fmt=frame.format.name
        )
        return super().__call__(frame)


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


class _AlphaMerger(RebuildableFilter, BaseAlphaMerger):
    def __init__(self, image_pix_fmt: str, alpha_pix_fmt: str):
        super().__init__()
        self.image_pix_fmt = image_pix_fmt
        self.alpha_pix_fmt = alpha_pix_fmt

    def _rebuild_graph(
        self,
        width: int,
        height: int,
    ):
        self._buffers = [
            self._graph.add_buffer(
                width=width,
                height=height,
                format=self.image_pix_fmt,
                time_base=fractions.Fraction(1, 1000),
            ),
            self._graph.add_buffer(
                width=width,
                height=height,
                format=self.alpha_pix_fmt,
                time_base=fractions.Fraction(1, 1000),
            ),
        ]

        (
            (self._buffers[0], self._buffers[1] >> self._graph.add("format", "gray"))
            >> self._graph.add("alphamerge")
            >> self._graph.add("buffersink")
        )

    def push_image(self, frame: av.VideoFrame):
        self.rebuild_graph(width=frame.width, height=frame.height)
        self._buffers[0].push(frame)

    def push_alpha(self, frame: av.VideoFrame):
        self.rebuild_graph(width=frame.width, height=frame.height)
        self._buffers[1].push(frame)

    def pull(self) -> av.VideoFrame:
        try:
            return self._graph.pull()
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


class ScaledCenterCropOverlay(Filter):
    def __init__(
        self,
        background_width: int,
        background_height: int,
        width: int,
        height: int,
        pix_fmt: str = "rgba",
    ):
        graph = Graph()
        super().__init__(
            graph,
            [
                graph.add_buffer(
                    width=background_width, height=background_height, format=pix_fmt
                ),
                graph.add_buffer(width=width, height=height, format=pix_fmt),
            ],
        )

        self._scale1 = self._graph.add(
            "scale", force_original_aspect_ratio="increase", flags="fast_bilinear"
        )
        self._scale2 = self._graph.add("scale", flags="fast_bilinear")
        self._crop = self._graph.add("crop", x="(iw-ow)/2", y="(ih-oh)/2")

        self._overlay = self._graph.add("overlay", format=pix_fmt.replace("a", ""))

        (
            (
                (self._buffers[0] >> self._scale1 >> self._crop),
                (self._buffers[1] >> self._scale2),
            )
            >> self._overlay
            >> self._graph.add("buffersink")
        )

        self._graph.configure()

    def process_command(
        self,
        x: int,
        y: int,
        background_width: int = -1,
        background_height: int = -1,
        width: int = -1,
        height: int = -1,
    ):
        self._scale1.process_command("w", f"{background_width}")
        self._scale1.process_command("h", f"{background_height}")
        self._crop.process_command("w", f"{background_width}")
        self._crop.process_command("h", f"{background_height}")
        self._scale2.process_command("w", f"{width}")
        self._scale2.process_command("h", f"{height}")
        self._overlay.process_command("x", f"{x}")
        self._overlay.process_command("y", f"{y}")


class Paste(Filter):
    def __init__(
        self,
        background_width: int,
        background_height: int,
        width: int,
        height: int,
        pix_fmt: str = "rgba",
    ):
        graph = Graph()
        super().__init__(
            graph,
            [
                graph.add_buffer(
                    width=background_width, height=background_height, format=pix_fmt
                ),
                graph.add_buffer(width=width, height=height, format=pix_fmt),
            ],
        )

        self._scale = self._graph.add("scale")
        self._overlay1 = self._graph.add(
            "overlay", format=pix_fmt.replace("a", "").replace("p", "")
        )
        self._overlay2 = self._graph.add(
            "overlay", format=pix_fmt.replace("a", "").replace("p", "")
        )

        buffer11, buffer12 = self._buffers[0] >> graph.add("split")
        buffer21, buffer22 = (
            self._buffers[1]
            >> self._scale
            >> graph.add("format", pix_fmt)
            >> graph.add("split")
        )

        (
            (
                (
                    buffer11 >> graph.add("alphaextract"),
                    buffer21 >> graph.add("alphaextract"),
                )
                >> self._overlay1
                >> graph.add("format", "gray"),
                (
                    buffer12 >> graph.add("format", "rgb24"),
                    buffer22 >> graph.add("format", "rgb24"),
                )
                >> self._overlay2,
            )
            >> graph.add("alphamerge")
            >> graph.add("buffersink")
        )

        self._graph.configure()

    def process_command(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
    ):
        self._scale.process_command("w", f"{w}")
        self._scale.process_command("h", f"{h}")
        self._overlay1.process_command("x", f"{x}")
        self._overlay1.process_command("y", f"{y}")
        self._overlay2.process_command("x", f"{x}")
        self._overlay2.process_command("y", f"{y}")
