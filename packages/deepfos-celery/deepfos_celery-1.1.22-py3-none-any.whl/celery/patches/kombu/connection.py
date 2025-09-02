import os
import socket
from contextlib import asynccontextmanager
from itertools import count

from kombu.connection import (
    Connection as SyncConnection,
    exceptions,
)
from kombu.utils.collections import HashedSeq
from kombu.utils.functional import lazy

from .utils import retry_over_time, Resource

_log_channel = os.environ.get('KOMBU_LOG_CHANNEL', False)


class Connection(SyncConnection):
    def register_with_event_loop(self, loop):
        return NotImplemented

    def get_transport_cls(self):
        if self.transport_cls == 'sentinel':
            from .redis import SentinelTransport
            return SentinelTransport
        elif self.transport_cls == 'redis-cluster':
            from .redis import ClusterTransport
            return ClusterTransport
        else:
            from .redis import Transport
            return Transport

    async def connect(self):
        return await self._ensure_connection(
            max_retries=1, reraise_as_library_errors=False
        )

    def ensure(self, obj, fun, errback=None, max_retries=None,
               interval_start=1, interval_step=1, interval_max=1,
               on_revive=None):
        """Ensure operation completes.

        Regardless of any channel/connection errors occurring.

        Retries by establishing the connection, and reapplying
        the function.

        Arguments:
            obj: The object to ensure an action on.
            fun (Callable): Method to apply.

            errback (Callable): Optional callback called each time the
                connection can't be established.  Arguments provided are
                the exception raised and the interval that will
                be slept ``(exc, interval)``.

            max_retries (int): Maximum number of times to retry.
                If this limit is exceeded the connection error
                will be re-raised.

            interval_start (float): The number of seconds we start
                sleeping for.
            interval_step (float): How many seconds added to the interval
                for each retry.
            interval_max (float): Maximum number of seconds to sleep between
                each retry.
            on_revive (Callable): Optional callback called whenever
                revival completes successfully

        Examples:
            >>> from kombu import Connection, Producer
            >>> conn = Connection('amqp://')
            >>> producer = Producer(conn)

            >>> def errback(exc, interval):
            ...     logger.error('Error: %r', exc, exc_info=1)
            ...     logger.info('Retry in %s seconds.', interval)

            >>> publish = conn.ensure(producer, producer.publish,
            ...                       errback=errback, max_retries=3)
            >>> publish({'hello': 'world'}, routing_key='dest')
        """

        async def _ensured(*args, **kwargs):
            got_connection = 0
            conn_errors = self.recoverable_connection_errors
            chan_errors = self.recoverable_channel_errors
            has_modern_errors = hasattr(
                self.transport, 'recoverable_connection_errors',
            )
            with self._reraise_as_library_errors():
                for retries in count(0):  # for infinity
                    try:
                        return await fun(*args, **kwargs)
                    except conn_errors as exc:
                        if got_connection and not has_modern_errors:
                            # transport can not distinguish between
                            # recoverable/irrecoverable errors, so we propagate
                            # the error if it persists after a new connection
                            # was successfully established.
                            raise
                        if max_retries is not None and retries >= max_retries:
                            raise
                        self._debug(
                            'ensure connection error: %r',
                            exc, exc_info=1
                        )
                        await self.collect()
                        errback and errback(exc, 0)
                        remaining_retries = None
                        if max_retries is not None:
                            remaining_retries = max(max_retries - retries, 1)
                        await self._ensure_connection(
                            errback,
                            remaining_retries,
                            interval_start, interval_step, interval_max,
                            reraise_as_library_errors=False,
                        )
                        channel = await self.default_channel()
                        obj.revive(channel)
                        if on_revive:
                            on_revive(channel)
                        got_connection += 1
                    except chan_errors as exc:
                        if max_retries is not None and retries > max_retries:
                            raise
                        self._debug(
                            'ensure channel error: %r',
                            exc, exc_info=1
                        )
                        errback and errback(exc, 0)

        _ensured.__name__ = f'{fun.__name__}(ensured)'
        _ensured.__doc__ = fun.__doc__
        _ensured.__module__ = fun.__module__
        return _ensured

    async def _ensure_connection(
        self, errback=None, max_retries=None,
        interval_start=2, interval_step=2, interval_max=30,
        callback=None, reraise_as_library_errors=True,
        timeout=None
    ):
        """Ensure we have a connection to the server.

        If not retry establishing the connection with the settings
        specified.

        Arguments:
            errback (Callable): Optional callback called each time the
                connection can't be established.  Arguments provided are
                the exception raised and the interval that will be
                slept ``(exc, interval)``.

            max_retries (int): Maximum number of times to retry.
                If this limit is exceeded the connection error
                will be re-raised.

            interval_start (float): The number of seconds we start
                sleeping for.
            interval_step (float): How many seconds added to the interval
                for each retry.
            interval_max (float): Maximum number of seconds to sleep between
                each retry.
            callback (Callable): Optional callback that is called for every
                internal iteration (1 s).
            timeout (int): Maximum amount of time in seconds to spend
                waiting for connection
        """
        if self.connected:
            return self._connection

        def on_error(exc, intervals, retries, interval=0):
            round = self.completes_cycle(retries)
            if round:
                interval = next(intervals)
            if errback:
                errback(exc, interval)
            self.maybe_switch_next()  # select next host

            return interval if round else 0

        ctx = self._reraise_as_library_errors
        if not reraise_as_library_errors:
            ctx = self._dummy_context
        with ctx():
            return await retry_over_time(
                self._connection_factory, self.recoverable_connection_errors,
                (), {}, on_error, max_retries,
                interval_start, interval_step, interval_max,
                callback, timeout=timeout
            )

    async def _connection_factory(self):
        self.declared_entities.clear()
        self._default_channel = None
        self._connection = await self._establish_connection()
        self._closed = False
        return self._connection

    async def _establish_connection(self):
        self._debug('establishing connection...')
        conn = await self.transport.establish_connection()
        self._debug('connection established: %r', self)
        return conn

    async def maybe_close_channel(self, channel):
        """Close given channel, but ignore connection and channel errors."""
        try:
            await channel.close()
        except (self.connection_errors + self.channel_errors):
            pass

    async def _do_close_self(self):
        # Close only connection and channel(s), but not transport.
        self.declared_entities.clear()
        if self._default_channel:
            await self.maybe_close_channel(self._default_channel)
        if self._connection:
            try:
                await self.transport.close_connection(self._connection)
            except self.connection_errors + (AttributeError, socket.error):
                pass
            self._connection = None

    async def default_channel(self):
        """Default channel.

        Created upon access and closed when the connection is closed.

        Note:
            Can be used for automatic channel handling when you only need one
            channel, and also it is the channel implicitly used if
            a connection is passed instead of a channel, to functions that
            require a channel.
        """
        # make sure we're still connected, and if not refresh.
        conn_opts = self._extract_failover_opts()
        await self._ensure_connection(**conn_opts)

        if self._default_channel is None:
            self._default_channel = self.channel()
        return self._default_channel

    async def _close(self):
        """Really close connection, even if part of a connection pool."""
        await self._do_close_self()
        self._do_close_transport()
        self._debug('closed')
        self._closed = True

    async def collect(self, socket_timeout=None):
        # amqp requires communication to close, we don't need that just
        # to clear out references, Transport._collect can also be implemented
        # by other transports that want fast after fork
        try:
            gc_transport = self._transport._collect
        except AttributeError:
            _timeo = socket.getdefaulttimeout()
            socket.setdefaulttimeout(socket_timeout)
            try:
                await self._do_close_self()
            except socket.timeout:
                pass
            finally:
                socket.setdefaulttimeout(_timeo)
        else:
            gc_transport(self._connection)

        self._do_close_transport()
        self.declared_entities.clear()
        self._connection = None

    def __eqhash__(self):
        return HashedSeq('aio' + self.transport_cls, self.hostname, self.userid,
                         self.password, self.virtual_host, self.port,
                         repr(self.transport_options))

    def Pool(self, limit=None, **kwargs):
        return ConnectionPool(self, limit, **kwargs)

    async def release(self):
        """Close the connection (if open)."""
        await self._close()

    close = release

    async def drain_events(self, **kwargs):
        return await self.transport.drain_events(self.connection, **kwargs)


class ConnectionPool(Resource):
    """Pool of connections."""
    LimitExceeded = exceptions.ConnectionLimitExceeded
    close_after_fork = True

    def __init__(self, connection: Connection, limit=None, **kwargs):
        self.connection = connection
        super().__init__(limit=limit)

    def new(self):
        return self.connection.clone()

    async def release_resource(self, resource: Connection):
        try:
            resource._debug('released')
        except AttributeError:
            pass

    async def close_resource(self, resource: Connection):
        await resource._close()

    @asynccontextmanager
    async def acquire_channel(self, block=False):
        connection: Connection
        async with self.acquire(block=block) as connection:
            yield connection, await connection.default_channel()

    def setup(self):
        if self.limit:
            q = self._resource.queue
            while len(q) < self.limit:
                self._resource.put_nowait(lazy(self.new))

    async def prepare(self, resource):
        if callable(resource):
            resource = resource()
        resource._debug('acquired')
        return resource
