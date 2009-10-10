# -*- coding: utf-8 -*-

import socket

from corrosion.core import calls



class Socket(object):
    def __init__(self, raw_socket):
        self.sock = raw_socket
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    def accept(self):
        yield calls.WaitRead(self.sock)
        conn, addr = self.sock.accept()
        self.sock.setblocking(0)
        yield (Socket(conn), addr)

    def send(self, buff):
        while buff:
            yield calls.WaitWrite(self.sock)
            try:
                out_len = self.sock.send(buff)
            except socket.error:
                yield socket.error
            buff = buff[out_len:]

    def recv(self, max_bytes):
        yield calls.WaitRead(self.sock)
        yield self.sock.recv(max_bytes)

    def __getattr__(self, name):
        return getattr(self.sock, name)
