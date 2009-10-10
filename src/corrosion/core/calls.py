# -*- coding: utf-8 -*-



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


class NewTask(SystemCall):
    def __init__(self, target):
        self.target = target

    def handle(self):
        task_id = self.scheduler.add(self.target)
        self.task.to_send = task_id
        self.scheduler._schedule_task(self.task)


class Schedule(SystemCall):
    def __init__(self, task_id):
        self.task_id = task_id

    def handle(self):
        task = self.scheduler._tasks[self.task_id]
        self.scheduler._schedule_task(task)
        self.task.to_send = True


class StopScheduler(SystemCall):
    def handle(self):
        self.scheduler.stop()


class Wait(SystemCall):
    pass


class WaitEnd(Wait):
    """Wait for task end and send it's return value to current task. If task
    with given id is not scheduled, returns `None`.
    """
    def __init__(self, task_id):
        super(WaitEnd, self).__init__()
        self.task_id = task_id

    def handle(self):
        result = self.scheduler._schedule_task_wait_end(self.task, self.task_id)
        if not result:
            self.task.to_send = None
            self.scheduler._schedule_task(self.task)
        else:
            subtask = self.scheduler._tasks[self.task_id]
            subtask.parent = self.task


class Worker(Wait):
    """Create new task, schedule it, wait for the result and spawn base taks
    with the result of the first one.
    """
    def __init__(self, task_gen, data):
        # initialize generator
        task_gen.next()
        self.task_gen = task_gen
        self.task_gen_data = data

    def handle(self):
        task_gen_id = self.scheduler.add(self.task_gen)
        task_gen = self.scheduler._tasks[task_gen_id]
        task_gen.to_send = self.task_gen_data
        if not self.scheduler._schedule_task_wait_end(self.task, task_gen_id):
            # fail at scheduling.. add base task to query
            self.scheduler._schedule_task(self.task)
        else:
            task_gen.parent = self.task


class WaitRead(Wait):
    """Wait for file like object till it will be ready for reading"""
    def __init__(self, file_like):
        self.file_like = file_like

    def handle(self):
        fd = self.file_like.fileno()
        self.scheduler._schedule_task_wait_read(self.task, fd)


class WaitWrite(Wait):
    """Wait for file like object till it will be ready for writing"""
    def __init__(self, file_like):
        self.file_like = file_like

    def handle(self):
        fd = self.file_like.fileno()
        self.scheduler._schedule_task_wait_write(self.task, fd)
