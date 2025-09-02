__all__ = ('apply_patch', )


def apply_patch():
    from billiard import heap
    from .heap import Arena
    heap.Arena = Arena
