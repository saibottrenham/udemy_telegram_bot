from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters,
    ConversationHandler, CallbackContext
)
from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from data_source import DataSource
import os
import threading
import time
import datetime



ADD_REMINDER_TEXT = 'Add Reminder ⏰'
INTERVAL = 30

TOKEN = os.getenv('TOKEN')
ENTER_MESSAGE, ENTER_TIME = range(2)
datasource = DataSource(os.getenv('DATABASE_URL'))


def start_handler(update, context):
    update.message.reply_text('Hi!', reply_markup=add_reminder_button())


def add_reminder_button():
    keyboard = [[KeyboardButton(ADD_REMINDER_TEXT)]]
    return ReplyKeyboardMarkup(keyboard)


def add_reminder_handler(update: Update, context: CallbackContext):
    update.message.reply_text('Please enter a message of the reminder:')
    return ENTER_MESSAGE


def enter_message_handler(update: Update, context: CallbackContext):
    update.message.reply_text('Please enter a time of the reminder:')
    context.user_data['message_text'] = update.message.text
    return ENTER_TIME


def enter_time_handler(update: Update, context: CallbackContext):
    message_text = context.user_data['message_text']
    message_time = datetime.datetime.strptime(update.message.text, "%d/%m/%Y %H:%M")
    message_data = datasource.create_reminder(update.message.chat_id, message_text, message_time)
    update.message.reply_text(f'Your reminder: {message_data.__repr__()}')
    return ConversationHandler.END


def start_check_reminder_task():
    thread = threading.Thread(target=check_reminders, args=())
    thread.daemon = True
    thread.start()


def check_reminders():
    while True:
        for reminder_data in datasource.get_all_reminders():
            if reminder_data.should_be_fired():
                datasource.fire_reminder(reminder_data.reminder_id)
                updater.bot.send_message(reminder_data.chat_id, reminder_data.message)
        time.sleep(INTERVAL)


if __name__ == '__main__':
    updater = Updater(token=TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler('start', start_handler))
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(ADD_REMINDER_TEXT), add_reminder_handler)],
        states={
            ENTER_MESSAGE: [MessageHandler(Filters.all, enter_message_handler)],
            ENTER_TIME: [MessageHandler(Filters.all, enter_time_handler)]
        },
        fallbacks=[]
    )
    updater.dispatcher.add_handler(conv_handler)
    datasource.create_tables()
    updater.start_polling()
    start_check_reminder_task()
