from database import db
from instances import user, instance, task, learning_track, section
import menu_navigation as nav
import State as ChangeState


class TestRule(instance.Instance):

    def __init__(self, *track_id):
        super().__init__()
        self.type = TestRule
        if len(track_id) == 1:
            self.uid = track_id[0]
            self.sorting: dict = self.get_sort()
            self.state = ChangeState.normal

        elif len(track_id) == 2:
            self.uid = track_id[0]
            self.sorting: dict = track_id[1]
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
                tests_dict[tests[0]][tests[1]] = tests[2], tests[3]
            else:
                tests_dict[tests[0]] = {}
                tests_dict[tests[0]][tests[1]] = tests[2], tests[3]
        tests_arr = []
        for uid in tests_dict.keys():
            tests_arr.append(TestRule(uid, tests_dict[uid]))
        return tests_arr

    def await_learning_track(self):
        self.change_state(ChangeState.await_learn_track)
        # TODO change to instance
        tracks_list = learning_track.get_all_learning_tracks()
        keyboard = []
        for track in tracks_list:
            button = track[1], f'{nav.change_test_rules_menu}{str(track[0]).zfill(3)}'
            keyboard.append(button)
        keyboard.append(("Back", f'{nav.manage_tests_menu}'))

        mes = f"Please select learning track:"
        return mes, keyboard

    def get_sort(self):
        if not self.sorting:
            info = self.get_info()
            sort = {}
            for row in info:
                sort[row[1]] = row[2], row[3]
            self.sorting = sort
        return self.sorting

    def sort_message(self, *add_text):
        sort = self.get_sort()
        if add_text:
            if isinstance(add_text[0], str):
                mes = add_text[0]
            elif add_text[0]:
                mes = add_text[0][0]
            else:
                mes = ''
        #mes = add_text[0][0] if add_text and add_text[0] else ''
        if not sort:
            mes = f'No sections added yet.'
        else:
            mes += 'Sort: Section; Number of tasks\n'
        for i in range(len(sort)):
            mes += f'{i}: id #{sort[i][0]}, {sort[i][1]} tasks\n'
        return mes

    def await_current_sort(self, *add_text):
        self.change_state(ChangeState.await_current_sort)
        mes = self.sort_message(add_text)

        # TODO of 0 tasks don't allow delete or change
        keyboard = [('Change sections\' sort', f'{nav.change_test_rules_menu}1'),
                    ('Add section to test', f'{nav.change_test_rules_menu}2'),
                    ('Delete section from test', f'{nav.change_test_rules_menu}3'),
                    ('Change number of tasks for section', f'{nav.change_test_rules_menu}4'),
                    ("Back", f'{nav.manage_tests_menu}')]
        return mes, keyboard

    def update_current_sort(self, user_state):
        if user_state[2] == '1':
            return self.await_change_current()
        elif user_state[2] == '2':
            return self.await_add_section()
        elif user_state[2] == '3':
            return self.await_remove_section()
        elif user_state[2] == '4':
            return self.await_change_q_tasks()

    # TODO check if 0 sections
    def await_remove_section(self, *add_text):
        self.change_state(ChangeState.await_remove_section)
        mes = add_text[0] if add_text and isinstance(add_text[0], str) else ''
        # noinspection PyRedundantParentheses
        mes += self.sort_message((f'Write section position to remove from the test rule:\n'), )
        return mes, None

    def await_add_section(self, *add_text):
        self.change_state(ChangeState.await_add_section)
        mes = add_text[0] if add_text else ''
        mes += 'Write Section ID to add:\n'
        mes = instance.all_instances_message(section.Section, mes)  # task.all_tasks_message(mes)
        return mes, None

    def await_change_current(self, *add_text):
        answer = self.await_remove_section(add_text)
        self.change_state(ChangeState.await_resort_existing)
        return answer

    def update_add_section(self, data):
        try:
            section_id = int(data)
        except ValueError:
            return self.await_add_section('Incorrect Section ID. Please try again\n')
        if not instance.instance_exists(section_id, section.Section):
            return self.await_add_section('Section ID doesn\'t exist. Please try again\n')
        self.change_state(ChangeState.update_add_task_middle)
        self.change_task(section_id)
        return self.await_q_tasks()

    def await_change_q_tasks(self, *add_text):
        self.change_state(ChangeState.await_change_q_tasks)
        mes = add_text[0] if add_text and isinstance(add_text[0], str) else ''
        mes += self.sort_message(f'Write section position to change number of tasks:\n')
        return mes, None

    def update_change_q_tasks(self, data):
        try:
            position = int(data)
            if position < 0 or position > len(self.get_sort()) - 1:
                raise ValueError
        except ValueError:
            return self.await_change_q_tasks('Incorrect position. Please try again\n')
        self.change_task(position)
        return self.await_q_tasks()

    def await_q_tasks(self, *add_text):
        self.change_state(ChangeState.await_q_tasks)
        mes = add_text[0] if add_text else ''
        mes += f'How many tasks from the section should be in test?\n'
        return mes, None

    def update_q_tasks_exist(self, data):
        try:
            q_tasks = int(data)
        except ValueError:
            q_tasks = 1
        self.change_state(ChangeState.update_q_tasks)
        sorting = self.get_sort()
        sorting[self.current_task] = sorting[self.current_task][0], q_tasks
        self.change_sorting(sorting)
        db.update_sorting(self.uid, self.sorting, self.type)
        text = 'Number of tasks in section was successfully changed.\n'
        return self.await_current_sort(text)

    def update_q_tasks(self, data):
        try:
            q_tasks = int(data)
        except ValueError:
            q_tasks = 1
        self.change_state(ChangeState.update_q_tasks)
        self.change_task((self.current_task, q_tasks))
        return self.await_set_position()

    def await_set_position(self, *add_text):
        self.change_state(ChangeState.await_set_position)
        mes = add_text[0] if add_text else ''
        # TODO if no tasks in sort don't ask
        mes += f'To which position do you want to insert section?\n'
        mes += self.sort_message()
        return mes, None

    def set_position_menu(self, data):
        self.update_set_position(data)
        db.update_sorting(self.uid, self.get_sort(), self.type)
        text = 'The Section was successfully added. New sort:\n'
        return self.await_current_sort(text)

    def update_remove_section(self, data):
        self.update_remove_task(data)
        db.update_sorting(self.uid, self.sorting, self.type)
        text = 'The Section was successfully removed. New sort:\n'
        return self.await_current_sort(text)

    def await_resort_existing(self, *add_text):
        answer = self.await_remove_section(add_text)
        self.change_state(ChangeState.await_resort_existing)
        return answer

    def resort_existing_menu(self, data):
        self.update_resort_existing(data)
        self.update_remove_task(data)
        key = self.await_set_position()
        self.change_state(ChangeState.await_resort)
        return key

    def update_resort_existing(self, text):
        answer = self.update_resort_existing_instance(text)
        if not isinstance(answer, tuple):
            return answer
        self.change_task(answer)

    def resort_menu(self, data):
        self.update_set_position(data)
        db.update_sorting(self.uid, self.get_sort(), self.type)
        text = 'The task was successfully moved. New sort:\n'
        return self.await_current_sort(text)


def manage_test_rule(user_id, user_state, *data):
    rule_state, person = instance.initiate_instance(user_id, user_state, TestRule)

    if rule_state.state == ChangeState.empty:
        return rule_state.await_learning_track()

    if rule_state.state == ChangeState.await_learn_track:
        rule_state.update_instance(user_state)
        return rule_state.await_current_sort()

    if rule_state.state == ChangeState.await_current_sort:
        return rule_state.update_current_sort(user_state)

    if rule_state.state == ChangeState.await_add_section:
        return rule_state.update_add_section(data[0][0])

    if rule_state.state == ChangeState.await_remove_section:
        return rule_state.update_remove_section(data[0][0])

    # if rule_state.state == ChangeState.await_resort_existing:
    #     return rule_state.resort_existing_await_position(data[0][0])

    if rule_state.state == ChangeState.await_change_q_tasks:
        mes_key = rule_state.update_change_q_tasks(data[0][0])
        rule_state.change_state(ChangeState.await_q_tasks_exist)
        return mes_key

    if rule_state.state == ChangeState.await_q_tasks_exist:
        return rule_state.update_q_tasks_exist(data[0][0])

    if rule_state.state == ChangeState.await_q_tasks:
        return rule_state.update_q_tasks(data[0][0])

    if rule_state.state == ChangeState.await_set_position:
        return rule_state.set_position_menu(data[0][0])

    if rule_state.state == ChangeState.await_resort_existing:
        return rule_state.resort_existing_menu(data[0][0])

    if rule_state.state == ChangeState.await_resort:
        return rule_state.resort_menu(data[0][0])
