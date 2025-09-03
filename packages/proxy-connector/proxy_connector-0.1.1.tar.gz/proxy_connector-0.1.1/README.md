# Python proxy-server lib
Can be used in cases when it is required to connect from white-ip server go grey-ip client. In fact, the websocket connection is initiated by client and then it is kept alive until program/container is stopped. Any data passed in binary format to client is redirected to server and vice versa. There are two possible options to use this lib: via running separate containers and via importing it from python.

## Option with separate containers
1. Create Dockerfiles from the following two files with the same config
2. Run container with client_side.py on a client machine
3. Run container with server_side.py on a server machine


```python
from proxy_connector.connection_config import ConnectionConfig

config = ConnectionConfig(remote_proxy_ip=<ip of a server>, 
                          remote_listen_port=<server listen port>, 
                          remote_forward_port=<internal proxy port>,
                          local_proxy_ip=<ip of a client>,
                          local_forward_port=<client listen port>,
                          local_source_port=<port within container>)

# example
config = ConnectionConfig(remote_proxy_ip="192.168.1.34", 
                          remote_listen_port=4805, 
                          remote_forward_port=61842,
                          local_proxy_ip="192.168.1.34",
                          local_forward_port=8008,
                          local_source_port=12215)
```

__client_side.py__
```python
from time import sleep
import threading

from proxy_connector.local_client import ProxyClient
# import config

server = ProxyClient(config)

main_thread = threading.Thread(target=server.start_client)
main_thread.start()
# do something
server.stop_server()
main_thread.join()
```
__server_side.py__
```python
from time import sleep
import threading

from proxy_connector.remote_proxy import ProxyServer
# import config

server = ProxyServer(config)

main_thread = threading.Thread(target=server.start_server)
main_thread.start()
# do something
server.stop_server()
main_thread.join()
```
