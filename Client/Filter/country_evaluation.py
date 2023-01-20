import json


def get_country_code(received_contry_code) -> str:
    # open text file with list of country names
    with open('Countries/country_list.txt', 'r') as file:
        countries = file.read().splitlines()

    # create dict out of read names with increasing numbers as keys
    evaluation_dict = {}
    count = 1
    for eval in countries:
        evaluation_dict[count] = eval
        count = count + 1

    return evaluation_dict[received_contry_code]


def get_malicious_countries() -> list:
    with open('Countries/malicious_countries.txt', 'r') as file:
        return file.read().splitlines()


def execute_filter(available_security_mechanisms, context_information_dict) -> list:
    # TODO change layout --> store necessary modes not in database but in file instead, which allows more granular decision making; also make new database
    #  table with x (in this case countries) where you can store multiple states
    necessary_modes = ["firewall1", "ids1", "ac1", "checker2"]
    # compare the received country code with the list of the existing countries and compare the particular one with a list of malicious nations
    if get_country_code(context_information_dict["location"]) in get_malicious_countries():
        return necessary_modes

    return available_security_mechanisms
