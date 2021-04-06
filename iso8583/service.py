import os
import sys
import time
import socket

from .logger import Logger
from .config import DeviceConfig
from .config import DeviceConfigLoader
from .base import ISO8583  # Temporary
from .builder import Builder


class BaseService(ISO8583):
    def __init__(self, device_name, dict_name, traffic=False):
        self.log = Logger()
        self.__traffic = traffic
        self.socket_closed = True
        self._packet_split = False
        self.buffer_size = 2048
        self.broken_pipe_count = 0
        self.max_broken_pipes = 3
        self.cfg = DeviceConfigLoader(device_name)
        self.address = (self.cfg.host, self.cfg.port)
        self.tcp_socket()
        self.builder = Builder(self.cfg)(dict_name)

    def tcp_socket(self):
        return None

    def handle_connection_failure(self, initial=False):
        self.broken_pipe_count += 1
        if self.broken_pipe_count >= self.max_broken_pipes:
            self.log.Error(
                f"Max Disconnections Count ({self.max_broken_pipes}) Reached ({self.cfg.host}:{self.cfg.port})")
            sys.exit(0)
        self.close_socket()

    def recv(self):
        if self.socket_closed: return None
        try:
            data = self.sock.recv(self.buffer_size)
        except socket.timeout:
            data = None
        except socket.error as e:
            self.log.Error(f"Error trying to read socket: {e} ({self.cfg.host}:{self.cfg.port})")
            self.handle_connection_failure()
            data = None
        except BlockingIOError as e:
            self.log.Error(f"Error while trying to read socket: {e} ({self.cfg.host}:{self.cfg.port})")
            self.handle_connection_failure()
            data = None
        # if data and self._traffic: self._traffic.write(data, out=True)
        self.log.Debug(f"Socket read complete: {data}")
        return data

    def send(self, msg, count=True) -> bool:
        self.log.Debug(f"Send message:\n{msg}")
        data = self.builder.build(msg)
        self.log.Debug(f"Send message HEX:\n{self.hexdump(data)}")
        try:
            self.sock.send(data)
        except socket.error as e:
            self.log.Error(f"Socket Error while trying to send message: {e} ({self.cfg.host}:{self.cfg.port})")
            return False
        except IOError as e:
            self.log.Error(f"IO Error while trying to send message: {e} ({self.cfg.host}:{self.cfg.port})")
            return False
        # if self.__traffic:
        #     self.__traffic.write(msg, out=False)
        return True

    def close_socket(self, increase_disconnections=False):
        try:
            self.sock.close()
        except Exception as e:
            self.log.Error(f"Error while trying to close socket: {e} ({self.cfg.host}:{self.cfg.port})")
        if increase_disconnections and not self.socket_closed:
            self.broken_pipe_count += 1
            if self.broken_pipe_count >= self.max_broken_pipes:
                self.log.Error(
                    f"Max Disconnections Count ({self.max_broken_pipes}) Reached ({self.cfg.host}:{self.cfg.port})")
                sys.exit(0)
        self.socket_closed = True



# class Client(ISO8583):
class Client(BaseService):
    def tcp_socket(self):
        if self.socket_closed:
            self.log.Info("Socket closed")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.cfg.socket.get("TCP_NO_DELAY", 0) == 1:
                self.log.Info("Socket TCP_NO_DELAY is set")
                self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
            if self.cfg.socket.get("SO_REUSEADDR", 1) == 1:
                self.log.Info("Socket SO_REUSEADDR is set")
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # if self.cfg.get("Socket", self._def_socket).get("SO_REUSEADDR", 1) == 1:
            #     self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, int(self.cfg["SO_RCVBUF"]))
            self.socket_closed = False
        try:
            self.log.Info(f"Trying to establish connection to {self.cfg.host}:{self.cfg.port}")
            self.sock.connect((self.cfg.host, self.cfg.port))
        except socket.timeout as e:
            self.log.Error(f"Error while trying to establish connection: {e} ({self.cfg.host}:{self.cfg.port})")
            self.handle_connection_failure(initial=True)
            return False
        except socket.error as e:
            self.log.Error(f"Error while trying to establish connection: {e} ({self.cfg.host}:{self.cfg.port})")
            self.handle_connection_failure(initial=True)
            return False
        self.sock.setblocking(1)
        # self.sock.setblocking(0)
        # Nagle algo
        if self._packet_split:
            self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        self.log.Info(f"Socket is open. Connection is established to {self.cfg.host}:{self.cfg.port}")
        return True

class Server(BaseService):
    def __init__(self, device_name, dict_name):
        self.server_alive = False
        super().__init__(device_name, dict_name)

    def tcp_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setblocking(0)
        server_address = (self.cfg.host, self.cfg.port)
        self._start_time = time.time()
        last_flush = time.time()
        self._last_read = time.time()
        try:
            self.sock.bind(server_address)
            self.server_alive = True
        except (socket.timeout, socket.error) as e:
            self.log.Error('Error while trying to bind socket: %s (%s:%i)' % (e, self.cfg.host, self.cfg.port))
            sys.exit(13)
        while self.server_alive:
            self.sock.settimeout(1.0)
            self.sock.listen(1)
            try:
                self.connection, self.client_address = self.sock.accept()
            except socket.timeout:
                continue
            self.connection.setblocking(0)
            self.client_addr = self.connection.getpeername()
            self.log.Info('Client connected (%s:%i)' % self.client_addr)
