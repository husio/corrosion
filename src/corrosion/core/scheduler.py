# -*- coding: utf-8 -*-

import time
import select
from Queue import Queue


from corrosion.core.task import Task
from corrosion.core.calls import SystemCall


class Scheduler(object):

    def __init__(self):
        self._epoll = select.epoll()
        self._tasks = {}
        self._ready_queue = Queue()
        self._waiting_io = {}
        self._waiting_end = {}

    def add(self, callback):
        task = Task(callback)
        self._tasks[task.id] = task
        self._schedule_task(task)
        return task.id

    def _schedule_task(self, task):
        self._ready_queue.put(task)

    def _schedule_task_wait_io(self, task, fd):
        assert fd not in self._waiting_io
        self._waiting_io[fd] = task
        self._epoll.register(fd, select.EPOLLIN | select.EPOLLOUT)

    def _schedule_task_wait_end(self, task, wait_id):
        if wait_id in self._tasks:
            self._waiting_end.setdefault(wait_id, []).append(task)
            return True
        return False

    def _remove_task(self, task):
        del self._tasks[task.id]
        waiting_tasks = self._waiting_end.pop(task.id, [])
        for task in waiting_tasks:
            self._schedule_task(task)

    def _io_pool(self, timeout=0.1):
        for fd, event in self._epoll.poll(timeout):
            if event in [select.EPOLLPRI, select.EPOLLOUT, select.EPOLLIN]:
                task = self._waiting_io.pop(fd)
                self._schedule_task(task)
                self._epoll.unregister(fd)
            else:
                # TODO
                raise NotImplemented

    def run(self):
        if getattr(self, '__keep_running', False):
            return False
        self.__keep_running = True
        try:
            self._run()
        except KeyboardInterrupt:
            self.stop()

    def _run(self):
        while self.__keep_running:
            while self._ready_queue.empty():
                self._io_pool()
            task = self._ready_queue.get()
            if task.wait_till and task.wait_till > time.time():
                self._schedule_task(task)
                continue
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
                self._remove_task(task)
                if self._ready_queue.empty():
                    self.stop()

    def stop(self):
        self.__keep_running = False
