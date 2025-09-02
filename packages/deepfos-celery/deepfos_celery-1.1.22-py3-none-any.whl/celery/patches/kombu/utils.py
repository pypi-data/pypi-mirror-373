import asyncio
import collections

from asyncio import sleep
from time import time
from itertools import count
from contextlib import asynccontextmanager
from inspect import isfunction, iscoroutinefunction, ismethod

from kombu.utils.functional import (
    fxrange,
    lazy,
    ChannelPromise
)
from kombu.resource import Resource as SyncResource


def is_async_callable(fun):
    if not callable(fun):
        return False

    if isfunction(fun) or ismethod(fun):
        return iscoroutinefunction(fun)

    return iscoroutinefunction(fun.__call__)


class LifoQueue(asyncio.LifoQueue):
    @property
    def queue(self):
        return self._queue

    def _init(self, maxsize):
        self._queue = collections.deque()


async def retry_over_time(
    fun, catch, args=None, kwargs=None, errback=None,
    max_retries=None, interval_start=2, interval_step=2,
    interval_max=30, callback=None, timeout=None
):
    """async version of kombu.util.functional: retry_over_time"""
    kwargs = {} if not kwargs else kwargs
    args = [] if not args else args
    interval_range = fxrange(interval_start,
                             interval_max + interval_start,
                             interval_step, repeatlast=True)
    end = time() + timeout if timeout else None
    errback_is_coro = errback and is_async_callable(errback)
    cb_is_coro = callback and is_async_callable(callback)

    for retries in count():
        try:
            return await fun(*args, **kwargs)
        except catch as exc:
            if max_retries is not None and retries >= max_retries:
                raise
            if end and time() > end:
                raise
            if callback:
                if cb_is_coro:
                    await callback()
                else:
                    callback()

            if errback:
                if errback_is_coro:
                    interval = await errback(exc, interval_range, retries)
                else:
                    interval = errback(exc, interval_range, retries)
                tts = float(interval)
            else:
                tts = next(interval_range)

            if tts:
                for _ in range(int(tts)):
                    if callback:
                        if cb_is_coro:
                            await callback()
                        else:
                            callback()
                    await sleep(1.0)
                # sleep remainder after int truncation above.
                await sleep(abs(int(tts) - tts))


class Resource(SyncResource):
    def __init__(self, limit=None, preload=None, close_after_fork=None):
        self._limit = limit
        self.preload = preload or 0
        self._closed = False
        self.close_after_fork = (
            close_after_fork
            if close_after_fork is not None else self.close_after_fork
        )

        self._resource = LifoQueue()
        self._dirty = set()
        self.setup()

    def new(self):
        raise NotImplementedError

    async def get(self, block=False, timeout=None):
        """Acquire resource.

        Arguments:
            block (bool): If the limit is exceeded,
                then block until there is an available item.
            timeout (float): Timeout to wait
                if ``block`` is true.  Default is :const:`None` (forever).

        Raises:
            LimitExceeded: if block is false and the limit has been exceeded.
        """
        if self._closed:
            raise RuntimeError('Acquire on closed pool')
        if self.limit:
            while 1:
                try:
                    if not block:
                        R = self._resource.get_nowait()
                    elif timeout is not None:
                        R = await asyncio.wait_for(
                            self._resource.get(),
                            timeout=timeout
                        )
                    else:
                        R = await self._resource.get()
                except asyncio.QueueEmpty:
                    self._add_when_empty()
                else:
                    try:
                        R = await self.prepare(R)
                    except BaseException:
                        if isinstance(R, async_lazy):
                            # not evaluated yet, just put it back
                            self._resource.put_nowait(R)
                        else:
                            # evaluted so must try to release/close first.
                            await self.release(R)
                        raise
                    self._dirty.add(R)
                    break
        else:
            R = await self.prepare(self.new())

        async def release():
            """Release resource so it can be used by another thread.

            Warnings:
                The caller is responsible for discarding the object,
                and to never use the resource again.  A new resource must
                be acquired if so needed.
            """
            await self.release(R)
        R.release = release

        return R

    @asynccontextmanager
    async def acquire(self, block=False, timeout=None):
        R = await self.get(block, timeout)
        try:
            yield R
        finally:
            await self.release(R)

    async def release_resource(self, resource):
        pass

    async def release(self, resource):
        if self.limit:
            self._dirty.discard(resource)
            self._resource.put_nowait(resource)
            await self.release_resource(resource)
        else:
            await self.close_resource(resource)

    async def close_resource(self, resource):
        await resource.close()

    async def prepare(self, resource):
        return resource


class async_lazy(lazy):
    async def __call__(self):
        return await self.evaluate()

    async def evaluate(self):
        return await self._fun(*self._args, **self._kwargs)


async def maybe_async_evaluate(value):
    """Evaluate value only if value is a :class:`lazy` instance."""
    if isinstance(value, async_lazy):
        return await value.evaluate()
    return value


class AsyncChannelPromise(ChannelPromise):

    async def __call__(self):
        try:
            return self.__value__
        except AttributeError:
            value = self.__value__ = await self.__contract__()
            return value
