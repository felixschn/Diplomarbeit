import sqlite3
from urllib.request import pathname2url


# generate database to store received context information
def create_context_information_database():
    global db_connection
    db_name = 'context_information_database.sqlite'

    # https://stackoverflow.com/questions/12932607/how-to-check-if-a-sqlite3-database-exists-in-python
    db_uri = 'file:{}?mode=rwc'.format(pathname2url(db_name))
    db_connection = sqlite3.connect(db_uri, uri=True)


def create_table_context_information_database(table_attributes):
    db_cursor = db_connection.cursor()

    db_cursor.execute("CREATE TABLE if not exists "
                      "received_context_information(%s)" % ", ".join(
        table_attributes.keys()))

    # add new column to table if table_attributes comes with additional non exising values
    for item in table_attributes:
        try:
            db_cursor.execute("ALTER TABLE received_context_information ADD COLUMN '%s'" %
                              item)
        except:
            print("table column already exist")


def insert_values_ci_db(context_information_values):
    db_cursor = db_connection.cursor()
    insert_query_string = "INSERT INTO received_context_information("
    insert_query_string += ",".join(context_information_values.keys())
    insert_query_string = insert_query_string[:-1]
    insert_query_string += ") VALUES ("
    insert_query_string += len(context_information_values.keys()) * '?,'
    insert_query_string = insert_query_string[:-1] + ')'

    db_cursor.execute(insert_query_string, list(context_information_values.values()))
    db_connection.commit()
    db_cursor.close()

# create_context_information_database()
# create_table_context_information_database(["id", "battery_state",
#                                            "charging_station_distance", "location",
#                                            "elicitation_date",
#                                            "bergholz", "klaus"])
