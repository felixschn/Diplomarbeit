import json
import time
from dataclasses import dataclass, field
from itertools import count


# class to dynamically update context information attributes and add new ones to the database
@dataclass()
class ContextInformationKeystoreUpdate:
    identifier: int = field(default_factory=count().__next__, init=False)
    keyname: str
    minimum_value: float
    maximum_value: float
    desirable_value: float
    weight: float
    separator_list: str
    message_type: str = field(default='keystore_update')


def send_keystore_update(sock):
    time_format = '%Y-%m-%dT%H:%M:%S.%f'
    context_information_keystore_update_battery_state = ContextInformationKeystoreUpdate('battery_state', 0, 100, 100,
                                                                                         5, '[20, 40, 60, 80]')

    while True:
        if sock:
            while True:
                sock.send(bytes(json.dumps(context_information_keystore_update_battery_state.__dict__), encoding='utf-8'))
                print(json.dumps(context_information_keystore_update_battery_state.__dict__))
                time.sleep(50)
        else:
            print("Couldn't establish socket connection for keystore_information")
            print("Will try again after 10 sec ...\n")
