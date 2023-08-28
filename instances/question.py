import logging

from instances import task, user
from database import db
import menu_navigation as nav


class QuestionType:
    open_question = 'Open question'
    single_test = 'Test with single answer'
    multiple_test = 'Test with multiple answers'
    none = 'None'


class QuestionState:
    none = 0
    await_menu = 1
    await_add_correct = 2
    update_add_correct = 3
    await_add_incorrect = 4
    update_add_incorrect = 5
    await_save = 6
    update_dave = 7
    normal = 8


class Question:
    def __init__(self, *task_id):
        if len(task_id) == 1:
            self.task_id = int(task_id[0])
            correct, incorrect = self.get_question_info()
            self.correct_answers = correct
            self.incorrect_answers = incorrect
            self.question_type = self.get_question_type()
            self.question_text = None
            self.state = QuestionState.none
        else:
            self.task_id = None
            self.correct_answers = []
            self.incorrect_answers = []
            self.question_type = QuestionType.none
            self.question_text = None
            self.state = QuestionState.none

    def get_question_info(self):
        answers = db.get_answers(self.task_id)
        correct = []
        incorrect = []
        for row in answers:
            if row[1] == 'TRUE':
                correct.append(row[0])
            else:
                incorrect.append(row[0])
        return correct, incorrect

    def get_question_type(self):
        if len(self.correct_answers) == 1 and len(self.incorrect_answers) == 0:
            return QuestionType.open_question
        elif len(self.correct_answers) == 1 and len(self.incorrect_answers) > 0:
            return QuestionType.single_test
        elif len(self.correct_answers) > 1 and len(self.incorrect_answers) > 0:
            return QuestionType.multiple_test
        return QuestionType.none

    def change_state(self, q_state):
        self.state = q_state

    def change_task_id(self, task_id):
        self.task_id = task_id

    def update_question_type(self):
        self.question_type = self.get_question_type()

    def add_correct_answer(self, answer):
        self.correct_answers.append(answer)
        self.update_question_type()

    def add_incorrect_answer(self, answer):
        self.incorrect_answers.append(answer)
        self.update_question_type()

    def set_question_settings(self):
        db.set_answers(self.task_id, self.correct_answers, self.incorrect_answers)

    def message_representation(self):
        mes = ''
        mes += f'Q: {self.question_text}\nCorrect answers:\n'
        for ans in self.correct_answers:
            mes += f'{ans}\n'
        mes += f'Incorrect answers:\n'
        for ans in self.incorrect_answers:
            mes += f'{ans}\n'
        mes += f'Question type: {self.question_type}'
        return mes


def add_question(user_id, user_state, *data):
    person: user.User = user.get_user(user_id)
    logging.debug(f"User {person.user_id} is here!. User state: {user_state}")

    # creating empty Question class if begins to create
    if person.working_on_add is None or type(person.working_on_add) is not Question:
        new_question = Question()
        new_question.question_text = get_question_text_for_new_task(person)
        person.working_on_add = new_question

    question_state: Question = person.working_on_add

    if question_state.state == QuestionState.none:
        return await_menu(question_state)

    if question_state.state == QuestionState.await_menu:
        if user_state[2] == '1':
            return await_add_correct_answer(question_state)
        elif user_state[2] == '2':
            return await_add_incorrect_answer(question_state)
        elif user_state[2] == '3':
            saved = await_save_answers(question_state)
            if not saved:
                err_mes = 'Not possible to save without at least 1 correct answer.'
                return await_menu(question_state, err_mes)

            if type(person.working_on) == task.Task:
                if person.working_on.state == task.ChangeState.adding_question_in_manage:
                    person.working_on.change_state(task.ChangeState.submit_change_question)
                    reply = task.manage_task(user_id, user_state)
                    return reply[0], reply[1]
                else:
                    person.working_on.change_state(task.ChangeState.to_submit)
                    reply = task.add_task(user_id, user_state)
                    return reply[0], reply[1], True
        elif user_state[2] == '4':
            person.working_on_add = None
            if person.working_on is not None and type(person.working_on) == task.Task:
                if person.working_on.state == task.ChangeState.adding_question_in_manage:
                    return task.await_question(person.working_on, nav.change_existing_task)
                else:
                    return task.await_question(person.working_on, nav.add_task_menu)

    if question_state.state == QuestionState.await_add_correct:
        add_text = ''
        if len(data[0][0]) > 0:
            question_state.add_correct_answer(data[0][0])
        else:
            add_text = 'Empty text. Please try again.'
        return await_menu(question_state, add_text)
    if question_state.state == QuestionState.await_add_incorrect:
        add_text = ''
        if len(data[0][0]) > 0:
            question_state.add_incorrect_answer(data[0][0])
        else:
            add_text = 'Empty text. Please try again.'
        return await_menu(question_state, add_text)


def get_question_text_for_new_task(person: user.User) -> str:
    if person.working_on is None or type(person.working_on) is not task.Task:
        return ''
    task_cur: task.Task = person.working_on
    return task_cur.text


# TODO check unsaved data and additional question
def await_menu(question_state: Question, *add_text):
    question_state.change_state(QuestionState.await_menu)
    mes = ''
    if len(add_text) > 0:
        mes += f'{add_text[0]}\n'
    mes += question_state.message_representation()
    keyboard = [['Add correct answer', '701'],
                ['Add incorrect answer', '702'],
                ['Save question settings', '703'],
                ['Back (ALL UNSAVED DATA WILL BE LOST)', '704']]
    return mes, keyboard


def await_add_correct_answer(question_state: Question):
    question_state.change_state(QuestionState.await_add_correct)
    mes = 'Please write correct answer:\n'
    return mes, None


def await_add_incorrect_answer(question_state: Question):
    question_state.change_state(QuestionState.await_add_incorrect)
    mes = 'Please write incorrect answer:\n'
    return mes, None


def await_save_answers(question_state: Question):
    question_state.change_state(QuestionState.await_save)
    if len(question_state.correct_answers) > 0:
        #question_state.set_question_settings()
        return True
    return False
