import socket
import queue
from threading import Lock

class ConnectionBrokenException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

def get_ip(DNS: str = "8.8.8.8", port: int = 80) -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((DNS, port))
    ip = s.getsockname()[0]
    s.close()
    return ip

def get_all_data_from_socket(target_socket: socket.socket) -> bytes:
    socket_data: bytes = b''
    new_data_exists: bool = True
    while new_data_exists:
        try:
            new_packet = target_socket.recv(4096)
            if new_packet == b'':
                raise ConnectionBrokenException()
            socket_data += new_packet
        except TimeoutError:
            new_data_exists = False
    return socket_data

def send_all_from_queue(target_socket: socket.socket, target_queue: queue.Queue, target_queue_lock: Lock) -> None:
    while not target_queue.empty():
        with target_queue_lock:
            # access the last value without removing it
            payload = target_queue.queue[0]
            target_socket.sendall(payload)
            # remove only after a successfull sending
            _ = target_queue.get()

class Singleton(type):
    def __init__(self, *args, **kwargs):
        self.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.__instance is None:
            self.__instance = super().__call__(*args, **kwargs)
            return self.__instance
        else:
            return self.__instance