from kombu import serialization
from kombu.utils.uuid import uuid

from celery.app.task import Task
from celery.result import denied_join_result


class AioTask(Task):
    def AsyncResult(self, task_id, **kwargs):
        """Get AsyncResult instance for the specified task.

        Arguments:
            task_id (str): Task id to get result for.
        """
        return self._get_app().AioAsyncResult(task_id, backend=self.backend,
                                           task_name=self.name, **kwargs)

    @property
    def backend(self):
        backend = self._backend
        if backend is None:
            return self.app.aio_backend
        return backend

    @backend.setter
    def backend(self, value):  # noqa
        self._backend = value

    async def apply_async(
        self,
        args=None, kwargs=None, task_id=None, producer=None,
        link=None, link_error=None, shadow=None,
        **options
    ):
        if self.typing:
            try:
                check_arguments = self.__header__
            except AttributeError:  # pragma: no cover
                pass
            else:
                check_arguments(*(args or ()), **(kwargs or {}))

        if self.__v2_compat__:
            shadow = shadow or self.shadow_name(self(), args, kwargs, options)
        else:
            shadow = shadow or self.shadow_name(args, kwargs, options)

        preopts = self._get_exec_options()
        options = dict(preopts, **options) if options else preopts

        options.setdefault('ignore_result', self.ignore_result)
        if self.priority:
            options.setdefault('priority', self.priority)

        app = self._get_app()
        if app.conf.task_always_eager:
            with app.producer_or_acquire(producer) as eager_producer:
                serializer = options.get('serializer')
                if serializer is None:
                    if eager_producer.serializer:
                        serializer = eager_producer.serializer
                    else:
                        serializer = app.conf.task_serializer
                body = args, kwargs
                content_type, content_encoding, data = serialization.dumps(
                    body, serializer,
                )
                args, kwargs = serialization.loads(
                    data, content_type, content_encoding,
                    accept=[content_type]
                )
            with denied_join_result():
                return self.apply(
                    args, kwargs, task_id=task_id or uuid(),
                    link=link, link_error=link_error, **options
                )
        else:
            return await app.asend_task(
                self.name, args, kwargs, task_id=task_id, producer=producer,
                link=link, link_error=link_error, result_cls=self.AsyncResult,
                shadow=shadow, task_type=self,
                **options
            )

