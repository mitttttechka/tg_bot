from telegram import InlineKeyboardMarkup

import menus
import logging
from instances import learning_track, user, task


def handle_response_connection(message):
    response: (str, InlineKeyboardMarkup) = handle_response(message)
    if type(response) is str:
       response = (response, None)
    logging.info('Bot: ', response)
    message.reply_text(response[0], reply_markup=response[1])


def handle_response(message):
    user_id = message.chat.id
    text = message.text

    person = user.get_user(user_id)
    logging.debug('Created person')
    print(str(person.current_position))

    if "admin" in str(text):
        return menus.menu_button_press(50, user_id)

    elif person.current_position == 0:
        person.set_current_position(1)
        return "Hi! What's your name?", None

    elif person.current_position == 1:
        person.update_name(text)
        person.set_current_position(2)
        return menus.menu_button_press(2, user_id)

    elif person.current_position == 59:
        logging.warning('current_59')
        response = menus.add_task_menu(user_id, None, text)
        return response

    elif person.current_position == 63:
        logging.warning('current_63')
        task.add_new_section(text)
        response = menus.menu_button_press(54, user_id)
        mes = f'Section \'{text}\' has been added successfully!\n{response[0]}'
        return mes, response[1]

    elif person.current_position == 66:
        logging.warning('current_66')
        new_track_id = learning_track.add_learning_track(user_id, text)
        response = menus.menu_button_press(67000 + int(new_track_id), user_id)
        return response

    elif person.current_position == 67:
        logging.warning('current_67')
        response = menus.manage_learning_track_menu(user_id, None, text)
        return response

    return "Answer", None
