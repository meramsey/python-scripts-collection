import socket
from contextlib import closing

free_port = ''

def find_free_port():
    global free_port
    # import websshport
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('127.0.0.1', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # websshport.free_port = s.getsockname()[1]
        free_port = s.getsockname()[1]
        return free_port

find_free_port()
print(free_port)