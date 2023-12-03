# AI_assistant

 # Simple agent with openai

OpenAI assistants are a way to interact with an LLM with persistent session data. 
This means that if you call a pre-defined thread of messages and an assistant ID,
the assistant will "remember" your messages and its replies.
Assistants have "threads" which allow them to store and access message history. 
An assistant and a thread can be "run" together, 
which instructs the AI to work with a specific set of messages. 


Now that we have created our assistant, thread, and message functions, 
we need a way to store our sessions. 
The solution:
I was creating a JSON file stored in the working directory that stores your 
sessions and assistant IDs. 
This makes it easy to choose which assistant you want to talk to;
you can also name them to help you remember who is who.


When you want to chat with one of your assistants, 
run the script, and you’ll be asked to choose an existing session from the 
set that is printed to the console or to make a new assistant.
Here is the function that saves your assistant’s data locally:
```commandline
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
   ```


each time that you are chatting with the AI, and say “exit”, this function is 
automatically called to scrape your messages from the cloud and save them into 
a text file:
```commandline

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
```

We can put all of the puzzle pieces together. The create lets you 
choose your session from your stored JSON file, 
or you can opt to create a new session.
To start, simply run the code and follow the instructions. 
To properly end a session, type “exit”

output
```commandline
Type 'new' to make a new assistant session. Press 'Enter' to choose an existing assistant session: new

Please type a name for this chat: omadeus
Created Session with omadeus, Assistant ID: asst_UkeZ7Lu8NuIIGoBBCYFev3yZ and Thread ID: thread_8BXqhSzJD9QK4CAyaw0cuJd1
Please type your question: what is your name?
omadeus: Hey there! My name is Omadeus. What's on your mind today?
Please type your question: how are you?
omadeus: I'm doing well, thanks for asking! How about you?

```

output2:

```commandline
Type 'new' to make a new assistant session. Press 'Enter' to choose an existing assistant session: 
Available Sessions:
Session 1: omadeus
Enter the session number to load: 1
Created Session with omadeus, Assistant ID: asst_UkeZ7Lu8NuIIGoBBCYFev3yZ and Thread ID: thread_8BXqhSzJD9QK4CAyaw0cuJd1
Please type your question: whats your name
omadeus: Hey, I'm still Omadeus. What's up? Time for a new topic, or are you still feeling bored?

```