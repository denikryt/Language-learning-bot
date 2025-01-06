from __future__ import annotations
from abc import ABC, abstractmethod
from state import State
from default import Default

class Context:
    """
    Контекст определяет интерфейс, представляющий интерес для клиентов. Он также
    хранит ссылку на экземпляр подкласса Состояния, который отображает текущее
    состояние Контекста.
    """

    _state = None
    """
    Ссылка на текущее состояние Контекста.
    """
    # def __str__ (self, state: State) -> None:
    #     return state.__name__

    def __init__(self, state: State) -> None:
        self.transition_to(state)

    def transition_to(self, state: State):
        """
        Контекст позволяет изменять объект Состояния во время выполнения.
        """

        print(f"Context: Transition to {type(state).__name__}")
        self._state = state
        self._state.context = self

    def set_default_state(self):
        self._state = Default()

    """
    Контекст делегирует часть своего поведения текущему объекту Состояния.
    """

    def start(self, message=None, call=None):
        self._state.start(message, call)

    def inline_buttons(self, message=None, call=None):
        self._state.inline_buttons(message, call)

    def printing(self, message, call):
        self._state.printing(self, chat_id)
    
    def sentence_buttons(self, message, call):
        self._state.sentence_buttons(self, message, call)

    def menu(self,message, call):
        self._state.menu(self,message, call)

    def vars(self, message, call, sents, count, lang):
        self._state.vars(message, call, sents, count, lang)

    def hello(self, *args, **kwargs):
        self._state.hello(*args, **kwargs)

    def text_to_sents(self, message, call):
        self._state.text_to_sents(message, call)

    def sent_to_words(self, message, call, sents):
        self._state.sent_to_words(message, call, sents)
    
    def write_word(self, message):
        self._state.write_word(message)

    def random_words(self, message, call):
        self._state.random_words(message)

    def words_buttons(self, message):
        self._state.buttons(message)

    def instructions(self, message):
        self._state.instructions(message)
