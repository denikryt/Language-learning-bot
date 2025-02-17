from deep_translator import GoogleTranslator
from lingua import Language, LanguageDetectorBuilder
from telebot import types
from state import State
from bot import BOT as bot
from database import db
import re
import emoji

class Text(State):
    """
    Description
    """

    # sent_count = 0
    text_count = 0
    # output_messages = 0
    # input_messages = 0
    # index_word = 0
    # last_message_id = 0
    # messages_while_changing = 0

    # text_window = 0
    # trans_window = 0
    # question_window = 0

    # word = ''
    # word_to_write = ''
    # user_past = ''
    # sent = ''
    # translated_word = ''
    # translated_sent = ''
    # temp_word = ''
    # lang = 'en'
    # text = ''

    # sents = []
    # words = []
    # current_ids = []
    # all_texts = []

    # changing_lang = False
    new_translate = False
    # free_input = False
    changing = False
    adding = False
    adding_input = False
    # all_text = False
    # reverse = False
    # wiki = False
    multiple_sents = False
    building = False
    translating_text = False

    def inline_buttons(self, message=None, call=None):
        if call.message:
            user_data = self.get_user_data(call=call)

            if call.data == 'write':
                self.write_word(message, call)
                bot.edit_message_text(chat_id=user_data['user_id'], message_id=self.trans_window, text='Записано!\n' + '<b>'+self.word+'</b>' + ':\n' + '<b>'+self.translated_word+'</b>', parse_mode='html')
                return
            
            if call.data == 'change':
                self.changing = True
                self.menu(message, call)

            if call.data == 'add':
                self.adding = True
                self.menu(message, call)

            if call.data == 'translate':
                self.translating_text = True
                self.translated_text = GoogleTranslator(source='auto', target='ru').translate(self.remove_underline(self.visual_text))
                self.visual_text = self.translated_text

                text = self.count_texts()
                markup = self.text_buttons(message, call)
                bot.edit_message_text(chat_id=user_data['user_id'], message_id=self.text_window, text=text, reply_markup=markup, parse_mode='html')
                return

            if call.data == 'original':
                self.translating_text = False
                self.visual_text = self.underline_existed_words(str(user_data['user_id']), self.text)
                
                text = self.count_texts()
                markup = self.text_buttons(message, call)
                bot.edit_message_text(chat_id=user_data['user_id'], message_id=self.text_window, text=self.visual_text, reply_markup=markup, parse_mode='html')
                return

            if call.data == 'next':
                self.reverse = False
                self.translating_text = False
                self.changing = False
                self.adding = False

                if len(self.all_texts) == 1:
                    return

                elif self.text_count == len(self.all_texts)-1:
                    self.text_count = 0
                    self.text = self.all_texts[self.text_count]
                    self.visual_text = self.underline_existed_words(str(user_data['user_id']), self.text)
                    text = self.count_texts()

                elif self.text_count >= 0:
                    self.text_count += 1
                    self.text = self.all_texts[self.text_count]
                    self.visual_text = self.underline_existed_words(str(user_data['user_id']), self.text)
                    text = self.count_texts()

                if self.building:
                    self.sent_count = 0
                    bot.delete_message(chat_id=user_data['user_id'], message_id=self.question_window)
                    bot.delete_message(chat_id=user_data['user_id'], message_id=self.trans_window)
                    self.build_sent(message, call)
                else:
                    markup = self.text_buttons(message, call)
                    bot.edit_message_text(chat_id=user_data['user_id'], message_id=self.text_window, text=text, reply_markup=markup, parse_mode='html')
                return

            if call.data == 'previous':
                self.reverse = False
                self.translating_text = False
                self.changing = False
                self.adding = False

                if len(self.all_texts) == 1:
                    return

                elif self.text_count == 0:
                    self.text_count = len(self.all_texts)-1
                    self.text = self.all_texts[self.text_count]
                    self.visual_text = self.underline_existed_words(str(user_data['user_id']), self.text)
                    text = self.count_texts()

                elif self.text_count <= len(self.all_texts)-1:
                    self.text_count -= 1
                    self.text = self.all_texts[self.text_count]
                    self.visual_text = self.underline_existed_words(str(user_data['user_id']), self.text)
                    text = self.count_texts()

                if self.building:
                    self.sent_count = 0
                    bot.delete_message(chat_id=user_data['user_id'], message_id=self.question_window)
                    bot.delete_message(chat_id=user_data['user_id'], message_id=self.trans_window)
                    self.build_sent(message, call)
                else:
                    markup = self.text_buttons(message, call)
                    bot.edit_message_text(chat_id=user_data['user_id'], message_id=self.text_window, text=text, reply_markup=markup, parse_mode='html')
                return
            
            if call.data == 'previous_sent':
                self.reverse = False
                if self.sent_count > 0:
                    self.sent_count -= 1
                    self.sent = self.sents[self.count]
                else:
                    return

                if self.building:
                    bot.delete_message(chat_id=user_data['user_id'], message_id=self.question_window)
                    bot.delete_message(chat_id=user_data['user_id'], message_id=self.trans_window)
                    self.build_sent(message, call)

                return

            if call.data == 'next_sent':
                self.reverse = False
                if self.sent_count < len(self.sents)-1:
                    self.sent_count += 1
                    # self.sent = self.sents[self.count]
                else:
                    return

                if self.building:
                    bot.delete_message(chat_id=user_data['user_id'], message_id=self.question_window)
                    bot.delete_message(chat_id=user_data['user_id'], message_id=self.trans_window)
                    self.build_sent(message, call)

                return

            if call.data =='all_text':
                self.all_text = True
                self.sentence_buttons(message, call)
                return

            if call.data == 'roll_up':
                if len(self.sents) > 1:
                    self.all_text = False
                self.sentence_buttons(message, call)
                return
    
            if call.data == 'build':
                self.sent_count = 0

                self.building = True
                self.input_sentences = False
                self.new_sentence = True

                self.build_sent(message, call)
                return

            if call.data == 'end':
                self.reverse = False
                self.building = False
                self.adding = False
                self.changing = False
                self.multiple_sents = False

                markup = self.text_buttons(message, call)
                bot.delete_message(chat_id=user_data['user_id'], message_id=self.question_window)
                bot.delete_message(chat_id=user_data['user_id'], message_id=self.trans_window)
                bot.edit_message_text(chat_id=user_data['user_id'], message_id=self.text_window, text=self.visual_text, reply_markup=markup, parse_mode='html')

            if call.data == 'delete':
                if not self.text and not self.text_window:
                    self.text = call.message.text
                    self.text_window = call.message.message_id

                text_to_delete = self.text

                db.delete_text(text_to_delete, str(user_data['user_id']))
                self.all_texts = db.get_texts(str(user_data['user_id']))

                if len(self.all_texts) == 1:
                    self.text_count = 0
                    self.text = self.all_texts[self.text_count]

                elif not self.all_texts:
                    self.text = 'Пока нет текстов!'

                elif self.text_count == len(self.all_texts)-1:
                    self.text_count -= 1
                    self.text = self.all_texts[self.text_count]

                elif self.text_count < len(self.all_texts)-1:
                    self.text = self.all_texts[self.text_count]

                elif self.text_count > len(self.all_texts)-1:
                    self.text_count = 0
                    self.text = self.all_texts[self.text_count]
                
                self.visual_text = self.underline_existed_words(str(user_data['user_id']), self.text)
                markup = self.text_buttons(message, call)
                bot.edit_message_text(chat_id=user_data['user_id'], message_id=self.text_window, text=self.visual_text, reply_markup=markup, parse_mode='html')
                return

            if call.data == 'previus_plus':
                if not self.free_input:
                    if self.current_ids[0] == 0:
                        pass
                    else:
                        self.current_ids[:0] = [self.current_ids[0]-1]
                        self.printing(message, call)

            if call.data == 'next_plus':
                if not self.free_input:
                    if self.current_ids[-1] == len(self.words)-1:
                        pass
                    else:
                        self.current_ids.append(self.current_ids[-1] + 1)
                        self.printing(message, call)

            if call.data == 'previus_minus':
                if not self.free_input:
                    if len(self.current_ids) == 1:
                        pass
                    else:
                        self.current_ids.pop(0)
                        self.printing(message, call)

            if call.data == 'next_minus':
                if not self.free_input:
                    if len(self.current_ids) == 1:
                        pass
                    else:
                        self.current_ids.pop()
                        self.printing(message, call)

            if call.data == 'plus':
                self.slicer +=1
                first_word = self.words.index(self.past_message)
                last_word = first_word + self.slicer +1

                if last_word >= len(self.words)+1:
                    last_word = last_word - self.slicer +1
                    self.slicer += -1
                    return

                self.word_to_write = ' '.join([x for x in self.words[first_word:last_word]])
                # print('word_to_write',self.word_to_write)

                markup = types.InlineKeyboardMarkup(row_width=2)
                item1 = types.InlineKeyboardButton(emoji.emojize(':heavy_minus_sign:', use_aliases=True), callback_data='minus')
                item2 = types.InlineKeyboardButton(emoji.emojize(':heavy_plus_sign:', use_aliases=True), callback_data='plus')
                item3 = types.InlineKeyboardButton('записать', callback_data='write')
                markup.add(item1,item2,item3)

                translated = GoogleTranslator(source=self.lang, target='ru').translate(self.word_to_write)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=self.trans_window, text='<b>'+self.word_to_write+'</b>' + '\nозначает:\n' + translated, reply_markup=markup, parse_mode='html')

            if call.data == 'minus':
                self.slicer += -1
                first_word = self.words.index(self.past_message)
                last_word = first_word + self.slicer +1

                if last_word == first_word:
                    self.slicer += 1
                    last_word = first_word + self.slicer +1
                    return

                self.word_to_write = ' '.join([x for x in self.words[first_word:last_word]])

                markup = types.InlineKeyboardMarkup(row_width=2)
                item1 = types.InlineKeyboardButton(emoji.emojize(':heavy_minus_sign:', use_aliases=True), callback_data='minus')
                item2 = types.InlineKeyboardButton(emoji.emojize(':heavy_plus_sign:', use_aliases=True), callback_data='plus')
                item3 = types.InlineKeyboardButton('записать', callback_data='write')
                markup.add(item1,item2,item3)

                translated = GoogleTranslator(source=self.lang, target='ru').translate(self.word_to_write)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=self.trans_window, text='<b>'+self.word_to_write+'</b>' + '\nозначает:\n' + translated, reply_markup=markup, parse_mode='html')

    def build_sent(self, message, call):
        user_data = self.get_user_data(message=message, call=call)

        if not self.multiple_sents:
            self.sents = self.text_to_sents(self.text)

        self.sent_words = self.sent_to_words(self.sents)

        if len(self.sents) > 1:
            self.multiple_sents = True
            text_markup = self.sentence_buttons(message, call)
            bot.edit_message_text(chat_id=user_data['user_id'], message_id=self.text_window, text=self.visual_text, reply_markup=text_markup, parse_mode='html')
        else:
            self.multiple_sents = False
            text_markup = self.text_buttons(message, call)
            text = self.count_texts()
            bot.edit_message_text(chat_id=user_data['user_id'], message_id=self.text_window, text=text, reply_markup=text_markup, parse_mode='html')
        
        words_markup = self.words_buttons(self.sent_words)
        bot.send_message(user_data['user_id'], 'Какое слово тебе не знакомо?', reply_markup=words_markup)
        bot.send_message(user_data['user_id'], 'Выбери слово')

        self.question_window = self.last_message_id+1
        self.trans_window = self.last_message_id+2
        self.last_message_id = self.trans_window
        
        db.set_collection(str(user_data['user_id']))
        db.update_last_message_id(self.last_message_id, str(user_data['user_id']))

    def sentence_buttons(self, message=None, call=None, state=None):
        user_data = self.get_user_data(message=message, call=call)

        if self.all_text:
            self.visual_text = self.underline_existed_words(str(user_data['user_id']), self.text)
            visibility_button = 'collapse'
            visibility_callback = 'roll_up'
        else:
            self.visual_text = self.sent
            visibility_button = 'full text'
            visibility_callback = 'all_text'

        if self.translating_text:
            trans_button = 'original'
            trans_callback = 'original'
        else:
            trans_button = 'translate'
            trans_callback = 'translate'

        markup = types.InlineKeyboardMarkup(row_width=3)

        prev = types.InlineKeyboardButton('previous', callback_data='previous')
        trans = types.InlineKeyboardButton(trans_button, callback_data=trans_callback)
        next = types.InlineKeyboardButton('next', callback_data='next')

        prev_sent = types.InlineKeyboardButton(emoji.emojize(':reverse_button:', use_aliases=True), callback_data='previous_sent')
        visibility = types.InlineKeyboardButton(visibility_button, callback_data=visibility_callback)
        next_sent = types.InlineKeyboardButton(emoji.emojize(':play_button:', use_aliases=True), callback_data='next_sent')

        end = types.InlineKeyboardButton('end', callback_data='end')

        markup.add(prev, trans, next, prev_sent, visibility, next_sent, end)

        return markup

    def printing(self, message=None, call=None):
        current_words = []
        self.word = None
        for x in self.current_ids:
            current_words.append(self.words[x])
        self.word = ' '.join(current_words)

        self.menu(message, call)

    def menu(self, message=None, call=None):
        user_data = self.get_user_data(message=message, call=call)

        markup = types.InlineKeyboardMarkup(row_width=3)
        item1 = types.InlineKeyboardButton(emoji.emojize(':reverse_button:'), callback_data='previus_plus')
        item3 = types.InlineKeyboardButton(emoji.emojize(':play_button:'), callback_data='next_plus')
        item2 = types.InlineKeyboardButton('add', callback_data='add')
        item4 = types.InlineKeyboardButton(emoji.emojize(':play_button:'), callback_data='previus_minus')
        item6 = types.InlineKeyboardButton(emoji.emojize(':reverse_button:'), callback_data='next_minus')
        item5 = types.InlineKeyboardButton('change', callback_data='change')
        item7 = types.InlineKeyboardButton('save', callback_data='write')

        markup.add(item1,item2,item3,item4,item5,item6,item7)

        sign = ''
        
        self.exist_word = db.get_word_translation(self.word, str(user_data['user_id']))

        if self.exist_word or self.changing or self.adding:

            if self.exist_word:
                x = [x for x in self.exist_word]
                self.translated_word = ', '.join(x)
                sign = 'Это слово уже есть!\n'

            if self.changing:
                if self.new_translate:
                    self.translated_word = self.new_translate
                    self.new_translate = None
                else:
                    sign = '<b>Кинь свой перевод!</b>\n'

            if self.adding:
                if self.new_translate:
                    self.translated_word = self.translated_word + ', ' + self.new_translate
                    self.new_translate = None
                else:
                    sign = '<b>Добавь перевод!</b>\n'
        else:
            def has_cyrillic(text):
                return bool(re.search('[а-яА-Я]', text))

            if has_cyrillic(self.word):
                target = self.lang
            else:
                target = 'ru'

            self.translated_word = GoogleTranslator(source='auto', target=target).translate(self.word)

        text = sign+'<b>'+self.word+'</b>' + '\nозначает:\n' + '<b>'+self.translated_word+'</b>'

        bot.edit_message_text(chat_id=user_data['user_id'], message_id=self.trans_window, text=text, reply_markup=markup, parse_mode='html')

    def sent_to_words(self, sents):
        self.sent = sents[self.sent_count]
        self.words = re.findall(r"[\w']+", self.sent)
        return self.words

    def words_buttons(self, words):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        items = [types.KeyboardButton(item) for item in words]
        markup.add(*items)

        return markup
    
    def detect_lang(self, text):
        languages = [Language.ENGLISH, Language.SPANISH]
        detector = LanguageDetectorBuilder.from_languages(*languages).build()
        language = detector.detect_language_of(text)
        language_code = language.iso_code_639_1

        return str(language_code.name).lower()
    
    def write_word(self, message=None, call=None):
        user_data = self.get_user_data(message=message, call=call)
        self.word_lang = self.detect_lang(self.text)

        db.save_word(word=self.word, language=self.word_lang, translations=[self.translated_word], examples=[self.sent], collection_name=str(user_data['user_id']))

    def instructions(self, message=None, call=None):
        user_data = self.get_user_data(message=message)
        self.last_message_id = user_data['message_id']

        db.update_last_message_id(self.last_message_id, str(user_data['user_id']))

        if self.building:
            if self.adding or self.changing:
                self.new_translate = message.text
                bot.delete_message(chat_id=user_data['user_id'], message_id=user_data['message_id'])
                self.menu(message, call)

                self.adding = False
                self.changing = False
                return

            try:
                self.word = message.text
                index_word = self.sent_words.index(self.word)
                self.current_ids = [index_word]
                self.free_input = False
            except ValueError:
                self.free_input = True

            bot.delete_message(chat_id=user_data['user_id'], message_id=user_data['message_id'])
            self.menu(message, call)
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

    def text_buttons(self, message=None, call=None):
        if self.building and self.multiple_sents:
            markup = self.sentence_buttons(message, call)
        else:
            markup = types.InlineKeyboardMarkup(row_width=3)
            prev = types.InlineKeyboardButton('previous', callback_data='previous')
            next = types.InlineKeyboardButton('next', callback_data='next')
            build = types.InlineKeyboardButton('build', callback_data='build')
            delete = types.InlineKeyboardButton('delete', callback_data='delete')
            end = types.InlineKeyboardButton('end', callback_data='end')

            if self.translating_text:
                trans = types.InlineKeyboardButton('original', callback_data='original')
            else:
                trans = types.InlineKeyboardButton('translate', callback_data='translate')

            if self.building:
                markup.add(prev, trans, next, end)
            else:
                markup.add(prev, trans, next, build, delete)

        return markup

    def start(self, message=None, call=None):
        user_data = self.get_user_data(message=message)

        self.building = False
        self.adding = False
        self.changing = False
        self.translating_text = False
        self.multiple_sents = False

        self.sent_count = 0
        self.last_message_id = user_data['message_id']
        
        self.all_texts = db.get_texts(str(user_data['user_id']))
        
        if self.all_texts:
            self.text = self.all_texts[0]
            self.visual_text = self.underline_existed_words(str(user_data['user_id']), self.text)
            self.visual_plus_count = f'{self.text_count}/{len(self.all_texts)}\n{self.visual_text}'
            
            text = self.count_texts()
            markup = self.text_buttons(message, call)
            bot.send_message(user_data['user_id'], text, reply_markup=markup, parse_mode='html')
            
            self.last_message_id += 1
            self.text_window = self.last_message_id
            db.update_last_message_id(self.last_message_id, str(user_data['user_id']))
        else:
            self.text = None
            bot.send_message(user_data['user_id'], 'Пока нет текстов!')

    def count_texts(self):
        return f'{self.text_count+1}/{len(self.all_texts)}\n{self.visual_text}'

    def underline_existed_words(self, user_id, text):
        words = db.get_words_by_example(example=text, collection_name=user_id)
        if words:
            for word in words:
                text = text.replace(word, f'<u>{word}</u>')

        return text

    def remove_underline(self, text):
        text = text.replace('<u>', '')
        text = text.replace('</u>', '')
        return text

    def text_to_sents(self, text):

        alphabets= "([A-Za-z])"
        prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
        suffixes = "(Inc|Ltd|Jr|Sr|Co)"
        starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
        acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
        websites = "[.](com|net|org|io|gov)"

        def split_into_sentences(text):

            text = " " + text + "  "
            # text = text.replace('-\n', '')
            # text = text.replace("\n"," ")
            text = re.sub(prefixes,"\\1<prd>",text)
            text = re.sub(websites,"<prd>\\1",text)
            if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
            text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
            text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
            text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
            text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
            text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
            text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
            text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
            if "”" in text: text = text.replace(".”","”.")
            if "\"" in text: text = text.replace(".\"","\".")
            if "!" in text: text = text.replace("!\"","\"!")
            if "?" in text: text = text.replace("?\"","\"?")
            text = text.replace(".",".<stop>")
            text = text.replace("?","?<stop>")
            text = text.replace("!","!<stop>")
            text = text.replace("<prd>",".")
            sentences = text.split("<stop>")
            if len(sentences) > 1:
                sentences = sentences[:-1]
            sentences = [s.strip() for s in sentences]
            # print(sentences)
            return sentences

        sents = split_into_sentences(text)
        return sents