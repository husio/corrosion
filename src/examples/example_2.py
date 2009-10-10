#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Exceptions example
"""

import random

from corrosion.core.scheduler import Scheduler
from corrosion.core import calls



class SimpleError(Exception):
    pass


class BadCall(calls.SystemCall):
    def __init__(self, throw):
        self.throw = throw

    def handle(self):
        if self.throw:
            raise SimpleError('System call exception..')
        else:
            self.scheduler._schedule_task(self.task)
            self.task.to_send = 'done'


def system_call_exception():
    for throw_exp in [False, True, False, True]:
        try:
            result = yield BadCall(throw=throw_exp)
        except SimpleError as e:
            print 'raised exception: %s -> %s' % \
                    (type(e).__name__, ','.join(e.args))
        else:
            print 'result:', result
    yield calls.StopScheduler()


def main():
    scheduler = Scheduler()
    scheduler.add(system_call_exception())
    scheduler.run()

if __name__ == '__main__':
    main()

