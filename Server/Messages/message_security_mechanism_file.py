import os.path
import time
import tqdm

filename = "D:\PyCharm Projects\Diplomarbeit\Server\Loading_Files\Security_Mechanism\\vpn.py"
size_of_file = os.path.getsize(f"{filename}")
message_type = "security_mechanism_file"
DELIMITER = '<delimiter>'
BUFFER_SIZE = 4096


def send_security_mechanism_file(sock):
    sock.send(f"{message_type}{DELIMITER}{filename}{DELIMITER}{size_of_file}{DELIMITER}".encode())
    show_progress = tqdm.tqdm(range(size_of_file), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    time.sleep(5)
    with open(filename, "rb") as file:
        while True:
            read_data = file.read(BUFFER_SIZE)
            if not read_data:
                break
            sock.sendall(read_data)
            show_progress.update(len(read_data))
    sock.close()

