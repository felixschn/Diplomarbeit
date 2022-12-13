import random


def get_country_evaluation() -> dict:
    with open('country_list.txt', 'r') as file:
        countries = file.read().splitlines()

    random.shuffle(countries)

    evaluation_dict = {}
    count = 1
    for eval in countries:
        evaluation_dict[count] = eval
        count = count + 1

    return evaluation_dict
