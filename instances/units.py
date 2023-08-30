from database import db
import instances
from datetime import datetime


class Units:
    unit_dict = {}
    # learning_track = None
    # task = None
    # section = None
    # user = None
    # test = None
    # course = None
    # question = None

    def __init__(self):
        Units.unit_dict[instances.learning_track.LearningTrack] = DictInstances([], db.Tables.learning_track_table, '')
        Units.unit_dict[instances.task.Task] = DictInstances([], db.Tables.task_table, '')
        Units.unit_dict[instances.section.Section] = DictInstances([], db.Tables.sections_table, '')
        Units.unit_dict[instances.user.User] = DictInstances([], db.Tables.user_table, '')
        Units.unit_dict[instances.test.Test] = DictInstances([], db.Tables.tests_table, '')
        Units.unit_dict[instances.course.Course] = DictInstances([], db.Tables.class_table, '')
        Units.unit_dict[instances.question.Question] = DictInstances([], db.Tables.task_answers_table, '')


class DictInstances:
    def __init__(self, statics, table, columns):
        self.statics = statics
        self.last_updated = datetime.now()
        self.db_table = table
        self.db_columns = columns
