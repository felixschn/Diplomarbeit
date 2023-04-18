import Client.Reasoning_Engine.Context_Model.Weight_Calculation.weight_calculation_standard as weight_calculation_standard
import Client.Reasoning_Engine.Context_Model.Weight_Calculation.weights as weight_file


def weight_calculation_distance(evaluation_dict) -> float:
    # charge                                                    in   %
    # weight_calculation_distance to next charging point        in   km
    # consumption                                               in kWh / 100km


    # define designated max_weight for special high-level context information derivation and neglect particular keystore weights
    weight_distance_calculation = 15
    weight_file.max_weight += weight_distance_calculation

    distance_attributes_list = ["battery_state", "battery_consumption", "trip_distance"]
    # define calculation specific context information attributes for high-level context information derivation
    weight_file.high_level_context_information_list.extend(distance_attributes_list)

    for key in evaluation_dict:
        if (key in distance_attributes_list) and set(distance_attributes_list).issubset(evaluation_dict.keys()):
            if key != distance_attributes_list[0]:
                # skip other keys so that weight is not calculated multiple times
                continue

        battery_state = evaluation_dict["battery_state"]
        battery_consumption = evaluation_dict["battery_consumption"]
        distance = evaluation_dict["trip_distance"]
        capacity = 100  # in  kWh     TODO: edit param battery capacity or transmit received_message_value
        max_reserve = 3
        min_reserve = 1
        battery_state = battery_state / 100 * capacity
        range = battery_state / battery_consumption * 100  # estimated range with current consumption

        reserve = range / distance
        # reserve >> 1.2     is good
        # 1.2 > reserve > 1  is dangerous
        # 1 > reserve        is critical

        if reserve < 1:
            print("reserve is critical")
            return 0.0  # TODO or maybe even negative numbers?

        if reserve < 1.2:
            print("reserve is dangerous")
            return (reserve - 1) * weight_distance_calculation * 0.5  # half weight because the small reserve is still critical # TODO: edit param?

        if reserve > max_reserve:
            return weight_distance_calculation

        print("reserve is good")

        return weight_calculation_standard.calculation(reserve, min_reserve, max_reserve, max_reserve, weight_distance_calculation)
