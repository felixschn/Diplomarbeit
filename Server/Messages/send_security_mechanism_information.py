import json
from dataclasses import dataclass, field

import Server.main as main


# class to create new security mechanism information and send it to the Client's Context Model during runtime
@dataclass
class SecurityMechanismInformation:
    mechanism_name: str
    modes: int
    mode_costs: list
    mode_values: list
    message_type: str = field(default="security_mechanisms_information")


def send_security_mechanisms_information(security_mechanism_information):
    # establish a socket connection by calling the function in main.py
    sock = main.connection_to_server("security_mechanisms_information")

    # sending security mechanism information to the Client if a socket connection is established
    if sock:
        sock.send(bytes(json.dumps(security_mechanism_information.__dict__), encoding='utf-8'))
        print("Sending Security Mechanism Information Message:\n\t\t", json.dumps(security_mechanism_information.__dict__))

    else:
        print("Couldn't establish socket connection for security_mechanisms_information")


# create SecurityMechanismInformation object and send it to the Client
send_security_mechanisms_information(SecurityMechanismInformation('vpn', 2, [0, 15], [0, 15]))
