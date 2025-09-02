from typing import *

from kombu.transport.virtual.exchange import (
    ExchangeType as SyncExchangeType,
    DirectExchange as SyncDirectExchange,
    TopicExchange as SyncTopicExchange,
    FanoutExchange as SyncFanoutExchange
)
from kombu.entity import (
    Exchange as SyncExchange,
)


class ExchangeType(SyncExchangeType):
    if TYPE_CHECKING:
        from .redis import Channel
        channel: Channel

    async def deliver(self, message, exchange, routing_key, **kwargs):
        raise NotImplementedError('subclass responsibility')


class DirectExchange(ExchangeType, SyncDirectExchange):
    async def deliver(self, message, exchange, routing_key, **kwargs):
        _lookup = self.channel._lookup
        _put = self.channel._put
        for queue in (await _lookup(exchange, routing_key)):
            await _put(queue, message, **kwargs)


class TopicExchange(ExchangeType, SyncTopicExchange):
    async def deliver(self, message, exchange, routing_key, **kwargs):
        _lookup = self.channel._lookup
        _put = self.channel._put
        deadletter = self.channel.deadletter_queue
        queues = (
            q for q in (await _lookup(exchange, routing_key))
            if q and q != deadletter
        )
        for queue in queues:
            await _put(queue, message, **kwargs)


class FanoutExchange(ExchangeType, SyncFanoutExchange):
    async def deliver(self, message, exchange, routing_key, **kwargs):
        if self.channel.supports_fanout:
            await self.channel._put_fanout(
                exchange, message, routing_key, **kwargs)


STANDARD_EXCHANGE_TYPES = {
    'direct': DirectExchange,
    'topic': TopicExchange,
    'fanout': FanoutExchange,
}


class Exchange(SyncExchange):
    if TYPE_CHECKING:
        from .redis import Channel
        @property
        def channel(self) -> Channel: ...

    async def declare(self, nowait=False, passive=None, channel=None):
        return super().declare(nowait, passive, channel)

    async def publish(self, message, routing_key=None, mandatory=False,
                immediate=False, exchange=None):
        if isinstance(message, str):
            message = self.Message(message)
        exchange = exchange or self.name
        return await self.channel.basic_publish(
            message,
            exchange=exchange,
            routing_key=routing_key,
            mandatory=mandatory,
            immediate=immediate,
        )

    async def delete(self, if_unused=False, nowait=False):
        return await self.channel.exchange_delete(
            exchange=self.name, if_unused=if_unused, nowait=nowait)
