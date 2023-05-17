import math
from importlib import import_module
from inspect import getframeinfo, currentframe

import Client.Data_Engine.context_information_database as context_information_database


def apply_filters(context_information_dict) -> list:
    necessary_modes_list = []

    try:
        # get available filter names out of database
        filter_list = context_information_database.get_security_mechanisms_filter()

    except:
        frame_info = getframeinfo(currentframe())
        print("[ERROR]: in", frame_info.filename, "in line:", frame_info.lineno,
              "could not retrieve filters from the database")
        return []

    # loop through the filter names
    for filter_file in filter_list:
        # remove .py extension for import call
        formatted_file_name = filter_file[0].replace('.py', '')

        try:
            # import the filter_file from Filter directory
            imported_mod = import_module(f"Client.Reasoning_Engine.Filter.{formatted_file_name}")

        except Exception as e:
            frame_info = getframeinfo(currentframe())
            print("[ERROR]: in", frame_info.filename, "in line:", frame_info.lineno,
                  "could not import filter: ", formatted_file_name)
            continue

        try:
            # import 'execute_filter' function from filter_file
            call_filter = getattr(imported_mod, 'execute_filter')

            # calling filter function and extend necessary_modes_list with the filter result
            necessary_modes_list.extend(call_filter(context_information_dict))

        except:
            frame_info = getframeinfo(currentframe())
            print("[ERROR]: in", frame_info.filename, "in line:", frame_info.lineno,
                  "could not execute filter: ", formatted_file_name)
            continue

    # return necessary_modes_list that contains no duplicates
    return list(set(necessary_modes_list))


def calculate_best_combination(calculated_weight, max_weight, context_information_dict):
    # apply filters to retrieve necessary security mechanism modes
    necessary_modes = apply_filters(context_information_dict)

    # calculate the weight limit for combinations to choose
    combination_weight_limit = math.floor(calculated_weight / max_weight * context_information_database.get_max_weight_combination())
    print("combination_weight_limit: ", combination_weight_limit)

    # query the database for the best affordable combinations (best means the highest value and lowest weight)
    best_affordable_combination = context_information_database.get_best_affordable_combination(combination_weight_limit, necessary_modes)

    return best_affordable_combination
