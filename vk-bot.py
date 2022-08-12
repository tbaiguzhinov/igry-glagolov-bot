import random
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from google.cloud import dialogflow
from dotenv import load_dotenv
import os


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
            random_id=random.randint(1,1000)
        )


def main():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            respond(event, vk_api)


if __name__ == "__main__":
    load_dotenv()
    GROUP_TOKEN = os.getenv('VK_GROUP_TOKEN')
    project_id = os.getenv('GOOGLE_PROJECT_ID')

    vk_session = vk_api.VkApi(token=GROUP_TOKEN)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    main()
