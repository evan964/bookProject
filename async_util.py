import asyncio
from asyncio import Event, Future
from collections import deque
from dataclasses import KW_ONLY, dataclass, field
from typing import Any, Awaitable, Callable, Generic, Optional, TypeVar


T = TypeVar('T')
S = TypeVar('S')

@dataclass(slots=True)
class BatchQueue(Generic[T, S]):
  func: Callable[[list[T]], Awaitable[list[S]]] = field(repr=False)
  _: KW_ONLY
  concurrent_count: int = 5
  # max_size: int = 50

  # _closed: bool = field(default=False, init=False, repr=False)
  _queue: deque[tuple[T, Future[S]]] = field(init=False, default_factory=deque, repr=False)
  _event: Event = field(default_factory=Event, init=False, repr=False)
  _task: Optional[asyncio.Task[None]] = field(init=False, repr=False)

  # def close(self):
  #   print('Close')

  #   if self._queue:
  #     self._event.set()

  #   self._closed = True

  async def push(self, item: T, /):
    # while len(self._queue) >= self.max_size:
    #   await self._event.wait()

    future = Future[S]()
    self._queue.append((item, future))
    self._event.set()

    return await future

  async def _run(self):
    while True:
      await self._event.wait()

      if len(self._queue) < self.concurrent_count:
        await asyncio.sleep(1)

      items = [self._queue.popleft() for _ in range(min(self.concurrent_count, len(self._queue)))]

      for (_, future), result in zip(items, await self.func([item for item, _ in items])):
        future.set_result(result)

      self._event.clear()

  async def __aenter__(self):
    self._task = asyncio.create_task(self._run())
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    assert self._task is not None
    self._task.cancel()

    try:
      await self._task
    except asyncio.CancelledError:
      pass
