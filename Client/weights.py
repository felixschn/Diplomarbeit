import ast

import Client.context_information_database as cid


# test data
# context_information_dictionary = {"identifier": 268, "battery_state": 50, "charging_station_distance": 500,
#                                  "location": 41, "elicitation_date": "2022-12-13T19:47:40.996571"}


def calculate_weights(context_information_dictionary) -> float:
    # create database cursor
    db_cursor = cid.get_cursor()

    # fetch all rows from database table and store them into keystore_list
    db_cursor.execute("SELECT * FROM context_information_keystore")
    keystore_list = db_cursor.fetchall()

    keystore_dict = {}
    for i in keystore_list:
        keystore_dict[i[0]] = i[1:]

    # calculate weights for evaluation
    weight_sum = 0
    for key in context_information_dictionary.keys():
        if key not in keystore_dict.keys():
            continue
        max = keystore_dict[key][1]
        min = keystore_dict[key][0]
        good = keystore_dict[key][2]
        weight = keystore_dict[key][3]

        # TODO:  further evaluation take string form database with seperators and build list out of string
        seperator = ast.literal_eval(keystore_dict[key][4])  # .strip('][').split(', ')

        # normalizing data because of different values (due to units e.g. 1000km distance vs 75% battery)
        # normalized = (value - min) / (max - min )
        # normalized = ((context_information_dictionary[key] - keystoredict[key][1])/ (keystoredict[key][2] - keystoredict[key][1]))
        normalized = (context_information_dictionary[key] - min) / (max - min)
        middle = (max - min) / 2

        if good > middle:
            weight_sum += (1 - normalized) * weight
        else:
            weight_sum += normalized * weight

        print(weight_sum)

    return weight_sum
