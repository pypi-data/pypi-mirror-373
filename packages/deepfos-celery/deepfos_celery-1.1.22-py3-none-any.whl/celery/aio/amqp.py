from kombu import Exchange
from kombu.common import Broadcast
from kombu.utils import cached_property

from celery.app.amqp import AMQP, Queues
from celery.patches.kombu import pools
from celery.patches.kombu.connection import Connection
from celery.patches.kombu.messaging import Producer
from celery.patches.kombu.entity import Queue
from celery import signals


class AioQueues(Queues):
    queue_cls = Queue


class AioAMQP(AMQP):
    Producer = Producer
    Connection = Connection
    queues_cls = AioQueues

    @property
    def producer_pool(self):
        if self._producer_pool is None:
            self._producer_pool = pools.producers[
                self.app.aconnection_for_write()]
            self._producer_pool.limit = self.app.pool.limit
        return self._producer_pool

    def _create_task_sender(self):
        default_retry = self.app.conf.task_publish_retry
        default_policy = self.app.conf.task_publish_retry_policy
        default_delivery_mode = self.app.conf.task_default_delivery_mode
        default_queue = self.default_queue
        queues = self.queues
        send_before_publish = signals.before_task_publish.asend
        before_receivers = signals.before_task_publish.areceivers
        send_after_publish = signals.after_task_publish.asend
        after_receivers = signals.after_task_publish.areceivers

        send_task_sent = signals.task_sent.asend   # XXX compat
        sent_receivers = signals.task_sent.areceivers

        default_evd = self._event_dispatcher
        default_exchange = self.default_exchange

        default_rkey = self.app.conf.task_default_routing_key
        default_serializer = self.app.conf.task_serializer
        default_compressor = self.app.conf.result_compression

        async def send_task_message(
            producer, name, message,
            exchange=None, routing_key=None, queue=None,
            event_dispatcher=None,
            retry=None, retry_policy=None,
            serializer=None, delivery_mode=None,
            compression=None, declare=None,
            headers=None, exchange_type=None, **kwargs
        ):
            retry = default_retry if retry is None else retry
            headers2, properties, body, sent_event = message
            if headers:
                headers2.update(headers)
            if kwargs:
                properties.update(kwargs)

            qname = queue
            if queue is None and exchange is None:
                queue = default_queue
            if queue is not None:
                if isinstance(queue, str):
                    qname, queue = queue, queues[queue]
                else:
                    qname = queue.name

            if delivery_mode is None:
                try:
                    delivery_mode = queue.exchange.delivery_mode
                except AttributeError:
                    pass
                delivery_mode = delivery_mode or default_delivery_mode

            if exchange_type is None:
                try:
                    exchange_type = queue.exchange.type
                except AttributeError:
                    exchange_type = 'direct'

            # convert to anon-exchange, when exchange not set and direct ex.
            if (not exchange or not routing_key) and exchange_type == 'direct':
                exchange, routing_key = '', qname
            elif exchange is None:
                # not topic exchange, and exchange not undefined
                exchange = queue.exchange.name or default_exchange
                routing_key = routing_key or queue.routing_key or default_rkey
            if declare is None and queue and not isinstance(queue, Broadcast):
                declare = [queue]

            # merge default and custom policy
            retry = default_retry if retry is None else retry
            _rp = (dict(default_policy, **retry_policy) if retry_policy
                   else default_policy)

            if before_receivers:
                await send_before_publish(
                    sender=name, body=body,
                    exchange=exchange, routing_key=routing_key,
                    declare=declare, headers=headers2,
                    properties=properties, retry_policy=retry_policy,
                )
            ret = await producer.publish(
                body,
                exchange=exchange,
                routing_key=routing_key,
                serializer=serializer or default_serializer,
                compression=compression or default_compressor,
                retry=retry, retry_policy=_rp,
                delivery_mode=delivery_mode, declare=declare,
                headers=headers2,
                **properties
            )
            if after_receivers:
                await send_after_publish(
                    sender=name, body=body, headers=headers2,
                    exchange=exchange, routing_key=routing_key
                )
            if sent_receivers:  # XXX deprecated
                if isinstance(body, tuple):  # protocol version 2
                    await send_task_sent(
                        sender=name, task_id=headers2['id'], task=name,
                        args=body[0], kwargs=body[1],
                        eta=headers2['eta'], taskset=headers2['group'],
                    )
                else:  # protocol version 1
                    await send_task_sent(
                        sender=name, task_id=body['id'], task=name,
                        args=body['args'], kwargs=body['kwargs'],
                        eta=body['eta'], taskset=body['taskset'],
                    )
            if sent_event:
                evd = event_dispatcher or default_evd
                exname = exchange
                if isinstance(exname, Exchange):
                    exname = exname.name
                sent_event.update({
                    'queue': qname,
                    'exchange': exname,
                    'routing_key': routing_key,
                })
                await evd.publish('task-sent', sent_event,
                            producer, retry=retry, retry_policy=retry_policy)
            return ret
        return send_task_message

    @cached_property
    def _event_dispatcher(self):
        return self.app.aio_events.Dispatcher(enabled=False)
