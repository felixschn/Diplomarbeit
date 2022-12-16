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

        # TODO check if check_same_thread=False may lead to any race conditions
        # SQLite objects created in a thread can only be used in that same thread. The object was created in thread id
        db_connection = sqlite3.connect(db_uri, uri=True, check_same_thread=False)

    return db_connection.cursor()


# retrieve entry with the latest date
def get_latest_date_entry(table_name) -> str:
    db_cursor = get_cursor()
    validation_query = "SELECT * FROM context_information_database.tables WHERE table_name = '%s'"
    db_cursor.execute(validation_query % table_name)

    if db_cursor.fetchone()[0] == 1:
        max_date_query = "SELECT MAX(elicitation_date) From received_context_information"
        return db_cursor.execute(max_date_query).fetchall()[0][0]
    else:
        return


def update_context_information_keystore(keystore_update_message):
    # global db_connection
    db_cursor = get_cursor()

    # create db table if not already present
    db_cursor.execute(
        "CREATE TABLE if not exists context_information_keystore(keyname, mini, maxi, good, weight, seperatorlist)")

    current_columns = db_cursor.execute("SELECT keyname FROM context_information_keystore").fetchall()
    if len(current_columns) == 0:
        pass
    elif keystore_update_message['keyname'] in current_columns[:][0]:
        return

    # TODO abfangen, dass beim Neustart nicht erneut geschrieben wird
    db_cursor.execute("INSERT INTO context_information_keystore(keyname,mini,maxi,good,weight,seperatorlist) "
                      "VALUES (?,?,?,?,?,?)",
                      list(keystore_update_message.values())[1:7])
    db_connection.commit()


def update_context_information(context_information_message):
    global db_connection
    db_cursor = get_cursor()

    # create table and make keys from dict to new columns
    db_cursor.execute(
        "CREATE TABLE if not exists received_context_information(%s)" % ", ".join(context_information_message.keys()))

    # add new column to table if table_attributes comes with additional non exising values
    for item in context_information_message:
        try:
            db_cursor.execute("ALTER TABLE received_context_information ADD COLUMN '%s'" % item)
        except:
            print("table column already exist")
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
