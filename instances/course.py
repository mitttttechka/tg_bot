import logging

from database import db
from datetime import datetime

static_sections = []


class LastUpdated:
    dt_all_sections_updated = None


class ChangeState:
    normal = 1
    new_section = 2


class Course:

    def __init__(self, *section_id):
        if len(section_id) == 1:
            self.section_id = section_id[0]
            info = self.get_section_info()
            self.section_name = info[1]
            self.state = ChangeState.normal
        elif len(section_id) == 2:
            self.section_id = section_id[0]
            self.section_name = section_id[1]
            self.state = ChangeState.normal
        else:
            self.section_id = None
            self.section_name = None
            self.state = ChangeState.new_section

    def get_section_info(self):
        return db.get_section_by_id(self.section_id)[0]

    def update(self, section_id):
        self.section_id = section_id
        info = self.get_section_info()
        self.section_name = info[1]
        self.state = ChangeState.normal
        update_active_sections(self)

    def change_id(self, section_id):
        self.section_id = section_id

    def change_state(self, state):
        self.state = state

    def change_name(self, name):
        self.section_name = name


def get_section(section_id):
    try:
        section_id = int(section_id)
    except ValueError:
        return None
    has_task = find_section_in_static(section_id)
    if has_task != -1:
        return static_sections[has_task]
    sections_array = db.get_task_by_id(section_id)
    if len(sections_array) > 0:
        db_section = db_answer_to_sections_array(sections_array)
        update_active_sections(db_section[0])
        return db_section[0]
    else:
        return None


def update_active_sections(section):
    index = find_section_in_static(section.section_id)
    if index == -1:
        static_sections.append(section)
        static_sections.sort(key= lambda x: x.section_id, reverse=False)
    else:
        static_sections[index] = section
    # TODO add async update to database


def find_section_in_static(section_id):
    for i in range(len(static_sections)):
        if static_sections[i].section_id == section_id:
            return i
    return -1


def all_sections_message(*add_text):
    sections = get_all_sections()
    return form_sections_message(sections, add_text)


def get_all_sections():
    if LastUpdated.dt_all_sections_updated is None or (datetime.now() - LastUpdated.dt_all_sections_updated).seconds > 120:
        sections_array = db.get_all_sections()
        LastUpdated.dt_all_tasks_updated = datetime.now()
        sections = db_answer_to_sections_array(sections_array)
        for single_section in sections:
            update_active_sections(single_section)
    return static_sections


def db_answer_to_sections_array(sections_array):
    sections = []
    for section in sections_array:
        t = Course(section[0], section[1])
        sections.append(t)
    return sections


def form_sections_message(sections, *add_text):
    logging.debug(f'add_text length: {len(add_text)}')
    mes = add_text[0][0] if len(add_text[0]) > 0 else ''
    for s_task in sections:
        mes += f'Section ID: {s_task.section_id}. {s_task.section_name}\n'
    return mes
