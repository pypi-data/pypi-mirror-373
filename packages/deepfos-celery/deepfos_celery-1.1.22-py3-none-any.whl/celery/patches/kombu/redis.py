import asyncio
import contextlib
import socket
import functools
import warnings

from itertools import count
from contextlib import asynccontextmanager
from time import monotonic, time
from typing import *
from urllib.parse import urlparse

import redis
import redis.asyncio as aioredis
import numbers

from redis.asyncio import (
    sentinel,
    cluster
)
from redis import exceptions
from kombu.transport.redis import (
    Transport as SyncTransport,
    Channel as SyncChannel,
    MultiChannelPoller as SyncMultiChannelPoller,
    QoS as SyncQoS,
    PrefixedStrictRedis,
    error_classes_t,
    virtual,
    dumps,
    loads,
    cycle_by_name,
    bytes_to_str,
    InconsistencyError,
    VersionMismatch,
    Empty,
    MutexHeld,

    crit,
    warn,
    _parse_url, DEFAULT_HEALTH_CHECK_INTERVAL, MultiChannelPoller,
)
from kombu.transport.virtual.base import (
    UNDELIVERABLE_FMT,
    queue_declare_ok_t,
    uuid,
    ChannelError,
    UndeliverableWarning,
    FairCycle,
)
from redis.exceptions import MovedError

from .exchange import STANDARD_EXCHANGE_TYPES
from .utils import is_async_callable
from celery.patches.redis import ClusterConnectionPool
from celery.utils.log import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def Mutex(client: aioredis.Redis, name, expire):
    """Acquire redis lock in non blocking way.

    Raise MutexHeld if not successful.
    """
    lock = client.lock(name, timeout=expire)
    lock_acquired = False
    try:
        lock_acquired = await lock.acquire(blocking=False)
        if lock_acquired:
            yield
        else:
            raise MutexHeld()
    finally:
        if lock_acquired:
            try:
                await lock.release()
            except exceptions.LockNotOwnedError:
                # when lock is expired
                pass


class QoS(SyncQoS):
    @asynccontextmanager
    async def pipe_or_acquire(self, pipe=None, client=None):
        if pipe:
            yield pipe
        else:
            with self.channel.conn_or_acquire(client) as client:
                async with client.pipeline() as pipe:
                    yield pipe

    async def _remove_from_indices(self, delivery_tag, pipe=None):
        async with self.pipe_or_acquire(pipe) as pipe:
            return pipe.zrem(self.unacked_index_key, delivery_tag) \
                       .hdel(self.unacked_key, delivery_tag)

    async def append(self, message, delivery_tag):
        delivery = message.delivery_info
        EX, RK = delivery['exchange'], delivery['routing_key']
        zadd_args = [{delivery_tag: time()}]

        async with self.pipe_or_acquire() as pipe:
            await (pipe
                .zadd(self.unacked_index_key, *zadd_args)
                .hset(self.unacked_key, delivery_tag,
                      dumps([message._raw, EX, RK]))
                .execute()
            )
            if self._dirty:
                self._flush()
            self._quick_append(delivery_tag, message)

    async def restore_unacked(self, client=None):
        with self.channel.conn_or_acquire(client) as client:
            for tag in self._delivered:
                await self.restore_by_tag(tag, client=client)
        self._delivered.clear()

    async def ack(self, delivery_tag):
        pipe = await self._remove_from_indices(delivery_tag)
        await pipe.execute()
        self._quick_ack(delivery_tag)

    async def reject(self, delivery_tag, requeue=False):
        if requeue:
            await self.restore_by_tag(delivery_tag, leftmost=True)
        await self.ack(delivery_tag)

    async def restore_visible(self, start=0, num=10, interval=10):
        self._vrestore_count += 1
        if (self._vrestore_count - 1) % interval:
            return
        with self.channel.conn_or_acquire() as client:
            ceil = time() - self.visibility_timeout
            try:
                async with Mutex(client, self.unacked_mutex_key,
                           self.unacked_mutex_expire):
                    visible = await client.zrevrangebyscore(
                        self.unacked_index_key, ceil, 0,
                        start=num and start, num=num, withscores=True)
                    for tag, score in visible or []:
                        await self.restore_by_tag(tag, client)
            except MutexHeld:
                pass

    async def restore_by_tag(self, tag, client=None, leftmost=False):

        async def restore_transaction(pipe):
            p = pipe.hget(self.unacked_key, tag)
            pipe.multi()
            pipe = await self._remove_from_indices(tag, pipe)
            if p:
                M, EX, RK = loads(bytes_to_str(p))  # json is unicode
                await self.channel._do_restore_message(M, EX, RK, pipe, leftmost)

        with self.channel.conn_or_acquire(client) as client:
            await client.transaction(restore_transaction, self.unacked_key)


class AsyncFairCycle(FairCycle):
    async def get(self, callback, **kwargs):
        """Get from next resource."""
        for tried in count(0):  # for infinity
            resource = self._next()
            try:
                return await self.fun(resource, callback, **kwargs)
            except self.predicate:
                # reraise when retries exchausted.
                if tried >= len(self.resources) - 1:
                    raise


def get_redis_error_classes():
    # This exception suddenly changed name between redis-py versions
    if hasattr(exceptions, 'InvalidData'):
        DataError = exceptions.InvalidData
    else:
        DataError = exceptions.DataError

    return error_classes_t(
        (virtual.Transport.connection_errors + (
            InconsistencyError,
            socket.error,
            IOError,
            OSError,
            exceptions.ConnectionError,
            exceptions.AuthenticationError,
            exceptions.TimeoutError,
            RuntimeError,  # uvloop might raise this
        )),
        (virtual.Transport.channel_errors + (
            DataError,
            exceptions.InvalidResponse,
            exceptions.ResponseError)),
    )


class PatchedChannel(SyncChannel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._counter = self._last_counter = 0

    def _brpop_start(self, timeout=1):
        queues = self._queue_cycle.consume(len(self.active_queues))
        if not queues:
            return

        self._counter = (self._counter + 1) % 86400
        keys = [self._q_for_pri(queue, pri) for pri in self.priority_steps
                for queue in queues] + [timeout or 0]
        self._in_poll = self.client.connection

        command_args = ['BRPOP', *keys]
        if self.global_keyprefix:
            command_args = self.client._prefix_args(command_args)

        self.client.connection.send_command(*command_args)

    def check_brpop_health(self):
        if self._last_counter == self._counter:
            raise IOError(f"BRPOP haven't been issued after 10 seconds")
        self._last_counter = self._counter


class PatchedMultiChannelPoller(MultiChannelPoller):
    def check_channel_health(self):
        for channel in self._channels:
            if channel.active_queues:
                channel.check_brpop_health()


class PatchedTransport(SyncTransport):
    health_check_interval = 0

    Channel = PatchedChannel

    def register_with_event_loop(self, connection, loop):
        super().register_with_event_loop(connection, loop)
        if self.health_check_interval > 0:
            logger.info(f"check channel health every {self.health_check_interval} seconds")
            loop.call_repeatedly(
                self.health_check_interval,
                self.cycle.check_channel_health
            )
        else:
            logger.info("check channel health disabled")


class Channel(PatchedChannel):
    QoS = QoS
    connection_class = aioredis.Connection
    connection_class_ssl = aioredis.SSLConnection
    exchange_types = dict(STANDARD_EXCHANGE_TYPES)

    if TYPE_CHECKING:
        from redis.asyncio.client import PubSub
        @property
        def subclient(self) -> PubSub: ...  # noqa

    def __init__(self, *args, **kwargs):
        virtual.Channel.__init__(self, *args, **kwargs)

        if not self.ack_emulation:  # disable visibility timeout
            self.QoS = virtual.QoS

        self._queue_cycle = cycle_by_name(self.queue_order_strategy)()
        self.Client = self._get_client()
        self.ResponseError = self._get_response_error()
        self.active_fanout_queues = set()
        self.auto_delete_queues = set()
        self._fanout_to_queue = {}
        self.handlers = {'BRPOP': self._brpop_read, 'LISTEN': self._receive}

        if self.fanout_prefix:
            if isinstance(self.fanout_prefix, str):
                self.keyprefix_fanout = self.fanout_prefix
        else:
            # previous versions did not set a fanout, so cannot enable
            # by default.
            self.keyprefix_fanout = ''

        self.connection.cycle.add(self)  # add to channel poller.
        # copy errors, in case channel closed but threads still
        # are still waiting for data.
        self.connection_errors = self.connection.connection_errors
        self._conn_evaled = False

        self._brpop_task: asyncio.Task = None
        self._listen_task: asyncio.Task = None

        # if register_after_fork is not None:
        #     register_after_fork(self, _after_fork_cleanup_channel)

    async def ping(self):
        return await self.client.ping()

    async def _after_fork(self):
        await self._disconnect_pools()

    async def _disconnect_pools(self):
        pool = self._pool
        async_pool = self._async_pool
        is_same_pool = pool is async_pool

        self._async_pool = self._pool = None

        if pool is not None:
            await pool.disconnect()

        if not is_same_pool and async_pool is not None:
            await async_pool.disconnect()

    async def _do_restore_message(self, payload, exchange, routing_key,
                            pipe, leftmost=False):
        try:
            try:
                payload['headers']['redelivered'] = True
                payload['properties']['delivery_info']['redelivered'] = True
            except KeyError:
                pass
            for queue in await self._lookup(exchange, routing_key):
                await (pipe.lpush if leftmost else pipe.rpush)(
                    queue, dumps(payload),
                )
        except Exception:
            crit('Could not restore message: %r', payload, exc_info=True)

    async def _restore(self, message, leftmost=False):
        if not self.ack_emulation:
            delivery_info = message.delivery_info
            message = message.serializable()
            message['redelivered'] = True
            for queue in await self._lookup(
                delivery_info['exchange'], delivery_info['routing_key']
            ):
                await self._put(queue, message)
            return

        tag = message.delivery_tag

        async def restore_transaction(pipe):
            P = await pipe.hget(self.unacked_key, tag)
            pipe.multi()
            await pipe.hdel(self.unacked_key, tag)
            if P:
                M, EX, RK = loads(bytes_to_str(P))  # json is unicode
                await self._do_restore_message(M, EX, RK, pipe, leftmost)

        with self.conn_or_acquire() as client:
            await client.transaction(restore_transaction, self.unacked_key)

    async def _restore_at_beginning(self, message):
        return await self._restore(message, leftmost=True)

    def _get_response_error(self):
        return exceptions.ResponseError

    async def _get(self, queue):
        with self.conn_or_acquire() as client:
            for pri in self.priority_steps:
                item = await client.rpop(self._q_for_pri(queue, pri))
                if item:
                    return loads(bytes_to_str(item))
            raise Empty()

    async def _size(self, queue):
        with self.conn_or_acquire() as client:
            async with client.pipeline() as pipe:
                for pri in self.priority_steps:
                    pipe = pipe.llen(self._q_for_pri(queue, pri))
                sizes = await pipe.execute()
        return sum(size for size in sizes
                   if isinstance(size, numbers.Integral))

    async def _put(self, queue, message, **kwargs):
        """Deliver message."""
        pri = self._get_message_priority(message, reverse=False)

        with self.conn_or_acquire() as client:
            await client.lpush(self._q_for_pri(queue, pri), dumps(message))

    async def _put_fanout(self, exchange, message, routing_key, **kwargs):
        """Deliver fanout message."""
        with self.conn_or_acquire() as client:
            await client.publish(
                self._get_publish_topic(exchange, routing_key),
                dumps(message),
            )

    async def _queue_bind(self, exchange, routing_key, pattern, queue):
        if self.typeof(exchange).type == 'fanout':
            # Mark exchange as fanout.
            self._fanout_queues[queue] = (
                exchange, routing_key.replace('#', '*'),
            )
        with self.conn_or_acquire() as client:
            await client.sadd(
                self.keyprefix_queue % (exchange,),
                self.sep.join([routing_key or '', pattern or '', queue or ''])
            )

    async def _delete(self, queue, exchange, routing_key, pattern, *args, **kwargs):
        self.auto_delete_queues.discard(queue)
        with self.conn_or_acquire(client=kwargs.get('client')) as client:
            await client.srem(self.keyprefix_queue % (exchange,),
                        self.sep.join([routing_key or '',
                                       pattern or '',
                                       queue or '']))
            async with client.pipeline() as pipe:
                for pri in self.priority_steps:
                    pipe = pipe.delete(self._q_for_pri(queue, pri))
                await pipe.execute()

    async def _has_queue(self, queue, **kwargs):
        with self.conn_or_acquire() as client:
            async with client.pipeline() as pipe:
                for pri in self.priority_steps:
                    pipe = pipe.exists(self._q_for_pri(queue, pri))
                return any(await pipe.execute())

    async def get_table(self, exchange):
        key = self.keyprefix_queue % exchange
        with self.conn_or_acquire() as client:
            values = await client.smembers(key)
            if not values:
                # table does not exists since all queues bound to the exchange
                # were deleted. We need just return empty list.
                return []
            return [tuple(bytes_to_str(val).split(self.sep)) for val in values]

    async def _purge(self, queue):
        with self.conn_or_acquire() as client:
            async with client.pipeline() as pipe:
                for pri in self.priority_steps:
                    priq = self._q_for_pri(queue, pri)
                    pipe = pipe.llen(priq).delete(priq)
                sizes = await pipe.execute()
                return sum(sizes[::2])

    async def close(self):
        self._closing = True
        if not self.closed:
            # remove from channel poller.
            self.connection.cycle.discard(self)

            # delete fanout bindings
            client = self.__dict__.get('client')  # only if property cached
            if client is not None:
                for queue in self._fanout_queues:
                    if queue in self.auto_delete_queues:
                        await self.queue_delete(queue, client=client)
            await self._disconnect_pools()
            await self._close_clients()

            # --------------------------------------
            # virtual.base::Channel
            self.closed = True

            for consumer in list(self._consumers):
                self.basic_cancel(consumer)  # todo maybe await
            if self._qos:
                self._qos.restore_unacked_once()
            if self._cycle is not None:
                self._cycle.close()
                self._cycle = None
            if self.connection is not None:
                self.connection.close_channel(self)  # todo maybe await
        self.exchange_types = None

    async def _close_clients(self):
        for attr in 'client', 'subclient':
            try:
                client = self.__dict__[attr]
                connection, client.connection = client.connection, None
                await connection.disconnect()
            except (KeyError, AttributeError, self.ResponseError):
                pass

    def _connparams(self, asynchronous=False):
        params = super(Channel, self)._connparams(asynchronous)
        channel = self

        if asynchronous:
            class Connection(self.connection_class):
                async def disconnect(self, nowait: bool = False):
                    await super().disconnect(nowait=nowait)
                    channel._on_connection_disconnect(self)

            params['connection_class'] = Connection
        return params

    def _get_pool(self, asynchronous=True):
        params = self._connparams(asynchronous=True)
        self.keyprefix_fanout = self.keyprefix_fanout.format(db=params['db'])
        return aioredis.ConnectionPool(**params)

    def _get_client(self):
        if getattr(redis, 'VERSION', (1, 0)) < (4, 1, 0):
            raise VersionMismatch(
                'Redis transport requires redis versions 4.1.0 or later. '
                f'You have {redis.__version__}')

        if self.global_keyprefix:
            return functools.partial(
                PrefixedStrictRedis,
                global_keyprefix=self.global_keyprefix,
            )
        return aioredis.StrictRedis

    # -----------------------------------------------------------------------------
    # virtual.base::Channel method overload
    async def queue_delete(self, queue, if_unused=False, if_empty=False, **kwargs):
        """Delete queue."""
        if if_empty and self._size(queue):
            return
        for exchange, routing_key, args in self.state.queue_bindings(queue):
            meta = self.typeof(exchange).prepare_bind(
                queue, exchange, routing_key, args,
            )
            await self._delete(queue, exchange, *meta, **kwargs)
        self.state.queue_bindings_delete(queue)

    async def after_reply_message_received(self, queue):
        await self.queue_delete(queue)

    async def queue_bind(self, queue, exchange=None, routing_key='',
                   arguments=None, **kwargs):
        """Bind `queue` to `exchange` with `routing key`."""
        exchange = exchange or 'amq.direct'
        if self.state.has_binding(queue, exchange, routing_key):
            return
        # Add binding:
        self.state.binding_declare(queue, exchange, routing_key, arguments)
        # Update exchange's routing table:
        table = self.state.exchanges[exchange].setdefault('table', [])
        meta = self.typeof(exchange).prepare_bind(
            queue, exchange, routing_key, arguments,
        )
        table.append(meta)
        if self.supports_fanout:
            await self._queue_bind(exchange, *meta)

    async def queue_unbind(self, queue, exchange=None, routing_key='',
                     arguments=None, **kwargs):
        # Remove queue binding:
        self.state.binding_delete(queue, exchange, routing_key)
        try:
            table = await self.get_table(exchange)
        except KeyError:
            return
        binding_meta = self.typeof(exchange).prepare_bind(
            queue, exchange, routing_key, arguments,
        )
        # TODO: the complexity of this operation is O(number of bindings).
        # Should be optimized.  Modifying table in place.
        table[:] = [meta for meta in table if meta != binding_meta]

    async def list_bindings(self):
        return ((queue, exchange, rkey)
                for exchange in self.state.exchanges
                for rkey, pattern, queue in await self.get_table(exchange))

    async def queue_declare(self, queue=None, passive=False, **kwargs):
        """Declare queue."""
        queue = queue or 'amq.gen-%s' % uuid()
        if passive and not (await self._has_queue(queue, **kwargs)):
            raise ChannelError(
                'NOT_FOUND - no queue {!r} in vhost {!r}'.format(
                    queue, self.connection.client.virtual_host or '/'),
                (50, 10), 'Channel.queue_declare', '404',
            )
        else:
            self._new_queue(queue, **kwargs)
        return queue_declare_ok_t(queue, await self._size(queue), 0)

    async def queue_purge(self, queue, **kwargs):
        """Remove all ready messages from queue."""
        return await self._purge(queue)

    async def basic_publish(self, message, exchange, routing_key, **kwargs):
        """Publish message."""
        self._inplace_augment_message(message, exchange, routing_key)
        if exchange:
            return await self.typeof(exchange).deliver(
                message, exchange, routing_key, **kwargs
            )
        # anon exchange: routing_key is the destination queue
        return await self._put(routing_key, message, **kwargs)

    async def basic_get(self, queue, no_ack=False, **kwargs):
        """Get message by direct access (synchronous)."""
        try:
            message = self.Message((await self._get(queue)), channel=self)
            if not no_ack:
                self.qos.append(message, message.delivery_tag)
            return message
        except Empty:
            pass

    async def _lookup(self, exchange, routing_key, default=None):
        """Find all queues matching `routing_key` for the given `exchange`.

        Returns:
            str: queue name -- must return the string `default`
                if no queues matched.
        """
        if default is None:
            default = self.deadletter_queue
        if not exchange:  # anon exchange
            return [routing_key or default]

        try:
            R = self.typeof(exchange).lookup(
                await self.get_table(exchange),
                exchange, routing_key, default,
            )
        except KeyError:
            R = []

        if not R and default is not None:
            warnings.warn(UndeliverableWarning(UNDELIVERABLE_FMT.format(
                exchange=exchange, routing_key=routing_key)),
            )
            self._new_queue(default)
            R = [default]
        return R

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

    def _reset_cycle(self):
        self._cycle = AsyncFairCycle(
            self._get_and_deliver, self._active_queues, Empty)

    async def _get_and_deliver(self, queue, callback):
        message = await self._get(queue)
        callback(message, queue)

    # -----------------------------------------------------------------------------
    # exchange
    async def exchange_delete(self, exchange, if_unused=False, nowait=False):
        """Delete `exchange` and all its bindings."""
        for rkey, _, queue in (await self.get_table(exchange)):
            await self.queue_delete(queue, if_unused=True, if_empty=True)
        self.state.exchanges.pop(exchange, None)

    # -----------------------------------------------------------------------------
    # consumer
    async def _brpop_start(self, timeout=1):
        queues = self._queue_cycle.consume(len(self.active_queues))
        if not queues:
            return

        keys = [self._q_for_pri(queue, pri) for pri in self.priority_steps
                for queue in queues] + [timeout or 0]

        command_args = ['BRPOP', *keys]
        if self.global_keyprefix:
            command_args = self.client._prefix_args(command_args)

        async def brpop(conn):
            await conn.send_command(*command_args)
            return await self._brpop_read_impl()

        self._in_poll = True
        self._brpop_task = task = asyncio.create_task(
            brpop(self.client.connection))

        await asyncio.sleep(0)
        return task

    async def _brpop_read_impl(self, **options):
        try:
            dest__item = await self.client.parse_response(
                self.client.connection,
                'BRPOP',
                **options
            )
        except self.connection_errors:
            # if there's a ConnectionError, disconnect so the next
            # iteration will reconnect automatically.
            await self.client.connection.disconnect()
            raise
        if dest__item:
            dest, item = dest__item
            dest = bytes_to_str(dest).rsplit(self.sep, 1)[0]
            self._queue_cycle.rotate(dest)
            self.connection._deliver(loads(bytes_to_str(item)), dest)
            return True
        else:
            raise Empty()

    def _brpop_read(self, **options):
        try:
            return self._brpop_task.result()
        finally:
            self._brpop_task = None
            self._in_poll = None

    async def _subscribe(self):
        keys = [self._get_subscribe_topic(queue)
                for queue in self.active_fanout_queues]
        if not keys:
            return
        c = self.subclient
        if not c.connection.is_connected:
            await c.connection.connect()
        self._in_listen = c.connection
        await c.psubscribe(keys)
        self._listen_task = t = asyncio.create_task(c.parse_response())
        await asyncio.sleep(0)
        return t

    async def _unsubscribe_from(self, queue):
        topic = self._get_subscribe_topic(queue)
        c = self.subclient
        if c.connection and c.connection.is_connected:
            await c.unsubscribe([topic])

    def _receive_one(self, c):
        try:
            response = self._listen_task.result()
        except self.connection_errors:
            self._in_listen = None
            raise
        finally:
            self._listen_task = None
        if isinstance(response, (list, tuple)):
            payload = self._handle_message(c, response)
            if bytes_to_str(payload['type']).endswith('message'):
                channel = bytes_to_str(payload['channel'])
                if payload['data']:
                    if channel[0] == '/':
                        _, _, channel = channel.partition('.')
                    try:
                        message = loads(bytes_to_str(payload['data']))
                    except (TypeError, ValueError):
                        warn('Cannot process event on channel %r: %s',
                             channel, repr(payload)[:4096], exc_info=1)
                        raise Empty()
                    exchange = channel.split('/', 1)[0]
                    self.connection._deliver(
                        message, self._fanout_to_queue[exchange])
                    return True


class MultiChannelPoller(SyncMultiChannelPoller):
    def __init__(self):
        self._channels = set()
        self._pending_tasks = set()

    @staticmethod
    async def ensure_connection(client):
        conn = getattr(client, 'connection', None)
        if conn is None:
            client.connection = await client.connection_pool.get_connection('_')
        elif not conn.is_connected:
            await client.connection.connect()

    async def _register_BRPOP(self, channel):
        """Enable BRPOP mode for channel."""
        await self.ensure_connection(channel.client)

        if not channel._in_poll:  # send BRPOP
            task = await channel._brpop_start()
            task.channel = channel
            task.cmd = 'BRPOP'
            self._pending_tasks.add(task)

    async def _register_LISTEN(self, channel):
        """Enable LISTEN mode for channel."""
        await self.ensure_connection(channel.client)

        if not channel._in_listen:
            task = await channel._subscribe()  # send SUBSCR
            task.channel = channel
            task.cmd = 'LISTEN'
            self._pending_tasks.add(task)

    async def poll(self, timeout):
        if not self._pending_tasks:
            return

        done, pending = await asyncio.wait(
            self._pending_tasks,
            timeout=timeout,
            return_when=asyncio.FIRST_COMPLETED
        )
        for task in done:
            self._pending_tasks.discard(task)
        if not done:
            return
        else:
            return done.pop()

    @staticmethod
    async def handle_task(task):
        chan = task.channel  # noqa
        type = task.cmd  # noqa

        if chan.qos.can_consume():
            hdlr = chan.handlers[type]
            if is_async_callable(hdlr):
                await hdlr()
            else:
                hdlr()

        return True

    async def get(self, callback, timeout=None):
        self._in_protected_read = True
        try:
            for channel in self._channels:
                if channel.active_queues:           # BRPOP mode?
                    if channel.qos.can_consume():
                        await self._register_BRPOP(channel)
                if channel.active_fanout_queues:    # LISTEN mode?
                    await self._register_LISTEN(channel)

            if (
                (done_task := await self.poll(timeout))
                and (await self.handle_task(done_task))
            ):
                return
            # - no new data, so try to restore messages.
            # - reset active redis commands.
            await self.maybe_restore_messages()
            raise Empty()
        finally:
            self._in_protected_read = False
            while self.after_read:
                try:
                    fun = self.after_read.pop()
                except KeyError:
                    break
                else:
                    fun()

    async def maybe_restore_messages(self):
        for channel in self._channels:
            if channel.active_queues:
                # only need to do this once, as they are not local to channel.
                return await channel.qos.restore_visible(
                    num=channel.unacked_restore_limit,
                )


class Transport(SyncTransport):
    Channel = Channel
    connection_errors, channel_errors = get_redis_error_classes()
    Poller = MultiChannelPoller

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # All channels share the same poller.
        self.cycle = self.Poller()

    async def establish_connection(self):
        channel: Channel = self.create_channel(self)
        await channel.ping()
        self._avail_channels.append(channel)
        return self     # for drain events

    async def close_connection(self, connection):
        self.cycle.close()
        for chan_list in self._avail_channels, self.channels:
            while chan_list:
                try:
                    channel = chan_list.pop()
                except LookupError:  # pragma: no cover
                    pass
                else:
                    await channel.close()

    async def drain_events(self, connection, timeout=None):
        time_start = monotonic()
        get = self.cycle.get
        polling_interval = self.polling_interval
        if timeout and polling_interval and polling_interval > timeout:
            polling_interval = timeout
        while 1:
            try:
                await get(self._deliver, timeout=timeout)
            except Empty:
                if timeout is not None and monotonic() - time_start >= timeout:
                    raise socket.timeout()
                if polling_interval is not None:
                    await asyncio.sleep(polling_interval)
            else:
                break


class SentinelManagedSSLConnection(
        sentinel.SentinelManagedConnection,
        aioredis.SSLConnection):
    pass


class SentinelChannel(Channel):
    from_transport_options = Channel.from_transport_options + (
        'master_name',
        'min_other_sentinels',
        'sentinel_kwargs')

    connection_class = sentinel.SentinelManagedConnection
    connection_class_ssl = SentinelManagedSSLConnection

    def _sentinel_managed_pool(self, asynchronous=False):
        connparams = self._connparams(asynchronous)

        additional_params = connparams.copy()

        additional_params.pop('host', None)
        additional_params.pop('port', None)

        sentinels = []
        for url in self.connection.client.alt:
            url = _parse_url(url)
            if url.scheme == 'sentinel':
                port = url.port or self.connection.default_port
                sentinels.append((url.hostname, port))

        # Fallback for when only one sentinel is provided.
        if not sentinels:
            sentinels.append((connparams['host'], connparams['port']))

        sentinel_inst = sentinel.Sentinel(
            sentinels,
            min_other_sentinels=getattr(self, 'min_other_sentinels', 0),
            sentinel_kwargs=getattr(self, 'sentinel_kwargs', None),
            **additional_params)

        master_name = getattr(self, 'master_name', None)

        if master_name is None:
            raise ValueError(
                "'master_name' transport option must be specified."
            )

        return sentinel_inst.master_for(
            master_name,
            self.Client,
        ).connection_pool

    def _get_pool(self, asynchronous=False):
        return self._sentinel_managed_pool(asynchronous)


class SentinelTransport(Transport):
    """Redis Sentinel Transport."""

    default_port = 26379
    Channel = SentinelChannel


class ClusterPoller(MultiChannelPoller):
    @staticmethod
    async def ensure_connection(client: cluster.RedisCluster):
        if client._initialize:
            await client.initialize()

    async def _register_BRPOP(self, channel):
        """Enable BRPOP mode for channel."""

        if not channel._in_poll:  # send BRPOP
            task = await channel._brpop_start()
            task.channel = channel
            task.cmd = 'BRPOP'
            self._pending_tasks.add(task)


async def wait_util_first_complete(*coros):
    futs = map(asyncio.ensure_future, coros)
    done, pending = await asyncio.wait(
        futs, return_when=asyncio.FIRST_COMPLETED)
    for fut in pending:
        assert isinstance(fut, asyncio.Future)
        try:
            fut.cancel()
        except Exception:  # noqa
            pass
    return done.pop()


class ClusterQoS(QoS):
    async def restore_by_tag(self, tag, client=None, leftmost=False):
        assert isinstance(client, cluster.RedisCluster)
        node = client.get_node_from_key(self.unacked_key)
        redis_cli = aioredis.Redis(
            connection_pool=ClusterConnectionPool(client, node))
        return await super().restore_by_tag(tag, redis_cli, leftmost)


class ClusterChannleMixin:
    socket_keepalive = True

    namespace = '{celery}'
    keyprefix_queue = '/{namespace}/_kombu/binding%s'
    keyprefix_fanout = '/{namespace}/_kombu/fanout.'
    unacked_key = '/{namespace}/_kombu/unacked'
    unacked_index_key = '/{namespace}/_kombu/unacked_index'
    unacked_mutex_key = '/{namespace}/_kombu/unacked_mutex'

    min_priority = 0
    max_priority = 0
    priority_steps = [min_priority]

    def _patch_options(self, options):
        namespace = options.get('namespace', self.namespace)
        keys = [
            'keyprefix_queue',
            'keyprefix_fanout',
            'unacked_key',
            'unacked_index_key',
            'unacked_mutex_key',
        ]

        for key in keys:
            if key not in options:
                value = options.get(key, getattr(self, key))
                options[key] = value.format(namespace=namespace)

    def _get_pool(self, asynchronous=False):
        raise NotImplementedError


class ClusterChannel(ClusterChannleMixin, Channel):
    QoS = ClusterQoS
    connection_class = cluster.Connection

    from_transport_options = Channel.from_transport_options + (
        'namespace',
        'keyprefix_queue',
        'keyprefix_fanout',
    )
    client: cluster.RedisCluster

    def __init__(self, conn, *args, **kwargs):
        options = conn.client.transport_options
        self._patch_options(options)
        super().__init__(conn, *args, **kwargs)
        self._default_client = self._create_client()
        self.connection_errors += (
            exceptions.ClusterError,
        )

    @contextlib.contextmanager
    def conn_or_acquire(self, client=None):
        if client:
            yield client
        else:
            yield self._default_client

    def _get_client(self):
        return cluster.RedisCluster

    def _create_client(self, asynchronous=False):
        params = self._connparams(asynchronous=False)
        params.pop('db', None)
        params.pop('connection_class', None)
        startup_nodes = []
        for url in self.connection.client.alt:
            parsed = urlparse(url)
            startup_nodes.append(cluster.ClusterNode(
                parsed.hostname, parsed.port))

        return self.Client(**params, startup_nodes=startup_nodes)

    async def _brpop_read_impl(
        self,
        node: cluster.ClusterNode,
        conn: cluster.Connection,
        **options
    ):
        client = self.client
        try:
            dest__item = await node.parse_response(conn, 'BRPOP', **options)
        except self.connection_errors:
            await self.client.close()
            raise Empty()
        except MovedError as err:
            # copied from rediscluster/client.py
            client.reinitialize_counter += 1
            if (
                client.reinitialize_steps
                and client.reinitialize_counter % client.reinitialize_steps == 0
            ):
                await client.close()
                # Reset the counter
                client.reinitialize_counter = 0
            else:
                client.nodes_manager._moved_exception = err
            raise Empty()

        if dest__item:
            dest, item = dest__item
            dest = bytes_to_str(dest).rsplit(self.sep, 1)[0]
            self._queue_cycle.rotate(dest)
            self.connection._deliver(loads(bytes_to_str(item)), dest)
            return True

    async def _brpop_start(self, timeout=1):
        queues = self._queue_cycle.consume(len(self.active_queues))
        if not queues:
            return

        cli = self.client
        node_to_keys = {}

        for key in queues:
            node = cli.get_node_from_key(key)
            node_to_keys.setdefault(node.name, []).append(key)

        async def brpop(node: cluster.ClusterNode, keys):
            conn = None
            try:
                conn = node.acquire_connection()
                await conn.send_command('BRPOP', *keys)
                return await self._brpop_read_impl(node, conn)
            finally: # noqa
                if conn is not None:
                    node._free.append(conn)

        subtasks = []

        for node_name, keys in node_to_keys.items():
            node = cli.get_node(node_name=node_name)
            subtasks.append(brpop(node, keys + [timeout]))

        self._in_poll = True
        self._brpop_task = task = asyncio.create_task(
            wait_util_first_complete(*subtasks))

        await asyncio.sleep(0)
        return task

    async def close(self):
        await super().close()
        await self._default_client.close()


class ClusterTransport(Transport):
    default_port = 30001
    Channel = ClusterChannel

    driver_type = 'redis-cluster'
    driver_name = driver_type
    Poller = ClusterPoller
