#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import socket
import threading
import unittest

from corrosion.core.scheduler import Scheduler
from corrosion.net.socket import Socket



def _get_free_port(port_bottom=None, max_try=100):
    port_bottom = port_bottom or 8000
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for i in range(0, max_try):
        port = port_bottom + i





class TestCaseWithLineReader(unittest.TestCase):

    SAFE_CONN_WAIT = 0.2
    REQUEST = 'echo message\r\n'
    RESPONSE_PREFIX = 'ECHO;'

    def setUp(self):
        self.host = ''
        self.port = self._get_free_port()
        self.test_case_clean = True

    def _wait_till_clean(self):
        while not self.test_case_clean:
            time.sleep(self.SAFE_CONN_WAIT)

    def _line_reader_echo(self):
        def _handle_request(client, address):
            total_data = []
            while True:
                data = yield client.recv(1024)
                total_data.append(data)
                if data.endswith('\r\n'):
                    break
            response = self.RESPONSE_PREFIX + ''.join(total_data)
            yield client.send(response)
            yield client.close()

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        s.listen(20)
        async_sock = Socket(s)
        while True:
            client, address = yield async_sock.accept()
            yield _handle_request(client, address)

    def _get_free_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # get free port
        for i in range(0, 100):
            port = 9000 + i
            try:
                s.bind((self.host, port))
                s.close()
                return port
            except socket.error:
                pass
        raise Exception('No free ports')

    def _assert_correct_request(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        time.sleep(self.SAFE_CONN_WAIT)
        s.connect((self.host, self.port))
        s.send(self.REQUEST)
        total_data = []
        while True:
            data = s.recv(2048)
            total_data.append(data)
            if data.endswith('\r\n'):
                break
        s.close()
        response = ''.join(total_data)
        assert response == (self.RESPONSE_PREFIX + self.REQUEST)
        self._wait_till_clean()
        self.scheduler.stop()

    def test_correct_connection(self):
        self.scheduler = Scheduler()
        self.scheduler.add(self._line_reader_echo())
        threading.Thread(target=self._assert_correct_request).start()
        self.scheduler.run()

    def test_connection_remote_close(self):
        def connect_and_close_socket():
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            time.sleep(self.SAFE_CONN_WAIT)
            s.connect((self.host, self.port))
            #s.send('incomplete data')
            s.close()
            self.scheduler.stop()
        self.scheduler = Scheduler()
        self.scheduler.add(self._line_reader_echo())
        threading.Thread(target=self._assert_correct_request).start()
        self.scheduler.run()


    def test_multiple_correct_connections(self):
        self.scheduler = Scheduler()
        self.scheduler.add(self._line_reader_echo())
        threading.Thread(target=self._assert_correct_request).start()
        threading.Thread(target=self._assert_correct_request).start()
        self.scheduler.run()
