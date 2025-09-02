from typing import *

from kombu.entity import (
    Queue as SyncQueue,
    Exchange,
    prepare_accept_content
)
from kombu.exceptions import NotBoundError
from kombu.utils.functional import ChannelPromise


class Queue(SyncQueue):
    if TYPE_CHECKING:
        binding_arguments = None
        no_declare: bool

    @property
    def channel(self):
        """Current channel if the object is bound."""
        channel = self._channel
        if channel is None:
            raise NotBoundError(
                "Can't call method on {} not bound to a channel".format(
                    type(self).__name__))
        if isinstance(channel, ChannelPromise):
            channel = self._channel = channel()
        return channel

    async def queue_bind(self, nowait=False, channel=None):
        return await self.bind_to(
            self.exchange, self.routing_key, self.binding_arguments,
            channel=channel, nowait=nowait)

    async def bind_to(self, exchange='', routing_key='',
            arguments=None, nowait=False, channel=None):
        if isinstance(exchange, Exchange):
            exchange = exchange.name

        return await (channel or self.channel).queue_bind(
            queue=self.name,
            exchange=exchange,
            routing_key=routing_key,
            arguments=arguments,
            nowait=nowait,
        )

    async def declare(self, nowait=False, channel=None):
        if not self.no_declare:
            # - declare main binding.
            self._create_exchange(nowait=nowait, channel=channel)
            await self._create_queue(nowait=nowait, channel=channel)
            self._create_bindings(nowait=nowait, channel=channel)
        return self.name

    async def _create_queue(self, nowait=False, channel=None):
        await self.queue_declare(nowait=nowait, passive=False, channel=channel)
        if self.exchange and self.exchange.name:
            await self.queue_bind(nowait=nowait, channel=channel)

    async def get(self, no_ack=None, accept=None):
        """Poll the server for a new message.

        This method provides direct access to the messages in a
        queue using a synchronous dialogue, designed for
        specific types of applications where synchronous functionality
        is more important than performance.

        Returns:
            ~kombu.Message: if a message was available,
                or :const:`None` otherwise.

        Arguments:
            no_ack (bool): If enabled the broker will
                automatically ack messages.
            accept (Set[str]): Custom list of accepted content types.
        """
        no_ack = self.no_ack if no_ack is None else no_ack
        message = await self.channel.basic_get(queue=self.name, no_ack=no_ack)
        if message is not None:
            m2p = getattr(self.channel, 'message_to_python', None)
            if m2p:
                message = m2p(message)
            if message.errors:
                message._reraise_error()
            message.accept = prepare_accept_content(accept)
        return message

    async def queue_declare(self, nowait=False, passive=False, channel=None):
        """Declare queue on the server.

        Arguments:
            nowait (bool): Do not wait for a reply.
            passive (bool): If set, the server will not create the queue.
                The client can use this to check whether a queue exists
                without modifying the server state.
        """
        channel = channel or self.channel
        queue_arguments = channel.prepare_queue_arguments(
            self.queue_arguments or {},
            expires=self.expires,
            message_ttl=self.message_ttl,
            max_length=self.max_length,
            max_length_bytes=self.max_length_bytes,
            max_priority=self.max_priority,
        )
        ret = await channel.queue_declare(
            queue=self.name,
            passive=passive,
            durable=self.durable,
            exclusive=self.exclusive,
            auto_delete=self.auto_delete,
            arguments=queue_arguments,
            nowait=nowait,
        )
        if not self.name:
            self.name = ret[0]
        if self.on_declared:
            self.on_declared(*ret)
        return ret
