import socket
import time
import random

sock = socket.create_connection(("localhost", 9009))

while True:
    value = random.randint(0, 100)
    line = f"test_data value={value}\n"
    sock.sendall(line.encode())
    time.sleep(1)