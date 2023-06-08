def execute_filter(evaluation_dict) -> list:
    necessary_modes = ["vpn1"]
    # defining coordinates for the dangerous area in the Sumo map
    dangerous_area_corner_1 = (51.037275, 13.769544)
    dangerous_area_corner_2 = (51.043342, 13.747986)
    current_latitude, current_longitude = evaluation_dict["location"]

    # check if the vehicle is in the dangerous area
    if dangerous_area_corner_1[0] <= current_latitude <= dangerous_area_corner_2[0]:
        if dangerous_area_corner_2[1] <= current_longitude <= dangerous_area_corner_1[1]:
            print(f"Dangerous Area Filter activated: ".ljust(33), necessary_modes)
            return necessary_modes

    return []
