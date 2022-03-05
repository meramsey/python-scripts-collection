import sys
import sqlite3


####################
# Constants
####################

# Plug in name of SQLite file here, assumed to be in current directory
DB_SERVER = 'ccl-aig.sqlite3'


def database_connect():
    """
    Does a standard connection to SQLite database.
    Connect to SQL Server using 'try' - if any problems terminate immediately
    and return user error code 100 - database error.
    SQLite is very loose in this aspect, if the file does not exist it will simply
    create a new one, so I use a pragma lookup.

    :return: DB connection object
    """
    try:
        c = sqlite3.connect(DB_SERVER)
    except sqlite3.DatabaseError as err:
        print('DB error: {0}'.format(err))
        print('Problem executing query, terminating program.')
        sys.exit(100)   # Database error

    # Check that we have a valid - not newly created - SQLite DB file
    # The schema version for a new file will be 0.
    db_verify = c.execute('PRAGMA SCHEMA_VERSION').fetchone()
    if not db_verify[0] > 0:
        print('***************************')
        print('*         WARNING         *')
        print('***************************')
        print('Application database file not found or is corrupted, program terminating.')
        sys.exit(100)   # Database error
    # If there is a serious DB error application will have terminated by this point anyway
    # otherwise return database connection handle
    return c


def run_test():
    # Connect to database
    cnx = database_connect()
    cursor_test = cnx.cursor()

    # Run query
    cursor_test.execute('''select * from rma_cases;''')

    # # Interesting to look at this progression to get to enumerate
    print(cursor_test.description)
    print(list(map(lambda x: x[0], cursor_test.description)))
    for i, column in enumerate(list(map(lambda x: x[0], cursor_test.description))):
        print(str(i) + ', ' + column)


if __name__ == "__main__":
    run_test()
