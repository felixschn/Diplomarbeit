import random
from dataclasses import dataclass, field
from itertools import count


@dataclass
class ContextInformationCreation():
    # get unique identifier for each object
    identifier: int = field(default_factory=count().__next__, init=False)
    battery_state: int

    # anmerkungen:
    # 1)vllt bei der Distanz eine Liste nehmen, falls verschiedene Ladestationen angezeigt wreden sollen
    # 2) Säule bei Start mit einbeziehen?
    charging_station_distance: float

    # bei location vllt auch ein Tuple nehmen, für die Koordinatenangabe
    location: int
    elicitation_date: str

    @staticmethod
    def battery_information() -> int:
        return random.randint(0, 99)

    @staticmethod
    def distance_generator() -> float:
        return round(random.uniform(0.00, 999.99), 2)

    @staticmethod
    def location_generator() -> int:
        return random.randint(1, 195)
