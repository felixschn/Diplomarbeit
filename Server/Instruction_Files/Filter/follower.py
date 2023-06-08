def execute_filter(received_context_information) -> list:
    necessary_modes = ["fw3"]

    # check whether the follower is within a distance of 50 metres
    if 0 < received_context_information["follower"] < 50:
        print(f"Follower Filter activated: ".ljust(33), necessary_modes)
        return necessary_modes

    return []
