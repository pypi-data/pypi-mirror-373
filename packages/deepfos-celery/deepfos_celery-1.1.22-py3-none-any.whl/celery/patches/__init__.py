

def apply_patches():
    from . import kombu
    from . import redis
    from . import billiard

    kombu.apply_patch()
    redis.apply_patch()
    billiard.apply_patch()
