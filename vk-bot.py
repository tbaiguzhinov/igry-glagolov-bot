import logging
import os
import random

import telegram
from vk_api import VkApi
from dotenv import load_dotenv
from vk_api.longpoll import VkEventType, VkLongPoll
from dialogflow_response import get_workflow_response
from telegramlogshandler import TelegramLogsHandler

logger = logging.getLogger('Logger')


def respond(event, vk_api):
    project_id = os.getenv('GOOGLE_PROJECT_ID')
    response = get_workflow_response(event.text, event.user_id, project_id)
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
