# -*- coding: utf-8 -*-

from corrosion.tools.log import get_logger

_log = get_logger('debug')


class Queue(object):
    def __init__(self):
        self.queue = []

    def put(self, item):
        _log.debug('put: %s', self)
        self.queue.append(item)

    def get(self):
        _log.debug('get: %s', self)
        return self.queue.pop(0)

    def empty(self):
        _log.debug('empty: %s', self)
        return len(self.queue) == 0

    def __repr__(self):
        return '<%s ~ %s>' % (type(self).__name__, self.queue)
