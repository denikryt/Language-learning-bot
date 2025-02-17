from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv()

data_schema = {
    "texts": [],
    "words": [],
    "last_message_id": 0,
    "channel_id": os.getenv('MY_CHANNEL_ID')
}

# object_schema = {
#         "text": "",
#         "language": "",
#         "words": {
#             "word": "",
#             "level": 0,
#             "translations": []
#         }
#     }

# data_schema = {
#     "objects": {},
#     "last_message_id": 0,
#     "channel_id": os.getenv('MY_CHANNEL_ID')
# }

words_schema = {
    "word": "",
    "level": 0,
    "language": "",
    "translations": [],
    "examples": []
}

text_schema = {
    "text": ""
}

class Database:
    _client = None
    _db = None
    _data_schema = data_schema
    _words_schema = words_schema

    def __init__(self, collection_name=None):
        if not Database._client:
            load_dotenv()
            Database._client = MongoClient(os.getenv('MONGO_DB'), server_api=ServerApi('1'))
            Database._db = Database._client['database']
            # Send a ping to confirm a successful connection
            try:
                Database._client.admin.command('ping')
                print("Pinged your deployment. You successfully connected to MongoDB!")
            except Exception as e:
                print(e)
        if collection_name:
            self.set_collection(collection_name)

    def set_collection(self, collection_name: str):
        # Create collection if not exists
        if collection_name not in Database._db.list_collection_names():
            Database._db.create_collection(collection_name)
            # Create basic schema
            Database._db[collection_name].insert_one(Database._data_schema)
        self.collection = Database._db[collection_name]

    def get_translations(self, word, collection_name: str):
        self.collection = Database._db[collection_name]

        result = self.collection.find_one({'words.word': word})
        if result:
            for item in result['words']:
                if item['word'] == word:
                    return item['translations']
        return None
    
    def get_texts(self, collection_name: str):
        self.collection = Database._db[collection_name]
        result = self.collection.find_one({})
        if result:
            return [item['text'] for item in result['texts']]
        return None
    
    def update_last_message_id(self, message_id, collection_name: str):
        self.collection = Database._db[collection_name]
        return self.collection.update_one({}, {'$set': {'last_message_id': message_id}})
    
    def save_text(self, text, collection_name: str):
        self.collection = Database._db[collection_name]
        return self.collection.update_one({}, {'$push': {'texts': {'text': text}}})
    
    def get_collection_name_by_channel_id(self, channel_id: str):
        collections = Database._db.list_collection_names()
        for collection in collections:
            result = Database._db[collection].find_one({'channel_id': channel_id})
            if result:
                return collection
        return None
    
    def get_word_translation(self, word, collection_name: str):
        self.collection = Database._db[collection_name]

        result = self.collection.find_one({'words.word': word})
        if result:
            for item in result['words']:
                if item['word'] == word:
                    return item['translations']
        return None
    
    def delete_text(self, text, collection_name: str):
        self.collection = Database._db[collection_name]
        self.collection.update_one({}, {'$pull': {'texts': {'text': text}}})

    def update_word_translation(self, word, translations: list, collection_name: str):
        self.collection = Database._db[collection_name]
        self.collection.update_one({'words.word': word}, {'$set': {'words.$.translations': translations}})

    def save_word(self, word, language, translations: list, examples: list, collection_name: str):
        self.collection = Database._db[collection_name]
        self.collection.update_one({}, {'$push': {'words': {
            'word': word, 
            'language': language, 
            'translations': translations, 
            'examples': examples, 
            'level': 0
            }}})
        
    def get_words(self, collection_name: str):
        self.collection = Database._db[collection_name]

        result = self.collection.find_one({})
        if result:
            return [item['word'] for item in result['words']]
        return None
    
    def delete_all_words(self, collection_name: str):
        self.collection = Database._db[collection_name]
        self.collection.update_one({}, {'$set': {'words': []}})

    def get_levels(self, collection_name: str):
        self.collection = Database._db[collection_name]

        result = self.collection.find_one({})
        if result:
            return [item['level'] for item in result['words']]
        return None
    
    def get_word_level(self, word, collection_name: str):
        self.collection = Database._db[collection_name]

        result = self.collection.find_one({'words.word': word})
        if result:
            for item in result['words']:
                if item['word'] == word:
                    return item['level']
        return None
    
    def update_word_level(self, word, level, collection_name: str):
        self.collection = Database._db[collection_name]

        self.collection.update_one({'words.word': word}, {'$set': {'words.$.level': level}})

    def get_words_by_example(self, example, collection_name: str):
        self.collection = Database._db[collection_name]

        result = self.collection.find_one({})
        if result:
            words = []
            for item in result['words']:
                if example in item['examples']:
                    words.append(item['word'])
            return words
        return None
    
    def text_exists(self, text, collection_name: str):
        self.collection = Database._db[collection_name]

        result = self.collection.find_one({'texts.text': text})
        if result:
            return True
        return False
    
    def get_examples_by_word(self, word, collection_name: str):
        self.collection = Database._db[collection_name]

        result = self.collection.find_one({'words.word': word})
        if result:
            for item in result['words']:
                if item['word'] == word:
                    return item['examples']
        return None


db = Database()