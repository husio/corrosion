#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import socket
import threading

from corrosion.core.scheduler import Scheduler
from corrosion.net.socket import Socket


def _get_free_port(port_bottom=None, max_try=100):
    port_bottom = port_bottom or 8000
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for i in range(0, max_try):
        port = port_bottom + i
        try:
            sock.bind(('', port))
            sock.close()
            return port
        except socket.error:
            pass
    raise socket.error

def _line_reader_echo(host, port):
    def _handle_request(client, address):
        total_data = []
        while True:
            data = yield client.recv(256)
            total_data.append(data)
            if data.endswith('\r\n'):
                break
        response = ''.join(total_data)
        yield client.send(response)
        yield client.close()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(10)
    async_sock = Socket(s)
    while True:
        client, address = yield async_sock.accept()
        yield _handle_request(client, address)

class TClient(threading.Thread):
    def __init__(self, scheduler, host, port):
        super(TClient, self).__init__()
        self._tests = []
        self.assertions = []
        self.scheduler = scheduler
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        for test in self._tests:
            test(self)

    def add_test(self, test):
        self._tests.append(test)

    def as_task(self):
        yield
        self.start()

def test_correct_connection():
    def correct_connection(client):
        request = str(time.time()) + '\r\n'
        client.sock.connect((client.host, client.port))
        client.sock.send(request)
        total_data = []
        while True:
            data = client.sock.recv(64)
            total_data.append(data)
            if data.endswith('\r\n'):
                break
        response = ''.joint(total_data)
        client.sock.close()
        client.assertions.append(request == response)
        client.scheduler.stop()

    scheduler = Scheduler()
    port = _get_free_port()
    client = TClient(scheduler, '', port)
    client.add_test(correct_connection)
    scheduler.add(_line_reader_echo('', port))
    scheduler.add(client.as_task())
    scheduler.run()
    client.join()
    assert all(client.assertions)

def test_connection_remote_close():
    port = _get_free_port()
    def connect_and_close_socket(client):
        client.sock.connect((client.host, client.port))
        client.sock.close()
        client.scheduler.stop()
    scheduler = Scheduler()
    client = TClient(scheduler, '', port)
    client.add_test(connect_and_close_socket)
    scheduler.add(_line_reader_echo('', port))
    scheduler.add(client.as_task())
    scheduler.run()
    client.join()
    assert all(client.assertions)


def test_multiple_correct_connections():
    port = _get_free_port()
    def correct_connection(client):
        request = str(time.time()) + '\r\n'
        client.sock.connect((client.host, client.port))
        client.sock.send(request)
        total_data = []
        while True:
            data = client.sock.recv(2048)
            total_data.append(data)
            if data.endswith('\r\n'):
                break
        response = ''.joint(total_data)
        client.sock.close()
        client.assertions.append(request == response)

    scheduler = Scheduler()
    scheduler.add(_line_reader_echo('', port))
    clients = []
    for c_id in range(3):
        client = TClient(scheduler, '', port)
        client.add_test(correct_connection)
        clients.append(client)
        scheduler.add(client.as_task())

    def all_tasks_done():
        yield
        [c.join() for c in clients]

    scheduler.add(all_tasks_done())
    scheduler.run()
    assert all(client.assertions)
