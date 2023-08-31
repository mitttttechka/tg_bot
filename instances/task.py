import logging

from database import db
from instances import user, question, section, instance
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
    create_question = 13
    awaiting_task_id = 14
    awaiting_manage_task = 15
    adding_question_in_manage = 16
    submit_change_question = 17


class Task(instance.Instance):

    def __init__(self, *task_id):
        super().__init__()
        self.type = Task
        if len(task_id) == 1:
            self.uid = task_id[0]
            info = self.get_info()
            self.text = info[1]
            self.picture_link = info[2]
            self.question = info[3]
            self.section_id: int = int(info[4])
            self.state = ChangeState.normal
        elif len(task_id) == 5:
            self.uid = task_id[0]
            self.text = task_id[1]
            self.picture_link = task_id[2]
            self.question = task_id[3]
            self.section_id = task_id[4]
            self.state = ChangeState.normal
        else:
            self.picture_link = None
            self.question = None
            self.section_id = None
            self.state = ChangeState.new_task

    def update(self, task_id):
        self.uid = task_id
        info = self.get_info()
        self.text = info[1]
        self.picture_link = info[2]
        self.question = info[3]
        self.section_id: int = int(info[4])
        self.state = ChangeState.normal
        self.update_active_instances()

    def change_section(self, section_id):
        self.section_id = section_id

    def change_picture(self, link):
        self.picture_link = link

    def change_question(self, need):
        self.question = need

    def db_answer_to_instances_array(self, tasks_array):
        tasks = []
        for task in tasks_array:
            t = Task(task[0], task[1], task[2], task[3], task[4])
            tasks.append(t)
        return tasks

    def manage_task_new_task(self, *add_text):
        mes = ''
        if len(add_text) > 0:
            mes += add_text[0]
        self.change_state(ChangeState.awaiting_task_id)
        mes += instance.all_instances_message(Task, 'Please write Task ID to manage:\n')
        keyboard = [['Back', f'{nav.manage_tasks_menu}']]
        return mes, keyboard

    def manage_task_await_task_id(self, *add_text):
        self.change_state(ChangeState.awaiting_manage_task)
        mes = ''
        if len(add_text) > 0:
            mes += add_text[0]
        mes += instance.instance_message(self.uid, Task)

        keyboard = [['Change text', f'{nav.change_existing_task}1'],
                    ['Change picture', f'{nav.change_existing_task}2'],
                    ['Change question', f'{nav.change_existing_task}3'],
                    ['Change section', f'{nav.change_existing_task}4'],
                    ['Delete task', f'{nav.change_existing_task}5'],
                    ['Back', f'{nav.manage_tasks_menu}']]

        return mes, keyboard

    def manage_task_await_manage_task(self, user_state):
        if user_state == '1':
            return self.await_text()
        elif user_state == '2':
            return self.await_picture_nec()
        elif user_state == '3':
            return self.await_question(nav.change_existing_task)
        elif user_state == '4':
            return self.await_section_id(nav.change_existing_task)
        elif user_state == '5':
            instance.delete_instance(self)
            return self.manage_task_new_task('Task was deleted. \n')

    def updating_existing_task(self, person):
        db.update_existing_task(self)
        self.update_active_instances()
        if person.working_on_add is not None and type(person.working_on_add) == question.Question:
            person.working_on_add.change_task_id(self.uid)
            person.working_on_add.set_question_settings()
            person.working_on_add = None
        return None

    def submitting_new_task(self, person):
        new_task_id = db.add_new_task(self)
        self.change_id(new_task_id)
        self.update_active_instances()
        if person.working_on_add is not None and type(person.working_on_add) == question.Question:
            person.working_on_add.change_task_id(new_task_id)
            person.working_on_add.set_question_settings()
            person.working_on_add = None
        person.working_on = None
        user.update_active_users(person)
        return self.adding_complete()

    def await_section_id(self, menu_section):
        self.change_state(ChangeState.awaiting_section_id)
        sections = instance.get_all_instances(section.Section)
        keyboard = []
        for s_section in sections:
            button = s_section.text, f'{menu_section}{str(s_section.uid).zfill(3)}'
            keyboard.append(button)
        keyboard.append(("Back", "52"))

        mes = f"Please select section for the task:"
        return mes, keyboard

    def update_section_id(self, user_state):
        self.change_state(ChangeState.updating_section_id)
        self.change_section(int(user_state[2:5]))
        return self

    def await_text(self):
        self.change_state(ChangeState.awaiting_text)
        mes = f"Please write task context for section {instance.get_name(self.section_id, section.Section)}:"
        return mes, None

    def update_text(self, text):
        self.change_state(ChangeState.updating_text)
        self.change_text(text)
        return self

    def await_picture_nec(self):
        # TODO make keyboard for picture adding
        self.change_state(ChangeState.awaiting_picture_nec)
        mes = f"Text \'{self.text}\' has been added. Do you want to add picture?\n" \
              f"Please send photo or type \'No\'"
        return mes, None

    def updating_picture(self, link):
        self.change_state(ChangeState.updating_picture)
        if link.lower() == 'no':
            self.change_picture('NONE')
        else:
            self.change_picture(link)
        return self

    def await_question(self, menu_section):
        self.change_state(ChangeState.awaiting_question)
        keyboard = []
        yes_but = "Yes", f"{menu_section}1"
        no_but = "No", f"{menu_section}2"
        keyboard.append(yes_but)
        keyboard.append(no_but)

        mes = f"Is the task is question and requires answer?"
        return mes, keyboard

    def update_question(self, text):
        self.change_state(ChangeState.updating_question)
        if text == '1':
            self.change_question('TRUE')
        else:
            self.change_question('FALSE')
        return self

    def adding_complete(self):
        mes = f"Task to section {self.section_id} was added.\nText: \'{self.text}\'" \
              f"\nQuestion?: {self.question} \nNeeds picture?: {self.picture_link}"
        return mes, None, True

    def get_existing_task(self, text):
        if not instance.instance_exists(text, Task):
            return self.manage_task_new_task('Task doesn\'t exist. Please try again.\n')
        self.update(int(text))
        return self


def add_task(user_id, user_state, *data):
    task_state, person = instance.initiate_instance(user_id, user_state, Task)

    # Received section_id in message, asks for text
    if task_state.state == ChangeState.awaiting_section_id:
        task_state.update_section_id(user_state)
        return task_state.await_text()

    # Task state is empty, first question
    if task_state.state == ChangeState.new_task:
        return task_state.await_section_id(nav.add_task_menu)

    # Receiving text, asks for picture
    elif task_state.state == ChangeState.awaiting_text:
        task_state.update_text(data[0][0])
        return task_state.await_picture_nec()

    elif task_state.state == ChangeState.awaiting_picture_nec:
        task_state.updating_picture(data[0][0])
        return task_state.await_question(nav.add_task_menu)

    elif task_state.state == ChangeState.awaiting_question:
        task_state.update_question(user_state[2])
        if task_state.question == 'TRUE':
            task_state.change_state(ChangeState.create_question)
            return question.add_question(user_id, '70')  # here or from menu?
        else:
            task_state.change_state(ChangeState.to_submit)

    if task_state.state == ChangeState.to_submit:
        return task_state.submitting_new_task(person)

    return None


def manage_task(user_id, user_state, *data):
    task_state, person = instance.initiate_instance(user_id, user_state, Task)

    if task_state.state == ChangeState.new_task:
        return task_state.manage_task_new_task()

    if task_state.state == ChangeState.awaiting_task_id:
        task_state = task_state.get_existing_task(data[0][0])
        return task_state.manage_task_await_task_id()

    if task_state.state == ChangeState.awaiting_manage_task:
        return task_state.manage_task_await_manage_task(user_state[2])

    if task_state.state == ChangeState.awaiting_text:
        task_state.update_text(data[0][0])
        task_state.updating_existing_task(person)
        return task_state.manage_task_await_task_id('Text was changed.\n')

    if task_state.state == ChangeState.awaiting_picture_nec:
        task_state.updating_picture(data[0][0])
        task_state.updating_existing_task(person)
        return task_state.manage_task_await_task_id('Picture was changed.\n')

    if task_state.state == ChangeState.awaiting_question:
        task_state.update_question(user_state[2])
        if task_state.question == 'TRUE':
            task_state.change_state(ChangeState.adding_question_in_manage)
            return question.add_question(user_id, '70')
        task_state.change_state(ChangeState.submit_change_question)

    if task_state.state == ChangeState.submit_change_question:
        task_state.updating_existing_task(person)
        return task_state.manage_task_await_task_id('Question was changed.\n')

    if task_state.state == ChangeState.adding_question_in_manage:
        task_state.updating_existing_task(person)
        return task_state.manage_task_await_task_id('Picture was changed.\n')

    if task_state.state == ChangeState.awaiting_section_id:
        task_state.update_section_id(user_state)
        task_state.updating_existing_task(person)
        return task_state.manage_task_await_task_id('Section was changed.\n')
