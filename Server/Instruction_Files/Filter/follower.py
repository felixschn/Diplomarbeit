def execute_filter(received_context_information) -> list:
    necessary_modes = ["fw3"]

    if 0 < received_context_information["follower"] < 50:
        print(f"Follower Filter activated: ".ljust(33), necessary_modes)
        return necessary_modes

    return []
