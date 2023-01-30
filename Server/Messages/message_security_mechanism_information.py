from dataclasses import dataclass, field
import json
import time

# class to dynamically add new information about security mechanisms who should be add to the system
@dataclass
class SecurityMechanismsInformation():
    mechanism_name: str
    modes: int
    mode_weights: list
    mode_values: list
    message_type: str = field(default="security_mechanisms_information")


def send_security_mechanisms_information(sock):
    time_format = '%Y-%m-%dT%H:%M:%S.%f'
    security_mechanisms_information = SecurityMechanismsInformation('checker', 5, [0, 5, 10, 15, 20], [0, 2, 3, 4, 10])

    while True:
        if sock:
            while True:
                sock.send(bytes(json.dumps(security_mechanisms_information.__dict__), encoding='utf-8'))
                print(json.dumps(security_mechanisms_information.__dict__))
                time.sleep(100)
        else:
            print("Couldn't establish socket connection for security_mechanisms_information")
            print("Will try again after 10 sec ...\n")
