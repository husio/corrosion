# -*- coding: utf-8 -*-

import time
import datetime


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


class WaitTime(Wait):
    def __init__(self, t):
        if isinstance(t, datetime.datetime):
            t = time.mktime(t.timetuple())
        if isinstance(t, datetime.timedelta):
            dt = datetime.datetime.now() + t
            t = time.mktime(dt.timetuple())
        self.wait_till = t

    def handle(self):
        self.task.wait_till = self.wait_till
        self.to_send = self.task.wait_till
        self.scheduler._schedule_task(self.task)


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
        fd = self.file_like.fileno()
        self.scheduler._schedule_task_wait_read(self.task, fd)


class WaitWrite(Wait):
    def __init__(self, file_like):
        self.file_like = file_like

    def handle(self):
        fd = self.file_like.fileno()
        self.scheduler._schedule_task_wait_write(self.task, fd)
