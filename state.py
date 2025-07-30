from __future__ import annotations
from abc import ABC, abstractmethod

class State(ABC):
    """
    Базовый класс Состояния объявляет методы, которые должны реализовать все
    Конкретные Состояния, а также предоставляет обратную ссылку на объект
    Контекст, связанный с Состоянием. Эта обратная ссылка может использоваться
    Состояниями для передачи Контекста другому Состоянию.
    """

    @property
    def context(self) -> Context:
        return self._context

    @context.setter
    def context(self, context: Context) -> None:
        self._context = context

    @abstractmethod
    def start(self, message, call) -> None:
        pass

    @abstractmethod
    def instructions(self, message) -> None:
        pass

    @abstractmethod
    def get_user_data(self, message,call) -> None:
        pass
