import itertools
import json
from inspect import getframeinfo, currentframe

import Client.Countries.country_evaluation as country_evaluation
import context_information_database

combination_cost = {}


# function to create all possible permutations of all security mechanisms
def create_all_possible_permutations(context_information_dict):
    # get all security mechanism information entries from database
    security_mechanisms_list = context_information_database.get_security_mechanisms_information()
    security_modes = {}
    security_mode_costs = {}
    # loop through all entries, create a key for the dict from the mechanism_name, and add all the modes to a list as
    # values of the dict
    for (mechanism_name, modes, mode_values) in security_mechanisms_list:
        # deserialize mode_values from database table security_mechanism_information
        mode_values = json.loads(mode_values)
        # create a list of security modes with dynamic names
        security_modes[f"{mechanism_name}_list"] = []
        for mode in range(modes):
            try:
                security_modes[f"{mechanism_name}_list"].append(mechanism_name + f"{mode}")

                # create a dictionary with the security mechanism mode as the key and the cost as the value
                security_mode_costs[mechanism_name + f"{mode}"] = mode_values[mode]

            except IndexError:
                frame_info = getframeinfo(currentframe())
                print("""[ERROR]: in""", frame_info.filename, "in line:", frame_info.lineno,
                      """creating security_mode or security_mode_list failed; create_all_possible_permutations is not possible\n fix security mechanism information through update message""")
                return

    # get the values (which are the lists) from the dict through unzipping
    _, values = zip(*security_modes.items())

    # calculate all possible permutations of the elements of the lists
    # container_list = [sorted(set(v)) for v in itertools.product(*values)]
    container_list = [v for v in itertools.product(*values)]

    global combination_cost
    for list_element in container_list:
        sum = 0
        for elem in list_element:
            sum = sum + security_mode_costs[elem]
        combination_cost[list_element] = sum

    # sort dict after values to get an order of the security mechanism combination costs
    combination_cost = dict(sorted(combination_cost.items(), key=lambda item: item[1]))

    # TODO create the funtionality to send a update message with different information about reducing the modes, i.e. if car is located in dangerous country
    #  then only specific firewall combination can be choosen; this has to be dynamic --> call it filter and give information which modes has to be deployed

    # compare the received country code with the list of the existing countries and compare the particular one with a list of malicious nations
    if country_evaluation.get_country_code(context_information_dict["location"]) in country_evaluation.get_malicious_countries():
        # TODO has to be dynamic
        print("dangerous location found!")
        fwl.remove('fw0')
        fwl.remove('fw1')
        idl.remove('id0')
        idl.remove('id1')
        acl.remove('ac0')
        acl.remove('ac1')
        acl.remove('ac2')

    return combination_cost.keys()


# TODO function where filter reduces amount of permutations with respect to specific context inforamtion

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
