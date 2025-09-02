import socket

from itertools import count
from contextlib import asynccontextmanager
from time import time

from kombu.utils import cached_property
from kombu.utils.functional import lazy
from kombu.pidbox import (
    Mailbox as SyncMailBox,
    uuid,
)

from celery.app.control import (
    Control as SyncControl,
    Inspect as SyncInspect,
    register_after_fork,
    _after_fork_cleanup_control
)
from celery.patches.kombu.messaging import Producer, Consumer
from celery.patches.kombu.exchange import Exchange
from celery.patches.kombu.entity import Queue
from celery.patches.kombu.common import maybe_declare


class Mailbox(SyncMailBox):
    def get_reply_queue(self):
        oid = self.oid
        return Queue(
            f'{oid}.{self.reply_exchange.name}',
            exchange=self.reply_exchange,
            routing_key=oid,
            durable=False,
            auto_delete=True,
            expires=self.reply_queue_expires,
            message_ttl=self.reply_queue_ttl,
        )

    def _get_exchange(self, namespace, type):
        return Exchange(self.exchange_fmt % namespace,
                        type=type,
                        durable=False,
                        delivery_mode='transient')

    @asynccontextmanager
    async def producer_or_acquire(self, producer=None, channel=None):
        if producer:
            yield producer
        elif self.producer_pool:
            async with self.producer_pool.acquire() as producer:
                yield producer
        else:
            yield Producer(channel, auto_declare=False)

    async def _broadcast(self, command, arguments=None, destination=None,
                   reply=False, timeout=1, limit=None,
                   callback=None, channel=None, serializer=None,
                   pattern=None, matcher=None):
        if destination is not None and \
                not isinstance(destination, (list, tuple)):
            raise ValueError(
                'destination must be a list/tuple not {}'.format(
                    type(destination)))
        if (pattern is not None and not isinstance(pattern, str) and
                matcher is not None and not isinstance(matcher, str)):
            raise ValueError(
                'pattern and matcher must be '
                'strings not {}, {}'.format(type(pattern), type(matcher))
            )

        arguments = arguments or {}
        reply_ticket = reply and uuid() or None
        chan = channel or (await self.connection.default_channel())

        # Set reply limit to number of destinations (if specified)
        if limit is None and destination:
            limit = destination and len(destination) or None

        serializer = serializer or self.serializer
        await self._publish(command, arguments, destination=destination,
                      reply_ticket=reply_ticket,
                      channel=chan,
                      timeout=timeout,
                      serializer=serializer,
                      pattern=pattern,
                      matcher=matcher)

        if reply_ticket:
            return await self._collect(reply_ticket, limit=limit,
                                 timeout=timeout,
                                 callback=callback,
                                 channel=chan)

    async def _publish(self, type, arguments, destination=None,
                 reply_ticket=None, channel=None, timeout=None,
                 serializer=None, producer=None, pattern=None, matcher=None):
        message = {'method': type,
                   'arguments': arguments,
                   'destination': destination,
                   'pattern': pattern,
                   'matcher': matcher}
        chan = channel or (await self.connection.default_channel())
        exchange = self.exchange
        if reply_ticket:
            await maybe_declare(self.reply_queue(chan))
            message.update(ticket=reply_ticket,
                           reply_to={'exchange': self.reply_exchange.name,
                                     'routing_key': self.oid})
        serializer = serializer or self.serializer
        if producer is None and self.connection:
            producer = Producer(self.connection, auto_declare=False)

        async with self.producer_or_acquire(producer, chan) as producer:
            await producer.publish(
                message, exchange=exchange.name, declare=[exchange],
                headers={'clock': self.clock.forward(),
                         'expires': time() + timeout if timeout else 0},
                serializer=serializer, retry=True,
            )

    async def _collect(self, ticket,
                 limit=None, timeout=1, callback=None,
                 channel=None, accept=None):
        if accept is None:
            accept = self.accept
        chan = channel or (await self.connection.default_channel())
        queue = self.reply_queue
        consumer = Consumer(chan, [queue], accept=accept, no_ack=True)
        await consumer.init()
        responses = []
        unclaimed = self.unclaimed
        adjust_clock = self.clock.adjust

        try:
            return unclaimed.pop(ticket)
        except KeyError:
            pass

        def on_message(body, message):
            # ticket header added in kombu 2.5
            header = message.headers.get
            adjust_clock(header('clock') or 0)
            expires = header('expires')
            if expires and time() > expires:
                return
            this_id = header('ticket', ticket)
            if this_id == ticket:
                if callback:
                    callback(body)
                responses.append(body)
            else:
                unclaimed[this_id].append(body)

        consumer.register_callback(on_message)
        try:
            with consumer:
                for i in limit and range(limit) or count():
                    try:
                        await self.connection.drain_events(timeout=timeout)
                    except socket.timeout:
                        break
                return responses
        finally:
            await chan.after_reply_message_received(queue.name)


class Inspect(SyncInspect):
    async def _request(self, command, **kwargs):
        reply = await self.app.aio_control.broadcast(
            command,
            arguments=kwargs,
            destination=self.destination,
            callback=self.callback,
            connection=self.connection,
            limit=self.limit,
            timeout=self.timeout, reply=True,
            pattern=self.pattern, matcher=self.matcher,
        )
        return self._prepare(reply)


class Control(SyncControl):
    Mailbox = Mailbox

    def __init__(self, app=None):
        self.app = app
        self.mailbox = self.Mailbox(
            app.conf.control_exchange,
            type='fanout',
            accept=['json'],
            producer_pool=lazy(lambda: self.app.aio_amqp.producer_pool),
            queue_ttl=app.conf.control_queue_ttl,
            reply_queue_ttl=app.conf.control_queue_ttl,
            queue_expires=app.conf.control_queue_expires,
            reply_queue_expires=app.conf.control_queue_expires,
        )
        register_after_fork(self, _after_fork_cleanup_control)

    @cached_property
    def inspect(self):
        return self.app.subclass_with_self(Inspect, reverse='control.inspect')

    async def broadcast(self, command, arguments=None, destination=None,
                  connection=None, reply=False, timeout=1.0, limit=None,
                  callback=None, channel=None, pattern=None, matcher=None,
                  **extra_kwargs):
        async with self.app.aio_connection_or_acquire(connection) as conn:
            arguments = dict(arguments or {}, **extra_kwargs)
            if pattern and matcher:
                # tests pass easier without requiring pattern/matcher to
                # always be sent in
                return await self.mailbox(conn)._broadcast(
                    command, arguments, destination, reply, timeout,
                    limit, callback, channel=channel,
                    pattern=pattern, matcher=matcher,
                )
            else:
                return await self.mailbox(conn)._broadcast(
                    command, arguments, destination, reply, timeout,
                    limit, callback, channel=channel,
                )

    async def election(self, id, topic, action=None, connection=None):
        await self.broadcast(
            'election', connection=connection, destination=None,
            arguments={
                'id': id, 'topic': topic, 'action': action,
            },
        )
