import logging

from database import db
from instances import user, question
import menu_navigation as nav


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
    create_question = 13,
    awaiting_task_id = 14,
    awaiting_manage_task = 15


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


def add_new_section(text):
    db.add_new_section(text)


def get_all_sections():
    sections = db.get_all_sections()
    print(sections)
    return sections


def task_exists(task_id):
    s_task = db.get_task_by_id(task_id)
    if len(s_task) > 0:
        return True
    else:
        return False


def add_task(user_id, user_state, *data):
    task_state, person = initiate_task(user_id, user_state)

    # Received section_id in message, asks for text
    if task_state.state == ChangeState.awaiting_section_id:
        task_state = update_section_id(task_state, user_state)
        return await_text(task_state)

    # Task state is empty, first question
    if task_state.state == ChangeState.new_task:
        return await_section_id(task_state)

    # Receiving text, asks for picture
    elif task_state.state == ChangeState.awaiting_text:
        task_state = update_text(task_state, data[0][0])

        return await_picture_nec(task_state)

    elif task_state.state == ChangeState.awaiting_picture_nec:
        task_state = updating_picture(task_state, data[0][0])
        return await_question(task_state)

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


# TODO make back buttons (either to menu, then empty current_task for users,
# when pressing back, either to the previous point
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
        updating_existing_task(task_state)
        return manage_task_await_task_id(task_state, 'Text was changed.\n')

    if task_state.state == ChangeState.awaiting_picture_nec:
        task_state = updating_picture(task_state, data[0][0])
        updating_existing_task(task_state)
        return manage_task_await_task_id(task_state, 'Picture was changed.\n')

    if task_state.state == ChangeState.awaiting_question:
        task_state = update_question(task_state, user_state[2])
        if task_state.question == 'TRUE':
            task_state.change_state(ChangeState.create_question)
            return question.add_question(user_id, '70')  # TODO change because redirects to add
        else:
            return manage_task_await_task_id(task_state, 'Question was changed.\n')

    if task_state.state == ChangeState.awaiting_section_id:
        task_state = update_section_id(task_state, user_state)
        updating_existing_task(task_state)
        return manage_task_await_task_id(task_state, 'Section was changed.\n')


def manage_task_new_task(task_state, *add_text):
    mes = ''
    if len(add_text) > 0:
        mes += add_text[0]
    task_state.change_state(ChangeState.awaiting_task_id)
    mes += all_tasks_message('Please write Task ID to manage:\n')
    return mes, None


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
                ['Back', f'{nav.admin_menu}']]

    return mes, keyboard


def manage_task_await_manage_task(task_state, user_state):
    if user_state == '1':
        return await_text(task_state)
    elif user_state == '2':
        return await_picture_nec(task_state)
    elif user_state == '3':
        return await_question(task_state)
    elif user_state == '4':
        return await_section_id(task_state)
    elif user_state == '5':
        return delete_task(task_state)


def delete_task(task_state):
    return 1


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


def updating_existing_task(task_state):
    db.update_existing_task(task_state)
    return None


def submitting_new_task(task_state, person):
    new_task_id = db.add_new_task(task_state)
    if person.working_on_add is not None and type(person.working_on_add) == question.Question:
        person.working_on_add.change_task_id(new_task_id)
        person.working_on_add.set_question_settings()
        person.working_on_add = None
    person.working_on = None
    user.update_active_users(person)
    return adding_complete(task_state)


def await_section_id(task_state):
    task_state.change_state(ChangeState.awaiting_section_id)
    sections = get_all_sections()
    keyboard = []
    for section in sections:
        button = section[1], f'59{str(section[0]).zfill(3)}'
        keyboard.append(button)
    keyboard.append(("Back", "52"))

    mes = f"Please select section for the task:"
    return mes, keyboard


def update_section_id(task_state, user_state):
    task_state.change_state(ChangeState.updating_section_id)
    task_state.change_section(int(user_state[2:5]))
    return task_state


def await_text(task_state):
    # TODO Change section_id to section name
    task_state.change_state(ChangeState.awaiting_text)
    mes = f"Please write task context for section {task_state.section_id}:"
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


def await_question(task_state):
    task_state.change_state(ChangeState.awaiting_question)
    keyboard = []
    yes_but = "Yes", "591"
    no_but = "No", "592"
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
    tasks = get_task_by_id(task_id)
    return form_tasks_message(tasks, add_text)


# TODO sort by task ID
def get_all_tasks():
    tasks_array = db.get_all_tasks()
    return db_answer_to_tasks_array(tasks_array)


def get_task_by_id(task_id):
    tasks_array = db.get_task_by_id(task_id)
    return db_answer_to_tasks_array(tasks_array)


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
