import sqlite3
from importlib import import_module
from inspect import getframeinfo, currentframe

import Client.Data_Engine.database_connector as database_connector
from Client.Reasoning_Engine.Context_Model.Rule_Set.asset_calculation_standard import asset_calculation_standard

max_sum_of_asset = 0
high_level_context_information_list = []


def asset_evaluation(received_context_information) -> tuple[float, float]:
    global max_sum_of_asset, high_level_context_information_list
    calculated_asset = 0
    max_sum_of_asset = 0
    db_cursor = database_connector.get_cursor()

    # check if any keystore information is available in the database, otherwise no calculation can be done
    keystore_list = database_connector.get_keystore_parameters()
    if not keystore_list:
        print("[Error]: the database does not contain any Keystore parameters; please send an update message")
        raise Exception

    # transform list of tuples to separate keys for better access to keystore data
    keystore_dict = {}
    for i in keystore_list:
        keystore_dict[i[0]] = i[1:]

    # omit context information received without a Keystore parameter to ignore non-processable data
    evaluation_dict = {}
    for key in keystore_dict.keys():
        if key in received_context_information.keys():
            evaluation_dict[key] = received_context_information[key]

    # retrieve and execute high-level derivation files; use standard calculation if none exist
    try:
        high_level_derivation_list = database_connector.get_high_level_derivation_files()
        if not high_level_derivation_list:
            print("[Warning]: the database, or the system, does not contain any high-level derivation files; "
                  "therefore, the standard asset calculation is used; consider sending an update message for high-level derivation")

    except sqlite3.OperationalError:
        frame_info = getframeinfo(currentframe())
        print("[ERROR]: in", frame_info.filename, "in line:", frame_info.lineno,
              "Could not retrieve high-level derivation file names; therefore, the standard weight "
              "calculation will be used")

        calculated_asset += asset_calculation_standard(evaluation_dict, keystore_dict)
        return calculated_asset, max_sum_of_asset

    for high_level_derivation_file in high_level_derivation_list:
        # remove .py extension for the import_module function
        formatted_file_name = high_level_derivation_file[0].replace('.py', '')

        try:
            # import the received high-level derivation file as a Python module
            imported_mod = import_module(f"Client.Reasoning_Engine.Context_Model.Rule_Set.{formatted_file_name}")

        except:
            frame_info = getframeinfo(currentframe())
            print("[ERROR]: in", frame_info.filename, "in line:", frame_info.lineno,
                  "could not import high-level derivation file: ", formatted_file_name)
            continue

        try:
            # add derived high-level context information to existing asset calculation
            derivation_function_entry_point = getattr(imported_mod, 'high_level_derivation')
            calculated_asset += (derivation_function_entry_point(evaluation_dict))

        except:
            frame_info = getframeinfo(currentframe())
            print("[ERROR]: in", frame_info.filename, "in line:", frame_info.lineno,
                  "could not execute high_level_derivation: ", formatted_file_name)
            continue

    calculated_asset += asset_calculation_standard(evaluation_dict, keystore_dict)

    return calculated_asset, max_sum_of_asset
