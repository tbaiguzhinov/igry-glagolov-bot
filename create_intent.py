import argparse
import json
import os

from dotenv import load_dotenv
from google.cloud import dialogflow


def create_intent(display_name, training_phrases, answer):
    intents_client = dialogflow.IntentsClient()

    parent = dialogflow.AgentsClient.agent_path(project_id)
    phrases = []
    for training_phrase in training_phrases:
        part = dialogflow.Intent.TrainingPhrase.Part(text=training_phrase)
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=answer)
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name, training_phrases=phrases, messages=[message]
    )

    intents_client.create_intent(
        request={"parent": parent, "intent": intent}
    )

    return f"Intent created: {display_name}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'path_to_file',
        type=str,
        help='Location of json file with questions and answers'
    )
    args = parser.parse_args()
    with open(args.path_to_file, 'r', encoding='utf-8') as file:
        training_set = json.load(file)

    for display_name, q_and_a in training_set.items():
        response = create_intent(
            display_name=display_name,
            training_phrases=q_and_a['questions'],
            answer=[q_and_a['answer']],
        )
        print(response)


if __name__ == "__main__":
    load_dotenv()
    project_id = os.getenv('GOOGLE_PROJECT_ID')
    main()
