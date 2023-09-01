import logging

from instances import user, task, instance
from database import db
import menu_navigation as nav


class ChangeState:
    empty = 0
    await_learn_track = 1
    update_learn_track = 2
    await_current_sort = 3
    update_current_sort = 4
    await_change_current = 5
    update_change_sort = 6
    await_add_task_middle = 7
    update_add_task_middle = 8
    await_remove_task = 9
    update_remove_task = 10
    await_resort_existing = 11
    update_resort_existing = 12
    await_new_sort = 13
    update_new_sort = 14
    await_add_task_end = 15
    update_add_task_end = 16
    normal = 17
    await_set_position = 18
    await_resort = 19
    view_current = 20


class LearningTrack(instance.Instance):

    def __init__(self, *track_id):
        super().__init__()
        self.type = LearningTrack
        if len(track_id) == 1:
            self.uid = track_id[0]
            self.sorting: dict = self.get_sort()
            self.state = ChangeState.normal
            self.current_task = None
        else:
            self.sorting = None
            self.state = ChangeState.empty
            self.current_task = None

    def get_sort(self):
        if self.sorting is None:
            data = db.get_learning_track(self.uid)
            sorted_dict = {}
            for row in data:
                sorted_dict[int(row[0])] = int(row[1])
            self.sorting = sorted_dict
        return self.sorting

    def change_task(self, task_id):
        self.current_task = task_id

    def change_sort(self, new_sort):
        self.sorting = new_sort

    def new_sort_menu(self, user_state, data):
        if user_state is not None and len(user_state) == 4:
            if user_state[3] == '1':
                return self.view_current_sort()
            elif user_state[3] == '2':
                db.update_learning_track(self.uid, self.get_sort())
                text = 'The new sorting was successfully saved.\n'
                return self.await_current_sort(text)
            else:
                return self.await_change_current()
        if data is not None:
            track_state, add_text = self.update_new_sort(data[0][0])
            return track_state.await_new_sort(add_text)

    def resort_menu(self, data):
        self.update_set_position(data)
        db.update_learning_track(self.uid, self.get_sort())
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
        db.update_learning_track(self.uid, self.get_sort())
        text = 'The task was successfully removed. New sort:\n'
        return self.await_change_current(text)

    def set_position_menu(self, data):
        self.update_set_position(data)
        db.update_learning_track(self.uid, self.get_sort())
        text = 'The task was successfully added. New sort:\n'
        return self.await_change_current(text)

    def update_task_middle(self, data):
        result = self.update_add_task_middle(data)
        if type(result) is not LearningTrack:
            return result
        #self = result
        return self.await_set_position()

    def update_current_sort(self, user_state):
        if user_state[2] == '1':
            return self.await_change_current()
        elif user_state[2] == '2':
            self.change_sort({})
            return self.await_new_sort()

    def update_change_current(self, user_state):
        if user_state[2] == '3':
            return self.await_add_task_middle()
        elif user_state[2] == '4':
            return self.await_remove_task()
        elif user_state[2] == '5':
            return self.await_resort_existing()

    def view_current_sort(self):
        self.change_state(ChangeState.view_current)
        mes = self.track_sort_message('')
        keyboard = [('Back to editing', f'{nav.manage_learning_track_menu}2')]
        return mes, keyboard

    # TODO additional message are you sure
    def await_new_sort(self, *add_text):
        self.change_state(ChangeState.await_new_sort)
        text = ''
        if len(add_text) > 0:
            text += add_text[0]
        text += 'Write Task ID to add to the end of the new sorting\n'
        mes = instance.all_instances_message(task.Task, text)  # task.all_tasks_message(text)
        self.change_text(mes)
        keyboard = [('View current new sorting', f'{nav.manage_learning_track_menu}21'),
                    ('Save sorting (OLD SORTING WILL BE DELETED)', f'{nav.manage_learning_track_menu}22'),
                    ("Back (PROGRESS WILL BE LOST)", f'{nav.manage_learning_track_menu}23')]
        return mes, keyboard

    # TODO opportunity to input several tasks
    def update_new_sort(self, text):
        answer = self.update_add_task_middle(text)
        if type(answer) is not LearningTrack:
            return self, 'Incorrect Task ID. Please try again\n'
        #track_state = answer
        if self.sorting is None:
            sort_id = 0
        else:
            sort_id = len(self.sorting)
        self.update_set_position(sort_id + 1)
        return self, 'Task was added to the new sorting.\n'

    def await_learning_track(self):
        self.change_state(ChangeState.await_learn_track)
        tracks_list = get_all_learning_tracks()
        keyboard = []
        for track in tracks_list:
            button = track[1], f'{nav.manage_learning_track_menu}{str(track[0]).zfill(3)}'
            keyboard.append(button)
        keyboard.append(("Back", f'{nav.learning_tracks_menu}'))

        mes = f"Please select learning track:"
        return mes, keyboard

    def update_learn_track(self, user_state):
        self.change_state(ChangeState.update_learn_track)
        self.change_id(int(user_state[2:5]))
        return self

    # TODO add opportunity to delete track
    def await_current_sort(self, *add_text):
        self.change_state(ChangeState.await_current_sort)
        mes = self.track_sort_message(add_text)
        self.change_text(mes)
        keyboard = [('Change current sort', f'{nav.manage_learning_track_menu}1'),
                    ('Make new sort from zero', f'{nav.manage_learning_track_menu}2'),
                    ("Back", f'{nav.learning_tracks_menu}')]
        return mes, keyboard

    def track_sort_message(self, add_text):
        sort = self.get_sort()
        mes = ''
        if len(add_text) > 0:
            mes += add_text[0]
        mes += 'Sort: Task ID\n'
        for i in range(len(sort)):
            mes += f'{i}: task {sort[i]}\n'
        if len(mes) == 0:
            mes = f'No tasks in the learning track yet.'
        return mes

    def await_change_current(self, *add_text):
        self.change_state(ChangeState.await_change_current)
        mes = ''
        if len(add_text) > 0:
            mes += add_text[0]
        mes += self.text
        keyboard = [('Add new task to the track', f'{nav.manage_learning_track_menu}3'),
                    ('Remove task from the track', f'{nav.manage_learning_track_menu}4'),
                    ('Resort existing tasks in the track', f'{nav.manage_learning_track_menu}5'),
                    ("Back", f'{nav.learning_tracks_menu}')]
        return mes, keyboard

    def await_add_task_middle(self, *add_text):
        self.change_state(ChangeState.await_add_task_middle)
        mes = ''
        if len(add_text) > 0:
            mes += add_text[0]
        mes += 'Write Task ID to add to the learning track:\n'
        mes = instance.all_instances_message(task.Task, mes)  # task.all_tasks_message(mes)
        return mes, None

    def await_remove_task(self, *add_text):
        self.change_state(ChangeState.await_remove_task)
        mes = ''
        if len(add_text) > 0:
            if type(add_text[0]) is str:
                mes += add_text[0]
        mes += 'Write task position to remove from the learning track:\n'
        mes += self.text
        return mes, None

    def update_add_task_middle(self, text):
        try:
            task_id = int(text)
        except:
            return self.await_add_task_middle('Incorrect Task ID. Please try again\n')
        if not instance.instance_exists(task_id, task.Task):  # task.task_exists(task_id):
            return self.await_add_task_middle('Task ID doesn\'t exist. Please try again\n')
        self.change_state(ChangeState.update_add_task_middle)
        self.change_task(task_id)
        return self

    def update_remove_task(self, text):
        try:
            position = int(text)
        except:
            return self.await_remove_task('Incorrect position. Please try again\n')

        new_sort = self.remove_position_from_sort(position)

        return self.update_sort(new_sort)

    def remove_position_from_sort(self, position):
        sort = self.get_sort()
        new_sort = {}

        if position >= len(sort):
            position = len(sort) - 1
        if position < 0:
            position = 0

        for i in range(position):
            new_sort[i] = sort[i]
        for i in range(position + 1, len(sort)):
            new_sort[i - 1] = sort[i]

        return new_sort

    def await_set_position(self, *add_text):
        self.change_state(ChangeState.await_set_position)
        mes = ''
        if len(add_text) > 0:
            mes += add_text[0]
        mes += f'To which position do you want to insert task {self.current_task}\n'
        mes += self.text
        return mes, None

    def update_set_position(self, text):
        try:
            l_position = int(text)
        except:
            return self.await_add_task_middle('Incorrect position. Please try again\n')

        sort = self.get_sort()
        new_sort = {}

        if l_position > len(sort):
            l_position = len(sort)
        if l_position < 0:
            l_position = 0

        for i in range(l_position):
            new_sort[i] = sort[i]
        new_sort[l_position] = self.current_task
        for i in range(l_position, len(sort)):
            new_sort[i + 1] = sort[i]

        self.update_sort(new_sort)
        return self

    def update_sort(self, new_sort):
        self.change_sort(new_sort)
        self.change_text(self.track_sort_message(''))
        return self

    def await_resort_existing(self, *add_text):
        answer = self.await_remove_task(add_text)
        self.change_state(ChangeState.await_resort_existing)
        return answer

    def update_resort_existing(self, text):
        try:
            position = int(text)
        except:
            return self.await_resort_existing('Incorrect position. Please try again\n')
        sort = self.get_sort()
        task_id = sort[position]

        self.change_task(task_id)
        return self


def add_learning_track(user_id, text):
    new_track_id = db.add_new_learning_track(text)
    person = user.get_user(user_id)
    new_task = LearningTrack()
    person.working_on = new_task
    track_state = person.working_on
    track_state.change_state(ChangeState.await_learn_track)
    return new_track_id


# TODO where list in message consider to change to buttons
def manage_learning_track(user_id, user_state, *data):
    track_state, person = instance.initiate_instance(user_id, user_state, LearningTrack)

    if track_state.state == ChangeState.empty:
        return track_state.await_learning_track()

    if track_state.state == ChangeState.await_learn_track:
        track_state.update_learn_track(user_state)
        return track_state.await_current_sort()

    if track_state.state == ChangeState.await_current_sort:
        return track_state.update_current_sort(user_state)

    if track_state.state == ChangeState.await_change_current:
        return track_state.update_change_current(user_state)

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
    if len(name) > 0:
        return name[0][0]
    return None
