from dataclasses import dataclass, field


# class to dynamically add new information about security mechanisms who should be add to the system
@dataclass
class SecurityMechanismsInformation():
    mechanism_name: str
    modes: int
    mode_values: list
    message_type: str = field(default="security_mechanisms_information")