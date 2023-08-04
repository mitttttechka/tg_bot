from typing import Final
from telegram.ext import *
import keys

print ('Starting up bot...')

def start_command(update, context):
    update.message.reply_text('Hello there, I\'m a bot')

def help_command(update, context):
    update.message.reply_text('I\'ll help you')

def custom_command(update, context):
    update.message.reply_text('This is custom command')

def handle_response(text: str) -> str:
    if 'hello' in text:
        return 'Hey there!'

    if 'how are you' in text:
        return 'I\'m good and you?'

    return 'Idk'

def handle_massage(update, context):
    message_type = update.message.chat.type
    text = str(update.message.text).lower()
    response = ''

    print(f'User ({update.message.chat.id}) says: "{text} in: {message_type}"')

    if message_type == 'group':
        if '@learn_without_bs_bot' in text:
            new_text = text.replace('@learn_without_bs_bot', '').strip()
            response = handle_response(new_text)
        else:
            response = handle_response(text)

    update.message.reply_text(response)

def error(update, context):
    print(f'Update {update} caused error: {context.error}')

if __name__ == '__main__':
    updater = Updater(keys.token, use_context = True)
    dp = updater.dispatcher

    #commands
    dp.add_handler(CommandHandler('start', start_command))
    dp.add_handler(CommandHandler('help', start_command))
    dp.add_handler(CommandHandler('custom', start_command))

    #dp.add_handler(MessageHandler(Filters.text, handle_massage))

    dp.add_error_handler(error)

    updater.start_polling(1.0)
    updater.idle()