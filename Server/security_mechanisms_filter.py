from dataclasses import dataclass, field


@dataclass
class SecurityMechanismsFilter():
    filter_name: str
    necessary_modes: list
    message_type: str = field(default='security_mechanisms_filter')
