from typing import *
from kombu.pools import (
    PoolGroup,
    connections,
    register_group,
    use_global_limit,
)

from .messaging import Producer
from .utils import Resource, async_lazy


class AioProducerPool(Resource):
    Producer = Producer
    close_after_fork = True

    if TYPE_CHECKING:
        from .connection import ConnectionPool
        connections: ConnectionPool

    def __init__(self, connections, *args, **kwargs):
        self.connections = connections
        self.Producer = kwargs.pop('Producer', None) or self.Producer
        super().__init__(*args, **kwargs)

    async def _acquire_connection(self):
        return await self.connections.get(block=True)

    async def create_producer(self):
        conn = await self._acquire_connection()
        try:
            return self.Producer(conn)
        except BaseException:
            await conn.release()
            raise

    def new(self):
        return async_lazy(self.create_producer)

    def setup(self):
        if self.limit:
            for _ in range(self.limit):
                self._resource.put_nowait(self.new())

    async def close_resource(self, resource):
        pass

    async def prepare(self, p):
        if isinstance(p, async_lazy):
            p = await p()
        if p._channel is None:
            conn = await self._acquire_connection()
            try:
                p.revive(conn)
            except BaseException:
                await conn.release()
                raise
        return p

    async def release(self, resource):
        if resource.__connection__:
            await resource.__connection__.release()
        resource.channel = None
        await super().release(resource)


class Producers(PoolGroup):
    def create(self, connection, limit):
        return AioProducerPool(connections[connection], limit=limit)


producers = register_group(Producers(limit=use_global_limit))
