import logging

from instances import user, task, instance
from database import db
import menu_navigation as nav
import State as ChangeState


# TODO del lists if don't need them
# TODO check if can apply .insert method to sorting
class LearningTrack(instance.Instance):

    def __init__(self, *track_id):
        super().__init__()
        self.type = LearningTrack
        if len(track_id) == 1:
            self.uid = track_id[0]
            self.sorting: dict = self.get_sort()
            self.state = ChangeState.normal

    def new_sort_menu(self, user_state, data):
        if user_state is not None and len(user_state) == 4:
            if user_state[3] == '1':
                return self.view_current_sort()
            elif user_state[3] == '2':
                db.update_sorting(self.uid, self.get_sort(), self.type)
                text = 'The new sorting was successfully saved.\n'
                return self.await_current_sort(text)
            else:
                return self.await_change_current()
        if data is not None:
            track_state, add_text = self.update_new_sort_instance(data[0][0])
            return track_state.await_new_sort(add_text)

    def resort_menu(self, data):
        self.update_set_position(data)
        db.update_sorting(self.uid, self.get_sort(), self.type)
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
        db.update_sorting(self.uid, self.get_sort(), self.type)
        text = 'The task was successfully removed. New sort:\n'
        return self.await_change_current(text)

    def set_position_menu(self, data):
        self.update_set_position(data)
        db.update_sorting(self.uid, self.get_sort(), self.type)
        text = 'The task was successfully added. New sort:\n'
        return self.await_change_current(text)

    def update_task_middle(self, data):
        result = LearningTrack.update_add_task_middle(self, data)
        if not isinstance(result, LearningTrack):
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
        mes = self.sort_message_instance('')
        keyboard = [('Back to editing', f'{nav.manage_learning_track_menu}2')]
        return mes, keyboard

    # TODO additional message are you sure
    def await_new_sort(self, *add_text):
        self.change_state(ChangeState.await_new_sort)
        text = add_text[0] if len(add_text) > 0 else ''
        text += 'Write Task ID to add to the end of the new sorting\n'
        mes = instance.all_instances_message(task.Task, text)
        keyboard = [('View current new sorting', f'{nav.manage_learning_track_menu}21'),
                    ('Save sorting (OLD SORTING WILL BE DELETED)', f'{nav.manage_learning_track_menu}22'),
                    ("Back (PROGRESS WILL BE LOST)", f'{nav.manage_learning_track_menu}23')]
        return mes, keyboard

    def await_learning_track(self):
        self.change_state(ChangeState.await_instance)
        # TODO change to instance
        tracks_list = get_all_learning_tracks()
        keyboard = []
        for track in tracks_list:
            button = track[1], f'{nav.manage_learning_track_menu}{str(track[0]).zfill(3)}'
            keyboard.append(button)
        keyboard.append(("Back", f'{nav.learning_tracks_menu}'))

        mes = f"Please select learning track:"
        return mes, keyboard

    # TODO add opportunity to delete track
    def await_current_sort(self, *add_text):
        self.change_state(ChangeState.await_current_sort)
        mes = self.sort_message_instance(add_text)

        keyboard = [('Change current sort', f'{nav.manage_learning_track_menu}1'),
                    ('Make new sort from zero', f'{nav.manage_learning_track_menu}2'),
                    ("Back", f'{nav.learning_tracks_menu}')]
        return mes, keyboard

    def await_change_current(self, *add_text):
        self.change_state(ChangeState.await_change_current)
        mes = add_text[0] if len(add_text) > 0 else ''
        mes += f'{self.text}\n{self.sort_message_instance()}'

        keyboard = [('Add new task to the track', f'{nav.manage_learning_track_menu}3'),
                    ('Remove task from the track', f'{nav.manage_learning_track_menu}4'),
                    ('Resort existing tasks in the track', f'{nav.manage_learning_track_menu}5'),
                    ("Back", f'{nav.learning_tracks_menu}')]
        return mes, keyboard

    @staticmethod
    def update_add_task_middle(self, text):
        result = self.update_add_task_middle_instance(text)
        if not isinstance(result, int):
            return result
        self.change_task(result)
        return self

    def update_resort_existing(self, text):
        answer = self.update_resort_existing_instance(text)
        if not isinstance(answer, int):
            return answer
        self.change_task(answer)
        return self


def add_learning_track(user_id, text):
    new_track_id = db.add_new_learning_track(text)
    person = user.get_user(user_id)
    new_task = LearningTrack()
    person.working_on = new_task
    track_state = person.working_on
    track_state.change_state(ChangeState.await_instance)
    return new_track_id


# TODO where list in message consider to change to buttons
def manage_learning_track(user_id, user_state, *data):
    track_state, person = instance.initiate_instance(user_id, user_state, LearningTrack)

    if track_state.state == ChangeState.empty:
        return track_state.await_learning_track()

    if track_state.state == ChangeState.await_instance:
        track_state.update_instance(user_state)
        return track_state.await_current_sort()

    if track_state.state == ChangeState.await_current_sort:
        return track_state.update_current_sort(user_state)

    if track_state.state == ChangeState.await_change_current:
        return track_state.update_change_current_instance(user_state)

    if track_state.state == ChangeState.await_add_task_middle:
        return track_state.update_task_middle(data[0][0])

    if track_state.state == ChangeState.await_set_position:
        return track_state.set_position_menu(data[0][0])

    if track_state.state == ChangeState.await_remove_task:
        return track_state.remove_task_menu(data[0][0])

    if track_state.state == ChangeState.await_resort_existing:
        return track_state.resort_existing_menu(data[0][0])

    if track_state.state == ChangeState.await_resort:
        return track_state.resort_menu(data[0][0])

    if track_state.state == ChangeState.await_new_sort:
        return track_state.new_sort_menu(user_state, data)

    if track_state.state == ChangeState.view_current:
        return track_state.await_new_sort()

    return None


def get_all_learning_tracks():
    tracks_list = db.get_learning_tracks_list()
    return tracks_list


def get_name_for_id(track_id):
    name = db.get_learning_track_name(track_id)
    return name[0][0] if len(name) > 0 else None
