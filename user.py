import db

class User:
    def __init__(self, user_id):
        self.user_id = user_id
        info = get_user_info()
        self.user_name = info[1]
        self.type = info[2]
        self.class_id = info[3]
        self.subscribed = info[4]

def get_user_info(user_id):
    user_info = db.direct_select(f'SELECT * FROM users WHERE user_id = {user_id}')

def create_new_user(self):
    self.type = 1
    self.class_id = 0
    self.subscribed = False