# -*- coding: utf-8 -*-
import socket
import select
import queue
import json

from .base_engine import BaseEngine
from easyquant.event_engine import Event

class XueqiuAllEngine(BaseEngine):
    """雪球全部市场行情推送引擎"""
    EventType = 'all'
    PushInterval = 0

    def init(self):
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_address = ("127.0.0.1", 8888)
        self.serversocket.bind(self.server_address)
        self.serversocket.listen(10)
        self.serversocket.setblocking(False)
        self.timeout = -1
        self.epoll = select.epoll()
        self.epoll.register(self.serversocket.fileno(), select.EPOLLIN)
        self.message_queues = {}
        self.buf = b''
        self.fd_to_socket = {self.serversocket.fileno(): self.serversocket,}


    def push_quotation(self):
        try:
            while self.is_active:
                events = self.epoll.poll(self.timeout)
                if not events:
                    continue
                for fd, event in events:
                    socket = self.fd_to_socket[fd]
                    if socket == self.serversocket:
                        connection, address = self.serversocket.accept()
                        connection.setblocking(False)
                        self.epoll.register(connection.fileno(), select.EPOLLIN)
                        self.fd_to_socket[connection.fileno()] = connection
                        self.message_queues[connection] = queue.Queue()
                    elif event & select.EPOLLHUP:
                        self.epoll.unregister(fd)
                        self.fd_to_socket[fd].close()
                        del self.fd_to_socket[fd]
                    elif event & select.EPOLLIN:
                        tmpbuf = socket.recv(10240)
                        if not len(tmpbuf):
                            self.epoll.modify(fd, select.EPOLLHUP)
                        if tmpbuf.endswith(b'EOF'):
                            self.buf += tmpbuf
                            self.message_queues[socket].put(self.buf.decode('utf-8')[:-3])
                            self.buf = b''
                            tmpbuf = b''
                            self.epoll.modify(fd, select.EPOLLOUT)
                        else:
                            self.buf += tmpbuf
                    elif event & select.EPOLLOUT:
                        try:
                            response_str = self.message_queues[socket].get_nowait()
                        except queue.Empty:
                            self.epoll.modify(fd, select.EPOLLIN)
                        else:
                            response_dict = json.loads(response_str)
                            event_req = Event(event_type=self.EventType, data=response_dict)
                            self.event_engine.put(event_req)
        finally:
            self.epoll.unregister(self.serversocket.fileno())
            self.epoll.close()
            self.serversocket.close()