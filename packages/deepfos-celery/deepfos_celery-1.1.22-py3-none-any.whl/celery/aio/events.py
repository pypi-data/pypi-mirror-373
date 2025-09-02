from celery.app.events import Events as SyncEvents


class Events(SyncEvents):
    dispatcher_cls = 'celery.aio.dispatcher:EventDispatcher'
