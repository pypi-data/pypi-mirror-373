import os
from abc import ABC, abstractmethod
from collections import deque, defaultdict
from typing import Optional
from copy import deepcopy
from sortedcontainers import SortedDict

from behave.model import Feature
from behave.configuration import Configuration
from behave.runner_util import parse_features, collect_feature_locations, PathManager
from behave.runner import path_getrootdir, Runner
from behave.exception import ConfigError


class FeatureFinder:
    """Поиск и настройка путей к фичам (feature-файлам)"""

    _config: Configuration

    def __init__(self, config: Configuration):
        self._config = config

    def _setup_paths(self, path_manager: PathManager):
        """Настройка путей для выполнения тестов

        - Определяет базовый каталог
        - Проверяет наличие нужных директорий и файлов
        - Обрабатывает ошибки конфигурации
        """
        # pylint: disable=too-many-branches, too-many-statements
        if self._config.paths:
            if self._config.verbose:
                print(
                    "Указанный путь:",
                    ", ".join('"%s"' % path for path in self._config.paths),
                )
            first_path = self._config.paths[0]
            if hasattr(first_path, "filename"):
                first_path = first_path.filename
            base_dir = first_path
            if base_dir.startswith("@"):
                base_dir = base_dir[1:]
                file_locations = self.feature_locations()
                if file_locations:
                    base_dir = os.path.dirname(file_locations[0].filename)
            base_dir = os.path.abspath(base_dir)

            # Если указанный путь является файлом, используем его директорию
            if os.path.isfile(base_dir):
                if self._config.verbose:
                    print("Основной путь указывает на файл, используем его директорию")
                base_dir = os.path.dirname(base_dir)
        else:
            if self._config.verbose:
                print(
                    'Используется стандартный путь "{}"'.format(
                        Runner.DEFAULT_DIRECTORY
                    )
                )
            base_dir = os.path.abspath(Runner.DEFAULT_DIRECTORY)

        # Получаем корневую директорию (учитываем Windows)
        root_dir = path_getrootdir(base_dir)
        new_base_dir = base_dir
        steps_dir = self._config.steps_dir
        environment_file = self._config.environment_file

        while True:
            if self._config.verbose:
                print("Проверяем директорию:", new_base_dir)

            # Ищем директорию с шагами или файлом окружения
            if os.path.isdir(os.path.join(new_base_dir, steps_dir)):
                break
            if os.path.isfile(os.path.join(new_base_dir, environment_file)):
                break
            if new_base_dir == root_dir:
                break

            new_base_dir = os.path.dirname(new_base_dir)

        if new_base_dir == root_dir:
            if self._config.verbose:
                if not self._config.paths:
                    print(
                        'ОШИБКА: Не найдена директория "%s". '
                        "Укажите, где находятся ваши фичи." % steps_dir
                    )
                else:
                    print(
                        'ОШИБКА: Не найдена директория "%s" в указанном '
                        'пути "%s"' % (steps_dir, base_dir)
                    )

            message = "Директория %s не найдена в %r" % (steps_dir, base_dir)
            raise ConfigError(message)

        base_dir = new_base_dir
        self._config.base_dir = base_dir

        # Проверяем наличие feature-файлов
        for _, _, filenames in os.walk(base_dir, followlinks=True):
            if [fn for fn in filenames if fn.endswith(".feature")]:
                break
        else:
            if self._config.verbose:
                if not self._config.paths:
                    print(
                        'ОШИБКА: Не найдены файлы "<name>.feature". '
                        "Укажите, где находятся ваши фичи."
                    )
                else:
                    print(
                        'ОШИБКА: Не найдены файлы "<name>.feature" '
                        'в указанном пути "%s"' % base_dir
                    )
            raise ConfigError("Фичи не найдены в %r" % base_dir)

        self.base_dir = base_dir
        path_manager.add(base_dir)
        if not self._config.paths:
            self._config.paths = [base_dir]

        if base_dir != os.getcwd():
            path_manager.add(os.getcwd())

    def _find_feature_location(self) -> list[str]:
        """Поиск местоположений фичей"""
        return [
            filename
            for filename in collect_feature_locations(self._config.paths)
            if not self._config.exclude(filename)
        ]

    def get_all_features(self) -> list[Feature]:
        """Получить список всех фичей из указанных путей"""
        path_manager = PathManager()
        with path_manager:
            self._setup_paths(path_manager)
            return parse_features(
                self._find_feature_location(), language=self._config.lang
            )


class TaskAllocator(ABC):
    """Абстрактный класс для распределения задач между воркерами"""

    _config: Configuration
    _feature_finder: FeatureFinder

    def __init__(self, config: Configuration):
        self._config = config
        self._feature_finder = FeatureFinder(config)

    @abstractmethod
    def allocate(self, job_number: int) -> Optional[Feature]:
        """Распределить задачу (фичу) для указанного номера воркера"""
        pass

    @abstractmethod
    def empty(self) -> bool:
        """Проверить, остались ли еще нераспределенные задачи"""
        pass


class FeatureTaskAllocator(TaskAllocator):
    """Реализация распределителя задач с использованием очереди фич"""

    _features: deque[Feature]

    def __init__(self, config: Configuration):
        super().__init__(config)
        self._features = deque(self._feature_finder.get_all_features())

    def allocate(self, _: int) -> Optional[Feature]:
        """Выдать следующую фичу из очереди"""
        if not self.empty():
            return self._features.popleft()

    def empty(self) -> bool:
        """Проверить, пустая ли очередь задач"""
        return len(self._features) == 0


class ScenarioTaskAllocator(TaskAllocator):
    """Реализация распределителя задач с использованием очереди сценариев"""

    _features: deque[Feature]

    def __init__(self, config: Configuration):
        super().__init__(config)
        self._features = self._get_splitted_features_by_scenario()

    def _get_splitted_features_by_scenario(self) -> deque[Feature]:
        queue = deque()
        for feature in self._feature_finder.get_all_features():
            scenarios = feature.scenarios
            feature.scenarios = []
            feature.run_items = []
            for scenario in scenarios:
                copied_feature = deepcopy(feature)
                copied_feature.add_scenario(scenario)
                queue.append(copied_feature)
        return queue

    def allocate(self, _: int) -> Optional[Feature]:
        """Выдать следующую фичу из очереди"""
        if not self.empty():
            return self._features.popleft()

    def empty(self) -> bool:
        """Проверить, пустая ли очередь задач"""
        return len(self._features) == 0


class DirectoryTaskAllocator(TaskAllocator):
    """Распределитель задач, который группирует фичи по директориям и выдает их воркерам.

    Каждая директория полностью выполняется одним воркером. Фичи внутри директории
    распределяются последовательно.
    """

    def __init__(self, config: Configuration):
        super().__init__(config)
        # Очередь директорий (каждая директория содержит свой список фич)
        self._features = self._group_features_by_dir()
        # Контекст воркеров: {id_воркера: очередь фич из его директории}
        self._worker_context = defaultdict(deque)

    def _group_features_by_dir(self) -> deque[deque[Feature]]:
        """Группирует фичи по директориям и возвращает очередь директорий."""
        # Используем SortedDict для детерминированной сортировки директорий
        dirs = SortedDict()

        # Группируем фичи по директориям
        for feature in self._feature_finder.get_all_features():
            # Нормализуем путь: корневые файлы попадают в директорию "."
            directory = os.path.dirname(feature.filename) or "."
            dirs.setdefault(directory, deque()).append(feature)

        return deque(dirs.values())

    def allocate(self, index: int) -> Optional[Feature]:
        """Выдает следующую фичу для воркера с учетом директорий.

        1. Если воркер еще не получил свою директорию - назначает ее.
        2. Возвращает первую фичу из очереди воркера.
        3. Возвращает None, если больше нет фич.
        """
        # Если у воркера еще нет фич, но есть нераспределенные директории
        if not self._worker_context[index] and not self.empty():
            self._worker_context[index] = self._features.popleft()

        # Возвращаем следующую фичу из контекста воркера
        return (
            self._worker_context[index].popleft()
            if self._worker_context[index]
            else None
        )

    def empty(self) -> bool:
        """Проверяет, все ли фичи были распределены."""
        # Учитываем как оставшиеся директории, так и текущие задания воркеров
        return len(self._features) == 0 and all(
            not context for context in self._worker_context.values()
        )
