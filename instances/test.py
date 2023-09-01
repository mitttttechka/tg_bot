import logging

from database import db
from instances import user, question, instance
import menu_navigation as nav


class ChangeState:
    normal = 1
    new_test = 2


class Test(instance.Instance):

    def __init__(self, *test_id):
        super().__init__()
        self.type = Test
        if len(test_id) == 1:
            self.uid = test_id[0]
            info = self.get_info()
            self.sorting: dict = self.get_sort(info)
            self.state = ChangeState.normal
        elif len(test_id) == 2:
            self.uid = test_id[0]
            self.sorting: dict = test_id[1]
            self.state = ChangeState.normal
        else:
            self.state = ChangeState.new_test

    def update(self, test_id):
        self.uid = test_id
        info = self.get_info()
        self.sorting: dict = self.get_sort(info)
        self.state = ChangeState.normal
        self.update_active_instances()

    def change_sorting(self, new_sort):
        self.sorting = new_sort

    def get_sort(self, info):
        sort = {}
        for row in info:
            sort[row[1]] = row[2]
        return sort

    def db_answer_to_instances_array(self, tests_array):
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





