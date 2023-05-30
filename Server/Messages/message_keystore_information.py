import json
from dataclasses import dataclass, field

import Server.main as main


# class to create Keystore updates for new context information in the Client's Context Model
@dataclass()
class KeystoreUpdate:
    keyname: str
    minimum_value: float
    maximum_value: float
    desirable_value: float
    weight: float
    message_type: str = field(default='keystore_update')


def send_keystore_update():
    # establish a socket connection by calling the function in main.py
    sock = main.connection_to_server("keystore_information")

    # create KeystoreUpdate object
    keystore_update_battery_state = KeystoreUpdate('trip_distance', 0, 500, 0, 5)

    # sending the created object to the Client if a socket connection is established
    if sock:
        print("Sending Keystore Update Message: ")
        sock.send(bytes(json.dumps(keystore_update_battery_state.__dict__), encoding='utf-8'))
        print(json.dumps(keystore_update_battery_state.__dict__))

    else:
        print("Couldn't establish socket connection for keystore_information")
        print("Will try again after 10 sec ...\n")


send_keystore_update()
