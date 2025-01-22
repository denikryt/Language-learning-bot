from collections import OrderedDict
from telebot import types, apihelper
from bot import BOT as bot
import random
from database import db

class Learn():
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

    guessing = False
    test = False

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


    def printing(self, chat_id=None):
        pass

    def menu(self,chat_id=None):
        pass

    def vars(self, message, sents, count):
        pass

    def reset(self):
        self.test = False
        self.testing = False
        self.guessed = []

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

        self.translate = db.get_translations(self.random_word, str(user_data['user_id']))
        self.translate = ', '.join(self.translate)

        self.mark = db.get_word_level(self.random_word, str(user_data['user_id']))

        self.start(message=message, call=call)

    def select_word(self, user_id):
        level_list = db.get_levels(user_id)
        weights = [100 - value / len(level_list) for value in level_list]

        return random.choices(self.words, weights=tuple(weights), k=1)[0]

    def text_to_sents(self, user):
        pass

    def sents_to_words(self, message, sents):
        pass

    def write_word(self, message):
        pass

    def buttons(self, message):
        pass

    def name_id(self, message, call, get=None):
        if message:
            user_name = message.from_user.first_name
            user_id = message.chat.id
            message_id = message.message_id
        if call :
            user_name = call.from_user.first_name
            user_id = call.from_user.id
            message_id = call.message.message_id
        if get == 'message_id':
            return message_id
        return user_name, user_id

    def random_words(self, message, call):
        pass

    def start(self, message=None, call=None):
        self.loose = False
        self.attempts = 3
        self.help = 3
        self.char = 0
        self.spelling = ''
        self.chars = []
        self.chars = [char.lower() for char in self.random_word]
        self.stars = []
        self.stars = ['*' if not x == ' ' else ' ' for x in self.random_word]

        self.spelling = ''.join(self.stars)
        self.send_start_message(message, call)
        
    def send_win_message(self, message=None, call=None):
        user_data = self.get_user_data(message, call)

        newWord = types.InlineKeyboardButton('new word', callback_data='new')
        finish = types.InlineKeyboardButton('finish', callback_data='finish')

        text = f'Correct!\n<b>{self.translate}</b>\nmeans\n<b>{self.random_word}</b>'
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(newWord, finish)

        bot.delete_message(user_data['user_id'],message_id=self.keyboard_message)
        bot.edit_message_text(chat_id=user_data['user_id'], message_id=self.game_window, text=text, reply_markup=markup, parse_mode='html')

    def send_start_message(self, message=None, call=None):
        user_data = self.get_user_data(message, call)

        inline_markup = types.InlineKeyboardMarkup(row_width=2)
        item1 = types.InlineKeyboardButton('help', callback_data='help')
        item2 = types.InlineKeyboardButton('give up', callback_data='give_up')
        inline_markup.add(item1, item2)

        keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        items = [types.KeyboardButton(item) for item in self.random_word]
        random.shuffle(items)
        keyboard_markup.add(*items)
        
        text = f'Translate the word\n<b>{self.translate}</b>\n{self.spelling}\nAttempts: {str(self.attempts)}\nHints: {str(self.help)}'

        msg = bot.send_message(user_data['user_id'], text, reply_markup=inline_markup, parse_mode='html')
        self.game_window = msg.message_id

        msg = bot.send_message(user_data['user_id'], 'Choose the letter', reply_markup=keyboard_markup, parse_mode='html')
        self.keyboard_message = msg.message_id

        self.last_message_id = msg.message_id

    def send_correct_message(self, message=None, call=None):
        user_data = self.get_user_data(message, call)
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        item1 = types.InlineKeyboardButton('help', callback_data='help')
        item2 = types.InlineKeyboardButton('give up', callback_data='give_up')
        markup.add(item1,item2)

        text = f'Translate the word\n<b>{self.translate}</b>\n{self.spelling}\nAttempts: {str(self.attempts)}\nHints: {str(self.help)}'

        bot.edit_message_text(chat_id=user_data['user_id'], message_id=self.game_window, text=text, reply_markup=markup, parse_mode='html')
    
    def send_incorrect_message(self, message=None, call=None):
        user_data = self.get_user_data(message, call)
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        item1 = types.InlineKeyboardButton('help', callback_data='help')
        item2 = types.InlineKeyboardButton('give up', callback_data='give_up')
        markup.add(item1,item2)

        text = f'Translate the word\n<b>{self.translate}</b>\n{self.spelling}\nAttempts: {str(self.attempts)}\nHints: {str(self.help)}'

        bot.edit_message_text(chat_id=user_data['user_id'], message_id=self.game_window, text=text, reply_markup=markup, parse_mode='html')

    def send_loose_message(self, message=None, call=None):
        user_data = self.get_user_data(message, call)

        markup = types.InlineKeyboardMarkup(row_width=1)
        item3 = types.InlineKeyboardButton('new word', callback_data='new')
        item5 = types.InlineKeyboardButton('finish', callback_data='finish')
        markup.add(item3, item5)

        text = f'You loose!\n<b>{self.translate}</b>\nmeans\n<b>{self.random_word}</b>'

        bot.delete_message(user_data['user_id'],message_id=self.keyboard_message)
        bot.edit_message_text(chat_id=user_data['user_id'], message_id=self.game_window, text=text, reply_markup=markup, parse_mode='html')

    def send_finish_message(self, message=None, call=None):
        user_data = self.get_user_data(message, call)

        markup = types.InlineKeyboardMarkup(row_width=1)
        item3 = types.InlineKeyboardButton('new word', callback_data='new')
        markup.add(item3)

        text = f'Well done!\nYour results:\n'
        for x in self.guessed:
            text += x + '\n'
        
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

            new_mark = self.attempts + self.help
            db.update_word_level(word=self.random_word, collection_name=str(user_data['user_id']), level=new_mark + self.mark)

            self.guessed.append(f"<b>{self.random_word}</b> : {str(self.mark)} +{str(new_mark)}")
            self.send_win_message(message, call)
            return

        if text == char:
            self.stars[self.char] = char
            self.spelling = ''.join(self.stars)
            self.char += 1

            if self.spelling == word:
                self.testing = False

                new_mark = self.attempts + self.help
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
                
    def send_message(self, message=None, call=None, case=None, message_id=None, user_id=None):
        
        cases = ['correct', 'incorrect', 'help'] 
        result = ['win', 'fast_win', 'loose', 'give_up'] 

        markup = types.InlineKeyboardMarkup(row_width=2)

        item1 = types.InlineKeyboardButton('Подсказка', callback_data='help')
        item2 = types.InlineKeyboardButton('Сдаюсь', callback_data='give_up')
        item3 = types.InlineKeyboardButton('Новое слово', callback_data='new')
        item4 = types.InlineKeyboardButton('Отгадать', callback_data='guess')
        item5 = types.InlineKeyboardButton('Закончить', callback_data='finish')

        if case == 'empty db':
            return

        if case == 'new word':
            text = f'Переведи слово\n<b>{self.translate}</b>'
            markup.add(item2,item4)
            bot.send_message(user_id, text, reply_markup=markup, parse_mode='html')
        else:
            user_name, user_id = self.name_id(message, call)
            text = f'Переведи слово\n<b>{self.translate}</b>\n{self.spelling}\nПопыток: {str(self.attempts)}\nПодсказок: {str(self.help)}'
            markup.add(item1,item2)

            markup2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
            items = [types.KeyboardButton(item) for item in self.random_word]
            random.shuffle(items)
            markup2.add(*items)

            if case == 'send':
                msg = bot.send_message(user_id, text, reply_markup=markup, parse_mode='html')
                self.game_window = msg.message_id

                msg = bot.send_message(user_id, 'Выбери букву', reply_markup=markup2, parse_mode='html')
                self.keyboard_message = msg.message_id

                self.last_message = msg.message_id
                
                return

            if case in cases:
                bot.edit_message_text(chat_id=user_id, message_id=self.game_window, text=text, reply_markup=markup, parse_mode='html')

            if case == 'delete':
                bot.delete_message(chat_id=user_id, message_id=message_id)
                return

            if case in result:
                if case == 'give_up':
                    mark = 0
                else:
                    mark = self.attempts + self.help
                self.guessed.append(f"{self.translate} - {self.random_word} : {str(self.mark)} +{str(mark)}")    

            if case == 'win':

                text = f'Правильно!\n<b>{self.translate}</b>\nозначает\n<b>{self.random_word}</b>'
                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(item3, item5)

                db, sql = self.data_base(user_name, user_id)

                new_level = self.mark+ self.attempts + self.help
                sql.execute(f"UPDATE english SET level = {new_level} WHERE word = '{self.random_word}'")
                db.commit()

                bot.delete_message(user_id,message_id=self.keyboard_message)
                bot.edit_message_text(chat_id=user_id, message_id=self.game_window, text=text, reply_markup=markup, parse_mode='html')

            if case == 'fast_win':

                text = f'СУПЕР!\n<b>{self.translate}</b>\nозначает\n<b>{self.random_word}</b>'
                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(item3, item5)

                db, sql = self.data_base(user_name, user_id)

                new_level = self.mark+ self.attempts + self.help
                sql.execute(f"UPDATE english SET level = {new_level} WHERE word = '{self.random_word}'")
                db.commit()

                bot.delete_message(user_id,message_id=self.keyboard_message)
                bot.edit_message_text(chat_id=user_id, message_id=self.game_window, text=text, reply_markup=markup, parse_mode='html')

            if case == 'loose' or case == 'give_up':

                text = f'Проиграл!\n<b>{self.translate}</b>\noзначает\n<b>{self.random_word}</b>'
                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(item3, item5)

                # if self.guessing:
                #     self.guessing = False
                bot.delete_message(user_id,message_id=self.keyboard_message)
                
                bot.edit_message_text(chat_id=user_id, message_id=self.game_window, text=text, reply_markup=markup, parse_mode='html')

            if case == 'finish':

                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(item3)

                text = f'Молодец!\nТвой результат:\n'
                for x in self.guessed:
                    text += x + '\n'
                
                bot.edit_message_text(chat_id=user_id, message_id=self.game_window, text=text, reply_markup=markup, parse_mode='html')


        # return
    