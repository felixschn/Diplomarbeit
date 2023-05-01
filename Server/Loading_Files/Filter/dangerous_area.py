def execute_filter(available_security_mechanisms_list, evaluation_dict) -> list:
    necessary_modes = ["vpn1"]
    dangerous_area_corner_1 = (51.037275, 13.769544)
    dangerous_area_corner_2 = (51.043342, 13.747986)
    current_latitude, current_longitude = evaluation_dict["location"]

    if dangerous_area_corner_1[0] <= current_latitude:
        if current_latitude <= dangerous_area_corner_2[0]:
            if dangerous_area_corner_2[1] <= current_longitude:
                if current_longitude <= dangerous_area_corner_1[1]:
                    print(f"Dangerous Area Filter activated: ", necessary_modes)
                    return necessary_modes

    return []
