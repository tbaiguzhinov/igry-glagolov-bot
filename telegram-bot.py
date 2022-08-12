import logging
import os

import json
import html
import traceback
import telegram
from dotenv import load_dotenv
from google.cloud import dialogflow
from telegram import Update
from telegram.constants import PARSEMODE_HTML
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          MessageHandler, Updater)

logger = logging.getLogger('Logger')


class TelegramLogsHandler(logging.Handler):
    """Logger handler class."""

    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def start(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Здравствуйте!"
    )


def response(update: Update, context: CallbackContext):
    response = get_workflow_response(
        update.message.text,
        update.message.from_user.id
    )
    update.message.reply_text(response)


def get_workflow_response(message, session_id):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.TextInput(text=message, language_code='ru')
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )
    return response.query_result.fulfillment_text


def error_handler(update: Update, context: CallbackContext):
    logger.error(msg="Бот упал с ошибкой:", exc_info=context.error)


def main():
    logger_bot = telegram.Bot(logger_bot_token)
    logger.addHandler(TelegramLogsHandler(logger_bot, chat_id))
    logger.warning("Саппорт бот запущен")

    updater = Updater(token=telegram_token, use_context=True)
    dispatcher = updater.dispatcher
    
    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(Filters.text, response)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(echo_handler)
    dispatcher.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()
    


if __name__ == "__main__":
    load_dotenv()
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    logger_bot_token = os.getenv('LOGGER_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    project_id = os.getenv('GOOGLE_PROJECT_ID')

    main()
