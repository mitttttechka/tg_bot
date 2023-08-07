import db


class User:

    def __init__(self, user_id):
        self.user_id = user_id
        info = self.get_user_info()
        self.user_name = info[1]
        self.type = info[2]
        self.class_id = info[3]
        self.subscribed = info[4]
        self.progress_point = info[5]

    def get_user_info(self):
        user_info = db.get_user(self.user_id)
        if len(user_info) == 0:
            db.create_new_user(self.user_id)
            user_info = [(self.user_id, '', 1, 0, False, 0)]
        return user_info[0]

    def set_progress_point(self, progress_point):
        db.set_progress(self.user_id, progress_point)
        self.progress_point = progress_point

    def update_name(self, name):
        db.update_name(self.user_id, name)
        self.user_name = name
