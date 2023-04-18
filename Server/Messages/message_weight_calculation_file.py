import os
import time
import tqdm

filename = "D:\PyCharm Projects\Diplomarbeit\Server\Loading_Files\Weight_Calculations\weight_calculation_distance.py"
size_of_file = os.path.getsize(f"{filename}")
DELIMITER = "<delimiter>"
message_type = "weight_calculation_file"
BUFFER_SIZE = 4096


def send_weight_calculation_file(sock):
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