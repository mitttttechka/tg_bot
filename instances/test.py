from database import db
from instances import user, instance, task
import menu_navigation as nav
import State as ChangeState


class Test(instance.Instance):

    def __init__(self, *test_id):
        super().__init__()
        self.type = Test
        if len(test_id) == 1:
            self.uid = test_id[0]
            self.sorting: dict = self.get_sort()
            self.state = ChangeState.normal
        elif len(test_id) == 2:
            self.uid = test_id[0]
            self.sorting: dict = test_id[1]
            self.state = ChangeState.normal

    def update(self, test_id):
        self.uid = test_id
        self.sorting: dict = self.get_sort()
        self.state = ChangeState.normal
        self.update_active_instances()

    @staticmethod
    def db_answer_to_instances_array(tests_array):
        tests_dict = {}
        for tests in tests_array:
            if int(tests[0]) in tests_dict.keys():
                tests_dict[tests[0]][tests[1]] = tests[2]
            else:
                tests_dict[tests[0]] = {}
                tests_dict[tests[0]][tests[1]] = tests[2]
        tests_arr = []
        for uid in tests_dict.keys():
            tests_arr.append(Test(uid, tests_dict[uid]))
        return tests_arr

    # TODO await_test to instance
    def await_test(self):
        self.change_state(ChangeState.await_test)
        tests_list = get_all_tests()
        keyboard = []
        for test in tests_list:
            button = test[1], f'{nav.change_existing_test_menu}{str(test[0]).zfill(3)}'
            keyboard.append(button)
        keyboard.append(("Back", f'{nav.manage_tests_menu}'))

        mes = f"Please select test:"
        return mes, keyboard

    def await_change_current(self, *add_text):
        self.change_state(ChangeState.await_change_current)
        mes = add_text[0] if len(add_text) > 0 else ''
        mes += f'{self.text}\n{self.sort_message_instance()}'

        keyboard = [('Add new task to the test', f'{nav.change_existing_test_menu}3'),
                    ('Remove task from the test', f'{nav.change_existing_test_menu}4'),
                    ('Resort existing tasks in the test', f'{nav.change_existing_test_menu}5'),
                    ("Back", f'{nav.manage_tests_menu}')]
        return mes, keyboard

    def set_position_menu(self, data):
        self.update_set_position(data)
        db.update_sorting(self.uid, self.get_sort(), Test)
        text = 'The task was successfully added. New sort:\n'
        return self.await_change_current(text)

    def update_add_task(self, data):
        result = self.update_add_task_middle(data)
        if not isinstance(result, Test):
            return result
        return self.await_set_position()

    def update_add_task_middle(self, text):
        result = self.update_add_task_middle_instance(text)
        if isinstance(result, int):
            return result
        self.change_task(result)
        return self

    def update_resort_existing(self, text):
        answer = self.update_resort_existing_instance(text)
        if not isinstance(answer, int):
            return answer
        self.change_task(answer)
        return self

    def new_sort_menu(self, user_state, data):
        if user_state is not None and len(user_state) == 4:
            if user_state[3] == '1':
                return self.view_current_sort()
            elif user_state[3] == '2':
                db.update_sorting(self.uid, self.get_sort(), Test)
                text = 'The new sorting was successfully saved.\n'
                return self.await_current_sort(text)
            else:
                return self.await_change_current()
        if data is not None:
            test_state, add_text = self.update_new_sort_instance(data[0][0])
            return test_state.await_new_sort(add_text)

    def resort_menu(self, data):
        self.update_set_position(data)
        db.update_sorting(self.uid, self.get_sort(), Test)
        text = 'The task was successfully moved. New sort:\n'
        return self.await_change_current(text)

    def resort_existing_menu(self, data):
        self.update_resort_existing(data)
        self.update_remove_task(data)
        key = self.await_set_position()
        self.change_state(ChangeState.await_resort)
        return key

    def remove_task_menu(self, data):
        self.update_remove_task(data)
        db.update_sorting(self.uid, self.get_sort(), Test)
        text = 'The task was successfully removed. New sort:\n'
        return self.await_change_current(text)

    def update_task_middle(self, data):
        result = self.update_add_task_middle(data)
        if isinstance(result, Test):
            return result
        return self.await_set_position()

    def update_current_sort(self, user_state):
        if user_state[2] == '1':
            return self.await_change_current()
        elif user_state[2] == '2':
            self.change_sorting({})
            return self.await_new_sort()

    def view_current_sort(self):
        self.change_state(ChangeState.view_current)
        mes = self.sort_message_instance('')
        keyboard = [('Back to editing', f'{nav.change_existing_test_menu}2')]
        return mes, keyboard

    # TODO additional message are you sure
    def await_new_sort(self, *add_text):
        self.change_state(ChangeState.await_new_sort)
        text = add_text[0] if len(add_text) > 0 else ''
        text += 'Write Task ID to add to the end of the new sorting\n'
        mes = instance.all_instances_message(task.Task, text)
        self.change_text(mes)
        keyboard = [('View current new sorting', f'{nav.change_existing_test_menu}21'),
                    ('Save sorting (OLD SORTING WILL BE DELETED)', f'{nav.change_existing_test_menu}22'),
                    ("Back (PROGRESS WILL BE LOST)", f'{nav.change_existing_test_menu}23')]
        return mes, keyboard

    # TODO add opportunity to delete track
    def await_current_sort(self, *add_text):
        self.change_state(ChangeState.await_current_sort)
        mes = self.sort_message_instance(add_text)
        self.change_text(mes)
        keyboard = [('Change current sort', f'{nav.change_existing_test_menu}1'),
                    ('Make new sort from zero', f'{nav.change_existing_test_menu}2'),
                    ("Back", f'{nav.change_existing_test_menu}')]
        return mes, keyboard


def add_test(user_id, text):
    new_test_id = db.add_new_test(text)
    person = user.get_user(user_id)
    new_test = Test()
    person.working_on = new_test
    test_state = person.working_on
    test_state.change_state(ChangeState.await_test)
    test_state.change_id(new_test_id)
    test_state.change_text(text)
    test_state.update_active_instances()
    return new_test_id


def manage_test(user_id, user_state, *data):
    test_state, person = instance.initiate_instance(user_id, user_state, Test)

    if test_state.state == ChangeState.empty:
        return test_state.await_test()

    if test_state.state == ChangeState.await_test:
        test_state.update_instance(user_state)
        return test_state.await_change_current()

    if test_state.state == ChangeState.await_current_sort:
        return test_state.update_current_sort(user_state)

    if test_state.state == ChangeState.await_change_current:
        return test_state.update_change_current_instance(user_state)

    if test_state.state == ChangeState.await_add_task_middle:
        return test_state.update_task_middle(data[0][0])

    if test_state.state == ChangeState.await_set_position:
        return test_state.set_position_menu(data[0][0])

    if test_state.state == ChangeState.await_remove_task:
        return test_state.remove_task_menu(data[0][0])

    if test_state.state == ChangeState.await_resort_existing:
        return test_state.resort_existing_menu(data[0][0])

    if test_state.state == ChangeState.await_resort:
        return test_state.resort_menu(data[0][0])

    if test_state.state == ChangeState.await_new_sort:
        return test_state.new_sort_menu(user_state, data)

    if test_state.state == ChangeState.view_current:
        return test_state.await_new_sort()

    return None


def get_all_tests():
    tests_list = db.get_tests_list()
    return tests_list
