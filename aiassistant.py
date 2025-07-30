from dotenv import load_dotenv
import os
import openai
import time

load_dotenv()

class Assistant:
    def __init__(self):
        self.id = os.getenv('ASSISTANT_ID')
        self.client = openai.Client(api_key=os.getenv('OPENAI_API_KEY'))

    def get_definition(self, text, instructions=None):
        thread_id = self.create_thread()
        message = self.create_message(thread_id, text)
        run_id = self.create_run(thread_id, instructions=instructions)
        result = self.get_response(thread_id=thread_id, run_id=run_id) 
        return result
    
    def get_response(self, thread_id, run_id, sleep_time=5):
        while True:
            try:
                run = self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
                if run.completed_at:
                    messages = self.client.beta.threads.messages.list(thread_id=thread_id)
                    last_message = messages.data[0]
                    response = last_message.content[0].text.value
                    return response
            except Exception as e:
                print(e)
                return False

            time.sleep(sleep_time)

    def create_thread(self):
        thread = self.client.beta.threads.create(
            messages=[]
        )
        return thread.id
    
    def create_message(self, thread_id, content):
        message = self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=content
        )
        return message
    
    def create_run(self, thread_id, instructions=''):
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.id,
            instructions=instructions
        )
        return run.id


ASSISTANT = Assistant()