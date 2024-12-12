import asyncio
import time
from asyncio import Future, Queue
from dataclasses import dataclass, field
from typing import Awaitable, Callable, Generic, Optional, TypeVar

import httpx


T = TypeVar('T')

@dataclass(kw_only=True, slots=True)
class Client(Generic[T]):
  func: Callable[[httpx.AsyncClient, T], Awaitable[httpx.Response]] = field(default=(lambda client, url: client.get(url)), repr=False)
  delay: float
  headers: dict[str, str] = field(default_factory=dict)

  _queue: Queue[tuple[T, Future[httpx.Response]]] = field(init=False, default_factory=(lambda: Queue(maxsize=50)), repr=False)
  _task: Optional[asyncio.Task[None]] = field(init=False, repr=False)

  async def get(self, url: T, /):
    future = Future[httpx.Response]()
    await self._queue.put((url, future))
    return await future

  async def _run(self):
    async with httpx.AsyncClient(headers=self.headers, http2=True) as client:
      while True:
        last_start_time = time.time()

        url, future = await self._queue.get()
        future.set_result(await self.func(client, url))

        current_time = time.time()
        await asyncio.sleep(max(self.delay - (current_time - last_start_time), 0))

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


user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

goodreads_reg = Client(delay=1.0, headers={
  'Accept-Language': 'en-US,en;q=0.9',
  'User-Agent': user_agent,
  'Referer': 'https://www.google.com/',
})

goodreads_api = Client(delay=1.0, headers={
  'User-Agent': user_agent,
  'x-api-key': 'da2-xpgsdydkbregjhpr6ejzqdhuwy',
}, func=(lambda client, data: client.post('https://kxbwmqov6jgg3daaamb744ycu4.appsync-api.us-east-1.amazonaws.com/graphql', json=data)))

google_books_api = Client(delay=0.5, headers={
  'User-Agent': user_agent,
})

google_books_reg = Client(delay=1.0, headers={
  'User-Agent': user_agent,
})

worldcat = Client(delay=4.0, headers={
  'Referer': 'https://search.worldcat.org',
  'User-Agent': user_agent,
})

clients = [
  goodreads_api,
  goodreads_reg,
  google_books_api,
  google_books_reg,
  worldcat,
]
