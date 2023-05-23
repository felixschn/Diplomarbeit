import json
import socket
import socketserver
import time
from dataclasses import dataclass, field


# class to dynamically add new information about security mechanisms who should be add to the system
@dataclass
class SecurityMechanismsInformation():
    mechanism_name: str
    modes: int
    mode_weights: list
    mode_values: list
    message_type: str = field(default="security_mechanisms_information")


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

def send_security_mechanisms_information():
    sock = connection_to_server("security_mechanisms_information")
    time_format = '%Y-%m-%dT%H:%M:%S.%f'
    security_mechanisms_information = SecurityMechanismsInformation('vpn', 2, [0, 15], [0, 15])

    while True:
        if sock:
            while True:
                sock.send(bytes(json.dumps(security_mechanisms_information.__dict__), encoding='utf-8'))
                print(json.dumps(security_mechanisms_information.__dict__))
                return

        else:
            print("Couldn't establish socket connection for security_mechanisms_information")
            print("Will try again after 10 sec ...\n")

send_security_mechanisms_information()
