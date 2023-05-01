import sqlite3
from importlib import import_module
from inspect import getframeinfo, currentframe

import Client.Data_Engine.context_information_database as context_information_database
import Client.Reasoning_Engine.Context_Model.Weight_Calculation.weight_calculation_standard as weight_standard

# high weight means   option for more security features
# low weight means    not enough power or threads for sec features

# every calculation should return values between 0 and 1 times weight


# test data
# context_information_dictionary = {"identifier": 268, "battery_state": 50, "charging_station_distance": 500,
#                                  "location": 41, "elicitation_date": "2022-12-13T19:47:40.996571"}
max_weight = 0
high_level_context_information_list = []


def evaluate_weight(context_information_dict) -> tuple[float, float]:
    # create database cursor
    global max_weight, high_level_context_information_list
    db_cursor = context_information_database.get_cursor()
    calculated_weight = 0
    max_weight = 0

    # check if any keystore information is available in the database, otherwise no calculation can be done
    try:
        # fetch all rows from database table and store them into keystore_list
        keystore_query = "SELECT * FROM context_information_keystore"
        keystore_list = db_cursor.execute(keystore_query).fetchall()


    except sqlite3.OperationalError:
        frame_info = getframeinfo(currentframe())
        print("""\n[ERROR]: in """, frame_info.filename, "in line:", frame_info.lineno, """Database does not contain keystore table;\ncontext information cannot be processed without keystore information;\n
            waiting for keystore update message\n""")
        # TODO check if this return received_message_value is correct
        return (None, None)

    keystore_dict = {}
    for i in keystore_list:
        keystore_dict[i[0]] = i[1:]

    evaluation_dict = {}
    for key in context_information_dict.keys():
        if key in keystore_dict:
            evaluation_dict[key] = context_information_dict[key]

    try:
        weight_files_query = "SELECT * FROM weight_calculation_files"
        weight_files_list = db_cursor.execute(weight_files_query).fetchall()

    except sqlite3.OperationalError:
        frame_info = getframeinfo(currentframe())
        print("""\n[ERROR]: in """, frame_info.filename, "in line:", frame_info.lineno,
              """Database does not contain weight calulation files;\nStandard weight calculation will be used;\n""")
        calculated_weight += weight_standard.weight_standard(evaluation_dict, keystore_dict)
        return calculated_weight, max_weight

    for weight_calculation_file in weight_files_list:
        formatted_file_name = weight_calculation_file[0].replace('.py', '')

        # try to import the filter_file from Filter directory
        try:
            imported_mod = import_module(f"Client.Reasoning_Engine.Context_Model.Weight_Calculation.{formatted_file_name}")

        except Exception as e:
            # TODO monitor the behavior of the program because sometimes an error occurs (maybe the function can't import the module because the filter file gets overwritten by an update message)
            print(e)
            continue

        # try to import 'execute_filter' function from filter_file
        try:
            call_weight_calculation = getattr(imported_mod, 'weight_calculation_distance')
            # merge the returned list of the filter files to the necessary_modes_list
            calculated_weight += (call_weight_calculation(evaluation_dict))
        except:
            print("""some of the files in the Filter directory aren't usable filters""")
            continue

    calculated_weight += weight_standard.weight_standard(evaluation_dict, keystore_dict)

    return calculated_weight, max_weight
