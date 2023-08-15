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
        if len(task_id) > 0:
            self.task_id = task_id
            info = self.get_task_info()
            self.text = info[1]
            self.picture_link = info[2]
            self.question = info[3]
            self.section_id: int = int(info[4])
            self.change_state = ChangeState.normal
        else:
            self.task_id = None
            self.text = None
            self.picture_link = None
            self.question = None
            self.section_id = None
            self.change_state = ChangeState.new_task

    def get_task_info(self):
        return db.get_task(self.task_id)

    def change_state(self, state, person):
        self.change_state = state
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


# TODO refactor to multiple classes
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
    # Change state - updating section id
    if task_state.change_state == ChangeState.awaiting_section_id:#if user_state is not None and len(user_state) == 5:
        # #task_state.change_state = ChangeState.updating_section_id
        task_state = task_state.change_state(ChangeState.updating_section_id, person)
        task_state = task_state.change_section(int(user_state[2:5]), person)
        # #task_state.section_id = int(user_state[2:5])
        #person.working_on = task_state
        #user.update_active_users(person)
        # Change state = awaiting text
        # TODO Change section_id to section name
        #task_state.change_state = ChangeState.awaiting_text
        task_state = task_state.change_state(ChangeState.awaiting_text, person)
        mes = f"Please write task context for section {task_state.section_id}:"
        return mes, None

    # Task state is empty, first question
    # change_state = null
    if task_state.change_state == ChangeState.new_task: #if task_state.section_id is None:
        ##task_state.change_state = ChangeState.awaiting_section_id

        sections = get_all_sections()
        keyboard = []
        for section in sections:
            button = section[1], f'59{str(section[0]).zfill(3)}'
            keyboard.append(button)
        keyboard.append(("Back", "52"))

        mes = f"Please select section for the task:"
        return mes, keyboard

    # Receiving text, asks for picture
    # change_state = updating text
    elif task_state.change_state == ChangeState.awaiting_text: #elif task_state.text is None:
        #task_state.change_state = ChangeState.updating_text
        task_state = task_state.change_state(ChangeState.updating_text, person)
        logging.warning('Here')
        task_state = task_state.change_text(data[0][0], person)
        #task_state.text = data[0][0]
        #person.working_on = task_state
        #user.update_active_users(person)
        # change_state = awaiting picture nec
        # TODO make keyboard for picture adding
        #task_state.change_state = ChangeState.awaiting_picture_nec
        task_state = task_state.change_state(ChangeState.awaiting_picture_nec, person)
        mes = f"Text \'{task_state.text}\' has been added. Do you want to add picture?"
        return mes, None

    # TODO add picture support
    # updating picture
    elif task_state.change_state == ChangeState.awaiting_picture_nec: #elif task_state.picture_link is None:
        #task_state.change_state = ChangeState.updating_picture
        task_state = task_state.change_state(ChangeState.updating_picture, person)
        if data[0][0].lower() == 'no':
            task_state = task_state.change_picture('NONE', person)
            #task_state.picture_link = 'NONE'
        else:
            #task_state.picture_link = data[0][0]
            task_state = task_state.change_picture(data[0][0], person)
        #person.working_on = task_state
        #user.update_active_users(person)

        # change state awaiting question
        #task_state.change_state = ChangeState.awaiting_question
        task_state = task_state.change_state(ChangeState.awaiting_question, person)
        keyboard = []
        yes_but = "Yes", "591"
        no_but = "No", "592"
        keyboard.append(yes_but)
        keyboard.append(no_but)

        mes = f"Is the task is question and requires answer?"
        return mes, keyboard

    # TODO add question type functional
    # change state updating question
    elif task_state.change_state == ChangeState.awaiting_question: #elif task_state.question is None:
        #task_state.change_state = ChangeState.updating_question
        task_state = task_state.change_state(ChangeState.updating_question, person)
        if user_state[2] == '1':
            #task_state.question = 'TRUE'
            task_state = task_state.change_question('TRUE', person)
        else:
            #task_state.question = 'FALSE'
            task_state = task_state.change_question('FALSE', person)

        #person.working_on = None
        #user.update_active_users(person)

        # change state updating in db
        db.add_new_task(task_state)

        # change state complete
        mes = f"Task to section {task_state.section_id} was added.\nText: \'{task_state.text}\'" \
            f"\nQuestion?: {task_state.question} \nNeeds picture?: {task_state.picture_link}"
        return mes, None, True

    return "Not possible to add task", None

