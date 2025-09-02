from celery.canvas import (
    group as syncgroup,
    Signature,
    GroupResult
)

from celery.patches.kombu.common import abarrier


@Signature.register_type()
class group(syncgroup):
    async def _apply_tasks(
        self, tasks, producer=None, app=None, p=None,
        add_to_parent=None, chord=None,
        args=None, kwargs=None, **options
    ):
        # pylint: disable=redefined-outer-name
        #   XXX chord is also a class in outer scope.
        app = app or self.app
        async with app.aio_producer_or_acquire(producer) as producer:
            for sig, res in tasks:
                await sig.apply_async(
                    producer=producer, add_to_parent=False,
                    chord=sig.options.get('chord') or chord,
                    args=args, kwargs=kwargs,
                    **options)

                # adding callback to result, such that it will gradually
                # fulfill the barrier.
                #
                # Using barrier.add would use result.then, but we need
                # to add the weak argument here to only create a weak
                # reference to the object.
                if p and not p.cancelled and not p.ready:
                    p.size += 1
                    await res.then(p, weak=True)
                yield res

    async def apply_async(
        self, args=None, kwargs=None, add_to_parent=True,
        producer=None, link=None, link_error=None, **options
    ):
        args = args if args else ()
        if link is not None:
            raise TypeError('Cannot add link to group: use a chord')
        if link_error is not None:
            raise TypeError(
                'Cannot add link to group: do that on individual tasks')
        app = self.app
        if app.conf.task_always_eager:
            return self.apply(args, kwargs, **options)
        if not self.tasks:
            return self.freeze()

        options, group_id, root_id = self._freeze_gid(options)
        tasks = self._prepared(self.tasks, [], group_id, root_id, app)
        p = await abarrier()
        results = []
        async for res in self._apply_tasks(
            tasks, producer, app, p,
            args=args, kwargs=kwargs, **options
        ):
            results.append(res)
        result = await self.app.AioGroupResult(group_id, results, ready_barrier=p)
        await p.finalize()

        # - Special case of group(A.s() | group(B.s(), C.s()))
        # That is, group with single item that's a chain but the
        # last task in that chain is a group.
        #
        # We cannot actually support arbitrary GroupResults in chains,
        # but this special case we can.
        if len(result) == 1 and isinstance(result[0], GroupResult):
            result = result[0]

        parent_task = app.current_worker_task
        if add_to_parent and parent_task:
            parent_task.add_trail(result)
        return result
