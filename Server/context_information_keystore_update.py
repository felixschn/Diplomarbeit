from dataclasses import dataclass, field
from itertools import count


@dataclass()
class ContextInformationKeystoreUpdate:
    identifier: int = field(default_factory=count().__next__, init=False)
    keyname: str
    minimum_value: float
    maximum_value: float
    optimum_value: float
    weight: float
    separator_list: list
    message_type: str = field(default='keystore_update')
