# -*- coding: utf-8 -*-

import socket

from corrosion.core import calls


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
        yield calls.WaitRead(self.sock)
        yield self.sock.recv(max_bytes)

    def close(self):
        yield self.sock.close()

    def bind(self, addr):
        self.sock.bind(addr)

    def listen(self, n=None):
        self.sock.listen(n)

    def __del__(self):
        self.close()
