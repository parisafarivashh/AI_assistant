import json
import time

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
            tools=[{"type": "code_interpreter"}]
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
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )

            if run.status == "completed":
                time.sleep(1)
                messages = self.client.beta.threads.messages.list(
                    thread_id=thread_id
                )
                return messages

    def create(self):
        user_name_input = input("Please type a name for this chat: ")
        IDS = self._setup_assistant(assistant_name=user_name_input)

        assistant_id = IDS[0]
        thread_id = IDS[1]

        if assistant_id and thread_id:
            print(
                f"Created Session with {user_name_input}, "
                f"Assistant ID: {assistant_id} and Thread ID: {thread_id}"
            )
            while True:
                user_message = input("Please type your question: ")

                self._send_message(thread_id, user_message)
                messages = self._run_assistant(assistant_id, thread_id)
                message_dict = json.loads(messages.model_dump_json())
                most_recent_message = message_dict['data'][0]
                assistant_message = most_recent_message['content'][0]['text']['value']
                print(f"{user_name_input}: {assistant_message}")


if __name__ == "__main__":
    Agent(token='token').create()

