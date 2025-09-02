import asyncio
import datetime
from typing import *

from celery import current_app
from celery.patches.kombu.common import apromise, abarrier
from celery.result import (
    AsyncResult as SyncResult,
    GroupResult as SyncGroupResult,
    states,
    ResultBase,
    assert_will_not_block,
    app_or_default,
    parse_iso8601
)


async def result_from_tuple(r, app=None):
    """Deserialize result from tuple."""
    # earlier backends may just pickle, so check if
    # result is already prepared.
    app = app_or_default(app)
    Result = app.AioAsyncResult
    if not isinstance(r, ResultBase):
        res, nodes = r
        id, parent = res if isinstance(res, (list, tuple)) else (res, None)
        if parent:
            parent = await result_from_tuple(parent, app)

        if nodes is not None:
            return await app.AioGroupResult(
                id, [await result_from_tuple(child, app) for child in nodes],
                parent=parent,
            )

        return Result(id, parent=parent)
    return r


class AsyncResult(SyncResult):
    if TYPE_CHECKING:
        from celery.app import Celery
        from celery.aio.backend import RedisBackend

        app: Celery
        backend: RedisBackend

    def __init__(self, id, backend=None,
                 task_name=None,            # deprecated
                 app=None, parent=None):
        if id is None:
            raise ValueError(
                f'AsyncResult requires valid id, not {type(id)}')
        self.app = app_or_default(app or self.app)
        self.id = id
        self.backend = backend or self.app.aio_backend
        self.parent = parent
        self.on_ready = apromise(self._on_fulfilled, weak=True)
        self._cache = None
        self._ignored = False
        self._fulfilled = False

    @property
    def result(self):
        """Task return value.

        Note:
            When the task has been executed, this contains the return value.
            If the task raised an exception, this will be the exception
            instance.
        """
        async def getter():
            meta = await self._get_task_meta()
            return meta['result']
        return getter()

    info = result

    async def get(self, timeout=None, propagate=True, interval=0.5,
            no_ack=True, follow_parents=True, callback=None, on_message=None,
            on_interval=None, disable_sync_subtasks=True,
            EXCEPTION_STATES=states.EXCEPTION_STATES,
            PROPAGATE_STATES=states.PROPAGATE_STATES):
        if self.ignored:
            return

        if disable_sync_subtasks:
            assert_will_not_block()
        _on_interval = apromise()
        if follow_parents and propagate and self.parent:
            _on_interval = apromise(self._maybe_reraise_parent_error, weak=True)
            await self._maybe_reraise_parent_error()
        if on_interval:
            await _on_interval.then(on_interval)

        if self._cache:
            if propagate:
                await self.maybe_throw(callback=callback)
            return await self.result

        await self.backend.add_pending_result(self)
        return await self.backend.wait_for_pending(
            self, timeout=timeout,
            interval=interval,
            on_interval=_on_interval,
            no_ack=no_ack,
            propagate=propagate,
            callback=callback,
            on_message=on_message,
        )
    wait = get  # deprecated alias to :meth:`get`.

    async def _maybe_reraise_parent_error(self):
        for node in reversed(list(self._parents())):
            await node.maybe_throw()

    async def _get_task_meta(self):
        if self._cache is None:
            return await self._maybe_set_cache(
                await self.backend.get_task_meta(self.id)
            )
        return self._cache

    async def _iter_meta(self, **kwargs):
        return [await self._get_task_meta()]

    async def maybe_throw(self, propagate=True, callback=None):
        cache = await self._get_task_meta() if self._cache is None else self._cache
        state, value, tb = (
            cache['status'], cache['result'], cache.get('traceback'))
        if state in states.PROPAGATE_STATES and propagate:
            self.throw(value, self._to_remote_traceback(tb))
        if callback is not None:
            await callback(self.id, value)
        return value
    maybe_reraise = maybe_throw   # XXX compat alias

    async def _on_fulfilled(self, result):
        await self.backend.remove_pending_result(self)
        self._fulfilled = True
        return result

    @property
    def fulfilled(self) -> bool:
        return self._fulfilled

    async def _maybe_set_cache(self, meta):
        if meta:
            state = meta['status']
            if state in states.READY_STATES:
                d = self._set_cache(self.backend.meta_from_decoded(meta))
                self.backend.maybe_set_future(meta['task_id'], d)
                await self.on_ready(self)
                return d
        return meta

    async def then(self, callback, on_error=None, weak=False):
        await self.backend.add_pending_result(self, weak=weak)
        return await self.on_ready.then(callback, on_error)

    def __del__(self):
        if self.backend is not None:
            self.backend.remove_pending_future(self)

    async def _get_state(self):
        return (await self._get_task_meta())['status']

    @property
    def state(self):
        return self._get_state()

    status = state

    async def _get_date_done(self):
        """UTC date and time."""
        date_done = (await self._get_task_meta()).get('date_done')
        if date_done and not isinstance(date_done, datetime.datetime):
            return parse_iso8601(date_done)
        return date_done

    @property
    def date_done(self):
        return self._get_date_done()

    async def successful(self):
        return (await self.state) == states.SUCCESS

    async def failed(self):
        return (await self.state) == states.FAILURE

    async def ready(self):
        return (await self.state) in self.backend.READY_STATES

    async def forget(self):
        """Forget the result of this task and its parents."""
        self._cache = None
        if self.parent:
            await self.parent.forget()
        await self.backend.forget(self.id)

    async def revoke(self, connection=None, terminate=False, signal=None,
               wait=False, timeout=None):
        await self.app.aio_control.revoke(
            self.id, connection=connection,
            terminate=terminate, signal=signal,
            reply=wait, timeout=timeout
        )


class GroupResult(SyncGroupResult):
    def __init__(
        self, id=None, results=None,
        parent=None, app=None, ready_barrier=None,
        **kwargs
    ):
        self.id = id
        self.parent = parent
        self._app = app
        self.results = results
        self.on_ready = apromise(args=(self,))
        self._ready_barrier = ready_barrier

    def __await__(self):
        return self._init_on_full().__await__()

    async def _init_on_full(self):
        self._on_full = self._ready_barrier or (await abarrier(self.results))
        if self._on_full:
            await self._on_full.then(apromise(self._on_ready, weak=True))
        return self

    @classmethod
    async def restore(cls, id, backend=None, app=None):
        """Restore previously saved group result."""
        app = app or (
            cls.app if not isinstance(cls.app, property) else current_app
        )
        backend = backend or app.aio_backend
        return await backend.restore_group(id)

    async def save(self, backend=None):
        """Save group-result for later retrieval using :meth:`restore`.

        Example:
            >>> def save_and_restore(result):
            ...     result.save()
            ...     result = GroupResult.restore(result.id)
        """
        return await (backend or self.app.aio_backend).save_group(self.id, self)

    async def join_native(self, timeout=None, propagate=True,
                    interval=0.5, callback=None, no_ack=True,
                    on_message=None, on_interval=None,
                    disable_sync_subtasks=True):
        if disable_sync_subtasks:
            assert_will_not_block()
        order_index = None if callback else {
            result.id: i for i, result in enumerate(self.results)
        }
        acc = None if callback else [None for _ in range(len(self))]
        async for task_id, meta in self.iter_native(timeout, interval, no_ack,
                                              on_message, on_interval):
            if isinstance(meta, list):
                value = []
                for children_result in meta:
                    value.append(children_result.get())
            else:
                value = meta['result']
                if propagate and meta['status'] in states.PROPAGATE_STATES:
                    raise value
            if callback:
                callback(task_id, value)
            else:
                acc[order_index[task_id]] = value
        return acc

    @property
    def backend(self):
        return self.app.aio_backend if self.app else self.results[0].backend

    async def _iter_meta(self, **kwargs):
        return [meta async for _, meta in self.backend.get_many(
            {r.id for r in self.results}, max_iterations=1, **kwargs
        )]

    def remove(self, result):
        """Remove result from the set; it must be a member.

        Raises:
            KeyError: if the result isn't a member.
        """
        if isinstance(result, str):
            result = self.app.AioAsyncResult(result)
        try:
            self.results.remove(result)
        except ValueError:
            raise KeyError(result)

    async def successful(self):
        return all(await asyncio.gather(*[
            result.successful() for result in self.results
        ]))

    async def failed(self):
        """Return true if any of the tasks failed.

        Returns:
            bool: true if one of the tasks failed.
                (i.e., raised an exception)
        """
        return any(await asyncio.gather(*[
            result.failed() for result in self.results
        ]))

    async def maybe_throw(self, callback=None, propagate=True):
        for result in self.results:
            await result.maybe_throw(callback=callback, propagate=propagate)
    maybe_reraise = maybe_throw  # XXX compat alias.

    async def waiting(self):
        """Return true if any of the tasks are incomplete.

        Returns:
            bool: true if one of the tasks are still
                waiting for execution.
        """
        return not (await self.ready())

    async def ready(self):
        """Did all of the tasks complete? (either by success of failure).

        Returns:
            bool: true if all of the tasks have been executed.
        """
        return all(await asyncio.gather(*[
            result.ready() for result in self.results
        ]))

    async def completed_count(self):
        """Task completion count.

        Returns:
            int: the number of tasks completed.
        """
        return sum(await asyncio.gather(*[
            result.successful() for result in self.results
        ]))

    async def forget(self):
        """Forget about (and possible remove the result of) all the tasks."""
        return await asyncio.gather(*[
            result.forget() for result in self.results
        ])

    async def revoke(self, connection=None, terminate=False, signal=None,
               wait=False, timeout=None):
        """Send revoke signal to all workers for all tasks in the set.

        Arguments:
            terminate (bool): Also terminate the process currently working
                on the task (if any).
            signal (str): Name of signal to send to process if terminate.
                Default is TERM.
            wait (bool): Wait for replies from worker.
                The ``timeout`` argument specifies the number of seconds
                to wait.  Disabled by default.
            timeout (float): Time in seconds to wait for replies when
                the ``wait`` argument is enabled.
        """
        await self.app.aio_control.revoke(
            [r.id for r in self.results],
            connection=connection, timeout=timeout,
            terminate=terminate, signal=signal, reply=wait
        )

    async def _on_ready(self):
        await self.backend.remove_pending_result(self)
        if self.backend.is_async:
            await self.on_ready()

    async def then(self, callback, on_error=None, weak=False):
        return await self.on_ready.then(callback, on_error)

    async def add(self, result):
        """Add :class:`AsyncResult` as a new member of the set.

        Does nothing if the result is already a member.
        """
        if result not in self.results:
            self.results.append(result)
            if self._on_full:
                await self._on_full.add(result)
