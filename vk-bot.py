import logging
import os
import random

import telegram
from vk_api import VkApi
from dotenv import load_dotenv
from google.cloud import dialogflow
from vk_api.longpoll import VkEventType, VkLongPoll

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


def get_workflow_response(message, session_id):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.TextInput(text=message, language_code='ru')
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )
    if not response.query_result.intent.is_fallback:
        return response.query_result.fulfillment_text


def respond(event, vk_api):
    response = get_workflow_response(event.text, event.user_id)
    if response:
        vk_api.messages.send(
            user_id=event.user_id,
            message=response,
            random_id=random.randint(1, 1000)
        )


def main():
    load_dotenv()
    GROUP_TOKEN = os.getenv('VK_GROUP_TOKEN')
    logger_bot_token = os.getenv('LOGGER_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    project_id = os.getenv('GOOGLE_PROJECT_ID')

    vk_session = VkApi(token=GROUP_TOKEN)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    logger_bot = telegram.Bot(logger_bot_token)
    logger.addHandler(TelegramLogsHandler(logger_bot, chat_id))
    logger.warning("VK саппорт бот запущен")

    while True:
        try:
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    respond(event, vk_api)
        except Exception:
            logger.exception("VK бот упал с ошибкой:")
        except KeyboardInterrupt:
            raise


if __name__ == "__main__":
    main()
