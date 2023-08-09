import user
import menus
import logging

def handle_response(message) -> str:
    user_id = message.chat.id
    text = message.text

    person = user.User(user_id)
    logging.debug('Created person')

    if "admin" in str(text):
        return menus.menu_button_press(50, user_id)

    elif person.progress_point == 0:
        person.set_progress_point(1)
        return "Hi! What's your name?", None

    elif person.progress_point == 1:
        person.update_name(text)
        person.set_progress_point(2)
        return menus.menu_button_press(2, user_id)

    return "Answer", None



