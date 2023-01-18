import json
import sqlite3
from urllib.request import pathname2url

db_connection: sqlite3.dbapi2 = None


def get_cursor():
    global db_connection
    if db_connection is None:
        db_name = 'context_information_database.sqlite'

        # https://stackoverflow.com/questions/12932607/how-to-check-if-a-sqlite3-database-exists-in-python
        # read, write, create database at given path
        db_uri = 'file:{}?mode=rwc'.format(pathname2url(db_name))

        # TODO check if check_same_thread=False may lead to any race conditions --> error SQLite objects created in a thread can only be used in that same
        #  thread. The object was created in thread id [...]
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

    return db_cursor.execute(db_query).fetchall()


# get all filters for the security mechanisms from the database
def get_security_mechanisms_filter() -> list:
    db_cursor = get_cursor()
    db_query = "SELECT * FROM security_mechanisms_filter"

    return db_cursor.execute(db_query).fetchall()


def update_security_mechanisms_information(mechanisms_information_update_message):
    db_cursor = get_cursor()
    # create table for security_mechanisms_information
    create_mechanisms_information_query = """CREATE TABLE if not exists security_mechanisms_information(mechanism_name, modes, mode_values)"""
    db_cursor.execute(create_mechanisms_information_query)

    # serialize mode_values because SQLite can't store lists; see:
    # https://stackoverflow.com/questions/20444155/python-proper-way-to-store-list-of-strings-in-sqlite3-or-mysql
    mechanisms_information_update_message['mode_values'] = json.dumps(mechanisms_information_update_message['mode_values'])

    # get the mechanism_name from the database table and check if entry already exists
    current_columns = db_cursor.execute("SELECT mechanism_name from security_mechanisms_information ").fetchall()
    # if an entry does not exist, create one
    if len(current_columns) == 0:
        pass
    # otherwise, update the existing entry
    elif mechanisms_information_update_message['mechanism_name'] in [elem[0] for elem in current_columns]:
        update_query = """UPDATE security_mechanisms_information SET modes = ?, mode_values = ? WHERE mechanism_name = ?"""

        # get values name, mode, mode_values from the dict
        query_params = list(mechanisms_information_update_message.values())[:3]
        # get the name attribute and store it in a separate variable in order to match the update_query requirements, where name has to be the last parameter
        list_element = query_params[0]
        # remove the name from the list and append it at the end
        query_params = [x for x in query_params if x != list_element] + [list_element]

        db_cursor.execute(update_query, query_params)
        db_connection.commit()
        return

    insert_mechanisms_information_query = """INSERT INTO security_mechanisms_information
                                    (mechanism_name, modes, mode_values) 
                                    VALUES (?, ?, ?)"""
    query_params = list(mechanisms_information_update_message.values())[:3]
    db_cursor.execute(insert_mechanisms_information_query, query_params)
    db_connection.commit()
    return


def update_security_mechanisms_filter(security_mechanisms_filter_message):
    db_cursor = get_cursor()

    create_filter_query = """CREATE TABLE if not exists security_mechanisms_filter(filter_name, necessary_modes)"""
    db_cursor.execute(create_filter_query)

    # serialize mode_values because SQLite can't store lists; see:
    # https://stackoverflow.com/questions/20444155/python-proper-way-to-store-list-of-strings-in-sqlite3-or-mysql
    security_mechanisms_filter_message['necessary_modes'] = json.dumps(security_mechanisms_filter_message['necessary_modes'])

    current_columns = db_cursor.execute("SELECT filter_name FROM security_mechanisms_filter").fetchall()
    if len(current_columns) == 0:
        pass

    elif security_mechanisms_filter_message['filter_name'] in [elem[0] for elem in current_columns]:
        update_query = """UPDATE security_mechanisms_filter SET
                        necessary_modes = ? WHERE filter_name = ?"""

        # get values name, mode, mode_values from the dict
        query_params = list(security_mechanisms_filter_message.values())[:2]
        # get the name attribute and store it in a separate variable in order to match the update_query requirements, where name has to be the last parameter
        list_element = query_params[0]
        # remove the name from the list and append it at the end
        query_params = [x for x in query_params if x != list_element] + [list_element]
        db_cursor.execute(update_query, query_params)
        db_connection.commit()
        return

    insert_filter_query = """INSERT INTO security_mechanisms_filter (filter_name, necessary_modes) VALUES (?, ?)"""
    query_params = list(security_mechanisms_filter_message.values())[:2]
    db_cursor.execute(insert_filter_query, query_params)
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
        # TODO compare if the update message brought new values for a specific keyname or overwrite entries all the time
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
