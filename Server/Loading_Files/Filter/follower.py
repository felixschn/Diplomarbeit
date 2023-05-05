def execute_filter(evaluation_dict) -> list:
    necessary_modes = ["fw3"]

    if evaluation_dict["follower"] > 0:
        if evaluation_dict["follower"] < 50:
            print(f"Follower Filter activated: ", necessary_modes)
            return necessary_modes

    return []