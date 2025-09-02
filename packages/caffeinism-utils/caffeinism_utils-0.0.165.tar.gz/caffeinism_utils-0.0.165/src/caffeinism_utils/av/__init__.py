import fractions
import threading
from abc import abstractmethod
from collections import defaultdict, deque
from typing import Callable, Iterable

import av
import av.filter
import av.filter.context
import numpy as np

from .codecs import AsyncDecoder, AsyncEncoder, VideoEncoder
from .filters import FilterContextOutput, Graph
from .io import BasePyAVReader, PyAVReader, PyAVWriter

type PyAVDisposableReader = PyAVReader
