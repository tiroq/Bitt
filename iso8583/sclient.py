import sys
import socket

from .logger import Logger
from .base import ISO8583  # Temporary

class Client(ISO8583):
    def __init__(self, config, traffic=False):
        self.log = Logger()
        self.__traffic = traffic
        self.socket_closed = True
        self._packet_split = False
        self.buffer_size = 2048
        self.broken_pipe_count = 0
        self.max_broken_pipes = 3
        self.cfg = config
        self.address = (self.cfg.host, self.cfg.port)
        self.tcp_socket()
    
    def tcp_socket(self):
        if self.socket_closed:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.cfg.socket.get("TCP_NO_DELAY", 0) == 1:
                self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
            if self.cfg.socket.get("SO_REUSEADDR", 1) == 1:
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # if self.cfg.get("Socket", self._def_socket).get("SO_REUSEADDR", 1) == 1:
            #     self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, int(self.cfg["SO_RCVBUF"]))
            self.socket_closed = False
        try:
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
        return True
    
    def handle_connection_failure(self, initial=False):
        self.broken_pipe_count += 1
        if self.broken_pipe_count >= self.max_broken_pipes:
            self.log.Error(f"Max Disconnections Count ({self.max_broken_pipes}) Reached ({self.cfg.host}:{self.cfg.port})")
            sys.exit(0)
        self.close_socket()

    def close_socket(self, increase_disconnections=False):
        try:
            self.sock.close()
        except Exception as e:
            self.log.Error(f"Error while trying to close socket: {e} ({self.cfg.host}:{self.cfg.port})")
        if increase_disconnections and not self.socket_closed:
            self.broken_pipe_count += 1
            if self.broken_pipe_count >= self.max_broken_pipes:
                self.log.Error(f"Max Disconnections Count ({self.max_broken_pipes}) Reached ({self.cfg.host}:{self.cfg.port})")
                sys.exit(0)
        self.socket_closed = True

    def read_socket(self):
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

    def send(self, data, count=True) -> bool:
        self.log.Debug(f"Send message:\n{self.hexdump(data)}")
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
