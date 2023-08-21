import logging
import db
import user


class ChangeState:
    new_task = 1,
    awaiting_section_id = 2,
    updating_section_id = 3,
    awaiting_text = 4,
    updating_text = 5,
    awaiting_picture_nec = 6,
    awaiting_picture_file = 7,
    updating_picture = 8,
    awaiting_question = 9,
    updating_question = 10,
    normal = 11


class Task:

    def __init__(self, *task_id):
        if len(task_id) == 1:
            self.task_id = task_id
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
        return db.get_task(self.task_id)

    def change_state(self, state, person):
        self.state = state
        person.working_on = self
        user.update_active_users(person)
        return self

    def change_section(self, section, person):
        self.section_id = section
        person.working_on = self
        user.update_active_users(person)
        return self

    def change_text(self, text, person):
        self.text = text
        person.working_on = self
        user.update_active_users(person)
        return self

    def change_picture(self, link, person):
        self.picture_link = link
        person.working_on = self
        user.update_active_users(person)
        return self

    def change_question(self, need, person):
        self.question = need
        person.working_on = self
        user.update_active_users(person)
        return self


def add_new_section(text):
    db.add_new_section(text)


def get_all_sections():
    sections = db.get_all_sections()
    print(sections)
    return sections


def get_all_tasks():
    tasks_array = db.get_all_tasks()
    tasks = []
    for task in tasks_array:
        t = Task(task[0], task[1], task[2], task[3], task[4])
        tasks.append(t)
    return tasks


def task_exists(task_id):
    s_task = db.get_task_by_id(task_id)
    if len(s_task) > 0:
        return True
    else:
        return False


# TODO make back buttons (either to menu, then empty current_task for users,
# when pressing back, either to the previous point
def add_task(user_id, user_state, *data):
    person = user.get_user(user_id)
    logging.debug(f"User {person.user_id} is here!. User state: {user_state}")

    # creating empty Task class if begins to create
    if person.working_on is None or type(person.working_on) is not Task:
        new_task = Task()
        person.working_on = new_task

    task_state = person.working_on
    logging.debug(f"Task_state: {task_state.section_id}")

    # Received section_id in message, asks for text
    if task_state.state == ChangeState.awaiting_section_id:
        task_state = update_section_id(task_state, person, user_state)
        return await_text(task_state, person)

    # Task state is empty, first question
    if task_state.state == ChangeState.new_task:
        return await_section_id(task_state, person)

    # Receiving text, asks for picture
    elif task_state.state == ChangeState.awaiting_text:
        task_state = update_text(task_state, person, data[0][0])
        return await_picture_nec(task_state, person)

    # TODO add picture support
    elif task_state.state == ChangeState.awaiting_picture_nec:
        task_state = updating_picture(task_state, person, data[0][0])
        return await_question(task_state, person)

    # TODO add question type functional
    elif task_state.state == ChangeState.awaiting_question:
        task_state = update_question(task_state, person, user_state[2])

    db.add_new_task(task_state)
    person.working_on = None
    user.update_active_users(person)
    return adding_complete(task_state)


def await_section_id(task_state, person):
    task_state.change_state(ChangeState.awaiting_section_id, person)
    sections = get_all_sections()
    keyboard = []
    for section in sections:
        button = section[1], f'59{str(section[0]).zfill(3)}'
        keyboard.append(button)
    keyboard.append(("Back", "52"))

    mes = f"Please select section for the task:"
    return mes, keyboard


def update_section_id(task_state, person, user_state):
    task_state = task_state.change_state(ChangeState.updating_section_id, person)
    task_state = task_state.change_section(int(user_state[2:5]), person)
    return task_state


def await_text(task_state, person):
    # TODO Change section_id to section name
    task_state = task_state.change_state(ChangeState.awaiting_text, person)
    mes = f"Please write task context for section {task_state.section_id}:"
    return mes, None


def update_text(task_state, person, text):
    task_state = task_state.change_state(ChangeState.updating_text, person)
    logging.warning('Here')
    task_state = task_state.change_text(text, person)
    return task_state


def await_picture_nec(task_state, person):
    # TODO make keyboard for picture adding
    task_state = task_state.change_state(ChangeState.awaiting_picture_nec, person)
    mes = f"Text \'{task_state.text}\' has been added. Do you want to add picture?"
    return mes, None


def updating_picture(task_state, person, link):
    task_state = task_state.change_state(ChangeState.updating_picture, person)
    if link.lower() == 'no':
        task_state = task_state.change_picture('NONE', person)
    else:
        task_state = task_state.change_picture(link, person)
    return task_state


def await_question(task_state, person):
    task_state.change_state(ChangeState.awaiting_question, person)
    keyboard = []
    yes_but = "Yes", "591"
    no_but = "No", "592"
    keyboard.append(yes_but)
    keyboard.append(no_but)

    mes = f"Is the task is question and requires answer?"
    return mes, keyboard


def update_question(task_state, person, text):
    task_state = task_state.change_state(ChangeState.updating_question, person)
    if text == '1':
        task_state = task_state.change_question('TRUE', person)
    else:
        task_state = task_state.change_question('FALSE', person)
    return task_state


def adding_complete(task_state):
    mes = f"Task to section {task_state.section_id} was added.\nText: \'{task_state.text}\'" \
          f"\nQuestion?: {task_state.question} \nNeeds picture?: {task_state.picture_link}"
    return mes, None, True


def all_tasks_message(*add_text):
    tasks = get_all_tasks()
    mes = ''
    logging.debug(f'add_text length: {len(add_text)}')
    if len(add_text) > 0:
        mes += add_text[0]
    for s_task in tasks:
        mes += f'Task ID: {s_task.task_id}. Section: {s_task.section_id} Question: {s_task.question}\n{s_task.text}\n'
    return mes
