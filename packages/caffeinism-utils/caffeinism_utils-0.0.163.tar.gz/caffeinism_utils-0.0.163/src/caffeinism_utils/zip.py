from concurrent.futures import ThreadPoolExecutor
from typing import Generator, Iterator, TypeVar

from .asyncio import run_in_executor
from .utils import DummyStopIteration, next_without_stop_iteration

T = TypeVar("T")


def thread_zip(*iterators: list[Iterator[T]]):
    generator = _thread_zip(*iterators)
    generator.send(None)
    return generator


def _thread_zip(*iterators: list[Iterator[T]]) -> Generator[list[T], None, None]:
    with ThreadPoolExecutor(len(iterators)) as p:
        iterators = [iter(iterator) for iterator in iterators]
        prefetched = [p.submit(next, iterator) for iterator in iterators]
        yield
        while True:
            try:
                rets = [task.result() for task in prefetched]
            except StopIteration:
                for iterator in iterators:
                    del iterator
                return
            prefetched = [p.submit(next, iterator) for iterator in iterators]
            yield rets


async def athread_zip(*iterators):
    with ThreadPoolExecutor(len(iterators)) as p:
        iterators = [iter(iterator) for iterator in iterators]
        prefetched = [
            run_in_executor(p, next_without_stop_iteration, iterator)
            for iterator in iterators
        ]
        while True:
            try:
                rets = [await task for task in prefetched]
            except DummyStopIteration:
                for iterator in iterators:
                    del iterator
                return
            prefetched = [
                run_in_executor(p, next_without_stop_iteration, iterator)
                for iterator in iterators
            ]
            yield rets
