import json
import socket
from dataclasses import dataclass, field


# class to dynamically update context information attributes and add new ones to the database
@dataclass()
class ContextInformationKeystoreUpdate:
    keyname: str
    minimum_value: float
    maximum_value: float
    desirable_value: float
    weight: float
    message_type: str = field(default='keystore_update')


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


def send_keystore_update():
    sock = connection_to_server("keystore_information")
    print("Thread 5")
    time_format = '%Y-%m-%dT%H:%M:%S.%f'
    context_information_keystore_update_battery_state = ContextInformationKeystoreUpdate('trip_distance', 0, 500, 0,
                                                                                         5)

    while True:
        if sock:
            while True:
                sock.send(bytes(json.dumps(context_information_keystore_update_battery_state.__dict__), encoding='utf-8'))
                print(json.dumps(context_information_keystore_update_battery_state.__dict__))
                return

        else:
            print("Couldn't establish socket connection for keystore_information")
            print("Will try again after 10 sec ...\n")


send_keystore_update()