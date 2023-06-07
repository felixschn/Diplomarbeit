import subprocess
from inspect import getframeinfo, currentframe


def _vpn0():
    print("disabled vpn0")

def _vpn1():
    print("enabled vpn1")



def vpn(mode):
    match mode:
        case 0:
            _vpn0()
        case 1:
            _vpn1()
        case _:
            print("cannot find vpn mode")
