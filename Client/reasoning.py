import itertools
import json
from importlib import import_module
from inspect import getframeinfo, currentframe
from inspect import getmembers, isfunction
from os import listdir
from os.path import isfile, join

import context_information_database

combination_cost = {}


def apply_filters(available_security_mechanisms, context_information_dict) -> tuple:
    try:
        filter_list = context_information_database.get_security_mechanisms_filter()

    except FileNotFoundError:
        frame_info = getframeinfo(currentframe())
        print("""[ERROR]: in""", frame_info.filename, "in line:", frame_info.lineno,
              """could not retrieve filters from the database""")
        return

    # loop through the filter files
    for filter_file in filter_list:
        # remove .py extension for import call
        formatted_file_name = filter_file[0].replace('.py', '')
        # import file from Filter directory
        imported_mod = import_module(f"Client.Filter.{formatted_file_name}")
        # get a list of all functions in the filter_file
        functions_list = getmembers(imported_mod, isfunction)
        try:
            call_filter = getattr(imported_mod, 'execute_filter')
            necessary_modes = call_filter(available_security_mechanisms, context_information_dict)
        except:
            print("""some of the files in the Filter directory aren't usable filters""")

        for mechanism in list(available_security_mechanisms):
            # loop through the particular mechanism list
            for mode_elem in mechanism:
                if mode_elem in necessary_modes:
                    break
                # remove the security modes that are not fulfilling the requirements
                available_security_mechanisms = [[elem for elem in sub if elem != mode_elem] for sub in available_security_mechanisms]

    return available_security_mechanisms


# function to create all possible permutations of all security mechanisms; returns dict.keys()
def create_all_possible_permutations(context_information_dict):
    # get all security mechanism information entries from database
    security_mechanisms_list = context_information_database.get_security_mechanisms_information()
    security_modes = {}
    security_mode_weight_costs = {}


    if not security_mechanisms_list:
        frame_info = getframeinfo(currentframe())
        print("""[ERROR]: in""", frame_info.filename, "in line:", frame_info.lineno,
              """retireved no security mechanisms information from database""")
        return
    # loop through all entries, create a key for the dict from the mechanism_name, and add all the modes to a list as
    # values of the dict
    for (mechanism_name, modes, mode_weights, mode_values) in security_mechanisms_list:
        # deserialize mode_weights and mode_values from database table security_mechanism_information
        mode_weights = json.loads(mode_weights)
        mode_values = json.loads(mode_values)
        # create a dict of security mode lists with dynamic names as their keys
        security_modes[f"{mechanism_name}_list"] = []

        for mode in range(modes):
            try:
                security_modes[f"{mechanism_name}_list"].append(mechanism_name + f"{mode}")

                # create dictionaries with the security mechanism mode as the keys and the mode_weight and mode_value costs as the value
                security_mode_weight_costs[mechanism_name + f"{mode}"] = (mode_weights[mode], mode_values[mode])

            except IndexError:
                frame_info = getframeinfo(currentframe())
                print("""[ERROR]: in""", frame_info.filename, "in line:", frame_info.lineno,
                      """creating security_mode or security_mode_list failed; create_all_possible_permutations is not possible\n fix security mechanism information through update message""")
                return

    # get the values (which are the lists) from the dict through unzipping
    _, available_security_mechanisms = zip(*security_modes.items())

    # remove modes dependent on available and applicable filters
    available_security_mechanisms = apply_filters(available_security_mechanisms, context_information_dict)

    # calculate all possible permutations of the elements of the lists
    # container_list = [sorted(set(v)) for v in itertools.product(*values)]
    container_list = [v for v in itertools.product(*available_security_mechanisms)]

    global combination_cost
    for list_element in container_list:
        sum_weight = 0
        sum_values = 0
        for elem in list_element:
            sum_weight = sum_weight + security_mode_weight_costs[elem][0]
            sum_values += security_mode_weight_costs[elem][1]
        combination_cost[list_element] = (sum_weight, sum_values)

    # sort dict after values to get an order of the security mechanism combination costs
    combination_cost = dict(sorted(combination_cost.items(), key=lambda item: item[1]))

    # TODO when applying filter, sometimes there are only costly combinations available --> so somehow we have to check if enough resources are available to choose one of the combination
    return combination_cost.keys()


# TODO function where apply_filters reduces amount of permutations with respect to specific context inforamtion

# create permutations for the hard-coded options list from above; this can be done more easily with itertools
def permute_options(fwl, idl, acl) -> list:
    possible_protection_settings = []
    for fw in range(len(fwl)):
        for id in range(len(idl)):
            for ac in range(len(acl)):
                possible_protection_settings.extend(list(zip(fwl, idl, acl)))
                acl.append(acl[0])
                acl = acl[1:]
            idl.append(idl[0])
            idl = idl[1:]
        fwl.append(fwl[0])
        fwl = fwl[1:]

    possible_protection_settings = list(dict.fromkeys(possible_protection_settings))  # remove duplicates
    possible_protection_settings = sorted(possible_protection_settings, key=lambda x: order[x])

    return possible_protection_settings
