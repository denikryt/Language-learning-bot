from collections import OrderedDict
from telebot import types, apihelper
from telebot.types import ReactionTypeEmoji 
from bot import BOT as bot
from aiassistant import ASSISTANT as assistant
import random
from database import db
import time

class Game():
    """
    Description
    """
    vocab = {}
    sents = {}

    temp_choise_list = []
    words = []
    trans = []
    repeat = []
    rand_answers = []

    rand_tran1 = ''
    rand_choice = ''
    random_word = ''

    test_window = 0
    result_window = 0
    translation_mark = 5
    shuffle_mark = 10

    guessing = False
    test = False
    help_add_translation = False
    help_shuffle_letters = False

    definition_instructions = "Provide an explanation and definition of the word only.\
        Give an aswer in a simple format, without any additional information or formatting. \
        Do not write the word itself in the answer."
    

    def inline_buttons(self, message=None, call=None):
        user_data = self.get_user_data(message, call)

        self.game_window = call.message.message_id

        if call.data == 'new':
            bot.delete_message(user_data['user_id'], message_id=user_data['message_id'])
            self.hello(message, call)
            return

        if call.data == 'help':
            if self.chars[self.char] == ' ':
                self.char += 1

            if self.help > 0:
                self.help -= 1

                self.stars[self.char] = self.chars[self.char]
                self.spelling = ''.join(self.stars)

                if self.spelling == self.random_word.lower():
                    mark = 0
                    self.guessed.append(f"<b>{self.random_word}</b> : {str(self.mark)} +{str(mark)}")
                
                    self.send_loose_message(message, call)
                    return

                self.char += 1

                self.send_correct_message(message, call)
            else:
                return

        if call.data == 'give_up':
            self.testing = False
            mark = 0
            self.guessed.append(f"<b>{self.random_word}</b> : {str(self.mark)} +{str(mark)}")  
            self.send_loose_message(message, call)

        if call.data == 'finish':
            self.test = False
            self.testing = False

            self.send_finish_message(message, call)

        if call.data == 'shuffle':
            self.help_shuffle_letters = True
            self.shuffle_mark = 0
            bot.edit_message_reply_markup(chat_id=user_data['user_id'], message_id=user_data['message_id'], reply_markup=self.inline_game_buttons())
            self.send_letters_message(message, call)

        if call.data == 'add_translation':
            self.help_add_translation = True
            self.translation_mark = 0
            self.send_correct_message(message, call)
            
        if call.data == 'save_text':
            db.save_text(text=self.definition, collection_name=str(user_data['user_id']))
            bot.set_message_reaction(user_data['user_id'], self.game_window, [ReactionTypeEmoji('👍')], is_big=False)

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

    def hello(self, message=None, call=None, case=None, user_name=None, user_id=None):
        user_data = self.get_user_data(message, call)

        result = db.get_words(str(user_data['user_id']))

        if result == []:
            bot.send_message(user_data['user_id'], 'No words found')
            return

        if not self.test:
            self.guessed = []

        self.test = True
        self.testing = True
        self.words = result

        self.random_word = self.select_word(str(user_data['user_id']))
        self.word_examples = db.get_examples_by_word(self.random_word, str(user_data['user_id']))
        self.random_word_example = random.choice(self.word_examples)

        text = f"Word: {self.random_word}, sentence: {self.random_word_example}"
        self.definition = assistant.get_definition(text=text, instructions=self.definition_instructions)

        self.translate = db.get_translations(self.random_word, str(user_data['user_id']))
        self.translate = ', '.join(self.translate)

        self.mark = db.get_word_level(self.random_word, str(user_data['user_id']))

        self.start(message=message, call=call)

    def select_word(self, user_id):
        level_list = db.get_levels(user_id)
        weights = [100 - value / len(level_list) for value in level_list]

        return random.choices(self.words, weights=tuple(weights), k=1)[0]

    def start(self, message=None, call=None):
        self.loose = False
        self.help_add_translation = False
        self.help_shuffle_letters = False
        self.translation_mark = 5
        self.shuffle_mark = 10
        self.attempts = 3
        self.help = 3
        self.char = 0
        self.spelling = ''
        self.chars = []
        self.chars = [char.lower() for char in self.random_word]
        self.keyboard_chars = self.chars.copy()
        self.keyboard_chars = [char for char in self.keyboard_chars if char != ' ']
        self.stars = []
        self.stars = ['*' if not x == ' ' else ' ' for x in self.random_word]

        self.spelling = ''.join(self.stars)
        self.send_start_message(message, call)

    def game_text(self):
        if self.help_add_translation:
            text = f'Guess the word\n<b>{self.definition}</b>\nTranslation: <b>{self.translate}</b>\n{self.spelling}\nAttempts: {str(self.attempts)}\nHints: {str(self.help)}'
        else:
            text = f'Guess the word\n<b>{self.definition}</b>\n{self.spelling}\nAttempts: {str(self.attempts)}\nHints: {str(self.help)}'
        return text
    
    def loose_text(self):
        text = f'You loose!\n<b>{self.definition}</b>\ndescribes the word\n<b>{self.random_word}</b>\nTranslation: <b>{self.translate}</b>\nExample:\n<b>{self.random_word_example}</b>'
        return text
    
    def win_text(self):
        text = f'Correct!\n<b>{self.definition}</b>\ndescribes the word\n<b>{self.random_word}</b>\nTranslation: <b>{self.translate}</b>\nExample:\n<b>{self.random_word_example}</b>'
        return text
    
    def finish_text(self):
        text = f'Well done!\nYour results:\n'
        for x in self.guessed:
            text += x + '\n'
        return text
        
    def inline_game_buttons(self):
        inline_markup = types.InlineKeyboardMarkup(row_width=2)
        item1 = types.InlineKeyboardButton('help', callback_data='help')
        item2 = types.InlineKeyboardButton('give up', callback_data='give_up')
        item3 = types.InlineKeyboardButton('translation', callback_data='add_translation')
        item4 = types.InlineKeyboardButton('save as text', callback_data='save_text')
        item5 = types.InlineKeyboardButton('shuffle letters', callback_data='shuffle')
        
        if self.help_shuffle_letters:
            inline_markup.add(item1, item2, item3, item4)
        else:
            inline_markup.add(item1, item2, item3, item4, item5)

        return inline_markup
    
    def inline_end_buttons(self):
        inline_markup = types.InlineKeyboardMarkup(row_width=1)
        item1 = types.InlineKeyboardButton('new word', callback_data='new')
        item2 = types.InlineKeyboardButton('finish', callback_data='finish')
        inline_markup.add(item1, item2)
        return inline_markup

    def send_letters_message(self, message=None, call=None):
        user_data = self.get_user_data(message, call)

        keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        items = [types.KeyboardButton(item) for item in self.keyboard_chars]
        random.shuffle(items)
        keyboard_markup.add(*items)

        msg = bot.send_message(user_data['user_id'], 'Choose the letter', reply_markup=keyboard_markup, parse_mode='html')
        self.letters_message = msg.message_id
        self.last_message_id = msg.message_id

    def send_start_message(self, message=None, call=None):
        user_data = self.get_user_data(message, call)

        inline_markup = self.inline_game_buttons()
                
        text = self.game_text()
        msg = bot.send_message(user_data['user_id'], text, reply_markup=inline_markup, parse_mode='html')
        self.game_window = msg.message_id

        self.last_message_id = msg.message_id

        bot.edit_message_reply_markup

    def send_win_message(self, message=None, call=None):
        user_data = self.get_user_data(message, call)

        inline_markup = self.inline_end_buttons()
        text = self.win_text()

        if self.help_shuffle_letters:
            bot.delete_message(user_data['user_id'],message_id=self.letters_message)
        
        bot.edit_message_text(chat_id=user_data['user_id'], message_id=self.game_window, text=text, reply_markup=inline_markup, parse_mode='html')

    def send_correct_message(self, message=None, call=None):
        user_data = self.get_user_data(message, call)
        
        inline_markup = self.inline_game_buttons()
        text = self.game_text()

        if self.help_shuffle_letters:
            bot.delete_message(chat_id=user_data['user_id'], message_id=self.letters_message)
            self.send_letters_message(message, call)

        bot.edit_message_text(chat_id=user_data['user_id'], message_id=self.game_window, text=text, reply_markup=inline_markup, parse_mode='html')

    def send_incorrect_message(self, message=None, call=None):
        user_data = self.get_user_data(message, call)
        
        inline_markup = self.inline_game_buttons()
        text = self.game_text()

        bot.edit_message_text(chat_id=user_data['user_id'], message_id=self.game_window, text=text, reply_markup=inline_markup, parse_mode='html')

    def send_loose_message(self, message=None, call=None):
        user_data = self.get_user_data(message, call)

        inline_markup = self.inline_end_buttons()
        text = self.loose_text()

        if self.help_shuffle_letters:
            bot.delete_message(user_data['user_id'],message_id=self.letters_message)
        
        bot.edit_message_text(chat_id=user_data['user_id'], message_id=self.game_window, text=text, reply_markup=inline_markup, parse_mode='html')

    def send_finish_message(self, message=None, call=None):
        user_data = self.get_user_data(message, call)

        markup = types.InlineKeyboardMarkup(row_width=1)
        item1 = types.InlineKeyboardButton('new word', callback_data='new')
        markup.add(item1)

        text = self.finish_text()
        
        bot.edit_message_text(chat_id=user_data['user_id'], message_id=self.game_window, text=text, reply_markup=markup, parse_mode='html')

    def instructions(self, message=None, call=None):
        user_data = self.get_user_data(message, call)

        self.last_message = message.message_id
        bot.delete_message(user_data['user_id'], message_id=self.last_message)

        if not self.testing:
            return

        text = message.text.strip().lower()
        word = self.random_word.lower()
        char = self.chars[self.char]

        if char == ' ':
            self.char += 1
            char = self.chars[self.char]

        if text == word:
            self.testing = False
            self.spelling = word

            new_mark = self.attempts + self.help + self.translation_mark + self.shuffle_mark
            db.update_word_level(word=self.random_word, collection_name=str(user_data['user_id']), level=new_mark + self.mark)

            self.guessed.append(f"<b>{self.random_word}</b> : {str(self.mark)} +{str(new_mark)}")
            self.send_win_message(message, call)
            return

        if text == char:
            self.stars[self.char] = char
            self.spelling = ''.join(self.stars)
            self.char += 1
            self.keyboard_chars.remove(char)

            if self.spelling == word:
                self.testing = False

                new_mark = self.attempts + self.help + self.translation_mark + self.shuffle_mark
                db.update_word_level(word=self.random_word, collection_name=str(user_data['user_id']), level=new_mark + self.mark)

                self.guessed.append(f"<b>{self.random_word}</b> : {str(self.mark)} +{str(new_mark)}")
                self.send_win_message(message, call)
            else:
                self.send_correct_message(message, call)
            return

        if not text == char:
            self.attempts -= 1
            if self.attempts > 0:
                self.send_incorrect_message(message, call)
            else:
                self.testing = False
                self.help = 0 
                mark = 0
                self.guessed.append(f"<b>{self.random_word}</b> : {str(self.mark)} +{str(mark)}")
                self.send_loose_message(message,call)
            return
            