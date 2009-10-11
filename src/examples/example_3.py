#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Subtask example
"""

import time

from corrosion.core.scheduler import Scheduler
from corrosion.core import calls


class SimpleError(Exception):
    pass

def micro_task(throw, msg_format):
    self_id = yield calls.GetSelfId()
    if throw:
        raise SimpleError('new error: %d' % self_id)
    yield msg_format % (self_id, time.time())

def worker():
    for i in range(7):
        throw = i % 2
        mt = micro_task(throw, '(%d) current time: %d')
        mt_id = yield calls.NewTask(mt)
        print 'waiting for micro task end'
        try:
            result = yield calls.WaitEnd(mt_id)
        except SimpleError as e:
            result = '%s: %s' % (type(e).__name__, ','.join(e.args))
        print 'micro task is done with result:', result
    yield calls.StopScheduler()


def main():
    scheduler = Scheduler()
    scheduler.add(worker())
    scheduler.run()

if __name__ == '__main__':
    main()

