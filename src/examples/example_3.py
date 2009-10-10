#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Subtask example
"""

import time

from corrosion.core.scheduler import Scheduler
from corrosion.core import calls



def worker():
    def mikro_task(msg_format):
        yield msg_format % time.time()

    for _ignore in range(3):
        micro_id = yield calls.NewTask(mikro_task('current time: %d'))
        print 'waiting for micro task end'
        result = yield calls.WaitEnd(micro_id)
        print 'micro task is done with result:', result
        yield
    yield calls.StopScheduler()


def main():
    scheduler = Scheduler()
    scheduler.add(worker())
    scheduler.run()

if __name__ == '__main__':
    main()

