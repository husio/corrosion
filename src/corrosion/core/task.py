# -*- coding: utf-8 -*-

import types

from corrosion.core import calls
from corrosion.tools.log import get_logger

_log = get_logger('task')


class Task(object):
    _id = 0
    id = None
    target = None
    to_send = None
    wait_till = None

    def __init__(self, target):
        Task._id += 1
        self.id = Task._id
        self.target = target
        self.to_send = None
        self._callstack = []

    def run(self):
        while True:
            try:
                result = self.target.send(self.to_send)
                if isinstance(result, calls.SystemCall):
                    # push it to scheduler
                    return result
                if isinstance(result, types.GeneratorType):
                    self._callstack.append(self.target)
                    self.to_send = None
                    self.target = result
                else:
                    if not self._callstack:
                        return
                    self.to_send = result
                    self.target = self._callstack.pop()
            except StopIteration:
                if not self._callstack:
                    # send information to scheduler
                    raise
                self.to_send = None
                self.target = self._callstack.pop()

    def __repr__(self):
        return '<%s #%d>' % (type(self).__name__, self.id)

