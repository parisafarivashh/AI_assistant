import json
import os
import time
from datetime import datetime

from openai import OpenAI


class Agent:

    def __init__(self, token):
        self.client = OpenAI(api_key=token)

    def _setup_assistant(self, assistant_name):
        """ This function creates a new assistant with the OpenAI Assistant API
        """
        assistant = self.client.beta.assistants.create(
            name=assistant_name,
            instructions=f"""
               You are a friend. Your name is {assistant_name}. You 
               are having a vocal conversation with a user. 
               You will never output any markdown or formatted text of any 
               kind, and you will speak in a concise, highly conversational 
               manner. You will adopt any persona that the user may ask of you.
               """,
            model="gpt-4-1106-preview",
        )
        # Create a thread
        thread = self.client.beta.threads.create()
        return assistant.id, thread.id

    def _send_message(self, thread_id, task):
        """ This function sends your message into the thread object,
        which then gets passed to the AI.
        """
        thread_message = self.client.beta.threads.messages.create(
            thread_id,
            role="user",
            content=task,
        )
        return thread_message

    def _run_assistant(self, assistant_id, thread_id):
        """ Runs the assistant with the given thread and assistant IDs.
        """
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )

        while run.status == "in_progress" or run.status == "queued":
            time.sleep(1)
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )

            if run.status == "completed":
                messages = self.client.beta.threads.messages.list(
                    thread_id=thread_id
                )
                return messages

    @staticmethod
    def _save_session(
            assistant_id,
            thread_id,
            user_name_input,
            file_path='chat_sessions.json',
    ):
        """ This function saves your session data locally, so you can easily
        retrieve it from the JSON file at any time.
        """
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                data = json.load(file)

        else:
            data = {"sessions": {}}

        next_session_number = str(len(data["sessions"]) + 1)

        data["sessions"][next_session_number] = {
            "AssistantID": assistant_id,
            "ThreadID": thread_id,
            "UserNameInput": user_name_input,
        }

        # Save data back to file
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

    @staticmethod
    def _display_sessions(file_path='chat_sessions.json'):
        """ This function shows your available sessions when you request it
        """
        if not os.path.exists(file_path):
            print("No sessions available.")
            return

        with open(file_path, 'r') as file:
            data = json.load(file)

        print("Available Sessions:")
        for number, session in data["sessions"].items():
            print(f"Session {number}: {session['UserNameInput']}")

    @staticmethod
    def _get_session_data(session_number, file_path='chat_sessions.json'):
        """ This function retrieves the session that you choose.
        """
        with open(file_path, 'r') as file:
            data = json.load(file)

        session = data["sessions"].get(session_number)
        if session:
            return session["AssistantID"], session["ThreadID"], session["UserNameInput"]
        else:
            print("Session not found.")
            return None, None

    def _collect_message_history(self, thread_id, user_name_input):
        """ This function downloads and writes your entire chat history
        to a text file, so you can keep your own records.
        """
        messages = self.client.beta.threads.messages.list(thread_id)
        message_dict = json.loads(messages.model_dump_json())

        with open(f'{user_name_input}_message_log.txt', 'w') as message_log:
            for message in reversed(message_dict['data']):
                text_value = message['content'][0]['text']['value']

                # Adding a prefix to distinguish between user and assistant messages
                if message['role'] == 'assistant':
                    prefix = f"{user_name_input}: "
                else:  # Assuming any other role is the user
                    prefix = "You: "

                # Writing the prefixed message to the log
                message_log.write(prefix + text_value + '\n')

        return f"Messages saved to {user_name_input}_message_log.txt"

    def create(self):
        user_choice = input(
            "Type 'new' to make a new assistant session. "
            "Press 'Enter' to choose an existing assistant session: "
        )
        if user_choice == 'new':
            user_name_input = input("Please type a name for this chat: ")
            IDS = self._setup_assistant(assistant_name=user_name_input)
            self._save_session(IDS[0], IDS[1], user_name_input)

            assistant_id = IDS[0]
            thread_id = IDS[1]

        else:
            self._display_sessions()
            session_number = input("Enter the session number to load: ")
            assistant_id, thread_id, user_name_input = self._get_session_data(
                session_number
            )

        if assistant_id and thread_id:
            print(
                f"Created Session with {user_name_input}, "
                f"Assistant ID: {assistant_id} and Thread ID: {thread_id}"
            )
            first_iteration = True
            while True:
                user_message = input("Please type your question: ")

                if first_iteration:
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
                    user_message = f"It is now {current_time}. {user_message}"
                    first_iteration = False

                if user_message.lower() == 'exit':
                    print("Exiting the program.")
                    self._collect_message_history(thread_id, user_name_input)
                    break

                self._send_message(thread_id, user_message)
                messages = self._run_assistant(assistant_id, thread_id)
                message_dict = json.loads(messages.model_dump_json())
                most_recent_message = message_dict['data'][0]
                assistant_message = most_recent_message['content'][0]['text']['value']
                print(f"{user_name_input}: {assistant_message}")


if __name__ == "__main__":
    Agent(token='token').create()

