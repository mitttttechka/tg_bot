from typing import Final
from telegram.ext import *
from telegram import Update

import keys

print ('Starting up bot...')

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello there, I\'m a bot')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('I\'ll help you')

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This is custom command')

def handle_response(text: str) -> str:
    processed: str = text.lower()

    if 'hello' in processed:
        return 'Hey there!'

    if 'how are you' in processed:
        return 'I\'m good and you?'

    return 'Idk'

async def handle_massage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text
    response = ''

    print(f'User ({update.message.chat.id}) says: "{text}" in: {message_type}')

    if message_type == 'group':
        if '@learn_without_bs_bot' in text:
            new_text: str = text.replace('@learn_without_bs_bot', '').strip()
            response: str = handle_response(new_text)
    else:
        response: str = handle_response(text)

    print('Bot: ', response)
    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error: {context.error}')

if __name__ == '__main__':
    dp = Application.builder().token(keys.token).build()
    dp.add_handler(CommandHandler('start', start_command))
    dp.add_handler(CommandHandler('help', help_command))
    dp.add_handler(CommandHandler('custom', custom_command))

    dp.add_handler(MessageHandler(filters.TEXT, handle_massage))

    dp.add_error_handler(error)

    dp.run_polling(poll_interval=3)

