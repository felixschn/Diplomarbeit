from dataclasses import dataclass, field

@dataclass
class ContextInformationSecurityMechanismsInformation():
    mechanism_name : str
    modes : int
    message_type: str = field(default='security_mechanisms_information')