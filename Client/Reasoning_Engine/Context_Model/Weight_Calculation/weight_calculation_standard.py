import Client.Reasoning_Engine.Context_Model.Weight_Calculation.weights as weight_file


def weight_calculation_normalised(received_message_value, minimum_value, maximum_value, desirable_value, weight) -> float:
    # calculate mean to check if the desirable_value inclines to the left or on the right of the scale
    mean_value = (maximum_value - minimum_value) / 2

    if desirable_value > mean_value:
        # desirable_value strives to the maximum_value
        if received_message_value >= desirable_value:
            return weight

        normalized = (received_message_value - minimum_value) / (desirable_value - minimum_value)
        return normalized * weight

    else:
        # desirable_ value strives to the minimum_value
        if received_message_value < desirable_value:
            return weight

        normalized = (received_message_value - desirable_value) / (maximum_value - desirable_value)
        return (1 - normalized) * weight


def weight_calculation_standard(evaluation_dict, keystore_dict) -> float:
    weight_sum = 0

    for key in evaluation_dict:
        if key in weight_file.high_level_context_information_list:
            continue

        # extract Keystore parameters for each key
        minimum_value = keystore_dict[key][0]
        maximum_value = keystore_dict[key][1]
        desirable_value = keystore_dict[key][2]
        context_information_weight = keystore_dict[key][3]

        weight_sum += weight_calculation_normalised(evaluation_dict[key], minimum_value, maximum_value, desirable_value, context_information_weight)
        weight_file.max_weight += context_information_weight

    return weight_sum
