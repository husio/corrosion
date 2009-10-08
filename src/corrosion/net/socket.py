# -*- coding: utf-8 -*-

from corrosion.core import calls


class Socket(object):
    def __init__(self, socket):
        self.socket = socket

    def accept(self):
        yield calls.WaitRead(self.socket)
        (client, address) = self.socket.accept()
        yield (Socket(client), address)

    def send(self, buff):
        while buff:
            yield calls.WaitWrite(self.socket)
            out_len = self.socket.send(buff)
            buff = buff[out_len:]

    def recv(self, max_bytes):
        yield calls.WaitRead(self.socket)
        yield self.socket.recv(max_bytes)

    def close(self):
        yield self.socket.close()

    def __del__(self):
        self.close()
