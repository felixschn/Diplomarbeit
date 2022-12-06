import json

# this class intends to send randomized context information to the client
import random
from itertools import count
from dataclasses import dataclass, field
from datetime import datetime


def battery_information() -> int:
    return random.randint(0, 99)


def distance_generator() -> float:
    return random.uniform(0.00, 999.99)


def location_generator() -> str:
    return str(random.uniform(1.0000000, 99.999999)) + ',' + str(random.uniform(1.0000000, 99.999999))


@dataclass
class ContextInformationCreation():
    # get unique identifier for each object
    identifier: int = field(default_factory=count().__next__, init=False)
    battery_state: int

    #anmerkungen:
    # 1)vllt bei der Distanz eine Liste nehmen, falls verschiedene Ladestationen angezeigt wreden sollen
    # 2) Säule bei Start mit einbeziehen?
    charging_station_distance: float

    #bei location vllt auch ein Tuple nehmen, für die Koordinatenangabe
    location: str
    elicitation_date: datetime



print(datetime.now().date())
