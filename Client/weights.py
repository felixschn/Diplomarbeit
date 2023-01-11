import ast
import math
import sqlite3
from bisect import bisect_left

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

    # check if any keystore information is available in the database, otherwise no calculation can be done
    try:
        # fetch all rows from database table and store them into keystore_list
        db_cursor.execute("SELECT * FROM context_information_keystore")
        keystore_list = db_cursor.fetchall()

    except sqlite3.OperationalError:
        print("""\n[ERROR]:database doesn't contain keystore table; context information cannot be processed without keystore information;
            waiting for keystore update message\n""")
        # TODO check if this return value is correct
        return None, None

    keystore_dict = {}
    for i in keystore_list:
        keystore_dict[i[0]] = i[1:]

    # define weight parameters for calculation and evaluation
    weight_sum = 0
    max_weight = 0

    # check if the attributes of the received context information are known database entries; otherwise, the key will be skipped because no calculation can
    # be done
    for key in context_information_dict.keys():
        if key not in keystore_dict.keys():
            continue

        # retrieve weight from the keystore entry in the database
        weight = keystore_dict[key][3]

        # TODO:  further evaluation take string form database with separators and build list out of string
        separator = ast.literal_eval(keystore_dict[key][4])  # .strip('][').split(', ')

        # specific calculation of relationship between battery_state, charging_station_distance and battery_consumption
        distance_keys = ['battery_state', 'charging_station_distance', 'battery_consumption']
        maximum_value = keystore_dict[key][1]
        minimum_value = keystore_dict[key][0]
        desirable_value = keystore_dict[key][2]

        if (key in distance_keys) and set(distance_keys).issubset(context_information_dict.keys()):
            if key != distance_keys[0]:
                # skip other keys so that weight is not calculated multiple times
                continue

            # calculate weight for triple and add it to the weight_sum
            weight_sum += distance(context_information_dict['battery_state'],
                                   context_information_dict['charging_station_distance'],
                                   context_information_dict['battery_consumption'], weight, minimum_value, maximum_value, desirable_value)

            # TODO is this really the right way to get the maximum weight when triple state, consumption and distance have different weights (in the db)
            max_weight += weight
            pass

        else:
            # if the key is not one of the three listed above, the weight will be calculated or normalized using their specific parameters
            weight_sum += normalized_weight(context_information_dict[key], minimum_value, maximum_value, desirable_value, weight)
            max_weight += weight

    return weight_sum, max_weight


def normalized_weight(value, minimum_value, maximum_value, desirable_value, weight) -> float:
    # normalizing data because of different values (due to units e.g. 1000km distance vs 75% battery)
    normalized = (value - minimum_value) / (maximum_value - minimum_value)

    # only to see if the value is more on the left or on the right of the scale
    middle = (maximum_value - minimum_value) / 2
    if desirable_value > middle:
        return normalized * weight
    else:
        # when left then subtract normalized value from 1
        return (1 - normalized) * weight


def distance(charge, distance, consumption, weight, minimum_value, maximum_value, desirable_value) -> float:
    # charge                              in   %
    # distance to next charging point     in   km
    # consumption                         in   kWh / 100km

    capacity = 100  # in  kWh     TODO: edit param battery capacity or transmit value
    max_reserve = 3
    min_reserve = 1
    charge = charge / 100 * capacity
    range = charge / consumption * 100  # estimated range with current consumption

    reserve = range / distance
    # reserve >> 1.2     is good
    # 1.2 > reserve > 1  is dangerous
    # 1 > reserve        is critical

    if reserve < 1:
        print("reserve is critical")
        return 0.0  # TODO or maybe even negative numbers?

    if reserve < 1.2:
        print("reserve is dangerous")
        return (reserve - 1) * weight * 0.5  # half weight because the small reserve is still critical # TODO: edit param?

    if reserve > max_reserve:
        return weight

    print("reserve is good")
    return normalized_weight(reserve, min_reserve, max_reserve, max_reserve, weight)


def choose_option(weight, max_weight, options):
    # easiest way
    # return options[math.ceil(weight / max_weight) * len(options)]

    # TODO check if calculation is correct when potential order list is small because of a dangerous country in the
    #  received data --> when list is small it is hard to reach a min_lvl greater then 1, so most of the time the
    #  output will be 0

    # calculate the resulted weight's position; a set of possible options is portioned on a scale, i.e., if only a subset of the possible options is
    # available, they are divided on the scale with their specific values.That means, if the min_lvl is, for example, 7, and there are only 4 options with
    # values greater than 7, the position will be 0
    min_lvl = math.ceil(weight / max_weight * len(Client.reasoning.order))
    pos = bisect_left(options, min_lvl, key=lambda x: Client.reasoning.order[x])
    print("position: ", pos)
    return options[pos]  # TODO: testing --> IndexError: list index out of range
