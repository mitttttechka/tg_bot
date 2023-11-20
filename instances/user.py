import logging
import json

from database import db


class User:

    def __init__(self, user_id, user_name=None, mtype=None, class_id=None, subscribed=None,
                 progress_point=None, current_position=None, working_on=None, working_on_add=None):
        self.user_id = user_id
        if user_name is None:
            info = self.get_user_info()
            self.user_name: str = info[1] if info[1] else None
            self.type: int = int(info[2])
            self.class_id: int = int(info[3])
            self.subscribed: bool = info[4]
            self.progress_point: int = int(info[5])
            self.current_position: int = int(info[6])
            self.working_on = None
            self.working_on_add = None
        else:
            self.user_name = user_name
            self.type: int = mtype
            self.class_id: int = class_id
            self.subscribed: bool = subscribed
            self.progress_point: int = progress_point
            self.current_position: int = current_position
            self.working_on = working_on
            self.working_on_add = working_on_add

    @staticmethod
    def from_json(json_dict):
        new_user = User(
            json_dict['user_id'],
            json_dict['user_name'],
            json_dict['type'],
            json_dict['class_id'],
            json_dict['subscribed'],
            json_dict['progress_point'],
            json_dict['current_position'],
            json_dict['working_on'],
            json_dict['working_on_add']
        )
        return new_user

    def get_user_info(self):
        logging.debug(self.user_id)
        user_info = db.get_user(self.user_id)
        logging.debug(f'User info size: {len(user_info)}')

        if len(user_info) == 0:
            logging.debug('Creating new user')
            db.create_new_user(self.user_id)
            user_info = [(self.user_id, '', 1, 0, False, 0, 0)]
        return user_info[0]

    def set_progress_point(self, progress_point):
        db.set_progress(self.user_id, int(progress_point))
        self.progress_point = progress_point
        update_active_users(self)

    def set_current_position(self, current_position):
        if self.current_position != current_position:
            db.set_current(self.user_id, int(current_position))
            self.current_position = current_position
            update_active_users(self)

    def update_name(self, name):
        db.update_name(self.user_id, name)
        self.user_name = name
        update_active_users(self)

    def update_working_on(self, substance):
        self.working_on = substance
        update_active_users(self)


def get_user(user_id):
    user = find_user_in_active(user_id)
    if user:
        return user
    new_user = User(user_id)
    update_active_users(new_user)
    return new_user
    '''has_active = find_user_in_active(user_id)
    if has_active != -1:
        return active_users[has_active]
    new_user = User(user_id)
    active_users.append(new_user)
    return new_user'''


def find_user_in_active(user_id):
    res = db.get_redis(f'userID:{user_id}', User)
    return res
    '''
    for i in range(len(active_users)):
        if active_users[i].user_id == user_id:
            return i
    return -1
    '''


def update_active_users(user):
    #index = find_user_in_active(user.user_id)

    #active_users[index] = user
    db.set_redis(f'userID:{user.user_id}', user)
    # TODO add async update to database


# TODO async delete from db
def delete_user(user_id):
    db.del_redis(f'userID{user_id}')
    #index = find_user_in_active(user_id)
    #if index != -1:
    #    active_users.pop(index)
