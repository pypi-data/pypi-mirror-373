from collections import deque

from kombu.common import (
    _ensure_channel_is_bound,
    ChannelError,
    RecoverableConnectionError,
)
from vine import promise, Thenable, barrier


async def maybe_declare(entity, channel=None, retry=False, **retry_policy):
    """Declare entity (cached)."""
    if retry:
        return await _imaybe_declare(entity, channel, **retry_policy)
    return await _maybe_declare(entity, channel)


async def _maybe_declare(entity, channel):
    # _maybe_declare sets name on original for autogen queues
    orig = entity

    _ensure_channel_is_bound(entity, channel)

    if channel is None:
        if not entity.is_bound:
            raise ChannelError(
                f"channel is None and entity {entity} not bound.")
        channel = entity.channel

    declared = ident = None
    if channel.connection and entity.can_cache_declaration:
        declared = channel.connection.client.declared_entities
        ident = hash(entity)
        if ident in declared:
            return False

    if not channel.connection:
        raise RecoverableConnectionError('channel disconnected')
    await entity.declare(channel=channel)
    if declared is not None and ident:
        declared.add(ident)
    if orig is not None:
        orig.name = entity.name
    return True


async def _imaybe_declare(entity, channel, **retry_policy):
    _ensure_channel_is_bound(entity, channel)

    if not entity.channel.connection:
        raise RecoverableConnectionError('channel disconnected')

    return await entity.channel.connection.client.ensure(
        entity, _maybe_declare, **retry_policy)(entity, channel)


@Thenable.register
class apromise(promise):
    def __init__(self, fun=None, args=None, kwargs=None,
                 callback=None, on_error=None, weak=False,
                 ignore_result=False):
        super().__init__(
            fun=fun, args=args, kwargs=kwargs,
            callback=None, on_error=on_error,
            weak=weak, ignore_result=ignore_result
        )

        if callback is not None:
            self._wrap_callback(callback)

    async def then(self, callback, on_error=None):
        if not isinstance(callback, Thenable):
            callback = apromise(callback, on_error=on_error)
        if self.cancelled:
            callback.cancel()
            return callback
        if self.failed:
            callback.throw(self.reason)
        elif self.ready:
            args, kwargs = self.value
            await callback(*args, **kwargs)
        return self._wrap_callback(callback)

    def _wrap_callback(self, callback, on_error=None):
        if not isinstance(callback, Thenable):
            callback = apromise(callback, on_error=on_error)
        if self._lvpending is None:
            svpending = self._svpending
            if svpending is not None:
                self._svpending, self._lvpending = None, deque([svpending])
            else:
                self._svpending = callback
                return callback
        self._lvpending.append(callback)
        return callback

    async def __call__(self, *args, **kwargs):
        retval = None
        if self.cancelled:
            return
        final_args = self.args + args if args else self.args
        final_kwargs = dict(self.kwargs, **kwargs) if kwargs else self.kwargs
        # self.fun may be a weakref
        fun = self._fun_is_alive(self.fun)
        if fun is not None:
            try:
                if self.ignore_result:
                    await fun(*final_args, **final_kwargs)
                    ca = ()
                    ck = {}
                else:
                    retval = await fun(*final_args, **final_kwargs)
                    self.value = (ca, ck) = (retval,), {}
            except Exception:
                return self.throw()
        else:
            self.value = (ca, ck) = final_args, final_kwargs
        self.ready = True
        svpending = self._svpending
        if svpending is not None:
            try:
                await svpending(*ca, **ck)
            finally:
                self._svpending = None
        else:
            lvpending = self._lvpending
            try:
                while lvpending:
                    p = lvpending.popleft()
                    await p(*ca, **ck)
            finally:
                self._lvpending = None
        return retval


@Thenable.register
class abarrier(barrier):
    def __init__(self, promises=None, args=None, kwargs=None,
                 callback=None, size=None):
        self.p = apromise()
        self.args = args or ()
        self.kwargs = kwargs or {}
        self._value = 0
        self.size = size or 0
        if not self.size and promises:
            # iter(l) calls len(l) so generator wrappers
            # can only return NotImplemented in the case the
            # generator is not fully consumed yet.
            plen = promises.__len__()
            if plen is not NotImplemented:
                self.size = plen
        self.ready = self.failed = False
        self.reason = None
        self.cancelled = False
        self.finalized = False

        self._promises = promises
        self._callback = callback
        self.finalized = False

    async def _init_cb_and_promises(self):
        promises = self._promises
        [await self.add_noincr(p) for p in promises or []]
        self.finalized = bool(promises or self.size)
        if self._callback:
            await self.then(self._callback)
        return self

    def __await__(self):
        return self._init_cb_and_promises().__await__()

    async def __call__(self, *args, **kwargs):
        if not self.ready and not self.cancelled:
            self._value += 1
            if self.finalized and self._value >= self.size:
                self.ready = True
                await self.p(*self.args, **self.kwargs)

    async def then(self, callback, errback=None):
        await self.p.then(callback, errback)

    async def finalize(self):
        if not self.finalized and self._value >= self.size:
            await self.p(*self.args, **self.kwargs)
        self.finalized = True

    async def add_noincr(self, p):
        if not self.cancelled:
            if self.ready:
                raise ValueError('Cannot add promise to full barrier')
            await p.then(self)

    async def add(self, p):
        if not self.cancelled:
            await self.add_noincr(p)
            self.size += 1
