import logging
from instances import learning_track, question, user, task


# TODO if user sends text when awaiting button press
def menu_button_press(data, user_id):
    data = str(data)
    original_data = data
    data = data[0:2]
    person = user.get_user(user_id)
    person.set_current_position(int(data))
    logging.warning(f"Person {person.user_id} is here: {person.current_position}. Data: {original_data}")
    if data == '3':
        return learn_menu()
    elif data == '4':
        return practice_menu()
    elif data == '5':
        return tests_menu()
    elif data == '6':
        return profile_menu()
    elif data == '50':
        user.get_user(user_id).update_working_on(None)
        return admin_menu()
    elif data == '51':
        return manage_users_menu()
    elif data == '52':
        return manage_tasks_menu()
    elif data == '53':
        return manage_classes_menu()
    elif data == '54':
        return manage_sections_menu()
    elif data == '55':
        return manage_tests_menu()
    elif data == '56':
        user.get_user(user_id).update_working_on(None)
        return learning_tracks_menu()
    elif data == '59':
        return add_task_menu(user_id, original_data)
    elif data == '63':
        return add_section_request()
    elif data == '66':
        return add_learning_track_menu()
    elif data == '67':
        return manage_learning_track_menu(user_id, original_data)
    elif data == '70':
        return add_question_menu(user_id, original_data)
    else:
        return main_menu()


def main_menu():
    keyboard = [["Learn", "3"],
                ["Practice", "4"],
                ["Tests", "5"],
                ["Profile", "6"]]
    return f"Check out the menu!", keyboard


def learn_menu():
    keyboard = [["Continue learning", "7"],
                ["Jump to the theme", "8"],
                ["Back", "2"]]
    return f"Let's learn something new!", keyboard


def practice_menu():
    keyboard = [["Practice the theme", "9"],
                ["Most often errors", "10"],
                ["Back", "2"]]
    return f"Practice makes perfect!", keyboard


def tests_menu():
    keyboard = [["Training tests", "11"],
                ["Tests by the themes", "12"],
                ["Assigned tests", "13"],
                ["Back", "2"]]
    return f"Don't be afraid!", keyboard


def profile_menu():
    keyboard = [["Profile settings", "14"],
                ["Class", "15"],
                ["Statistics", "16"],
                ["Back", "2"]]
    return f"It's all about you!", keyboard


def admin_menu():
    keyboard = [["Manage users", "51"],
                ["Manage tasks", "52"],
                ["Manage classes", "53"],
                ["Manage sections", "54"],
                ["Manage tests", "55"],
                ["Manage learning_tracks", "56"]]
    return f"Admin menu / 50", keyboard


def manage_users_menu():
    keyboard = [["Delete user by id", "57"],
                ["Change user by id", "58"],
                ["Back", "50"]]
    return f"Manage users menu / 51", keyboard


def manage_tasks_menu():
    keyboard = [["Add task", "59"],
                ["Find task by id", "60"],
                ["Back", "50"]]
    return f"Manage tasks menu / 52", keyboard


def add_task_menu(user_id, user_state, *text):
    reply = task.add_task(user_id, user_state, text)
    message = reply[0]
    keyboard = reply[1]
    if len(reply) == 3:
        complete = menu_button_press(52, user_id)
        message += f'\n{complete[0]}'
        keyboard = complete[1]

    return message, keyboard


def add_question_menu(user_id, user_state, *text):
    reply = question.add_question(user_id, user_state, text)
    message = reply[0]
    keyboard = reply[1]
    if len(reply) == 3:
        complete = menu_button_press(52, user_id)
        message += f'\n{complete[0]}'
        keyboard = complete[1]
    return message, keyboard


def manage_classes_menu():
    keyboard = [["Add class", "61"],
                ["Find class by id", "62"],
                ["Back", "50"]]
    return f"Manage classes menu / 53", keyboard


def manage_sections_menu():
    keyboard = [["Add section", "63"],
                ["Find section by id", "64"],
                ["Back", "50"]]
    return f"Manage sections menu / 54", keyboard


def add_section_request():
    return f"Please write new section name:", None


def manage_tests_menu():
    keyboard = [["Change test rules", "65"],
                ["Manage prescripted tests by id", "66"],
                ["Back", "50"]]
    return f"Manage tests menu / 55", keyboard


def learning_tracks_menu():
    keyboard = [["Add learning track", "66"],
                ["Manage learning track by id", "67"],
                ["Back", "50"]]
    return f"Manage learning tracks menu / 56", keyboard


def add_learning_track_menu():
    return "Please enter new learning track name", None


def manage_learning_track_menu(user_id, user_state, *text):
    reply = learning_track.manage_learning_track(user_id, user_state, text)
    return reply[0], reply[1]



