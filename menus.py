import logging
from instances import learning_track, question, user, task, section
import menu_navigation as nav


def menu_navigation(data, user_id, original_data, text):
    person: user.User = user.get_user(user_id)
    person.set_current_position(data)
    if data == nav.start:
        return start(person)
    elif data == nav.say_my_name:
        say_my_name(person, text)
        return main_menu()
    elif data == nav.learn_menu:
        return learn_menu()
    elif data == nav.practice_menu:
        return practice_menu()
    elif data == nav.tests_menu:
        return tests_menu()
    elif data == nav.profile_menu:
        return profile_menu()
    elif data == nav.admin_menu:
        user.get_user(user_id).update_working_on(None)
        return admin_menu()
    elif data == nav.manage_users_menu:
        user.get_user(user_id).update_working_on(None)
        return manage_users_menu()
    elif data == nav.manage_tasks_menu:
        user.get_user(user_id).update_working_on(None)
        return manage_tasks_menu()
    elif data == nav.manage_classes_menu:
        user.get_user(user_id).update_working_on(None)
        return manage_classes_menu()
    elif data == nav.manage_sections_menu:
        user.get_user(user_id).update_working_on(None)
        return manage_sections_menu()
    elif data == nav.manage_tests_menu:
        user.get_user(user_id).update_working_on(None)
        return manage_tests_menu()
    elif data == nav.learning_tracks_menu:
        user.get_user(user_id).update_working_on(None)
        return learning_tracks_menu()
    elif data == nav.add_task_menu:
        return add_task(user_id, original_data, text)
    elif data == nav.change_existing_task:
        return manage_task(user_id, original_data, text)
    elif data == nav.add_section_request:
        return add_section_request(text, person.user_id)
    elif data == nav.find_section:
        return manage_section(user_id, original_data, text)
    elif data == nav.add_learning_track_menu:
        return add_learning_track(user_id, text)
    elif data == nav.manage_learning_track_menu:
        return manage_learning_track(user_id, original_data, text)
    elif data == nav.add_question_menu:
        return add_question(user_id, original_data, text)
    else:
        return main_menu()


# TODO if user sends text when awaiting button press
def menu_button_press(data, user_id):
    data: str = str(data)
    original_data: str = data
    data: int = int(data[0:2])
    return menu_navigation(data, user_id, original_data, None)


def message(person: user.User, text):
    if "admin" in str(text):
        person.set_current_position(nav.admin_menu)
    # if person.current_position == nav.add_task_menu:
    #    response = add_task_menu(user_id, None, text)
    #    return response
    return menu_navigation(person.current_position, person.user_id, None, text)


def start(person):
    person.set_current_position(nav.say_my_name)
    return "Hi! What's your name?", None


def say_my_name(person, text):
    person.update_name(text)
    person.set_current_position(nav.main_menu)


def main_menu():
    keyboard = [["Learn", f'{nav.learn_menu}'],
                ["Practice", f'{nav.practice_menu}'],
                ["Tests", f'{nav.tests_menu}'],
                ["Profile", f'{nav.profile_menu}']]
    return f"Check out the menu!", keyboard


def learn_menu():
    keyboard = [["Continue learning", f'{nav.continue_learning}'],
                ["Jump to the theme", f'{nav.jump_to_theme}'],
                ["Back", f'{nav.main_menu}']]
    return f"Let's learn something new!", keyboard


def practice_menu():
    keyboard = [["Practice the theme", f'{nav.practice_theme}'],
                ["Most often errors", f'{nav.most_often_errors}'],
                ["Back", f'{nav.main_menu}']]
    return f"Practice makes perfect!", keyboard


def tests_menu():
    keyboard = [["Training tests", f'{nav.training_tests}'],
                ["Tests by the themes", f'{nav.tests_by_themes}'],
                ["Assigned tests", f'{nav.assigned_tests}'],
                ["Back", f'{nav.main_menu}']]
    return f"Don't be afraid!", keyboard


def profile_menu():
    keyboard = [["Profile settings", f'{nav.profile_settings}'],
                ["Class", f'{nav.my_class}'],
                ["Statistics", f'{nav.statistics}'],
                ["Back", f'{nav.main_menu}']]
    return f"It's all about you!", keyboard


def admin_menu():
    keyboard = [["Manage users", f'{nav.manage_users_menu}'],
                ["Manage tasks", f'{nav.manage_tasks_menu}'],
                ["Manage classes", f'{nav.manage_classes_menu}'],
                ["Manage sections", f'{nav.manage_sections_menu}'],
                ["Manage tests", f'{nav.manage_tests_menu}'],
                ["Manage learning_tracks", f'{nav.learning_tracks_menu}']]
    return f"Admin menu / {nav.admin_menu}", keyboard


def manage_users_menu():
    keyboard = [["Delete user by id", f'{nav.delete_user_menu}'],
                ["Change existing user", f'{nav.change_user_menu}'],
                ["Back", f'{nav.admin_menu}']]
    return f"Manage users menu / {nav.manage_users_menu}", keyboard


def manage_tasks_menu():
    keyboard = [["Add task", f'{nav.add_task_menu}'],
                ["Change existing task", f'{nav.change_existing_task}'],
                ["Back", f'{nav.admin_menu}']]
    return f"Manage tasks menu / {nav.manage_tasks_menu}", keyboard


def manage_classes_menu():
    keyboard = [["Add class", f'{nav.add_class}'],
                ["Change existing class", f'{nav.find_class}'],
                ["Back", f'{nav.admin_menu}']]
    return f"Manage classes menu / {nav.manage_classes_menu}", keyboard


def manage_sections_menu():
    keyboard = [["Add section", f'{nav.add_section_request}'],
                ["Change existing section", f'{nav.find_section}'],
                ["Back", f'{nav.admin_menu}']]
    return f"Manage sections menu / {nav.manage_sections_menu}", keyboard


def learning_tracks_menu():
    keyboard = [["Add learning track", f'{nav.add_learning_track_menu}'],
                ["Change existing learning track", f'{nav.manage_learning_track_menu}'],
                ["Back", f'{nav.admin_menu}']]
    return f"Learning tracks menu / {nav.learning_tracks_menu}", keyboard


def manage_tests_menu():
    keyboard = [["Add prescripted test", f'{nav.add_test_menu}'],
                ["Change existing prescripted test", f'{nav.change_existing_test_menu}'],
                ["Manage test rules", f'{nav.change_test_rules_menu}'],
                ["Back", f'{nav.admin_menu}']]
    return f"Learning tracks menu / {nav.learning_tracks_menu}", keyboard


def add_task(user_id, user_state, *text):
    reply = task.add_task(user_id, user_state, text)
    mes = reply[0]
    keyboard = reply[1]
    if len(reply) == 3:
        complete = menu_button_press(nav.manage_tasks_menu, user_id)
        mes += f'\n{complete[0]}'
        keyboard = complete[1]
    return mes, keyboard


def manage_task(user_id, user_state, *text):
    reply = task.manage_task(user_id, user_state, text)
    mes = reply[0]
    keyboard = reply[1]
    if len(reply) == 3:
        complete = menu_button_press(nav.manage_tasks_menu, user_id)
        mes += f'\n{complete[0]}'
        keyboard = complete[1]
    return mes, keyboard


def add_question(user_id, user_state, *text):
    reply = question.add_question(user_id, user_state, text)
    mes = reply[0]
    keyboard = reply[1]
    if len(reply) == 3:
        complete = menu_button_press(nav.manage_tasks_menu, user_id)
        mes += f'\n{complete[0]}'
        keyboard = complete[1]
    return mes, keyboard


def add_section_request(text, user_id):
    if text is not None:
        section.add_new_section(text)
        response = menu_button_press(nav.manage_sections_menu, user_id)
        mes = f'Section \'{text}\' has been added successfully!\n{response[0]}'
        return mes, response[1]
    return f"Please write new section name:", None


def manage_section(user_id, user_state, *text):
    reply = section.manage_section(user_id, user_state, text)
    mes = reply[0]
    keyboard = reply[1]
    return mes, keyboard


def add_learning_track(user_id, text):
    if text is not None:
        new_track_id = learning_track.add_learning_track(user_id, text)
        response = menu_button_press(nav.manage_learning_track_menu * 1000 + int(new_track_id), user_id)
        return response
    return "Please enter new learning track name", None


def manage_learning_track(user_id, user_state, *text):
    reply = learning_track.manage_learning_track(user_id, user_state, text)
    return reply[0], reply[1]

