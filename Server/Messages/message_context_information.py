import json
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from itertools import count


# class to create extended context information packet for simulation purposes
@dataclass
class ContextInformationCreation():
    # get unique identifier for each object
    identifier: int = field(default_factory=count().__next__, init=False)
    battery_state: int
    battery_consumption: int
    battery_health: str

    # anmerkungen:
    # 1)vllt bei der Distanz eine Liste nehmen, falls verschiedene Ladestationen angezeigt wreden sollen
    # 2) Säule bei Start mit einbeziehen?
    charging_station_distance: float

    # bei location vllt auch ein Tuple nehmen, für die Koordinatenangabe
    location: int
    elicitation_date: str
    message_type: str = field(default='context_information')

    @staticmethod
    def battery_information() -> float:
        return random.uniform(0.01, 99.00)

    @staticmethod
    def distance_generator() -> float:
        return round(random.uniform(0.01, 99.99), 2)

    @staticmethod
    def location_generator() -> int:
        return random.randint(1, 193)


def send_context_information(sock):
    time_format = '%Y-%m-%dT%H:%M:%S.%f'

    while True:
        if sock:
            context_information = ContextInformationCreation(ContextInformationCreation.battery_information(),
                                                             ContextInformationCreation.battery_information(),
                                                             "good",
                                                             ContextInformationCreation.distance_generator(),
                                                             125, datetime.now().strftime(time_format))

            sock.send(bytes(json.dumps(context_information.__dict__), encoding='utf-8'))
            print(json.dumps(context_information.__dict__))
            time.sleep(10)


        else:
            print("Couldn't establish socket connection for context information message")
            print("Will try again after 10 sec ...\n")
