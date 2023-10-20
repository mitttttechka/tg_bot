y = "a;b;c;"
z = y.split(';')
print(len(z))
# mun_list = [1, 2, 3, 4, 5]
# mun_list.remove(2)
# print(mun_list)
# a = reversed(list(range(1,11)))
# print(a)
# import random
# symbols = [*[a for a in range(48, 58)], *[a for a in range(97, 123)], *[a for a in range(65, 91)]]
# code = ''
# for i in range(8):
#     code += chr(symbols[random.randint(0, len(symbols))])
# print(code)
# a = ((2,),)
# print(*a)


'''
class A:
    def __init__(self):
        self.a = 3

    def increase(self):
        self.a += 1 
        return None


class B:
    def __init__(self, d):
        self.a = d


d = A()
c = B(d)
print(c.a.a)
print(d.a)
d.increase()
print(c.a.a)
print(d.a)


import logging

from database import db
from instances import user, question, section
import menu_navigation as nav
from datetime import datetime

static_tasks = []


class LastUpdated:
    dt_all_tasks_updated = None


class ChangeState:
    new_task = 1
    awaiting_section_id = 2
    updating_section_id = 3
    awaiting_text = 4
    updating_text = 5
    awaiting_picture_nec = 6
    awaiting_picture_file = 7
    updating_picture = 8
    awaiting_question = 9
    updating_question = 10
    normal = 11
    to_submit = 12
    create_question = 13
    awaiting_task_id = 14
    awaiting_manage_task = 15
    adding_question_in_manage = 16
    submit_change_question = 17


class Task:

    def __init__(self, *task_id):
        if len(task_id) == 1:
            self.task_id = task_id[0]
            info = self.get_task_info()
            self.text = info[1]
            self.picture_link = info[2]
            self.question = info[3]
            self.section_id: int = int(info[4])
            self.state = ChangeState.normal
        elif len(task_id) == 5:
            self.task_id = task_id[0]
            self.text = task_id[1]
            self.picture_link = task_id[2]
            self.question = task_id[3]
            self.section_id = task_id[4]
            self.state = ChangeState.normal
        else:
            self.task_id = None
            self.text = None
            self.picture_link = None
            self.question = None
            self.section_id = None
            self.state = ChangeState.new_task

    def get_task_info(self):
        return db.get_task_by_id(self.task_id)[0]

    def update(self, task_id):
        self.task_id = task_id
        info = self.get_task_info()
        self.text = info[1]
        self.picture_link = info[2]
        self.question = info[3]
        self.section_id: int = int(info[4])
        self.state = ChangeState.normal
        update_active_tasks(self)

    def change_id(self, task_id):
        self.task_id = task_id

    def change_state(self, state):
        self.state = state

    def change_section(self, section):
        self.section_id = section

    def change_text(self, text):
        self.text = text

    def change_picture(self, link):
        self.picture_link = link

    def change_question(self, need):
        self.question = need


def get_task(task_id):
    try:
        task_id = int(task_id)
    except:
        return None
    has_task = find_task_in_static(task_id)
    if has_task != -1:
        return static_tasks[has_task]
    tasks_array = db.get_task_by_id(task_id)
    if len(tasks_array) > 0:
        db_task = db_answer_to_tasks_array(tasks_array)
        update_active_tasks(db_task[0])
        return db_task[0]
    else:
        return None


def find_task_in_static(task_id):
    for i in range(len(static_tasks)):
        if static_tasks[i].task_id == task_id:
            return i
    return -1


def update_active_tasks(task):
    index = find_task_in_static(task.task_id)
    if index == -1:
        static_tasks.append(task)
        static_tasks.sort(key= lambda x: x.task_id, reverse=False)
    else:
        static_tasks[index] = task
    # TODO add async update to database


def task_exists(task_id):
    if get_task(task_id) is not None:
        return True
    return False


def add_task(user_id, user_state, *data):
    task_state, person = initiate_task(user_id, user_state)

    # Received section_id in message, asks for text
    if task_state.state == ChangeState.awaiting_section_id:
        task_state = update_section_id(task_state, user_state)
        return await_text(task_state)

    # Task state is empty, first question
    if task_state.state == ChangeState.new_task:
        return await_section_id(task_state, nav.add_task_menu)

    # Receiving text, asks for picture
    elif task_state.state == ChangeState.awaiting_text:
        task_state = update_text(task_state, data[0][0])

        return await_picture_nec(task_state)

    elif task_state.state == ChangeState.awaiting_picture_nec:
        task_state = updating_picture(task_state, data[0][0])
        return await_question(task_state, nav.add_task_menu)

    elif task_state.state == ChangeState.awaiting_question:
        task_state = update_question(task_state, user_state[2])
        if task_state.question == 'TRUE':
            task_state.change_state(ChangeState.create_question)
            return question.add_question(user_id, '70')  # here or from menu?
        else:
            task_state.change_state(ChangeState.to_submit)

    if task_state.state == ChangeState.to_submit:
        return submitting_new_task(task_state, person)

    return None


def manage_task(user_id, user_state, *data):
    task_state, person = initiate_task(user_id, user_state)

    if task_state.state == ChangeState.new_task:
        return manage_task_new_task(task_state)

    if task_state.state == ChangeState.awaiting_task_id:
        task_state = get_existing_task(task_state, data[0][0])
        return manage_task_await_task_id(task_state)

    if task_state.state == ChangeState.awaiting_manage_task:
        return manage_task_await_manage_task(task_state, user_state[2])

    if task_state.state == ChangeState.awaiting_text:
        task_state = update_text(task_state, data[0][0])
        updating_existing_task(task_state, person)
        return manage_task_await_task_id(task_state, 'Text was changed.\n')

    if task_state.state == ChangeState.awaiting_picture_nec:
        task_state = updating_picture(task_state, data[0][0])
        updating_existing_task(task_state, person)
        return manage_task_await_task_id(task_state, 'Picture was changed.\n')

    if task_state.state == ChangeState.awaiting_question:
        task_state = update_question(task_state, user_state[2])
        if task_state.question == 'TRUE':
            task_state.change_state(ChangeState.adding_question_in_manage)
            return question.add_question(user_id, '70')
        task_state.change_state(ChangeState.submit_change_question)

    if task_state.state == ChangeState.submit_change_question:
        updating_existing_task(task_state, person)
        return manage_task_await_task_id(task_state, 'Question was changed.\n')

    if task_state.state == ChangeState.adding_question_in_manage:
        updating_existing_task(task_state, person)
        return manage_task_await_task_id(task_state, 'Picture was changed.\n')

    if task_state.state == ChangeState.awaiting_section_id:
        task_state = update_section_id(task_state, user_state)
        updating_existing_task(task_state, person)
        return manage_task_await_task_id(task_state, 'Section was changed.\n')


def manage_task_new_task(task_state, *add_text):
    mes = ''
    if len(add_text) > 0:
        mes += add_text[0]
    task_state.change_state(ChangeState.awaiting_task_id)
    mes += all_tasks_message('Please write Task ID to manage:\n')
    keyboard = [['Back', f'{nav.manage_tasks_menu}']]
    return mes, keyboard


def get_existing_task(task_state, text):
    if not task_exists(text):
        return manage_task_new_task(task_state, 'Task doesn\'t exist. Please try again.\n')
    task_state.update(int(text))
    return task_state


def manage_task_await_task_id(task_state, *add_text):
    task_state.change_state(ChangeState.awaiting_manage_task)
    mes = ''
    if len(add_text) > 0:
        mes += add_text[0]
    mes += task_message(task_state.task_id)

    keyboard = [['Change text', f'{nav.change_existing_task}1'],
                ['Change picture', f'{nav.change_existing_task}2'],
                ['Change question', f'{nav.change_existing_task}3'],
                ['Change section', f'{nav.change_existing_task}4'],
                ['Delete task', f'{nav.change_existing_task}5'],
                ['Back', f'{nav.manage_tasks_menu}']]

    return mes, keyboard


def manage_task_await_manage_task(task_state, user_state):
    if user_state == '1':
        return await_text(task_state)
    elif user_state == '2':
        return await_picture_nec(task_state)
    elif user_state == '3':
        return await_question(task_state, nav.change_existing_task)
    elif user_state == '4':
        return await_section_id(task_state, nav.change_existing_task)
    elif user_state == '5':
        return delete_task(task_state)


def delete_task(task_state):
    db.delete_task(task_state.task_id)
    index = find_task_in_static(task_state.task_id)
    static_tasks.pop(index)
    return manage_task_new_task(task_state, 'Task was deleted. \n')


def initiate_task(user_id, user_state):
    person = user.get_user(user_id)
    logging.debug(f"User {person.user_id} is here!. User state: {user_state}")

    # creating empty Task class if begins to create
    if person.working_on is None or type(person.working_on) is not Task:
        new_task = Task()
        person.working_on = new_task

    task_state = person.working_on
    logging.debug(f"Task_state: {task_state.section_id}")
    return task_state, person


def updating_existing_task(task_state, person):
    db.update_existing_task(task_state)
    update_active_tasks(task_state)
    if person.working_on_add is not None and type(person.working_on_add) == question.Question:
        person.working_on_add.change_task_id(task_state.task_id)
        person.working_on_add.set_question_settings()
        person.working_on_add = None
    return None


def submitting_new_task(task_state, person):
    new_task_id = db.add_new_task(task_state)
    task_state.change_id(new_task_id)
    update_active_tasks(task_state)
    if person.working_on_add is not None and type(person.working_on_add) == question.Question:
        person.working_on_add.change_task_id(new_task_id)
        person.working_on_add.set_question_settings()
        person.working_on_add = None
    person.working_on = None
    user.update_active_users(person)
    return adding_complete(task_state)


def await_section_id(task_state, menu_section):
    task_state.change_state(ChangeState.awaiting_section_id)
    sections = section.get_all_sections()
    keyboard = []
    for s_section in sections:
        button = s_section.section_name, f'{menu_section}{str(s_section.section_id).zfill(3)}'
        keyboard.append(button)
    keyboard.append(("Back", "52"))

    mes = f"Please select section for the task:"
    return mes, keyboard


def update_section_id(task_state, user_state):
    task_state.change_state(ChangeState.updating_section_id)
    task_state.change_section(int(user_state[2:5]))
    return task_state


def await_text(task_state):
    task_state.change_state(ChangeState.awaiting_text)
    mes = f"Please write task context for section {section.get_name_for_section(task_state.section_id)}:"
    return mes, None


def update_text(task_state, text):
    task_state.change_state(ChangeState.updating_text)
    logging.warning('Here')
    task_state.change_text(text)
    return task_state


def await_picture_nec(task_state):
    # TODO make keyboard for picture adding
    task_state.change_state(ChangeState.awaiting_picture_nec)
    mes = f"Text \'{task_state.text}\' has been added. Do you want to add picture?\n" \
          f"Please send photo or type \'No\'"
    return mes, None


def updating_picture(task_state, link):
    task_state.change_state(ChangeState.updating_picture)
    if link.lower() == 'no':
        task_state.change_picture('NONE')
    else:
        task_state.change_picture(link)
    return task_state


def await_question(task_state, menu_section):
    task_state.change_state(ChangeState.awaiting_question)
    keyboard = []
    yes_but = "Yes", f"{menu_section}1"
    no_but = "No", f"{menu_section}2"
    keyboard.append(yes_but)
    keyboard.append(no_but)

    mes = f"Is the task is question and requires answer?"
    return mes, keyboard


def update_question(task_state, text):
    task_state.change_state(ChangeState.updating_question)
    if text == '1':
        task_state.change_question('TRUE')
    else:
        task_state.change_question('FALSE')
    return task_state


def adding_complete(task_state):
    mes = f"Task to section {task_state.section_id} was added.\nText: \'{task_state.text}\'" \
          f"\nQuestion?: {task_state.question} \nNeeds picture?: {task_state.picture_link}"
    return mes, None, True


def all_tasks_message(*add_text):
    tasks = get_all_tasks()
    return form_tasks_message(tasks, add_text)


def task_message(task_id, *add_text):
    tasks = get_task(task_id)
    return form_tasks_message([tasks], add_text)


def get_all_tasks():
    if LastUpdated.dt_all_tasks_updated is None or (datetime.now() - LastUpdated.dt_all_tasks_updated).seconds > 120:
        tasks_array = db.get_all_tasks()
        LastUpdated.dt_all_tasks_updated = datetime.now()
        tasks = db_answer_to_tasks_array(tasks_array)
        for single_task in tasks:
            update_active_tasks(single_task)
    return static_tasks


def db_answer_to_tasks_array(tasks_array):
    tasks = []
    for task in tasks_array:
        t = Task(task[0], task[1], task[2], task[3], task[4])
        tasks.append(t)
    return tasks


def form_tasks_message(tasks, *add_text):
    mes = ''
    logging.debug(f'add_text length: {len(add_text)}')
    if len(add_text[0]) > 0:
        mes += add_text[0][0]
    for s_task in tasks:
        mes += f'Task ID: {s_task.task_id}. {s_task.text}\n'
    return mes









import logging

from database import db
from instances import user, question
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


class Section:

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

    def change_text(self, name):
        self.section_name = name


def get_section(section_id):
    try:
        section_id = int(section_id)
    except:
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
        LastUpdated.dt_all_tasks_updated = datetime.now()
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
    for s_task in sections:
        mes += f'Section ID: {s_task.section_id}. {s_task.section_name}\n'
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
    logging.debug(f"Task_state: {section_state.section_id}")
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
        return manage_section_new_section(section_state, 'Task doesn\'t exist. Please try again.\n')
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
'''