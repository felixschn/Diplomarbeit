import random
from dataclasses import dataclass, field
from itertools import count

# class to create extended context information packet for simulation purposes
@dataclass
class ContextInformationCreationExtended():
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
