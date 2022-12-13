import ast
import sqlite3
import Client.context_information_database as cid

#Testdata
context_information_dictionary = {"identifier": 268, "battery_state": 47, "charging_station_distance": 42.8, "location": 41, "elicitation_date": "2022-12-13T19:47:40.996571"}

db_cursor = cid.get_cursor()

db_cursor.execute("SELECT * FROM context_information_keystore")
keystorelist = db_cursor.fetchall()
keystoredict = {}
for i in keystorelist:
    keystoredict[i[0]] = i[1:]
weightsum = 0
for key in context_information_dictionary.keys():
    if key not in keystoredict.keys():
        continue
    max = keystoredict[key][1]
    min = keystoredict[key][0]
    good = keystoredict[key][2]
    weight = keystoredict[key][3]
    seperator = ast.literal_eval(keystoredict[key][4])  # .strip('][').split(', ')

    # normalized = (value - min) / (max - min )
    # normalized = ((context_information_dictionary[key] - keystoredict[key][1])/ (keystoredict[key][2] - keystoredict[key][1]))
    normalized = (context_information_dictionary[key] - min) / (max - min)
    middle = (max - min)  / 2
    if good > middle:
        weightsum += (1 - normalized) * weight
    else:
        weightsum += normalized * weight

    print(weightsum)