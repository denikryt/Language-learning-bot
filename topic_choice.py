from articles_topic import ArticlesTopic
from state import State
from bot import BOT as bot
from database import db
from telebot import types
from context import Context


class TopicChoice(State):
    
    def __init__(self, context: Context):
        self.context = context
        self.switcher = {
                'Articles: a/an, the, zero article': lambda: self.context.transition_to(ArticlesTopic())
            }
        self.topics = ['Articles: a/an, the, zero article']
        
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
    
    def start(self, message=None, call=None):
        user_data = self.get_user_data(message, call)
        
        keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        items = [types.KeyboardButton(topic) for topic in self.topics]
        keyboard_markup.add(*items)
        
        msg = bot.send_message(user_data['user_id'], 'Choose topic', reply_markup=keyboard_markup, parse_mode='html')
        self.choose_topic_message = msg.message_id
        
        self.last_message_id = msg.message_id
        
        db.update_last_message_id(self.last_message_id, str(user_data['user_id']))

    def instructions(self, message):
        user_data = self.get_user_data(message=message)
        self.last_message_id = user_data['message_id']
        db.update_last_message_id(self.last_message_id, str(user_data['user_id']))
        
        if message.text in self.switcher:
            bot.delete_message(user_data['user_id'], self.choose_topic_message)

            self.switcher[message.text]()
            self.context.start(message=message)
        else:
            bot.delete_message(user_data['user_id'], user_data['message_id'])