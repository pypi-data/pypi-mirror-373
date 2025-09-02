import asyncio
import collections
import logging
from collections import deque
from typing import *
from functools import partial
from contextlib import asynccontextmanager
import time
import socket

import redis.asyncio as aioredis
from redis.asyncio import cluster
from redis.connection import SERVER_CLOSED_CONNECTION_ERROR
from redis.exceptions import RedisClusterException, ConnectionError

from celery.backends.redis import (
    RedisBackend as SyncRedisBackend,
    SentinelBackend as SyncSentinelBackend,
    ResultConsumer as SyncResultConsumer,
    task_join_will_block,
    states,
    logger,
    E_RETRY_LIMIT_EXCEEDED,
)
from celery.backends.asynchronous import (
    Empty,
    Drainer as SyncDrainer,
    register_drainer,
    drainers,
    detect_environment
)
from celery.backends.base import (
    bytes_to_str,
    get_exponential_backoff_interval,
    raise_with_context,
    BackendGetMetaError,
    BackendStoreError,
)
from celery.exceptions import TimeoutError
from celery.result import GroupResult

from celery.aio.result import result_from_tuple
from celery.patches.kombu.redis import get_redis_error_classes
from celery.patches.kombu.utils import retry_over_time


@register_drainer('aio-default')
class Drainer(SyncDrainer):
    if TYPE_CHECKING:
        result_consumer: 'ResultConsumer'

    def __init__(self, result_consumer):
        self.result_consumer = result_consumer
        self._started = False
        self._drainer: Optional[asyncio.Task] = None

    async def drain_events_until(self, r, timeout=None, interval=1, on_interval=None, wait=None):
        wait = wait or self.result_consumer.drain_events
        p = r.on_ready
        time_start = time.monotonic()

        while 1:
            # Total time spent may exceed a single call to wait()
            if timeout and time.monotonic() - time_start >= timeout:
                raise socket.timeout()
            try:
                await wait(r, interval)
            except socket.timeout:
                pass
            if on_interval:
                await on_interval()
            if p.ready:  # got event on the wanted channel.
                break

    async def start(self):
        await self.result_consumer.spawn_drainer()

    def stop(self):
        self.result_consumer.stop_drainer()


class ResultConsumer(SyncResultConsumer):
    if TYPE_CHECKING:
        from redis.asyncio.client import PubSub

        backend: 'RedisBackend'
        _pubsub: Optional[PubSub]
        drainer: Drainer
        _running_drainer: Optional[asyncio.Task]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.drainer = drainers['aio-' + detect_environment()](self)
        self._running_drainer = None
        self._pubsub_lock = asyncio.Lock()

    async def on_after_fork(self):
        try:
            self.backend.client.connection_pool.reset()
            if self._pubsub is not None:
                await self._pubsub.close()
        except KeyError as e:
            logger.warning(str(e))

    async def _reconnect_pubsub(self):
        self._pubsub = None
        self.backend.client.connection_pool.reset()
        # task state might have changed when the connection was down so we
        # retrieve meta for all subscribed tasks before going into pubsub mode
        metas = await self.backend.client.mget(self.subscribed_to)
        metas = [meta for meta in metas if meta]
        for meta in metas:
            await self.on_state_change(self._decode_result(meta), None)
        self._pubsub = self.backend.client.pubsub(
            ignore_subscribe_messages=True,
        )
        if self.subscribed_to:
            await self._pubsub.subscribe(*self.subscribed_to)

    @asynccontextmanager
    async def reconnect_on_error(self):
        try:
            yield
        except self._connection_errors:
            try:
                await self._ensure(self._reconnect_pubsub, ())
            except self._connection_errors:
                logger.critical(E_RETRY_LIMIT_EXCEEDED)
                raise

    async def _maybe_cancel_ready_task(self, meta):
        if meta['status'] in states.READY_STATES:
            await self.cancel_for(meta['task_id'])

    async def on_state_change(self, meta, message):
        if self.on_message:
            self.on_message(meta)
        if meta['status'] in states.READY_STATES:
            task_id = meta['task_id']
            try:
                result = self._get_pending_result(task_id)
            except KeyError:
                # send to buffer in case we received this result
                # before it was added to _pending_results.
                self._pending_messages.put(task_id, meta)
            else:
                await result._maybe_set_cache(meta)
                buckets = self.buckets
                try:
                    # remove bucket for this result, since it's fulfilled
                    bucket = buckets.pop(result)
                except KeyError:
                    pass
                else:
                    # send to waiter via bucket
                    bucket.append(result)
        await asyncio.sleep(0)
        await self._maybe_cancel_ready_task(meta)

    async def start(self, initial_task_id, **kwargs):
        self._pubsub = self.backend.client.pubsub(
            ignore_subscribe_messages=True,
        )
        await self._consume_from(initial_task_id)

    async def on_wait_for_pending(self, result, **kwargs):
        for meta in await result._iter_meta(**kwargs):
            if meta is not None:
                await self.on_state_change(meta, None)

    async def stop(self):
        if self._pubsub is not None:
            await self._pubsub.close()

    async def _drain_events(self):
        logger.debug(f'start drainer on channel: [{self._pubsub.channels}]')
        async with self.reconnect_on_error():
            async for message in self._pubsub.listen():
                if message and message['type'] == 'message':
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f'got message: {message}')
                    await self.on_state_change(
                        self._decode_result(message['data']), message
                    )

        logger.debug(f'stoping drainer... | '
                     f'subscribed: {self._pubsub.subscribed}')
        self._running_drainer = None

    async def spawn_drainer(self) -> Optional[asyncio.Task]:
        if not self._pubsub:
            return

        if self._running_drainer is None:
            self._running_drainer = asyncio.create_task(self._drain_events())
            await asyncio.sleep(0)
        return self._running_drainer

    def stop_drainer(self):
        if self._running_drainer is not None:
            self._running_drainer.cancel()
            self._running_drainer = None

    async def drain_events(self, result, timeout=None):
        await self.spawn_drainer()
        await self.backend.wait_for_future(result, timeout)

    async def consume_from(self, task_id):
        if self._pubsub is None:
            return await self.start(task_id)
        await self._consume_from(task_id)

    async def _consume_from(self, task_id):
        key = self._get_key_for_task(task_id)
        if key not in self.subscribed_to:
            self.subscribed_to.add(key)
            async with self.reconnect_on_error():
                async with self._pubsub_lock:
                    if self._pubsub:  # double check needed
                        await self._pubsub.subscribe(key)

    async def cancel_for(self, task_id):
        key = self._get_key_for_task(task_id)
        self.subscribed_to.discard(key)
        if self._pubsub:
            async with self.reconnect_on_error():
                async with self._pubsub_lock:
                    if self._pubsub:  # double check needed
                        await self._pubsub.unsubscribe(key)

    # -------------------------------------------------------
    # celery.backends.asynchronou::BaseResultConsumer
    async def _wait_for_pending(
        self, result, timeout=None,
        on_interval=None, on_message=None, **kwargs
    ):
        await self.on_wait_for_pending(result, timeout=timeout, **kwargs)
        prev_on_m, self.on_message = self.on_message, on_message
        try:
            await self.drain_events_until(
                result, timeout=timeout,
                on_interval=on_interval
            )
        except socket.timeout:
            raise TimeoutError('The operation timed out.')
        finally:
            self.on_message = prev_on_m

    async def drain_events_until(self, r, timeout=None, on_interval=None):
        return await self.drainer.drain_events_until(
            r, timeout=timeout, on_interval=on_interval)


class RedisBackend(SyncRedisBackend):
    if TYPE_CHECKING:
        @property
        def client(self) -> aioredis.Redis: ...  # noqa
        result_consumer: ResultConsumer
        _pending_future: Dict[str, Dict[int, asyncio.Future]]

    ResultConsumer = ResultConsumer
    redis = aioredis

    def __init__(self, host=None, port=None, db=None, password=None,
                 max_connections=None, url=None,
                 connection_pool=None, **kwargs):
        super().__init__(
            host=host, port=port, db=db, password=password,
            max_connections=max_connections, url=url,
            connection_pool=connection_pool, **kwargs
        )
        self._pending_future = collections.defaultdict(dict)
        self.always_retry = True

    def exception_safe_to_retry(self, exc):
        return (
            isinstance(exc, ConnectionError)
            and exc.args[0] == SERVER_CLOSED_CONNECTION_ERROR
        )

    def get_redis_error_classes(self):
        return get_redis_error_classes()

    async def on_task_call(self, producer, task_id):
        if not task_join_will_block():
            await self.result_consumer.consume_from(task_id)

    async def get(self, key):
        return await self.client.get(key)

    async def mget(self, keys):
        return await self.client.mget(keys)

    async def ensure(self, fun, args, **policy):
        retry_policy = dict(self.retry_policy, **policy)
        max_retries = retry_policy.get('max_retries')
        return await retry_over_time(
            fun, self.connection_errors, args, {},
            partial(self.on_connection_error, max_retries),
            **retry_policy
        )

    async def set(self, key, value, **retry_policy):
        return await self.ensure(self._set, (key, value), **retry_policy)

    async def _set(self, key, value):
        async with self.client.pipeline() as pipe:
            if self.expires:
                pipe.setex(key, self.expires, value)
            else:
                pipe.set(key, value)
            pipe.publish(key, value)
            await pipe.execute()

    async def remove_pending_result(self, result):
        self._remove_pending_result(result.id)
        await self.on_result_fulfilled(result)
        self.remove_pending_future(result)
        return result

    async def _forget(self, task_id):
        await self.delete(self.get_key_for_task(task_id))

    async def forget(self, task_id):
        self._cache.pop(task_id, None)
        await self._forget(task_id)
        await self.result_consumer.cancel_for(task_id)

    async def delete(self, key):
        await self.client.delete(key)

    async def incr(self, key):
        return await self.client.incr(key)

    async def expire(self, key, value):
        return await self.client.expire(key, value)

    async def add_to_chord(self, group_id, result):
        await self.client.incr(self.get_key_for_group(group_id, '.t'), 1)

    async def on_result_fulfilled(self, result):
        await self.result_consumer.cancel_for(result.id)

    async def add_pending_result(self, result, weak=False, start_drainer=True):
        if start_drainer:
            await self.result_consumer.drainer.start()
        try:
            await self._maybe_resolve_from_buffer(result)
        except Empty:
            await self._add_pending_result(result.id, result, weak=weak)
        return result

    async def _maybe_resolve_from_buffer(self, result):
        await result._maybe_set_cache(self._pending_messages.take(result.id))

    async def _add_pending_result(self, task_id, result, weak=False):
        if id(result) not in self._pending_future.get(task_id, {}):
            self._pending_future[task_id][id(result)] = \
                asyncio.get_running_loop().create_future()

        concrete, weak_ = self._pending_results
        if task_id not in weak_ and result.id not in concrete:
            (weak_ if weak else concrete)[task_id] = result
            await self.result_consumer.consume_from(task_id)
        else:
            ori_result = weak_.get(task_id, concrete.get(task_id))
            if ori_result is not result:
                await ori_result.on_ready.then(result.on_ready)

    async def add_pending_results(self, results, weak=False):
        await self.result_consumer.drainer.start()
        return [
            await self.add_pending_result(
                result, weak=weak, start_drainer=False)
            for result in results
        ]

    async def wait_for_pending(self, result,
                         callback=None, propagate=True, **kwargs):
        self._ensure_not_eager()
        await self._wait_for_pending(result, **kwargs)
        return await result.maybe_throw(callback=callback, propagate=propagate)

    async def _wait_for_pending(
        self, result, timeout=None, on_interval=None,
        on_message=None, **kwargs
    ):
        return await self.result_consumer._wait_for_pending(
            result, timeout=timeout,
            on_interval=on_interval, on_message=on_message,
            **kwargs
        )

    async def _get_task_meta_for(self, task_id):
        """Get task meta-data for a task by id."""
        meta = await self.get(self.get_key_for_task(task_id))
        if not meta:
            return {'status': states.PENDING, 'result': None}
        return self.decode_result(meta)

    async def _store_result(self, task_id, result, state,
                      traceback=None, request=None, **kwargs):
        meta = self._get_result_meta(result=result, state=state,
                                     traceback=traceback, request=request)
        meta['task_id'] = bytes_to_str(task_id)

        # Retrieve metadata from the backend, if the status
        # is a success then we ignore any following update to the state.
        # This solves a task deduplication issue because of network
        # partitioning or lost workers. This issue involved a race condition
        # making a lost task overwrite the last successful result in the
        # result backend.
        current_meta = await self._get_task_meta_for(task_id)

        if current_meta['status'] == states.SUCCESS:
            return result

        await self._set_with_state(
            self.get_key_for_task(task_id),
            self.encode(meta), state
        )
        return result

    async def get_task_meta(self, task_id, cache=True):
        """Get task meta from backend.

        if always_retry_backend_operation is activated, in the event of a recoverable exception,
        then retry operation with an exponential backoff until a limit has been reached.
        """
        self._ensure_not_eager()
        if cache:
            try:
                return self._cache[task_id]
            except KeyError:
                pass
        retries = 0
        while True:
            try:
                meta = await self._get_task_meta_for(task_id)
                break
            except Exception as exc:
                if self.always_retry and self.exception_safe_to_retry(exc):
                    if retries < self.max_retries:
                        retries += 1

                        # get_exponential_backoff_interval computes integers
                        # and time.sleep accept floats for sub second sleep
                        sleep_amount = get_exponential_backoff_interval(
                            self.base_sleep_between_retries_ms, retries,
                            self.max_sleep_between_retries_ms, True) / 1000
                        await self._sleep(sleep_amount)
                    else:
                        raise_with_context(
                            BackendGetMetaError("failed to get meta", task_id=task_id),
                        )
                else:
                    raise

        if cache and meta.get('status') == states.SUCCESS:
            self._cache[task_id] = meta
        return meta

    async def store_result(self, task_id, result, state,
                     traceback=None, request=None, **kwargs):
        """Update task state and result.

        if always_retry_backend_operation is activated, in the event of a recoverable exception,
        then retry operation with an exponential backoff until a limit has been reached.
        """
        result = self.encode_result(result, state)

        retries = 0

        while True:
            try:
                await self._store_result(
                    task_id, result, state, traceback,
                    request=request, **kwargs)
                return result
            except Exception as exc:
                if self.always_retry and self.exception_safe_to_retry(exc):
                    if retries < self.max_retries:
                        retries += 1

                        # get_exponential_backoff_interval computes integers
                        # and time.sleep accept floats for sub second sleep
                        sleep_amount = get_exponential_backoff_interval(
                            self.base_sleep_between_retries_ms, retries,
                            self.max_sleep_between_retries_ms, True) / 1000
                        await self._sleep(sleep_amount)
                    else:
                        raise_with_context(
                            BackendStoreError("failed to store result on the backend", task_id=task_id, state=state),
                        )
                else:
                    raise

    async def _sleep(self, amount):
        await asyncio.sleep(amount)

    async def _set_with_state(self, key, value, state):
        return await self.set(key, value)

    async def _wait_for_single_future(self, result, timeout):
        if await result.ready():
            return
        if result.fulfilled:
            # N.B future might have been set and removed
            # after last await. So a double check is needed here.
            return

        future = self._pending_future[result.id][id(result)]
        try:
            await asyncio.wait_for(asyncio.shield(future), timeout=timeout)
        except asyncio.TimeoutError:
            pass

    async def wait_for_future(self, result, timeout):
        if isinstance(result, GroupResult):
            results = result.results
        else:
            results = [result]

        await asyncio.gather(*[
            self._wait_for_single_future(r, timeout)
            for r in results
        ])

    def maybe_set_future(self, task_id, result):
        if task_id not in self._pending_future:
            return

        logger.debug(f'Set result for task[{task_id}]')
        for future in self._pending_future[task_id].values():
            if not future.done():
                future.set_result(result)

    def remove_pending_future(self, result):
        task_id = result.id
        mapping = self._pending_future.get(task_id)
        if mapping is not None:
            logger.debug(f'Remove pending future {task_id} -> {id(result)}')
            mapping.pop(id(result), None)
            if not mapping:
                self._pending_future.pop(task_id)

    async def restore_group(self, group_id, cache=True):
        meta = await self.get_group_meta(group_id, cache=cache)
        if meta:
            return meta['result']

    async def get_group_meta(self, group_id, cache=True):
        self._ensure_not_eager()
        if cache:
            try:
                return self._cache[group_id]
            except KeyError:
                pass

        meta = await self._restore_group(group_id)
        if cache and meta is not None:
            self._cache[group_id] = meta
        return meta

    async def _restore_group(self, group_id):
        """Get task meta-data for a task by id."""
        meta = await self.get(self.get_key_for_group(group_id))
        # previously this was always pickled, but later this
        # was extended to support other serializers, so the
        # structure is kind of weird.
        if meta:
            meta = self.decode(meta)
            result = meta['result']
            meta['result'] = await result_from_tuple(result, self.app)
            return meta

    async def _save_group(self, group_id, result):
        await self._set_with_state(
            self.get_key_for_group(group_id),
            self.encode({'result': result.as_tuple()}),
            states.SUCCESS
        )
        return result

    async def iter_native(self, result, no_ack=True, **kwargs):
        self._ensure_not_eager()

        results = result.results
        if not results:
            raise StopIteration()

        # we tell the result consumer to put consumed results
        # into these buckets.
        bucket = deque()
        for node in results:
            if not hasattr(node, '_cache'):
                bucket.append(node)
            elif node._cache:
                bucket.append(node)
            else:
                self._collect_into(node, bucket)

        await self._wait_for_pending(result, no_ack=no_ack, **kwargs)
        while bucket:
            node = bucket.popleft()
            if not hasattr(node, '_cache'):
                yield node.id, node.children
            else:
                yield node.id, node._cache

        while bucket:
            node = bucket.popleft()
            yield node.id, node._cache

    async def get_many(
        self, task_ids, timeout=None, interval=0.5, no_ack=True,
        on_message=None, on_interval=None, max_iterations=None,
        READY_STATES=states.READY_STATES
    ):
        interval = 0.5 if interval is None else interval
        ids = task_ids if isinstance(task_ids, set) else set(task_ids)
        cached_ids = set()
        cache = self._cache
        for task_id in ids:
            try:
                cached = cache[task_id]
            except KeyError:
                pass
            else:
                if cached['status'] in READY_STATES:
                    yield bytes_to_str(task_id), cached
                    cached_ids.add(task_id)

        ids.difference_update(cached_ids)
        iterations = 0
        while ids:
            keys = list(ids)
            r = self._mget_to_results(
                await self.mget(
                    [self.get_key_for_task(k)
                     for k in keys]
                ), keys, READY_STATES
            )
            cache.update(r)
            ids.difference_update({bytes_to_str(v) for v in r})
            for key, value in r.items():
                if on_message is not None:
                    on_message(value)
                yield bytes_to_str(key), value
            if timeout and iterations * interval >= timeout:
                raise TimeoutError(f'Operation timed out ({timeout})')
            if on_interval:
                on_interval()
            time.sleep(interval)  # don't busy loop.
            iterations += 1
            if max_iterations and iterations >= max_iterations:
                break


class SentinelBackend(RedisBackend):
    sentinel = getattr(aioredis, "sentinel", None)

    if TYPE_CHECKING:
        from redis.asyncio.sentinel import Sentinel
        def _get_sentinel_instance(self, **params) -> Sentinel: ...

    def _params_from_url(self, url, defaults):
        chunks = url.split(";")
        connparams = dict(defaults, hosts=[])
        for chunk in chunks:
            data = super()._params_from_url(
                url=chunk, defaults=defaults)
            connparams['hosts'].append(data)
        for param in ("host", "port", "db", "password"):
            connparams.pop(param)

        # Adding db/password in connparams to connect to the correct instance
        for param in ("db", "password"):
            if connparams['hosts'] and param in connparams['hosts'][0]:
                connparams[param] = connparams['hosts'][0].get(param)
        return connparams

    _get_sentinel_instance = SyncSentinelBackend._get_sentinel_instance # noqa
    _get_pool = SyncSentinelBackend._get_pool # noqa


class ClusterBackend(RedisBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connparams.pop('db')
        self.connection_errors += (RedisClusterException, )

    def _params_from_url(self, url, defaults):
        chunks = url.split(";")
        connparams = dict(defaults, hosts=[])
        for chunk in chunks:
            data = super()._params_from_url(
                url=chunk, defaults=defaults)
            connparams['hosts'].append(data)
        for param in ("host", "port", "db", "password"):
            connparams.pop(param)

        # Adding db/password in connparams to connect to the correct instance
        for param in ("db", "password"):
            if connparams['hosts'] and param in connparams['hosts'][0]:
                connparams[param] = connparams['hosts'][0].get(param)
        return connparams

    def _get_pool(self, **params):
        return NotImplementedError

    def _create_client(self, **params):
        hosts = params.pop('hosts')
        startup_nodes = [
            cluster.ClusterNode(conf['host'], conf['port'])
            for conf in hosts
        ]
        return cluster.RedisCluster(**params, startup_nodes=startup_nodes)

    async def _set(self, key, value):
        async with self.client.pipeline() as pipe:
            if self.expires:
                pipe.setex(key, self.expires, value)
            else:
                pipe.set(key, value)
            await pipe.execute()
        await self.client.publish(key, value)
