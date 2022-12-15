import sqlite3

from urllib.request import pathname2url

db_connection: sqlite3.dbapi2 = None


# generate database to store received context information
def create_context_information_database():
    get_cursor()
    add_columns()


# retrieve entry with the latest date
def get_latest_date_entry() -> str:
    db_cursor = get_cursor()
    max_date_query = "SELECT MAX(elicitation_date) From received_context_information"
    return db_cursor.execute(max_date_query).fetchall()[0][0]


def add_columns():
    db_cursor = get_cursor()
    db_cursor.execute(
        "CREATE TABLE if not exists context_information_keystore(keyname, mini, maxi, good, weight, seperatorlist)")

    # TODO abfangen, dass beim Neustart nicht erneut geschrieben wird
    db_cursor.execute("INSERT INTO context_information_keystore(keyname,mini,maxi,good,weight,seperatorlist) "
                      "VALUES (?,?,?,?,?,?)",
                      ["battery_state", 0, 100, 100, 15, '[10, 20, 50, 80]'])
    db_cursor.execute("INSERT INTO context_information_keystore(keyname,mini,maxi,good,weight,seperatorlist) "
                      "VALUES (?,?,?,?,?,?)",
                      ["charging_station_distance", 0, 1000, 0, 0.2, '[50, 100, 800]'])


def get_cursor():
    global db_connection
    if db_connection is None:
        db_name = 'context_information_database.sqlite'

        # https://stackoverflow.com/questions/12932607/how-to-check-if-a-sqlite3-database-exists-in-python
        # read, write, create database at given path
        db_uri = 'file:{}?mode=rwc'.format(pathname2url(db_name))
        db_connection = sqlite3.connect(db_uri, uri=True)

    return db_connection.cursor()


def create_table_context_information_database(table_attributes):
    db_cursor = get_cursor()

    # create table and make keys from dict to new columns
    db_cursor.execute(
        "CREATE TABLE if not exists received_context_information(%s)" % ", ".join(table_attributes.keys()))

    # add new column to table if table_attributes comes with additional non exising values
    for item in table_attributes:
        try:
            db_cursor.execute("ALTER TABLE received_context_information ADD COLUMN '%s'" % item)
        except:
            print("table column already exist")


def insert_values_ci_db(context_information_values):
    db_cursor = get_cursor()
    # create adaptive query with respect to the total amount of keys in context_information_values dict
    insert_query_string = "INSERT INTO received_context_information("

    # retrieve all keys from dict and write it into query; add necessary ',' to the end
    insert_query_string += ",".join(context_information_values.keys())

    # append needed sql statement VALUES
    insert_query_string += ") VALUES ("

    # add placeholder ? for every key in context_information_values; add necessary ',' to the end
    insert_query_string += len(context_information_values.keys()) * '?,'

    # last ? should not have a ',' in order to have a valid query; close query string with ')'
    insert_query_string = insert_query_string[:-1] + ')'

    # add items to database, commit and close
    db_cursor.execute(insert_query_string, list(context_information_values.values()))
    db_connection.commit()
    db_cursor.close()
