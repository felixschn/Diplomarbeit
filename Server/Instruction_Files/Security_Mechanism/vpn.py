import subprocess
from inspect import getframeinfo, currentframe


def _vpn0():
    try:
        result = subprocess.run(["sudo", "wq-quick", "down", "raspi_client.conf"], capture_output=True)
    except:
        frame_info = getframeinfo(currentframe())
        print("""[ERROR]: in""", frame_info.filename, "in line:", frame_info.lineno,
              """could not turn down vpn connection""")
        return


def _vpn1():
    try:
        result = subprocess.run(["sudo", "wq-quick", "up", "raspi_client.conf"], capture_output=True)
    except:
        frame_info = getframeinfo(currentframe())
        print("""[ERROR]: in""", frame_info.filename, "in line:", frame_info.lineno,
              """could not turn on vpn connection""")
        return


def vpn(mode):
    match mode:
        case 0:
            _vpn0()
        case 1:
            _vpn1()
        case _:
            print("cannot find vpn mode")
