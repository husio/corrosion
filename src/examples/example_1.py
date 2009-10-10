# -*- coding: utf-8 -*-

import socket
import optparse

from corrosion.core.scheduler import Scheduler
from corrosion.core import calls
from corrosion.net.sock import Socket


def handle_request(sock, addr):
    data = ''
    while True:
        data += yield sock.recv(1024)
        # using telnet for tests
        if '\r\n' in data:
            break
    response = 'echo: ' + data
    yield sock.send(response)
    yield sock.close()

def echo(raw_sock, host, port):
    sock = Socket(raw_sock)
    sock.bind((host, port))
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.listen(2)
    while True:
        print '>> waiting for new connection'
        conn, addr = yield sock.accept()
        yield calls.SubCall(handle_request(conn, addr))



def main():
    parser = optparse.OptionParser('usage: %prog [-p <port>] [-h <host>]')
    parser.add_option('-p', '--port', type='int', default=8080, dest='port',
            help='server port')
    parser.add_option('--host', default='', dest='host',
            help='server host')
    (options, args) = parser.parse_args()
    scheduler = Scheduler()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    scheduler.add(echo(sock, options.host, options.port))
    print('>> server running  %s:%d' % (options.host or '0.0.0.0', options.port))
    try:
        scheduler.run()
    except KeyboardInterrupt:
        scheduler.stop()
    finally:
        sock.close()

if __name__ == '__main__':
    main()

