from abc import ABC
from typing import Generator, TypeVar, Generic

from behave.configuration import Configuration

T = TypeVar("T")


class PoolExecutor(ABC, Generic[T]):
    """Абстрактный обобщенный класс для управления пулом элементов (воркеров/потоков)

    Основная цель:
    - Создание и управление набором однотипных объектов
    - Обеспечение доступа к элементам по индексу
    - Поддержка итерации по всем элементам
    """

    _config: Configuration
    _pool: list[T]

    def __init__(self, config: Configuration, item_class: type[T]):
        """Инициализация пула

        Args:
            config: Конфигурация из behave
            item_class: Класс элементов пула
        """
        self._config = config
        self._pool = self._init_items(item_class)

    def _init_items(self, item_class: type[T]) -> list[T]:
        """Создать список элементов пула

        Args:
            item_class: Тип элемента для инициализации

        Returns:
            Список инициализированных элементов
        """
        return [item_class(self._config, index) for index in range(self._config.jobs)]

    def __getitem__(self, index: int) -> T:
        """Получить элемент по индексу

        Args:
            index: Индекс элемента в пуле

        Returns:
            Элемент пула по указанному индексу
        """
        return self._pool[index]

    def __iter__(self) -> Generator[T, None, None]:
        """Итератор по элементам пула

        Yields:
            Последовательность элементов пула
        """
        for worker in self._pool:
            yield worker
