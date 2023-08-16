import logging
import db
import user


class ChangeState:
    empty = 0,
    await_learn_track = 1,
    update_learn_track = 2,
    await_current_sort = 3,
    update_current_sort = 4,
    await_change_current = 5,
    update_change_sort = 6,
    await_add_task_middle = 7,
    update_add_task_middle = 8,
    await_remove_task = 9,
    update_remove_task = 10,
    await_resort_existing = 11,
    update_resort_existing = 12,
    await_new_sort = 13,
    update_new_sort = 14,
    await_add_task_end = 15,
    update_add_task_end = 16,
    normal = 17


class LearningTrack:

    def __init__(self, *track_id):
        if len(track_id) > 0:
            self.track_id = track_id
            self.sorting: dict = self.get_sort()
            self.state = ChangeState.normal
        else:
            self.track_id = None
            self.sorting = None,
            self.state = ChangeState.empty

    def get_sort(self):
        data = db.get_learning_track(self.track_id)
        sorted_dict = {}
        for row in data:
            sorted_dict[int(row[0])] = int(row[1])
        return sorted_dict

    def change_state(self, state, person):
        self.state = state
        person.working_on = self
        user.update_active_users(person)
        return self


# TODO add several learning tracks. Maybe add table for learning_track - name
# def add_learning_track():


def manage_learning_track(user_id, user_state, *data):
    person = user.get_user(user_id)
    logging.debug(f"User {person.user_id} is here!. User state: {user_state}")

    # creating empty Task class if begins to create
    if person.working_on is None or type(person.working_on) is not LearningTrack:
        new_task = LearningTrack()
        person.working_on = new_task

    track_state = person.working_on

    if track_state.state == ChangeState.empty:
        return await_learning_track(track_state, person)
    # TODO continue to manage learning track
    return None
    #db.get_learning_track()


def await_learning_track(track_state, person):
    track_state = track_state.change_state(ChangeState.await_learn_track, person)
    tracks_list = get_all_learning_tracks()
    keyboard = []
    for track in tracks_list:
        button = track[0], f'67{str(track[0]).zfill(3)}'
        keyboard.append(button)
    keyboard.append(("Back", "52"))

    mes = f"Please select learning track:"
    return mes, keyboard


def get_all_learning_tracks():
    tracks_list = db.get_learning_tracks_list()
    return tracks_list
