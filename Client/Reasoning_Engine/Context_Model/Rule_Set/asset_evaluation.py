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
    # create database cursor
    db_cursor = database_connector.get_cursor()

    # check if any keystore information is available in the database, otherwise no calculation can be done
    try:
        # fetch all rows from database table and store them into keystore_list
        keystore_query = "SELECT * FROM context_information_keystore"
        keystore_list = db_cursor.execute(keystore_query).fetchall()

    except sqlite3.OperationalError:
        frame_info = getframeinfo(currentframe())
        print("\n[ERROR]: in ", frame_info.filename, "in line:", frame_info.lineno,
              """Database does not contain keystore table;\ncontext information cannot be processed without keystore information; waiting for keystore update 
              message\n""")
        return

    # conversion of the returned database Keystore list to dict
    keystore_dict = {}
    for i in keystore_list:
        keystore_dict[i[0]] = i[1:]

    # omit context information received without a Keystore parameter to ignore non-processable data
    evaluation_dict = {}
    for key in received_context_information.keys():
        if key in keystore_dict:
            evaluation_dict[key] = received_context_information[key]

    try:
        derivation_files_query = "SELECT * FROM high_level_derivation_files"
        high_level_derivation_list = db_cursor.execute(derivation_files_query).fetchall()

    except sqlite3.OperationalError:
        frame_info = getframeinfo(currentframe())
        print("\n[ERROR]: in", frame_info.filename, "in line:", frame_info.lineno, "Database does not contain high-level derivation files;\nStandard weight "
                                                                                   "calculation will be used;\n")
        calculated_asset += asset_calculation_standard(evaluation_dict, keystore_dict)
        return calculated_asset, max_sum_of_asset

    for high_level_derivation_file in high_level_derivation_list:
        formatted_file_name = high_level_derivation_file[0].replace('.py', '')

        try:
            # import received source code as python module
            imported_mod = import_module(f"Client.Reasoning_Engine.Context_Model.Rule_Set.{formatted_file_name}")

        except:
            frame_info = getframeinfo(currentframe())
            print("[ERROR]: in", frame_info.filename, "in line:", frame_info.lineno,
                  "could not import high-level derivation file: ", formatted_file_name)
            continue

        try:
            # loading and calling high-level_derivation function to calculate weight
            call_high_level_derivation = getattr(imported_mod, 'high_level_derivation')
            calculated_asset += (call_high_level_derivation(evaluation_dict))

        except:
            frame_info = getframeinfo(currentframe())
            print("[ERROR]: in", frame_info.filename, "in line:", frame_info.lineno,
                  "could not call high_level_derivation: ", formatted_file_name)
            continue

    calculated_asset += asset_calculation_standard(evaluation_dict, keystore_dict)

    return calculated_asset, max_sum_of_asset
