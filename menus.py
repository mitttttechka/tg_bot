from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import user
import task
import logging


def menu_button_press(data, user_id):
    data = str(data)
    original_data = data
    data = data[0:2]
    person = user.User(user_id)
    person.set_progress_point(int(data))
    logging.warning(f"Person {person.user_id} is here: {person.progress_point}")
    if data == '3':
        return learn_menu()
    elif data == '4':
        return practice_menu()
    elif data == '5':
        return tests_menu()
    elif data == '6':
        return profile_menu()
    elif data == '50':
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
        return manage_learning_tracks_menu()
    elif data == '59':
        return add_task(user_id, original_data)
    elif data == '63':
        return add_section_request()
    else:
        return main_menu()


def main_menu():
    keyboard = [
        [InlineKeyboardButton("Learn", callback_data="3")],
        [InlineKeyboardButton("Practice", callback_data="4")],
        [InlineKeyboardButton("Tests", callback_data="5")],
        [InlineKeyboardButton("Profile", callback_data="6")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    return f"Check out the menu!", reply_markup


def learn_menu():
    keyboard = [
        [InlineKeyboardButton("Continue learning", callback_data="7")],
        [InlineKeyboardButton("Jump to the theme", callback_data="8")],
        [InlineKeyboardButton("Back", callback_data="2")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return f"Let's learn something new!", reply_markup


def practice_menu():
    keyboard = [
        [InlineKeyboardButton("Practice the theme", callback_data="9")],
        [InlineKeyboardButton("Most often errors", callback_data="10")],
        [InlineKeyboardButton("Back", callback_data="2")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return f"Practice makes perfect!", reply_markup


def tests_menu():
    keyboard = [
        [InlineKeyboardButton("Training tests", callback_data="11")],
        [InlineKeyboardButton("Tests by the themes", callback_data="12")],
        [InlineKeyboardButton("Assigned tests", callback_data="13")],
        [InlineKeyboardButton("Back", callback_data="2")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return f"Don't be afraid!", reply_markup


def profile_menu():
    keyboard = [
        [InlineKeyboardButton("Profile settings", callback_data="14")],
        [InlineKeyboardButton("Class", callback_data="15")],
        [InlineKeyboardButton("Statistics", callback_data="16")],
        [InlineKeyboardButton("Back", callback_data="2")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return f"It's all about you!", reply_markup


def admin_menu():
    keyboard = [
        [InlineKeyboardButton("Manage users", callback_data="51")],
        [InlineKeyboardButton("Manage tasks", callback_data="52")],
        [InlineKeyboardButton("Manage classes", callback_data="53")],
        [InlineKeyboardButton("Manage sections", callback_data="54")],
        [InlineKeyboardButton("Manage tests", callback_data="55")],
        [InlineKeyboardButton("Manage learning_tracks", callback_data="56")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    return f"Admin menu / 50", reply_markup


def manage_users_menu():
    keyboard = [
        [InlineKeyboardButton("Delete user by id", callback_data="57")],
        [InlineKeyboardButton("Change user by id", callback_data="58")],
        [InlineKeyboardButton("Back", callback_data="50")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    return f"Manage users menu / 51", reply_markup


def manage_tasks_menu():
    keyboard = [
        [InlineKeyboardButton("Add task", callback_data="59")],
        [InlineKeyboardButton("Find task by id", callback_data="60")],
        [InlineKeyboardButton("Back", callback_data="50")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    return f"Manage tasks menu / 52", reply_markup


def add_task(user_id, original_data):
    logging.warning("We are here!")
    person = user.get_user(user_id)
    logging.warning(f"User {person.user_id} is here!")
    if person.working_on is None or type(person.working_on) is not task.Task:
        logging.warning("We are here!")
        new_task = task.Task()
        logging.warning("We are here!")
        person.working_on = new_task
    logging.warning("We are here!")
    task_state = person.working_on
    logging.warning("We are here")

    if len(original_data) > 2:
        task_state.section_id = int(original_data[2:5])
        user.update_active_users(person)

    if task_state.section_id is None:
        sections = task.get_all_sections()
        keyboard = []
        for section in sections:
            button = [InlineKeyboardButton(section[1], callback_data=f'59{str(section[0]).zfill(3)}')]
            keyboard.append(button)
        keyboard.append([InlineKeyboardButton("Back", callback_data="50")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        return f"Please select section for the task:", reply_markup
    elif task_state.text is None:
        return f"Please write task context for section {task_state.section_id}:", None
    #elif task_state.picture_link is None:  //// Pictures in tasks!
        #return f"Please send a picture"
    elif task_state.question is None:
        return f"Is the task is question and requires answer?"
    return f"Please write task context:", None


def manage_classes_menu():
    keyboard = [
        [InlineKeyboardButton("Add class", callback_data="61")],
        [InlineKeyboardButton("Find class by id", callback_data="62")],
        [InlineKeyboardButton("Back", callback_data="50")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    return f"Manage classes menu / 53", reply_markup


def manage_sections_menu():
    keyboard = [
        [InlineKeyboardButton("Add section", callback_data="63")],
        [InlineKeyboardButton("Find section by id", callback_data="64")],
        [InlineKeyboardButton("Back", callback_data="50")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    return f"Manage sections menu / 54", reply_markup


def add_section_request():
    return f"Please write new section name:", None


def manage_tests_menu():
    keyboard = [
        [InlineKeyboardButton("Change test rules", callback_data="65")],
        [InlineKeyboardButton("Manage prescripted tests by id", callback_data="66")],
        [InlineKeyboardButton("Back", callback_data="50")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    return f"Manage tests menu / 55", reply_markup


def manage_learning_tracks_menu():
    keyboard = [
        [InlineKeyboardButton("Add learning track", callback_data="66")],
        [InlineKeyboardButton("Manage learning track by id", callback_data="67")],
        [InlineKeyboardButton("Back", callback_data="50")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    return f"Manage learning tracks menu / 56", reply_markup