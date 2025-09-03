import socket
import threading
import queue
from threading import Lock, Event
from proxy_connector.connection_config import ConnectionConfig
from proxy_connector.utils import get_all_data_from_socket, send_all_from_queue, ConnectionBrokenException, get_ip, Singleton
from standarted_logger.logger import Logger
from time import sleep


class ProxyClient(metaclass=Singleton):
    RECONNECT_TIMEOUT = 1

    def __init__(self, config: ConnectionConfig, logger_enabled: bool = True):
        self.__config = config
        self.__proxy_incoming_messages: queue.Queue[bytes] = queue.Queue()
        self.__local_incoming_messages: queue.Queue[bytes] = queue.Queue()
        self.__proxy_queue_lock: Lock = Lock()
        self.__local_queue_lock: Lock = Lock()
        self.__threads_running: Event = Event()
        self.__logger = Logger.get_logger("proxy-client")
        self.__log = logger_enabled

    def __handle_connection(self, 
                            host: str, 
                            port: int, 
                            msg_queue_put: queue.Queue, 
                            msg_queue_read: queue.Queue, 
                            put_queue_lock: Lock,
                            read_queue_lock: Lock,
                            source_port: int|None = None) -> None:

        while self.__threads_running.is_set():
            try:
                target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                if source_port is not None:
                    local_ip: str = get_ip()
                    if local_ip.startswith("192.168"):
                        if self.__log:
                            self.__logger.debug(f"Not binding source port - testing not in container")
                    else:
                        if self.__log:
                            self.__logger.debug(f"Binding source port to {source_port}")
                        target_socket.bind(("0.0.0.0", source_port))
                target_socket.connect((host, port))
                target_socket.settimeout(0.1)
                if self.__log:
                    self.__logger.debug(f"Connection to {host}:{port} established")

                try:
                    while self.__threads_running.is_set():
                        send_all_from_queue(target_socket, msg_queue_read, read_queue_lock)
                        payload = get_all_data_from_socket(target_socket)
                        if payload != b'':
                            with put_queue_lock:
                                msg_queue_put.put(payload)
                except ConnectionBrokenException:
                    if self.__log:
                        self.__logger.debug(f"Disconnected, reconnecting in {ProxyClient.RECONNECT_TIMEOUT}s")
                    sleep(ProxyClient.RECONNECT_TIMEOUT)
                except Exception as exc:
                    if self.__log:
                        self.__logger.debug(f"Exception in handle_socket: {exc}")
                target_socket.close()
            except ConnectionRefusedError:
                if self.__log:
                    self.__logger.debug(f"Connection to {host}:{port} refused, reconnecting in {ProxyClient.RECONNECT_TIMEOUT}s")
                sleep(ProxyClient.RECONNECT_TIMEOUT)
            
    def stop_server(self) -> None:
        if self.__threads_running.is_set():
            self.__threads_running.clear()
            if self.__log:
                self.__logger.debug(f"Stopping server")
        else:
            if self.__log:
                self.__logger.debug(f"Not stopping server because it is not started")

    def start_client(self):
        if self.__threads_running.is_set():
            if self.__log:
                self.__logger.debug(f"Client is already running")
                return
            
        if self.__log:
            self.__logger.debug(f"Starting local proxy client")
        self.__threads_running.set()
        while self.__threads_running.is_set():
            try:
                client_handler = threading.Thread(target=self.__handle_connection, args=(self.__config.remote_proxy_ip, 
                                                                                self.__config.remote_forward_port, 
                                                                                self.__local_incoming_messages, 
                                                                                self.__proxy_incoming_messages, 
                                                                                self.__local_queue_lock,
                                                                                self.__proxy_queue_lock,))
                server_handler = threading.Thread(target=self.__handle_connection, args=(self.__config.local_proxy_ip, 
                                                                                self.__config.local_forward_port, 
                                                                                self.__proxy_incoming_messages, 
                                                                                self.__local_incoming_messages, 
                                                                                self.__proxy_queue_lock,
                                                                                self.__local_queue_lock,
                                                                                self.__config.local_source_port))
                client_handler.start()
                server_handler.start()
                client_handler.join()
                server_handler.join()
            except Exception as exc:
                if self.__log:
                    self.__logger.debug(f"Exception in main thread: {exc}")