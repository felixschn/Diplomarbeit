from inspect import getframeinfo, currentframe

import Client.Reasoning_Engine.Context_Model.Weight_Calculation.asset_calculation_standard as weight_calculation_standard
import Client.Reasoning_Engine.Context_Model.Weight_Calculation.asset_evaluation as weight_file


def high_level_derivation(evaluation_dict) -> float:
    battery_surplus_attributes_list = ["battery_state", "battery_consumption", "trip_distance"]

    # define calculation-specific context information attributes for high-level context information derivation
    if not set(battery_surplus_attributes_list).issubset(evaluation_dict.keys()):
        frame_info = getframeinfo(currentframe())
        print("""[ERROR]: in""", frame_info.filename, "in line:", frame_info.lineno,
              """missing low-level context information for calculating battery surplus""")
        return 0

    # add required low-level context information to list to ignore them in standard weight calculation
    weight_file.high_level_context_information_list.extend(battery_surplus_attributes_list)

    # battery_state                     in   %
    # battery consumption               in kWh / 100km
    # trip_distance                     in   km
    battery_state = evaluation_dict["battery_state"]
    battery_consumption = evaluation_dict["battery_consumption"]
    trip_distance = evaluation_dict["trip_distance"]

    # define Keystore parameters for high-level context information of battery surplus
    weight_battery_surplus = 15
    weight_file.max_sum_of_asset += weight_battery_surplus
    max_surplus = 2
    min_surplus = 0

    range = battery_state / battery_consumption * 100  # estimated range with current consumption
    battery_surplus = range / trip_distance - 1

    # battery_surplus >> 0.2     is good
    # 0.2 > battery_surplus > 0  is dangerous
    # 0 > battery_surplus        is critical
    if battery_surplus < 0:
        print("battery_surplus is critical")
        return 0.0

    if battery_surplus < 0.2:
        print("battery_surplus is dangerous")
        # half weight because the small battery_surplus is still critical
        return battery_surplus * weight_battery_surplus * 0.5

    if battery_surplus > max_surplus:
        return weight_battery_surplus

    print("battery_surplus is good")

    # return battery_surplus with required Keystore Parameter
    return weight_calculation_standard.asset_calculation(battery_surplus, min_surplus, max_surplus, max_surplus, weight_battery_surplus)
