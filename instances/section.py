import logging

from database import db
from instances import user, question, instance
import menu_navigation as nav


class ChangeState:
    normal = 1
    new_section = 2
    awaiting_section_id = 3
    awaiting_manage_section = 4
    awaiting_text = 5
    updating_text = 6


class Section(instance.Instance):

    def __init__(self, *section_id):
        super().__init__()
        self.type = Section
        if len(section_id) == 1:
            self.uid = section_id[0]
            info = self.get_info()
            self.text = info[1]
            self.state = ChangeState.normal
        elif len(section_id) == 2:
            self.uid = section_id[0]
            self.text = section_id[1]
            self.state = ChangeState.normal
        else:
            self.text = None
            self.state = ChangeState.new_section

    def update(self, section_id):
        self.uid = section_id
        info = self.get_info()
        self.text = info[1]
        self.state = ChangeState.normal
        self.update_active_instances()

    def db_answer_to_instances_array(self, sections_array):
        sections = []
        for section in sections_array:
            t = Section(section[0], section[1])
            sections.append(t)
        return sections

    def manage_section_new_section(self, *add_text):
        mes = ''
        if len(add_text) > 0:
            mes += add_text[0]
        self.change_state(ChangeState.awaiting_section_id)
        mes += instance.all_instances_message(Section, 'Please write Section ID to manage:\n')
        keyboard = [['Back', f'{nav.manage_sections_menu}']]
        return mes, keyboard

    def manage_section_await_section_id(self, *add_text):
        self.change_state(ChangeState.awaiting_manage_section)
        mes = ''
        if len(add_text) > 0:
            mes += add_text[0]
        mes += instance.instance_message(self.uid, Section)

        keyboard = [['Change name', f'{nav.find_section}1'],
                    ['Delete section', f'{nav.find_section}2'],
                    ['Back', f'{nav.manage_sections_menu}']]

        return mes, keyboard

    def manage_section_await_manage_section(self, user_state):
        if user_state == '1':
            return self.await_text()
        elif user_state == '2':
            instance.delete_instance(self)
            return self.manage_section_new_section('Section was deleted. \n')

    def await_text(self):
        self.change_state(ChangeState.awaiting_text)
        mes = f"Please write new section name:"
        return mes, None

    def update_text(self, text):
        self.change_state(ChangeState.updating_text)
        logging.warning('Here')
        self.change_text(text)
        return self

    def updating_existing_section(self):
        db.update_existing_section(self)
        self.update_active_instances()

    def get_existing_section(self, text):
        if not instance.instance_exists(text, Section):
            return self.manage_section_new_section('Section doesn\'t exist. Please try again.\n')
        self.update(int(text))
        return self


def add_new_section(text):
    new_id = db.add_new_section(text)
    new_section = Section(new_id, text)
    new_section.update_active_instances()


def manage_section(user_id, user_state, *data):
    section_state, person = instance.initiate_instance(user_id, user_state, Section)

    if section_state.state == ChangeState.new_section:
        return section_state.manage_section_new_section()

    if section_state.state == ChangeState.awaiting_section_id:
        section_state.get_existing_section(data[0][0])
        return section_state.manage_section_await_section_id()

    if section_state.state == ChangeState.awaiting_manage_section:
        return section_state.manage_section_await_manage_section(user_state[2])

    if section_state.state == ChangeState.awaiting_text:
        section_state.update_text(data[0][0])
        section_state.updating_existing_section()
        return section_state.manage_section_await_section_id('Section name was changed.\n')

    return 1
