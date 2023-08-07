import user
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def handle_response(message) -> str:
    user_id = message.chat.id
    text = message.text

    person = user.User(user_id)
    if person.progress_point == 0:
        person.set_progress_point(1)

    if person.progress_point == 1:
        person.update_name(text)
        person.set_progress_point(2)

    if person.progress_point == 1:
        return "Hi! What's your name?", None
    elif person.progress_point == 2:
        return menu_button_press(2)

    return "Answer", None


def menu_button_press(data):
    if data == '3':
        return learn_menu()
    elif data == '4':
        return practice_menu()
    elif data == '5':
        return tests_menu()
    elif data == '6':
        return profile_menu()
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
        [InlineKeyboardButton("Continue learning", callback_data="6")],
        [InlineKeyboardButton("Jump to the theme", callback_data="7")],
        [InlineKeyboardButton("Back", callback_data="2")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return f"Let's learn something new!", reply_markup


def practice_menu():
    keyboard = [
        [InlineKeyboardButton("Practice the theme", callback_data="8")],
        [InlineKeyboardButton("Most often errors", callback_data="9")],
        [InlineKeyboardButton("Back", callback_data="2")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return f"Practice makes perfect!", reply_markup


def tests_menu():
    keyboard = [
        [InlineKeyboardButton("Training tests", callback_data="10")],
        [InlineKeyboardButton("Tests by the themes", callback_data="11")],
        [InlineKeyboardButton("Assigned tests", callback_data="12")],
        [InlineKeyboardButton("Back", callback_data="2")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return f"Don't be afraid!", reply_markup


def profile_menu():
    keyboard = [
        [InlineKeyboardButton("Profile settings", callback_data="13")],
        [InlineKeyboardButton("Class", callback_data="14")],
        [InlineKeyboardButton("Statistics", callback_data="15")],
        [InlineKeyboardButton("Back", callback_data="2")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return f"It's all about you!", reply_markup

