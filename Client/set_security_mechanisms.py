from importlib import import_module
from inspect import getframeinfo, currentframe
from os import listdir
from os.path import isfile, join


def set_security_mechanisms(best_option):
    try:
        security_mechanisms_path = "Security_Mechanisms"
        list_security_mechanism_files = [file for file in listdir(security_mechanisms_path) if isfile(join(security_mechanisms_path, file))]

    except FileNotFoundError:
        frame_info = getframeinfo(currentframe())
        print("""[ERROR]: in""", frame_info.filename, "in line:", frame_info.lineno,
              """could not find security mechanism files in Security_Mechanisms directory""")
        return

    for security_mechanisms_file in list_security_mechanism_files:
        # remove '.py' extension for import call
        formatted_file_name = security_mechanisms_file.replace('.py', '')
        # import file from Security_Mechanisms directory
        imported_mod = import_module(f"Client.Security_Mechanisms.{formatted_file_name}")

        if any(formatted_file_name in item for item in best_option):
            for mode in best_option:
                if mode.startswith(formatted_file_name):
                    call_filter = getattr(imported_mod, mode)
                    call_filter()
