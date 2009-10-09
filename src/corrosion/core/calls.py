# -*- coding: utf-8 -*-

from corrosion.tools.log import get_logger

_log = get_logger('calls')


class SystemCall(object):
    task = None
    scheduler = None

    def handle(self):
        raise NotImplemented

    def __repr__(self):
        return '<%s from #%d>' % (type(self).__name__, self.task.id)


class GetSelfId(SystemCall):
    def handle(self):
        self.task.to_send = self.task.id
        self.scheduler._schedule_task(self.task)


class SubCall(SystemCall):
    def __init__(self, target):
        self.target = target

    def handle(self):
        task_id = self.scheduler.add(self.target)
        self.task.to_send = task_id
        self.scheduler._schedule_task(self.task)


class Wait(SystemCall):
    pass


class WaitEnd(Wait):
    def __init__(self, task_id):
        super(WaitEnd, self).__init__()
        self.task_id = task_id

    def handle(self):
        result = self.scheduler._schedule_task_wait_end(self.task, self.task_id)
        self.task.to_send = result
        if not result:
            self.scheduler._schedule_task(self.task)


class WaitRead(Wait):
    def __init__(self, file_like):
        self.file_like = file_like

    def handle(self):
        _log.debug('%6s: %s %s',
                type(self).__name__, self.task, self.task.target)
        fd = self.file_like.fileno()
        self.scheduler._schedule_task_wait_read(self.task, fd)


class WaitWrite(Wait):
    def __init__(self, file_like):
        self.file_like = file_like

    def handle(self):
        fd = self.file_like.fileno()
        self.scheduler._schedule_task_wait_write(self.task, fd)
