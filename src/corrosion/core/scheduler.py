# -*- coding: utf-8 -*-

import select
from Queue import Queue


from corrosion.tools.log import get_logger
from corrosion.core.task import Task
from corrosion.core.calls import SystemCall

_log = get_logger('scheduler')



class Scheduler(object):

    def __init__(self):
        self._epoll = select.epoll()
        self._tasks = {}
        self._ready_queue = Queue()
        self._waiting_read = {}
        self._waiting_write = {}
        self._waiting_end = {}

    def add(self, coro):
        task = Task(coro)
        self._tasks[task.id] = task
        self._schedule_task(task)
        return task.id

    def _schedule_task(self, task):
        self._ready_queue.put(task)

    def _schedule_task_wait_read(self, task, fd):
        assert fd not in self._waiting_read
        self._waiting_read[fd] = task
        self._epoll.register(fd, select.EPOLLIN)

    def _schedule_task_wait_write(self, task, fd):
        assert fd not in self._waiting_write
        self._waiting_write[fd] = task
        self._epoll.register(fd, select.EPOLLOUT)

    def _schedule_task_wait_end(self, task, wait_id):
        if wait_id in self._tasks:
            self._waiting_end.setdefault(wait_id, []).append(task)
            return True
        return False

    def _remove_task(self, task_id):
        del self._tasks[task_id]
        waiting_tasks = self._waiting_end.pop(task_id, [])
        for task in waiting_tasks:
            self._schedule_task(task)

    def _io_poll(self, timeout=1, maxevents=-1):
        events = self._epoll.poll(timeout, maxevents)
        for fd, event in events:
            _log.debug('-' * 20)
            _log.debug('epoll tick:   fd: %d   event: %d', fd, event)
            if event & select.EPOLLIN:
                _log.debug('EPOLLIN')
                task = self._waiting_read.pop(fd)
                self._schedule_task(task)
            elif event & select.EPOLLOUT:
                _log.debug('EPOLLOUT')
                task = self._waiting_write.pop(fd)
                self._schedule_task(task)
            elif event & select.EPOLLERR:
                _log.debug('EPOLLERR')
                _log.warning('EPOLLERR: Error condition happened on the assoc fd')
                self._epoll.unregister(fd)
                self._remove_task[fd]
            elif event & select.EPOLLHUP:
                _log.debug('EPOLLHUP')
                _log.warning('EPOLLHUP: Hang up happened on the assoc fd')
                self._epoll.unregister(fd)
                self._remove_task[fd]
            else:
                _log.error('unknown event: %d', event)
                # TODO
                raise Exception
            self._epoll.unregister(fd)

    def _io_poll_task(self):
        while True:
            if self._ready_queue.empty():
                self._io_poll(1)
            else:
                self._io_poll(0)
            yield

    def run(self):
        if getattr(self, '__keep_running', False):
            return False
        self.__keep_running = True
        try:
            self._run()
        except KeyboardInterrupt:
            self.stop()

    def _run(self):
        # ready sockets schedulation running as task
        self.add(self._io_poll_task())
        while self.__keep_running:
            task = self._ready_queue.get()
            _log.debug('got new task - run %d', task.id)
            try:
                result = task.run()
                if isinstance(result, SystemCall):
                    syscall = result
                    syscall.task = task
                    syscall.scheduler = self
                    syscall.handle()
                else:
                    self._schedule_task(task)
            except StopIteration:
                self._remove_task(task.id)
                if self._ready_queue.empty():
                    self.stop()

    def stop(self):
        self.__keep_running = False
