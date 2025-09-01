import sys

from behave.model import Tag
from behave.formatter.base import StreamOpener
from behave.reporter.summary import AbstractSummaryReporter

# Для конфигурации multiprocessing (сериализация/десериализация)


# AbstractSummaryReporter


def reporter_getstate(self):
    """Исключает несериализуемый атрибут `stream` из состояния объекта.

    Используется для корректной сериализации объекта SummaryReporter,
    когда он передается между процессами в multiprocessing.
    """
    state = self.__dict__.copy()
    if "stream" in state:
        del state["stream"]  # Удаляем поток, который нельзя сериализовать
    return state


def reporter_setstate(self, state):
    """Восстанавливает состояние объекта после десериализации.

    Args:
        state: Словарь с сохраненным состоянием объекта
    """
    self.__dict__.update(state)
    # Пересоздаем поток на основе сохраненного имени
    stream = getattr(sys, self.output_stream_name, sys.stdout)
    self.stream = StreamOpener.ensure_stream_with_encoder(stream)


AbstractSummaryReporter.__getstate__ = reporter_getstate
AbstractSummaryReporter.__setstate__ = reporter_setstate


# Tag


def tag_getstate(self):
    """Сохраняет минимальное состояние объекта Tag для сериализации.

    Возвращает:
        Кортеж из строки тега и номера строки
    """
    return (super(Tag, self).__str__(), self.line)


def tag_reduce(self):
    """Определяет, как создать новый объект Tag при десериализации.

    Returns:
        Кортеж: (класс Tag, аргументы для его инициализации)
    """
    return (Tag, (super(Tag, self).__str__(), self.line))


Tag.__getstate__ = tag_getstate
Tag.__reduce__ = tag_reduce
