from database import db
from instances import user, instance, task
import menu_navigation as nav
import State as ChangeState
import random


class Course(instance.Instance):

    def __init__(self, *class_id):
        super().__init__()
        self.type = Course
        if len(class_id) == 1:
            self.uid = class_id[0]
            info = self.get_info()
            self.text = info[1]
            self.teacher_id = int(info[2])
            self.invite_code = info[3]
            self.max_students = int(info[4])
            self.state = ChangeState.normal
        elif len(class_id) == 5:
            self.uid = class_id[0]
            self.text = class_id[1]
            self.teacher_id = int(class_id[2])
            self.invite_code = class_id[3]
            self.max_students = int(class_id[4])
            self.state = ChangeState.normal
        else:
            self.teacher_id = None
            self.invite_code = None
            self.max_students = 1

    def update(self, class_id):
        self.uid = class_id
        info = self.get_info()
        self.teacher_id = int(info[2])
        self.invite_code = info[3]
        self.max_students = int(info[4])
        self.state = ChangeState.normal
        self.update_active_instances()

    def change_teacher_id(self, teacher_id):
        self.teacher_id = teacher_id

    def change_invite_code(self, code):
        self.invite_code = code

    def create_code(self):
        code = instance.generate_code()
        self.change_invite_code(code)

    @staticmethod
    def db_answer_to_instances_array(courses_array):
        courses = []
        for course in courses_array:
            t = Course(course[0], course[1], course[2], course[3], course[4])
            courses.append(t)
        return courses

    def manage_class_new_class(self, *add_text):
        mes = add_text[0] if add_text else ''
        self.change_state(ChangeState.awaiting_instance_id)
        mes += instance.all_instances_message(Course, 'Please write Class ID to manage:\n')
        keyboard = [['Back', f'{nav.manage_classes_menu}']]
        return mes, keyboard

    def get_existing_instance(self, text):
        if not instance.instance_exists(text, Course):
            return self.manage_class_new_class('Class doesn\'t exist. Please try again.\n')
        self.update(int(text))
        return self

    def instance_message(self, *add_text):
        mes = add_text[0] if len(add_text) > 0 else ''
        mes += f'ID: {self.uid}\nName: {self.text}\nMaximum number of students: {self.max_students}\n'
        return mes

    def manage_class_await_class_id(self, *add_text):
        self.change_state(ChangeState.awaiting_manage_instance)
        mes = add_text[0] if len(add_text) > 0 else ''
        mes += self.instance_message()

        keyboard = [['Change name', f'{nav.find_class}1'],
                    ['Change maximum number of students', f'{nav.find_class}2'],
                    ['Delete class', f'{nav.find_class}3'],
                    ['Back', f'{nav.manage_classes_menu}']]

        return mes, keyboard


def add_new_class(text, teacher_id):
    new_id = db.add_new_instance(text, Course)
    new_course = Course(new_id, text, teacher_id, instance.generate_code(), 5)
    new_course.update_active_instances()


def manage_class(user_id, user_state, *data):
    class_state, person = instance.initiate_instance(user_id, user_state, Course)

    if class_state.state == ChangeState.empty:
        return class_state.manage_class_new_class()

    if class_state.state == ChangeState.awaiting_instance_id:
        class_state.get_existing_instance(data[0][0])
        return class_state.manage_class_await_class_id()

    return None


def get_all_tests():
    tests_list = db.get_tests_list()
    return tests_list
