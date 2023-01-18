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
