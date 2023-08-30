import logging

from database import db
from instances import user, question, instance
import menu_navigation as nav
from datetime import datetime

static_sections = []


class LastUpdated:
    dt_all_sections_updated = None


class ChangeState:
    normal = 1
    new_section = 2
    awaiting_section_id = 3
    awaiting_manage_section = 4
    awaiting_text = 5
    updating_text = 6


class Section(instance.Instance):

    def __init__(self, *section_id):
        super().__init__(self, section_id)
        self.type = Section
        if len(section_id) == 1:
            self.state = ChangeState.normal
        elif len(section_id) == 2:
            self.section_name = section_id[1]
            self.state = ChangeState.normal
        else:
            self.section_name = None
            self.state = ChangeState.new_section

    def update(self, section_id):
        self.section_id = section_id
        info = self.get_info()
        self.section_name = info[1]
        self.state = ChangeState.normal
        update_active_sections(self)


def get_section(section_id):
    try:
        section_id = int(section_id)
    except:
        return None
    has_section = find_section_in_static(section_id)
    if has_section != -1:
        return static_sections[has_section]
    sections_array = db.get_section_by_id(section_id)
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


def section_exists(section_id):
    if get_section(section_id) is not None:
        return True
    return False


def all_sections_message(*add_text):
    sections = get_all_sections()
    return form_sections_message(sections, add_text)


def section_message(section_id, *add_text):
    sections = get_section(section_id)
    return form_sections_message([sections], add_text)


def get_all_sections():
    if LastUpdated.dt_all_sections_updated is None \
            or (datetime.now() - LastUpdated.dt_all_sections_updated).seconds > 120:
        sections_array = db.get_all_sections()
        LastUpdated.dt_all_sections_updated = datetime.now()
        sections = db_answer_to_sections_array(sections_array)
        for single_section in sections:
            update_active_sections(single_section)
    return static_sections


def db_answer_to_sections_array(sections_array):
    sections = []
    for section in sections_array:
        t = Section(section[0], section[1])
        sections.append(t)
    return sections


def form_sections_message(sections, *add_text):
    mes = ''
    logging.debug(f'add_text length: {len(add_text)}')
    if len(add_text[0]) > 0:
        mes += add_text[0][0]
    for s_section in sections:
        mes += f'Section ID: {s_section.section_id}. {s_section.section_name}\n'
    return mes


def add_new_section(text):
    new_id = db.add_new_section(text)
    new_section = Section(new_id, text)
    update_active_sections(new_section)


def get_name_for_section(section_id):
    name = get_section(section_id)
    if name is not None:
        return name.section_name
    return None


def manage_section(user_id, user_state, *data):
    section_state, person = initiate_section(user_id, user_state)

    if section_state.state == ChangeState.new_section:
        return manage_section_new_section(section_state)

    if section_state.state == ChangeState.awaiting_section_id:
        section_state = get_existing_section(section_state, data[0][0])
        return manage_section_await_section_id(section_state)

    if section_state.state == ChangeState.awaiting_manage_section:
        return manage_section_await_manage_section(section_state, user_state[2])

    if section_state.state == ChangeState.awaiting_text:
        section_state = update_text(section_state, data[0][0])
        updating_existing_section(section_state)
        return manage_section_await_section_id(section_state, 'Section name was changed.\n')

    return 1


def initiate_section(user_id, user_state):
    person = user.get_user(user_id)
    logging.debug(f"User {person.user_id} is here!. User state: {user_state}")

    if person.working_on is None or type(person.working_on) is not Section:
        new_section = Section()
        person.working_on = new_section

    section_state = person.working_on
    logging.debug(f"Section_state: {section_state.section_id}")
    return section_state, person


def manage_section_new_section(section_state, *add_text):
    mes = ''
    if len(add_text) > 0:
        mes += add_text[0]
    section_state.change_state(ChangeState.awaiting_section_id)
    mes += all_sections_message('Please write Section ID to manage:\n')
    keyboard = [['Back', f'{nav.manage_sections_menu}']]
    return mes, keyboard


def get_existing_section(section_state, text):
    if not section_exists(text):
        return manage_section_new_section(section_state, 'Section doesn\'t exist. Please try again.\n')
    section_state.update(int(text))
    return section_state


def manage_section_await_section_id(section_state, *add_text):
    section_state.change_state(ChangeState.awaiting_manage_section)
    mes = ''
    if len(add_text) > 0:
        mes += add_text[0]
    mes += section_message(section_state.section_id)

    keyboard = [['Change name', f'{nav.find_section}1'],
                ['Delete section', f'{nav.find_section}2'],
                ['Back', f'{nav.manage_sections_menu}']]

    return mes, keyboard


def manage_section_await_manage_section(section_state, user_state):
    if user_state == '1':
        return await_text(section_state)
    elif user_state == '2':
        return delete_section(section_state)


def await_text(section_state):
    section_state.change_state(ChangeState.awaiting_text)
    mes = f"Please write new section name:"
    return mes, None


def update_text(section_state, text):
    section_state.change_state(ChangeState.updating_text)
    logging.warning('Here')
    section_state.change_text(text)
    return section_state


def delete_section(section_state):
    db.delete_section(section_state.section_id)
    index = find_section_in_static(section_state.section_id)
    static_sections.pop(index)
    return manage_section_new_section(section_state, 'Section was deleted. \n')


def updating_existing_section(section_state):
    db.update_existing_section(section_state)
    update_active_sections(section_state)
