import os
import time
import tqdm
import socket

filename = "D:\PyCharm Projects\Diplomarbeit\Server\Loading_Files\Filter\\follower.py"
size_of_file = os.path.getsize(f"{filename}")
DELIMITER = "<delimiter>"
message_type = "security_mechanisms_filter"
BUFFER_SIZE = 4096


def connection_to_server(message_name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 65000
    host = "127.0.0.1"

    # Connect to server and send data
    try:
        sock.connect((host, port))
        # sock.sendall(bytes(data + "\n", "utf-8"))
        print("Connection established")
        return sock

    except:
        print(f"{message_name}: Couldn't connect, because wrong port or IP address was used", port)

    return

def send_filter_file():
    sock = connection_to_server("filter_file")
    print("Thread 3")
    sock.send(f"{message_type}{DELIMITER}{filename}{DELIMITER}{size_of_file}{DELIMITER}".encode())
    show_progress = tqdm.tqdm(range(size_of_file), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    time.sleep(2)
    with open(filename, "rb") as file:
        while True:
            read_data = file.read(BUFFER_SIZE)
            if not read_data:
                break
            sock.sendall(read_data)
            show_progress.update(len(read_data))
    sock.close()

send_filter_file()

