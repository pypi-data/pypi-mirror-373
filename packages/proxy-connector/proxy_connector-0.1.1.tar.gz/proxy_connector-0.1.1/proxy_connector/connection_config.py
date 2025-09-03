
from dataclasses import dataclass
import re

@dataclass
class ConnectionConfig:
    remote_proxy_ip: str            # remote server address
    remote_listen_port: int         # main server program's port - remote proxy part listening on it
    remote_forward_port: int        # port, to which local proxy part is connecting

    local_proxy_ip: str             # address to which the traffic is redirected from local part of proxy
    local_forward_port: int         # port to which the traffic is redirected from local part of proxy
    local_source_port: int          # source port from which connection to remote proxy part is established (because of possible use of container)

    def __post_init__(self):
        ip_pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
        ip_str = "\"int.int.int.int\""
        assert re.search(ip_pattern, self.remote_proxy_ip), f"IP pattern not matching: {self.remote_proxy_ip}, should be {ip_str}"
        assert re.search(ip_pattern, self.local_proxy_ip), f"IP pattern not matching: {self.local_proxy_ip}, should be {ip_str}"
        
        assert isinstance(self.remote_listen_port, int), f"Invalid port specified: {self.remote_listen_port}"
        assert isinstance(self.remote_forward_port, int), f"Invalid port specified: {self.remote_forward_port}"
        assert isinstance(self.local_forward_port, int), f"Invalid port specified: {self.local_forward_port}"
        assert isinstance(self.local_source_port, int), f"Invalid port specified: {self.local_source_port}"