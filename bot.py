from telebot import TeleBot
from dotenv import load_dotenv
import os
import openai
import time

load_dotenv()
BOT = TeleBot(os.getenv('BOT_TOKEN'), threaded=False)

class Assistant:
    def __init__(self):
        self.id = os.getenv('ASSISTANT_ID')
        self.client = openai.Client(api_key=os.getenv('OPENAI_API_KEY'))
        self.definition_instructions = "Provide an explanation and definition of the word only. Give an aswer in a simple format, without any additional information or formatting. Do not write the word itself in the answer."

    def get_definition(self, word, example):
        thread = self.client.beta.threads.create(
            messages=[]
        )
        thread_id = thread.id

        messaage = f"Word: {word}, sentence: {example}"
        messaage = self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=messaage
        )

        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.id,
            instructions=self.definition_instructions,
        )

        run_id = run.id

        result = self.get_response(thread_id=thread_id, run_id=run_id) 
        return result
    
    def get_response(self, thread_id, run_id, sleep_time=5):
        while True:
            try:
                run = self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
                if run.completed_at:
                    messaages = self.client.beta.threads.messages.list(thread_id=thread_id)
                    last_message = messaages.data[0]
                    response = last_message.content[0].text.value
                    return response
            except Exception as e:
                print(e)
                return False

            time.sleep(sleep_time)

ASSISTANT = Assistant()