from typing import Protocol
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field


class ScheduleItem(Protocol):
    def __call__(self) -> None: ...


class Scheduler(Protocol):

    def __call__(self, func: ScheduleItem, /) -> None: ...


class ScheduleErrorHandler(Protocol):
    def __call__(self, error: BaseException, /) -> None: ...


@dataclass(kw_only=True)
class ThreadPoolScheduler(Scheduler):
    on_error: ScheduleErrorHandler
    workers: int
    _pool: ThreadPoolExecutor = field(init=False)

    def __post_init__(self):
        self._pool = ThreadPoolExecutor(max_workers=self.workers)

    def __call__(self, func: ScheduleItem) -> None:
        def callback(f: Future[None]):
            if ex := f.exception():
                self.on_error(ex)
            return object()

        self._pool.submit(func).add_done_callback(callback)


def default_scheduler(on_error: ScheduleErrorHandler):
    return ThreadPoolScheduler(workers=1, on_error=on_error)
