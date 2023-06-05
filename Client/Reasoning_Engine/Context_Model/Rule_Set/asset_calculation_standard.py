import Client.Reasoning_Engine.Context_Model.Rule_Set.asset_evaluation as asset_evaluation


def asset_calculation(received_message_value, minimum_value, maximum_value, desirable_value, weight) -> float:
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


def asset_calculation_standard(evaluation_dict, keystore_dict) -> float:
    asset_sum = 0

    for key in evaluation_dict:
        if key in asset_evaluation.high_level_context_information_list:
            # skip low-level information because it was already used in high-level derivation
            continue

        # extract Keystore parameters for each key
        minimum_value = keystore_dict[key][0]
        maximum_value = keystore_dict[key][1]
        desirable_value = keystore_dict[key][2]
        context_information_weight = keystore_dict[key][3]

        asset_sum += asset_calculation(evaluation_dict[key], minimum_value, maximum_value, desirable_value, context_information_weight)
        asset_evaluation.max_sum_of_asset += context_information_weight

    return asset_sum
