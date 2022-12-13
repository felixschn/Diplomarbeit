import sqlite3
import Client.context_information_database as cid

db_cursor = cid.get_cursor()

db_cursor.execute("SELECT * FROM context_information_keystore")
context_information_dictionary = db_cursor.fetchall()
# (min & max value
keystore = {"battery_state":[100, 0, 15], "charging_station_distance":[0, 1000, 0.2]}


weight = 1_000
for key in context_information_dictionary.keys():
    if key not in keystore:
        continue
    middle = 0.5 * (keystore[key][1] - keystore[key][0])
    weight -= context_information_dictionary[key] / middle * keystore[key][2]
    print(weight)