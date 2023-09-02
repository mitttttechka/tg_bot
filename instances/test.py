from database import db
from instances import user, instance, task
import menu_navigation as nav


class ChangeState:
    empty = 0
    normal = 1
    new_test = 2
    await_test = 3
    await_current_sort = 4
    await_change_current = 5
    await_add_task_middle = 6
    await_remove_task = 7
    await_resort_existing = 8
    await_set_position = 9
    await_resort = 10
    await_new_sort = 11
    view_current = 12
    update_test = 13
    update_add_task_middle = 14


class Test(instance.Instance):

    def __init__(self, *test_id):
        super().__init__()
        self.type = Test
        if len(test_id) == 1:
            self.uid = test_id[0]
            # info = self.get_info()
            self.sorting: dict = self.get_sort()
            self.state = ChangeState.normal
            self.current_task = None
        elif len(test_id) == 2:
            self.uid = test_id[0]
            self.sorting: dict = test_id[1]
            self.state = ChangeState.normal
            self.current_task = None
        else:
            self.state = ChangeState.new_test
            self.sorting = {}
            self.current_task = None

    def update(self, test_id):
        self.uid = test_id
        # info = self.get_info()
        self.sorting: dict = self.get_sort()
        self.state = ChangeState.normal
        self.update_active_instances()

    def change_sorting(self, new_sort):
        self.sorting = new_sort

    def get_sort(self):
        info = self.get_info()
        sort = {}
        for row in info:
            sort[row[1]] = row[2]
        return sort

    def change_task(self, task_id):
        self.current_task = task_id

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
        tests_list = instance.get_all_instances(Test)
        keyboard = []
        for test in tests_list:
            button = test.text, f'{nav.change_existing_test_menu}{str(test.uid).zfill(3)}'
            keyboard.append(button)
        keyboard.append(("Back", f'{nav.manage_tests_menu}'))

        mes = f"Please select test:"
        return mes, keyboard

    def await_change_current(self, *add_text):
        self.change_state(ChangeState.await_change_current)
        mes = ''
        if len(add_text) > 0:
            mes += add_text[0]
        mes += f'{self.text}\n{self.test_sort_message()}'

        keyboard = [('Add new task to the test', f'{nav.change_existing_test_menu}3'),
                    ('Remove task from the test', f'{nav.change_existing_test_menu}4'),
                    ('Resort existing tasks in the test', f'{nav.change_existing_test_menu}5'),
                    ("Back", f'{nav.manage_tests_menu}')]
        return mes, keyboard

    def test_sort_message(self, *add_text):
        sort = self.sorting
        mes = ''
        if len(add_text) > 0:
            mes += add_text[0]
        if len(sort) == 0:
            mes = f'No tasks in the test yet.'
        else:
            mes += 'Sort: Task ID\n'
        for i in range(len(sort)):
            mes += f'{i}: task {sort[i]}\n'
        return mes

        # TODO show only questions

    def await_add_task_middle(self, *add_text):
        self.change_state(ChangeState.await_add_task_middle)
        mes = ''
        if len(add_text) > 0:
            mes += add_text[0]
        mes += 'Write Question ID to add to the test:\n'
        mes = instance.all_instances_message(task.Task, mes)  # task.all_tasks_message(mes)
        return mes, None

    def set_position_menu(self, data):
        self.update_set_position(data)
        db.update_sorting(self.uid, self.get_sort(), Test)
        text = 'The task was successfully added. New sort:\n'
        return self.await_change_current(text)

    def update_add_task(self, data):
        result = self.update_add_task_middle(data)
        if type(result) is not Test:
            return result
        return self.await_set_position()

    def update_add_task_middle(self, text):
        try:
            task_id = int(text)
        except:
            return self.await_add_task_middle('Incorrect Task ID. Please try again\n')
        if not instance.instance_exists(task_id, task.Task):  # task.task_exists(task_id):
            return self.await_add_task_middle('Task ID doesn\'t exist. Please try again\n')
        self.change_state(ChangeState.update_add_task_middle)
        self.change_task(task_id)
        return self

    def await_remove_task(self, *add_text):
        self.change_state(ChangeState.await_remove_task)
        mes = ''
        if len(add_text) > 0:
            if type(add_text[0]) is str:
                mes += add_text[0]
        mes += self.test_sort_message('Write task position to remove from the test:\n')
        return mes, None

    def await_resort_existing(self, *add_text):
        answer = self.await_remove_task(add_text)
        self.change_state(ChangeState.await_resort_existing)
        return answer

    def update_change_current(self, user_state):
        if user_state[2] == '3':
            return self.await_add_task_middle()
        elif user_state[2] == '4':
            return self.await_remove_task()
        elif user_state[2] == '5':
            return self.await_resort_existing()

    def update_resort_existing(self, text):
        try:
            position = int(text)
        except:
            return self.await_resort_existing('Incorrect position. Please try again\n')
        sort = self.get_sort()
        task_id = sort[position]

        self.change_task(task_id)
        return self

    def update_remove_task(self, text):
        try:
            position = int(text)
        except:
            return self.await_remove_task('Incorrect position. Please try again\n')

        new_sort = self.remove_position_from_sort(position)

        return self.update_sort(new_sort)

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
            test_state, add_text = self.update_new_sort(data[0][0])
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
        if type(result) is not Test:
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
        mes = self.test_sort_message('')
        keyboard = [('Back to editing', f'{nav.change_existing_test_menu}2')]
        return mes, keyboard

    # TODO additional message are you sure
    def await_new_sort(self, *add_text):
        self.change_state(ChangeState.await_new_sort)
        text = ''
        if len(add_text) > 0:
            text += add_text[0]
        text += 'Write Task ID to add to the end of the new sorting\n'
        mes = instance.all_instances_message(task.Task, text)  # task.all_tasks_message(text)
        self.change_text(mes)
        keyboard = [('View current new sorting', f'{nav.change_existing_test_menu}21'),
                    ('Save sorting (OLD SORTING WILL BE DELETED)', f'{nav.change_existing_test_menu}22'),
                    ("Back (PROGRESS WILL BE LOST)", f'{nav.change_existing_test_menu}23')]
        return mes, keyboard

    # TODO opportunity to input several tasks
    def update_new_sort(self, text):
        answer = self.update_add_task_middle(text)
        if type(answer) is not Test:
            return self, 'Incorrect Task ID. Please try again\n'
        if self.sorting is None:
            sort_id = 0
        else:
            sort_id = len(self.sorting)
        self.update_set_position(sort_id + 1)
        return self, 'Task was added to the new sorting.\n'

    def update_test(self, user_state):
        self.change_state(ChangeState.update_test)
        self.change_id(int(user_state[2:5]))
        return self

    # TODO add opportunity to delete track
    def await_current_sort(self, *add_text):
        self.change_state(ChangeState.await_current_sort)
        mes = self.test_sort_message(add_text)
        self.change_text(mes)
        keyboard = [('Change current sort', f'{nav.change_existing_test_menu}1'),
                    ('Make new sort from zero', f'{nav.change_existing_test_menu}2'),
                    ("Back", f'{nav.change_existing_test_menu}')]
        return mes, keyboard

    def remove_position_from_sort(self, position):
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

    def await_set_position(self, *add_text):
        self.change_state(ChangeState.await_set_position)
        mes = ''
        if len(add_text) > 0:
            mes += add_text[0]
        mes += f'To which position do you want to insert task {self.current_task}\n'
        mes += self.text
        return mes, None

    def update_set_position(self, text):
        try:
            l_position = int(text)
        except:
            return self.await_add_task_middle('Incorrect position. Please try again\n')

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

        self.update_sort(new_sort)
        return self

    def update_sort(self, new_sort):
        self.change_sorting(new_sort)
        self.change_text(self.test_sort_message(''))
        return self


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
    #
    # if test_state.state == ChangeState.await_test:
    #     return test_state.await_change_current()
    #
    # if test_state.state == ChangeState.await_change_current:
    #     return test_state.update_change_current(user_state)
    #
    # if test_state.state == ChangeState.await_add_task_middle:
    #     return test_state.update_add_task(data[0][0])
    #
    # if test_state.state == ChangeState.await_remove_task:
    #     return test_state.update_remove_task(data[0][0])
    #
    # if test_state.state == ChangeState.await_resort_existing:
    #     return test_state.update_resort_existing(data[0][0])
    #
    # return 1
    if test_state.state == ChangeState.empty:
        return test_state.await_test()

    if test_state.state == ChangeState.await_test:
        test_state.update_test(user_state)
        return test_state.await_change_current()

    if test_state.state == ChangeState.await_current_sort:
        return test_state.update_current_sort(user_state)

    if test_state.state == ChangeState.await_change_current:
        return test_state.update_change_current(user_state)

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


def manage_test_rules(user_id, user_state, *data):
    return 1
