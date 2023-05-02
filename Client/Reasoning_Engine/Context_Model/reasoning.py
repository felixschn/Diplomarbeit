import math
from importlib import import_module
from inspect import getframeinfo, currentframe

import Client.Data_Engine.context_information_database as context_information_database


def apply_filters(context_information_dict) -> list:
    necessary_modes_list = []
    available_security_mechanisms_list = context_information_database.get_security_mechanisms_information_name()

    try:
        # better to access information through the database instead of iterating through the filter directory, which prevents the execution of unknown (
        # filter) files --> security vulnerabilities if attacker could add a file to the directory and their
        filter_list = context_information_database.get_security_mechanisms_filter()

    except:
        frame_info = getframeinfo(currentframe())
        print("""[ERROR]: in""", frame_info.filename, "in line:", frame_info.lineno,
              """could not retrieve filters from the database""")
        return []

    # loop through the filter files
    for filter_file in filter_list:
        # remove .py extension for import call
        formatted_file_name = filter_file[0].replace('.py', '')

        # try to import the filter_file from Filter directory
        try:
            imported_mod = import_module(f"Client.Reasoning_Engine.Filter.{formatted_file_name}")

        except Exception as e:
            print(e)
            continue

        # try to import 'execute_filter' function from filter_file
        try:
            call_filter = getattr(imported_mod, 'execute_filter')
            # merge the returned list of the filter files to the necessary_modes_list
            necessary_modes_list.extend(call_filter(available_security_mechanisms_list, context_information_dict))

        except:
            print("""some of the files in the Filter directory aren't usable filters""")
            continue

    # return a list that contains no duplicates
    return list(set(necessary_modes_list))


def calculate_best_combination(weight, max_weight, context_information_dict):
    # call filter files to retrieve necessary security mechanism modes depending on the context information
    necessary_modes = apply_filters(context_information_dict)

    # calculate the weight limit for combinations to choose
    # TODO check if floor (abrunden) is better then ceil (aufrunden)
    combination_weight_limit = math.floor(weight / max_weight * context_information_database.get_max_weight_combination())
    print("combination_weight_limit: ", combination_weight_limit)

    # query the database for the best affordable combinations (best means the highest value and lowest weight)
    best_affordable_combination = context_information_database.get_best_affordable_combination(combination_weight_limit, necessary_modes)

    return best_affordable_combination
