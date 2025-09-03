import socket
import threading
from threading import Lock, Event
import queue
from proxy_connector.utils import get_all_data_from_socket, send_all_from_queue, ConnectionBrokenException, Singleton
from proxy_connector.connection_config import ConnectionConfig
from standarted_logger.logger import Logger

class ProxyServer(metaclass=Singleton):
    def __init__(self, config: ConnectionConfig, logger_enabled: bool = True):
        self.__config = config
        self.__server_incoming_messages: queue.Queue[bytes] = queue.Queue()
        self.__client_incoming_messages: queue.Queue[bytes] = queue.Queue()
        self.__server_queue_lock: Lock = Lock()
        self.__client_queue_lock: Lock = Lock()
        self.__threads_running: Event = Event()
        self.__logger = Logger.get_logger("proxy-server")
        self.__log = logger_enabled

    def __handle_socket(self, 
                        host: str, 
                        port: int, 
                        msg_queue_put: queue.Queue, 
                        msg_queue_read: queue.Queue, 
                        put_queue_lock: Lock,
                        read_queue_lock: Lock) -> None:
        target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        target_socket.bind((host, port))
        target_socket.listen(1) # number of accepted connections
        target_socket.settimeout(0.1)

        while self.__threads_running.is_set():
            target_client = None
            try:
                target_client, _ = target_socket.accept()
                target_client.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3) # Number of probes
                target_client.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1) # Time before first probe
                target_client.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 1) # Interval between probes
                target_client.settimeout(0.1)
                if self.__log:
                    self.__logger.debug(f"(Re)Connected to {host}:{port} successfully")
            except TimeoutError:
                continue
            try:
                while self.__threads_running.is_set():
                    send_all_from_queue(target_client, msg_queue_read, read_queue_lock)
                    target_data = get_all_data_from_socket(target_client)
                    if target_data == b'':
                        continue
                    with put_queue_lock:
                        msg_queue_put.put(target_data)
            except ConnectionBrokenException:
                if self.__log:
                    self.__logger.debug(f"Client {host}:{port} disconnected")
            except Exception as exc:
                if self.__log:
                    self.__logger.debug(f"Exception in handle_socket: {exc}")

            if target_client is not None:
                target_client.close()
        target_socket.close()

    def stop_server(self) -> None:
        if self.__threads_running.is_set():
            self.__threads_running.clear()
            if self.__log:
                self.__logger.debug(f"Stopping server")
        else:
            if self.__log:
                self.__logger.debug(f"Not stopping server because it is not started")

    def start_server(self) -> None:
        if self.__threads_running.is_set():
            if self.__log:
                self.__logger.debug(f"Server is already running")
                return
            
        if self.__log:
            self.__logger.debug(f"Starting remote proxy server")
        self.__threads_running.set()
        while self.__threads_running.is_set():
            try:
                server_handler = threading.Thread(target=self.__handle_socket, args=(self.__config.remote_proxy_ip,
                                                                                self.__config.remote_listen_port,
                                                                                self.__server_incoming_messages,
                                                                                self.__client_incoming_messages,
                                                                                self.__server_queue_lock,
                                                                                self.__client_queue_lock))
                client_handler = threading.Thread(target=self.__handle_socket, args=(self.__config.remote_proxy_ip,
                                                                                self.__config.remote_forward_port,
                                                                                self.__client_incoming_messages,
                                                                                self.__server_incoming_messages,
                                                                                self.__client_queue_lock,
                                                                                self.__server_queue_lock))
                server_handler.start()
                client_handler.start()
                server_handler.join()
                client_handler.join()
            except Exception as exc:
                if self.__log:
                    self.__logger.debug(f"Exception in main thread: {exc}")
