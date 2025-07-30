from collections import OrderedDict
from telebot import types, apihelper
from telebot.types import ReactionTypeEmoji 
from bot import BOT as bot
from aiassistant import ASSISTANT as assistant
import random
from database import db
import time

class Topics:
    topic_prompt = {
        'Articles: a/an, the, zero article': 'Write an exercise on the topic \
            "Articles (a/an, the, zero article)" in English. \
                Write only one sentence. The sentence should be such that \
                    there is only one correct article. Do not write the correct answer.',
    }

    def __init__(self):
        self.topic_func = {
            'Articles: a/an, the, zero article': self.articles_topic_func,
        }

    def get_user_data(self, message=None, call=None):
        if message:
            user_name = message.from_user.first_name
            user_id = message.chat.id
            message_id = message.message_id
        if call:
            user_name = call.from_user.first_name
            user_id = call.message.chat.id
            message_id = call.message.message_id
        return {'user_name': user_name, 'user_id': user_id, 'message_id': message_id}

    def start(self, message, call):
        user_data = self.get_user_data(message=message)

        topics = list(self.topics_prompts.keys())
        keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        items = [types.KeyboardButton(topic) for topic in topics]
        random.shuffle(items)
        keyboard_markup.add(*items)

        msg = bot.send_message(user_data['user_id'], 'Choose topic', reply_markup=keyboard_markup, parse_mode='html')
        self.choose_topic_message = msg.message_id

        self.last_message_id = msg.message_id

        db.update_last_message_id(self.last_message_id, str(user_data['user_id']))

        return
    
    def instructions(self, message):
        user_data = self.get_user_data(message=message)
        self.last_message_id = user_data['message_id']
        db.update_last_message_id(self.last_message_id, str(user_data['user_id']))

        bot.delete_message(user_data['user_id'], user_data['message_id'])

        if message.text in self.topic_prompt:
            bot.delete_message(user_data['user_id'], self.choose_topic_message)

            self.topic = message.text
            self.topic_func[self.topic](user_data)
    
            return
        
        if message.text in self.keyboard_items:
            new_message = assistant.create_message(self.thread_id, message.text)
            run_id = assistant.create_run(self.thread_id)
            response = assistant.get_response(self.thread_id, run_id)
            text = self.exercise_text + '\n\n' + response

            print('--------------> response', response)
            print('--------------> text', text)

            inline_markup = types.InlineKeyboardMarkup(row_width=1)
            item1 = types.InlineKeyboardButton('regenerate', callback_data='regenerate')
            inline_markup.add(item1)

            # bot.delete_message(chat_id=user_data['user_id'], message_id=self.game_window_message)

            # bot.send_message(user_data['user_id'], text, reply_markup=keyboard_markup, parse_mode='html')

            bot.edit_message_text(
                text=text, 
                chat_id=user_data['user_id'], 
                message_id=self.game_window_message,
                reply_markup=inline_markup
            )
    
            return
        
    def articles_topic_func(self, user_data):
        exercise_text = self.generate_text()
        self.exercise_text = exercise_text
        inline_markup = types.InlineKeyboardMarkup(row_width=1)
        item1 = types.InlineKeyboardButton('regenerate', callback_data='regenerate')
        inline_markup.add(item1)

        article_text = "Choose correct article"
        keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        items = ['a', 'an', 'the', 'zero article']
        keyboard_markup.add(*items)

        self.keyboard_items = items

        msg = bot.send_message(user_data['user_id'], exercise_text, reply_markup=inline_markup, parse_mode='html')
        self.game_window_message = msg.message_id
        
        msg = bot.send_message(user_data['user_id'], article_text, reply_markup=keyboard_markup, parse_mode='html')
        
        self.article_message = msg.message_id
        self.last_message_id = msg.message_id
        db.update_last_message_id(self.last_message_id, str(user_data['user_id']))


    def generate_text(self):
        thread_id = assistant.create_thread()
        message = assistant.create_message(thread_id, self.topics_prompts[self.topic])
        run_id = assistant.create_run(thread_id)
        response = assistant.get_response(thread_id, run_id)

        self.thread_id = thread_id
        return response
