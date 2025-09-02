import asyncio
import os
import time

from collections import deque, defaultdict
from copy import copy

from celery.events.dispatcher import (
    EventDispatcher as SyncEventDispatcher,
    Event,
    app_or_default,
    anon_nodename,
    utcoffset,
    group_from,
)
from celery.events.event import EVENT_EXCHANGE_NAME
from celery.patches.kombu.messaging import Producer
from celery.patches.kombu.exchange import Exchange


event_exchange = Exchange(EVENT_EXCHANGE_NAME, type='topic')


def get_exchange(conn, name=EVENT_EXCHANGE_NAME):
    """Get exchange used for sending events.

    Arguments:
        conn (kombu.Connection): Connection used for sending/receiving events.
        name (str): Name of the exchange. Default is ``celeryev``.

    Note:
        The event type changes if Redis is used as the transport
        (from topic -> fanout).
    """
    ex = copy(event_exchange)
    if conn.transport.driver_type == 'redis':
        # quick hack for Issue #436
        ex.type = 'fanout'
    if name != ex.name:
        ex.name = name
    return ex


class EventDispatcher(SyncEventDispatcher):
    def __init__(self, connection=None, hostname=None, enabled=True,
                 channel=None, buffer_while_offline=True, app=None,
                 serializer=None, groups=None, delivery_mode=1,
                 buffer_group=None, buffer_limit=24, on_send_buffered=None):
        self.app = app_or_default(app or self.app)
        self.connection = connection
        self.channel = channel
        self.hostname = hostname or anon_nodename()
        self.buffer_while_offline = buffer_while_offline
        self.buffer_group = buffer_group or frozenset()
        self.buffer_limit = buffer_limit
        self.on_send_buffered = on_send_buffered
        self._group_buffer = defaultdict(list)
        self.mutex = asyncio.Lock()
        self.producer = None
        self._outbound_buffer = deque()
        self.serializer = serializer or self.app.conf.event_serializer
        self.on_enabled = set()
        self.on_disabled = set()
        self.groups = set(groups or [])
        self.tzoffset = [-time.timezone, -time.altzone]
        self.clock = self.app.clock
        self.delivery_mode = delivery_mode
        if not connection and channel:
            self.connection = channel.connection.client
        self.enabled = enabled
        conninfo = self.connection or self.app.aconnection_for_write()
        self.exchange = get_exchange(conninfo,
                                     name=self.app.conf.event_exchange)
        if conninfo.transport.driver_type in self.DISABLED_TRANSPORTS:
            self.enabled = False
        if self.enabled:
            self.enable()
        self.headers = {'hostname': self.hostname}
        self.pid = os.getpid()

    def enable(self):
        self.producer = Producer(self.channel or self.connection,
                                 exchange=self.exchange,
                                 serializer=self.serializer,
                                 auto_declare=False)
        self.enabled = True
        for callback in self.on_enabled:
            callback()

    async def publish(self, type, fields, producer,
                blind=False, Event=Event, **kwargs):
        clock = None if blind else self.clock.forward()
        event = Event(type, hostname=self.hostname, utcoffset=utcoffset(),
                      pid=self.pid, clock=clock, **fields)
        async with self.mutex:
            return await self._publish(
                event, producer,
                routing_key=type.replace('-', '.'),
                **kwargs
            )

    async def _publish(
        self, event, producer, routing_key, retry=False,
        retry_policy=None, utcoffset=utcoffset
    ):
        exchange = self.exchange
        try:
            await producer.publish(
                event,
                routing_key=routing_key,
                exchange=exchange.name,
                retry=retry,
                retry_policy=retry_policy,
                declare=[exchange],
                serializer=self.serializer,
                headers=self.headers,
                delivery_mode=self.delivery_mode,
            )
        except Exception as exc:  # pylint: disable=broad-except
            if not self.buffer_while_offline:
                raise
            self._outbound_buffer.append((event, routing_key, exc))


    async def send(self, type, blind=False, utcoffset=utcoffset, retry=False,
             retry_policy=None, Event=Event, **fields):
        if self.enabled:
            groups, group = self.groups, group_from(type)
            if groups and group not in groups:
                return
            if group in self.buffer_group:
                clock = self.clock.forward()
                event = Event(type, hostname=self.hostname,
                              utcoffset=utcoffset(),
                              pid=self.pid, clock=clock, **fields)
                buf = self._group_buffer[group]
                buf.append(event)
                if len(buf) >= self.buffer_limit:
                    await self.flush()
                elif self.on_send_buffered:
                    self.on_send_buffered()
            else:
                return await self.publish(
                    type, fields, self.producer,
                    blind=blind, Event=Event, retry=retry,
                    retry_policy=retry_policy)

    async def flush(self, errors=True, groups=True):
        if errors:
            buf = list(self._outbound_buffer)
            try:
                async with self.mutex:
                    for event, routing_key, _ in buf:
                        await self._publish(event, self.producer, routing_key)
            finally:
                self._outbound_buffer.clear()
        if groups:
            async with self.mutex:
                for group, events in self._group_buffer.items():
                    await self._publish(
                        events, self.producer, '%s.multi' % group)
                    events[:] = []  # list.clear
