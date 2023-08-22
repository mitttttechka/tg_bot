import logging
from database import db
import user
import task


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
    normal = 17,
    await_set_position = 18,
    await_resort = 19,
    view_current = 20


class LearningTrack:

    def __init__(self, *track_id):
        if len(track_id) > 0:
            self.track_id = track_id
            self.sorting: dict = self.get_sort()
            self.state = ChangeState.normal
            self.sort_mes = None
            self.current_task = None
        else:
            self.track_id = None
            self.sorting = None
            self.state = ChangeState.empty
            self.sort_mes = None
            self.current_task = None

    def get_sort(self):
        if self.sorting is None:
            data = db.get_learning_track(self.track_id)
            sorted_dict = {}
            for row in data:
                sorted_dict[int(row[0])] = int(row[1])
            self.sorting = sorted_dict
        return self.sorting

    def change_state(self, state):
        self.state = state

    def change_track_id(self, track_id):
        self.track_id = track_id

    def change_mes(self, mes):
        self.sort_mes = mes

    def change_task(self, task_id):
        self.current_task = task_id

    def change_sort(self, new_sort):
        self.sorting = new_sort


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
    person = user.get_user(user_id)
    logging.debug(f"User {person.user_id} is here!. User state: {user_state}")

    # creating empty Task class if begins to create
    if person.working_on is None or type(person.working_on) is not LearningTrack:
        new_task = LearningTrack()
        person.working_on = new_task

    track_state = person.working_on

    if track_state.state == ChangeState.empty:
        return await_learning_track(track_state)

    if track_state.state == ChangeState.await_learn_track:
        track_state = update_learn_track(track_state, user_state)
        return await_current_sort(track_state)

    if track_state.state == ChangeState.await_current_sort:
        if user_state[2] == '1':
            return await_change_current(track_state)
        elif user_state[2] == '2':
            track_state.change_sort({})
            return await_new_sort(track_state)

    if track_state.state == ChangeState.await_change_current:
        if user_state[2] == '3':
            return await_add_task_middle(track_state)
        elif user_state[2] == '4':
            return await_remove_task(track_state)
        elif user_state[2] == '5':
            return await_resort_existing(track_state)

    if track_state.state == ChangeState.await_add_task_middle:
        result = update_add_task_middle(track_state, data[0][0])
        if type(result) is not LearningTrack:
            return result
        track_state = result
        return await_set_position(track_state)

    if track_state.state == ChangeState.await_set_position:
        track_state = update_set_position(track_state, data[0][0])
        db.update_learning_track(track_state.track_id, track_state.get_sort())
        text = 'The task was successfully added. New sort:\n'
        return await_change_current(track_state, text)

    if track_state.state == ChangeState.await_remove_task:
        track_state = update_remove_task(track_state, data[0][0])
        db.update_learning_track(track_state.track_id, track_state.get_sort())
        text = 'The task was successfully removed. New sort:\n'
        return await_change_current(track_state, text)

    if track_state.state == ChangeState.await_resort_existing:
        track_state = update_resort_existing(track_state, data[0][0])
        track_state = update_remove_task(track_state, data[0][0])
        # db.update_learning_track(track_state.track_id, track_state.get_sort())
        key = await_set_position(track_state)
        track_state.change_state(ChangeState.await_resort)
        return key

    if track_state.state == ChangeState.await_resort:
        track_state = update_set_position(track_state, data[0][0])
        db.update_learning_track(track_state.track_id, track_state.get_sort())
        text = 'The task was successfully moved. New sort:\n'
        return await_change_current(track_state, text)

    if track_state.state == ChangeState.await_new_sort:
        if user_state is not None and len(user_state) == 4:
            if user_state[3] == '1':
                return view_current_sort(track_state)
            elif user_state[3] == '2':
                db.update_learning_track(track_state.track_id, track_state.get_sort())
                text = 'The new sorting was successfully saved.\n'
                return await_current_sort(track_state, text)
            else:
                return await_change_current(track_state)
        if data is not None:
            track_state, add_text = update_new_sort(track_state, data[0][0])
            return await_new_sort(track_state, add_text)

    if track_state.state == ChangeState.view_current:
        return await_new_sort(track_state)

    return None


def view_current_sort(track_state):
    track_state.change_state(ChangeState.view_current)
    mes = track_sort_message(track_state, '')
    keyboard = [('Back to editing', '672')]
    return mes, keyboard


# TODO additional message are you sure
def await_new_sort(track_state, *add_text):
    track_state.change_state(ChangeState.await_new_sort)
    text = ''
    if len(add_text) > 0:
        text += add_text[0]
    text += 'Write Task ID to add to the end of the new sorting\n'
    mes = task.all_tasks_message(text)
    track_state.change_mes(mes)
    keyboard = [('View current new sorting', '6721'),
                ('Save sorting (OLD SORTING WILL BE DELETED)', '6722'),
                ("Back (PROGRESS WILL BE LOST)", "6723")]
    return mes, keyboard


# TODO opportunity to input several tasks
def update_new_sort(track_state, person, text):
    answer = update_add_task_middle(track_state, person, text)
    if type(answer) is not LearningTrack:
        return track_state, 'Incorrect Task ID. Please try again\n'
    track_state = answer
    if track_state.sorting is None:
        sort_id = 0
    else:
        sort_id = len(track_state.sorting)
    track_state = update_set_position(track_state, person, sort_id + 1)
    return track_state, 'Task was added to the new sorting.\n'


def await_learning_track(track_state):
    track_state.change_state(ChangeState.await_learn_track)
    tracks_list = get_all_learning_tracks()
    keyboard = []
    for track in tracks_list:
        button = track[1], f'67{str(track[0]).zfill(3)}'
        # button = track[0], f'67{str(track[0]).zfill(3)}'
        keyboard.append(button)
    keyboard.append(("Back", "56"))

    mes = f"Please select learning track:"
    return mes, keyboard


def get_all_learning_tracks():
    tracks_list = db.get_learning_tracks_list()
    return tracks_list


def update_learn_track(track_state, user_state):
    track_state.change_state(ChangeState.update_learn_track)
    track_state.change_track_id(int(user_state[2:5]))
    return track_state


# TODO add opportunity to delete track
def await_current_sort(track_state, *add_text):
    track_state.change_state(ChangeState.await_current_sort)
    mes = track_sort_message(track_state, add_text)
    track_state.change_mes(mes)
    keyboard = [('Change current sort', '671'),
                ('Make new sort from zero', '672'),
                ("Back", "56")]
    return mes, keyboard


def track_sort_message(track_state, add_text):
    sort = track_state.get_sort()
    mes = ''
    if len(add_text) > 0:
        mes += add_text[0]
    mes += 'Sort: Task ID\n'
    for i in range(len(sort)):
        mes += f'{i}: task {sort[i]}\n'
    if len(mes) == 0:
        mes = f'No tasks in the learning track yet.'
    return mes


def await_change_current(track_state, *add_text):
    track_state.change_state(ChangeState.await_change_current)
    mes = ''
    if len(add_text) > 0:
        mes += add_text[0]
    mes += track_state.sort_mes
    keyboard = [('Add new task to the track', '673'),
                ('Remove task from the track', '674'),
                ('Resort existing tasks in the track', '675'),
                ("Back", "56")]
    return mes, keyboard


def await_add_task_middle(track_state, *add_text):
    track_state.change_state(ChangeState.await_add_task_middle)
    mes = ''
    if len(add_text) > 0:
        mes += add_text[0]
    mes += 'Write Task ID to add to the learning track:\n'
    mes = task.all_tasks_message(mes)
    return mes, None


def await_remove_task(track_state, *add_text):
    track_state.change_state(ChangeState.await_remove_task)
    mes = ''
    if len(add_text) > 0:
        if type(add_text[0]) is str:
            mes += add_text[0]
    mes += 'Write task position to remove from the learning track:\n'
    mes += track_state.sort_mes
    return mes, None


def update_add_task_middle(track_state, text):
    try:
        task_id = int(text)
    except:
        return await_add_task_middle(track_state, 'Incorrect Task ID. Please try again\n')
    if not task.task_exists(task_id):
        return await_add_task_middle(track_state, 'Task ID doesn\'t exist. Please try again\n')
    track_state.change_state(ChangeState.update_add_task_middle)
    track_state.change_task(task_id)
    return track_state


def update_remove_task(track_state, text):
    try:
        position = int(text)
    except:
        return await_remove_task(track_state, 'Incorrect position. Please try again\n')

    new_sort = remove_position_from_sort(track_state, position)

    return update_sort(track_state, new_sort)


def remove_position_from_sort(track_state, position):
    sort = track_state.get_sort()
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


def await_set_position(track_state, *add_text):
    track_state.change_state(ChangeState.await_set_position)
    mes = ''
    if len(add_text) > 0:
        mes += add_text[0]
    mes += f'To which position do you want to insert task {track_state.current_task}\n'
    mes += track_state.sort_mes
    return mes, None


def update_set_position(track_state, text):
    try:
        position = int(text)
    except:
        return await_add_task_middle(track_state, 'Incorrect position. Please try again\n')

    sort = track_state.get_sort()
    new_sort = {}

    if position > len(sort):
        position = len(sort)
    if position < 0:
        position = 0

    for i in range(position):
        new_sort[i] = sort[i]
    new_sort[position] = track_state.current_task
    for i in range(position, len(sort)):
        new_sort[i + 1] = sort[i]

    track_state = update_sort(track_state, new_sort)
    return track_state


def update_sort(track_state, new_sort):
    track_state.change_sort(new_sort)
    track_state.change_mes(track_sort_message(track_state, ''))
    return track_state


def await_resort_existing(track_state, *add_text):
    answer = await_remove_task(track_state, add_text)
    track_state.change_state(ChangeState.await_resort_existing)
    return answer


def update_resort_existing(track_state, text):
    try:
        position = int(text)
    except:
        return await_resort_existing(track_state, 'Incorrect position. Please try again\n')
    sort = track_state.get_sort()
    task_id = sort[position]

    track_state.change_task(task_id)
    return track_state


def get_name_for_id(track_id):
    name = db.get_learning_track_name(track_id)
    if len(name) > 0:
        return name[0][0]
    return None
