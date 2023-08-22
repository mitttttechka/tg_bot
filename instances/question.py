import logging
from database import db
import user
import task


class QuestionType:
    open_question = 'Open question',
    single_test = 'Test with single answer',
    multiple_test = 'Test with multiple answers',
    none = 'None'


class QuestionState:
    none = 0,
    await_menu = 1,
    await_add_correct = 2,
    update_add_correct = 3,
    await_add_incorrect = 4,
    update_add_incorrect = 5,
    await_save = 6,
    update_dave = 7,
    normal = 8


class Question:
    def __init__(self, *task_id):
        if len(task_id) == 1:
            self.task_id = int(task_id)
            correct, incorrect = self.get_question_info()
            self.correct_answers = correct
            self.incorrect_answers = incorrect
            self.question_type = self.get_question_type()
            self.question_text = None
            self.state = QuestionState.none
        else:
            self.task_id = None
            self.correct_answers = None
            self.incorrect_answers = None
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
        await_menu(question_state)


def get_question_text_for_new_task(person: user.User) -> str:
    if person.working_on is None or type(person.working_on_add) is not task.Task:
        return ''
    task_cur: task.Task = person.working_on
    return task_cur.text


# TODO check unsaved data and additional question
def await_menu(question_state: Question, *add_text):
    question_state.change_state
    mes = question_state.message_representation()
    keyboard = [['Add correct answer', '5911'],
                ['Add incorrect answer', '5912'],
                ['Save question settings', '5913'],
                ['Back (ALL UNSAVED DATA WILL BE LOST'], '59']




