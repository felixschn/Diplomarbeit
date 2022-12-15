import ast
import math
from bisect import bisect_left, bisect_right

import Client.context_information_database as cid
import Client.reasoning


# high weight means   option for more security features
# low weight means    not enough power or threads for sec features

# every calculation should return values between 0 and 1 times weight


# test data
# context_information_dictionary = {"identifier": 268, "battery_state": 50, "charging_station_distance": 500,
#                                  "location": 41, "elicitation_date": "2022-12-13T19:47:40.996571"}


def calculate_weights(context_information_dict) -> tuple[float, float]:
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
    max_weight = 0
    for key in context_information_dict.keys():
        if key not in keystore_dict.keys():
            continue

        weight = keystore_dict[key][3]
        max_weight += weight

        # TODO:  further evaluation take string form database with separators and build list out of string
        separator = ast.literal_eval(keystore_dict[key][4])  # .strip('][').split(', ')

        distance_keys = ['battery_state', 'charging_station_distance', 'battery_consumption']
        if (key in distance_keys) and set(distance_keys).issubset(context_information_dict.keys()):
            if key != distance_keys[0]:
                continue  # skip other keys so that weight is not calculated multiple times
            weight_sum += distance(context_information_dict['battery_state'],
                                   context_information_dict['charging_station_distance'],
                                   context_information_dict['battery_consumption'], weight)

            pass
        else:
            max = keystore_dict[key][1]
            min = keystore_dict[key][0]
            good = keystore_dict[key][2]
            weight_sum += normalized_weight(context_information_dict[key], min, max, good, weight)

    return weight_sum, max_weight


def normalized_weight(value, min, max, good, weight) -> float:
    # normalizing data because of different values (due to units e.g. 1000km distance vs 75% battery)
    normalized = (value - min) / (max - min)

    middle = (max - min) / 2
    if good > middle:
        return normalized * weight
    else:
        return (1 - normalized) * weight


def distance(charge, distance, consumption, weight) -> float:
    # charge                              in   %
    # distance to next charging point     in   km
    # consumption                         in   kWh / 100km

    capacity = 100  # in  kWh     TODO: edit param battery capacity or transmit value
    charge = charge * capacity
    range = charge / consumption * 100  # estimated range with current consumption

    reserve = range / distance
    # reserve >> 1.2     is good
    # 1.2 > reserve > 1  is dangerous
    # 1 > reserve        is catastrophic

    if reserve < 1:
        return 0.0  # TODO or maybe even negative numbers?

    if reserve < 1.2:
        return (reserve - 1) * weight * 0.5  # half weight because the small reserve is still critical # TODO: edit param?

    return normalized_weight(reserve, 1, 50, 50, weight)


def choose_option(weight, max_weight, options):
    # easiest way
    # return options[math.ceil(weight / max_weight) * len(options)]

    min_lvl = math.ceil(weight / max_weight * len(Client.reasoning.order))

    pos = bisect_left(options, min_lvl, key=lambda x: Client.reasoning.order[x])

    return options[pos]  # TODO: testing
