from __future__ import annotations
from telebot import types
from telebot.types import ReactionTypeEmoji
from bot import BOT as bot
import traceback
import context
import default
import learn
import os
import database
import text
import nltk
from dotenv import load_dotenv
import os

load_dotenv()
MY_ID = os.getenv('MY_ID')
MY_CHANNEL_ID = os.getenv('MY_CHANNEL_ID')

nltk.download('punkt')
db = database.Database()

@bot.channel_post_handler() 
def channel_handler(message):
    channel_data = get_user_data(channel=message)

    if str(channel_data['user_id']) != str(MY_CHANNEL_ID):
        return
    
    user_collection = db.get_collection_name_by_channel_id(str(channel_data['user_id']))
    print(user_collection)
    print(type(user_collection))
    db.save_text(message.text, user_collection)

    bot.set_message_reaction(channel_data['user_id'], channel_data['message_id'], [ReactionTypeEmoji('👍')], is_big=False)

@bot.message_handler(commands=['start'])
def welcome(message):
    user_data = get_user_data(message=message)

    if user_data['user_id'] != int(MY_ID):
        return
    
    text = '/texts - work with texts\n/learn - learn words'
    bot.send_message(user_data['user_id'], text)

    db.set_collection(str(user_data['user_id']))
    db.update_last_message_id(user_data['message_id']+1) 
    return

@bot.message_handler(commands=['learn'])
def welcome(message):
    context.transition_to(learn.Learn())
    context.hello(message=message)

@bot.message_handler(commands=['texts'])
def welcome(message):
    context.transition_to(text.Text())
    context.start(message=message)

@bot.message_handler(content_types=['text'])
def lalala(message):
    user_data = get_user_data(message=message)

    if user_data['user_id'] != int(MY_ID):
        return
    
    context.instructions(message)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    context.inline_buttons(call=call)

def get_user_data(message=None, call=None, channel=None):
    if message:
        user_name = message.from_user.first_name
        user_id = message.chat.id
        message_id = message.message_id
    if call:
        user_name = call.from_user.first_name
        user_id = call.from_user.id
        message_id = call.message.message_id
    if channel:
        user_name = channel.chat.title
        user_id = channel.chat.id
        message_id = channel.message_id

    return {
        'user_name': user_name, 
        'user_id': user_id,
        'message_id': message_id
    }

bot.send_message(MY_ID, 'helo')

if __name__ == "__main__":
    """Client code"""

    context = context.Context(default.Default())
    bot.remove_webhook()
    bot.polling(none_stop=True)




