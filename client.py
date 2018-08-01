# Echo client program
import socket
import time

HOST = 'localhost'    # The remote host
PORT = 50012              # The same port as used by the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.send(b'dddddddddddd', 7)
    time.sleep(2)
    s.detach()
    s.connect((HOST, PORT))
    s.send(b'fffffffffffff', 7)
    time.sleep(2)
    s.connect((HOST, PORT))
    s.send(b'Hello, world')
    time.sleep(2)
    s.send(b'blblblblbl')
    time.sleep(2)
    s.send(b'dddddddddddd', 12)