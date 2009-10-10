# -*- coding: utf-8 -*-

import types

from corrosion.core import calls



class Task(object):
    __id = 0
    to_send = None
    result = None

    def __init__(self, target):
        Task._Task__id += 1
        self.id = Task._Task__id
        self.target = target
        self._callstack = []

    def run(self):
        try:
            if isinstance(self.to_send, Exception):
                result = self.target.throw(self.to_send)
            else:
                result = self.target.send(self.to_send)
            self.result = result
            if isinstance(result, calls.SystemCall):
                # push it to scheduler
                return result
            elif isinstance(result, types.GeneratorType):
                # act like trampoline
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

