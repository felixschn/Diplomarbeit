import math
from importlib import import_module
from inspect import getframeinfo, currentframe

import Client.Data_Engine.database_connector as database_connector


def apply_filters(received_context_information) -> list:
    necessary_modes_list = []

    try:
        # get available filter names out of database
        filter_list = database_connector.get_filter_files()

    except:
        frame_info = getframeinfo(currentframe())
        print("[ERROR]: in", frame_info.filename, "in line:", frame_info.lineno,
              "could not retrieve filters from the database")
        return []

    for filter_file in filter_list:
        # remove .py extension for import_module function
        formatted_file_name = filter_file[0].replace(".py", "")

        try:
            # import the filter file from Filter directory
            imported_mod = import_module(f"Client.Reasoning_Engine.Filter.{formatted_file_name}")

        except:
            frame_info = getframeinfo(currentframe())
            print("[ERROR]: in", frame_info.filename, "in line:", frame_info.lineno,
                  "could not import filter: ", formatted_file_name)
            continue

        try:
            # extend necessary mode list by calling execute_filter function of imported filter file
            filter_function_entry_point = getattr(imported_mod, "execute_filter")
            necessary_modes_list.extend(filter_function_entry_point(received_context_information))

        except:
            frame_info = getframeinfo(currentframe())
            print("[ERROR]: in", frame_info.filename, "in line:", frame_info.lineno,
                  "could not execute filter: ", formatted_file_name)
            continue

    # return necessary_modes_list that contains no duplicates
    return list(set(necessary_modes_list))


def calculate_best_combination(calculated_asset, sum_of_max_asset, received_information):
    necessary_modes = apply_filters(received_information)

    # determine the best combination (with the highest value and lowest cost) by calculating the cost limit
    max_combination_cost = database_connector.get_max_combination_cost()
    combination_cost_limit = math.floor(calculated_asset / sum_of_max_asset * max_combination_cost)
    print("combination_cost_limit: ", combination_cost_limit, "out of ", max_combination_cost)
    best_affordable_combination = database_connector.get_best_affordable_combination(combination_cost_limit, necessary_modes)

    return best_affordable_combination
