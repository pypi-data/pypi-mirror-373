__all__ = ('apply_patch', )


def apply_patch():
    from .redis import PatchedMultiChannelPoller
    from kombu import transport
    from kombu.transport import redis

    redis.MultiChannelPoller = PatchedMultiChannelPoller
    transport.TRANSPORT_ALIASES.update({
      'redis-cluster': 'celery.patches.kombu.redis_cluster:Transport',
      'redis': 'celery.patches.kombu.redis:PatchedTransport',
    })
