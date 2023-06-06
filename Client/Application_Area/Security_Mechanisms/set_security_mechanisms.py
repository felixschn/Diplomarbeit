import re
from importlib import import_module
from inspect import getframeinfo, currentframe


def set_security_mechanisms(best_option):
    # extract security mechanism modes from best options and execute them
    for security_mechanism in best_option:
        mechanism_name = "".join((re.findall(r"[a-zA-Z]+", security_mechanism)))
        mode_number = int("".join((re.findall(r"\d+", security_mechanism))))

        try:
            imported_mod = import_module(f"Client.Application_Area.Security_Mechanisms.{mechanism_name}")
            security_mechanism_entry_point = getattr(imported_mod, mechanism_name)
            security_mechanism_entry_point(mode_number)

        except:
            frame_info = getframeinfo(currentframe())
            print("""[ERROR]: in""", frame_info.filename, "in line:", frame_info.lineno, "could not import and set security mechanism; security file missing?")
