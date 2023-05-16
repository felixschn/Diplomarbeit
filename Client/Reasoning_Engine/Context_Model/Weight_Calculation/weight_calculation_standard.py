import Client.Reasoning_Engine.Context_Model.Weight_Calculation.weights as weight_file
def calculation(received_message_value, minimum_value, maximum_value, desirable_value, weight) -> float:
    # only to see if the received_message_value is more on the left or on the right of the scale
    mean_value = (maximum_value - minimum_value) / 2
    if desirable_value > mean_value:
        if received_message_value >= desirable_value:
            return weight
        # normalizing data because of different value units
        normalized = (received_message_value - minimum_value) / (desirable_value - minimum_value)
        return normalized * weight
    else:
        if received_message_value < desirable_value:
            return weight
        normalized = (received_message_value - desirable_value) / (maximum_value - desirable_value)
        # when left then subtract normalized received_message_value from 1
        return (1 - normalized) * weight


def weight_standard(evaluation_dict, keystore_dict) -> float:
    weight_sum = 0

    for key in evaluation_dict:
        if key in weight_file.high_level_context_information_list:
            continue
        minimum_value = keystore_dict[key][0]
        maximum_value = keystore_dict[key][1]
        desirable_value = keystore_dict[key][2]
        context_information_weight = keystore_dict[key][3]

        weight_sum += calculation(evaluation_dict[key], minimum_value, maximum_value, desirable_value, context_information_weight)
        weight_file.max_weight += context_information_weight

    return weight_sum
