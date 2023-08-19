import psycopg2
import logging


class Connection:
    conn = None
    user_table = 'users'
    tests_table = 'prescripted_test'
    test_rule_table = 'test_rule'
    sections_table = 'sections'
    task_table = 'task'
    statistics_table = 'statistics'
    task_answers_table = 'task_answers'
    learning_track_table = 'learning_track'
    students_table = 'students'
    class_table = 'class'


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


# TODO for every class pending 0 and default values not to show them
# TODO add data for easier test
def renew_database():
    q = f"DROP TABLE {Connection.tests_table};" \
        f"DROP TABLE {Connection.test_rule_table};" \
        f"DROP TABLE {Connection.sections_table};" \
        f"DROP TABLE {Connection.task_table};" \
        f"DROP TABLE {Connection.statistics_table};" \
        f"DROP TABLE {Connection.task_answers_table};" \
        f"DROP TABLE {Connection.learning_track_table};" \
        f"DROP TABLE {Connection.students_table};" \
        f"DROP TABLE {Connection.user_table};" \
        f"DROP TABLE {Connection.class_table};" \
        f"CREATE TABLE {Connection.tests_table} (test_id integer, task_id integer, sort integer); " \
        f"CREATE TABLE {Connection.test_rule_table} (track_id integer, section_id integer," \
        f" number_tasks integer, sort integer); " \
        f"CREATE TABLE {Connection.sections_table} (section_id integer, section_name varchar(30)); " \
        f"INSERT INTO {Connection.sections_table} VALUES (0, 'default'); " \
        f"CREATE TABLE {Connection.task_table} (task_id integer, text text, picture_link text, " \
        f"question boolean, section_id integer); " \
        f"INSERT INTO {Connection.task_table} VALUES (0, 'default', 'NONE', FALSE, 0); " \
        f"INSERT INTO {Connection.task_table} VALUES (1, 'theme 1', 'NONE', FALSE, 0); " \
        f"INSERT INTO {Connection.task_table} VALUES (2, 'theme 2', 'NONE', TRUE, 0); " \
        f"CREATE TABLE {Connection.statistics_table} (user_id bigint, test_id integer, correct boolean, " \
        f"dt timestamp DEFAULT current_timestamp); " \
        f"CREATE TABLE {Connection.task_answers_table} (task_id integer, answer text, correct boolean); " \
        f"CREATE TABLE {Connection.learning_track_table} (track_id integer, sort integer, task_id integer); " \
        f"INSERT INTO {Connection.learning_track_table} VALUES (0, 0, 0); " \
        f"INSERT INTO {Connection.learning_track_table} VALUES (0, 1, 1); " \
        f"INSERT INTO {Connection.learning_track_table} VALUES (0, 2, 2); " \
        f"CREATE TABLE {Connection.students_table} (user_id bigint, track_id integer, sort integer); " \
        f"CREATE TABLE {Connection.user_table} (user_id bigint, user_name varchar(30), type integer DEFAULT 1, " \
        f"class_id integer DEFAULT 0, subscribed boolean DEFAULT false, progress_point integer DEFAULT 0, " \
        f"current_position integer DEFAULT 0); " \
        f"CREATE TABLE {Connection.class_table} (class_id integer, class_name text);"
    send_query(q)


# values - array of tuples
def insert(table, values):
    q = f'INSERT INTO {table} VALUES '
    for row in values:
        q += f'{row}, '
    q = q[0:len(q) - 2]
    logging.debug(q)
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
    logging.debug(f'Creating for {user_id}')
    insert(Connection.user_table, [(user_id, '', 1, 0, 'False', 0, 0)])


def set_progress(user_id, progress_point):
    q = f'UPDATE {Connection.user_table} SET progress_point = {progress_point} WHERE user_id = {user_id}'
    send_query(q)


def set_current(user_id, current_state):
    q = f'UPDATE {Connection.user_table} SET current_position = {current_state} WHERE user_id = {user_id}'
    send_query(q)


def update_name(user_id, name):
    q = f'UPDATE {Connection.user_table} SET user_name = \'{name}\' WHERE user_id = {user_id}'
    send_query(q)


def add_new_section(text):
    q = f'INSERT INTO {Connection.sections_table} VALUES (' \
        f'(SELECT MAX(section_id) + 1 FROM {Connection.sections_table}), ' \
        f'\'{text}\')'
    send_query(q)


def get_all_sections():
    q = f'SELECT * FROM {Connection.sections_table}'
    answer = send_query(q)
    return answer


def get_all_tasks():
    q = f'SELECT * FROM {Connection.task_table}'
    answer = send_query(q)
    return answer


def add_new_task(task):
    q = f'INSERT INTO {Connection.task_table} VALUES (' \
        f'(SELECT MAX(task_id) + 1 FROM {Connection.task_table}), ' \
        f'\'{task.text}\', ' \
        f'\'{task.picture_link}\', ' \
        f'{task.question}, ' \
        f'{task.section_id})'
    logging.warning(q)
    send_query(q)


def get_task_by_id(task_id):
    q = f'SELECT * FROM {Connection.task_table} WHERE task_id = {task_id}'
    answer = send_query(q)
    return answer


def get_learning_tracks_list():
    q = f'SELECT DISTINCT track_id FROM {Connection.learning_track_table}'
    answer = send_query(q)
    return answer


def get_learning_track(track_id):
    q = f'SELECT sort, task_id FROM {Connection.learning_track_table} WHERE track_id = {str(track_id)}'
    answer = send_query(q)
    return answer


def update_learning_track(track_id, sort):
    q = f'DELETE FROM {Connection.learning_track_table} WHERE track_id = {track_id}'
    send_query(q)
    if len(sort) > 0:
        q = f'INSERT INTO {Connection.learning_track_table} VALUES '
        for i in range(len(sort)):
            q += f'({track_id}, {i}, {sort[i]}), '
        q = q[0:len(q) - 2]
        send_query(q)

