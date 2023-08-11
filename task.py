import db


class Task:

    def __init__(self, *task_id):
        if len(task_id) > 0:
            self.task_id = task_id
            info = self.get_task_info()
            self.text = info[1]
            self.picture_link = info[2]
            self.question = info[3]
            self.section_id: int = int(info[4])
        else:
            self.task_id = None
            self.text = None
            self.picture_link = None
            self.question = None
            self.section_id: int = None

    def get_task_info(self):
        return db.get_task(self.task_id)


def add_new_section(text):
    db.add_new_section(text)


def get_all_sections():
    sections = db.get_all_sections()
    print(sections)
    return sections
