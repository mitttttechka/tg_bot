import user
import menus
import task
import logging


def handle_response(message) -> str:
    user_id = message.chat.id
    text = message.text

    person = user.get_user(user_id)
    logging.debug('Created person')
    print(str(person.progress_point))

    if "admin" in str(text):
        return menus.menu_button_press(50, user_id)

    elif person.progress_point == 0:
        person.set_progress_point(1)
        return "Hi! What's your name?", None

    elif person.progress_point == 1:
        person.update_name(text)
        person.set_progress_point(2)
        return menus.menu_button_press(2, user_id)

    elif person.progress_point == 63:
        logging.warning('progress_63')
        task.add_new_section(text)
        response = menus.menu_button_press(54, user_id)
        mes = f'Section \'{text}\' has been added successfully!\n{response[0]}'
        return (mes, response[1])

    return "Answer", None



