import psycopg2


class Connection:
    conn = None
    user_table = 'users'


def connect():
    """ Connect to the PostgreSQL database server """
    # conn = None
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


def send_query(query):
    if Connection.conn is None:
        print('No connection to the database')
        return 0
    cur = Connection.conn.cursor()
    cur.execute(query)
    if query[0:6].strip().lower() == 'select':
        answer = cur.fetchall()
    else:
        answer = 1
    Connection.conn.commit()
    cur.close()
    return answer


def renew_database():
    q = "DROP TABLE prescripted_test;" \
        "DROP TABLE test_rule;" \
        "DROP TABLE sections;" \
        "DROP TABLE task;" \
        "DROP TABLE statistics;" \
        "DROP TABLE task_answers;" \
        "DROP TABLE learning_track;" \
        "DROP TABLE students;" \
        "DROP TABLE users;" \
        "DROP TABLE class;" \
        "CREATE TABLE prescripted_test (test_id integer, task_id integer, sort integer); " \
        "CREATE TABLE test_rule (track_id integer, section_id integer, number_tasks integer, sort integer); " \
        "CREATE TABLE sections (section_id integer, section_name varchar(30)); " \
        "CREATE TABLE task (task_id integer, text text, picture_link text, question boolean, section_id integer); " \
        "CREATE TABLE statistics (user_id integer, test_id integer, correct boolean, " \
        "dt timestamp DEFAULT current_timestamp); " \
        "CREATE TABLE task_answers (task_id integer, answer text, correct boolean); " \
        "CREATE TABLE learning_track (track_id integer, sort integer, task_id integer); " \
        "CREATE TABLE students (user_id integer, track_id integer, sort integer); " \
        "CREATE TABLE users (user_id integer, user_name varchar(30), type integer DEFAULT 1, " \
        "class_id integer DEFAULT 0, subscribed boolean DEFAULT false, progress_point integer DEFAULT 0); " \
        "CREATE TABLE class (class_id integer, class_name text);"
    send_query(q)


# values - array of tuples
def insert(table, values):
    q = f'INSERT INTO {table} VALUES '
    for row in values:
        q += f'{row}, '
    q = q[0:len(q) - 2]
    send_query(q)


# values - array of strings(column names)
def select(table, *values):
    q = f'SELECT '
    if len(values) == 0:
        q += '* '
    else:
        for param in values:
            for column in param:
                q += f'{column}, '
        q = q[0:len(q) - 2]
    q += f' FROM {table}'
    answer = send_query(q)
    return answer


def get_user(user_id):
    q = f'SELECT * FROM {Connection.user_table} WHERE user_id = {user_id}'
    answer = send_query(q)
    return answer


def create_new_user(user_id):
    insert(Connection.user_table, [(user_id, '', 1, 0, 'False', 0)])


def set_progress(user_id, progress_point):
    q = f'UPDATE {Connection.user_table} SET progress_point = {progress_point} WHERE user_id = {user_id}'
    send_query(q)


def update_name(user_id, name):
    q = f'UPDATE {Connection.user_table} SET user_name = \'{name}\' WHERE user_id = {user_id}'
    send_query(q)