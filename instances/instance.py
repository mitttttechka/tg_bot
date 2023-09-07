import logging

from database import db
from instances import user, units, task
from datetime import datetime
import State as ChangeState


class Instance:

    def __init__(self):
        self.uid = None
        self.text = None
        self.state = ChangeState.empty
        self.type = None
        self.sorting = {}
        self.current_task = None

    def get_info(self):
        ans = db.get_info_by_id(self.uid, self.type)
        if len(ans) > 0:
            return ans
        else:
            return []

    def change_id(self, uid):
        self.uid = uid

    def change_state(self, state):
        self.state = state

    def change_text(self, text):
        self.text = text

    def change_task(self, task_id):
        self.current_task = task_id

    def get_sort(self):
        if not self.sorting:
            info = self.get_info()
            sort = {}
            for row in info:
                sort[row[1]] = row[2]
            self.sorting = sort
        return self.sorting

    def change_sorting(self, new_sort):
        self.sorting = new_sort

    def update_active_instances(self):
        units.Units.unit_dict[self.type].statics[self.uid] = self
        # TODO add async update to database

    def await_add_task_middle_instance(self, *add_text):
        self.change_state(ChangeState.await_add_task_middle)
        mes = ''
        if len(add_text):
            mes += add_text[0]
        mes += 'Write Task ID to add:\n'
        mes = all_instances_message(task.Task, mes)  # task.all_tasks_message(mes)
        return mes, None

    def sort_message_instance(self, *add_text):
        sort = self.get_sort()
        mes = ''
        if add_text and len(add_text[0]):
            mes += add_text[0][0]
        if len(sort) == 0:
            mes = f'No tasks added yet.'
        else:
            mes += 'Sort: Task ID\n'
        for i in range(len(sort)):
            mes += f'{i}: task {sort[i]}\n'
        return mes

    def update_add_task_middle_instance(self, text):
        try:
            task_id = int(text)
        except ValueError:
            return self.await_add_task_middle_instance('Incorrect Task ID. Please try again\n')
        if not instance_exists(task_id, task.Task):  # task.task_exists(task_id):
            return self.await_add_task_middle_instance('Task ID doesn\'t exist. Please try again\n')
        self.change_state(ChangeState.update_add_task_middle)
        return task_id

    def await_remove_task_instance(self, *add_text):
        self.change_state(ChangeState.await_remove_task)
        mes = ''
        if len(add_text):
            if isinstance(add_text[0], str):
                mes += add_text[0]
        mes += self.sort_message_instance(f'Write task position to remove from the {self.type.__name__}:\n')
        return mes, None

    def remove_position_from_sort_instance(self, position):
        sort = self.get_sort()
        new_sort = {}

        if position >= len(sort):
            position = len(sort) - 1
        if position < 0:
            position = 0

        for i in range(position):
            new_sort[i] = sort[i]
        for i in range(position + 1, len(sort)):
            new_sort[i - 1] = sort[i]

        return new_sort

    def await_resort_existing_instance(self, *add_text):
        answer = self.await_remove_task_instance(add_text)
        self.change_state(ChangeState.await_resort_existing)
        return answer

    def update_resort_existing_instance(self, text):
        try:
            position = int(text)
        except ValueError:
            return self.await_resort_existing_instance('Incorrect position. Please try again\n')
        sort = self.get_sort()
        task_id = sort[position]
        return task_id

    def update_change_current_instance(self, user_state):
        if user_state[2] == '3':
            return self.await_add_task_middle_instance()
        elif user_state[2] == '4':
            return self.await_remove_task_instance()
        elif user_state[2] == '5':
            return self.await_resort_existing_instance()

    def update_set_position(self, text):
        try:
            l_position = int(text)
        except ValueError:
            return self.await_add_task_middle_instance('Incorrect position. Please try again\n')

        sort = self.get_sort()
        new_sort = {}

        if l_position > len(sort):
            l_position = len(sort)
        if l_position < 0:
            l_position = 0

        for i in range(l_position):
            new_sort[i] = sort[i]
        new_sort[l_position] = self.current_task
        for i in range(l_position, len(sort)):
            new_sort[i + 1] = sort[i]

        self.change_sorting(new_sort)
        return self

    def await_set_position(self, *add_text):
        self.change_state(ChangeState.await_set_position)
        mes = ''
        if len(add_text):
            mes += add_text[0]
        # TODO if no tasks in sort don't ask
        mes += f'To which position do you want to insert task {self.current_task}\n'
        mes += self.sort_message_instance()
        return mes, None

    def update_remove_task(self, text):
        try:
            position = int(text)
        except ValueError:
            return self.await_remove_task_instance('Incorrect position. Please try again\n')

        new_sort = self.remove_position_from_sort_instance(position)

        return self.change_sorting(new_sort)

    # TODO opportunity to input several tasks
    def update_new_sort_instance(self, text):
        answer = self.type.update_add_task_middle(self, text)
        if not isinstance(answer, self.type):
            return self, 'Incorrect Task ID. Please try again\n'
        if self.get_sort() is None:
            sort_id = 0
        else:
            sort_id = len(self.get_sort())
        self.update_set_position(sort_id + 1)
        return self, 'Task was added to the new sorting.\n'

    def update_instance(self, user_state):
        self.change_state(ChangeState.update_instance)
        self.change_id(int(user_state[2:5]))
        return self


def get_instance(uid, unit_type):
    try:
        uid = int(uid)
    except ValueError:
        return None
    if uid in units.Units.unit_dict[unit_type].statics.keys():
        return units.Units.unit_dict[unit_type].statics[uid]
    instances_array = db.get_info_by_id(uid, unit_type)
    if len(instances_array) > 0:
        db_instance = unit_type.db_answer_to_instances_array(instances_array)
        db_instance[0].update_active_instances()
        return db_instance[0]
    else:
        return None


def get_all_instances_dict(unit_type):
    if units.Units.unit_dict[unit_type].last_updated is None \
            or (datetime.now() - units.Units.unit_dict[unit_type].last_updated).seconds > 120:
        instances_array = db.get_all_instances(unit_type)
        units.Units.unit_dict[unit_type].last_updated = datetime.now()
        instances = unit_type.db_answer_to_instances_array(instances_array)
        for single_instance in instances:
            single_instance.update_active_instances()
    return units.Units.unit_dict[unit_type].statics


def get_all_instances(unit_type):
    return get_all_instances_dict(unit_type).values()


def form_instances_message(instances, *add_text):
    mes = ''
    logging.debug(f'add_text length: {len(add_text)}')
    if len(add_text[0]) > 0:
        mes += add_text[0][0]
    for s_instance in instances:
        mes += f'ID: {s_instance.uid}. {s_instance.text}\n'
    return mes


def find_instance_in_static(uid: int, unit_type):
    if uid in units.Units.unit_dict[unit_type].statics.keys():
        return uid
    return -1


def instance_exists(uid, unit_type):
    if get_instance(uid, unit_type) is not None:
        return True
    return False


def instance_message(uid, unit_type, *add_text):
    instances = get_instance(uid, unit_type)
    return form_instances_message([instances], add_text)


def get_name(uid, unit_type):
    instance = get_instance(uid, unit_type)
    if instance is not None:
        return instance.text
    return None


def delete_instance(instance_state):
    db.delete_instance(instance_state.uid, instance_state.type)
    index = find_instance_in_static(instance_state.uid, instance_state.type)
    units.Units.unit_dict[instance_state.type].statics.pop(index)
    return None


def get_existing_instance(instance_state, uid, unit_type):
    if not instance_exists(uid, unit_type):
        return None  # manage_instance_new_instance(instance_state, 'Task doesn\'t exist. Please try again.\n')
    instance_state.update(int(uid))
    return instance_state


def all_instances_message(unit_type, *add_text):
    instances = get_all_instances(unit_type)
    return form_instances_message(instances, add_text)


def initiate_instance(user_id, user_state, unit_type):
    person = user.get_user(user_id)
    logging.debug(f"User {person.user_id} is here!. User state: {user_state}")
    if not isinstance(person.working_on, unit_type):
        new_instance = unit_type()
        person.working_on = new_instance

    instance_state = person.working_on
    logging.debug(f"Task_state: {instance_state.uid}")
    return instance_state, person
