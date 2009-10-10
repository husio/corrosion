# -*- coding: utf-8 -*-

import socket

from corrosion.tools import log
from corrosion.core import calls

_log = log.get_logger('sock')


class Socket(object):
    def __init__(self, sock):
        self.sock = sock
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.sock.setblocking(0)

    def accept(self):
        yield calls.WaitRead(self.sock)
        print 'socket ready do acccept'
        conn, addr = self.sock.accept()
        print 'accepted, waiting for data & blocking other dudes..'
        yield (Socket(conn), addr)

    def send(self, buff):
        while buff:
            yield calls.WaitWrite(self.sock)
            out_len = self.sock.send(buff)
            buff = buff[out_len:]

    def recv(self, max_bytes):
        _log.debug('waiting for socket to read')
        yield calls.WaitRead(self.sock)
        _log.debug('reading from socket')
        yield self.sock.recv(max_bytes)

    def close(self):
        yield self.sock.close()

    def __getattr__(self, name):
        return getattr(self.sock, name)

    def __del__(self):
        self.close()
