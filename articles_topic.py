from collections import OrderedDict
from telebot import types, apihelper
from telebot.types import ReactionTypeEmoji 
from bot import BOT as bot
from aiassistant import ASSISTANT as assistant
import random
from database import db
import time
import re

class ArticlesTopic:
    topic_prompt = "Write an exercise on the topic \
    'Articles (a/an, the, zero article)' in English. \
    Options are :'a', 'an', 'the', 'zero article'. \
    Write ten different excersice sentences. Separate sentences with '.' only, do not use numbers. \
    Write exercise sentences only.\ Replace the article with '___'. \
    The sentences should be such that there is only one correct article. \
    Do not write the correct answer. Be creative!"

    check_prompt = "Answer 'Correct!' if the article is correct for the given sentence. Explain why it is correct.\
        'Incorrect!' if the article is incorrect. If the article is incorrect, explain why. \
            Place the words 'Correct!' or 'Incorrect!' with <b>bold</b> tags at the beginning of the message."
    
    chatting_instructions = "Answer specifically and to the point, without unnecessary phrases."
    chat_messages = []
    excercise_count = 0
    answered = False

    def inline_buttons(self, message, call):
        user_data = self.get_user_data(call=call)

        if call.data == 'next':
            self.excercise_count += 1

            if self.excercise_count > len(self.exercise_sentences)-1:

                for message_id in self.chat_messages:
                    bot.delete_message(user_data['user_id'], message_id)
                
                self.start(message, call)
                return
            else:
                self.answered = False
                self.exercise_text = self.exercise_sentences[self.excercise_count]
                
                for message_id in self.chat_messages:
                    bot.delete_message(user_data['user_id'], message_id)
                
                self.chat_messages.clear()

                msg = bot.send_message(
                    text=self.exercise_text, 
                    chat_id=user_data['user_id'], 
                    parse_mode='html'
                )

                self.game_window_message = msg.message_id
                self.chat_messages.append(msg.message_id)

                article_text = "Choose correct article"
                keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                items = ['a', 'an', 'the', 'zero article']
                keyboard_markup.add(*items)
                msg = bot.send_message(user_data['user_id'], article_text, reply_markup=keyboard_markup, parse_mode='html')

                self.article_message = msg.message_id
                self.last_message_id = msg.message_id
                db.update_last_message_id(self.last_message_id, str(user_data['user_id']))
                return

        if call.data == 'regenerate':

            for message_id in self.chat_messages:
                bot.delete_message(user_data['user_id'], message_id)

            self.start(message, call)
            return
        
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
        self.answered = False
        self.chat_messages = []
        self.exercise_sentences= [] 
        self.excercise_count = 0

        user_data = self.get_user_data(message, call)

        thread_id = assistant.create_thread()
        message = assistant.create_message(thread_id, self.topic_prompt)
        run_id = assistant.create_run(thread_id)
        response = assistant.get_response(thread_id, run_id)

        self.exercises_thread = thread_id
        self.exercise_sentences = [sentence.strip() for sentence in re.split(r'[.!?]', response) if sentence.strip()]
        self.exercise_text = self.exercise_sentences[self.excercise_count]
        
        inline_markup = types.InlineKeyboardMarkup(row_width=2)
        item1 = types.InlineKeyboardButton('next', callback_data='next')
        item2 = types.InlineKeyboardButton('regenerate', callback_data='regenerate')
        inline_markup.add(item1,item2)

        article_text = "Choose correct article"
        keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        items = ['a', 'an', 'the', 'zero article']
        keyboard_markup.add(*items)

        self.keyboard_items = items

        msg = bot.send_message(user_data['user_id'], self.exercise_text, reply_markup=inline_markup, parse_mode='html')
        self.game_window_message = msg.message_id
        self.chat_messages.append(msg.message_id)
        
        msg = bot.send_message(user_data['user_id'], article_text, reply_markup=keyboard_markup, parse_mode='html')
        
        self.article_message = msg.message_id
        self.last_message_id = msg.message_id
        db.update_last_message_id(self.last_message_id, str(user_data['user_id']))

    def instructions(self, message):
        user_data = self.get_user_data(message=message)
        self.last_message_id = user_data['message_id']
        db.update_last_message_id(self.last_message_id, str(user_data['user_id']))

        if message.text in self.keyboard_items and self.answered == False:
            self.answered = True
            bot.delete_message(user_data['user_id'], user_data['message_id'])
            bot.delete_message(user_data['user_id'], self.article_message)

            text_with_article = self.insert_article(message.text, self.exercise_text)
            inline_markup = types.InlineKeyboardMarkup(row_width=2)
            item1 = types.InlineKeyboardButton('next exercise', callback_data='next')
            item2 = types.InlineKeyboardButton('regenerate', callback_data='regenerate')
            inline_markup.add(item1,item2)

            bot.edit_message_text(
                text=text_with_article, 
                chat_id=user_data['user_id'], 
                message_id=self.game_window_message,
                reply_markup=inline_markup,
                parse_mode='html'
            )

            message_text = f"Is the article '{message.text}' correct for this sentence?\n{self.exercise_text}"
            
            thread_id = assistant.create_thread()
            new_message = assistant.create_message(thread_id, message_text)
            run_id = assistant.create_run(thread_id=thread_id, instructions=self.check_prompt)
            response = assistant.get_response(thread_id, run_id)
            self.chat_thread = thread_id
            
            msg = bot.send_message(user_data['user_id'], response, parse_mode='html')

            self.chat_messages.append(msg.message_id)
            self.last_message_id = msg.message_id
            db.update_last_message_id(self.last_message_id, str(user_data['user_id']))
            return
        else:
            self.chat_messages.append(user_data['message_id'])

            new_message = assistant.create_message(self.chat_thread, message.text)
            run_id = assistant.create_run(thread_id=self.chat_thread, instructions=self.chatting_instructions)
            response = assistant.get_response(self.chat_thread, run_id)

            msg = bot.send_message(user_data['user_id'], response, parse_mode='html')

            self.chat_messages.append(msg.message_id)
            self.last_message_id = msg.message_id
            db.update_last_message_id(self.last_message_id, str(user_data['user_id']))
            return

    def generate_text(self):
        thread_id = assistant.create_thread()
        message = assistant.create_message(thread_id, self.topic_prompt)
        run_id = assistant.create_run(thread_id)
        response = assistant.get_response(thread_id, run_id)

        self.thread_id = thread_id
        return response

    def insert_article(self, article, text):
        "Replace ___ with underlined article"
        article = f'<u>{article}</u>'
        text = text.replace('___', article)
        return text