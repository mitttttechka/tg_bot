import db


class Task:

    def __init__(self, task_id):
        self.task_id = task_id
        info = self.get_task_info()
        self.text = info[1]
        self.picture_link = info[2]
        self.question = info[3]
        self.section_id = info[4]


    def get_task_info(self):
        db.get_task