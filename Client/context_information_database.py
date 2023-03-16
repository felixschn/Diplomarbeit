import itertools
import json
import random
import re
import sqlite3
from collections import deque
from inspect import getframeinfo, currentframe
from urllib.request import pathname2url

db_connection: sqlite3.dbapi2 = None


def get_cursor():
    global db_connection
    if db_connection is None:
        db_name = 'context_information_database.sqlite'

        # https://stackoverflow.com/questions/12932607/how-to-check-if-a-sqlite3-database-exists-in-python
        # read, write, create database at given path
        db_uri = 'file:{}?mode=rwc'.format(pathname2url(db_name))
        db_connection = sqlite3.connect(db_uri, uri=True, check_same_thread=False)

    return db_connection.cursor()


# retrieve the entry with the latest date
def get_latest_date_entry(table_name) -> str:
    db_cursor = get_cursor()
    # validate if table is stored in the database; idea from: https://stackoverflow.com/questions/305378/list-of-tables-db-schema-dump-etc-using-the-python
    # -sqlite3-api/33100538#33100538
    validation_query = "SELECT name FROM sqlite_master WHERE type='table';"
    db_cursor.execute(validation_query)
    available_tables_list = [elements[0] for elements in db_cursor.fetchall()]

    if table_name not in available_tables_list:
        pass

    max_date_query = "SELECT MAX(elicitation_date) From received_context_information"
    return db_cursor.execute(max_date_query).fetchall()[0][0]


# get all the information about security mechanisms from the database
def get_security_mechanisms_information() -> list:
    db_cursor = get_cursor()
    db_query = "SELECT * FROM security_mechanisms_information"

    try:
        return db_cursor.execute(db_query).fetchall()
    except:
        frame_info = getframeinfo(currentframe())
        print("""[ERROR]: in""", frame_info.filename, "in line:", frame_info.lineno,
              """could not find security mechanism information in database""")
        return []


def get_security_mechanisms_information_name() -> list:
    db_cursor = get_cursor()
    db_query = "SELECT mechanism_name from security_mechanisms_information"

    try:
        return db_cursor.execute(db_query).fetchall()
    except:
        frame_info = getframeinfo(currentframe())
        print("""[ERROR]: in""", frame_info.filename, "in line:", frame_info.lineno,
              """could not find security mechanism information in database""")
        return []


# get all filters for the security mechanisms from the database
def get_security_mechanisms_filter() -> list:
    db_cursor = get_cursor()
    db_query = "SELECT * FROM security_mechanisms_filter"

    return db_cursor.execute(db_query).fetchall()


def update_security_mechanisms_information(mechanisms_information_update_message):
    db_cursor = get_cursor()
    # create table for security_mechanisms_information
    create_mechanisms_information_query = """CREATE TABLE if not exists security_mechanisms_information(mechanism_name, modes, mode_weights, mode_values)"""
    db_cursor.execute(create_mechanisms_information_query)

    # serialize mode_weights because SQLite can't store lists; see:
    # https://stackoverflow.com/questions/20444155/python-proper-way-to-store-list-of-strings-in-sqlite3-or-mysql
    mechanisms_information_update_message['mode_weights'] = json.dumps(mechanisms_information_update_message['mode_weights'])
    mechanisms_information_update_message['mode_values'] = json.dumps(mechanisms_information_update_message['mode_values'])

    # get the mechanism_name from the database table and check if entry already exists
    current_columns = db_cursor.execute("SELECT mechanism_name from security_mechanisms_information ").fetchall()
    # if an entry does not exist, create one
    if len(current_columns) == 0:
        pass
    # otherwise, update the existing entry
    elif mechanisms_information_update_message['mechanism_name'] in [elem[0] for elem in current_columns]:
        update_query = """UPDATE security_mechanisms_information SET modes = ?, mode_weights = ?, mode_values = ? WHERE mechanism_name = ?"""

        # get values name, mode, mode_weights, mode_values from the dict
        query_params = list(mechanisms_information_update_message.values())[:4]
        # get the name attribute and store it in a separate variable in order to match the update_query requirements, where name has to be the last parameter
        list_element = query_params[0]
        # remove the name from the list and append it at the end
        query_params = [x for x in query_params if x != list_element] + [list_element]

        db_cursor.execute(update_query, query_params)
        db_connection.commit()
        return

    insert_mechanisms_information_query = """INSERT INTO security_mechanisms_information
                                    (mechanism_name, modes, mode_weights, mode_values) 
                                    VALUES (?, ?, ?, ? )"""
    query_params = list(mechanisms_information_update_message.values())[:4]
    db_cursor.execute(insert_mechanisms_information_query, query_params)
    db_connection.commit()
    return


def get_max_weight_combination() -> int:
    db_cursor = get_cursor()
    return db_cursor.execute("SELECT MAX(weight) FROM security_mechanisms_combination").fetchone()[0]


def get_best_affordable_combination(combination_weight_limit, necessary_modes):
    db_cursor = get_cursor()

    # create a query to retrieve the security mechanism combination with the highest received_message_value and lowest weight depending on several conditions like weight or
    # necessary modes
    combination_query = 'SELECT * from ('
    combination_query_max_value = 'SELECT * from security_mechanisms_combination WHERE received_message_value = (SELECT MAX(received_message_value) from security_mechanisms_combination WHERE weight <= ?'
    combination_query_min_value = 'WHERE weight = (SELECT MIN(weight) from ('

    # add the necessary modes to the combination_query_max_value
    for mode in necessary_modes:
        # separate mode name and number
        mode_name = "".join((re.findall(r"[a-zA-Z]+", mode)))
        mode_number = "".join((re.findall(r"\d+", mode)))
        # append mode name and number to the query
        combination_query_max_value += f" AND {mode_name} >= {mode_number}"
    # add a closing bracket to the combination_query
    combination_query_max_value += '))'
    # merge all the sub queries
    combination_query += combination_query_max_value + ' ' + combination_query_min_value + combination_query_max_value + ')'

    affordable_combinations = db_cursor.execute(combination_query, (combination_weight_limit, combination_weight_limit)).fetchall()

    # check if affordable_combinations is empty
    if not affordable_combinations:
        # query to find the combination with the highest received_message_value and lowest weight without considering necessary modes because there was no affordable
        # option when considering all necessary modes
        alternative_combination_query = """SELECT * from (SELECT * from security_mechanisms_combination WHERE received_message_value = 
                                        (SELECT MAX(received_message_value) from security_mechanisms_combination WHERE weight <= ?)) WHERE weight = 
                                        (SELECT MIN(weight) from (SELECT * from security_mechanisms_combination WHERE received_message_value = 
                                        (SELECT MAX(received_message_value) from security_mechanisms_combination WHERE weight <= ?)))"""
        affordable_combinations = db_cursor.execute(alternative_combination_query, (combination_weight_limit, combination_weight_limit,)).fetchall()

    elif len(affordable_combinations) > 1:
        # TODO think about what to do in case both the weight and received_message_value of the chosen combinations are equal --> Normally, the program should have chosen
        #  equally strong mechanism combinations, so which combination the program chooses is unimportant.

        # return one of the combinations randomly
        return affordable_combinations[random.randint(0, len(affordable_combinations) - 1)][0]

    return affordable_combinations[0][0]


def create_security_mechanism_combinations():
    db_cursor = get_cursor()

    # delete existing security_mechanism_combination table
    db_cursor.execute("DROP TABLE if exists security_mechanisms_combination")

    # create table security_mechanisms_combination with predefined (combination, weight, received_message_value) and dynmaic columns (available security mechanism columns)
    security_mechanisms_name_deque = deque(["combination", "weight", "value"])
    security_mechanisms_name_deque.extend(deque((itertools.chain(*get_security_mechanisms_information_name()))))
    create_combination_query = "CREATE TABLE if not exists security_mechanisms_combination(%s)" % ", ".join(security_mechanisms_name_deque)
    db_cursor.execute(create_combination_query)

    # get the current security mechanism information from the database and initialize the necessary dictionaries to store modes and their costs
    security_mechanisms_list = get_security_mechanisms_information()
    security_modes = {}
    security_mode_weight_costs = {}

    # check if the database returned any security mechanism information
    if not security_mechanisms_list:
        frame_info = getframeinfo(currentframe())
        print("""[ERROR]: in""", frame_info.filename, "in line:", frame_info.lineno,
              """retireved no security mechanisms information from database""")
        return

    # loop through all entries, create a key for the dict from the mechanism_name, and add all the modes to a list as values of the dict
    for (mechanism_name, modes, mode_weights, mode_values) in security_mechanisms_list:
        # deserialize mode_weights and mode_values from database table security_mechanism_information
        mode_weights = json.loads(mode_weights)
        mode_values = json.loads(mode_values)
        # create a dict of security mode lists with dynamic names as their keys
        security_modes[f"{mechanism_name}_list"] = []

        for mode in range(modes):
            try:
                security_modes[f"{mechanism_name}_list"].append(mechanism_name + f"{mode}")
                # create dictionaries with the security mechanism mode as the keys and the mode_weight and mode_value costs as the received_message_value
                security_mode_weight_costs[mechanism_name + f"{mode}"] = (mode_weights[mode], mode_values[mode])

            except IndexError:
                frame_info = getframeinfo(currentframe())
                print("""[ERROR]: in""", frame_info.filename, "in line:", frame_info.lineno,
                      """creating security_mode or security_mode_list failed; create_all_possible_permutations is not possible\n fix security mechanism information through update message""")
                return

    # get the values (which are the lists) from the dict through unzipping
    _, available_security_mechanisms = zip(*security_modes.items())

    # calculate all possible permutations of the elements of the lists
    # container_list = [sorted(set(v)) for v in itertools.product(*values)]
    container_list = [v for v in itertools.product(*available_security_mechanisms)]

    # create adaptive query with respect to the total amount of keys in context_information_values dict
    insert_query_string = "INSERT INTO security_mechanisms_combination("

    # retrieve all keys from dict and write it into query; add necessary ',' to the end
    insert_query_string += ",".join(security_mechanisms_name_deque)

    # append needed sql statement VALUES
    insert_query_string += ") VALUES ("

    # add placeholder ? for every key in context_information_values; add necessary ',' to the end
    insert_query_string += len(security_mechanisms_name_deque) * '?,'

    # last ? should not have a ',' in order to have a valid query; close query string with ')'
    insert_query_string = insert_query_string[:-1] + ')'

    # add items to database, commit and close
    # db_cursor.execute(insert_query_string)

    global combination_cost
    for list_element in container_list:
        sum_weights = 0
        sum_values = 0
        mode_number_list = []
        for elem in list_element:
            sum_weights += security_mode_weight_costs[elem][0]
            sum_values += security_mode_weight_costs[elem][1]
            mode_number_list.append(int("".join(re.findall(r"\d+", elem))))
        # combination_cost[list_element] = (sum_weights, sum_values)
        insert_deque = deque([str(list_element), sum_weights, sum_values])
        insert_deque.extend(mode_number_list)
        db_cursor.execute(insert_query_string, insert_deque)
    db_connection.commit()

    # TODO store in database: combination: list_element; weight = sum_weights; received_message_value = sum_values; --> all mechanisms from list_element with only the integer

    # sort dict after values to get an order of the security mechanism combination costs
    # combination_cost = dict(sorted(combination_cost.items(), key=lambda item: item[1]))


def update_security_mechanisms_filter(filename):
    db_cursor = get_cursor()

    create_filter_query = """CREATE TABLE if not exists security_mechanisms_filter(filter_name)"""
    db_cursor.execute(create_filter_query)

    current_columns = db_cursor.execute("SELECT filter_name FROM security_mechanisms_filter").fetchall()
    if len(current_columns) == 0:
        pass

    elif filename in [elem[0] for elem in current_columns]:
        update_query = """UPDATE security_mechanisms_filter SET filter_name = ?"""

        query_params = filename
        db_cursor.execute(update_query, (query_params,))
        db_connection.commit()
        return

    insert_filter_query = """INSERT INTO security_mechanisms_filter (filter_name) VALUES (?)"""
    query_params = filename
    db_cursor.execute(insert_filter_query, (query_params,))
    db_connection.commit()
    return


def update_context_information_keystore(keystore_update_message):
    # global db_connection
    db_cursor = get_cursor()

    # create db table if not already present
    create_keystore_query = """CREATE TABLE if not exists context_information_keystore(keyname,minimum_value, maximum_value,desirable_value,weight,separatorlist)"""
    db_cursor.execute(create_keystore_query)

    # fetch all table entries to prevent keystore attribute duplicates
    current_columns = db_cursor.execute("SELECT keyname FROM context_information_keystore").fetchall()
    if len(current_columns) == 0:
        pass

    # check if keyname is in list, therefore get first elements in a list of tuples
    elif keystore_update_message['keyname'] in [elem[0] for elem in current_columns]:
        update_query = """UPDATE context_information_keystore SET 
                        minimum_value = ?,
                        maximum_value = ?,
                        desirable_value = ?,
                        weight = ?,
                        separatorlist = ? WHERE keyname = ?"""

        query_params = list(keystore_update_message.values())[2:7]
        query_params.append('battery_consumption')
        db_cursor.execute(update_query, query_params)
        db_connection.commit()
        return

    insert_keystore_query = """INSERT INTO context_information_keystore(keyname,minimum_value,maximum_value,desirable_value,weight,separatorlist) 
                        VALUES (?,?,?,?,?,?)"""

    db_cursor.execute(insert_keystore_query, list(keystore_update_message.values())[1:7])
    db_connection.commit()


def update_context_information(context_information_message):
    global db_connection
    db_cursor = get_cursor()

    # create table and make keys from dict to new columns
    db_cursor.execute("CREATE TABLE if not exists received_context_information(%s)" % ", ".join(context_information_message.keys()))

    # add new column to table if table_attributes comes with additional non-existing values
    # sqlite alter table command has no if not exists functionality therefore the command is wrapped in try/except
    for item in context_information_message:
        try:
            db_cursor.execute("ALTER TABLE received_context_information ADD COLUMN '%s'" % item)
        except sqlite3.OperationalError:
            # print("table column",item,"already exist")
            pass

    # create adaptive query with respect to the total amount of keys in context_information_values dict
    insert_query_string = "INSERT INTO received_context_information("

    # retrieve all keys from dict and write it into query; add necessary ',' to the end
    insert_query_string += ",".join(context_information_message.keys())

    # append needed sql statement VALUES
    insert_query_string += ") VALUES ("

    # add placeholder ? for every key in context_information_values; add necessary ',' to the end
    insert_query_string += len(context_information_message.keys()) * '?,'

    # last ? should not have a ',' in order to have a valid query; close query string with ')'
    insert_query_string = insert_query_string[:-1] + ')'

    # add items to database, commit and close
    db_cursor.execute(insert_query_string, list(context_information_message.values()))
    db_connection.commit()
    db_cursor.close()
