import logging

from database import db
from instances import user, question, units
import menu_navigation as nav
from datetime import datetime


class Instance:

    def __init__(self):
        self.uid = None
        self.text = None
        self.state = None
        self.type = None

    def get_info(self):
        return db.get_info_by_id(self.uid, self.type)[0]

    def change_id(self, uid):
        self.uid = uid

    def change_state(self, state):
        self.state = state

    def change_text(self, text):
        self.text = text

    def update_active_instances(self):
        index = find_instance_in_static(self.uid, self.type)
        if index == -1:
            units.Units.unit_dict[self.type].statics.append(self)
            units.Units.unit_dict[self.type].statics.sort(key=lambda x: x.uid, reverse=False)
        else:
            units.Units.unit_dict[self.type].statics[index] = self
        # TODO add async update to database


def get_instance(uid, unit_type):
    try:
        uid = int(uid)
    except:
        return None
    has_instance = find_instance_in_static(uid)
    if has_instance != -1:
        return units.Units.unit_dict[unit_type].statics[has_instance]
    instances_array = db.get_info_by_id(uid, unit_type)
    if len(instances_array) > 0:
        db_instance = db_answer_to_instances_array(instances_array)
        db_instance[0].update_active_instances()
        return db_instance[0]
    else:
        return None


def get_all_instances(unit_type):
    if units.Units.unit_dict[unit_type].last_updated is None \
            or (datetime.now() - units.Units.unit_dict[unit_type].last_updated).seconds > 120:
        instances_array = db.get_all_instances()
        units.Units.unit_dict[unit_type].last_updated = datetime.now()
        instances = db_answer_to_instances_array(instances_array)
        for single_instance in instances:
            single_instance.update_active_instances()
    return units.Units.unit_dict[unit_type].statics


def form_instances_message(instances, *add_text):
    mes = ''
    logging.debug(f'add_text length: {len(add_text)}')
    if len(add_text[0]) > 0:
        mes += add_text[0][0]
    for s_instance in instances:
        mes += f'ID: {s_instance.uid}. {s_instance.instance_name}\n'
    return mes


def db_answer_to_instances_array(instances_array):
    instances = []
    for instance in instances_array:
        t = Instance(instance)
        instances.append(t)
    return instances


def find_instance_in_static(uid, unit_type):
    for i in range(len(units.Units.unit_dict[unit_type].statics)):
        if units.Units.unit_dict[unit_type].statics[i].uid == uid:
            return i
    return -1


def instance_exists(uid, unit_type):
    if get_instance(uid, unit_type) is not None:
        return True
    return False


def instance_message(self, *add_text):
    instances = self.get_instance()
    return form_instances_message([instances], add_text)


def get_name(uid, unit_type):
    instance = get_instance(uid, unit_type)
    if instance is not None:
        return instance.text
    return None


def delete_instance(instance_state):
    db.delete_instance(instance_state)
    index = find_instance_in_static(instance_state.uid, instance_state.type)
    units.Units.unit_dict[instance_state.type].statics.pop(index)
    return manage_instance_new_instance(instance_state, 'instance was deleted. \n')


def get_existing_instance(self, text):
    if not instance_exists(text):
        return manage_instance_new_instance(self, 'Task doesn\'t exist. Please try again.\n')
    self.update(int(text))
    return self


def all_instances_message(*add_text):
    instances = get_all_instances()
    return form_instances_message(instances, add_text)


def manage_instance(user_id, user_state, *data):
    instance_state, person = initiate_instance(user_id, user_state)

    if instance_state.state == ChangeState.new_instance:
        return manage_instance_new_instance(instance_state)

    if instance_state.state == ChangeState.awaiting_uid:
        instance_state = get_existing_instance(instance_state, data[0][0])
        return manage_instance_await_uid(instance_state)

    if instance_state.state == ChangeState.awaiting_manage_instance:
        return manage_instance_await_manage_instance(instance_state, user_state[2])

    if instance_state.state == ChangeState.awaiting_text:
        instance_state = update_text(instance_state, data[0][0])
        updating_existing_instance(instance_state)
        return manage_instance_await_uid(instance_state, 'instance name was changed.\n')

    return 1


def initiate_instance(user_id, user_state):
    person = user.get_user(user_id)
    logging.debug(f"User {person.user_id} is here!. User state: {user_state}")

    if person.working_on is None or type(person.working_on) is not Instance:
        new_instance = Instance()
        person.working_on = new_instance

    instance_state = person.working_on
    logging.debug(f"Task_state: {instance_state.uid}")
    return instance_state, person


def manage_instance_new_instance(instance_state, *add_text):
    mes = ''
    if len(add_text) > 0:
        mes += add_text[0]
    instance_state.change_state(ChangeState.awaiting_uid)
    mes += all_instances_message('Please write instance ID to manage:\n')
    keyboard = [['Back', f'{nav.manage_instances_menu}']]
    return mes, keyboard





# def manage_instance_await_uid(instance_state, *add_text):
#     instance_state.change_state(ChangeState.awaiting_manage_instance)
#     mes = ''
#     if len(add_text) > 0:
#         mes += add_text[0]
#     mes += instance_message(instance_state.uid)
#
#     keyboard = [['Change name', f'{nav.find_instance}1'],
#                 ['Delete instance', f'{nav.find_instance}2'],
#                 ['Back', f'{nav.manage_instances_menu}']]
#
#     return mes, keyboard


def manage_instance_await_manage_instance(instance_state, user_state):
    if user_state == '1':
        return await_text(instance_state)
    elif user_state == '2':
        return delete_instance(instance_state)


def await_text(instance_state):
    instance_state.change_state(ChangeState.awaiting_text)
    mes = f"Please write new instance name:"
    return mes, None


def update_text(instance_state, text):
    instance_state.change_state(ChangeState.updating_text)
    logging.warning('Here')
    instance_state.change_text(text)
    return instance_state





def updating_existing_instance(instance_state):
    db.update_existing_instance(instance_state)
    update_active_instances(instance_state)