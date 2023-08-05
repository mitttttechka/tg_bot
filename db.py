import psycopg2

class Connection:
    conn = None

def connect():
    """ Connect to the PostgreSQL database server """
    #conn = None
    try:

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        Connection.conn = psycopg2.connect(
            host="localhost",
            database="tg_bot_develop",
            user="mitttttechka",
            password="",
            port="5434")


    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def disconnect():
    Connection.conn.commit()
    if Connection.conn is not None:
        Connection.conn.close()
        print('Database connection closed.')

def create_query():
    # create a cursor
    cur = Connection.conn.cursor()
    # execute a statement
    #print('PostgreSQL database version:')
    q = "CREATE TABLE prescripted_test (test_id integer, task_id integer, sort integer); " \
        "CREATE TABLE test_rule (track_id integer, section_id integer, number_tasks integer, sort integer); " \
        "CREATE TABLE sections (section_id integer, section_name varchar(30)); " \
        "CREATE TABLE task (task_id integer, text text, picture_link text, question boolean, section_id integer); " \
        "CREATE TABLE statistics (user_id integer, test_id integer, correct boolean, dt timestamp); " \
        "CREATE TABLE task_answers (task_id integer, answer text, correct boolean); " \
        "CREATE TABLE learning_track (track_id integer, sort integer, task_id integer); " \
        "CREATE TABLE students (user_id integer, track_id integer, sort integer); " \
        "CREATE TABLE users (user_id integer, type integer, class_id integer); " \
        "CREATE TABLE class (class_id integer, class_name text);"
    cur.execute(q)
    cur.close()

def insert():
    cur = Connection.conn.cursor()
    q = "INSERT INTO prescripted_test VALUES (1, 2, 0)"
    cur.execute(q)
    q = "SELECT * FROM prescripted_test"
    cur.execute(q)
    answer = cur.fetchone()
    print(answer)