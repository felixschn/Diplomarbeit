import os
import time
from pathlib import Path

import tqdm

import Server.main as main

DELIMITER = "<delimiter>"
BUFFER_SIZE = 4096

# create dynamic path declarations and file information
path_to_project = Path(__file__).parents[2]
path_to_file = path_to_project.joinpath("Server\\Instruction_Files\\Filter\\dangerous_area.py")
size_of_file = os.path.getsize(f"{path_to_file}")
filename = path_to_file.name
message_type = "security_mechanisms_filter"


def send_filter_file():
    # establish a socket connection by calling the function in main.py
    sock = main.connection_to_server("filter_file")

    # send a message identifier string that contains the message type, filename, and size of the file
    sock.send(f"{message_type}{DELIMITER}{filename}{DELIMITER}{size_of_file}{DELIMITER}".encode())

    # create a graphical bar that will show the progress of the transmission; optional delay for better graphical representation
    show_progress = tqdm.tqdm(range(size_of_file), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    time.sleep(2)

    # reading the security mechanism file from the Sever and sending it to the Client
    with open(path_to_file, "rb") as file:
        while True:
            read_data = file.read(BUFFER_SIZE)
            if not read_data:
                break
            sock.sendall(read_data)
            show_progress.update(len(read_data))
    sock.close()


send_filter_file()
