# -*- coding: utf-8 -*-

import socket
import optparse

from corrosion.core.scheduler import Scheduler
from corrosion.net.socket import Socket


def handle_request(client, address):
    total_data = []
    while True:
        data = yield client.recv(1024)
        total_data.append(data)
        # using telnet for tests
        if data == '\r\n':
            break
    response = 'echo: ' + ''.join(total_data)
    yield client.send(response)
    yield client.close()

def echo(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock = Socket(s)
    s.bind((host, port))
    s.listen(10)
    while True:
        client, address = yield sock.accept()
        yield handle_request(client, address)



def main():
    parser = optparse.OptionParser('usage: %prog [-p <port>] [-h <host>]')
    parser.add_option('-p', '--port', type='int', default=8080, dest='port',
            help='server port')
    parser.add_option('--host', default='', dest='host',
            help='server host')
    (options, args) = parser.parse_args()
    scheduler = Scheduler()
    scheduler.add(echo(options.host, options.port))
    print('server running >> %s:%d' % (options.host or '0.0.0.0', options.port))
    scheduler.run()

if __name__ == '__main__':
    main()

