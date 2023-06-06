import itertools
import json
import re
import sqlite3
from collections import deque
from inspect import getframeinfo, currentframe
from pathlib import Path
from urllib.request import pathname2url

db_connection: sqlite3.dbapi2 = None

# create dynamic path declarations
path_to_project = Path(__file__).parents[2]
path_to_database = path_to_project.joinpath("Client\\Data_Engine\\system_database.sqlite")


def get_cursor():
    global db_connection
    if db_connection is None:
        db_name = str(path_to_database)
        db_uri = "file:{}?mode=rwc".format(pathname2url(db_name))
        db_connection = sqlite3.connect(db_uri, uri=True, check_same_thread=False)

    return db_connection.cursor()


def get_latest_date_entry() -> str:
    db_cursor = get_cursor()
    max_date_query = "SELECT MAX(elicitation_date) From received_context_information"

    try:
        return db_cursor.execute(max_date_query).fetchall()[0][0]

    except:
        frame_info = getframeinfo(currentframe())
        print("ERROR]: in", frame_info.filename, "in line:", frame_info.lineno,
              "could not find security mechanism information in database")
        raise Exception


# get all the information about security mechanisms from the database
def get_security_mechanism_information() -> list:
    db_cursor = get_cursor()
    db_query = "SELECT * FROM security_mechanism_information"

    try:
        return db_cursor.execute(db_query).fetchall()

    except:
        frame_info = getframeinfo(currentframe())
        print("[ERROR]: in", frame_info.filename, "in line:", frame_info.lineno,
              "could not find security mechanism information in database")
        return []


def get_security_mechanism_names():
    db_cursor = db_connection
    db_query = "SELECT mechanism_name FROM security_mechanism_information"

    try:
        return db_cursor.execute(db_query).fetchall()

    except:
        frame_info = getframeinfo(currentframe())
        print("[ERROR]: in", frame_info.filename, "in line:", frame_info.lineno,
              "could not find security mechanism names in database")
        return []


def get_filter_files() -> list:
    db_cursor = get_cursor()
    db_query = "SELECT * FROM filter_files"
    try:
        return db_cursor.execute(db_query).fetchall()

    except:
        frame_info = getframeinfo(currentframe())
        print("[ERROR]: in", frame_info.filename, "in line:", frame_info.lineno,
              "could not find filter files in database")
        return []


def update_security_mechanism_information(mechanism_information_update_message):
    db_cursor = get_cursor()

    create_table_query = "CREATE TABLE if not exists security_mechanism_information(mechanism_name, modes, mode_costs, mode_values)"
    db_cursor.execute(create_table_query)

    # serialize lists because SQLite can't store them
    mechanism_information_update_message["mode_costs"] = json.dumps(mechanism_information_update_message["mode_costs"])
    mechanism_information_update_message["mode_values"] = json.dumps(mechanism_information_update_message["mode_values"])

    mechanism_name = mechanism_information_update_message["mechanism_name"]

    # check if mechanism is already in table to update or insert
    mechanism_information_entry = db_cursor.execute("SELECT mechanism_name from security_mechanism_information WHERE mechanism_name = ?",
                                                    [mechanism_name]).fetchall()
    if len(mechanism_information_entry) == 0:
        insert_query = "INSERT INTO security_mechanism_information (mechanism_name, modes, mode_costs, mode_values) VALUES (?, ?, ?, ? )"
        query_params = list(mechanism_information_update_message.values())[:4]
        db_cursor.execute(insert_query, query_params)
        db_connection.commit()

    else:
        update_query = "UPDATE security_mechanism_information SET modes = ?, mode_costs = ?, mode_values = ? WHERE mechanism_name = ?"
        query_params = list(mechanism_information_update_message.values())
        query_params = query_params[1:4] + query_params[:1]
        db_cursor.execute(update_query, query_params)
        db_connection.commit()


def get_max_combination_cost() -> int:
    db_cursor = get_cursor()

    try:
        return db_cursor.execute("SELECT MAX(cost) FROM security_mechanism_combination").fetchone()[0]

    except:
        frame_info = getframeinfo(currentframe())
        print("[ERROR]: in", frame_info.filename, "in line:", frame_info.lineno,
              "could not retrieve combination with highest costs; calculation proceeds with 0")
        return 0


def get_best_affordable_combination(combination_cost_limit, necessary_modes):
    db_cursor = get_cursor()

    modes_for_query = ""
    # add the necessary modes to the combination_query_max_value
    for mode in necessary_modes:
        # separate mode name and number
        mode_name = "".join((re.findall(r"[a-zA-Z]+", mode)))
        mode_number = "".join((re.findall(r"\d+", mode)))
        modes_for_query += f" AND {mode_name} >= {mode_number}"
    modes_for_query += ")"

    # create a query to retrieve the security mechanism combination with the highest value and lowest cost depending on several conditions like cost or
    # necessary modes
    combination_query = "SELECT combination from ("
    combination_query_max_value = "SELECT * from security_mechanism_combination WHERE value = (SELECT MAX(value) from security_mechanism_combination" \
                                  " WHERE cost <= ?"
    combination_query_min_value = "WHERE cost = (SELECT MIN(cost) from ("

    # combine pre-defined sql queries with the dynamic necessary modes
    combination_query_max_value += modes_for_query
    combination_query_min_value += combination_query_max_value + modes_for_query

    # merge all sub strings to one final query
    combination_query += combination_query_max_value + modes_for_query + " " + combination_query_min_value + ")"

    # store query result to affordable_combination
    affordable_combinations = db_cursor.execute(combination_query, (combination_cost_limit, combination_cost_limit)).fetchall()

    # if no affordable combination with necessary modes was found;
    # neglect necessary modes and get alternative combination with the highest value and lowest cost
    if not affordable_combinations:
        print(f"No affordable combinations concerning the filters are available; proceeding with alternative combinations")

        alternative_combination_query = """SELECT combination from (SELECT * from security_mechanism_combination WHERE value = 
                                        (SELECT MAX(value) from security_mechanism_combination WHERE cost <= ?)) WHERE cost = 
                                        (SELECT MIN(cost) from (SELECT * from security_mechanism_combination WHERE value = 
                                        (SELECT MAX(value) from security_mechanism_combination WHERE cost <= ?)))"""
        affordable_combinations = db_cursor.execute(alternative_combination_query, (combination_cost_limit, combination_cost_limit,)).fetchall()

    # return always the first item of affordable_combinations; either affordable_combinations consists of a single combination or multiple combinations
    # are equally strong and, thus, it is unimportant which one is selected
    return affordable_combinations[0]


def create_security_mechanism_combinations():
    db_cursor = get_cursor()

    # delete existing security_mechanism_combination table
    db_cursor.execute("DROP TABLE if exists security_mechanism_combination")

    # create table security_mechanism_combination with predefined (combination, cost, value) and dynamic columns (available security mechanism columns)
    security_mechanisms_name_deque = deque(["combination", "cost", "value"])
    security_mechanisms_name_deque.extend(deque((itertools.chain(*get_security_mechanism_names()))))
    create_combination_query = "CREATE TABLE if not exists security_mechanism_combination(%s)" % ", ".join(security_mechanisms_name_deque)
    db_cursor.execute(create_combination_query)

    # get the current security mechanism information from the database and initialize the necessary dictionaries to store modes and their costs
    security_mechanisms_list = get_security_mechanism_information()
    security_modes = {}
    security_mode_costs = {}

    # check if the database returned any security mechanism information
    if not security_mechanisms_list:
        frame_info = getframeinfo(currentframe())
        print("[ERROR]: in", frame_info.filename, "in line:", frame_info.lineno,
              "retrieved no security mechanisms information from database")
        return

    # loop through all security_mechanisms_list entries, create a key for the dict from the mechanism_name, and add all the modes to a list as values of the dict
    for (mechanism_name, modes, mode_costs, mode_values) in security_mechanisms_list:
        # deserialize mode_costs and mode_values from database table security_mechanism_information
        mode_costs = json.loads(mode_costs)
        mode_values = json.loads(mode_values)
        # create a dict of security mode lists with dynamic names as their keys
        security_modes[f"{mechanism_name}_list"] = []

        for mode in range(modes):
            try:
                security_modes[f"{mechanism_name}_list"].append(mechanism_name + f"{mode}")
                # create dictionaries with the security mechanism mode as the keys and the mode_cost and mode_value
                security_mode_costs[mechanism_name + f"{mode}"] = (mode_costs[mode], mode_values[mode])

            except IndexError:
                frame_info = getframeinfo(currentframe())
                print("[ERROR]: in", frame_info.filename, "in line:", frame_info.lineno,
                      "creating security_mode or security_mode_list failed; create_all_possible_permutations is not possible\n" \
                      " fix security mechanism information through update message")
                return

    # get the values (which are the lists) from the dict through unzipping
    _, available_security_mechanisms = zip(*security_modes.items())

    # calculate all possible permutations of the elements of the lists
    # container_list = [sorted(set(v)) for v in itertools.product(*values)]
    container_list = [v for v in itertools.product(*available_security_mechanisms)]

    # create adaptive query with respect to the total amount of keys in context_information_values dict
    insert_query_string = "INSERT INTO security_mechanism_combination("

    # retrieve all keys from dict and write it into query; add necessary "," to the end
    insert_query_string += ",".join(security_mechanisms_name_deque)

    # append needed sql statement VALUES
    insert_query_string += ") VALUES ("

    # add placeholder ? for every key in context_information_values; add necessary "," to the end
    insert_query_string += len(security_mechanisms_name_deque) * "?,"

    # last ? should not have a "," in order to have a valid query; close query string with ")"
    insert_query_string = insert_query_string[:-1] + ")"

    # add items to database, commit and close
    # db_cursor.execute(insert_query_string)

    global combination_cost
    for list_element in container_list:
        sum_costs = 0
        sum_values = 0
        mode_number_list = []
        for elem in list_element:
            sum_costs += security_mode_costs[elem][0]
            sum_values += security_mode_costs[elem][1]
            mode_number_list.append(int("".join(re.findall(r"\d+", elem))))
        # combination_cost[list_element] = (sum_costs, sum_values)
        insert_deque = deque([str(list_element), sum_costs, sum_values])
        insert_deque.extend(mode_number_list)
        db_cursor.execute(insert_query_string, insert_deque)
    db_connection.commit()


def update_high_level_derivation_files(filename):
    db_cursor = get_cursor()

    create_high_level_derivation_files_query = "CREATE TABLE if not exists high_level_derivation_files(high_level_name)"
    db_cursor.execute(create_high_level_derivation_files_query)

    current_columns = db_cursor.execute("SELECT high_level_name FROM high_level_derivation_files").fetchall()
    if len(current_columns) == 0:
        pass

    elif filename in [elem[0] for elem in current_columns]:
        update_query = "UPDATE high_level_derivation_files SET high_level_name = ?"
        query_params = filename
        db_cursor.execute(update_query, (query_params,))
        db_connection.commit()
        return

    insert_high_level_derivation_query = "INSERT INTO high_level_derivation_files(high_level_name) VALUES (?)"
    query_params = filename
    db_cursor.execute(insert_high_level_derivation_query, (query_params,))
    db_connection.commit()
    return


def update_filter_files(filter_name):
    db_cursor = get_cursor()

    create_filter_query = "CREATE TABLE if not exists filter_files(filter_name)"
    db_cursor.execute(create_filter_query)

    current_columns = db_cursor.execute("SELECT filter_name FROM filter_files").fetchall()
    if len(current_columns) == 0:
        pass

    elif filter_name in [elem[0] for elem in current_columns]:
        return

    insert_filter_query = "INSERT INTO filter_files (filter_name) VALUES (?)"
    query_params = filter_name
    db_cursor.execute(insert_filter_query, (query_params,))
    db_connection.commit()
    return


def update_context_information_keystore(keystore_update_message):
    # global db_connection
    db_cursor = get_cursor()

    # create db table if not already present
    create_keystore_query = "CREATE TABLE if not exists context_information_keystore(keyname,minimum_value, maximum_value,desirable_value,weight)"
    db_cursor.execute(create_keystore_query)

    # fetch all table entries to prevent keystore attribute duplicates
    current_columns = db_cursor.execute("SELECT keyname FROM context_information_keystore").fetchall()
    # TODO maybe change if structure because pass looks like bad practice
    if len(current_columns) == 0:
        pass

    # check if keyname is in list, therefore get first elements in a list of tuples
    elif keystore_update_message["keyname"] in [elem[0] for elem in current_columns]:
        update_query = """UPDATE context_information_keystore SET 
                        minimum_value = ?,
                        maximum_value = ?,
                        desirable_value = ?,
                        weight = ?
                        WHERE keyname = ?"""

        query_params = list(keystore_update_message.values())[1:5]
        query_params.append(keystore_update_message["keyname"])
        db_cursor.execute(update_query, query_params)
        db_connection.commit()
        return

    insert_keystore_query = "INSERT INTO context_information_keystore(keyname,minimum_value,maximum_value,desirable_value,weight) VALUES (?,?,?,?,?)"

    db_cursor.execute(insert_keystore_query, list(keystore_update_message.values())[0:5])
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
            # as for each already-existing column, the except method would trigger an error message and, therefore, pollute the console output; pass is used
            pass

    # create adaptive query with respect to the total amount of keys in context_information_values dict
    insert_query_string = "INSERT INTO received_context_information("

    # retrieve all keys from dict and write it into query; add necessary "," to the end
    insert_query_string += ",".join(context_information_message.keys())

    # append needed sql statement VALUES
    insert_query_string += ") VALUES ("

    # add placeholder ? for every key in context_information_values; add necessary "," to the end
    insert_query_string += len(context_information_message.keys()) * "?,"

    # last ? should not have a "," in order to have a valid query; close query string with ")"
    insert_query_string = insert_query_string[:-1] + ")"

    # add items to database, commit and close
    db_cursor.execute(insert_query_string, list(context_information_message.values()))
    db_connection.commit()
    db_cursor.close()
