import logging
import db
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
    await_resort = 19


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

    def change_state(self, state, person):
        self.state = state
        person.working_on = self
        user.update_active_users(person)
        return self

    def change_track_id(self, track_id, person):
        self.track_id = track_id
        person.working_on = self
        user.update_active_users(person)
        return self

    def change_mes(self, mes, person):
        self.sort_mes = mes
        person.working_on = self
        user.update_active_users(person)
        return self

    def change_task(self, task_id, person):
        self.current_task = task_id
        person.working_on = self
        user.update_active_users(person)
        return self

    def change_sort(self, new_sort, person):
        self.sorting = new_sort
        person.working_on = self
        user.update_active_users(person)
        return self


# TODO add several learning tracks. Maybe add table for learning_track - name
# def add_learning_track():


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
        return await_learning_track(track_state, person)

    if track_state.state == ChangeState.await_learn_track:
        track_state = update_learn_track(track_state, person, user_state)
        return await_current_sort(track_state, person)

    if track_state.state == ChangeState.await_current_sort:
        if user_state[2] == '1':
            return await_change_current(track_state, person)
        elif user_state[2] == '2':
            return await_new_sort(track_state, person)

    if track_state.state == ChangeState.await_change_current:
        if user_state[2] == '3':
            return await_add_task_middle(track_state, person)
        elif user_state[2] == '4':
            return await_remove_task(track_state, person)
        elif user_state[2] == '5':
            return await_resort_existing(track_state, person)

    if track_state.state == ChangeState.await_add_task_middle:
        track_state = update_add_task_middle(track_state, person, data[0][0])
        return await_set_position(track_state, person)

    if track_state.state == ChangeState.await_set_position:
        track_state = update_set_position(track_state, person, data[0][0])
        db.update_learning_track(track_state.track_id, track_state.get_sort())
        text = 'The task was successfully added. New sort:\n'
        return await_change_current(track_state, person, text)

    if track_state.state == ChangeState.await_remove_task:
        track_state = update_remove_task(track_state, person, data[0][0])
        db.update_learning_track(track_state.track_id, track_state.get_sort())
        text = 'The task was successfully removed. New sort:\n'
        return await_change_current(track_state, person, text)

    # TODO can optimize without twice db usage
    if track_state.state == ChangeState.await_resort_existing:
        track_state = update_resort_existing(track_state, person, data[0][0])
        track_state = update_remove_task(track_state, person, data[0][0])
        # db.update_learning_track(track_state.track_id, track_state.get_sort())
        key = await_set_position(track_state, person)
        track_state.change_state(ChangeState.await_resort, person)
        return key

    if track_state.state == ChangeState.await_resort:
        track_state = update_set_position(track_state, person, data[0][0])
        db.update_learning_track(track_state.track_id, track_state.get_sort())
        text = 'The task was successfully moved. New sort:\n'
        return await_change_current(track_state, person, text)
    # TODO continue to manage learning track

    if track_state.state == ChangeState.await_new_sort:
        return None
    return None


# TODO additional message are you sure
def await_new_sort(track_state, person):
    track_state = track_state.change_state(ChangeState.await_new_sort, person)
    add_text = 'Write Task ID to add to the end of the new sorting\n'
    mes = task.all_tasks_message(add_text)
    track_state.change_mes(mes, person)
    keyboard = [('View current new sorting', '6721'),
                ('Save sorting (OLD SORTING WILL BE DELETED)', '6722'),
                ("Back (PROGRESS WILL BE LOST)", "56")]
    return mes, keyboard


def update_new_sort(track_state, person, text):
    track_state = update_add_task_middle(track_state, person, text)
    update_set_position(track_state, person, len(track_state.sorting) + 1)


def await_learning_track(track_state, person):
    track_state.change_state(ChangeState.await_learn_track, person)
    tracks_list = get_all_learning_tracks()
    keyboard = []
    for track in tracks_list:
        button = track[0], f'67{str(track[0]).zfill(3)}'
        keyboard.append(button)
    keyboard.append(("Back", "56"))

    mes = f"Please select learning track:"
    return mes, keyboard


def get_all_learning_tracks():
    tracks_list = db.get_learning_tracks_list()
    return tracks_list


def update_learn_track(track_state, person, user_state):
    track_state = track_state.change_state(ChangeState.update_learn_track, person)
    track_state = track_state.change_track_id(int(user_state[2:5]), person)
    return track_state


def await_current_sort(track_state, person):
    track_state = track_state.change_state(ChangeState.await_current_sort, person)
    sort = track_state.get_sort()
    mes = 'Sort: Task ID\n'
    for i in range(len(sort)):
        mes += f'{i}: task {sort[i]}\n'
    if len(mes) == 0:
        mes = f'No tasks in the learning track yet.'
    track_state.change_mes(mes, person)
    keyboard = [('Change current sort', '671'),
                ('Make new sort from zero', '672'),
                ("Back", "56")]
    return mes, keyboard


def await_change_current(track_state, person, *add_text):
    track_state = track_state.change_state(ChangeState.await_change_current, person)
    mes = ''
    if len(add_text) > 0:
        mes += add_text[0]
    mes += track_state.sort_mes
    keyboard = [('Add new task to the track', '673'),
                ('Remove task from the track', '674'),
                ('Resort existing tasks in the track', '675'),
                ("Back", "56")]
    return mes, keyboard


def await_add_task_middle(track_state, person, *add_text):
    track_state.change_state(ChangeState.await_add_task_middle, person)
    mes = ''
    if len(add_text) > 0:
        mes += add_text[0]
    mes += 'Write Task ID to add to the learning track:\n'
    mes = task.all_tasks_message(mes)
    return mes, None


def await_remove_task(track_state, person, *add_text):
    track_state = track_state.change_state(ChangeState.await_remove_task, person)
    mes = ''
    if len(add_text) > 0:
        if type(add_text[0]) is str:
            mes += add_text[0]
    mes += 'Write task position to remove from the learning track:\n'
    mes += track_state.sort_mes
    return mes, None


def update_add_task_middle(track_state, person, text):
    try:
        task_id = int(text)
    except:
        return await_add_task_middle(track_state, person, 'Incorrect Task ID. Please try again\n')
    if not task.task_exists(task_id):
        return await_add_task_middle(track_state, person, 'Task ID doesn\'t exist. Please try again\n')
    track_state = track_state.change_state(ChangeState.update_add_task_middle, person)
    track_state = track_state.change_task(task_id, person)
    return track_state


def update_remove_task(track_state, person, text):
    try:
        position = int(text)
    except:
        return await_remove_task(track_state, person, 'Incorrect position. Please try again\n')

    new_sort = remove_position_from_sort(track_state, position)

    return update_sort(track_state, person, new_sort)


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


def await_set_position(track_state, person, *add_text):
    track_state = track_state.change_state(ChangeState.await_set_position, person)
    mes = ''
    if len(add_text) > 0:
        mes += add_text[0]
    mes += f'To which position do you want to insert task {track_state.current_task}\n'
    mes += track_state.sort_mes
    return mes, None


def update_set_position(track_state, person, text):
    try:
        position = int(text)
    except:
        return await_add_task_middle(track_state, person, 'Incorrect position. Please try again\n')

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

    return update_sort(track_state, person, new_sort)


def update_sort(track_state, person, new_sort):
    mes = 'Sort: Task ID'
    for i in range(len(new_sort)):
        mes += f'{i}: task {new_sort[i]}\n'
    if len(mes) == 0:
        mes = 'No tasks in the learning track yet.'
    track_state = track_state.change_mes(mes, person)
    track_state = track_state.change_sort(new_sort, person)

    return track_state


def await_resort_existing(track_state, person, *add_text):
    answer = await_remove_task(track_state, person, add_text)
    track_state.change_state(ChangeState.await_resort_existing, person)
    return answer


def update_resort_existing(track_state, person, text):
    try:
        position = int(text)
    except:
        return await_resort_existing(track_state, person, 'Incorrect position. Please try again\n')
    sort = track_state.get_sort()
    task_id = sort[position]

    track_state = track_state.change_task(task_id, person)
    return track_state
