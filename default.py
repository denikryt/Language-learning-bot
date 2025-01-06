from telebot import types
from bot import BOT as bot
from state import State

class Default(State):
    """
    Description
    """

    def data_base(self, message, call):
        pass

    def inline_buttons(self, message=None, call=None):
        if call.data == 'continue':
            self.context.transition_to(LoadText())
            self.context.sents_to_words(message, call, None)
            # self.sent_to_words(call.message)
        if call.data == 'new':
            self.context.transition_to(LoadText())
            self.context.hello(message, call)
        if call.data == 'learn':
            self.context.transition_to(Learn())
            self.context.hello(message, call)

        if call.data == 'main_menu':

            items = ['Загрузим текст', 'Поучим слова', 'Записать слова']

            markup = types.ReplyKeyboardMarkup(resize_keyboard=False)
            items = [types.KeyboardButton(item) for item in items]
            markup.add(*items)
            bot.send_message(call.from_user.id, 'Что будем делать?', reply_markup=markup)

        if call.data == 'build':
            # call.message.text = Sentences.text
            # print(call.message.message_id)
            # self.context.transition_to(Sentences())
            # text = self.context.inline_buttons(None, call)
            self.context.transition_to(Text())
            self.context.text_to_sents(message, call)
        
        if call.data == 'next':
            return
            self.context.transition_to(Sentences())
            self.context.inline_buttons(message, call)

        if call.data == 'delete':
            self.context.transition_to(Text())
            self.context.inline_buttons(message, call)

    def printing(self, message, call):
        pass

    def sentence_buttons(self, message=None, call=None):
        pass

    def menu(self, message, call):
        pass

    def vars(self, message, sents, count):
        pass

    def hello(self, message=None, call=None) -> None:
        user_name = message.from_user.first_name
        user_id = message.chat.id
        folder_name = user_name + '(' + str(user_id) + ')'

        c = open(folder_name+'\\count.txt','r').readlines()
        print(c)
        if int(c[0]) > 0:
        # if len(c) > 0:
        
            markup = types.InlineKeyboardMarkup(row_width=3)
            item1 = types.InlineKeyboardButton('Продолжить', callback_data='continue')
            item2 = types.InlineKeyboardButton('Новый текст', callback_data='new')
            markup.add(item1, item2)

            bot.send_message(message.chat.id, 'Что?', reply_markup=markup)
            # LAST_MESSAGE += 1
        else:
            self.context.transition_to(LoadText())
            # bot.send_message(message.chat.id, 'Пришли мне текст!')
            self.context.hello(message, None)

        # print('Куда?')
        # print("'text'")
        # print("'learn'")
        # print("'game'")

    def text_to_sents(self, user):
        pass

    def sent_to_words(self, message, sents):
        pass

    def write_word(self, message):
        pass

    def start(self, message, call):
        pass

    def random_words(self):
        pass

    def words_buttons(self, call):
        pass
         
    def instructions(self, message=None, call=None) -> None:
        return
        if message.text == 'Загрузить предложения':
            self.context.transition_to(Text())
            self.context.hello(message, None)
            return

        if message.text in self.lang:
            Text.lang = self.lang[message.text]

            items = ['Работать с текстом', 'Загрузить предложения']
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            items = [types.KeyboardButton(item) for item in items]
            markup.add(*items)
            bot.send_message(message.chat.id, 'Что будем делать?', reply_markup=markup)
            return

        if message.text == 'Тестики':
            self.context.transition_to(Learn())
            self.context.reset()
            self.context.hello(message, None)
            return

        if message.text == '/wiki':
            self.context.transition_to(Wiki())
            self.context.hello(message, call)
            return


        if message.text == 'Поучим слова':
            self.context.transition_to(Learn())
            self.context.hello(message, None)
            return
        
        if message.text == 'Загрузим предложение':
            self.context.transition_to(Words())
            self.context.hello(message, None)
            return
            
        if message.text == 'game':
            self.context.transition_to(Game())
            self.context.hello(message, None)
            return

        # else:
        #     bot.send_message(message.chat.id, 'Что?')