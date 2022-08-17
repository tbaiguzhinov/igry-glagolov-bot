import logging
import os

import telegram
from dotenv import load_dotenv
from dialogflow_response import get_workflow_response
from telegram import Update
from telegramlogshandler import LogsHandler
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          MessageHandler, Updater)

logger = logging.getLogger('Logger')


def start(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Здравствуйте!"
    )


def response(update: Update, context: CallbackContext):
    project_id = os.getenv('GOOGLE_PROJECT_ID')
    is_fallback, response = get_workflow_response(
        update.message.text,
        update.message.from_user.id,
        project_id,
    )
    if is_fallback:
        response = 'Я Вас не понял, передаю запрос службе поддержки'
    update.message.reply_text(response)


def error_handler(update: Update, context: CallbackContext):
    logger.error(msg="Телеграм бот упал с ошибкой:", exc_info=context.error)


def main():
    load_dotenv()
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    logger_bot_token = os.getenv('LOGGER_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    logger_bot = telegram.Bot(logger_bot_token)
    logger.addHandler(LogsHandler(logger_bot, chat_id))
    logger.warning("Telegram саппорт бот запущен")

    updater = Updater(token=telegram_token, use_context=True)
    dispatcher = updater.dispatcher
    
    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(Filters.text, response)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(message_handler)
    dispatcher.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()
    

if __name__ == "__main__":
    main()
