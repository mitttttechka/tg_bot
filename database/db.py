from database import db_connection
import logging
import json
from collections import namedtuple
from instances import units


def send_query(query):
    logging.warning(query)
    answer = db_connection.send_query(query)
    return answer


def get_redis(key):
    res = db_connection.Connection.rdb.get(key)
    if res:
        x = json.loads(res, object_hook=lambda d: namedtuple('X', d.keys()) * (d.values()))
        return x
    return res


def set_redis(key, value):
    json_str = json.dumps(value.__dict__)
    db_connection.Connection.rdb.set(key, json_str)


def del_redis(key):
    db_connection.Connection.rdb.delete(key)


class Tables:
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
    track_id_name_table = 'track_id_name'
    test_id_name_table = 'test_id_name'


# TODO for every class pending 0 and default values not to show them
# TODO add data for easier test
def renew_database():
    q = f"DROP TABLE {Tables.tests_table};" \
        f"DROP TABLE {Tables.test_rule_table};" \
        f"DROP TABLE {Tables.sections_table};" \
        f"DROP TABLE {Tables.task_table};" \
        f"DROP TABLE {Tables.statistics_table};" \
        f"DROP TABLE {Tables.task_answers_table};" \
        f"DROP TABLE {Tables.learning_track_table};" \
        f"DROP TABLE {Tables.students_table};" \
        f"DROP TABLE {Tables.user_table};" \
        f"DROP TABLE {Tables.class_table};" \
        f"DROP TABLE {Tables.track_id_name_table};" \
        f"DROP TABLE {Tables.test_id_name_table};" \
        f"CREATE TABLE {Tables.tests_table} (id integer, task_id integer, sort integer); " \
        f"INSERT INTO {Tables.tests_table} VALUES (0, 0, 0); " \
        f"CREATE TABLE {Tables.test_rule_table} (id integer, section_id integer," \
        f" number_tasks integer, sort integer); " \
        f"CREATE TABLE {Tables.sections_table} (id integer, section_name varchar(30)); " \
        f"INSERT INTO {Tables.sections_table} VALUES (0, 'default'); " \
        f"CREATE TABLE {Tables.task_table} (id integer, text text, picture_link text, " \
        f"question boolean, section_id integer); " \
        f"INSERT INTO {Tables.task_table} VALUES (0, 'default', 'NONE', FALSE, 0); " \
        f"INSERT INTO {Tables.task_table} VALUES (1, 'theme 1', 'NONE', FALSE, 0); " \
        f"INSERT INTO {Tables.task_table} VALUES (2, 'theme 2', 'NONE', TRUE, 0); " \
        f"CREATE TABLE {Tables.statistics_table} (id bigint, test_id integer, correct boolean, " \
        f"dt timestamp DEFAULT current_timestamp); " \
        f"CREATE TABLE {Tables.task_answers_table} (id integer, answer text, correct boolean); " \
        f"CREATE TABLE {Tables.learning_track_table} (id integer, sort integer, task_id integer); " \
        f"INSERT INTO {Tables.learning_track_table} VALUES (0, 0, 0); " \
        f"INSERT INTO {Tables.learning_track_table} VALUES (0, 1, 1); " \
        f"INSERT INTO {Tables.learning_track_table} VALUES (0, 2, 2); " \
        f"CREATE TABLE {Tables.track_id_name_table} (id integer, track_name varchar(30)); " \
        f"INSERT INTO {Tables.track_id_name_table} VALUES (0, \'default track\'); " \
        f"CREATE TABLE {Tables.test_id_name_table} (id integer, test_name varchar(30)); " \
        f"INSERT INTO {Tables.test_id_name_table} VALUES (0, \'default test\'); " \
        f"CREATE TABLE {Tables.students_table} (id bigint, track_id integer, sort integer); " \
        f"CREATE TABLE {Tables.user_table} (id bigint, user_name varchar(30), type integer DEFAULT 1, " \
        f"class_id integer DEFAULT 0, subscribed boolean DEFAULT false, progress_point integer DEFAULT 0, " \
        f"current_position integer DEFAULT 0); " \
        f"CREATE TABLE {Tables.class_table} (id integer, class_name text, teacher_id integer, " \
        f"invite_code varchar(30), max_students integer); " \
        f"INSERT INTO {Tables.class_table} VALUES (0, \'default class\', 0, \'INV000\', 5); "
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
    q = f'SELECT * FROM {Tables.user_table} WHERE id = {user_id}'
    answer = send_query(q)
    return answer


def get_task_by_id(task_id):
    q = f'SELECT * FROM {Tables.task_table} WHERE id = {task_id}'
    answer = send_query(q)
    return answer


def get_section_by_id(section_id):
    q = f'SELECT * FROM {Tables.sections_table} WHERE id = {section_id}'
    answer = send_query(q)
    return answer


def get_info_by_id(uid, unit_type):
    q = f'SELECT * FROM {units.Units.unit_dict[unit_type].db_table} WHERE id = {uid}'
    answer = send_query(q)
    return answer


def create_new_user(user_id):
    insert(Tables.user_table, [(user_id, '', 1, 0, 'False', 0, 0)])


def set_progress(user_id, progress_point):
    q = f'UPDATE {Tables.user_table} SET progress_point = {progress_point} WHERE id = {user_id}'
    send_query(q)


def set_current(user_id, current_state):
    q = f'UPDATE {Tables.user_table} ' \
        f'SET current_position = {current_state} ' \
        f'WHERE id = {user_id}'
    send_query(q)


def update_name(user_id, name):
    q = f'UPDATE {Tables.user_table} ' \
        f'SET user_name = \'{name}\' ' \
        f'WHERE id = {user_id}'
    send_query(q)


def update_existing_task(task):
    q = f'UPDATE {Tables.task_table} ' \
        f'SET text = \'{task.text}\', picture_link = \'{task.picture_link}\', ' \
        f'question = \'{task.question}\', section_id = {task.section_id} ' \
        f'WHERE id = {task.uid}'
    send_query(q)


def update_existing_section(section):
    q = f'UPDATE {Tables.sections_table} ' \
        f'SET section_name = \'{section.text}\' ' \
        f'WHERE id = {section.uid}'
    send_query(q)





def get_all_sections():
    q = f'SELECT * FROM {Tables.sections_table}'
    answer = send_query(q)
    return answer


def get_all_tasks():
    q = f'SELECT * FROM {Tables.task_table}'
    answer = send_query(q)
    return answer


def get_all_instances(unit_type):
    q = f'SELECT * FROM {units.Units.unit_dict[unit_type].db_table}'
    answer = send_query(q)
    return answer


def add_new_task(task):
    q = f'SELECT MAX(id) FROM {Tables.task_table}'
    answer = send_query(q)
    task_id = int(answer[0][0]) + 1
    q = f'INSERT INTO {Tables.task_table} VALUES (' \
        f'{str(task_id)}, ' \
        f'\'{task.text}\', ' \
        f'\'{task.picture_link}\', ' \
        f'{task.question}, ' \
        f'{task.section_id})'
    send_query(q)
    return task_id


def get_learning_tracks_list():
    q = f'SELECT id, track_name FROM {Tables.track_id_name_table}'
    answer = send_query(q)
    return answer


def get_tests_list():
    q = f'SELECT id, test_name FROM {Tables.test_id_name_table}'
    answer = send_query(q)
    return answer


def get_learning_track(track_id):
    q = f'SELECT sort, task_id FROM {Tables.learning_track_table} WHERE id = {str(track_id)}'
    answer = send_query(q)
    return answer


def update_sorting(uid, sort, unit_type):
    q = f'DELETE FROM {units.Units.unit_dict[unit_type].db_table} WHERE id = {uid}'
    send_query(q)
    if len(sort) > 0:
        q = f'INSERT INTO {units.Units.unit_dict[unit_type].db_table} VALUES '
        for i in range(len(sort)):
            sort_str = sort[i] if isinstance(sort[i], int) else str(sort[i])[1:-1]
            q += f'({uid}, {i}, {sort_str}), '
        q = q[0:len(q) - 2]
        send_query(q)


def get_learning_track_name(track_id):
    q = f'SELECT track_name FROM {Tables.track_id_name_table} WHERE id = {str(track_id)}'
    answer = send_query(q)
    return answer


def get_section_name(section):
    q = f'SELECT section_name FROM {Tables.sections_table} WHERE id = {str(section)}'
    answer = send_query(q)
    return answer


def add_new_instance(text, unit_type):
    q = f'SELECT MAX(id) FROM {units.Units.unit_dict[unit_type].db_table}'
    answer = send_query(q)
    new_uid = int(answer[0][0]) + 1
    q = f'INSERT INTO {units.Units.unit_dict[unit_type].db_table} VALUES (' \
        f'{str(new_uid)}, ' \
        f'\'{text}\')'
    send_query(q)
    return new_uid


# def add_new_section(text):
#     q = f'SELECT MAX(id) FROM {Tables.sections_table}'
#     answer = send_query(q)
#     new_section_id = int(answer[0][0]) + 1
#     q = f'INSERT INTO {Tables.sections_table} VALUES (' \
#         f'{str(new_section_id)}, ' \
#         f'\'{text}\')'
#     send_query(q)
#     return new_section_id


# def add_new_class(text):
#     q = f'SELECT MAX(id) FROM {Tables.class_table}'
#     answer = send_query(q)
#     new_section_id = int(answer[0][0]) + 1
#     q = f'INSERT INTO {Tables.class_table} VALUES (' \
#         f'{str(new_section_id)}, ' \
#         f'\'{text}\')'
#     send_query(q)
#     return new_section_id


def add_new_learning_track(track_name):
    q = f'SELECT MAX(id) FROM {Tables.track_id_name_table}'
    answer = send_query(q)
    track_id = int(answer[0][0]) + 1
    q = f'INSERT INTO {Tables.track_id_name_table} VALUES ({track_id}, \'{track_name}\')'
    send_query(q)
    return track_id


def add_new_test(test_name):
    q = f'SELECT MAX(id) FROM {Tables.test_id_name_table}'
    answer = send_query(q)
    test_id = int(answer[0][0]) + 1
    q = f'INSERT INTO {Tables.test_id_name_table} VALUES ({test_id}, \'{test_name}\')'
    send_query(q)
    return test_id


def get_answers(task_id):
    q = f'SELECT answer, correct FROM {Tables.task_answers_table} WHERE id = {str(task_id)}'
    answer = send_query(q)
    return answer


def set_answers(task_id, correct, incorrect):
    q = f'DELETE FROM {Tables.task_answers_table} WHERE id = {task_id}'
    send_query(q)
    q = f'INSERT INTO {Tables.task_answers_table} VALUES '
    for answer in correct:
        q += f'({task_id}, \'{answer}\', \'TRUE\'), '
    for answer in incorrect:
        q += f'({task_id}, \'{answer}\', \'FALSE\'), '
    q = q[0:len(q) - 2]
    send_query(q)


def delete_task(task_id):
    q = f'DELETE FROM {Tables.task_table} WHERE id = {task_id}'
    send_query(q)
    q = f'DELETE FROM {Tables.task_answers_table} WHERE id = {task_id}'
    send_query(q)


def delete_section(section_id):
    q = f'DELETE FROM {Tables.sections_table} WHERE id = {section_id}'
    send_query(q)
    q = f'UPDATE {Tables.task_table} SET section_id = 0 WHERE section_id = {section_id}'
    send_query(q)


# TODO delete from connected tables
def delete_instance(uid, unit_type):
    q = f'DELETE FROM {units.Units.unit_dict[unit_type].db_table} WHERE id = {uid}'
    send_query(q)
