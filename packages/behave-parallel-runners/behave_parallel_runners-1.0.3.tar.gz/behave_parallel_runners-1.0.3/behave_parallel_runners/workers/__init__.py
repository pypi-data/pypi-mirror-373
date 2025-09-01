from os import environ
from abc import ABC, abstractmethod
from typing import Optional

from behave.model import Feature
from behave.runner import Runner as BehaveRunner
from behave.runner import Context
from behave.formatter._registry import make_formatters
from behave.runner import the_step_registry as behave_step_registry

from behave.configuration import Configuration

from ..pool import PoolExecutor

WORKER_TERMINATE_TIMEOUT_IN_SEC = int(
    environ.get("WORKER_TERMINATE_TIMEOUT_IN_SEC", 30)
)

QUEUE_WAIT_TIMEOUT_IN_SEC = WORKER_TERMINATE_TIMEOUT_IN_SEC / 3


class WorkerRunner(BehaveRunner):
    """Подкласс Runner для выполнения фичей внутри воркера (потока/процесса)

    Поведение:
    - Создает один `Context` на воркер (инициализируется один раз в `setup()`)
    - Загружает хуки и определения шагов один раз
    - Предоставляет `run_feature()` для динамического выполнения фичей
    - `teardown()` завершает выполнение (after_all, очистка, закрытие форматтера)
    """

    _is_started: bool
    _is_finished: bool
    _is_failed: bool
    _index: int

    def __init__(self, config: Configuration, index: int):
        super().__init__(config)
        self._is_started = False
        self._is_finished = False
        self._is_failed = False
        self._index = index

    @property
    def index(self) -> int:
        """Индекс воркера"""
        return self._index

    def __str__(self):
        return f"{self.__class__.__name__}-{self.index}"

    def __repr__(self) -> str:
        return "self[%s]" % self.__str__()

    def setup(self) -> None:
        """Подготовка воркера (выполняется один раз на воркер)

        - Настройка путей
        - Создание `Context`
        - Загрузка хуков и определений шагов
        - Инициализация форматтеров
        - Вызов `before_all`
        """
        if self._is_started:
            return
        self.setup_paths()

        # Создание нового контекста для этого воркера и предварительная загрузка хуков/шагов
        self.context = Context(self)
        self.step_registry = self.step_registry or behave_step_registry
        self.load_hooks()
        self.load_step_definitions()

        stream_openers = self.config.outputs
        self.formatters = make_formatters(self.config, stream_openers)

        # Вызов хука before_all один раз на воркер
        self.hook_failures = 0
        self.run_hook("before_all")
        self._is_started = True

    def run_feature(self, feature: Optional[Feature]) -> None:
        """Выполнить одну фичу с контекстом воркера"""
        self.setup()

        if feature is None:
            self.teardown()
            return

        is_failed = False
        if not (self.aborted or self.config.stop):
            try:
                self.feature = feature
                for formatter in self.formatters:
                    formatter.uri(feature.filename)

                is_failed = feature.run(self)
            except Exception as ex:
                self.abort(reason=ex.__class__.__name__)
                is_failed = True

        for reporter in self.config.reporters:
            reporter.feature(feature)

        self._is_failed |= is_failed

    def teardown(self) -> None:
        """Завершить работу воркера"""
        if not self._is_started or self._is_finished:
            return
        cleanups_failed = False
        self.run_hook_with_capture("after_all")
        try:
            self.context._do_remaining_cleanups()
        except Exception:
            cleanups_failed = True

        if self.aborted:
            print("\nABORTED: By user.")
        for formatter in self.formatters:
            formatter.close()
        for reporter in self.config.reporters:
            reporter.end()

        self._is_failed = (
            self.is_failed
            or self.aborted
            or (self.hook_failures > 0)
            or (len(self.undefined_steps) > 0)
            or cleanups_failed
        )

        self._is_finished = True

    @property
    def is_failed(self) -> bool:
        """Флаг, указывающий на наличие ошибок"""
        return self._is_failed


class Worker(ABC):

    _runner: WorkerRunner

    def __init__(self, config: Configuration, index: int):
        self._runner = WorkerRunner(config, index)

    def __str__(self):
        return f"{self.__class__.__name__}-{self.index}"

    def __repr__(self) -> str:
        return "self[%s]" % self.__str__()

    @property
    def runner(self) -> WorkerRunner:
        """Получить экземпляр Runner"""
        return self._runner

    @property
    def index(self) -> int:
        """Индекс воркера"""
        return self.runner.index

    @abstractmethod
    def run_feature(self, feature: Optional[Feature]) -> None:
        """Абстрактный метод для выполнения фичи"""
        pass

    @abstractmethod
    def done(self) -> bool:
        """Проверить завершение работы воркера"""
        pass

    @abstractmethod
    def is_alive(self) -> bool:
        pass

    def shutdown(self):
        """Метод завершения работы"""
        pass


class WorkerPoolExecutor(PoolExecutor[Worker]):

    def __init__(self, config: Configuration, worker_class: type):
        super().__init__(config, worker_class)

    def done(self) -> bool:
        """Проверить завершение всех воркеров"""
        return all(worker.done() for worker in self)

    def is_alive(self) -> bool:
        return any(worker.is_alive() for worker in self)

    def __enter__(self) -> "WorkerPoolExecutor":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for worker in self._pool:
            worker.shutdown()
