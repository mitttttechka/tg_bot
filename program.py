from telegram import InlineKeyboardMarkup, InlineKeyboardButton

import menus
import logging
from instances import learning_track, user, task


async def handle_response_photo(message, context):
    file = message.photo[0].file_id
    # obj = context.bot.get_file(file)
    new_file = await message.effective_attachment[-1].get_file()
    file_to_write = open(f'files/{file}', 'wb')
    await new_file.download_to_memory(file_to_write)
    file_to_write.close()
    await handle_response_message(message, file)
    # await message.reply_text(f"{file} saved successfully")

    # chat_id = message.chat.id
    # file_to_send = open(f'files/{file}', 'rb')
    # await context.bot.send_photo(chat_id=chat_id, photo=file_to_send)


async def handle_response_message(message, *text):
    response: (str, [[str, str]]) = handle_response(message, text)
    if type(response) is str:
        response = (response, None)
    logging.info('Bot: ', response)
    await message.reply_text(response[0], reply_markup=array_to_keyboard(response[1]))


async def handle_button(query):
    response: (str, [[str, str]]) = menus.menu_button_press(query.data, query.message.chat.id)
    await query.edit_message_text(text=response[0], reply_markup=array_to_keyboard(response[1]))


def handle_response(message, *add_text):
    user_id = message.chat.id
    if len(add_text[0]) > 0:
        text = add_text[0][0]
    else:
        text = message.text

    person = user.get_user(user_id)
    logging.debug('Created person')

    return menus.message(person, text)


def array_to_keyboard(array):
    if array is None:
        return None
    keyboard = []
    for button in array:
        keyboard.append([InlineKeyboardButton(button[0], callback_data=button[1])])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup
