from typing import Final
from telegram.ext import *
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

import keys
import db
import program

print ('Starting up bot...')

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with three inline buttons attached."""
    await update.message.reply_text('Welcome to the learning bot!')

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    response: (str, InlineKeyboardMarkup) = program.menu_button_press(query.data)

    await query.edit_message_text(text=response[0], reply_markup=response[1])

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('I\'ll help you')

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This is custom command')


async def handle_massage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) says: "{text}"')

    response: (str, InlineKeyboardMarkup) = program.handle_response(update.message)

    print('Bot: ', response)
    await update.message.reply_text(response[0], reply_markup=response[1])

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error: {context.error}')

if __name__ == '__main__':
    db.connect()
    #db.renew_database()
    dp = Application.builder().token(keys.token).build()
    dp.add_handler(CommandHandler('start', start_command))
    dp.add_handler(CommandHandler('help', help_command))
    dp.add_handler(CommandHandler('custom', custom_command))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(filters.TEXT, handle_massage))

    dp.add_error_handler(error)

    dp.run_polling(poll_interval=3)

    #db.disconnect()

